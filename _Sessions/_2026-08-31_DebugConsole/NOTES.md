# Session Notes

**Doc ID**: LANADEBG-NOTES

## Initial Request

````text
we need to add a second console for debugging and logging.

The logging should be super-fast. We need a command line flag that opens a second console. Also in ACP mode.
````

## Session Info

- **Started**: 2026-08-31
- **Goal**: Add a second console window for real-time debug/logging output, activated by a CLI flag, working in both interactive and ACP modes
- **Operation Mode**: IMPL-CODEBASE
- **Output Location**: src/lana/

## Agent Instructions

- Never run `_build.bat` or `_build.ps1` - tell user to rebuild after code changes
- `.lana/` is the authoritative agent folder; `.devin/` is synced from IPPS repo
- Zero-setup philosophy: auto-create what is needed, report what was created
- ACP mode uses stdio for JSON-RPC 2.0 - second console must not interfere with stdio transport

## Requirements

The debug console is the **single source of truth** to analyze and fix issues across three domains:

1. **ACP communication** - Server/client message flow, where time is lost, where errors occur
2. **LLM backend communication** - OpenAI/Anthropic request/response latency, cost per call, cache expiry, unexpected responses
3. **Tool call execution** - Success/failure, latency per tool, errors and unexpected behaviors

**Design principles:**
- Pre-calculate values that would cause logging delays (e.g. compute durations, token counts, cost before writing the log line)
- Immediate flush over performance-optimized occasional flush - every log line written and visible instantly
- Must answer: what happened, when, how long did it take, what went wrong, what was the cost

## Key Decisions

- **LANADEBG-DD-01**: Option B chosen - pipe-connected spawned console (direct transport). Main process writes debug lines to `subprocess.stdin` pipe; subprocess renders in its own console window. Rationale: no filesystem dependency, direct transport, clean separation. Post-mortem persistence via optional `--debug` tee to file (existing mechanism).

## Important Findings

### Current Architecture

- **Event flow**: `agent.run_prompt()` yields `AgentEvent` objects consumed by 3 observers: `SessionStore` (JSONL file), `Renderer` (CLI console), `EventTranslator` (ACP updates)
- **SessionStore**: Append-only JSONL with `write+flush` per line - proven immediate-flush pattern
- **StdoutWriter** (`jsonrpc.py`): Bounded queue + dedicated writer thread for non-blocking stdout in ACP mode - proven async-write pattern
- **ACP mode**: stdout = JSON-RPC protocol. `acp.log()` writes timestamped lines to stderr. `build_runtime()` prints are redirected to stderr via `contextlib.redirect_stdout`
- **Current `--debug`**: `dump_debug()` in each adapter writes raw request/response JSON to `.lana-data/logs/`. No timing, no console output, no tool/ACP coverage

### ACP Registry (Highlander Principle)

There can only be one. On Windows, both Devin Desktop and Devin Next read from the **same** registry file:

```
%APPDATA%\Code\User\acp\registry.json
```

`%APPDATA%\Devin - Next\User\acp\registry.json` exists but is NOT read by Devin Next. Do not touch it. `cmd` must point directly to the `.exe` -- `.bat` wrappers silently fail (Node.js `child_process.spawn` cannot execute `.bat` files). For the debug console in ACP mode, pass `--debug-console` in the `args` array: `["--debug-console", "--acp"]`.

### Timing Gaps (no instrumentation exists)

- **LLM calls**: No duration measured for `stream_turn()` or time-to-first-token
- **Tool calls**: No duration measured for `dispatch_call()` in agent.py
- **ACP round-trips**: No duration for permission/elicitation broker round-trips
- **Cache hits**: Token counts exist in `Usage` but not surfaced as debug output
- **Cost**: Computed in `CostTracker.turn_cost()` but only displayed in the main console `TurnFinished` line

### Instrumentation Points (where to add debug logging)

- `agent.py:154` - before/after `adapter.stream_turn()` - LLM latency, TTFT
- `agent.py:128-129` - before/after `registry.dispatch()` - tool execution latency
- `agent.py:171-174` - after turn completes - token counts, cost, cache stats
- `openai_adapter.py:91` - request sent / `openai_adapter.py:101` - response complete
- `anthropic_adapter.py:121` - request sent / `anthropic_adapter.py:129` - response complete
- `acp/server.py:handle_request` - ACP method dispatch timing
- `acp/jsonrpc.py:142-143` - outbound message send timing
- `acp/bridge.py` - permission/elicitation round-trip timing

## Proposed Options

### Option A: JSONL debug log + spawned tail viewer (file transport)

