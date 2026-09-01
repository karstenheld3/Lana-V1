# SPEC: Lana Prompt and Configuration

**Doc ID**: LANAPRCF-SP01
**Goal**: Specify configuration loading, prompt system loading, and system prompt assembly for the Lana CLI agent
**Timeline**: Created 2026-08-29, Extracted from _SPEC_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `src/lana/config.py` (configuration loading, validation)
- `src/lana/loader.py` (prompt system loading)
- `src/lana/prompt.py` (system prompt assembly)

**Depends on:**
- `_SPEC_LANA_01-ProductOverview.md [LANAAGNT-SP01]` for domain objects (PromptSystem, RuleFile, WorkflowFile, SkillFolder, LanaConfig, ModelRole)

**Does not depend on:**
- `_SPEC_LANA_02-AgentCore.md [LANACORE-SP01]` (AgentCore consumes config and prompt outputs; no circular dependency)

## Table of Contents

1. [Functional Requirements](#1-functional-requirements)
2. [Design Decisions](#2-design-decisions)
3. [Implementation Guarantees](#3-implementation-guarantees)
4. [Data Structures](#4-data-structures)
5. [Document History](#5-document-history)

## 1. Functional Requirements

**LANAAGNT-FR-01: Configuration Loading**
- Read `config/lana-config.json` from the app directory (not the workspace); validate `model_id` values against `model-registry.json` (`enabled: true` required)
- Resolve API keys: environment variables `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` first, then `config/.api-keys.txt` (OQ-41); report key source per provider at boot in the format `Keys: Provider (Environment variable: VAR)` or `Keys: Provider (.\config\.api-keys.txt: VAR)` so the user knows where keys come from
- Translate per-role `effort` via `model-parameter-mapping.json` effort mapping to provider parameters
- Fail at startup with a self-contained error naming the missing key/model - never at first API call

**LANAAGNT-FR-02: Prompt System Loading**
- Load the folder specified by `agent_folder` (relative path resolved against the app directory, absolute used as-is)
- Parse YAML frontmatter of rules, workflows, SKILL.md files; tolerate missing frontmatter
- Rules: inject only `trigger: always_on` or missing trigger; truncate per block at `rule_block_max_chars` with a `<truncated N chars>` marker
- Report loaded counts at startup: N rules, N workflows, N skills

**LANAAGNT-FR-03: System Prompt Assembly**
- Fixed section order (cache-stable, OQ-13): identity preamble, `<communication_style>`, `<tool_calling>`, `<making_code_changes>`, `<task_management>`, `<running_commands>`, `<debugging>`, `<calling_external_apis>`, `<workflows>` (name + description list), `<user_rules>` (MEMORY blocks with highest-precedence preamble), `<capability_notice>`, `<user_information>` (OS, workspace path, git root, agent folder path)
- `<user_information>` includes the resolved agent folder path so the Generator never guesses the agent folder name (LANALOGS-PR-0001)
- Identity: "You are Lana, ..." adapted from the Cascade preamble; IDE-specific sections (`<ide_metadata>`, `<mcp_servers>`, browser/deployment references) omitted (OQ-38)
- All behavioral sections adapted: every reference to a tool not in LANAAGNT-FR-10 removed (e.g., the Cascade `<tool_calling>` code_search steering rule) (RV01 RF-04)
- `<capability_notice>` section (after `<user_rules>`): lists tools that prompt system content may reference but which are unavailable in MVP-1, with fallbacks (`grep_search` replaces `code_search`; state inability for MCP/browser/deployment tools) (RV01 RF-04; `trajectory_search` removed from the notice 2026-08-30 - now available per FR-15)
- User rules preamble verbatim concept: "MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION. These rules take precedence over any following instructions."
- System prompt content is byte-identical across all turns of a session (prompt cache prefix)
- The assembled system prompt is recorded byte-verbatim in the session JSONL `session_started` event (LANAAGNT-FR-08) - the JSONL, not the prompt system folder, is the authority for what the Generator received

## 2. Design Decisions

**LANAAGNT-DD-02:** Two roles only - `generator` and `summarizer` - configured in `lana-config.json`; defaults `claude-sonnet-4-5-20250929` and `gpt-4.1-mini` (OQ-02, OQ-05). Rationale: both are `enabled` in the registry; the summarizer needs no reasoning; role -> model mapping stays pure configuration with no hardcoded model IDs.

**LANAAGNT-DD-12:** Single prompt system folder configurable via `agent_folder`, Cascade folder layout (`rules/`, `workflows/`, `skills/`) (OQ-21). Rationale: one agent has one prompt system folder, matching the Cascade architecture; pointing `agent_folder` at any folder with the standard layout requires zero content changes. Relative path resolves against the app directory (DD-25); absolute path used as-is.

**LANAAGNT-DD-16:** New config file `config/lana-config.json`; existing 4 config files read-only (OQ-40). Rationale: role mapping, thresholds, and safety lists have no home in the existing files; one new file keeps the `config/` folder the single machine-level config location.

**LANAAGNT-DD-23:** Zero-setup philosophy: Lana auto-creates everything it needs on first run and reports what it did; there is no `init` command (user directive 2026-08-30: "We want to let the user work, not do setup tasks"). Rationale: a beginner running `lana` in an empty workspace must reach a working prompt without reading setup docs; auto-creation is bounded to artifacts derivable from defaults (data dirs, folder scaffold, default config) - shipped model data files stay required until distribution bundles them.

**LANAAGNT-DD-25:** App directory separates infrastructure base from workspace (bootstrapping bug 2026-08-31). Rationale: when Lana runs as a packaged binary (`dist/lana.exe`) the CWD is the user's project, not the binary's directory; config, prompt library, and runtime data must resolve relative to the EXE location, not the user's CWD. Resolution hierarchy: `--app-dir <path>` CLI flag > env `LANA_APP_DIR` > PyApp exe parent (auto-detected: PyApp sets the `PYAPP` env var to the outer binary's absolute path when built with `PYAPP_PASS_LOCATION=1`, `resolve_app_dir()` reads it) > workspace (CWD fallback for dev mode). The workspace stays CWD for tool operations (file reading/editing, command execution, git root detection, `<user_information>`). In ACP mode, the app directory is auto-detected from the `PYAPP` env var; the ACP `session/new` `cwd` param sets only the workspace.

## 3. Implementation Guarantees

**LANAAGNT-IG-01:** The system prompt byte content is identical across all Generator calls within one session (cache prefix stability).

## 4. Data Structures

**LanaConfig (`config/lana-config.json`):**
```json
{
  "roles": {
    "generator":  { "model_id": "claude-sonnet-4-5-20250929", "effort": "medium" },
    "summarizer": { "model_id": "gpt-4.1-mini", "effort": "low" },
    "websearch":  { "model_id": "gpt-4.1-mini", "effort": "low" }
  },
  "agent_folder": ".lana",          // resolved relative to app directory (DD-25)
  "data_dir": ".lana-data",            // resolved relative to app directory (DD-25)
  "rule_block_max_chars": 6000,
  "max_tool_calls_per_prompt": 25,
  "auto_continue": false,
  "tool_result_max_chars": 50000,
  "compaction_threshold_fraction": 0.6,
  "compaction_threshold_max_tokens": 150000,
  "execution_policy": "manual",
  "command_denylist": ["rm", "del", "rmdir", "erase", "ri", "Remove-Item", "Move-Item", "format", "kill", "pkill", "Stop-Process", "shutdown", "git push --force"]
}
```

## 5. Document History

**[2026-09-01 21:45]**
- Extracted from `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]`: FR-01, FR-02, FR-03, DD-02, DD-12, DD-16, DD-23, DD-25, IG-01, Section 10 (LanaConfig schema)
- Content is verbatim from source with section renumbering and header block update only
