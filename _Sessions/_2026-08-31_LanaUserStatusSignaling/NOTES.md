# Session Notes

**Doc ID**: LANAUSRX-NOTES

## Initial Request

````text
I want to improve the user communication of the agent. We dont want any unresponsive states where the user cannot differentiate between a stalled agent and a working agent.

For this we need to inspect every part of the interaction chain, identify all cases and decide how we signify the correct status and progress to the user.
````

## Session Info

- **Started**: 2026-08-31
- **Goal**: Audit the full interaction chain for dead-air spots and design status/progress signaling so the user always knows whether Lana is working or stalled
- **Operation Mode**: IMPL-CODEBASE
- **Output Location**: `src/lana/` (render.py, agent.py, events.py, acp/translator.py, cli.py, compaction.py, providers, tools)

## Agent Instructions

- Two frontends: CLI (render.py) and ACP/Devin Desktop (acp/translator.py). Both must be covered.
- Do not add emojis to console output.
- Respect existing `markup=False` pattern in render.py (BG-0004: untrusted payloads).
- Debug console (`debuglog.py` / `debug_viewer.py`) is a diagnostic tool, not user-facing status. Don't change its contract.

## Design System Reference

**CRITICAL**: The design system's internal name (see `!NOTES.md`) MUST NEVER appear in shipped code, binaries, UI output, config files, commit messages, or any artifact that reaches end users. Reference as "the design system" or by Doc ID only.

**Applicable brand principles for CLI status signaling** (distilled from DLPHS-IN07 + DLPHS-IN10):

- **Flow pillar**: "Eliminates friction, waiting time, and mental fragmentation." Status signals must prevent the user from wondering whether the agent is stuck. Dead air = broken flow.
- **Reliability pillar**: "No surprises, no worries. Predictable, verified results." If something takes time, say so upfront. Never silently wait.
- **Safety pillar**: "Nothing happens that you didn't approve." Approval prompts are correctly signaled (F5). No change needed there.
- **Design principle (CLEN-CARE-FROM)**: CLear ENgineered, CAlm RElaxed, FResh MOdern. Status messages must be precise and informative, not noisy or decorative.
- **Loading states >300ms** (DLPHS-IN10 Section 16.2): Any operation taking >300ms MUST show a loading indicator. This is the threshold for user-perceptible delay.
- **No interruption patterns** (DLPHS-IN07 Section 9.2): Don't add unnecessary confirmations or noisy notifications. Status should be calm and integrated, not disruptive.
- **Frugal language** (DLPHS-IN07 Section 9.1): Zero overhead in messaging. "Thinking 5s" not "The AI model is currently processing your request, please wait..."
- **Error messages**: State what failed + what to do next (DLPHS-IN10 Section 12.5). Already partially implemented (ErrorEvent rendering).

## Current Phase

**Phase**: DOCUMENT (complete) -> DESIGN (next)
**Workflow**: /solve (knowledge output: analysis + design before implementation)
**Assessment**: INFO document written: `_INFO_LANAUSRX_INTERACTION_CHAIN.md [LANAUSRX-IN01]`. Awaiting user review before SPEC.

## Key Decisions

(pending)

## Important Findings

### Interaction Chain: Complete Dead-Air Inventory

**7 phases** identified where the user may see zero output. Severity rated by duration and frequency.

#### F1. LLM Request Wait (turn_started -> first content delta) [HIGH]
- **Duration**: 2-30+ seconds (model-dependent, cache-miss worst case)
- **CLI**: Spinner "generator thinking... Ns" (FR-16 UX-01/02). Ticks elapsed seconds via hidden thinking deltas.
- **ACP**: `turn_started` yields ZERO updates (`translator.py:45-48`, returns `[]`). Client shows nothing until first `text_delta` or `tool_call_requested`.
- **Gap**: CLI spinner is good but stops updating when no thinking deltas arrive (pure dead air between request send and first SSE event). ACP has no thinking indicator at all.

#### F2. Tool Execution (tool_call_requested -> tool_call_finished) [HIGH]
- **Duration**: 0-600s (run_command Blocking), 2-15s (search_web), up to 120s (read_url_content fetch)
- **CLI**: One `[tool]` line at start, one `OK.` line at end. Nothing in between.
- **ACP**: One `tool_call` update (status: pending), then `tool_call_update` (completed/failed). Nothing in between.
- **Gap**: Long-running tools (`run_command` Blocking, `read_url_content` on slow servers, `search_web`) show zero progress. The `run_command` Blocking case is worst: up to 600s of dead air.

#### F3. Provider Retries (retryable error -> retry delay -> re-attempt) [MEDIUM]
- **Duration**: 2s + 8s delays (RETRY_DELAYS_SECONDS)
- **CLI**: ErrorEvent renders yellow WARNING. Visible.
- **ACP**: ErrorEvent -> `agent_message_chunk`. Appears as text, not a structured status.
- **Gap**: ACP representation is unstructured. User sees retry text mixed with agent output.

#### F4. Compaction / Summarizer Call [MEDIUM]
- **Duration**: 5-30s for the summarizer LLM call
- **CLI**: NOTICE printed before, "Compacted" line after. Nothing during the LLM call itself.
- **ACP**: NOTICE -> inline text. CheckpointCreated -> NOT forwarded (documented omission in translator.py:72-74).
- **Gap**: During the summarizer call (which is a full LLM round trip), zero progress in either frontend.

#### F5. Approval Wait (user action required) [LOW - by design]
- **Duration**: Unbounded (waiting for human)
- **CLI**: Clear prompt "[action] detail, Approve? [y/n/a]"
- **ACP**: PermissionBroker round-trip
- **Gap**: Correctly signaled in both frontends. Not a problem.

#### F6. Session Build at Startup [LOW]
- **Duration**: 0.5-5s
- **CLI**: Sequential prints (roles banner, loading prompt system, policy)
- **ACP**: All redirected to stderr. Client sees nothing until session/new response.
- **Gap (ACP only)**: No progress during session build. Duration usually short enough to be acceptable.

#### F7. Session Resume / Replay [LOW-MEDIUM]
- **Duration**: 1-30s for large sessions
- **CLI**: "Resuming..." then "Resumed session: N messages"
- **ACP**: session/load replays updates (translator replaying=True). No overall progress bar.
- **Gap**: CLI shows nothing during parse. ACP replays but no progress indicator on how far along.

### Screenshot Analysis

The screenshot shows:
- Left: Main console with the cursor blinking after the Turn stats line. The model's next LLM request is being prepared or in flight. No spinner or indicator visible.
- Right: Debug console shows the timeline of operations. The debug console reveals the agent IS working (request/response pairs visible), but the main console gives no such signal.

**Core problem**: After `Turn: in=... out=...`, before the next `[tool]` line or text output, there is dead air. The user cannot distinguish "preparing next LLM call" from "crashed/stuck".

## Topic Registry

**Global topics** (registered in ID-REGISTRY.md):
- `LANAUSRX` - Lana User Status/Progress Experience (CLI + ACP dead-air elimination)

**Subtopics** (session-local):
- (none yet)

## Topic Folders

(none)

## Step Folders

(none)

## Bug List

- (none yet)

## Significant Prompts Log

(none yet)
