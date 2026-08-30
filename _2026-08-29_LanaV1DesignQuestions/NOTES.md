# Session Notes

**Doc ID**: LANAAGNT-NOTES

## Initial Request

````text
In this project I want to implement an agent called "Lana-V1".

I want to adapt the architecture of the Cascade agent documented here:
docs/Windsurf/HowCascadeWorks/HowWindsurfCascadeWorks.md

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

## Authoritative ACP Documentation (MVP-2)

**`docs/AI-Standards/ACP-AgentClientProtocol_2026-08-30/` is the authoritative ACP documentation** (refresh in progress 2026-08-30, replaces `ACP-AgentClientProtocol_2026-06-12/`). All MVP-2 ACP SPEC/IMPL/TEST work MUST cite the 2026-08-30 folder. Key deltas vs 2026-06-12: ACP v2 Draft published (2026-07-20), Elicitation stabilized (`elicitation/create`, 2026-07-24), Request Cancellation stabilized (`$/cancel_request`, 2026-06-29), Boolean Config Options + Terminal Authentication stabilized, Session Compaction + Session Notices RFDs in Draft, Python SDK v0.12.0+ has HTTP/WebSocket transports.

## Agent Instructions

- All design questions grounded in `HowWindsurfCascadeWorks.md` (Cascade reference) and ACP research docs
- Only OpenAI and Anthropic backends are allowed - no Google, no other providers
- Existing `config/` files are input constraints, not to be redesigned without reason

## Key Decisions

- (none yet - design questions must be answered by user first)

## Important Findings

- See `_INFO_OPEN_DESIGN_QUESTIONS.md [LANAAGNT-IN01]` Summary section

## Topic Registry

**Global topics** (registered in ID-REGISTRY.md):
- `LANAAGNT` - Lana-V1 Agent

**Subtopics** (session-local):
- (none yet)

## Bug List

- `LANAAGNT-BG-0001` ApprovalEventNotYielded (resolved 2026-08-30)
- `LANAAGNT-BG-0002` ResumeCostNotSeeded (resolved 2026-08-30)
- `LANAAGNT-BG-0003` AnthropicWebSearchBadParam (resolved 2026-08-30)
- `LANAAGNT-BG-0004` RendererMarkupInjection (resolved 2026-08-30)
- `LANAAGNT-BG-0005` ResumeMissingFileTraceback (resolved 2026-08-30)

## Significant Prompts Log

- (none yet beyond Initial Request)
