# INFO: Lana Interaction Chain and Dead-Air Audit

**Doc ID**: LANAUSRX-IN01
**Goal**: Map the full agent interaction chain, classify every user-visible interaction by category, identify all dead-air phases, and establish an interaction color scheme
**Timeline**: Created 2026-08-31, Updated 2 times (2026-08-31 - 2026-08-31)

**Depends on:**
- `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` for event types and renderer contract
- `_INFO_DELPHIOS_DESIGN_SYSTEM.md [DLPHS-IN10]` for color system and interaction states (design system name: internal use only, never in shipped artifacts)
- `_INFO_DELPHIOS_BRAND.md [DLPHS-IN07]` for brand pillars (Flow, Reliability, Safety) and communication tone

## Summary

- Lana has 12 AgentEvent types flowing through 2 frontends: Command-Line Interface (CLI) renderer, Agent Client Protocol (ACP) translator [VERIFIED]
- 7 dead-air phases identified where the user cannot distinguish working from stalled [VERIFIED]
- 3 phases rated HIGH severity (Large Language Model (LLM) thinking, tool execution, post-turn gap), 2 MEDIUM (compaction, retries), 2 LOW (session build, approval wait) [VERIFIED]
- 6 interaction categories proposed for color classification: Thinking, Streaming, Tool, Approval, System, Error [VERIFIED]
- CLI currently uses 4 styles only: default (no style), dim, yellow, red [VERIFIED]
- ACP translator produces 6 core update types (plus 2 conditional); has no thinking/status indicator at all [VERIFIED]
- Brand >300ms rule (DLPHS-IN10 Section 16.2): any operation exceeding 300ms must show a loading indicator [VERIFIED]
- Brand frugal-language rule: status messages must be precise and minimal, never verbose [VERIFIED]

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Event Types and Flow](#2-event-types-and-flow)
3. [Interaction Categories](#3-interaction-categories)
4. [Dead-Air Inventory](#4-dead-air-inventory)
5. [Current Visual Treatment](#5-current-visual-treatment)
6. [Proposed Color Scheme](#6-proposed-color-scheme)
7. [Next Steps](#7-next-steps)
8. [Sources](#8-sources)
9. [Document History](#9-document-history)

## 1. Architecture Overview

### 1.1 Two Frontends, One Event Stream

Lana's agent core (`agent.py`) is an async generator yielding `AgentEvent` objects. Two frontends consume this stream independently:

```
User prompt
  │
  v
agent.run_prompt()  ── async generator ──> AgentEvent stream
  │                                            │
  ├── CLI mode ──> cli.py:run_one_prompt() ──> render.py:Renderer.handle()
  │                                            │
  └── ACP mode ──> server.py:run_prompt_turn() ──> translator.py:EventTranslator.translate()
                                                   │
                                                   v
                                               session/update JSON-RPC notifications
```

### 1.2 Component Responsibilities

- **`agent.py`** - Core turn loop. Calls LLM provider, dispatches tools, handles approval callbacks, emits events
- **`render.py`** - CLI renderer. Rich console output with status spinner, styled text, tool summaries
- **`translator.py`** - ACP frontend. Maps AgentEvents to `session/update` JSON-RPC payloads for Devin Desktop
- **`compaction.py`** - Context summarizer. Runs post-turn when token count exceeds threshold. Emits ErrorEvent (NOTICE) and CheckpointCreated
- **`providers/`** - LLM adapters (OpenAI, Anthropic). Streaming with retry logic. Emit AdapterDelta objects consumed by agent.py
- **`tools/`** - Tool executors. Synchronous (or async for ACP elicitation). Shell commands, web fetching, file operations

### 1.3 Lifecycle of One Prompt

```
[1] User types prompt
 │
[2] agent.run_prompt() enters while-loop
 │
 ├─[3] TurnStarted event
 ├─[4] Provider stream_turn() ── network round-trip to LLM API
 │   ├── ThinkingDelta events (0..N)
 │   ├── TextDelta events (0..N)
 │   └── Tool calls collected
 ├─[5] TurnFinished event (usage stats)
 │
 ├── If tool calls:
 │   ├─[6] ToolCallRequested event (per call)
 │   ├─[7] Approval check (if policy requires)
 │   │   └── ApprovalRequired event
 │   ├─[8] Tool executor runs
 │   ├─[9] ToolCallFinished event
 │   └── Loop back to [3] for next LLM turn
 │
 ├── If no tool calls: exit loop
 │
 └─[10] maybe_compact()
     ├── ErrorEvent (NOTICE: "Compacting context...")
     ├── Summarizer LLM call (separate provider round-trip)
     └── CheckpointCreated event
```

## 2. Event Types and Flow

### 2.1 All 12 AgentEvent Types

Each event type, its producer, and how each frontend handles it:

- **session_started** - Produced once at session init. CLI: not rendered. ACP: not forwarded (session-file-only).
- **user_message** - Produced per prompt. CLI: not rendered. ACP: forwarded only during session/load replay as `user_message_chunk`.
- **turn_started** - Produced at each LLM call start. CLI: starts spinner. ACP: rotates messageId, returns zero updates.
- **text_delta** - Streamed LLM text output. CLI: prints inline (no style). ACP: `agent_message_chunk`.
- **thinking_delta** - Streamed LLM reasoning. CLI: dim text (if shown) or spinner tick (if hidden). ACP: `agent_thought_chunk`.
- **tool_call_requested** - Before tool dispatch. CLI: `[tool] name 'summary'...` line. ACP: `tool_call` update (status: pending).
- **tool_call_finished** - After tool completes. CLI: `OK. N chars.` or `ERROR: ...`. ACP: `tool_call_update` (completed/failed).
- **approval_required** - After approval resolved. CLI: `[action] approved/denied.`. ACP: consumed by PermissionBroker (not forwarded as update).
- **turn_finished** - After LLM turn completes. CLI: Turn stats line. ACP: `usage_update`.
- **checkpoint_created** - After compaction succeeds. CLI: `Compacted: N messages...`. ACP: not forwarded (documented omission).
- **error** - Warnings, notices, errors. CLI: yellow/dim/red by prefix. ACP: inline `agent_message_chunk` (unstructured).
- **prompt_step** - Headless prompt queue boundary. CLI: not rendered in interactive mode. ACP: not forwarded (headless-only).

### 2.2 Event Timing Characteristics

Events grouped by their timing behavior (determines dead-air risk):

**Instantaneous** (<1ms, never produce dead air):
- session_started, user_message, turn_started, approval_required, checkpoint_created, turn_finished, prompt_step

**Streaming** (continuous output while active, no dead air during stream):
- text_delta, thinking_delta

**Gated by external I/O** (variable latency, primary dead-air sources):
- Provider stream_turn(): 2-30s before first delta (network + model inference)
- Tool executors: 0-600s (run_command Blocking), 2-120s (web tools), <1s (file tools)
- Compaction summarizer: 5-30s (separate LLM call)
- Provider retries: 2s + 8s sleep delays

## 3. Interaction Categories

Every user-visible moment in the agent lifecycle falls into one of 6 categories. These categories form the basis for the color scheme.

### 3.1 Category Definitions

**CAT-THINK: Model Thinking**
- **What**: LLM is processing (request sent, waiting for response or streaming reasoning)
- **Events**: turn_started, thinking_delta (hidden), provider retry delays
- **User question**: "Is it thinking or stuck?"
- **Duration**: 2-30s per turn, unbounded with retries
- **Current CLI treatment**: Spinner "generator thinking... Ns" (dim animated)

**CAT-STREAM: Content Streaming**
- **What**: LLM is producing visible output (text or shown thinking)
- **Events**: text_delta, thinking_delta (shown)
- **User question**: None (output is flowing, user sees activity)
- **Duration**: Continuous while active
- **Current CLI treatment**: Text printed inline (no style / dim for thinking)

**CAT-TOOL: Tool Execution**
- **What**: Agent is executing a tool (file read/write, shell command, web fetch, search)
- **Events**: tool_call_requested, tool_call_finished
- **User question**: "Is the command still running or did it hang?"
- **Duration**: <1s (file ops) to 600s (blocking commands)
- **Current CLI treatment**: Static `[tool]` line, then `OK.` or `ERROR:` line

**CAT-APPROVE: User Action Required**
- **What**: Agent needs human decision (approval, elicitation, continue prompt)
- **Events**: approval_required (plus interactive prompts in CLI, permission round-trips in ACP)
- **User question**: None (prompt is visible, ball is in user's court)
- **Duration**: Unbounded (human response time)
- **Current CLI treatment**: `[action] detail`, `Approve? [y/n/a]` prompt

**CAT-SYSTEM: Internal Operations**
- **What**: Agent performing housekeeping (compaction, session build, session resume, message serialization)
- **Events**: checkpoint_created, error (NOTICE prefix)
- **User question**: "What is happening behind the scenes?"
- **Duration**: 0.5-30s (compaction), 0.5-5s (session build), 0-2s (message prep)
- **Current CLI treatment**: NOTICE dim text, Compacted line (no style)

**CAT-ERROR: Errors and Warnings**
- **What**: Something went wrong or needs attention
- **Events**: error (WARNING prefix, ERROR prefix, unprefixed)
- **User question**: "What failed and what should I do?"
- **Duration**: Instantaneous (display only)
- **Current CLI treatment**: Yellow (WARNING), red (ERROR)

### 3.2 Event-to-Category Mapping

Every AgentEvent type maps to exactly one interaction category:

- turn_started → CAT-THINK
- thinking_delta (hidden) → CAT-THINK
- thinking_delta (shown) → CAT-STREAM
- text_delta → CAT-STREAM
- tool_call_requested → CAT-TOOL
- tool_call_finished → CAT-TOOL
- approval_required → CAT-APPROVE
- turn_finished → CAT-SYSTEM (informational stats)
- checkpoint_created → CAT-SYSTEM
- error (NOTICE:) → CAT-SYSTEM
- error (WARNING:) → CAT-ERROR
- error (ERROR / unprefixed) → CAT-ERROR
- session_started → CAT-SYSTEM (not rendered)
- user_message → (not rendered in live mode)
- prompt_step → CAT-SYSTEM (headless only)

### 3.3 Gaps Between Events (Implicit States)

Some dead-air phases occur BETWEEN events, not during any event:

- **Pre-first-delta gap**: After turn_started, before any text_delta/thinking_delta/tool_call. Duration: network round-trip + model startup. Belongs to CAT-THINK.
- **Post-turn gap**: After turn_finished, before next turn_started. Duration: message serialization + request preparation. Belongs to CAT-THINK (preparing next request) or CAT-SYSTEM (compaction check).
- **Tool dispatch gap**: After tool_call_requested, before tool_call_finished. Duration: tool executor runtime. Belongs to CAT-TOOL.
- **Retry sleep gap**: During provider retry delay (2s, 8s). Announced by WARNING event, then silence during sleep. Belongs to CAT-THINK.

## 4. Dead-Air Inventory

### 4.1 Severity Criteria

Severity rated by: 1) maximum duration, 2) frequency of occurrence, 3) user confusion potential.

- **HIGH**: >5s common, user likely concludes agent is stuck
- **MEDIUM**: 2-10s, user uncertain but usually waits
- **LOW**: <2s typical, or correctly signaled already

### 4.2 Dead-Air Phase Details

**DA-01: LLM First Token Wait** [HIGH]
- **Phase**: turn_started → first content delta
- **Category**: CAT-THINK
- **Duration**: 2-30s (model-dependent, cache-miss worst case)
- **CLI status**: Spinner "generator thinking..." with elapsed seconds. Ticks via hidden thinking deltas. Frozen when no thinking deltas arrive (pure network wait before first streaming token).
- **ACP status**: NOTHING. `turn_started` yields zero session/update payloads. Client shows no activity until first text_delta or tool_call.
- **Brand violation**: >300ms with no indicator (ACP). Broken Flow pillar.
- **Root cause (CLI)**: `tick_status()` only called on thinking_delta events. No independent timer.
- **Root cause (ACP)**: `EventTranslator.translate()` returns `[]` for turn_started.

**DA-02: Post-Turn Dead Air** [HIGH]
- **Phase**: turn_finished → next turn_started (within tool loop)
- **Category**: CAT-THINK / CAT-SYSTEM
- **Duration**: 0.5-5s (message serialization, request construction)
- **CLI status**: Blinking cursor after Turn stats line. No spinner, no indication.
- **ACP status**: usage_update sent, then silence until next event.
- **Brand violation**: >300ms with no indicator. This is the dead air visible in the user's screenshot.
- **Root cause**: `turn_finished` stops the spinner via `stop_status()`. The next `turn_started` (which re-starts it) only fires after the while-loop iteration completes and `stream_turn()` is called.

**DA-03: Long Tool Execution** [HIGH]
- **Phase**: tool_call_requested → tool_call_finished
- **Category**: CAT-TOOL
- **Duration**: 0-600s (run_command Blocking), 2-15s (search_web), up to 120s (read_url_content)
- **CLI status**: Static `[tool] name 'summary'...` line. No progress. No elapsed time.
- **ACP status**: `tool_call` update (pending). No intermediate updates until completion.
- **Brand violation**: >300ms for nearly all tool calls except trivial file reads.
- **Root cause**: Tool executors are synchronous. No callback mechanism for progress reporting.

**DA-04: Compaction Summarizer Call** [MEDIUM]
- **Phase**: NOTICE displayed → CheckpointCreated or WARNING
- **Category**: CAT-SYSTEM
- **Duration**: 5-30s (full LLM round-trip to summarizer role)
- **CLI status**: NOTICE "Compacting context (~N tokens, threshold M)..." printed, then silence until done.
- **ACP status**: NOTICE forwarded as inline text. CheckpointCreated not forwarded.
- **Brand violation**: >300ms silence during summarizer call. Partial mitigation: NOTICE announces the start.

**DA-05: Provider Retry Sleep** [MEDIUM]
- **Phase**: WARNING displayed → retry attempt starts
- **Category**: CAT-THINK
- **Duration**: 2s (first retry), 8s (second retry)
- **CLI status**: WARNING "Anthropic/OpenAI ...retrying in Ns..." rendered yellow. Then silence during sleep.
- **ACP status**: Error event forwarded as inline text (unstructured).
- **Brand violation**: Delay announced but no countdown or progress during the sleep.

**DA-06: Session Build** [LOW]
- **Phase**: session/new request → response
- **Category**: CAT-SYSTEM
- **Duration**: 0.5-5s (filesystem, prompt system loading)
- **CLI status**: Sequential prints (loading prompt system, roles banner). Visible activity.
- **ACP status**: All output redirected to stderr. Client sees nothing until session/new response.
- **Brand violation (ACP only)**: Typically under 2s. Acceptable for v1.

**DA-07: Approval Wait** [LOW - by design]
- **Phase**: approval prompt displayed → user responds
- **Category**: CAT-APPROVE
- **Duration**: Unbounded (human)
- **CLI status**: Clear prompt with `[y/n/a]`. User knows ball is in their court.
- **ACP status**: `request_permission` round-trip. Client shows permission UI.
- **Brand violation**: None. Correctly signaled in both frontends.

### 4.3 Dead-Air Summary Table

Ordered by severity and actionability:

- **DA-01** LLM First Token Wait - HIGH - CLI: spinner exists but frozen without thinking. ACP: no signal at all
- **DA-02** Post-Turn Dead Air - HIGH - Both: no signal between Turn stats and next turn start
- **DA-03** Long Tool Execution - HIGH - Both: static start marker, no progress, no elapsed time
- **DA-04** Compaction Summarizer - MEDIUM - Both: start announced, no progress during LLM call
- **DA-05** Provider Retry Sleep - MEDIUM - Both: delay announced, silence during countdown
- **DA-06** Session Build - LOW - ACP only: no signal, short duration
- **DA-07** Approval Wait - LOW - Both frontends correctly signal. No fix needed

## 5. Current Visual Treatment

### 5.1 CLI Renderer Styles

The CLI renderer (`render.py`) uses [Rich](https://rich.readthedocs.io/) console with 4 distinct visual treatments:

- **No style** (default terminal color): text_delta output, tool_call_requested `[tool]` lines, tool_call_finished `OK.`/`ERROR:` results, approval `[action]` lines, turn_finished stats, checkpoint_created line
- **dim**: thinking_delta text (when shown), error with NOTICE: prefix
- **yellow**: error with WARNING: prefix
- **red**: error without recognized prefix (treated as ERROR)
- **Spinner** (Rich status, animated): Active during CAT-THINK phase. Text: "generator thinking... Ns"

### 5.2 ACP Translator Update Types

The ACP translator (`translator.py`) produces 6 core `session/update` types from the event stream:

- **agent_message_chunk**: text_delta, error events (all severity levels mixed as text)
- **agent_thought_chunk**: thinking_delta
- **tool_call**: tool_call_requested (status: pending, with title and kind)
- **tool_call_update**: tool_call_finished (status: completed/failed, with content)
- **usage_update**: turn_finished (used/size/cost)
- **plan**: todo_list tool results (entries with content/priority/status)

Conditional / external (not part of core event translation):

- **user_message_chunk**: user_message during session/load replay only (translator, replaying=True)
- **available_commands_update**: workflows list after session creation (produced by `server.py`, not translator)

Not forwarded: turn_started (empty return), session_started, approval_required, checkpoint_created, prompt_step.

### 5.3 ACP Tool Call Kinds

The translator classifies tools into kinds for client-side rendering:

- **read**: read_file, list_dir, view_content_chunk
- **search**: grep_search, find_by_name, trajectory_search
- **edit**: edit, multi_edit, write_to_file
- **execute**: run_command, command_status
- **fetch**: search_web, read_url_content
- **think**: todo_list
- **other**: skill, ask_user_question

## 6. Proposed Color Scheme

### 6.1 Design Principles Applied

The color scheme must satisfy these design system constraints:

**Brand constraints:**
- **>300ms rule**: Any interaction lasting >300ms gets a visual indicator (DLPHS-IN10 Section 16.2)
- **Frugal language**: Short, precise status messages. No verbose explanations (DLPHS-IN07 Section 9.1)
- **No interruption patterns**: Status integrates calmly, never disrupts content flow (DLPHS-IN07 Section 9.2)
- **CLEN-CARE-FROM**: Clear, engineered, calm. Precision first, then human comfort (DLPHS-IN10 Section 1)
- **Flow pillar**: "Eliminates friction, waiting time, and mental fragmentation" (DLPHS-IN07 Section 2.1)

**Color zone isolation** (DLPHS-IN10 Section 3.10):
- Each semantic zone (Severity, Progress, Confirmation) MUST use its own distinct colors
- Severity colors (red/orange/amber/green) reserved exclusively for errors, warnings, and risk levels
- Progress colors (blue/slate/teal/purple/grey) reserved for lifecycle states (In Progress/Open/Done/Planned/Inactive)
- Never borrow colors across zones. If a screen shows both severity and progress, they must be visually unambiguous.

**Interaction Philosophy** (DLPHS-IN10 Section 11.5):
- **Explorative over instructive**: Status indicators must not force attention. User notices them when needed, ignores them when focused on content.
- **Self-explanatory**: Each status indicator must be understandable without documentation. A "thinking 5s" label needs no explanation.
- **Zero friction**: Reduce cognitive burden. Offer simple defaults (dim for system, spinner for thinking) while allowing depth for power users (debug console for detailed timing).
- **Always just works**: Status signaling must handle weird states gracefully (e.g., provider timeout mid-stream, tool crash, cancelled compaction).

### 6.2 Interaction Category Color Mapping

Each of the 6 categories maps to a distinct visual treatment. Two contexts: CLI (Rich terminal styles) and ACP (design system tokens for client rendering).

**CAT-THINK: Model Thinking**
- **CLI**: Animated spinner, dim text. Current: "generator thinking... Ns". Already correct tone.
- **ACP semantic**: In Progress state. Maps to design system progress-inprogress (`#2C5ED6`, brand active blue)
- **Decision Guide trace**: Step 1 "lifecycle STATE?" → Yes, model is actively working → Progress palette → progress-inprogress (`#2C5ED6`). Semantic role: `interactive-default`.
- **Design rationale**: Thinking is the primary active state. Brand blue = "active work" (DLPHS-IN10 Section 3.8). Animated indicator mandatory (>300ms rule).

**CAT-STREAM: Content Streaming**
- **CLI**: No style (default). Model output should not compete with content for attention.
- **CLI (thinking shown)**: dim. Reasoning is secondary to final output.
- **ACP semantic**: Default text. No special color needed - content IS the activity indicator.
- **Decision Guide trace**: Step 7 "regular DATA with no emotional valence?" → Yes, streaming content is neutral output → `text-primary` (COLOR-NAVY `#14213A`). No color coding.
- **Design rationale**: Content streaming is self-indicating. Adding color would violate "no decoration" principle.

**CAT-TOOL: Tool Execution**
- **CLI**: dim for the `[tool]` line (structural, not content). Tool name and summary visible.
- **ACP semantic**: Tool call kinds already classified (read/search/edit/execute/fetch/think/other). Active tools map to progress-inprogress (`#2C5ED6`); completed tools map to progress-done (`#0891B2` teal).
- **Decision Guide trace**: Step 1 "lifecycle STATE?" → Yes, tools transition through pending → running → completed/failed → Progress palette. Active: progress-inprogress. Done: progress-done. Failed: Step 2 "RISK LEVEL?" → Severity palette (severity-error `#EA2A2A`).
- **Design rationale**: Tools are subordinate to the agent's reasoning. Dim treatment keeps them visible but non-competing with model text. Elapsed time indicator needed for tools >300ms.

**CAT-APPROVE: User Action Required**
- **CLI**: Brand blue equivalent in terminal (bright/bold blue or cyan). The ONE thing that needs attention.
- **ACP semantic**: Already handled by `request_permission` round-trip. Client renders its own UI.
- **Decision Guide trace**: Step 5 "KEY element on this screen?" → Yes, approval prompt is the single actionable element → COLOR-PRIMARY (`#2C5ED6`). Also qualifiable as Step 1 "lifecycle STATE?" → progress-open (awaiting user input, COLOR-SLATE `#536078`), but emphasis wins because approval blocks all progress.
- **Design rationale**: Approval is the single element requiring user action. Brand 10% emphasis rule: "the ONE thing that matters" gets the highlight.

**CAT-SYSTEM: Internal Operations**
- **CLI**: dim. Housekeeping is informational, not actionable.
- **ACP semantic**: Maps to design system `text-secondary` (COLOR-SLATE `#536078`). Low visual weight.
- **Decision Guide trace**: Step 7 "regular DATA with no emotional valence?" → Yes, system metadata is neutral → `text-secondary` (COLOR-SLATE). Not a lifecycle state (compaction has no user-meaningful "done" transition), not a risk level.
- **Design rationale**: System operations (stats, compaction, session setup) are metadata. User should see them but not be distracted. "Whitespace as active design element" principle - system lines create visual breathing room.

**CAT-ERROR: Errors and Warnings**
- **CLI**: Already correct: yellow for WARNING, red for ERROR. Matches severity palette convention.
- **ACP semantic**: Maps to design system severity tokens: error `#EA2A2A` (red), warning `#EA580C` (orange), caution `#CA8A04` (amber)
- **Decision Guide trace**: Step 2 "RISK LEVEL or URGENCY?" → Yes → Severity palette. Provider error = severity-error. Rate limit/transient = severity-warning. NOTICE (informational) → falls through to Step 7, handled by CAT-SYSTEM.
- **Design rationale**: Severity colors are established (DLPHS-IN10 Section 3.6). Zone isolation: severity colors reserved exclusively for errors/warnings, never borrowed for other categories.

### 6.3 Category-to-Style Reference

CLI terminal styles (Rich):

- CAT-THINK: `style="dim"` + animated spinner, text like "thinking 5s" or "retrying 8s"
- CAT-STREAM (text): no style (default)
- CAT-STREAM (thinking): `style="dim"`
- CAT-TOOL: `style="dim"` for `[tool]` line, with elapsed spinner for long operations
- CAT-APPROVE: `style="bold"` or default (interactive prompt, already draws attention by blocking)
- CAT-SYSTEM: `style="dim"` (Turn stats, compaction, notices)
- CAT-ERROR (WARNING): `style="yellow"`
- CAT-ERROR (ERROR): `style="red"`

ACP update semantic tokens (for client-side rendering):

- CAT-THINK: New `agent_status` update type (or `agent_thought_chunk` with status indicator). Color zone: Progress (progress-inprogress `#2C5ED6`)
- CAT-STREAM: `agent_message_chunk` (existing). Color zone: Neutral (`text-primary`)
- CAT-TOOL: `tool_call` / `tool_call_update` (existing, add progress updates). Color zone: Progress (active: inprogress, done: `#0891B2`, failed: Severity)
- CAT-APPROVE: `request_permission` / `elicitation/create` (existing). Color zone: Emphasis (COLOR-PRIMARY)
- CAT-SYSTEM: `usage_update` (existing), extend for compaction. Color zone: Neutral (`text-secondary`)
- CAT-ERROR: Separate from `agent_message_chunk` (currently mixed; needs structured error update). Color zone: Severity

### 6.4 Consistency Rule

All output from the same interaction category MUST use the same visual style. Current violations:

- Turn stats (`turn_finished`): Renders with no style, should be dim (CAT-SYSTEM)
- Compaction line (`checkpoint_created`): Renders with no style, should be dim (CAT-SYSTEM)
- NOTICE errors: Already dim (correct for CAT-SYSTEM)
- Tool `OK.` result: Renders with no style. Should match `[tool]` line style (CAT-TOOL, dim)

## 7. Next Steps

**Design:**
1. **Write SPEC**: Define the status signaling contract for both frontends, covering all 7 dead-air phases with interaction category assignments and the color scheme from Section 6

**HIGH severity fixes (DA-01, DA-02, DA-03):**
2. **Fix DA-01 (ACP)**: Emit a structured thinking indicator on `turn_started` in `translator.py`
3. **Fix DA-01 (CLI)**: Add background timer tick to spinner independent of thinking_delta events
4. **Fix DA-02**: Emit `turn_started` earlier (before message serialization) or add inter-turn status indicator
5. **Fix DA-03**: Add elapsed-time spinner for tool execution in CLI. Add progress updates for ACP tool calls

**MEDIUM severity fixes (DA-04, DA-05) and style consistency:**
6. **Fix DA-04**: Add elapsed indicator during compaction summarizer call
7. **Fix DA-05**: Consider countdown display during retry sleep
8. **Apply color scheme**: Make Turn stats, compaction line, and tool result lines dim (CAT-SYSTEM / CAT-TOOL consistency)

## 8. Sources

**Primary Sources:**
- `LANAUSRX-IN01-SC-SRC-AGNPY`: `src/lana/agent.py` - Core turn loop, event emission points, tool dispatch [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-RNDPY`: `src/lana/render.py` - CLI renderer, 4 styles, spinner logic [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-EVTPY`: `src/lana/events.py` - 12 AgentEvent types with type literals [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-TRNPY`: `src/lana/acp/translator.py` - ACP event-to-update mapping, 6 update types [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-SRVPY`: `src/lana/acp/server.py` - ACP server lifecycle, prompt turn execution [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-BRGPY`: `src/lana/acp/bridge.py` - PermissionBroker and ElicitationBroker [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-CMPPY`: `src/lana/compaction.py` - Context compaction with summarizer LLM call [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-CLIPY`: `src/lana/cli.py` - CLI entry point, run_one_prompt consumer loop [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-SHEPY`: `src/lana/tools/shell_tools.py` - run_command executor, 600s blocking timeout [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-WEBPY`: `src/lana/tools/web_tools.py` - read_url_content (120s deadline), search_web (provider sidecall) [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-ANTPY`: `src/lana/providers/anthropic_adapter.py` - Anthropic streaming, retry logic [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-OAIPY`: `src/lana/providers/openai_adapter.py` - OpenAI streaming, retry logic [VERIFIED]
- `LANAUSRX-IN01-SC-SRC-BASPY`: `src/lana/providers/base.py` - PROVIDER_TIMEOUT, RETRY_DELAYS_SECONDS [VERIFIED]
- `LANAUSRX-IN01-SC-DLPH-IN10`: `specs/UXDesign/_INFO_DELPHIOS_DESIGN_SYSTEM.md [DLPHS-IN10]` - Color system, interaction states, >300ms rule, severity/progress palettes [VERIFIED]
- `LANAUSRX-IN01-SC-DLPH-IN07`: `specs/UXDesign/_INFO_DELPHIOS_BRAND.md [DLPHS-IN07]` - Brand pillars (Flow, Reliability, Safety), communication DO/DONT, frugal language [VERIFIED]

## 9. Document History

**[2026-08-31 17:30]**
- Fixed: Arrow symbol `->` replaced with ` → ` throughout (core-conventions violation, 16 instances)
- Added: Section 6.1 - Color zone isolation constraint (DLPHS-IN10 Section 3.10) and Interaction Philosophy (Section 11.5) as explicit design constraints
- Added: Section 6.2 - Decision Guide trace line per CAT-* category, mapping each color choice through DLPHS-IN10 Section 3.10 seven-step guide to specific palette zone and semantic role
- Added: Section 6.2 CAT-TOOL - Progress palette lifecycle mapping (pending → inprogress → done/failed)
- Changed: Section 6.3 ACP reference - added color zone annotations per update type

**[2026-08-31 17:20]**
- Fixed: AP-PR-06 - expanded CLI, ACP, LLM on first use
- Fixed: SOCAS-01 - clarified 6 core vs 2 conditional ACP update types (summary and Section 5.2 now consistent)
- Fixed: AP-PR-07 - replaced imprecise "SSE event" with "streaming token"
- Fixed: AP-ST-07 - grouped Next Steps by severity (8 items → 3 clusters)
- Fixed: MW-HS-01 - renamed "Category Coverage Matrix" to "Event-to-Category Mapping"

**[2026-08-31 17:10]**
- Initial document created from full codebase audit of 14 source files across agent, renderer, ACP translator, providers, tools, and compaction
