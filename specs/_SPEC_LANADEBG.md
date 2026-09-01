# SPEC: Lana Debug Console

**Doc ID**: LANADEBG-SP01
**Feature**: debug-console
**Goal**: Specify a second console window showing real-time debug/timing output for LLM calls, tool execution, and ACP communication, activated by `--debug-console`, working in CLI and ACP modes.
**Timeline**: Created 2026-08-31
**Target file(s)**:
- `src/lana/debuglog.py` (new)
- `src/lana/debug_viewer.py` (new)
- `src/lana/cli.py`
- `src/lana/agent.py`
- `src/lana/providers/openai_adapter.py`
- `src/lana/providers/anthropic_adapter.py`
- `src/lana/acp/server.py`
- `src/lana/acp/bridge.py`

**Depends on:**
- `specs/_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` for AgentEvent model and turn loop
- `specs/_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` for ACP stdio constraints

**Does not depend on:**
- Existing `--debug` payload dumps (`dump_debug`) - stays unchanged, complementary concern

## MUST-NOT-FORGET

- ACP mode: stdout is JSON-RPC transport - debug output MUST NOT touch stdout or stdin
- Pre-calculate every logged value BEFORE the write call (durations, tokens, cost)
- Immediate flush per line - no buffering, no batching
- Viewer death MUST NOT crash or stall Lana - degrade silently, log once to stderr
- Never log per-delta events (text deltas, session/update) - summary lines only
- Zero overhead when flag absent - one None check per call site

## Table of Contents

