[DEFAULT_SESSIONS_FOLDER]: [WORKSPACE_FOLDER]\_Sessions
[SESSION_ARCHIVE_FOLDER]: [DEFAULT_SESSIONS_FOLDER]\Archive
[AGENT_FOLDER]: [WORKSPACE_FOLDER]\.devin

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

## Design Constraints (from user, 2026-08-30)

6. `.lana/` is the [AGENT_FOLDER] - identical structure to `.devin/` (or `.windsurf/`). Contains ONLY: `rules/`, `workflows/`, `skills/`. No session data, no logs, no runtime artifacts.
7. Runtime data (sessions, debug logs, URL chunks) lives in `.lana-data/` - separate from the agent configuration folder.
8. `agent_folder` (string) replaces `prompt_system_paths`. One agent = one prompt system folder. Relative path resolved against workspace, absolute used as-is.
9. **Zero-setup philosophy**: Lana auto-creates everything it needs on first run (data dirs, default config, prompt library) and tells the user what it did. No `init` command, no manual setup steps. The user runs `lana` and works. Prompt library distribution is a separate concern (deferred).