New `DebugLog` class writes structured JSONL to `.lana-data/debug/<session>.debug.jsonl`. Each line: `{ts, domain, op, duration_ms, detail}` with all values pre-computed before write. Synchronous `write()+flush()` per line (same pattern as `SessionStore`). `--debug-console` spawns a viewer process in a new console window that tails and colorizes the file. Explicit `debug.log_xxx()` calls at each instrumentation point.

- **Transport**: File (append + flush)
- **Main-thread cost**: ~1 microsecond per line (SSD write + flush)
- **Persistence**: Yes - debug log survives for post-mortem analysis
- **Viewer**: Independent process, can be restarted, can filter by domain
- **ACP safe**: Yes - no stdout/stdin involvement
- **Complexity**: Low - follows proven `SessionStore` pattern
- **Downside**: Manual `debug.log_xxx()` at each call site; file I/O per line (negligible but non-zero)

### Option B: Pipe-connected spawned console (direct transport)

`--debug-console` spawns a Python subprocess with a new console window (`CREATE_NEW_CONSOLE` on Windows). Main process writes debug lines directly to `subprocess.stdin` pipe. Same explicit instrumentation points as Option A. No intermediate file.

- **Transport**: OS pipe to subprocess stdin
- **Main-thread cost**: ~0.5 microseconds per line (pipe write + flush)
- **Persistence**: None unless tee-d to file (adds complexity)
- **Viewer**: Built into the subprocess, dies with main process
- **ACP safe**: Yes - pipe is separate from stdio
- **Complexity**: Medium - platform-specific console spawning, pipe error handling, no post-mortem without extra tee
- **Downside**: If viewer subprocess dies, pipe errors need graceful handling; no persistence by default; Windows vs Unix console creation differs

### Option C: Background writer thread + queue + dual sink (async transport)

Follows the `StdoutWriter` pattern from `jsonrpc.py`. Main thread enqueues debug messages via `queue.put_nowait()` (fire-and-forget). Dedicated writer thread drains queue, writes to both: debug JSONL file AND pipe to spawned console. Bounded queue with overflow drop + counter. Provider adapters and tool dispatch wrapped with timing decorators for automatic instrumentation.

- **Transport**: In-process queue -> writer thread -> file + pipe
- **Main-thread cost**: ~0.1 microseconds (just `queue.put_nowait`)
- **Persistence**: Yes - dual output (file + live console)
- **Viewer**: Spawned console fed by pipe from writer thread
- **ACP safe**: Yes - no stdout/stdin involvement
- **Complexity**: High - queue + thread + dual sink + timing decorators
- **Downside**: Most moving parts; queue adds indirection; overflow drops messages silently; decorator wrapping adds coupling

### Comparison

```
                        Option A (File)   Option B (Pipe)   Option C (Queue)
Main-thread latency     ~1 us             ~0.5 us           ~0.1 us
Persistence             Yes               No (extra work)   Yes
Viewer independence     Yes (restart OK)  No (dies w/ main)  Partial
ACP compatible          Yes               Yes               Yes
Post-mortem analysis    Yes               No                Yes
Complexity              Low               Medium            High
Proven pattern in code  SessionStore      (none)            StdoutWriter
```

### Recommendation

Agent recommended Option A; user chose **Option B** (LANADEBG-DD-01). Rationale: direct pipe transport, no filesystem dependency. Post-mortem persistence available via existing `--debug` tee to file when needed.

## Topic Registry

**Global topics** (registered in ID-REGISTRY.md):
- `LANADEBG` - Lana Debug Console (second console for real-time debug/logging)

**Subtopics** (session-local):
(none yet)

## Topic Folders

(none)

## Step Folders

(none)

## Bug List

- **LANADEBG-BG-0001**: Anthropic 400 after cancellation - orphaned `tool_use` without `tool_result`

## Housekeeping

- `_SPEC_LANADEBG.md` moved to `specs/_SPEC_LANADEBG.md` (2026-09-01) - central specs folder per workspace convention

## Significant Prompts Log

[2026-08-31 13:03] User clarified the real goal and requirements for the debug console
````text
First think of what we really need.

The goal is to be able at any time to analyze and fix issues with:
- How ACP server and clients communicate, where precious time is lost, where errors occur
- How Lana communicates with the OpenAI and Anthropic backend. What causes latency, what causes cost, when do caches expire, when do unexpected things happen.
- How tool calls succeed or fail. Also here: what causes latency and how much? What are the errors and unexpected behaviors.

The logging must be the single source of truth to answer all these questions.
If we can, we should pre-calculate values that would cause logging delays. Also we prefer immediate flush over performance-optimized occasional flush
````
