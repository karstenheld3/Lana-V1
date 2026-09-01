# TEST: Lana Debug Console - Verification Plan

**Doc ID**: LANADEBG-TP01
**Goal**: Verify the debug console meets all LANADEBG-SP01 requirements -- writer behavior via pytest, viewer via pytest, integration via manual harness
**Timeline**: Created 2026-09-01

**Target file(s)**:
- `tests/test_debuglog.py` (writer + viewer unit tests)
- Manual verification via `lana --debug-console` in CLI, headless, and ACP modes

**Depends on:**
- `_SPEC_LANA_08-DebugConsole.md [LANADEBG-SP01]` for requirements
- `_IMPL_LANA_08-DebugConsole.md [LANADEBG-IP01]` for implementation structure, edge cases, and TC definitions

## MUST-NOT-FORGET

- IG-01: no stdout/stdin touches in any debug code path - ACP protocol integrity
- Offline tests never spawn a real viewer window - mock the pipe
- Integration tests require a Windows console environment
- Never log full prompts, tool results, or API keys (IG-05)

## Table of Contents

1. [Test Strategy](#1-test-strategy)
2. [Test Fixtures](#2-test-fixtures)
3. [Test Cases](#3-test-cases)
4. [Test Phases](#4-test-phases)
5. [Verification Checklist](#5-verification-checklist)
6. [Document History](#6-document-history)

## 1. Test Strategy

Three layers matching the IMPL categories:

- **Layer 1 (pytest)**: Writer behavior - singleton lifecycle, pipe write/fail/disable, log file output. Mock subprocess pipe. 5 tests.
- **Layer 2 (pytest)**: Viewer behavior - JSONL parsing, colorized rendering, EOF handling. Capture output. 3 tests.
- **Layer 3 (manual)**: Integration - real viewer window in CLI/ACP/headless modes, degradation on viewer close. 3 tests.

## 2. Test Fixtures

**Setup:**
```python
# Writer tests: monkeypatch subprocess.Popen to return a mock pipe; tmpdir for --log-dir
# Viewer tests: feed JSONL lines via StringIO stdin mock; capture CONOUT$ output
# All: reset module-level _writer singleton between tests
```

**Teardown:**
- pytest `tmp_path` auto-cleanup; singleton reset in fixture finalizer

## 3. Test Cases

### Category 1: Writer behavior (5 tests, pytest)

- **LANADEBG-TP01-TC-01**: `dlog()` when disabled (no `enable()` call) -> no subprocess, no pipe, immediate return, no side effects (IG-04, NFR-01)
- **LANADEBG-TP01-TC-02**: `enable()` + `dlog("app", "startup", mode="repl", version="1.0")` -> JSONL line on mock pipe contains `ts`, `dom`="app", `op`="startup", `mode`="repl" (FR-05)
- **LANADEBG-TP01-TC-03**: Pipe write raises `BrokenPipeError` -> `dead` flag set, subsequent `dlog()` calls are no-ops, exactly one stderr warning line (IG-02, EC-01)
- **LANADEBG-TP01-TC-04**: `enable(log_dir=tmpdir)` + `dlog()` -> timestamped `.jsonl` file created in tmpdir, valid JSONL lines written (FR-07)
- **LANADEBG-TP01-TC-05**: Pipe dead but log file open -> file logging continues independently, pipe logging stopped (EC-10/11)

### Category 2: Viewer behavior (3 tests, pytest)

- **LANADEBG-TP01-TC-06**: Valid JSONL line `{"ts":"13:04:22.123","dom":"llm","op":"request",...}` -> colorized output with dim timestamp, cyan domain tag, aligned op (FR-06)
- **LANADEBG-TP01-TC-07**: Non-JSON line "corrupted data" -> rendered raw, dim, no crash or exception (EC-06)
- **LANADEBG-TP01-TC-08**: EOF on stdin -> "connection closed" notice printed (NFR-02)

### Category 3: Integration (3 manual tests)

- **LANADEBG-TP01-TC-09**: `lana --debug-console -p "hello"` headless run -> viewer window opens before first LLM call, LLM request/first_token/response lines visible, viewer stays open after Lana exits with keypress prompt (FR-01, FR-02, FR-06)
- **LANADEBG-TP01-TC-10**: `lana --debug-console --acp` with initialize request -> ACP recv/send lines visible in viewer, zero stdout contamination verified by pipe capture (FR-04, IG-01)
- **LANADEBG-TP01-TC-11**: Close viewer window mid-headless-session -> Lana continues and completes, one stderr warning, no further debug lines appear in log file (EC-01, NFR-02)

## 4. Test Phases

1. **Phase 1: Offline unit** - TC-01..05 (writer) + TC-06..08 (viewer) -- mock pipe, no window spawn
2. **Phase 2: Integration** - TC-09..11 -- real viewer window, requires Windows console + scripted adapter for determinism

## 5. Verification Checklist

### Offline (pytest)
- [x] **LANADEBG-TP01-VC-01**: TC-01..08 implemented in `tests/test_debuglog.py`
- [x] **LANADEBG-TP01-VC-02**: `pytest tests/test_debuglog.py -q` green

### Integration (manual)
- [x] **LANADEBG-TP01-VC-03**: TC-09 headless debug console verified
- [x] **LANADEBG-TP01-VC-04**: TC-10 ACP debug console verified, stdout pure
- [x] **LANADEBG-TP01-VC-05**: TC-11 viewer close degradation verified

### Coverage cross-check
- [x] **LANADEBG-TP01-VC-06**: Every SP01 FR has at least one TC (FR-01..07 -> TC map above)
- [x] **LANADEBG-TP01-VC-07**: NFR-01 performance parity verified (SP01 section 5 test result)

## 6. Document History

**[2026-09-01 21:55]**
- Initial test plan created (spec restructure step 9)
