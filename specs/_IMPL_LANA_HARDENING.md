# IMPL: Lana Robustness Hardening (Tier 1 + Tier 2)

**Doc ID**: LANAAGNT-IP02
**Goal**: Implement LANAAGNT-FR-16 (zero-setup + resilience) and the LANAACPB hardening bullets (BL-01/02/04/06) - all findings from LANAAGNT-IN03 scoped for MVP-2 hardening
**Timeline**: Created 2026-08-30
**Target file(s)**:
- `src/lana/cli.py`, `src/lana/config.py`, `src/lana/render.py`, `src/lana/compaction.py`, `src/lana/agent.py`
- `src/lana/tools/shell_tools.py`, `src/lana/tools/web_tools.py`, `src/lana/tools/__init__.py`
- `src/lana/providers/openai_adapter.py`, `src/lana/providers/anthropic_adapter.py`, `src/lana/providers/base.py`
- `src/lana/acp/jsonrpc.py`, `src/lana/acp/server.py`
- `tests/test_hardening.py` (new)

**Depends on:**
- `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` FR-16, DD-23, DD-24
- `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` FR-01/03/10 hardening bullets
- `_INFO_ROBUSTNESS_HAZARDS.md [LANAAGNT-IN03]` finding evidence and mitigations

## MUST-NOT-FORGET

- AgentEvent enum stays at 11 types (DD-24) - notices ride on ErrorEvent with severity prefixes
- ACP stdout purity (LANAACPB-IG-01): zero-setup print lines are already stderr-redirected in ACP mode
- No test deleted or weakened; 227 existing tests stay green
- Auto-create only the DEFAULT config path; explicit `--config` missing stays ConfigError
- Wire bytes of the ACP writer thread identical to direct writes (tests with injected write_line unaffected)

## Implementation Steps

**Phase 1: Zero-setup + startup/REPL resilience (FR-16, IN03 CR-01/02/03, UX-05)**
- [x] LANAAGNT-IP02-IS-01: `config.py` - `DEFAULT_LANA_CONFIG` constant (DD-02 roles, SPEC section 10 values); `load_lana_config` creates it at the default path when missing (`created_files` list on AppConfig for reporting); explicit override missing stays ConfigError
- [x] LANAAGNT-IP02-IS-02: `cli.py build_runtime` - ensure `data_dir/sessions/` and `agent_folder/{rules,workflows,skills}/` exist; print one `Created ...` line per created artifact; print empty-prompt-system notice; print `Resuming '<file>'...` before parsing (UX-05)
- [x] LANAAGNT-IP02-IS-03: `cli.py main` - catch `OSError` alongside `ConfigError` (exit 2, self-contained message); `repl`/`run_headless` - broad `except Exception` around the turn (REPL stays alive; headless exit 4)

**Phase 2: Tool hardening (IN03 BL-03/07, BL-02/06 shared helper)**
- [x] LANAAGNT-IP02-IS-04: `shell_tools.py` - clamp `WaitDurationSeconds` to 60 s, note clamp in result; `foreground_process` slot on ToolContext; `terminate_tool_processes(context)` helper terminating foreground + background Popen handles, returning survivor names
- [x] LANAAGNT-IP02-IS-05: `web_tools.py` - chunked read loop with 120 s wall-clock deadline
- [x] LANAAGNT-IP02-IS-06: `cli.py` - call `terminate_tool_processes` at REPL exit and headless end; print one line naming survivors

**Phase 3: Renderer responsiveness (IN03 UX-01/02/04, DD-24)**
- [x] LANAAGNT-IP02-IS-07: `render.py` - `turn_started` starts a rich status spinner with elapsed ticker; first visible output stops it; hidden `thinking_delta` updates the ticker text; severity-prefix rendering (WARNING yellow, NOTICE dim, else red ERROR)
- [x] LANAAGNT-IP02-IS-08: `cli.py` - `--show-thinking` flag wired to Renderer
- [x] LANAAGNT-IP02-IS-09: `compaction.py` - yield `NOTICE: Compacting context (~N tokens)...` BEFORE the Summarizer call; widen try/except to the whole compact body (CR-04)

**Phase 4: Provider timeouts + visible retries (IN03 BL-05/UX-03)**
- [x] LANAAGNT-IP02-IS-10: `providers/base.py` - `RETRYABLE_STATUS` set, `is_retryable_error(error)` helper, `RETRY_DELAYS = (2, 8)`; AdapterDelta gains `kind="notice"`
- [x] LANAAGNT-IP02-IS-11: both adapters - explicit `httpx.Timeout(connect=10, read=120, write=30, pool=10)`, `max_retries=0`; `stream_turn` retries the initial request up to 2 times on retryable errors before the first delta, yielding a notice delta per retry
- [x] LANAAGNT-IP02-IS-12: `agent.py` - `delta.kind == "notice"` → emit `ErrorEvent(message="WARNING: ...")`

