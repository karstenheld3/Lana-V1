# Session Notes

**Doc ID**: LANAAGNT-NOTES

## Initial Request

````text
In this project I want to implement an agent called "Lana-V1".

I want to adapt the architecture of the Cascade agent documented here:
knowledge/Windsurf/HowCascadeWorks/HowWindsurfCascadeWorks.md

What we copy:
1. Multi-LLM design (Brain, memory, generation, compacting, etc.)
2. Extensibility (rules, workfows, skills, MCP)
3. internal tools

Differences:
1. Python-only CLI implementation
2. ACP support -> E:\Dev\Delphios-Lana-V1\docs\AI-Standards\ACP-AgentClientProtocol_2026-06-12
3. No backend except OpenAI and Anthropic backend (depending on model)
4. Usage of \config folder with existing files

Initialize project, read [Cascade doc] and think hard, which design questions are open

/write-info _INFO_OPEN_DESIGN_QUESTIONS.md
````

## Session Info

- **Started**: 2026-08-29
- **Goal**: Initialize project and collect all open design questions for adapting the Cascade architecture to Lana-V1
- **Operation Mode**: IMPL-ISOLATED (research/design only, no code changes)
- **Output Location**: [SESSION_FOLDER]
- **Status**: COMPLETE - design questions answered, implementation moved to `_2026-08-29_Lana-MVP-1/` and `_2026-08-30_Lana-MVP-2/`

## Agent Instructions

- All design questions grounded in `HowWindsurfCascadeWorks.md` (Cascade reference) and ACP research docs
- Only OpenAI and Anthropic backends are allowed - no Google, no other providers
- Existing `config/` files are input constraints, not to be redesigned without reason

## Important Findings

- See `_INFO_OPEN_DESIGN_QUESTIONS.md [LANAAGNT-IN01]` Summary section

## Related Sessions

- `_2026-08-29_Lana-MVP-1/` - MVP-1 implementation (SPEC, IMPL, TEST, TASKS, bugs, code)
- `_2026-08-30_Lana-MVP-2/` - MVP-2 ACP frontend + robustness hardening
