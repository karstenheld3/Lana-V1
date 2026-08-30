# Session Progress

**Doc ID**: LANATEST-PROGRESS

## To Do

- [ ] Optional: full 20-model sweep (`selftest.py 04`) -- [ACTOR] scoped live runs to common models only
- [ ] TP01-TC-16: `/selftest` menu flow inside Lana (agent-driven) -- script layer proven, workflow file shipped

## In Progress

- (none -- goal reached)

## Done

- [x] 2026-08-30: Investigated existing coverage -- TC-40..42 in `test_adapters.py` cover default smoke (1 model per provider)
- [x] 2026-08-30: Session created, problems and plan documented
- [x] 2026-08-30: Design decision -- Option E chosen: `/selftest` as workflow+skill, zero src/ changes
- [x] 2026-08-30: SPEC written (`_SPEC_SELFTEST.md [LANATEST-SP01]`), verified, generalized to category framework
- [x] 2026-08-30: LANATEST-PR-0003 resolved -- registry v1.7.1 prefix fixes (dot -> dash) + new haiku-4-5/sonnet-4-6 entries, all 20 models resolve, 0 test regressions
- [x] 2026-08-30: IMPL plan written (`_IMPL_SELFTEST.md [LANATEST-IP01]`), PR-0004 resolved via DC-01 interpreter discovery
- [x] 2026-08-30: TEST plan written (`_TEST_SELFTEST.md [LANATEST-TP01]`) -- 16 offline + 3 live cases, 4 phases, FR coverage verified
- [x] 2026-08-30: IS-01..10 implemented -- `.lana/workflows/selftest.md`, `.lana/skills/selftest/SKILL.md`, `selftest.py`, `tests/test_selftest_script.py`
- [x] 2026-08-30: Offline tests 16/16 green; full suite 277 passed (only pre-existing PR-0005 failures remain)
- [x] 2026-08-30: Live verification (~$0.02 total) -- offline cats 13/13; sweep on 7 common models all pass; effort matrix 5 methods (17+4 pass); tool calls 4/4 pass
- [x] 2026-08-30: [DECISION] Live scope limited to common models per user instruction -- full sweep available via `selftest.py 04` - rules: /go decision logging
- [x] 2026-08-30: Live run found 2 real defects, both fixed: sonnet-4-6 xhigh unsupported (registry v1.7.2), tool-call category used conflicting system prompt (TOOL_SYSTEM_PROMPT added)
- [x] 2026-08-30: PR-0001, PR-0002 resolved [PROVEN]; .tmp_verify_registry.py cleaned up
