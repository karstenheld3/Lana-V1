# INFO: Lana Robustness and Responsiveness Hazard Analysis

**Doc ID**: LANAAGNT-IN03
**Goal**: Identify problems in the implemented MVP-1/MVP-2 codebase that can cause 1) crashes from unhandled errors, 2) avoidable blocking/hanging scenarios, 3) unresponsive user experiences mitigable by up-front notices or progress indicators
**Timeline**: Created 2026-08-30

**Depends on:**
- `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` and `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` for specified error handling (EC-14..29)
- `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` and `_IMPL_LANA_MVP-2_ACP.md [LANAACPB-IP01]` for ACP error handling (FR-11, EC-01..23)
- `src/lana/` implementation as analyzed (all findings verified by direct code read unless labeled [ASSUMED])

## Summary

- **4 crash findings span 2 exception surfaces (startup + REPL)**: the CLI catches only `ConfigError` at startup and only `UnknownWorkflowError` in the REPL - any other exception (disk full on JSONL append, permission error creating `.lana/`, locked prompt system file) kills the process with a raw traceback. The ACP server has broad catches and survives the same failures [VERIFIED]
- **The ACP server has one total-hang hazard**: a client that stops reading stdout blocks `sys.stdout.write` on the event loop thread - the whole server freezes including cancel processing [VERIFIED]
- **Cancellation cannot stop executor-thread tools**: `task.cancel()` abandons the await but the worker thread and its child `pwsh` process keep running; process exit then blocks on the `concurrent.futures` atexit join until the tool finishes [VERIFIED mechanism; join behavior VERIFIED - stdlib docs: "All threads enqueued to ThreadPoolExecutor will be joined before the interpreter can exit"]
- **`command_status` accepts unbounded `WaitDurationSeconds`**: the schema advises max 60 s but nothing enforces it - one tool call can block its dispatch slot for hours [VERIFIED]
- **Three dead-air UX moments dominate**: nothing renders between Enter and the first token (reasoning models: 10-60 s), thinking is hidden by default (long silent reasoning stretches), and compaction runs a silent Summarizer call between turns [VERIFIED]
- **Provider SDK defaults hide latency**: ~600 s request timeout and 2 silent retries with backoff mean a degraded provider looks like a frozen agent for minutes [VERIFIED - OpenAI `_constants.py`: `DEFAULT_TIMEOUT = httpx.Timeout(timeout=600, connect=5.0)`, `DEFAULT_MAX_RETRIES = 2`; Anthropic `_constants.py` identical]
- Specified fail-safes (EC-16/17/20/21, compaction no-op, corrupt-line skip, denial paths) are implemented and tested - this analysis found no gap in SPECed error handling, only in UNSPECIFIED error surfaces [VERIFIED]

## Table of Contents

