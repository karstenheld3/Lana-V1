# IMPL: Lana Debug Console

**Doc ID**: LANADEBG-IP01
**Feature**: debug-console
**Goal**: Implement the debug console per LANADEBG-SP01 - pipe-connected viewer, LLM/tool/ACP/app instrumentation, graceful degradation
**Timeline**: Created 2026-08-31, Documented 2026-09-01

**Target file(s)**:
- `src/lana/debuglog.py` (NEW ~180 lines - writer, DebugLine serialization, self-disabling pipe)
- `src/lana/debug_viewer.py` (NEW ~100 lines - JSONL stdin reader, colorized rendering, EOF latch)
- `src/lana/cli.py` (MODIFY - `--debug-console`, `--log-dir`, `--debug-viewer` flags, viewer spawn)
- `src/lana/agent.py` (MODIFY - LLM request/response/TTFT/error instrumentation calls)
- `src/lana/acp/server.py` (MODIFY - ACP recv/send/turn instrumentation)
- `src/lana/acp/jsonrpc.py` (MODIFY - ACP roundtrip instrumentation)
- `src/lana/tools/web_tools.py` (MODIFY - websearch sidecall instrumentation)
- `src/lana/compaction.py` (MODIFY - compaction_start/compaction_failed instrumentation)

**Depends on:**
- `_SPEC_LANA_08-DebugConsole.md [LANADEBG-SP01]` for all FR/DD/IG/NFR/EC requirements
- `_SPEC_LANA_02-AgentCore.md [LANACORE-SP01]` for AgentEvent model and turn loop
- `_SPEC_LANA_07-ACP.md [LANAACPB-SP01]` for ACP stdio constraints

**Does not depend on:**
- `--debug` payload dumps (complementary, stays unchanged per DD-06)

## MUST-NOT-FORGET

- IG-01: zero stdout/stdin touches in any debug-console code path
- IG-02: pipe failure never raises into call sites - catch, disable, warn once
- IG-03: all durations from monotonic clocks, never wall-clock subtraction
- IG-04: no subprocess spawned and no debug code beyond None check when flag absent
- IG-05: no full prompts, tool results, or API keys in debug lines
- DD-08: viewer renders via CONOUT$, spawn detaches child stdout/stderr

## Table of Contents