**Phase 5: ACP hardening (LANAACPB FR-01/03/10, IN03 BL-01/02/04/06)**
- [x] LANAAGNT-IP02-IS-13: `acp/jsonrpc.py` - `StdoutWriter` thread with bounded queue (default 1000); overflow drops with stderr log; `close()` drains on shutdown; injected `write_line` unaffected
- [x] LANAAGNT-IP02-IS-14: `acp/server.py` - `build_session_runtime` via `run_in_executor` (stdout redirect inside the callable); cancel paths and EOF shutdown call `terminate_tool_processes` per session

## Edge Cases

- [x] LANAAGNT-IP02-EC-01: default config path missing but `config/` dir also missing → both created, two report lines
- [x] LANAAGNT-IP02-EC-02: `--config` explicit path missing → ConfigError (no auto-create)
- [x] LANAAGNT-IP02-EC-03: data_dir path exists as a FILE → OSError caught, self-contained message, exit 2
- [x] LANAAGNT-IP02-EC-04: REPL turn raises non-ToolError exception → error line printed, next prompt shown, session file intact
- [x] LANAAGNT-IP02-EC-05: `WaitDurationSeconds: 3600` → waits max 60 s, result notes the clamp
- [x] LANAAGNT-IP02-EC-06: compaction `split_sections` raises → WARNING event, no truncation, turn continues (EC-17 semantics)
- [x] LANAAGNT-IP02-EC-07: retry exhausted (3 failures) → provider_error path unchanged, 2 WARNING notices seen
- [x] LANAAGNT-IP02-EC-08: error mid-stream (after first delta) → NO retry, provider_error immediately
- [x] LANAAGNT-IP02-EC-09: writer queue overflow → message dropped + stderr log, loop alive
- [x] LANAAGNT-IP02-EC-10: cancel with live foreground pwsh → process terminated, turn responds cancelled
- [x] LANAAGNT-IP02-EC-11: exit with running background process → terminated, survivor line printed if kill failed

## Test Cases (tests/test_hardening.py unless noted)

- [x] LANAAGNT-IP02-TC-01: zero-setup in empty temp workspace (registry files present): default config + data dirs + agent folder created, `Created` lines printed, startup proceeds
- [x] LANAAGNT-IP02-TC-02: explicit `--config` missing → ConfigError, nothing created
- [x] LANAAGNT-IP02-TC-03: data_dir blocked by file → exit 2, message names path, no traceback
- [x] LANAAGNT-IP02-TC-04: headless turn raising RuntimeError → exit 4, self-contained message
- [x] LANAAGNT-IP02-TC-05: command_status clamp: wait 3600 requested → returns within budget, clamp noted
- [x] LANAAGNT-IP02-TC-06: compaction post-Summarizer failure → WARNING event, messages NOT truncated
- [x] LANAAGNT-IP02-TC-07: compaction pre-notice event ordering: NOTICE before checkpoint_created
- [x] LANAAGNT-IP02-TC-08: renderer severity: WARNING yellow no-ERROR-prefix, NOTICE dim, plain red
- [x] LANAAGNT-IP02-TC-09: renderer status lifecycle: turn_started starts, text_delta stops (no crash on repeated events)
- [x] LANAAGNT-IP02-TC-10: `is_retryable_error` classification (connection error, 429, 500 retryable; 400, 401 not)
- [x] LANAAGNT-IP02-TC-11: adapter retry loop: fake stream factory failing twice retryable then succeeding → 2 notice deltas + text; failing with 400 → immediate raise
- [x] LANAAGNT-IP02-TC-12: agent notice delta → ErrorEvent with WARNING prefix in stream and JSONL
- [x] LANAAGNT-IP02-TC-13: StdoutWriter: lines arrive in order at sink; overflow drops with count; close drains
- [x] LANAAGNT-IP02-TC-14: web fetch deadline: monotonic-patched trickle aborts with ToolError naming the deadline
- [x] LANAAGNT-IP02-TC-15: terminate_tool_processes kills foreground + background, returns empty survivors on success
- [x] LANAAGNT-IP02-TC-16: ACP regression: existing 48 tests green with writer-thread Connection and executor runtime build

## Verification Checklist

- [x] LANAAGNT-IP02-VC-01: full offline suite green (227 existing + new)
- [x] LANAAGNT-IP02-VC-02: `lana` in an empty workspace (with model data files) reaches the prompt with only `Created ...` lines - no manual step
- [x] LANAAGNT-IP02-VC-03: no raw traceback reachable via startup or REPL fault injection
- [x] LANAAGNT-IP02-VC-04: ACP wire bytes unchanged (fixture tests untouched and green)

## Document History

**[2026-08-30 17:40]**
- Changed: all ISs/ECs/TCs/VCs implemented and green - 240 passed (223 existing + 17 new in `tests/test_hardening.py`); TC-06/07 partially live in `tests/test_compaction.py` (TC-38 extended)

**[2026-08-30 17:00]**
- Initial implementation plan: 14 ISs across 5 phases, 11 ECs, 16 TCs, 4 VCs - covers LANAAGNT-FR-16 and LANAACPB hardening bullets