1. [Scenario](#1-scenario)
2. [Context](#2-context)
3. [Domain Objects](#3-domain-objects)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Design Decisions](#6-design-decisions)
7. [Implementation Guarantees](#7-implementation-guarantees)
8. [Key Mechanisms](#8-key-mechanisms)
9. [Action Flow](#9-action-flow)
10. [Data Structures](#10-data-structures)
11. [User Actions](#11-user-actions)
12. [UX Design](#12-ux-design)
13. [Logging Requirements](#13-logging-requirements)
14. [Technical Constraints](#14-technical-constraints)
15. [Edge Cases](#15-edge-cases)
16. [Document History](#16-document-history)

## 1. Scenario

**Problem:** No real-time visibility into where Lana loses time, spends money, or fails. Diagnosing ACP latency, LLM cost/cache behavior, and tool failures requires reading session JSONL files after the fact. In ACP mode there is no visible output at all (stdout is protocol, stderr is buried in the client's process log).

**Solution:**
- `--debug-console` opens a second console window at startup (CLI and ACP modes)
- Lana writes one structured JSONL line per operation to the viewer's stdin pipe
- The viewer renders colorized, aligned, human-readable lines in real time
- The debug stream is the single source of truth for: ACP message flow and timing, LLM latency/tokens/cost/cache, tool call success/failure/latency

**What we don't want:**
- Per-delta logging (text/thinking deltas, session/update notifications) - noise kills signal
- Buffered/batched writes - lines must appear instantly
- Any interference with the main console UX or the ACP stdio protocol
- Crash or stall of the agent when the viewer window is closed

## 2. Context

Lana is an event-sourced CLI agent: the turn loop yields AgentEvents consumed by SessionStore (JSONL persistence), Renderer (main console), and EventTranslator (ACP updates). None of these observers carry timing or cost-per-operation data at operation granularity. The debug console is a fourth, independent output channel fed by explicit instrumentation calls - not an AgentEvent observer, because its data (durations, wire-level ACP traffic, adapter retries) does not exist in the event stream.

## 3. Domain Objects

### DebugLog

A **DebugLog** is the process-wide writer that owns the viewer subprocess and its stdin pipe.

**Key properties:**
- `viewer` - spawned subprocess handle (new console window)
- `dead` - set on first pipe failure; all subsequent calls become no-ops

**Lifecycle:** enabled once at startup when `--debug-console` or `--log-dir` present; lives for the process lifetime; never re-spawned.

**Optional log file:** when `--log-dir` is given, every JSONL line is also written to a timestamped file (`lana-debug-YYYY-MM-DD_HH-MM-SS.jsonl`) in the specified directory. File write failures disable file logging independently of the viewer pipe.

### DebugLine

A **DebugLine** is one JSONL object written to the pipe. Common fields:
- `ts` - wall-clock time `YYYY-MM-DD HH:MM:SS.mmm` (full date for session-JSONL correlation, LOG-AP-01; the viewer displays time only)
- `dom` - domain: `llm`, `tool`, `acp`, `app`
- `op` - operation name within the domain
- op-specific fields (see Data Structures)

### Viewer

The **Viewer** is a subprocess running in its own console window. Reads JSONL lines from stdin, renders them colorized and aligned. On stdin EOF (Lana exited) it announces the closed connection and waits for a keypress so output stays readable.

## 4. Functional Requirements

**LANADEBG-FR-01: CLI Flag**
- `--debug-console` opens the viewer window at startup, before any instrumented operation
- Works in interactive REPL, headless (`-p`, `--prompt-file`), and ACP (`--acp`) modes
- Independent of `--debug` (payload dumps) - both can be active simultaneously

**LANADEBG-FR-07: Log File Output**
- `--log-dir DIR` writes every debug JSONL line to a timestamped file in DIR
- File naming: `lana-debug-YYYY-MM-DD_HH-MM-SS.jsonl`
- Directory auto-created if it does not exist
- Can be used with or without `--debug-console`: with both, lines go to viewer AND file; with `--log-dir` alone, lines go to file only (stderr fallback on non-Windows)
- File write failure disables file logging with one stderr warning; viewer pipe unaffected
- ACP registry entry for `lana-debug` passes `--log-dir E:/Dev/Lana-V1/dist/logs`

**LANADEBG-FR-02: LLM Domain Coverage**
- Request start: role name, provider, model, message count, tool count (generator and summarizer roles)
- First streamed content delta: time-to-first-token in ms (generator; includes any retry delays - retry lines explain the gap)
- Response complete: total duration ms, input tokens, cache-read tokens, cache-write tokens, output tokens, cost USD, tool call count
- Retries: one line per adapter retry notice (error type, attempt, delay)
- Errors: error text (first 300 chars); generator errors include duration ms
- Websearch side-call: one `sidecall` line with duration ms and result count - provider web-search wrappers surface no usage/tokens, so no response line exists (failures appear as tool `end` errors)

**LANADEBG-FR-03: Tool Domain Coverage**
- Call start: tool name, one-line argument summary
- Call end: tool name, duration ms, status (ok, error, cancelled), result char count
- Errors: status plus error text (first 300 chars)
- Approval gate: action, resolution (approved, denied), wait duration ms

**LANADEBG-FR-04: ACP Domain Coverage**
- Inbound: every request and notification (method, id)
- Outbound responses: method, id, handler duration ms, ok or error code (all methods except session/prompt)
- Prompt turn summary: one `turn` line per session/prompt - id, full turn duration ms, stop reason, session/update count (individual updates never logged)
- Agent-originated round-trips (permission, elicitation): method, round-trip duration ms, outcome (ok, cancelled, client error)
- Lifecycle: initialize, session/new, session/load, cancellations, stdin EOF

**LANADEBG-FR-05: App Domain Coverage**
- Startup: mode (repl, headless, acp), version
- Roles banner: one `roles` line when the runtime is built (per ACP session; config is not loaded at startup time)
- Prompt system loaded: rule/workflow/skill counts, load duration ms
- Session created or resumed: session file name; resume carries the parse duration ms
- Compaction announce: `compaction_start` with projected tokens and threshold (the trigger reason)
- Compaction report: truncated and kept message counts, checkpoint char size
- Compaction failure after the summarizer call: `compaction_failed` with error text (the silent-continue path stays visible)

**LANADEBG-FR-06: Viewer Rendering**
- One line per DebugLine: dim timestamp, color-coded domain tag, aligned operation, detail fields
- Errors rendered red, warnings yellow
- On stdin EOF: print connection-closed notice, keep window open until keypress

## 5. Non-Functional Requirements

**LANADEBG-NFR-01: Performance - main-thread write cost**
- Disabled: one None check per call site (nanoseconds)
- Enabled: JSON serialize + pipe write + flush, no other work on the caller's thread
- All values pre-computed by the caller before the log call (durations from monotonic clocks, cost from the existing cost engine)
- Verification: no measurable full-run duration difference with viewer attached [TESTED 2026-08-31: scripted headless runs, 3x each - without 686 ms avg, with 633 ms avg - delta within run-to-run noise]

**LANADEBG-NFR-02: Reliability - viewer independence**
- Viewer crash or window close: Lana continues; first pipe failure disables logging permanently for the process and prints one stderr warning
- Lana exit: viewer window stays open (EOF notice + keypress wait) so the tail of the log stays readable

**LANADEBG-NFR-03: Observability - immediate flush**
- Every line flushed at write time; a line is visible in the viewer before the next instrumented operation starts

## 6. Design Decisions

**LANADEBG-DD-01:** Pipe-connected spawned console (Option B). Main process writes JSONL to the viewer's stdin pipe. Rationale: direct transport, no filesystem dependency, clean separation; chosen by user over file-tail (A) and queue/dual-sink (C).

**LANADEBG-DD-02:** Module-level singleton, not AppConfig field. Rationale: ACP mode needs the console before any session/AppConfig exists (server starts, sessions come later); adapters and jsonrpc layers have no AppConfig access. Precedent: `_ADAPTER_CACHE` in providers.

**LANADEBG-DD-03:** Viewer is Lana itself re-invoked with a hidden `--debug-viewer` flag. Rationale: works identically from source (`python -m lana`) and PyApp binary (`sys.executable` is the PyApp-managed interpreter, module re-invocation resolves [ASSUMED - not yet verified with a built binary; verify after next rebuild]); no second artifact to ship.

**LANADEBG-DD-04:** Explicit instrumentation calls, no decorators or event-model changes. Rationale: the needed data (TTFT, wire traffic, retry attempts) does not exist in AgentEvents; decorators cannot see mid-stream timing; explicit calls keep the hot path visible and greppable.

**LANADEBG-DD-05:** Summary-level logging only - never per-delta. Rationale: hundreds of text deltas per turn would drown the signal the console exists to provide; TTFT plus response summary answers the latency question.

**LANADEBG-DD-06:** `--debug` stays unchanged. Rationale: payload dumps (full request/response JSON) and flow/timing observability are different concerns; existing tests and workflows depend on `--debug` behavior.

**LANADEBG-DD-07:** Non-Windows fallback: debug lines go to stderr (no window spawn). Rationale: Lana ships win-x64 only (build pipeline); stderr keeps the feature usable in dev containers without platform-specific terminal-emulator detection.

**LANADEBG-DD-08:** Viewer renders via its own console device (CONOUT$), and the spawn detaches the viewer's stdout/stderr from the parent. Rationale: redirecting stdin makes Windows hand the child the PARENT's stdout/stderr handles (STARTF_USESTDHANDLES) - the new window would stay blank and viewer output would pollute the parent's streams, corrupting the ACP protocol (found in smoke test, LANADEBG-PR-0005).

## 7. Implementation Guarantees

**LANADEBG-IG-01:** No write to stdout or read from stdin in any debug-console code path (ACP protocol integrity).

**LANADEBG-IG-02:** A pipe failure never raises into an instrumented call site - the writer catches, disables itself, warns once on stderr.

**LANADEBG-IG-03:** Every duration is computed from monotonic clocks captured at operation boundaries, never from wall-clock subtraction.

**LANADEBG-IG-04:** With the flag absent, no subprocess is spawned and no debug code beyond a None check executes.

**LANADEBG-IG-05:** Debug lines never contain full prompts, tool results, or API keys - identifiers, counts, durations, and truncated error text only (privacy + noise).

## 8. Key Mechanisms

- **Null-object fast path**: module function checks a singleton reference; disabled means immediate return - call sites never branch on configuration
- **Pre-computation contract**: callers capture monotonic timestamps at operation start/end and pass finished values; the writer only serializes and writes
- **Self-disabling writer**: first `OSError`/`BrokenPipeError` flips `dead`, all later calls no-op - one failure mode, handled once
- **EOF-latched viewer**: viewer treats stdin EOF as "Lana exited", not an error - prints notice, waits for keypress, exits

## 9. Action Flow

```
lana --debug-console [--acp | -p ... | REPL]
├─> main() parses args
│   ├─> debug console enabled: spawn viewer subprocess (new console window, stdin=PIPE)
│   │   └─> viewer: reads stdin lines → renders colorized
│   ├─> app: startup line (mode, version)
│   └─> normal mode dispatch (REPL / headless / ACP)
│
Turn execution (any mode)
├─> llm: request line (role, model, msgs, tools)
├─> llm: first_token line (TTFT ms)                 ← first streamed delta
├─> llm: response line (dur, tokens, cache, cost)   ← usage + cost already computed
├─> tool: start line (name, args summary)
├─> tool: end line (name, dur, status, chars)
│
ACP mode additionally
├─> acp: recv line per inbound request/notification
├─> acp: send line per response, handler dur (all methods except session/prompt)
├─> acp: roundtrip line per permission/elicitation
└─> acp: turn line at prompt end (dur, stop reason, update count)
```

## 10. Data Structures

**DebugLine examples (JSONL on the pipe, one per line):**
```
<llm>
{"ts":"13:04:22.123","dom":"llm","op":"request","role":"generator","provider":"anthropic","model":"claude-sonnet-4-5","msgs":12,"tools":17}
{"ts":"13:04:23.001","dom":"llm","op":"first_token","dur_ms":878}
{"ts":"13:04:31.410","dom":"llm","op":"response","dur_ms":9287,"in_tok":24130,"cache_read":23800,"cache_write":0,"out_tok":512,"cost_usd":0.0214,"tool_calls":2}
{"ts":"13:04:24.100","dom":"llm","op":"retry","err":"Anthropic APITimeoutError - retrying in 2s (attempt 1/2)..."}
{"ts":"13:04:31.500","dom":"llm","op":"error","dur_ms":9377,"err":"Provider error: ..."}
{"ts":"13:05:02.100","dom":"llm","op":"sidecall","role":"websearch","provider":"openai","model":"gpt-4.1-mini","dur_ms":2140,"results":5}
</llm>
<tool>
{"ts":"13:04:31.412","dom":"tool","op":"start","tool":"read_file","args":"e:\\Dev\\Lana-V1\\README.md"}
{"ts":"13:04:31.430","dom":"tool","op":"end","tool":"read_file","dur_ms":18,"status":"ok","chars":4213}
{"ts":"13:04:31.480","dom":"tool","op":"end","tool":"read_file","dur_ms":2,"status":"error","chars":54,"err":"File not found: 'e:\\Dev\\Lana-V1\\missing.md'"}
{"ts":"13:04:35.100","dom":"tool","op":"approval","action":"run_command","dur_ms":8213,"approved":true}
</tool>
<acp>
{"ts":"13:04:20.000","dom":"acp","op":"recv","method":"session/prompt","id":3}
{"ts":"13:04:19.900","dom":"acp","op":"send","method":"initialize","id":1,"dur_ms":2,"status":"ok"}
{"ts":"13:04:28.214","dom":"acp","op":"roundtrip","method":"session/request_permission","dur_ms":8213,"outcome":"ok"}
{"ts":"13:04:31.500","dom":"acp","op":"turn","id":3,"dur_ms":11500,"stop":"end_turn","updates":47}
</acp>
<app>
{"ts":"2026-08-31 13:04:19.500","dom":"app","op":"startup","mode":"acp","version":"1.2.0"}
{"ts":"2026-08-31 13:04:20.900","dom":"app","op":"roles","roles":"generator: claude-sonnet-4-5 (medium) | summarizer: gpt-4.1-mini (low) | websearch: gpt-4.1-mini (low)"}
{"ts":"2026-08-31 13:04:20.950","dom":"app","op":"prompt_system","dur_ms":32,"rules":8,"workflows":48,"skills":24}
{"ts":"2026-08-31 13:04:21.000","dom":"app","op":"session","file":"2026-08-31_130421_a1b2c3.jsonl","resumed":true,"dur_ms":40}
{"ts":"2026-08-31 13:08:59.000","dom":"app","op":"compaction_start","projected":152000,"threshold":120000}
{"ts":"2026-08-31 13:09:00.000","dom":"app","op":"compaction","truncated":40,"kept":6,"checkpoint_chars":5120}
{"ts":"2026-08-31 13:09:00.100","dom":"app","op":"compaction_failed","err":"KeyError: ..."}
</app>
```

## 11. User Actions

- **Start with debug console**: `lana --debug-console` (any mode) - second window opens before the first prompt
- **Start with log file**: `lana --debug-console --log-dir ./logs` - viewer window AND timestamped JSONL file
- **Log file only** (no viewer): `lana --log-dir ./logs` - debug lines go to file and stderr (non-Windows) or file and viewer (Windows)
- **Close viewer window**: Lana continues unaffected; debug logging silently stops for the rest of the process (file logging continues if active)
- **Exit Lana**: viewer shows connection-closed notice and waits for a keypress

## 12. UX Design

Viewer window (colorized: timestamp dim, domain tag colored, errors red):

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Lana Debug Console - connected                                               │
│                                                                              │
│ 13:04:19.500 app  startup      acp v1.2.0                                    │
│ 13:04:20.000 acp  recv         session/prompt id=3                           │
│ 13:04:22.123 llm  request      generator anthropic claude-sonnet-4-5         │
│                                msgs=12 tools=17                              │
│ 13:04:23.001 llm  first_token  878ms                                         │
│ 13:04:31.410 llm  response     9287ms in=24130 (cache 23800) out=512         │
│                                $0.0214 tool_calls=2                          │
│ 13:04:31.412 tool start        read_file e:\Dev\Lana-V1\README.md            │
│ 13:04:31.430 tool end          read_file 18ms ok 4213 chars                  │
│ 13:04:35.100 tool approval     run_command 8213ms approved                   │
│ 13:04:40.000 llm  error        Provider error: Anthropic API error: ...      │
│ 13:04:41.000 acp  turn         id=3 21000ms end_turn updates=47               │
│                                                                              │
│ -- connection closed (Lana exited) - press any key to close --               │
└──────────────────────────────────────────────────────────────────────────────┘
```

Domain colors: `llm` cyan, `tool` green, `acp` magenta, `app` white.

## 13. Logging Requirements

**Applicable logging types:**
- [x] App-Level (AP) - the debug stream itself (`LOGGING-RULES-APP-LEVEL.md`)
- [x] User-Facing (UF) - startup/degradation notices on the main console

**App-Level (the debug stream):**
- **Audience**: Developer diagnosing latency, cost, cache behavior, errors across ACP/LLM/tool layers
- **Goal**: Single source of truth - what happened, when, how long, what it cost, what failed
- **Key operations**: every LLM request/response, every tool call, every ACP message, approvals, retries, compaction

**User-Facing (main console):**
- **Audience**: User starting Lana with the flag
- **Goal**: Know the viewer opened (or why not) without reading the second window

**Expected main-console output:**
```
Debug console opened (PID 12345).
```
Degradation (once, stderr):
```
WARNING: debug console pipe broken - debug logging disabled for this session.
```

## 14. Technical Constraints

- ACP stdio protocol: stdout carries only JSON-RPC; stderr already carries `acp.log()` lines - viewer pipe is the only new channel
- Windows viewer spawn uses a new-console process creation flag; non-Windows falls back to stderr lines (LANADEBG-DD-07)
- PyApp binary: the running interpreter is PyApp's managed Python, so module re-invocation of Lana works for the viewer (LANADEBG-DD-03)
- Viewer rendering reuses the existing rich dependency (already used by the main-console Renderer)
- Cost values come from the existing cost engine at turn end - no duplicate pricing logic
- Adapter retry notices already exist as stream deltas; instrumentation reuses those boundaries

## 15. Edge Cases

**LANADEBG-EC-01:** Viewer window closed mid-session → first write fails → logging disabled, one stderr warning, Lana unaffected
**LANADEBG-EC-02:** Viewer spawn fails at startup (no console available, spawn error) → stderr warning, Lana starts normally without debug console
**LANADEBG-EC-03:** `--debug-console` without a TTY on POSIX → stderr fallback lines (DD-07)
**LANADEBG-EC-04:** Lana crashes or is killed → viewer gets EOF → connection-closed notice, waits for keypress
**LANADEBG-EC-05:** ACP client restarts Lana quickly → each process owns its own viewer window; no window reuse
**LANADEBG-EC-06:** Non-JSON line reaches the viewer (defensive) → rendered raw, dim, never crashes the viewer
**LANADEBG-EC-07:** `--debug-viewer` invoked directly by a user → behaves as viewer (reads stdin), harmless
**LANADEBG-EC-08:** Inherited std handles point at the parent (stdin=PIPE side effect) → viewer ignores them: renders to its own console (CONOUT$), spawn detaches stdout/stderr (DD-08)
**LANADEBG-EC-09:** `--log-dir` with unwritable path → stderr warning at startup, Lana starts without file logging, viewer unaffected
**LANADEBG-EC-10:** Log file write fails mid-session (disk full, permissions) → file logging disabled with one stderr warning, viewer pipe unaffected
**LANADEBG-EC-11:** Viewer pipe breaks but log file still open → viewer logging stops, file logging continues independently

## 16. Document History

**[2026-09-01 19:10]**
- Added: FR-07 (--log-dir file output), EC-09/EC-10/EC-11 (file failure modes)
- Changed: DebugLog lifecycle includes --log-dir activation path
- Changed: User Actions expanded with log file and log-only modes
- Synced from code: `debuglog.py` enable(log_dir=), DebugLogWriter dual-output, `cli.py` --log-dir arg

**[2026-08-31 14:10]**
- Changed: ts field carries the full date (LOG-AP-01, session-JSONL correlation); viewer displays time only
- Added: compaction announce (`compaction_start` with projected/threshold), checkpoint char size on the report, `compaction_failed` line (FR-05)
- Added: `prompt_system` load line and resume duration on the `session` line (FR-05)
- Changed: viewer durations follow LOG-GN-04 (`245 ms`, `1.5 secs`, `2 mins 30 secs`); paths and file names quoted (LOG-GN-02)

**[2026-08-31 13:50]**
- Added: summarizer instrumentation and websearch `sidecall` line (FR-02, drift item 03)
- Added: error text on failed tool `end` lines (FR-03, drift item 04)
- Changed: roles banner moved to dedicated `roles` line at runtime build (FR-05, drift item 07)
- Changed: DD-03 PyApp claim labeled [ASSUMED] pending binary verification (drift item 16)

**[2026-08-31 13:30]**
- Added: DD-08 and EC-08 - viewer renders via CONOUT$, spawn detaches child stdout/stderr (blank-window bug found in smoke test)

**[2026-08-31 13:25]**
- Changed: request line drops attempt field - retries are separate lines from adapter notices (FR-02)
- Changed: turn_updates op consolidated into acp `turn` line (id, dur_ms, stop, updates) (FR-04)
- Changed: roundtrip outcome values generic (ok, cancelled, client error) - decision detail stays in stderr acp.log

**[2026-08-31 13:15]**
- Initial specification created (P1-S7, from session findings and LANADEBG-DD-01)