1. [File Structure](#1-file-structure)
2. [Edge Cases](#2-edge-cases)
3. [Implementation Steps](#3-implementation-steps)
4. [Test Cases](#4-test-cases)
5. [Verification Checklist](#5-verification-checklist)
6. [Document History](#6-document-history)

## 1. File Structure

```
src/lana/
├── debuglog.py         # Module-level singleton writer (DD-02) [NEW]
├── debug_viewer.py     # Viewer subprocess entry point (DD-03) [NEW]
├── cli.py              # --debug-console, --log-dir, --debug-viewer flags [MODIFY]
├── agent.py            # LLM instrumentation calls [MODIFY]
├── tools/
│   └── web_tools.py    # Websearch sidecall instrumentation [MODIFY]
├── compaction.py       # Compaction start/failed instrumentation [MODIFY]
└── acp/
    ├── server.py       # ACP recv/send/turn instrumentation [MODIFY]
    └── jsonrpc.py      # ACP roundtrip instrumentation [MODIFY]
```

## 2. Edge Cases

- **LANADEBG-IP01-EC-01**: Viewer window closed mid-session -> first write fails -> `dead` flag set, logging disabled, one stderr warning (FR-06, IG-02)
- **LANADEBG-IP01-EC-02**: Viewer spawn fails at startup -> stderr warning, Lana starts normally (NFR-02)
- **LANADEBG-IP01-EC-03**: `--debug-console` on non-Windows -> stderr fallback lines (DD-07)
- **LANADEBG-IP01-EC-04**: Lana killed -> viewer gets EOF -> connection-closed notice, keypress wait
- **LANADEBG-IP01-EC-05**: Non-JSON line reaches viewer -> rendered raw, dim, never crashes
- **LANADEBG-IP01-EC-06**: `--debug-viewer` invoked directly -> behaves as viewer (reads stdin), harmless
- **LANADEBG-IP01-EC-07**: Inherited std handles -> viewer renders via CONOUT$, spawn detaches stdout/stderr (DD-08)
- **LANADEBG-IP01-EC-08**: `--log-dir` with unwritable path -> stderr warning, Lana starts without file logging
- **LANADEBG-IP01-EC-09**: Log file write fails mid-session -> file logging disabled, viewer pipe unaffected
- **LANADEBG-IP01-EC-10**: Viewer pipe breaks but log file open -> viewer stops, file continues independently

## 3. Implementation Steps

### LANADEBG-IP01-IS-01: debuglog.py - writer module

**Location**: `src/lana/debuglog.py` (NEW)

**Action**: Create module-level singleton writer with self-disabling pipe

**Code**:
```python
# Module-level: _writer: DebugLogWriter | None = None
# enable(log_dir=None) -> spawn viewer (--debug-console) or file-only (--log-dir alone)
# dlog(dom, op, **fields) -> if _writer and not _writer.dead: serialize DebugLine, write to pipe + file
# DebugLogWriter: viewer subprocess handle, dead flag, optional log file handle
#   write(): try pipe.write + flush; OSError/BrokenPipeError -> dead=True, stderr warning (IG-02)
#   optional file write: independent failure path (EC-09/10)
```

**Note**: DD-02 module-level singleton. None check is the fast path when disabled (IG-04). Pre-computed values only - caller captures monotonic timestamps.

### LANADEBG-IP01-IS-02: debug_viewer.py - viewer subprocess

**Location**: `src/lana/debug_viewer.py` (NEW)

**Action**: Create JSONL stdin reader with colorized rendering

**Code**:
```python
# Read stdin line by line (JSONL); parse each as DebugLine; render colorized
# Domain colors: llm=cyan, tool=green, acp=magenta, app=white; errors=red
# Render to CONOUT$ (DD-08), not stdout/stderr
# On stdin EOF: print "-- connection closed (Lana exited) - press any key to close --", wait for keypress
# Non-JSON line: render raw, dim (EC-05)
```

### LANADEBG-IP01-IS-03: CLI flags and viewer spawn

**Location**: `src/lana/cli.py`

**Action**: Add `--debug-console`, `--log-dir`, `--debug-viewer` flags; spawn viewer subprocess

**Code**:
```python
# --debug-console: spawn viewer as subprocess with CREATE_NEW_CONSOLE, stdin=PIPE, detach stdout/stderr (DD-08)
# --log-dir DIR: enable file logging to timestamped JSONL in DIR
# --debug-viewer: hidden flag, runs debug_viewer.main() and exits
# Both --debug-console and --log-dir can be active simultaneously
```

### LANADEBG-IP01-IS-04: LLM domain instrumentation

**Location**: `src/lana/agent.py`, `src/lana/tools/web_tools.py`

**Action**: Add instrumentation calls at operation boundaries

**Code**:
```python
# agent.py: dlog("llm", "request", role=, provider=, model=, msgs=, tools=)
# agent.py: dlog("llm", "first_token", dur_ms=)  # TTFT from monotonic clock
# agent.py: dlog("llm", "response", dur_ms=, in_tok=, cache_read=, cache_write=, out_tok=, cost_usd=, tool_calls=)
# agent.py: dlog("llm", "error", dur_ms=, err=truncate(300))
# agent.py: dlog("llm", "retry", err=) per notice delta from adapter
# web_tools.py: dlog("llm", "sidecall", role=, provider=, model=, dur_ms=, results=)
```

### LANADEBG-IP01-IS-05: Tool domain instrumentation

**Location**: `src/lana/agent.py`

**Action**: Add tool start/end/approval instrumentation

**Code**:
```python
# dlog("tool", "start", tool=, args=one_line_summary)
# dlog("tool", "end", tool=, dur_ms=, status=, chars=, err=truncate(300))
# dlog("tool", "approval", action=, dur_ms=, approved=)
```

### LANADEBG-IP01-IS-06: ACP domain instrumentation

**Location**: `src/lana/acp/server.py`, `src/lana/acp/jsonrpc.py`

**Action**: Add ACP recv/send/turn/roundtrip instrumentation

**Code**:
```python
# server.py: dlog("acp", "recv", method=, id=) per inbound request/notification
# server.py: dlog("acp", "send", method=, id=, dur_ms=, status=) per outbound response (except session/prompt)
# server.py: dlog("acp", "turn", id=, dur_ms=, stop=, updates=) per prompt turn end
# jsonrpc.py: dlog("acp", "roundtrip", method=, dur_ms=, outcome=) per permission/elicitation round-trip
```

### LANADEBG-IP01-IS-07: App domain instrumentation

**Location**: `src/lana/cli.py`, `src/lana/agent.py`, `src/lana/compaction.py`

**Action**: Add startup/roles/session/compaction instrumentation

**Code**:
```python
# cli.py: dlog("app", "startup", mode=, version=)
# cli.py: dlog("app", "roles", roles=formatted_string) at runtime build
# cli.py: dlog("app", "prompt_system", dur_ms=, rules=, workflows=, skills=)
# cli.py: dlog("app", "session", file=, resumed=, dur_ms=)
# agent.py: dlog("app", "compaction", truncated=, kept=, checkpoint_chars=)
# compaction.py: dlog("app", "compaction_start", projected=, threshold=)
# compaction.py: dlog("app", "compaction_failed", err=)
```

## 4. Test Cases

### Category 1: Writer behavior (5 tests, pytest)

- **LANADEBG-IP01-TC-01**: `dlog()` when disabled -> no subprocess, no pipe, immediate return (IG-04)
- **LANADEBG-IP01-TC-02**: `enable()` + `dlog("app", "startup", ...)` -> JSONL line on mock pipe with ts/dom/op fields
- **LANADEBG-IP01-TC-03**: Pipe write raises `BrokenPipeError` -> `dead` set, subsequent calls no-op, one stderr warning (IG-02)
- **LANADEBG-IP01-TC-04**: `--log-dir` with writable tmpdir -> timestamped `.jsonl` file created, lines written
- **LANADEBG-IP01-TC-05**: Pipe dead but log file open -> file logging continues (EC-10)

### Category 2: Viewer behavior (3 tests, pytest)

- **LANADEBG-IP01-TC-06**: Valid JSONL line -> colorized output (domain tag, aligned op, detail fields)
- **LANADEBG-IP01-TC-07**: Non-JSON line -> rendered raw, dim, no crash (EC-05)
- **LANADEBG-IP01-TC-08**: EOF on stdin -> connection-closed notice printed

### Category 3: Integration (3 tests, manual/harness)

- **LANADEBG-IP01-TC-09**: `lana --debug-console -p "hello"` headless -> viewer window opens, LLM request/first_token/response lines visible, viewer stays open after Lana exits
- **LANADEBG-IP01-TC-10**: `lana --debug-console --acp` -> ACP recv/send lines visible, zero stdout contamination (IG-01)
- **LANADEBG-IP01-TC-11**: Close viewer window mid-session -> Lana continues, one stderr warning, no further debug lines

## 5. Verification Checklist

### Prerequisites
- [x] **LANADEBG-IP01-VC-01**: LANADEBG-SP01 read, all FR/DD/IG cross-checked
- [x] **LANADEBG-IP01-VC-02**: NFR-01 verified: no measurable duration difference with viewer attached

### Implementation
- [x] **LANADEBG-IP01-VC-03**: IS-01 debuglog.py created
- [x] **LANADEBG-IP01-VC-04**: IS-02 debug_viewer.py created
- [x] **LANADEBG-IP01-VC-05**: IS-03 CLI flags wired
- [x] **LANADEBG-IP01-VC-06**: IS-04..07 all instrumentation calls added

### Validation
- [x] **LANADEBG-IP01-VC-07**: TC-01..05 writer tests pass
- [x] **LANADEBG-IP01-VC-08**: TC-06..08 viewer tests pass
- [x] **LANADEBG-IP01-VC-09**: TC-09..11 integration verified
- [x] **LANADEBG-IP01-VC-10**: Full offline suite green (no regression from instrumentation calls)

## 6. Document History

**[2026-09-01 23:30]**
- Fixed: Target files and file structure synced from code - removed adapter files and `bridge.py` (zero dlog calls); added `jsonrpc.py` (roundtrip), `web_tools.py` (sidecall), `compaction.py` (compaction_start/failed)
- Fixed: IS-01 function name `log()` -> `dlog()` (consistent with IS-04..07 and actual code)
- Fixed: IS-04 locations - retry instrumentation is in `agent.py` (notice delta handler), sidecall in `web_tools.py` (not in adapter files)
- Fixed: IS-06 roundtrip location `bridge.py` -> `jsonrpc.py` (Connection.request method)
- Fixed: IS-07 added `compaction.py` for `compaction_start` and `compaction_failed`; `session` dlog moved from `agent.py` to `cli.py`
- Source: `/fact-check` + `/sync` against source code

**[2026-09-01 21:55]**
- Initial implementation plan created (spec restructure step 9, post-hoc documentation of implemented debug console)