1. [Method and Scope](#1-method-and-scope)
2. [Class CR: Crash Hazards](#2-class-cr-crash-hazards)
3. [Class BL: Blocking and Hang Hazards](#3-class-bl-blocking-and-hang-hazards)
4. [Class UX: Unresponsive Experience Hazards](#4-class-ux-unresponsive-experience-hazards)
5. [Non-Findings](#5-non-findings)
6. [Next Steps](#6-next-steps)
7. [Sources](#7-sources)
8. [Document History](#8-document-history)

## 1. Method and Scope

Re-read of all 4 planning documents (SPEC/IMPL for MVP-1 and MVP-2) followed by targeted code inspection of every I/O boundary: startup, REPL, turn loop, tool executors, provider adapters, session store, compaction, renderer, ACP server. Each finding states evidence (file), trigger, consequence, mitigation, and effort.

Mitigations for UX findings should conform to `LOGGING-RULES-USER-FACING.md` (LG-UF-03 progress indicators, LG-UF-04 activity boundaries, LG-UF-05 error messages) and `LOGGING-RULES-APP-LEVEL.md` (LG-AP-02 error context). CR error messages should follow LG-UF-05 (what happened, why, what to do).

Severity meaning:
- **[HIGH]** - process dies or hangs, or the user is misled for minutes
- **[MEDIUM]** - degraded behavior with workaround, or seconds-scale confusion
- **[LOW]** - edge condition, cosmetic, or already partially mitigated

## 2. Class CR: Crash Hazards

Unhandled expected/unexpected errors that kill the process.

### CR-01: CLI startup catches only ConfigError [HIGH]

- **Evidence**: `cli.main` wraps `build_runtime` in `except ConfigError` only; `SessionStore.create` does `mkdir`/`open` unguarded; `loader.py` `read_text` has `errors="replace"` for encoding but no `OSError` handling
- **Trigger**: read-only workspace (cannot create `.lana/sessions/`), locked/unreadable prompt system file, `PermissionError` on `config/.api-keys.txt`
- **Consequence**: raw traceback at startup - violates LANAAGNT-IG-05 ("every user-visible failure produces a self-contained error message")
- **Mitigation**: catch `OSError` alongside `ConfigError` in `main` and in `build_runtime`'s file-touching steps; name path + corrective action. Same class as resolved `LANAAGNT-BG-0005` (resume missing file), which fixed one instance, not the category
- **Effort**: small (one except clause + message)

### CR-02: REPL dies on any unexpected turn exception [HIGH]

- **Evidence**: `cli.repl` catches only `UnknownWorkflowError` around `run_one_prompt`; `cli.run_headless` identical
- **Trigger**: `OSError` from `session.append` (disk full, file lock by a backup tool), a renderer defect, any uncaught bug in the turn path
- **Consequence**: whole process dies mid-session with a traceback; conversation JSONL survives (resumable) but the user loses the live session and any background processes
- **Mitigation**: broad `except Exception` in the REPL loop - print self-contained error, keep the REPL alive; the session file allows continuing. The ACP server already does exactly this (`handle` broad catch, FR-11) - the CLI deserves the same guarantee
- **Effort**: small

### CR-03: CLI/ACP asymmetry on session-write failures [MEDIUM]

- **Evidence**: `agent.emit` -> `session.append` is unguarded by design (crash-safety = flush per line); ACP `run_prompt_turn` broad-catches it into a JSON-RPC error response; CLI has no equivalent (CR-02 path)
- **Trigger**: disk full mid-turn
- **Consequence**: identical fault, different outcome per frontend - ACP degrades gracefully, CLI dies
- **Mitigation**: covered by CR-02 fix; alternatively guard `emit` itself with a one-time warning + in-memory-only fallback (rejected leaning: silently losing the audit trail contradicts IG-02 - prefer loud failure that keeps the REPL alive)
- **Effort**: covered by CR-02

### CR-04: Compaction post-Summarizer steps outside the fail-safe [LOW]

- **Evidence**: `compaction.make_compactor` wraps only `run_summarizer` in try/except (EC-17); `split_sections`/`build_checkpoint`/tail-trim run unprotected afterwards
- **Trigger**: none known today - deterministic string operations; a future defect there would crash the turn consumer
- **Consequence**: turn dies after a PAID Summarizer call
- **Mitigation**: widen the try to the whole compact body (same EC-17 warn-and-continue semantics)
- **Effort**: trivial

## 3. Class BL: Blocking and Hang Hazards

Threads or loops that block where they need not.

### BL-01: ACP stdout backpressure freezes the entire server [HIGH]

- **Evidence**: `jsonrpc.Connection._write_stdout` runs `sys.stdout.write` + `flush` on the event loop thread; every `session/update` flows through it
- **Trigger**: client process stops draining Lana's stdout (client bug, breakpoint, pipe buffer full during a burst such as session/load replay)
- **Consequence**: `write` blocks -> event loop frozen -> no cancel, no EOF detection, no further processing; from outside indistinguishable from a dead agent
- **Mitigation**: route writes through a dedicated writer thread fed by a `queue.Queue` (bounded; on overflow, log to stderr and drop-or-block by policy) - the read loop and turn tasks stay live; cancel keeps working
- **Effort**: medium (one writer thread + queue in `Connection`, tests unaffected - same wire bytes)

### BL-02: Cancellation abandons, but does not stop, executor-thread tools [MEDIUM]

- **Evidence**: `agent.dispatch_call` uses `run_in_executor` in ACP mode; `asyncio.Task.cancel` cancels the await, never the thread; `shell_tools` child `pwsh` keeps running; `concurrent.futures.thread` joins workers at interpreter exit
- **Trigger**: `session/cancel` during a long `run_command` (up to 600 s) or `command_status` wait; then stdin EOF
- **Consequence**: turn reports cancelled (correct per FR-10 - completed calls kept, note appended) but the tool still runs to completion invisibly; process exit blocks until the worker thread finishes [VERIFIED - stdlib docs confirm atexit join]. In ACP mode, a subsequent `session/prompt` may start while the abandoned executor thread still mutates the workspace (server checks `active_task.done()`, not whether the executor thread terminated)
- **Mitigation**: 1) track live `Popen` handles in `ToolContext.background_processes` plus a current-foreground slot, `terminate()` them on cancel/EOF; 2) cap executor tool time (BL-03 covers the worst offender). Full thread interruption is not achievable in Python - process-kill is the honest lever
- **Effort**: medium

### BL-03: command_status WaitDurationSeconds unbounded [MEDIUM]

- **Evidence**: `shell_tools.execute_command_status` busy-waits `time.sleep(0.05)` until `deadline = now + WaitDurationSeconds`; the verbatim Cascade schema only ADVISES "Do not wait for a command for more than 60 seconds"
- **Trigger**: Generator passes a large value (models do follow tool descriptions, but nothing enforces it)
- **Consequence**: CLI: main thread blocked (Ctrl+C still works); ACP: executor thread blocked, turn uncancellable-in-effect for the duration (BL-02)
- **Mitigation**: clamp the wait to 60 s server-side (description already promises that bound - clamping cannot surprise the model); note the clamp in the result on trigger
- **Effort**: trivial

### BL-04: session/new and session/load block the ACP read loop [MEDIUM]

- **Evidence**: `server.build_session_runtime` calls `build_runtime` directly on the event loop; NFR-03 budgets up to 2 s for prompt system load; session/load additionally parses the whole JSONL and replays N updates
- **Trigger**: every session creation; large prompt systems or long sessions stretch it
- **Consequence**: no message processing (cancel, ping, second client request) during the load; multi-second unresponsiveness classified as EC-22-adjacent but unhandled for the session-setup path
- **Mitigation**: `await loop.run_in_executor(None, build_runtime, ...)` - the function is self-contained and thread-safe for this use (stdout redirect must move inside the callable)
- **Effort**: small
- **Note**: the same call in the CLI is fine - nothing else needs the thread at startup

### BL-05: No explicit provider timeouts - SDK defaults govern stalls [MEDIUM]

- **Evidence**: `openai.AsyncOpenAI(api_key=...)` and `anthropic.AsyncAnthropic(api_key=...)` constructed without `timeout`/`max_retries`; defaults ~600 s total with 2 retries [VERIFIED - both SDKs define `DEFAULT_TIMEOUT = httpx.Timeout(timeout=600, connect=5.0)` and `DEFAULT_MAX_RETRIES = 2` in `_constants.py`]
- **Trigger**: TCP half-open, proxy stall, provider incident mid-stream
- **Consequence**: a dead turn occupies up to ~10 minutes; CLI Ctrl+C and ACP cancel DO work (the await is cancellable) - this is a hang-duration hazard, not a hard hang
- **Mitigation**: explicit `timeout=httpx.Timeout(connect=10, read=120, ...)` per adapter (config-surfaced), `max_retries` owned by Lana so retries become visible (UX-02)
- **Effort**: small

### BL-06: Orphaned background pwsh processes at exit [LOW]

- **Evidence**: `shell_tools` background table holds `Popen` handles; no terminate-on-exit anywhere; reader threads are daemon (die silently)
- **Trigger**: `/exit` or EOF while a background command runs
- **Consequence**: child processes outlive Lana (leaked work, locked files); not a Lana hang
- **Mitigation**: iterate `background_processes` at shutdown, `terminate()` + short `wait()`; print one line naming survivors
- **Effort**: small

### BL-07: read_url_content total time unbounded by slow trickle [LOW]

- **Evidence**: `urllib.request.urlopen(request, timeout=30)` - the timeout applies per socket operation, not to the whole transfer
- **Trigger**: hostile or broken server dripping bytes (slow-loris pattern)
- **Consequence**: a fetch can exceed 30 s arbitrarily while never idling long enough to trip the timeout; bounded in damage by the 5 MB cap
- **Mitigation**: wall-clock deadline around the read loop (read in chunks, abort past e.g. 120 s)
- **Effort**: small

## 4. Class UX: Unresponsive Experience Hazards

Expected waits that look like hangs because nothing tells the user.

### UX-01: Dead air between Enter and first token [HIGH]

- **Evidence**: `render.Renderer.handle` has no `turn_started` branch - nothing prints when the Generator call begins; reasoning models commonly take 10-60 s to first visible output
- **Consequence**: the user cannot distinguish "model thinking" from "process hung" - the highest-frequency confusion moment in every session
- **Mitigation**: render a status line on `turn_started` (`  generator thinking...` or a rich spinner via `console.status`), clear it on the first delta; ACP clients render their own progress - CLI-only fix
- **Effort**: small

### UX-02: Thinking hidden by default extends the dead air [MEDIUM]

- **Evidence**: `Renderer.show_thinking = False` and no CLI flag toggles it; `thinking_delta` events arrive and are dropped
- **Consequence**: with UX-01 fixed the spinner helps, but minutes-long reasoning still shows zero content although content EXISTS
- **Mitigation**: either default `show_thinking` to dim-styled on, or add `--show-thinking`; cheapest honest signal: keep thinking hidden but tick the status line (`thinking... 23s`)
- **Effort**: small

### UX-03: Silent provider retries [MEDIUM]

- **Evidence**: SDK-internal retries (BL-05) emit no event; the user waits through backoff with no signal [VERIFIED - SDK retry with exponential backoff 0.5-8 s per `_constants.py`]
- **Mitigation**: own the retry loop in the adapters: on retryable status, emit an `error`-severity-free notice event (`Provider 429 - retrying in 8s (attempt 2/3)...`); requires `max_retries=0` on the SDK client
- **Effort**: medium (adapter retry loop + one new rendered line; event enum unchanged - reuse ErrorEvent with WARNING prefix like EC-17 does)

### UX-04: Compaction runs silently before its result line [MEDIUM]

- **Evidence**: `make_compactor` yields events only AFTER the Summarizer call; the CLI shows `Compacted: ...` when it is over; the ACP translator forwards `checkpoint_created` not at all (documented v1 omission)
- **Consequence**: a multi-second silent gap between turns exactly when the session is already at its largest and slowest; ACP users get dead air with no trailing explanation either
- **Mitigation**: yield a notice event (`Compacting context (~N tokens)...`) BEFORE `run_summarizer`; ACP: translate that notice as `agent_message_chunk` or keep the stderr log - the up-front CLI line is the main win
- **Effort**: small

### UX-05: Resume parses silently before reporting [LOW]

- **Evidence**: `build_runtime` prints `Resumed session ...: N messages.` only after `resume_session` parsed the full JSONL (multi-MB files: noticeable)
- **Mitigation**: print `Resuming '<file>'...` before parsing (matches the LOG-AP-03 action-before-result pattern already used for prompt system loading)
- **Effort**: trivial

### UX-06: Skill folder scan can stretch startup invisibly [LOW]

- **Evidence**: `loader.load_skill` runs `folder.rglob("*")` per skill; a skill folder containing a dependency tree (e.g., an accidental `node_modules`) scans everything inside the 2 s NFR-03 budget assumption
- **Mitigation**: none needed today (IPPS max 160 files); if startup regressions appear, cap the listing with a `<truncated>` marker like tool results
- **Effort**: defer

## 5. Non-Findings

Verified robust during this analysis (no action):

- **Specified fail-safes hold**: EC-16 provider error -> error event; EC-17 Summarizer failure -> warn + no truncation; EC-20 context overflow -> advisory message, no retry; EC-21 corrupt JSONL lines -> broad `except Exception` skip with count; EC-22/23 unknown tool / invalid args -> tool errors
- **run_command blocking is bounded**: 600 s join, then automatic move to background with a self-explaining result - no unbounded foreground block
- **ACP router never crashes the connection**: broad catches on requests AND notifications (FR-11), tested by the hostile battery (TP01-TC-10)
- **Renderer injection**: untrusted payloads print with `markup=False` everywhere (BG-0004 fix holds)
- **Ctrl+C paths**: REPL prompt, approval prompts, question prompts, and the turn loop all catch `KeyboardInterrupt`; cancellation note semantics per FR-04

## 6. Next Steps

Suggested order (crash class first, then the cheap high-value items):

1. **CR-01 + CR-02/CR-03**: broaden CLI startup and REPL exception handling to `OSError`/`Exception` with IG-05-conformant messages (small, kills both crash classes)
2. **BL-03**: clamp `WaitDurationSeconds` to the 60 s the description promises (trivial)
3. **UX-01 + UX-02**: `turn_started` status line with elapsed ticker (small, biggest perceived-quality win)
4. **UX-04**: pre-compaction notice event (small)
5. **BL-01**: ACP writer thread for stdout (medium - decide before any real-client usage beyond smoke tests)
6. **BL-05 + UX-03**: explicit SDK timeouts + Lana-owned visible retries (medium, one config surface)
7. **BL-02 + BL-06**: process-handle cleanup on cancel/exit (medium)
8. **CR-04, UX-05, BL-07**: trivial hardening batch
9. Decision needed: which items enter an MVP-2 hardening IMPL vs MVP-3 backlog - `/write-impl-plan` once scoped

## 7. Sources

**Primary Sources (all analyzed 2026-08-30 by direct read):**
- `LANAAGNT-IN03-SC-SPEC-MVP1`: `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` - FR-04/07/08/12/14, EC references, IG-05 [VERIFIED]
- `LANAAGNT-IN03-SC-IMPL-MVP1`: `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` - EC-14..29 specified failure handling [VERIFIED]
- `LANAAGNT-IN03-SC-SPEC-MVP2`: `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` - FR-10/11, IG-05 cancellation semantics [VERIFIED]
- `LANAAGNT-IN03-SC-IMPL-MVP2`: `_IMPL_LANA_MVP-2_ACP.md [LANAACPB-IP01]` - EC-01..23 [VERIFIED]
- `LANAAGNT-IN03-SC-CODE-CLI`: `src/lana/cli.py` - startup/REPL exception surface (CR-01/02/03, UX-05) [VERIFIED]
- `LANAAGNT-IN03-SC-CODE-AGNT`: `src/lana/agent.py` - dispatch, cancellation, executor seam (BL-02) [VERIFIED]
- `LANAAGNT-IN03-SC-CODE-PROV`: `src/lana/providers/openai_adapter.py`, `anthropic_adapter.py` - client construction without timeouts (BL-05, UX-03) [VERIFIED code and SDK defaults]
- `LANAAGNT-IN03-SC-CODE-SHTL`: `src/lana/tools/shell_tools.py` - 600 s bound, background table, unbounded wait (BL-03/06) [VERIFIED]
- `LANAAGNT-IN03-SC-CODE-WEBT`: `src/lana/tools/web_tools.py` - fetch timeout semantics (BL-07) [VERIFIED]
- `LANAAGNT-IN03-SC-CODE-CMPT`: `src/lana/compaction.py` - EC-17 scope, silent Summarizer call (CR-04, UX-04) [VERIFIED]
- `LANAAGNT-IN03-SC-CODE-RNDR`: `src/lana/render.py` - no turn_started branch, show_thinking default (UX-01/02) [VERIFIED]
- `LANAAGNT-IN03-SC-CODE-ACPS`: `src/lana/acp/server.py`, `acp/jsonrpc.py` - stdout write on loop thread, session build on loop (BL-01/04) [VERIFIED]
- `LANAAGNT-IN03-SC-CODE-SESS`: `src/lana/session.py` - unguarded append, broad resume skip (CR-03, non-finding EC-21) [VERIFIED]

## 8. Document History

**[2026-08-30 16:15]**
- Changed: applied 4 reconciled findings from `/critique` + `/reconcile` (LANAAGNT-IN03-RV01): Summary precision ("4 findings / 2 surfaces"), 3 [ASSUMED] relabeled to [VERIFIED] with SDK/stdlib source references, logging-rules cross-reference added to Method section, BL-02 concurrent-mutation-after-cancel consequence added

**[2026-08-30 15:20]**
- Initial hazard analysis created: 4 crash findings (CR), 7 blocking findings (BL), 6 responsiveness findings (UX), 5 verified non-findings, prioritized next steps
