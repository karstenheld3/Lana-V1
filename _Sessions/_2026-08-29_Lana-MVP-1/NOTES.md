# Session Notes

**Doc ID**: LANAAGNT-MVP1-NOTES

## Session Info

- **Started**: 2026-08-29
- **Goal**: Design, implement, and test Lana MVP-1 - a Python CLI agent running prompt systems (rules/workflows/skills) on OpenAI/Anthropic backends
- **Operation Mode**: IMPL-CODEBASE
- **Output Location**: `src/lana/`, `tests/`
- **Origin**: Split from `_2026-08-29_LanaV1DesignQuestions/` on 2026-08-30

## Key Documents

- `specs/_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` - 12 FRs, 4 NFRs, 18 DDs
- `specs/_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` - 10 phases (A-J), 20 implementation steps, 25 edge cases
- `specs/_TEST_LANA_MVP-1.md [LANAAGNT-TP01]` - 4-layer strategy, 10 black-box scenarios
- `TASKS_LANA_MVP-1.md [LANAAGNT-TK01]` - 36 tasks, all completed
- `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` - 16 verbatim tool definitions

## Key Decisions

- DD-04: Responses API (not Chat Completions) for OpenAI gpt-5.4+
- DD-05: Sequential tool dispatch (not parallel) for safety gating
- DD-16: model-registry.json as read-only input (no hardcoded per-model logic)
- DD-17: Closed dependency list (no pip installs at runtime)
- DD-20: Scripted adapter for deterministic offline testing

## Bug List

- `LANAAGNT-BG-0001` ApprovalEventNotYielded (resolved 2026-08-30)
- `LANAAGNT-BG-0002` ResumeCostNotSeeded (resolved 2026-08-30)
- `LANAAGNT-BG-0003` AnthropicWebSearchBadParam (resolved 2026-08-30)
- `LANAAGNT-BG-0004` RendererMarkupInjection (resolved 2026-08-30)
- `LANAAGNT-BG-0005` ResumeMissingFileTraceback (resolved 2026-08-30)

## Implementation Result

- 22 source modules (~2600 lines), 24 test modules, 179 offline tests + 5 live smokes, all green
- `/go` execution completed all 36 TK01 tasks
- `/drift-detect` + `/drift-correct` closed 10 gaps, found BG-0003
- Live acceptance passed with real keys (OpenAI + Anthropic)
