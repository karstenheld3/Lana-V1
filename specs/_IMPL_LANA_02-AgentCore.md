# IMPL: Lana Agent Core

**Doc ID**: LANACORE-IP01
**Goal**: Implement the agent turn loop, session persistence, checkpoint compaction, and command safety per LANACORE-SP01
**Timeline**: Created 2026-08-29, Extracted from _IMPL_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `src/lana/agent.py` (turn loop, tool dispatch, compaction trigger)
- `src/lana/session.py` (JSONL append store, resume projection)
- `src/lana/compaction.py` (projection, summarizer call, checkpoint)
- `src/lana/safety.py` (ExecutionPolicy, denylist, approval gate)

**Depends on:**
- `_SPEC_LANA_02-AgentCore.md [LANACORE-SP01]` for FR-04, FR-05, FR-07, FR-08, FR-12, DD-05, DD-07, DD-08, DD-13, DD-15, DD-22, IG-02..04, IG-06..07
- `_IMPL_LANA_01-ProductOverview.md [LANAAGNT-IP01]` for IS-01 (skeleton), IS-02 (models/events)

**Does not depend on:**
- `_IMPL_LANA_04-Providers.md [LANAPRVD-IP01]` (adapters are independent; AgentCore consumes the ProviderAdapter protocol)

## MUST-NOT-FORGET

- System prompt byte-identical across a session (LANAAGNT-IG-01) - no timestamps, no cwd, no variable content in it
- Every AgentEvent appended to the JSON Lines (JSONL) session file at occurrence, user events before the turn starts (LANAAGNT-IG-02)
- Denylist checks the FIRST token after alias normalization; wrappers are never parsed, always approved (LANAAGNT-FR-12)
- Deterministic todo extraction - never let the Summarizer touch todo state (LANAAGNT-IG-04)
- Small cycles: implement -> test -> green -> commit per phase; never proceed on red

## Table of Contents

