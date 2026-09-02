[DEFAULT_SESSIONS_FOLDER]: [WORKSPACE_FOLDER]\_Sessions
[SESSION_ARCHIVE_FOLDER]: [DEFAULT_SESSIONS_FOLDER]\Archive
[AGENT_FOLDER]: [WORKSPACE_FOLDER]\.devin

# Workspace Notes

**Doc ID**: GLOB-NOTES

## Project

- **Name**: Lana-V1
- **Goal**: Python-only CLI agent named "Lana-V1" adapting the Windsurf Cascade architecture (multi-LLM pipeline, extensibility, internal tools) with ACP support and OpenAI/Anthropic backends only
- **Scenario**: SINGLE-PROJECT, SINGLE-VERSION, SESSION-MODE

## Folder Purposes

- `knowledge\` - documentation of stuff used by agent to implement and maintain product
- `docs\` - product documentation
- `specs\` - internal specifications and plans
- `specs\SOPS\` - workflow-related SOPs (standard operating procedures for improving, testing, releasing Lana)
- `.lana-tools\` - agent infrastructure binaries (rg.exe), bundled in exe, auto-materialized at startup (DD-12)
- `.tools\` - skill binaries (Ghostscript, ImageMagick, etc.), user-installed, NOT bundled (FR-09, DD-12)

## Key Inputs

- Cascade architecture reference: `knowledge/Windsurf/HowCascadeWorks/HowWindsurfCascadeWorks.md`
- ACP protocol research: `knowledge/AI-Standards/ACP-AgentClientProtocol_2026-06-12/`
- Existing configuration: `config/` (model-registry.json, model-parameter-mapping.json, model-pricing.json, .api-keys.txt)
- Source code target: `src/`

## Design Constraints (from user, 2026-08-29)

1. Copy from Cascade: multi-LLM design (Brain, Memory, Generator, Compacting), extensibility (rules, workflows, skills, MCP), internal tools
2. Python-only CLI implementation
3. ACP support (Agent Client Protocol)
4. No LLM backend except OpenAI and Anthropic (depending on model)
5. Use existing `config/` folder files

## Versioning Strategy (from user, 2026-08-30)

10. Lana-V1 starts at version **1.0.0**. Only minor and patch versions are bumped (1.1.x, 1.2.0, ...). No major version bump in this repo.
11. Lana 1.x supports ACP 1.x. Lana 2.x (separate repo) will support ACP 2.x.

## Build

- **NEVER run `_build.bat` or `_build.ps1` from an agent session.** The user builds manually via the batch file.
- After code changes that affect the exe, tell the user to rebuild — do not build yourself

## Python Environment

- **ALWAYS use `.venv`**: `.venv\Scripts\python.exe` for ALL Python operations (pytest, pip install, scripts). NEVER use bare `python` or `python -m pip` - that hits the global install and pollutes it.
- **Tests**: `.venv\Scripts\python.exe -m pytest tests/ -n 4 -x -q --tb=short` (parallel via pytest-xdist, ~20s instead of ~100s)
- **pip install**: `.venv\Scripts\python.exe -m pip install <package>`
- Global Python at `C:\Users\User\AppData\Local\Programs\Python\Python312\` is for other projects - do not touch it from this workspace

## ACP Registry (Devin Desktop)

- **Windows registry path bug**: Devin Desktop reads `%APPDATA%\Code\User\acp\registry.json` on Windows regardless of channel (stable/next). The `.windsurf-next\acp\registry.json` path is IGNORED. Always edit the `%APPDATA%\Code\User\` copy.
- Two files exist: `C:\Users\User\.windsurf-next\acp\registry.json` (unused) and `C:\Users\User\AppData\Roaming\Code\User\acp\registry.json` (actual). Keep both in sync or only edit the real one.
- After editing, run "Reload ACP Connections" from Command Palette or restart Devin Desktop.
- **NEVER wrap the exe in a .bat for ACP registry entries.** The registry `cmd` MUST point directly to the exe. Bat wrappers break the debug console visibility (`CREATE_NEW_CONSOLE` only works from a direct exe spawn, not from a bat-launched child process). Add features via CLI args to the exe instead (e.g., `--log-dir`).

## IPPS Upstream (Integrated Prompt & Process System)

- `e:\Dev\IPPS\DevSystemV4.3` - canonical source (rules, workflows, skills without agent-folder wrapper)
- `e:\Dev\IPPS\.devin` - `.devin/` mirror of DevSystemV4.3
- Sync direction: Lana-V1 changes → IPPS (both locations) when rules/workflows/skills are improved here

## Source Control Approach

- `.lana/` and `.devin/` are mirrors - must stay in sync (same rules, workflows, skills)
- `.lana/` is the authoritative source; `.devin/` is being synced from IPPS repo
- **Lana-specific skills** (e.g., `selftest/`) live in `.devin/skills/` ONLY - do NOT add them to `.lana/`. `.lana/` is the IPPS prompt library bundled with the binary; Lana-specific code belongs in `src/` or `.devin/` only.
- When files in `.lana/` change, immediately mirror to `dist\.lana\` (the runtime copy used by the built binary and `lana-acp.bat`)
- `src/lana/bundled/agent/` and `src/lana/bundled/config/` are gitignored (build-time only, synced by `_build.ps1`)
- `_Sessions/` tracked in git (session notes, specs, plans, bugfix backups are versioned history)
- `_Sessions/.../backup/*.py` files are intentional pre-fix source snapshots (not redundant with git history)
- `config/.api-keys.txt` gitignored (secrets); all other config files tracked
- `evals/runs_gitignore/` gitignored via `*_gitignore/` convention (test run output); `evals/suite/` tracked (test definitions, fixtures, drive scripts)
- API keys: env vars (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) take priority over `.api-keys.txt` (FR-01)
- `knowledge/` tracked (reference docs for agent implementation); large JSON files accepted (e.g. `sdk_methods.json`)

## UX Design System (from user, 2026-08-31)

- **Design system reference**: `specs/UXDesign/_INFO_DELPHIOS_DESIGN_SYSTEM.md [DLPHS-IN10]`
- **Brand reference**: `specs/UXDesign/_INFO_DELPHIOS_BRAND.md [DLPHS-IN07]`
- **CRITICAL**: The design system's internal name MUST NEVER appear in shipped code, binaries, UI output, config files, commit messages, or any artifact that reaches end users. Reference it internally as "the design system" or by Doc ID only.
- **CLI applicability**: The design system targets web apps and presentations. For CLI/terminal output, apply the brand PRINCIPLES (not visual tokens): frugal language, zero overhead, calm and precise, status for any operation >300ms, no interruption patterns, no noise.

## Design Constraints (from user, 2026-08-30)

6. `.lana/` is the [AGENT_FOLDER] - identical structure to `.devin/` (or `.windsurf/`). Contains ONLY: `rules/`, `workflows/`, `skills/`. No session data, no logs, no runtime artifacts.
7. Runtime data (sessions, debug logs, URL chunks) lives in `.lana-data/` - separate from the agent configuration folder.
8. `agent_folder` (string) replaces `prompt_system_paths`. One agent = one prompt system folder. Relative path resolved against workspace, absolute used as-is.
9. **Zero-setup philosophy**: Lana auto-creates everything it needs on first run (data dirs, default config, prompt library) and tells the user what it did. No `init` command, no manual setup steps. The user runs `lana` and works. Prompt library distribution is a separate concern (deferred).
