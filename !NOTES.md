# Workspace Notes

**Doc ID**: GLOB-NOTES

## Project

- **Name**: Delphios Lana-V1
- **Goal**: Python-only CLI agent named "Lana-V1" adapting the Windsurf Cascade architecture (multi-LLM pipeline, extensibility, internal tools) with ACP support and OpenAI/Anthropic backends only
- **Scenario**: SINGLE-PROJECT, SINGLE-VERSION, SESSION-MODE

## Key Inputs

- Cascade architecture reference: `docs/Windsurf/HowCascadeWorks/HowWindsurfCascadeWorks.md`
- ACP protocol research: `docs/AI-Standards/ACP-AgentClientProtocol_2026-06-12/`
- Existing configuration: `config/` (model-registry.json, model-parameter-mapping.json, model-pricing.json, .api-keys.txt)
- Source code target: `src/`

## Design Constraints (from user, 2026-08-29)

1. Copy from Cascade: multi-LLM design (Brain, Memory, Generator, Compacting), extensibility (rules, workflows, skills, MCP), internal tools
2. Python-only CLI implementation
3. ACP support (Agent Client Protocol)
4. No LLM backend except OpenAI and Anthropic (depending on model)
5. Use existing `config/` folder files