1. [Edge Cases](#1-edge-cases)
2. [Implementation Steps](#2-implementation-steps)
3. [Test Cases](#3-test-cases)
4. [Verification Checklist](#4-verification-checklist)
5. [Document History](#5-document-history)

## 1. Edge Cases

**Input boundaries:**
- **LANAAGNT-IP01-EC-04**: Tool result exceeds `tool_result_max_chars` -> tail-truncate, append `<truncated N chars>` marker (LANAAGNT-FR-04)
- **LANAAGNT-IP01-EC-05**: Unknown `/name` input -> list up to 3 closest workflow names (prefix + edit distance), do not call the Generator
- **LANAAGNT-IP01-EC-06**: Workflow filename collides with built-in (`help.md`, `cost.md`, `exit.md`) -> built-in wins, warn once at startup

**State transitions:**
- **LANAAGNT-IP01-EC-10**: Ctrl+C during tool loop -> completed ToolCalls kept, synthetic cancellation note appended, REPL prompt returns (LANAAGNT-FR-04)
- **LANAAGNT-IP01-EC-11**: `max_tool_calls_per_prompt` reached -> pause with continue prompt; `auto_continue: true` skips the pause
- **LANAAGNT-IP01-EC-12**: Compaction fires with zero `todo_list` events -> checkpoint omits the todo section (LANAAGNT-FR-07)
- **LANAAGNT-IP01-EC-13**: Two Lana instances, same workspace -> distinct session files (timestamp+id in name); no lock needed; ReadLedger divergence caught by EC-08 mtime check

**External failures:**
- **LANAAGNT-IP01-EC-17**: Summarizer call fails during compaction -> no truncation, warning, session continues (LANAAGNT-FR-07)
- **LANAAGNT-IP01-EC-20**: Context overflow despite projection (provider 400 "too long") -> error event advising model switch or new session; no auto-retry with same payload

**Data anomalies:**
- **LANAAGNT-IP01-EC-21**: JSONL last line truncated (crash mid-write) -> skip invalid line on resume, log count of skipped lines
- **LANAAGNT-IP01-EC-22**: Generator emits unknown tool name -> tool error listing available tools (no crash)
- **LANAAGNT-IP01-EC-23**: Generator emits invalid JSON args -> tool error with schema validation message
- **LANAAGNT-IP01-EC-28**: `--resume` on a legacy session file without `session_started` (pre-FR-08 full recall) -> fall back to disk prompt assembly, warn "legacy session file - recorded environment unavailable, system prompt assembled from current prompt system"
- **LANAAGNT-IP01-EC-29**: `--resume` with a generator provider differing from a recorded thinking payload's provider -> payload dropped from the adapter resend (signatures are provider-bound, SPEC FR-08); rendered thinking text stays in the log

## 2. Implementation Steps

### Phase E: Agent Loop, Session, Safety

### LANAAGNT-IP01-IS-09: Safety gate (LANAAGNT-FR-12)

**Location**: `safety.py`

**Action**: `classify(command, policy, config) -> RUN | ASK`:
```python
# 1. first_token = first whitespace-delimited token, strip path/quotes, casefold
# 2. wrapper? (pwsh|powershell|cmd|bash + -Command|-c|/c present) -> ASK in auto/turbo
# 3. denylist: single-token entries match first_token; multi-token entries prefix-match full line
# 4. policy: manual -> always ASK; auto -> ASK unless SafeToAutoRun and no match; turbo -> RUN unless match
```

**Note**: Approval renders exact command + cwd (render.py); IG-03 test: `Remove-Item` and `pwsh -Command "Remove-Item x"` both stop in auto policy

### LANAAGNT-IP01-IS-13: Turn loop (LANAAGNT-FR-04)

**Location**: `agent.py`

**Action**: `run_prompt(user_input)`: expand slash command (FR-05, via loader), build user message with metadata block (date, cwd - HERE, not in system prompt), then loop: adapter stream -> events -> execute tool calls sequentially through registry + safety -> append results -> repeat. Enforce call limit + auto_continue (EC-11), tool result cap (EC-04), Ctrl+C handling (EC-10), unknown tool / bad args (EC-22/23)

**Note**: The loop is a pure async generator over AgentEvents - frontends only consume events (DD-06)

### LANAAGNT-IP01-IS-14: Session store and resume (LANAAGNT-FR-08)

**Location**: `session.py`

**Action**: Append-only JSONL writer (`user_message` flushed synchronously, every line flushed at write per FR-08 - the external tail contract); `resume(path)` projects events -> canonical messages: replay user/assistant/tool events, apply last `checkpoint_created` (truncate prior history, splice checkpoint text; the event carries `kept_messages` so the retained tail reprojects exactly - synced 2026-08-30), skip corrupt lines with count (EC-21), inject cancellation notes for turns ending in cancellation; resume also restores usage/cost/turn totals per role for CostTracker seeding (BG-0002)

### Phase G: Compaction

### LANAAGNT-IP01-IS-17: Usage-anchored projection and checkpoint (LANAAGNT-FR-07)

**Location**: `compaction.py`

**Action**:
```python
def projected_tokens(anchor_tokens, chars_since_anchor): ...   # anchor + chars/4 delta
def extract_last_todo(events): ...                             # deterministic, byte-verbatim
def build_checkpoint(summary_sections, todo_json): ...         # SPEC section 10 template, 3 anchors
def compact(session, summarizer_adapter): ...                  # one call, 3 labeled sections; failure -> warn + no-op (EC-17)
```

**Note**: Threshold = `min(fraction x generator max_input, max_tokens)`, fires at >= (TC-36 boundary); checked after EVERY turn in `agent.py` including between tool-loop turns (drift item 02). Truncation keeps the last 6 messages; leading orphan tool-result messages are trimmed from the tail so no tool_result survives without its tool_use partner (provider 400 guard) (synced 2026-08-30)

### LANAAGNT-IP01-IS-24: Full-recall session log (LANAAGNT-FR-08, DD-22, IG-07)

**Location**: `events.py`, `session.py`, `cli.py`, `agent.py`, `providers/scripted_adapter.py`

**Action**:
```python
# events.py: SessionStarted event - system_prompt (byte-verbatim), tool_definitions (verbatim array),
#            config_snapshot (role -> model_id/effort/provider, policy, thresholds, limits),
#            prompt_system_fingerprint (paths, per-folder counts, sha256 content hash)
# events.py: TurnFinished gains optional thinking_payloads: [{provider, payload}] - the turn's
#            resendable ThinkingBlocks (Anthropic signature blocks, OpenAI reasoning items); enum stays at 11
# cli.py:   new session -> session_started written as the FIRST line before any user event
# session.py resume: read session_started -> recorded system prompt + tool definitions REPLACE disk assembly
#            for Generator calls; projector rebuilds Message.thinking from turn_finished.thinking_payloads
# session.py resume: fingerprint compare vs freshly loaded prompt system -> one-line WARNING on mismatch
# cli.py resume: recorded vs current generator model differ -> one-line report (model change, FR-08)
# agent.py:  drop resurrected thinking payloads whose provider != resumed generator provider (EC-29)
# scripted_adapter.py: LANA_SCRIPTED_CAPTURE=<path> dumps each received (system, tools) to a JSONL file -
#            the TC-65/TP01-TC-11 byte-identity oracle for what the Generator actually received
```

**Note**: Fingerprint hash over sorted (path, content) pairs - deterministic across machines [ASSUMED - mtime excluded to survive copies/checkouts]. Legacy files without `session_started` follow EC-28. The recorded tool definitions are the resume authority - a tool added after recording is absent from resumed Generator calls until a new session (IG-01 byte-identity extends to the tool block)

## 3. Test Cases

### Category 5: Safety (6 tests)

- **LANAAGNT-IP01-TC-26**: `Remove-Item x` first-token match -> ASK in auto
- **LANAAGNT-IP01-TC-27**: `pwsh -Command "Remove-Item x"` wrapper -> ASK in auto and turbo (IG-03)
- **LANAAGNT-IP01-TC-28**: `git push --force-with-lease` prefix-matches `git push --force` entry -> ASK
- **LANAAGNT-IP01-TC-29**: `echo hi` in auto with SafeToAutoRun -> RUN
- **LANAAGNT-IP01-TC-30**: manual policy -> ASK for everything
- **LANAAGNT-IP01-TC-31**: out-of-workspace write_to_file -> approval required

### Category 6: Loop, Session, Compaction (8 tests, fake adapter)

- **LANAAGNT-IP01-TC-32**: Scripted 3-tool-call turn -> event sequence and JSONL complete (IG-02)
- **LANAAGNT-IP01-TC-33**: Call limit 25 (EC-11) -> pause; auto_continue -> no pause
- **LANAAGNT-IP01-TC-34**: Cancellation mid-loop (EC-10) -> kept results + synthetic note; resume reflects it
- **LANAAGNT-IP01-TC-35**: Resume after simulated crash with truncated last line (EC-21)
- **LANAAGNT-IP01-TC-36**: Projection: anchor 100K + 80K chars delta -> 120K projected, compaction fires
- **LANAAGNT-IP01-TC-37**: Checkpoint content: 3 anchors present, todo JSON byte-identical (IG-04)
- **LANAAGNT-IP01-TC-38**: Summarizer failure (EC-17) -> no truncation, warning event
- **LANAAGNT-IP01-TC-39**: No-todo compaction (EC-12) -> todo section omitted

### Category 13: Full-Recall Session Log (4 tests)

- **LANAAGNT-IP01-TC-64**: `session_started` is the first JSONL line of every new session and carries system prompt byte-identical to the assembled one, the verbatim tool definitions array, config snapshot, and fingerprint (FR-08, IG-07)
- **LANAAGNT-IP01-TC-65**: Resume authority - modify the fake prompt system on disk, `--resume` -> Generator receives the RECORDED system prompt byte-identically (scripted adapter captures the request); fingerprint mismatch warning printed; changed generator model in config -> model-change report line (IG-01 across resume)
- **LANAAGNT-IP01-TC-66**: Thinking payload round trip - scripted turn yields a thinking payload -> `turn_finished.thinking_payloads` in JSONL; resume reprojects it into Message.thinking on provider match; provider mismatch drops it from the resend while the event stays in the log (EC-29)
- **LANAAGNT-IP01-TC-67**: Legacy session file without `session_started` (EC-28) -> resume succeeds via disk assembly, legacy warning printed, conversation projection unchanged

## 4. Verification Checklist

- [x] **LANACORE-IP01-VC-01**: LANACORE-SP01 re-read; all 5 FRs, 6 DDs, 5 IGs accounted for
- [x] **LANACORE-IP01-VC-02**: Phase E green (TC-26..35, safety + loop + session)
- [x] **LANACORE-IP01-VC-03**: Phase G green (TC-36..39, compaction)
- [x] **LANACORE-IP01-VC-04**: Category 13 green (TC-64..67, full recall)
- [x] **LANACORE-IP01-VC-05**: IG-03 test: denylist command never auto-runs in any policy
- [x] **LANACORE-IP01-VC-06**: IG-04 test: todo JSON byte-identical through compaction

## 5. Document History

**[2026-09-01 21:45]**
- Extracted from `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]`: IS-09 (safety gate), IS-13 (turn loop), IS-14 (session store/resume), IS-17 (compaction), IS-24 (full-recall session log)
- Edge cases: EC-04/05/06/10/11/12/13/17/20/21/22/23/28/29
- Test cases: Categories 5 (safety), 6 (loop/session/compaction), 13 (full recall)
- Content is verbatim from source with section renumbering and header block update only
