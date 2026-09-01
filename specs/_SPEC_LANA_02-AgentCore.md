# SPEC: Lana Agent Core

**Doc ID**: LANACORE-SP01
**Goal**: Specify the central agent logic: turn loop, slash command expansion, session persistence, checkpoint compaction, and command safety
**Timeline**: Created 2026-08-29, Extracted from _SPEC_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `src/lana/agent.py` (turn loop, tool dispatch)
- `src/lana/session.py` (JSONL append store, resume)
- `src/lana/compaction.py` (projection, summarizer call, checkpoint)
- `src/lana/safety.py` (ExecutionPolicy, denylist, approval gate)

**Depends on:**
- `_SPEC_LANA_01-ProductOverview.md [LANAAGNT-SP01]` for domain objects (AgentEvent, Session, Checkpoint, ExecutionPolicy, ToolCall)

**Does not depend on:**
- `_SPEC_LANA_03-PromptAndConfig.md [LANAPRCF-SP01]` (config and prompt assembly are independent; AgentCore consumes their outputs)
- `_SPEC_LANA_05-Tools.md [LANATOOL-SP01]` (tool executors are independent; AgentCore dispatches through the registry)

## Table of Contents

1. [Functional Requirements](#1-functional-requirements)
2. [Design Decisions](#2-design-decisions)
3. [Implementation Guarantees](#3-implementation-guarantees)
4. [Key Mechanisms](#4-key-mechanisms)
5. [Action Flow](#5-action-flow)
6. [Document History](#6-document-history)

## 1. Functional Requirements

**LANAAGNT-FR-04: Agent Turn Loop**
- One user message starts a loop: Generator call, execute requested ToolCalls sequentially (OQ-08), append results, repeat until the Generator responds without tool calls
- Hard limit `max_tool_calls_per_prompt` (default 40) per user message; on reaching it, pause and ask the user to continue unless `auto_continue: true` (OQ-07; RV01 RF-09; raised from 25 per LANALOGS-PR-0006)
- Every tool result is capped at `tool_result_max_chars` (default 50000), tail-truncated with a `<truncated N chars>` marker before entering conversation state (RV01 RF-03)
- Streaming: assistant text and thinking rendered incrementally as AgentEvents (OQ-09)
- Cancellation: Ctrl+C aborts the in-flight API call; completed ToolCalls of the aborted turn remain in conversation state, closed with a synthetic note "turn cancelled after N tool calls"; only the incomplete API response is discarded (RV01 RF-06)

**LANAAGNT-FR-05: Slash Command Expansion**
- Input starting with `/name` matching a loaded workflow: wrap the workflow content into the user message in the Cascade format (`<user_request>` + `<workflows>` block with full Markdown content) (OQ-22)
- Unknown `/name`: list closest matches, do not send to the Generator
- Built-in commands (not sent to the Generator): `/exit`, `/help` (list workflows + built-ins), `/cost` (session usage summary)

**LANAAGNT-FR-07: Checkpoint Compaction**
- Trigger: projected context tokens reach or exceed `min(compaction_threshold_fraction x generator max_input, compaction_threshold_max_tokens)` (defaults 0.6 and 150000), checked after each turn - including between the turns of one tool loop (OQ-14), reactive only (OQ-15)
- Projection is usage-anchored: last provider-reported input token count + chars/4 estimate of content added since that call (RV01 RF-05)
- One Summarizer call producing three labeled sections: objective, conversation summary, code interaction history (OQ-12)
- Last `todo_list` state extracted deterministically from the event log - never via the Summarizer (OQ-12)
- Checkpoint replaces truncated history as the first conversation message; includes the three hardcoded behavioral anchors from the Cascade template: "keep this up to date with todo_list tool", "Make sure to continue working off of this TODO list", "DO NOT ACKNOWLEDGE THIS CHECKPOINT MESSAGE"
- Fail-safe: on Summarizer call failure, no truncation occurs - warn the user and continue uncompacted
- No `todo_list` state in the event log: the todo section is omitted from the checkpoint
- System prompt and tool definitions never truncated

**LANAAGNT-FR-08: Session Persistence - Full Recall**
- First event of every session file: `session_started` carrying 1) the byte-verbatim assembled system prompt, 2) the verbatim tool definitions array (name, description, JSON Schema) as sent to the provider, 3) the resolved config snapshot (role -> model_id/effort/provider, execution policy, compaction thresholds, tool/result limits), 4) a prompt system fingerprint (ordered path list, per-folder file counts, content hash)
- Every AgentEvent appended to the session JSONL file at occurrence (crash-safe) (OQ-10)
- Each event line is flushed to disk at write time - external processes can tail the session file as a live activity monitor (test harness contract, LANAAGNT-DD-20)
- Full recall: every byte sent to the Generator is reconstructible from the JSONL alone - system prompt and tool definitions from `session_started`, conversation from event projection, checkpoint text from `checkpoint_created` (LANAAGNT-IG-07)
- Assistant thinking payloads that the adapter must resend on later calls (Anthropic thinking blocks with signatures) are recorded verbatim on the turn's `turn_finished` event - resume reproduces the exact resend content without adding a 12th event type
- `lana --resume [session-file]` rebuilds conversation state, system prompt, and tool definitions from the JSONL and continues - the recorded system prompt is reused byte-verbatim (preserves LANAAGNT-IG-01 across resume); the on-disk prompt system is loaded only for new workflow expansion and skill invocation
- Resume fingerprint check: when the loaded prompt system's fingerprint differs from the recorded one, print a one-line warning naming the difference (counts/hash) - the recorded system prompt still wins for Generator calls
- Model change on resume: role -> model resolution follows the CURRENT `lana-config.json` (enables switching models between runs); the recorded config snapshot serves audit and reconstruction, never model selection; a differing generator is reported at startup (recorded vs current)
- Provider independence: recall never depends on provider-side state - prompt caches are ephemeral (minutes-scale TTL) and provider-bound; after a model or provider change the full recorded context is re-sent from the JSONL (cold-cache cost effect only, no information loss)
- Cross-provider thinking payloads: recorded thinking payloads are resent only when the resumed provider matches their recording provider; on provider change they are dropped from the resend (signatures are provider-bound) while their rendered text remains in the log for recall
- Session files never auto-deleted

**LANAAGNT-FR-12: Command Safety**
- Generator self-classifies via `SafeToAutoRun` (schema kept verbatim); Lana runtime applies the ExecutionPolicy on top (OQ-29)
- `manual` (default): every `run_command` requires interactive y/n/a approval showing the exact command line and working directory; `a` (all) approves the current and all remaining approval-gated tool calls for the rest of the session
- `auto`: `SafeToAutoRun: true` commands run without prompt; denylist match overrides to approval
- `turbo`: all run except denylist matches (always require approval)
- Denylist matching: case-insensitive comparison of the command line's first token (multi-token entries prefix-match the command line); default: `rm`, `del`, `rmdir`, `erase`, `ri`, `Remove-Item`, `Move-Item`, `format`, `kill`, `pkill`, `Stop-Process`, `shutdown`, `git push --force` (RV01 RF-02)
- Shell wrapper invocations (`pwsh`, `powershell`, `cmd`, `bash` with `-Command`, `-c`, or `/c`) always require approval in `auto` and `turbo` - inner commands are not parsed (RV01 RF-02)
- Approval prompts also gate `write_to_file`/`edit` outside the workspace root

## 2. Design Decisions

**LANAAGNT-DD-05:** Sequential tool execution (OQ-08, narrows the INFO leaning) [TESTED - full offline suite + live acceptance green with sequential dispatch 2026-08-30]. Rationale: parallel execution adds ordering and interleaved-output complexity for reads only; MVP-1 favors zero race conditions. The AgentEvent stream is order-preserving either way.

**LANAAGNT-DD-07:** Single Summarizer call + deterministic todo extraction instead of Cascade's 3 parallel calls (OQ-12). Rationale: one structured call is cheaper and simpler; the deterministic todo path is the highest-value element and is kept exactly.

**LANAAGNT-DD-08:** Compaction threshold relative to the generator's `max_input` with an absolute cap (OQ-14). Rationale: registry windows span 200K to 1.05M tokens; a fixed 100K wastes large windows; the cap bounds Summarizer cost.

**LANAAGNT-DD-13:** Agent-side slash command expansion (OQ-22). Rationale: one code path that also serves ACP in MVP-2, where slash commands arrive as plain prompt text.

**LANAAGNT-DD-15:** Three-level ExecutionPolicy with denylist (OQ-29). Rationale: mirrors Cascade's proven dual-consent model minus the allowlist level (redundant with `auto` for a CLI user who sees every command).

**LANAAGNT-DD-22:** [ASSUMED] Full-recall session log: the `session_started` event records the byte-verbatim system prompt, tool definitions, and config snapshot; `--resume` reuses the recorded prompt instead of reassembling from disk. Rationale: "single source of truth" previously covered only conversation state - a prompt system or config change between exit and resume silently altered the resumed session's instructions, and the JSONL could not answer "what exactly did the Generator receive?". Provider-side state is ephemeral and model-bound: prompt caches expire within minutes and never survive a model or provider change, so persistence must be complete and self-sufficient - the JSONL alone rebuilds the full request for ANY model. Recording the environment costs ~100 KB per session file (one-time, negligible against conversation volume) and extends the IG-01 byte-identity guarantee across same-model resumes (cache hits within provider TTL are a bonus, never a dependency). The on-disk prompt system remains the source for NEW workflow expansions and skill invocations after resume - only already-sent content is immutable.

## 3. Implementation Guarantees

**LANAAGNT-IG-02:** No tool executes without an entry in the session JSONL recording its arguments and result.

**LANAAGNT-IG-03:** A command whose first token matches the denylist (per LANAAGNT-FR-12 matching rules) never executes without interactive approval, regardless of ExecutionPolicy or `SafeToAutoRun`. Scope: the denylist guards against ACCIDENTAL destructive commands; it is not an adversarial-input defense (see LANAAGNT-NFR-05).

**LANAAGNT-IG-04:** The last `todo_list` state survives compaction byte-identically (deterministic extraction, no LLM paraphrase).

**LANAAGNT-IG-06:** Conversation state after `--resume` equals state before process exit (minus any incomplete in-flight turn), reconstructed exclusively from the session JSONL - no dependency on prompt system folder state for previously sent content.

**LANAAGNT-IG-07:** Every byte sent to the Generator - system prompt, tool definitions, conversation messages, checkpoint text - is reconstructible from the session JSONL alone (full recall, LANAAGNT-FR-08).

## 4. Key Mechanisms

- **Cache-stable prompt layout**: fixed assembly order [system prompt | tool definitions | conversation]; all per-turn variability (date, cwd) lives in the user message metadata block, never in the system prompt
- **Deterministic todo persistence**: compaction scans the event log backwards for the last `todo_list` result and splices its JSON verbatim into the checkpoint (Cascade's proven no-LLM path)
- **Read-gate ledger**: per-session map of file path to last-read modification time backs the edit enforcement gate
- **Event-sourced session**: the JSONL event log is the single source of truth for the entire Generator input - environment (`session_started`: system prompt, tool definitions, config) plus conversation; API request state and the resume feature are both projections of it, with zero dependency on external folder state for recall

## 5. Action Flow

Interactive turn with workflow invocation:

```
User types "/prime"
├─> Slash expander: match workflows/prime.md
│   └─> Build user message: <user_request>/prime</user_request> + <workflows>{full prime.md}</workflows>
├─> Turn loop (repeat until no tool calls or limit 25):
│   ├─> ProviderAdapter: canonical messages -> provider request (cache breakpoints set)
│   ├─> Stream response: text_delta / thinking_delta events -> CLI renderer
│   ├─> For each requested ToolCall (sequential):
│   │   ├─> Safety gate (run_command; file writes outside workspace): ExecutionPolicy + denylist -> approval_required event if needed
│   │   ├─> Execute tool -> tool_call_finished event -> append to JSONL
│   │   └─> Append result to canonical messages
│   └─> turn_finished event: usage + cost line rendered
├─> Compaction check: est_tokens > threshold?
│   └─> Yes: Summarizer call + todo extraction -> checkpoint_created event -> history replaced
└─> Prompt for next input
```

## 6. Document History

**[2026-09-01 21:45]**
- Extracted from `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]`: FR-04, FR-05, FR-07, FR-08, FR-12, DD-05, DD-07, DD-08, DD-13, DD-15, DD-22, IG-02, IG-03, IG-04, IG-06, IG-07, Section 8 (Key Mechanisms), Section 9 (Action Flow)
- Content is verbatim from source with section renumbering and header block update only
- Verbatim tool contract mechanism moved to `_SPEC_LANA_01-ProductOverview.md [LANAAGNT-SP01]` (cross-cutting)
