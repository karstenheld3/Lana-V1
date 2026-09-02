# SPEC: Lana Product Overview

**Doc ID**: LANAAGNT-SP01
**Goal**: Define the product vision, domain model, non-functional requirements, and architectural constraints for the Lana CLI agent
**Timeline**: Created 2026-08-29, Extracted from _SPEC_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `src/lana/models.py` (canonical types)
- `src/lana/events.py` (AgentEvent stream)

**Depends on:**
- `_INFO_OPEN_DESIGN_QUESTIONS.md [LANAAGNT-IN01]` for design question analysis (OQ-01 to OQ-43)

**Does not depend on:**
- Any component-specific spec (02-AgentCore through 11-Selftest) -- this is the root spec

## Table of Contents

1. [Scenario](#1-scenario)
2. [Context](#2-context)
3. [Domain Objects](#3-domain-objects)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [Design Decisions](#5-design-decisions)
6. [Implementation Guarantees](#6-implementation-guarantees)
7. [Technical Constraints](#7-technical-constraints)
8. [Document History](#8-document-history)

## 1. Scenario

**Problem:** The IPPS prompt system (8 rules files, 46 workflows, 21 skills) currently runs only inside Windsurf Cascade. There is no self-owned agent that can load these rules, expand workflow slash commands, invoke skills, and execute an agentic tool loop against OpenAI/Anthropic APIs directly.

**Solution:**
- Interactive CLI agent `lana` with a single-model agentic tool loop (16 tools incl. web research and session trajectory search)
- Loads a configurable prompt system folder (rules/, workflows/, skills/) - IPPS or any workspace `.lana/` folder
- Assembles a Cascade-compatible system prompt (identity, behavioral sections, MEMORY rule blocks, workflow list)
- Manages context via checkpoint compaction, persists sessions as JSON Lines (JSONL), tracks cost per turn

**What we don't want:**
- Multi-model Brain/Generator pipeline (OQ-01: mechanism unproven, doubles cost/latency)
- Any LLM provider besides OpenAI and Anthropic (user constraint)
- A memory database in MVP-1 (OQ-17 to OQ-20: rules injection covers the "global rules" memory type; rest deferred)
- MCP client, ACP frontend, code_search subagent in MVP-1 (deferred; see section 2 roadmap)
- A feature flag system (OQ-39: plain config keys suffice)
- Telemetry of any kind (deliberate privacy improvement over Cascade's full-context echo)

## 2. Context

### 2.1 Target Prompt System: IPPS

Analyzed at `.lana/` (397 files; snapshot 2026-08-29 - the folder evolves, e.g. 23 skills by 2026-08-30; the loader derives counts from the filesystem at startup):

- `rules/` - 8 Markdown files, ~59 KB total, largest 13.5 KB (`devsystem-core.md`). YAML frontmatter: `trigger: always_on`
- `workflows/` - 46 Markdown files. YAML frontmatter: `description`, `auto_execution_mode`. Invoked by user as `/name`
- `skills/` - 21 folders, each with `SKILL.md` (frontmatter: `name`, `description`) plus 1-160 supporting files

The rules reference Cascade tool names (`read_file`, `run_command`, `todo_list`, ...) and conventions (MEMORY blocks, MUST-NOT-FORGET, session folders). Running this system faithfully requires tool-name compatibility (OQ-30) and the MEMORY block injection format (OQ-23).

### 2.2 MVP Roadmap (scope boundary)

- **MVP-1** (this SPEC): CLI frontend, single Generator model, 16 tools (incl. web research via provider-native search and trajectory search over session logs), prompt system loading, checkpoint compaction, session persistence, cost tracking, command safety
- **MVP-2** (not specified here): ACP frontend, MCP client
- **MVP-3** (not specified here): memory database, code_search subagent, hooks, automated memories

**Workspace definition:** the workspace is the current working directory at `lana` launch. All `[workspace]` paths, the file-write safety boundary (LANAAGNT-FR-12), and `<user_information>` derive from it.

**App directory definition:** the app directory is the base directory for Lana's own infrastructure: config files, prompt library (`agent_folder`), and runtime data (`data_dir`). Resolution: `--app-dir` flag > env `LANA_APP_DIR` > PyApp exe parent (auto-detected via `PYAPP` env var when built with `PYAPP_PASS_LOCATION=1`) > workspace (CWD fallback for dev mode). When running as a packaged binary, the auto-detection ensures config/agent/data stay next to the EXE regardless of CWD (DD-25).

**Tool demand evidence** (full-text scan of all 397 IPPS files, 2026-08-29): `read_url_content` 17 refs / 5 files and `search_web` 14 refs / 4 files - concentrated in the deep-research skill (24 files, flagship capability) and `/research`; `find_by_name` 5, `read_file` 4, `run_command` 4, `command_status` 3, `grep_search` 2 (all in MVP-1); `trajectory_search` 3 refs in `/remove` only; `mcp1_*` 3 refs in browser skills; all other Cascade tools 0 refs.

**Known MVP-1 limitation:** Workflows using MCP tools (browser automation skills) will load but cannot complete those steps. (`/remove` became executable 2026-08-30 - `trajectory_search` added, FR-15.) Web research workflows (`/deep-research`, `/research`) and all file/command/document workflows (`/prime`, `/write-spec`, `/verify`, `/session-new`, `/commit`, ...) are fully executable.

## 3. Domain Objects

### PromptSystem

A **PromptSystem** represents one folder containing agent configuration content.

**Storage:** configurable via `agent_folder` in config (relative path resolved against the app directory, absolute used as-is)
**Key properties:**
- `rules` - list of RuleFile, loaded from `rules/*.md`
- `workflows` - list of WorkflowFile, loaded from `workflows/*.md`
- `skills` - list of SkillFolder, loaded from `skills/*/SKILL.md`

### RuleFile

A **RuleFile** is one Markdown file injected as a `<MEMORY[filename]>` block into the system prompt.

**Key properties:**
- `filename` - block label
- `trigger` - from frontmatter; MVP-1 injects `always_on` (or missing frontmatter), skips all other trigger values
- `content` - Markdown body without frontmatter, truncated at per-block character limit

### WorkflowFile

A **WorkflowFile** is one Markdown file invocable as a slash command.

**Key properties:**
- `name` - filename without extension; invocation token is `/name`
- `description` - from frontmatter; shown in the system prompt workflow list
- `content` - full Markdown body, injected into the user message on invocation

### SkillFolder

A **SkillFolder** is one folder with `SKILL.md` and supporting files, loadable via the `skill` tool.

**Key properties:**
- `name`, `description` - from SKILL.md frontmatter; listed in the `skill` tool description
- `content` - SKILL.md body returned on invocation
- `supporting_files` - relative paths listed in the tool result (agent reads them via `read_file`)

### ToolDefinition

A **ToolDefinition** is one callable capability exposed to the Generator: name, description, JSON Schema. 16 in MVP-1 (see LANAAGNT-FR-10).

### ToolCall

A **ToolCall** is one Generator-requested tool execution: unique ID, tool name, arguments (JSON), result text, status.

### Turn

A **Turn** is one Generator API call and its outcome: assistant text, thinking content, 0-N ToolCalls, token usage, cost.

### Session

A **Session** is one conversation: ordered event log (JSONL file), cumulative usage/cost, 0-N Checkpoints. The JSONL is self-contained: its first event records the full Generator environment (system prompt, tool definitions, config snapshot), so the file alone reconstructs everything ever sent to the Generator (LANAAGNT-FR-08, LANAAGNT-IG-07).

**Storage:** `[workspace]/.lana-data/sessions/[YYYY-MM-DD_HHMMSS]_[id].jsonl`

### Checkpoint

A **Checkpoint** is a compaction artifact replacing truncated history: objective, summary, code interaction history (one Summarizer call) plus the last TodoList state (deterministic extraction, no LLM).

### TodoList

A **TodoList** is the full-replace task state maintained via the `todo_list` tool: items with `id`, `content`, `status` (pending/in_progress/completed), `priority` (high/medium/low).

### ModelRole

A **ModelRole** maps a pipeline function to a model. MVP-1 roles: `generator`, `summarizer`, `websearch`. Each has: `model_id` (must exist and be enabled in `model-registry.json`), `effort` (level from `model-parameter-mapping.json`).

### ProviderAdapter

A **ProviderAdapter** translates the canonical internal message/tool-call model to one provider API. Exactly two: OpenAI (Responses), Anthropic (Messages).

### ExecutionPolicy

An **ExecutionPolicy** governs command auto-execution. One of: `manual` (every command approved), `auto` (Generator-classified safe commands run, unsafe require approval), `turbo` (all run except denylist matches).

### AgentEvent

An **AgentEvent** is one item on the internal event stream consumed by the frontend: `session_started`, `user_message`, `turn_started`, `text_delta`, `thinking_delta`, `tool_call_requested`, `tool_call_finished`, `approval_required`, `checkpoint_created`, `turn_finished`, `error`, `prompt_step`. The `checkpoint_created` event carries the full checkpoint text (required for resume replay). The `session_started` event carries the byte-verbatim system prompt, the verbatim tool definitions, the resolved config snapshot, and a prompt system fingerprint; the `turn_finished` event carries the turn's resendable thinking payloads (both required for full recall, LANAAGNT-FR-08). The `prompt_step` event marks prompt queue boundaries in headless mode (LANAACPB-FR-12).

### LanaConfig

A **LanaConfig** is the merged runtime configuration from `config/lana-config.json` plus CLI flag overrides. Schema in `_SPEC_LANA_03-PromptAndConfig.md [LANAPRCF-SP01]`.

## 4. Non-Functional Requirements

**LANAAGNT-NFR-01: Security - No Telemetry**
- The Lana process itself makes no network calls except `api.openai.com`, `api.anthropic.com`, and user-approved `read_url_content` fetches (commands executed via `run_command` are outside this guarantee and covered by the approval gates in LANAAGNT-FR-12)
- API keys never logged, never echoed, never written to session files
- Verification: network capture of one session without `run_command` or `read_url_content` usage shows only the two API hosts

**LANAAGNT-NFR-02: Reliability - Crash-Safe Sessions**
- A killed process loses at most the in-flight turn; JSONL replay restores everything prior
- Verification: kill -9 during a tool loop, resume, conversation state intact

**LANAAGNT-NFR-03: Performance - Prompt Cache Utilization**
- After turn 1 of a session, Anthropic cache-read tokens cover the system prompt + tool definitions (verified via API usage fields)
- Startup (config + prompt system load) under 2 seconds for IPPS (397 files)

**LANAAGNT-NFR-04: Observability - Debuggable API Traffic**
- `--debug` flag writes full request/response JSON (keys redacted) to `[workspace]/.lana-data/logs/`
- Every AgentEvent carries a timestamp (`YYYY-MM-DD HH:MM:SS`)

**LANAAGNT-NFR-05: Security - Prompt Injection Threat Model**
- All content the Generator reads (workspace files, prompt system content, command output) is untrusted input
- `manual` is the only ExecutionPolicy with an adversarial-input guarantee; `auto` and `turbo` accept prompt-injection risk and are recommended only for trusted workspaces
- Switching to `auto` or `turbo` prints a one-line risk notice at startup (RV01 RF-08)

## 5. Design Decisions

**LANAAGNT-DD-06:** Internal AgentEvent stream as the frontend contract (OQ-09, OQ-32). Rationale: the CLI renderer is the only MVP-1 consumer, but the ACP server in MVP-2 subscribes to the same stream - this is the one structural investment made for the future.

**LANAAGNT-DD-09:** No memory database in MVP-1 (OQ-17 to OQ-20). Rationale: IPPS needs only the "global rules" memory type, which rules injection provides; `create_memory` without retrieval is dead weight; deferring removes storage, retrieval, and injection-timing questions entirely.

**LANAAGNT-DD-17:** Python 3.12+, dependencies: `openai`, `anthropic`, `pydantic`, `rich`, `prompt_toolkit`, `pyyaml` (OQ-43). Rationale: minimal set - SDKs, canonical model validation, terminal rendering, input line editing, frontmatter parsing. No `textual` (full TUI framework is MVP overkill).

**LANAAGNT-DD-18:** Deferred to MVP-2/3 with no MVP-1 implementation: ACP frontend (OQ-32 to OQ-37), MCP client (OQ-25, OQ-36), hooks (OQ-26), mid-session model switching (OQ-06), code_search subagent (OQ-28), proactive summarization (OQ-15). Rationale: user directive - simple but effective, avoid complexity and risk.

## 6. Implementation Guarantees

**LANAAGNT-IG-05:** Every user-visible failure (missing key, disabled model, malformed frontmatter, API error) produces a self-contained error message naming file/key/model and the corrective action.

## 7. Technical Constraints

- Provider parameter methods (temperature vs reasoning_effort vs thinking) come from `model_id_startswith` matching in `model-registry.json` - Lana never hardcodes per-model parameter logic
- Anthropic multi-turn tool use requires resending prior thinking blocks; the canonical model must store them per turn
- Token projection is usage-anchored (LANAAGNT-FR-07); the chars/4 heuristic covers only the delta since the last provider-reported count, bounding the known 2-4x under-count risk of pure heuristics on JSON-heavy payloads
- No pre-call emergency compaction in MVP-1 - accepted risk: with the 50K-char tool result cap and the 60% threshold, the remaining 40% window headroom absorbs a full turn of capped results (`LANAAGNT-SP01-RV01` RF-03 reconcile decision)
- `run_command` executes via the host shell (pwsh on Windows); working directory always explicit, `cd` never part of the command line (Cascade contract)
- YAML frontmatter parsing must tolerate IPPS variations: key order differs across files, `workspace-rules.md` is near-empty (32 bytes)
- Windows paths and UTF-8 file content are the default test environment; encoding per `core-conventions.md`
- Tool definition authority chain: `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` (live-session verbatim, all 16 tools) > `HowWindsurfCascadeWorks.md` chapters 8-9 (wire-capture, 12 of 16 verbatim) > any memory of tool behavior

## 8. Document History

**[2026-09-01 21:58]**
- Fixed: ToolDefinition count 12 -> 16 (synced from `src/lana/tools/definitions.py` DESCRIPTION_TEMPLATES)
- Fixed: AgentEvent types 11 -> 12 (added `prompt_step` from LANAACPB-FR-12, synced from `src/lana/events.py`)
- Added: `prompt_system_fingerprint` to `session_started` description (synced from `SessionStarted` class)
- Source: `/fact-check` + `/sync` against source code

**[2026-09-01 21:45]**
- Extracted from `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]`: Sections 1 (Scenario), 2 (Context), 3 (Domain Objects), 5 (Non-Functional Requirements), 13 (Technical Constraints), DD-06, DD-09, DD-17, DD-18, IG-05
- Content is verbatim from source with section renumbering and header block update only
- LanaConfig schema reference updated to point to `_SPEC_LANA_03-PromptAndConfig.md [LANAPRCF-SP01]`
