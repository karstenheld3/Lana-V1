# Deferred Improvements: src/lana (Code)

**Doc ID**: LANAAGNT-DF03
**Goal**: Track code improvement candidates deferred from `/improve` runs on the Lana implementation (successor to LANAAGNT-DF02, which was consumed by user-invoked `/cleanup`; DF02 content is in git history)
**Target file(s)**:
- `src/lana/`, `tests/`
**Timeline**: Created 2026-08-30, Updated 0 times

**Depends on:**
- `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` for implementation context

## Candidates

### D-01: Extract sub-methods from Agent.run_prompt (~70 lines)
- **Issue**: Fowler long-method smell - the core loop mixes streaming, tool dispatch, limit handling, and compaction triggering
- **Fix**: Extract `stream_one_turn()` and `process_tool_call()`; loop body becomes ~20 lines
- **Effort**: Medium
- **Value**: MEDIUM - fails pragmatic Q3 (proportionality) TODAY: the method is fully covered by tests and stable; refactor when MVP-2 ACP work actually touches the loop, with the change requirements in hand

### D-02: Share runtime wiring between cli.build_runtime and tests/conftest.agent_factory
- **Issue**: Registry/context/agent assembly duplicated (rule-of-three not yet reached: 2 sites)
- **Fix**: Extract an `assemble_agent(app, prompt_system, ...)` factory used by both
- **Effort**: Low
- **Value**: LOW - fails pragmatic Q2 (theoretical): the duplication has caused zero divergence bugs; the test wiring intentionally differs (in-process, no prompts)

## Log

- **Run 3** (2026-08-30): APPLIED - jsonl stdout purity (diagnostics to stderr in headless jsonl mode; evidence: harness skip-non-JSON workaround proved contamination; purity regression tests added). Violations fixed: 4 unused test imports. D-01/D-02 deferred with per-question rationale

## Document History

**[2026-08-30 04:55]**
- Initial file (DF03) created from `/improve` run 3
