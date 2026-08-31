# SPEC: Lana MVP-1 - CLI Agent Running IPPS

**Doc ID**: LANAAGNT-SP01
**Feature**: lana-mvp-1
**Goal**: Specify a minimal Python command-line interface (CLI) agent that runs the IPPS prompt system (rules, workflows, skills) with an agentic tool loop on OpenAI/Anthropic backends
**Timeline**: Created 2026-08-29, Updated 0 times
**Target file(s)**:
- `src/lana/` (new package)
- `config/lana-config.json` (new config file)

**Depends on:**
- `_INFO_OPEN_DESIGN_QUESTIONS.md [LANAAGNT-IN01]` for design question analysis (OQ-01 to OQ-43)
- `config/model-registry.json` for model properties and boundaries
- `config/model-parameter-mapping.json` for effort level translation
- `config/model-pricing.json` for cost tracking
- `config/.api-keys.txt` for API keys
- `.lana/` as the reference prompt system to run

**Does not depend on:**
- ACP (Agent Client Protocol) research docs (ACP deferred to MVP-2, only the event abstraction prepares for it)
- MCP (Model Context Protocol) SDK (deferred to MVP-2)

## MUST-NOT-FORGET

- Every design decision cites its OQ-NN from LANAAGNT-IN01 - no undocumented deviations
- Only OpenAI and Anthropic backends - no other LLM providers, no external search APIs
- Existing `config/` files are read as-is, never duplicated or rewritten
- Tool names, descriptions, and schemas copied verbatim from the Cascade reference (OQ-30) - the IPPS rules reference these exact names
- SPEC defines WHAT, not HOW - no code, line numbers, or function signatures
- Deferred scope (ACP, MCP, memory database, web tools) must not leak requirements into MVP-1

## Table of Contents

1. [Scenario](#1-scenario)
2. [Context](#2-context)
3. [Domain Objects](#3-domain-objects)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Design Decisions](#6-design-decisions)
7. [Implementation Guarantees](#7-implementation-guarantees)
8. [Key Mechanisms](#8-key-mechanisms)
9. [Action Flow](#9-action-flow)
10. [Data Structures](#10-data-structures)
11. [User Actions](#11-user-actions)
12. [Logging Requirements](#12-logging-requirements)
13. [Technical Constraints](#13-technical-constraints)
14. [Document History](#14-document-history)

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

**Install root definition:** the install root is the base directory for Lana's own infrastructure: config files, prompt library (`agent_folder`), and runtime data (`data_dir`). Resolution: `--install-root` flag (or env `LANA_INSTALL_ROOT`) if set, otherwise falls back to the workspace. When running as a packaged binary, the launcher sets `--install-root` to the binary's directory so config/agent/data stay next to the EXE regardless of CWD (DD-25).

**Tool demand evidence** (full-text scan of all 397 IPPS files, 2026-08-29): `read_url_content` 17 refs / 5 files and `search_web` 14 refs / 4 files - concentrated in the deep-research skill (24 files, flagship capability) and `/research`; `find_by_name` 5, `read_file` 4, `run_command` 4, `command_status` 3, `grep_search` 2 (all in MVP-1); `trajectory_search` 3 refs in `/remove` only; `mcp1_*` 3 refs in browser skills; all other Cascade tools 0 refs.

**Known MVP-1 limitation:** Workflows using MCP tools (browser automation skills) will load but cannot complete those steps. (`/remove` became executable 2026-08-30 - `trajectory_search` added, FR-15.) Web research workflows (`/deep-research`, `/research`) and all file/command/document workflows (`/prime`, `/write-spec`, `/verify`, `/session-new`, `/commit`, ...) are fully executable.

## 3. Domain Objects

### PromptSystem

A **PromptSystem** represents one folder containing agent configuration content.

**Storage:** configurable via `agent_folder` in config (relative path resolved against the install root, absolute used as-is)
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

A **ToolDefinition** is one callable capability exposed to the Generator: name, description, JSON Schema. 12 in MVP-1 (see LANAAGNT-FR-10).

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

An **AgentEvent** is one item on the internal event stream consumed by the frontend: `session_started`, `user_message`, `turn_started`, `text_delta`, `thinking_delta`, `tool_call_requested`, `tool_call_finished`, `approval_required`, `checkpoint_created`, `turn_finished`, `error`. The `checkpoint_created` event carries the full checkpoint text (required for resume replay). The `session_started` event carries the byte-verbatim system prompt, the verbatim tool definitions, and the resolved config snapshot; the `turn_finished` event carries the turn's resendable thinking payloads (both required for full recall, LANAAGNT-FR-08).

### LanaConfig

A **LanaConfig** is the merged runtime configuration from `config/lana-config.json` plus CLI flag overrides. Schema in section 10.

## 4. Functional Requirements

**LANAAGNT-FR-01: Configuration Loading**
- Read `config/lana-config.json` from the install root (not the workspace); validate `model_id` values against `model-registry.json` (`enabled: true` required)
- Resolve API keys: environment variables `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` first, then `config/.api-keys.txt` (OQ-41); report key source per provider at boot in the format `Keys: Provider (Environment variable: VAR)` or `Keys: Provider (.\config\.api-keys.txt: VAR)` so the user knows where keys come from
- Translate per-role `effort` via `model-parameter-mapping.json` effort mapping to provider parameters
- Fail at startup with a self-contained error naming the missing key/model - never at first API call

**LANAAGNT-FR-02: Prompt System Loading**
- Load the folder specified by `agent_folder` (relative path resolved against the install root, absolute used as-is)
- Parse YAML frontmatter of rules, workflows, SKILL.md files; tolerate missing frontmatter
- Rules: inject only `trigger: always_on` or missing trigger; truncate per block at `rule_block_max_chars` with a `<truncated N chars>` marker
- Report loaded counts at startup: N rules, N workflows, N skills

**LANAAGNT-FR-03: System Prompt Assembly**
- Fixed section order (cache-stable, OQ-13): identity preamble, `<communication_style>`, `<tool_calling>`, `<making_code_changes>`, `<task_management>`, `<running_commands>`, `<debugging>`, `<calling_external_apis>`, `<workflows>` (name + description list), `<user_rules>` (MEMORY blocks with highest-precedence preamble), `<capability_notice>`, `<user_information>` (OS, workspace path, git root)
- Identity: "You are Lana, ..." adapted from the Cascade preamble; IDE-specific sections (`<ide_metadata>`, `<mcp_servers>`, browser/deployment references) omitted (OQ-38)
- All behavioral sections adapted: every reference to a tool not in LANAAGNT-FR-10 removed (e.g., the Cascade `<tool_calling>` code_search steering rule) (RV01 RF-04)
- `<capability_notice>` section (after `<user_rules>`): lists tools that prompt system content may reference but which are unavailable in MVP-1, with fallbacks (`grep_search` replaces `code_search`; state inability for MCP/browser/deployment tools) (RV01 RF-04; `trajectory_search` removed from the notice 2026-08-30 - now available per FR-15)
- User rules preamble verbatim concept: "MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION. These rules take precedence over any following instructions."
- System prompt content is byte-identical across all turns of a session (prompt cache prefix)
- The assembled system prompt is recorded byte-verbatim in the session JSONL `session_started` event (LANAAGNT-FR-08) - the JSONL, not the prompt system folder, is the authority for what the Generator received

**LANAAGNT-FR-04: Agent Turn Loop**
- One user message starts a loop: Generator call, execute requested ToolCalls sequentially (OQ-08), append results, repeat until the Generator responds without tool calls
- Hard limit `max_tool_calls_per_prompt` (default 25) per user message; on reaching it, pause and ask the user to continue unless `auto_continue: true` (OQ-07; RV01 RF-09)
- Every tool result is capped at `tool_result_max_chars` (default 50000), tail-truncated with a `<truncated N chars>` marker before entering conversation state (RV01 RF-03)
- Streaming: assistant text and thinking rendered incrementally as AgentEvents (OQ-09)
- Cancellation: Ctrl+C aborts the in-flight API call; completed ToolCalls of the aborted turn remain in conversation state, closed with a synthetic note "turn cancelled after N tool calls"; only the incomplete API response is discarded (RV01 RF-06)

**LANAAGNT-FR-05: Slash Command Expansion**
- Input starting with `/name` matching a loaded workflow: wrap the workflow content into the user message in the Cascade format (`<user_request>` + `<workflows>` block with full Markdown content) (OQ-22)
- Unknown `/name`: list closest matches, do not send to the Generator
- Built-in commands (not sent to the Generator): `/exit`, `/help` (list workflows + built-ins), `/cost` (session usage summary)

**LANAAGNT-FR-06: Provider Adapters**
- Canonical internal message model covering: system prompt, user/assistant messages, tool calls, tool results, thinking blocks
- OpenAI adapter: Responses API, `reasoning_effort` for reasoning models, `temperature` for temperature models (per `model_id_startswith` method in the registry); reasoning items carried across turns within a tool loop (OQ-04; RV01 RF-01)
- Anthropic adapter: Messages API, `thinking` budget from effort mapping, thinking blocks resent in multi-turn tool use, `cache_control` breakpoints on the tool definitions block and the system prompt block (provider-defined prefix order applies) plus top-level automatic caching so growing conversation history is cache-read too (OQ-13; RV01 RF-07)
- Adapter selection by `provider` field of the resolved model in `model-registry.json` (OQ-03)

**LANAAGNT-FR-07: Checkpoint Compaction**
- Trigger: projected context tokens reach or exceed `min(compaction_threshold_fraction x generator max_input, compaction_threshold_max_tokens)` (defaults 0.6 and 150000), checked after each turn - including between the turns of one tool loop (OQ-14), reactive only (OQ-15)
- Projection is usage-anchored: last provider-reported input token count + chars/4 estimate of content added since that call (RV01 RF-05)
- One Summarizer call producing three labeled sections: objective, conversation summary, code interaction history (OQ-12)
- Last `todo_list` state extracted deterministically from the event log - never via the Summarizer (OQ-12)
- Checkpoint replaces truncated history as the first conversation message; includes the three hardcoded behavioral anchors from the Cascade template: "keep this up to date with todo_list tool", "Make sure to continue working off of this TODO list", "DO NOT ACKNOWLEDGE THIS CHECKPOINT MESSAGE"
- Fail-safe: on Summarizer call failure, no truncation occurs - warn the user and continue uncompacted
- No `todo_list` state in the event log: the todo section is omitted from the checkpoint
- System prompt and tool definitions never truncated

**LANAAGNT-FR-08: Session Persistence - Full Recall**
- First event of every session file: `session_started` carrying 1) the byte-verbatim assembled system prompt, 2) the verbatim tool definitions array (name, description, JSON Schema) as sent to the provider, 3) the resolved config snapshot (role -> model_id/effort/provider, execution policy, compaction thresholds, tool/result limits), 4) a prompt system fingerprint (ordered path list, per-folder file counts, content hash)
- Every AgentEvent appended to the session JSONL file at occurrence (crash-safe) (OQ-10)
- Each event line is flushed to disk at write time - external processes can tail the session file as a live activity monitor (test harness contract, LANAAGNT-DD-20)
- Full recall: every byte sent to the Generator is reconstructible from the JSONL alone - system prompt and tool definitions from `session_started`, conversation from event projection, checkpoint text from `checkpoint_created` (LANAAGNT-IG-07)
- Assistant thinking payloads that the adapter must resend on later calls (Anthropic thinking blocks with signatures) are recorded verbatim on the turn's `turn_finished` event - resume reproduces the exact resend content without adding a 12th event type
- `lana --resume [session-file]` rebuilds conversation state, system prompt, and tool definitions from the JSONL and continues - the recorded system prompt is reused byte-verbatim (preserves LANAAGNT-IG-01 across resume); the on-disk prompt system is loaded only for new workflow expansion and skill invocation
- Resume fingerprint check: when the loaded prompt system's fingerprint differs from the recorded one, print a one-line warning naming the difference (counts/hash) - the recorded system prompt still wins for Generator calls
- Model change on resume: role -> model resolution follows the CURRENT `lana-config.json` (enables switching models between runs); the recorded config snapshot serves audit and reconstruction, never model selection; a differing generator is reported at startup (recorded vs current)
- Provider independence: recall never depends on provider-side state - prompt caches are ephemeral (minutes-scale TTL) and provider-bound; after a model or provider change the full recorded context is re-sent from the JSONL (cold-cache cost effect only, no information loss)
- Cross-provider thinking payloads: recorded thinking payloads are resent only when the resumed provider matches their recording provider; on provider change they are dropped from the resend (signatures are provider-bound) while their rendered text remains in the log for recall
- Session files never auto-deleted

**LANAAGNT-FR-09: Cost Tracking**
- Per-turn: input/output/cache-read/cache-write tokens and cost from `model-pricing.json`, rendered after each turn (OQ-42)
- `/cost`: session totals per role (generator, summarizer, websearch)
- Unknown model in pricing file: show token counts with cost marked `?`

**LANAAGNT-FR-10: Tool Set (16 tools)**
- File reading: `read_file`, `list_dir`, `grep_search`, `find_by_name`
- File editing: `edit`, `multi_edit`, `write_to_file`
- Execution: `run_command`, `command_status`
- Web research: `search_web`, `read_url_content`, `view_content_chunk` (behavior in LANAAGNT-FR-13)
- Session history: `trajectory_search` (behavior in LANAAGNT-FR-15; added 2026-08-30, resolves deferred candidate D-01)
- State: `todo_list`
- Prompt system: `skill`
- Interaction: `ask_user_question`
- Names, descriptions, parameter names, and JSON Schemas verbatim from the Cascade reference documented in `HowWindsurfCascadeWorks.md` chapters 8-9 (OQ-27, OQ-30); OS/shell placeholders in `run_command` filled per host
- `read_file` refuses image files with an explanatory error - visual presentation is unavailable in a CLI; the capability notice states this limitation (synced from implementation 2026-08-30)
- Dropped from Cascade's 27 with rationale recorded in LANAAGNT-DD-10

**LANAAGNT-FR-11: Edit Enforcement Gates**
- `edit`/`multi_edit` fail unless the target file was read via `read_file` in the current session after its last external modification (OQ-31)
- `old_string` uniqueness enforced unless `replace_all`; `old_string == new_string` rejected
- `write_to_file` fails on existing target files
- A successful `edit`/`multi_edit`/`write_to_file` updates the read ledger to the post-edit state; "external modification" = any change not performed by Lana's own tools (RV01 RF-10)

**LANAAGNT-FR-12: Command Safety**
- Generator self-classifies via `SafeToAutoRun` (schema kept verbatim); Lana runtime applies the ExecutionPolicy on top (OQ-29)
- `manual` (default): every `run_command` requires interactive y/n/a approval showing the exact command line and working directory; `a` (all) approves the current and all remaining approval-gated tool calls for the rest of the session
- `auto`: `SafeToAutoRun: true` commands run without prompt; denylist match overrides to approval
- `turbo`: all run except denylist matches (always require approval)
- Denylist matching: case-insensitive comparison of the command line's first token (multi-token entries prefix-match the command line); default: `rm`, `del`, `rmdir`, `erase`, `ri`, `Remove-Item`, `Move-Item`, `format`, `kill`, `pkill`, `Stop-Process`, `shutdown`, `git push --force` (RV01 RF-02)
- Shell wrapper invocations (`pwsh`, `powershell`, `cmd`, `bash` with `-Command`, `-c`, or `/c`) always require approval in `auto` and `turbo` - inner commands are not parsed (RV01 RF-02)
- Approval prompts also gate `write_to_file`/`edit` outside the workspace root

**LANAAGNT-FR-13: Web Research Tools**
- `search_web`: implemented as a side-call by the `websearch` role using the provider-native web search tool (OpenAI: `web_search` on the Responses API; Anthropic: `web_search` server tool) - stays within the two allowed backends; result rendered in Cascade's documented format: 5 results with title, URL, ~300-char summary, plus the trailing read-further prompt
- `read_url_content`: local HTTP/HTTPS GET + HTML-to-text conversion + chunking; returns the first chunk and a `document_id`; NOT an LLM backend call - plain fetching, same as Cascade's own tool
- `view_content_chunk`: returns chunk at `position` for a previously fetched `document_id`
- Approval: `read_url_content` always requires interactive approval before fetching (Cascade parity); `search_web` requires none (provider-mediated, no direct site contact)
- Web tool results count against `tool_result_max_chars` like all tool results

**LANAAGNT-FR-14: Headless Mode and Test Interfaces**
- `lana -p "<prompt>"`: non-interactive single-prompt run - executes the full turn loop, prints the final assistant text (default) or streams every AgentEvent as JSON Lines to stdout (`--output-format jsonl`), then exits
- Exit codes: 0 = turn completed, 2 = configuration error, 3 = provider/API failure after retries, 4 = stopped without completion (cancelled or tool-call limit without continue)
- Non-interactive approvals: in headless mode or when stdin is not a terminal, `approval_required` is DENIED automatically - the tool result reads "approval denied (non-interactive session)" and the loop continues; `ask_user_question` returns "no answer (non-interactive session)"
- `--config <path>` (or env `LANA_CONFIG`) overrides the default `config/lana-config.json` location - test isolation without touching the real config
- When stdin is not a terminal, the interactive loop reads plain lines from stdin (no terminal-dependent input features) - pipe-driven sessions work
- Scripted adapter (test infrastructure, NOT a third LLM backend): env `LANA_SCRIPTED_ADAPTER=<script.jsonl>` replaces both provider adapters with a deterministic replay adapter; never active without the env var; the startup banner marks the session SCRIPTED; no API keys required in this mode
- Built-ins (`/help`, `/cost`, `/exit`) are dispatched in headless `-p` mode exactly like in the REPL - they never reach the Generator (synced from implementation 2026-08-30)

**LANAAGNT-FR-15: Session Trajectory Search**
- `trajectory_search` operates on Lana's own session JSONL files - they ARE the trajectories (deferred candidate D-01 design)
- `ID` resolves against `[workspace]/.lana-data/sessions/`: exact filename, filename without extension, or unique prefix; unknown ID -> error listing available session ids
- Each session event renders as one chunk (type + content excerpt); `Query` terms score chunks by case-insensitive term overlap, results sorted by score descending
- Empty `Query` returns all chunks in chronological order (tool contract: "An empty query will return all trajectory steps")
- Maximum 50 chunks returned (tool contract); results pass through `tool_result_max_chars` like all tool results
- `SearchType` `"user"` -> error (no user-activity index in Lana; the tool contract already forbids it)
- Scoring is lexical term overlap, not embedding-based [ASSUMED - adequate for session-scale text; revisit if relevance quality disappoints]

**LANAAGNT-FR-16: Zero-Setup Startup and Runtime Resilience** (hardening per `_INFO_ROBUSTNESS_HAZARDS.md [LANAAGNT-IN03]`)
- Zero-setup: at startup Lana auto-creates every missing artifact it can create safely - the runtime data directory (`data_dir` with `sessions/`), the agent folder scaffold (`agent_folder` with `rules/`, `workflows/`, `skills/`), and a default `config/lana-config.json` (DD-02 default roles) - all relative to the install root - and prints one line per created artifact; no init command, no manual setup steps (DD-23)
- Auto-created config applies only to the DEFAULT config path; an explicit `--config`/`LANA_CONFIG` override that does not exist stays a ConfigError (an explicit path is a user statement, not a gap)
- Model data files (`model-registry.json`, `model-parameter-mapping.json`, `model-pricing.json`) are shipped data: when missing, startup fails with the existing self-contained ConfigError (bundled-default distribution deferred)
- Empty prompt system (0 rules, 0 workflows, 0 skills): print a one-line notice that Lana runs without prompt system content
- Startup resilience (IN03 CR-01): `OSError` during startup is handled like `ConfigError` - self-contained message naming path and corrective action, exit code 2, never a raw traceback
- REPL/headless resilience (IN03 CR-02/CR-03): any unexpected exception in a prompt turn prints a self-contained error; the REPL stays alive (headless: exit code 4); the session JSONL survives for `--resume`
- Compaction fail-safe widened (IN03 CR-04): the entire compaction body runs under EC-17 warn-and-continue semantics, not only the Summarizer call
- `command_status` wait clamp (IN03 BL-03): `WaitDurationSeconds` is clamped to 60 s server-side (the bound the tool description already promises); a triggered clamp is noted in the result
- Fetch wall-clock deadline (IN03 BL-07): `read_url_content` reads in chunks under a 120 s wall-clock deadline - a trickling server cannot extend a fetch beyond it
- Provider timeouts and visible retries (IN03 BL-05/UX-03): SDK clients are constructed with explicit timeouts (connect 10 s, read 120 s) and SDK-internal retries disabled; Lana owns up to 2 retries on retryable failures (connection errors, HTTP 408/429/5xx) occurring before the first streamed delta, each announced as a user-visible WARNING notice with backoff delay
- Responsiveness (IN03 UX-01/02/04/05): a status line renders between turn start and the first visible output, ticking elapsed seconds while thinking stays hidden; `--show-thinking` streams thinking dim-styled; a notice line announces compaction BEFORE the Summarizer call; resume prints the session file name BEFORE parsing
- Process cleanup (IN03 BL-02/BL-06): live tool child processes (foreground and background `pwsh`) are terminated on turn cancellation and at process exit; survivors are named in one line

## 5. Non-Functional Requirements

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

## 6. Design Decisions

Each decision resolves the referenced open question from `_INFO_OPEN_DESIGN_QUESTIONS.md [LANAAGNT-IN01]`.

**LANAAGNT-DD-01:** Single-model loop, no Brain (OQ-01). Rationale: the Brain/Generator interplay is [ASSUMED] even in the wire capture and cannot be copied; modern generators plan and call tools natively; a second model doubles latency and cost for unproven benefit. The ModelRole abstraction keeps the door open.

**LANAAGNT-DD-02:** Two roles only - `generator` and `summarizer` - configured in `lana-config.json`; defaults `claude-sonnet-4-5-20250929` and `gpt-4.1-mini` (OQ-02, OQ-05). Rationale: both are `enabled` in the registry; the summarizer needs no reasoning; role → model mapping stays pure configuration with no hardcoded model IDs.

**LANAAGNT-DD-03:** Own thin adapter layer over the official `openai` and `anthropic` Python SDKs; no LiteLLM (OQ-03). Rationale: two providers is small N; a third-party abstraction adds a dependency, lags provider features, and obscures cache control.

**LANAAGNT-DD-04:** OpenAI adapter uses the Responses API (OQ-04, matches the INFO leaning; revised per `LANAAGNT-SP01-RV01` RF-01) [PROVEN - live round trips TC-40/TC-42 green 2026-08-30]. Rationale: gpt-5.4+ models do not support tool calling with `reasoning_effort` above `none` on Chat Completions (all are enabled generator candidates in the registry); reasoning items persist across turns only on Responses; 40-80% better cache utilization. Source: OpenAI migration guide, checked 2026-08-29.

**LANAAGNT-DD-05:** Sequential tool execution (OQ-08, narrows the INFO leaning) [TESTED - full offline suite + live acceptance green with sequential dispatch 2026-08-30]. Rationale: parallel execution adds ordering and interleaved-output complexity for reads only; MVP-1 favors zero race conditions. The AgentEvent stream is order-preserving either way.

**LANAAGNT-DD-06:** Internal AgentEvent stream as the frontend contract (OQ-09, OQ-32). Rationale: the CLI renderer is the only MVP-1 consumer, but the ACP server in MVP-2 subscribes to the same stream - this is the one structural investment made for the future.

**LANAAGNT-DD-07:** Single Summarizer call + deterministic todo extraction instead of Cascade's 3 parallel calls (OQ-12). Rationale: one structured call is cheaper and simpler; the deterministic todo path is the highest-value element and is kept exactly.

**LANAAGNT-DD-08:** Compaction threshold relative to the generator's `max_input` with an absolute cap (OQ-14). Rationale: registry windows span 200K to 1.05M tokens; a fixed 100K wastes large windows; the cap bounds Summarizer cost.

**LANAAGNT-DD-09:** No memory database in MVP-1 (OQ-17 to OQ-20). Rationale: IPPS needs only the "global rules" memory type, which rules injection provides; `create_memory` without retrieval is dead weight; deferring removes storage, retrieval, and injection-timing questions entirely.

**LANAAGNT-DD-10:** 16 tools; dropped from Cascade's 27: deployment tools, browser tools, notebook tools, `read_terminal` (no IDE terminals), `create_memory` (DD-09), `code_search` (needs subagent), MCP meta-tools (no MCP) (OQ-27). (`trajectory_search` moved from dropped to included 2026-08-30 - see DD-21.) Rationale: the IPPS scan (section 2.2) shows every kept tool has demand and every dropped tool has 0 or niche references.

**LANAAGNT-DD-11:** Tool names, descriptions, and schemas verbatim from Cascade (OQ-30). Rationale: IPPS rules and workflows reference exact tool names and embedded behavioral constraints; verbatim copy transfers proven prompt engineering and keeps the prompt system portable between Cascade and Lana.

**LANAAGNT-DD-12:** Single prompt system folder configurable via `agent_folder`, Cascade folder layout (`rules/`, `workflows/`, `skills/`) (OQ-21). Rationale: one agent has one prompt system folder, matching the Cascade architecture; pointing `agent_folder` at any folder with the standard layout requires zero content changes. Relative path resolves against the install root (DD-25); absolute path used as-is.

**LANAAGNT-DD-13:** Agent-side slash command expansion (OQ-22). Rationale: one code path that also serves ACP in MVP-2, where slash commands arrive as plain prompt text.

**LANAAGNT-DD-14:** `skill` tool returns SKILL.md plus a supporting-file listing, not concatenated folder content (OQ-24). Rationale: Cascade-compatible behavior at bounded cost (some DevSystem skills have 160 files); the agent reads supporting files on demand via `read_file`.

**LANAAGNT-DD-15:** Three-level ExecutionPolicy with denylist (OQ-29). Rationale: mirrors Cascade's proven dual-consent model minus the allowlist level (redundant with `auto` for a CLI user who sees every command).

**LANAAGNT-DD-16:** New config file `config/lana-config.json`; existing 4 config files read-only (OQ-40). Rationale: role mapping, thresholds, and safety lists have no home in the existing files; one new file keeps the `config/` folder the single machine-level config location.

**LANAAGNT-DD-17:** Python 3.12+, dependencies: `openai`, `anthropic`, `pydantic`, `rich`, `prompt_toolkit`, `pyyaml` (OQ-43). Rationale: minimal set - SDKs, canonical model validation, terminal rendering, input line editing, frontmatter parsing. No `textual` (full TUI framework is MVP overkill).

**LANAAGNT-DD-18:** Deferred to MVP-2/3 with no MVP-1 implementation: ACP frontend (OQ-32 to OQ-37), MCP client (OQ-25, OQ-36), hooks (OQ-26), mid-session model switching (OQ-06), code_search subagent (OQ-28), proactive summarization (OQ-15). Rationale: user directive - simple but effective, avoid complexity and risk.

**LANAAGNT-DD-19:** Web research tools included in MVP-1 via provider-native web search (revised from MVP-2 deferral per user directive and scan evidence) [PROVEN - live web search TC-43 + Anthropic branch smoke green 2026-08-30]. Rationale: `search_web`/`read_url_content` are the most-referenced non-core tools in IPPS (14 + 17 refs), powering the flagship deep-research skill; OpenAI and Anthropic both offer native web search tools, so the two-backend constraint holds; `read_url_content` is plain HTTP fetching (no LLM backend involved), gated by Cascade-parity user approval.

**LANAAGNT-DD-20:** Black-box CLI testing via three observable interfaces (FR-14): headless prompt injection, per-line-flushed session JSONL as the activity monitor, and the scripted replay adapter for deterministic turns. Rationale: tests exercise the real `lana` executable end-to-end without API cost, nondeterminism, or pseudo-terminal emulation (fragile on Windows); the AgentEvent stream (DD-06) stays the single observability surface for humans, tests, and the future ACP frontend alike.

**LANAAGNT-DD-21:** `trajectory_search` implemented locally over session JSONL files, lexical scoring, no embeddings (resolves deferred candidate D-01; amends the DD-18 deferral). Rationale: the session log is already the event-sourced trajectory (Key Mechanisms); the `/remove` workflow (3 refs) becomes executable; the verbatim Cascade contract (IN02 section 7) is satisfiable without a vector index - semantic ranking quality beyond term overlap is deferred until evidence demands it.

**LANAAGNT-DD-22:** [ASSUMED] Full-recall session log: the `session_started` event records the byte-verbatim system prompt, tool definitions, and config snapshot; `--resume` reuses the recorded prompt instead of reassembling from disk. Rationale: "single source of truth" previously covered only conversation state - a prompt system or config change between exit and resume silently altered the resumed session's instructions, and the JSONL could not answer "what exactly did the Generator receive?". Provider-side state is ephemeral and model-bound: prompt caches expire within minutes and never survive a model or provider change, so persistence must be complete and self-sufficient - the JSONL alone rebuilds the full request for ANY model. Recording the environment costs ~100 KB per session file (one-time, negligible against conversation volume) and extends the IG-01 byte-identity guarantee across same-model resumes (cache hits within provider TTL are a bonus, never a dependency). The on-disk prompt system remains the source for NEW workflow expansions and skill invocations after resume - only already-sent content is immutable.

**LANAAGNT-DD-23:** Zero-setup philosophy: Lana auto-creates everything it needs on first run and reports what it did; there is no `init` command (user directive 2026-08-30: "We want to let the user work, not do setup tasks"). Rationale: a beginner running `lana` in an empty workspace must reach a working prompt without reading setup docs; auto-creation is bounded to artifacts derivable from defaults (data dirs, folder scaffold, default config) - shipped model data files stay required until distribution bundles them.

**LANAAGNT-DD-24:** Severity-prefixed notices over the existing `error` event: messages starting `WARNING:` render yellow, `NOTICE:` render dim (prefix stripped), all others red with `ERROR:` prefix; the AgentEvent enum stays at 11 types. Rationale: retry notices (FR-16) and the pre-compaction line need non-error rendering; a 12th event type would touch the JSONL schema, resume projection, and the ACP translator for a pure presentation concern - the EC-17 `WARNING:` prefix convention already exists, this formalizes it.

**LANAAGNT-DD-25:** Install root separates infrastructure base from workspace (bootstrapping bug 2026-08-31). Rationale: when Lana runs as a packaged binary (`dist/lana.exe`) the CWD is the user's project, not the binary's directory; config, prompt library, and runtime data must resolve relative to the EXE location, not the user's CWD. Resolution hierarchy: `--install-root <path>` CLI flag > env `LANA_INSTALL_ROOT` > workspace (CWD fallback for dev mode). The workspace stays CWD for tool operations (file reading/editing, command execution, git root detection, `<user_information>`). In ACP mode, the install root comes from the CLI flag on the `lana --acp` process; the ACP `session/new` `cwd` param sets only the workspace.

## 7. Implementation Guarantees

**LANAAGNT-IG-01:** The system prompt byte content is identical across all Generator calls within one session (cache prefix stability).

**LANAAGNT-IG-02:** No tool executes without an entry in the session JSONL recording its arguments and result.

**LANAAGNT-IG-03:** A command whose first token matches the denylist (per LANAAGNT-FR-12 matching rules) never executes without interactive approval, regardless of ExecutionPolicy or `SafeToAutoRun`. Scope: the denylist guards against ACCIDENTAL destructive commands; it is not an adversarial-input defense (see LANAAGNT-NFR-05).

**LANAAGNT-IG-04:** The last `todo_list` state survives compaction byte-identically (deterministic extraction, no LLM paraphrase).

**LANAAGNT-IG-05:** Every user-visible failure (missing key, disabled model, malformed frontmatter, API error) produces a self-contained error message naming file/key/model and the corrective action.

**LANAAGNT-IG-06:** Conversation state after `--resume` equals state before process exit (minus any incomplete in-flight turn), reconstructed exclusively from the session JSONL - no dependency on prompt system folder state for previously sent content.

**LANAAGNT-IG-07:** Every byte sent to the Generator - system prompt, tool definitions, conversation messages, checkpoint text - is reconstructible from the session JSONL alone (full recall, LANAAGNT-FR-08).

## 8. Key Mechanisms

- **Cache-stable prompt layout**: fixed assembly order [system prompt | tool definitions | conversation]; all per-turn variability (date, cwd) lives in the user message metadata block, never in the system prompt
- **Verbatim tool contract**: the Cascade tool documentation in `HowWindsurfCascadeWorks.md` chapters 8-9 is the normative source for the 12 tool definitions; Lana-specific deviations are limited to OS/shell substitution in `run_command`
- **Deterministic todo persistence**: compaction scans the event log backwards for the last `todo_list` result and splices its JSON verbatim into the checkpoint (Cascade's proven no-LLM path)
- **Read-gate ledger**: per-session map of file path to last-read modification time backs the edit enforcement gate
- **Event-sourced session**: the JSONL event log is the single source of truth for the entire Generator input - environment (`session_started`: system prompt, tool definitions, config) plus conversation; API request state and the resume feature are both projections of it, with zero dependency on external folder state for recall

## 9. Action Flow

Interactive turn with workflow invocation:

```
User types "/prime"
├─> Slash expander: match workflows/prime.md
│   └─> Build user message: <user_request>/prime</user_request> + <workflows>{full prime.md}</workflows>
├─> Turn loop (repeat until no tool calls or limit 25):
│   ├─> ProviderAdapter: canonical messages -> provider request (cache breakpoints set)
│   ├─> Stream response: text_delta / thinking_delta events -> CLI renderer
│   ├─> For each requested ToolCall (sequential):
│   │   ├─> Safety gate (run_command; file writes outside workspace): ExecutionPolicy + denylist -> approval_required event if needed
│   │   ├─> Execute tool -> tool_call_finished event -> append to JSONL
│   │   └─> Append result to canonical messages
│   └─> turn_finished event: usage + cost line rendered
├─> Compaction check: est_tokens > threshold?
│   └─> Yes: Summarizer call + todo extraction -> checkpoint_created event -> history replaced
└─> Prompt for next input
```

## 10. Data Structures

**LanaConfig (`config/lana-config.json`):**
```json
{
  "roles": {
    "generator":  { "model_id": "claude-sonnet-4-5-20250929", "effort": "medium" },
    "summarizer": { "model_id": "gpt-4.1-mini", "effort": "low" },
    "websearch":  { "model_id": "gpt-4.1-mini", "effort": "low" }
  },
  "agent_folder": ".lana",          // resolved relative to install root (DD-25)
  "data_dir": ".lana-data",            // resolved relative to install root (DD-25)
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

**Session JSONL (one AgentEvent per line):**
```json
{"ts": "2026-08-29 21:05:10", "type": "session_started", "system_prompt": "You are Lana, ...", "tool_definitions": [{"name": "read_file", "description": "...", "schema": {}}], "config_snapshot": {"roles": {"generator": {"model_id": "claude-sonnet-4-5-20250929", "effort": "medium", "provider": "anthropic"}}, "execution_policy": "manual"}, "prompt_system_fingerprint": {"paths": [".lana"], "counts": {"rules": 8, "workflows": 46, "skills": 23}, "content_hash": "sha256:..."}}
{"ts": "2026-08-29 21:05:12", "type": "user_message", "content": "/prime", "expanded_workflow": "prime"}
{"ts": "2026-08-29 21:05:14", "type": "tool_call_requested", "id": "tc_001", "tool": "read_file", "args": {"file_path": "e:/Dev/Lana-V1/!NOTES.md"}}
{"ts": "2026-08-29 21:05:14", "type": "tool_call_finished", "id": "tc_001", "status": "ok", "result": "     1\t# Notes\n...", "result_chars": 1204}
{"ts": "2026-08-29 21:05:18", "type": "turn_finished", "input_tokens": 21050, "output_tokens": 412, "cache_read_tokens": 18200, "cost_usd": 0.0164}
```

**Checkpoint message (first conversation message after compaction):**
```text
The following is a summary of important context from your previous session.
{{ CHECKPOINT 1 }}
# Objective:
{Summarizer section 1}
# Current working TODO list (keep this up to date with todo_list tool):
{last todo_list JSON, verbatim}
Make sure to continue working off of this TODO list
# Session Summary:
{Summarizer section 2}
# Code Interaction Summary:
{Summarizer section 3}
DO NOT ACKNOWLEDGE THIS CHECKPOINT MESSAGE.
```

## 11. User Actions

- **Start**: `lana` (workspace = cwd) | `lana --install-root [path]` (infrastructure base, DD-25) | `lana --resume [session-file]` | `lana --debug` | `lana --policy manual|auto|turbo` | `lana --config [path]`
- **Headless**: `lana -p "<prompt>"` | `--output-format text|jsonl` - single prompt, exit code signals outcome (LANAAGNT-FR-14)
- **Chat**: free text sends a user message; `/name` invokes a workflow
- **Built-ins**: `/help` (workflows + built-ins), `/cost` (session usage), `/exit`
- **Approve command**: y/n/a prompt showing command line + working directory when the safety gate requires it; `a` approves all remaining approval-gated calls in the turn
- **Answer question**: numbered choice prompt when the Generator calls `ask_user_question`
- **Cancel**: Ctrl+C aborts the current turn, returns to input

## 12. Logging Requirements

**Applicable logging types:**
- [x] User-Facing (UF) - `LOGGING-RULES-USER-FACING.md`
- [x] App-Level (AP) - `LOGGING-RULES-APP-LEVEL.md` (only with `--debug`)
- [ ] Script-Level (SC) - N/A in MVP-1 (no selftest scripts specified here; TEST plan will add them)

**User-Facing (UF):**
- Audience: the person chatting with Lana in the terminal
- Goal: always know what Lana is doing - which tool runs, what it costs, when compaction happens
- Key operations: startup load, tool execution, approval gates, turn completion, compaction

**Expected user-facing output for startup and one turn:**
```text
Lana MVP-1 | generator: claude-sonnet-4-5 (medium) | summarizer: gpt-4.1-mini (low)
Keys: Anthropic (Environment variable: ANTHROPIC_API_KEY), OpenAI (Environment variable: OPENAI_API_KEY)
Loading prompt system '.lana'...
  8 rules (7 injected, 1 skipped: empty), 46 workflows, 21 skills.
  OK. Loaded in 0.4 secs.

> /prime
Running workflow 'prime'...
  [tool] read_file '!NOTES.md'...
    OK. 34 lines.
  [tool] run_command 'git log -n 5 --oneline' (policy: manual)
    Approve? [y/n/a] y
    OK. Exit code 0.
  Turn: in=21050 (cache 18200) out=412 | $0.0164 | session $0.0164
```

**App-Level (AP, `--debug` only):**
- Audience: developer debugging provider requests
- Goal: reproduce any API call from the log alone (keys redacted)
- Key operations: request/response JSON per API call, cache token accounting, compaction decisions

## 13. Technical Constraints

- Provider parameter methods (temperature vs reasoning_effort vs thinking) come from `model_id_startswith` matching in `model-registry.json` - Lana never hardcodes per-model parameter logic
- Anthropic multi-turn tool use requires resending prior thinking blocks; the canonical model must store them per turn
- Token projection is usage-anchored (LANAAGNT-FR-07); the chars/4 heuristic covers only the delta since the last provider-reported count, bounding the known 2-4x under-count risk of pure heuristics on JSON-heavy payloads
- No pre-call emergency compaction in MVP-1 - accepted risk: with the 50K-char tool result cap and the 60% threshold, the remaining 40% window headroom absorbs a full turn of capped results (`LANAAGNT-SP01-RV01` RF-03 reconcile decision)
- `run_command` executes via the host shell (pwsh on Windows); working directory always explicit, `cd` never part of the command line (Cascade contract)
- YAML frontmatter parsing must tolerate IPPS variations: key order differs across files, `workspace-rules.md` is near-empty (32 bytes)
- Windows paths and UTF-8 file content are the default test environment; encoding per `core-conventions.md`
- Tool definition authority chain: `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` (live-session verbatim, all 16 tools) > `HowWindsurfCascadeWorks.md` chapters 8-9 (wire-capture, 12 of 16 verbatim) > any memory of tool behavior

## 14. Document History

**[2026-08-31 18:30]**
- Added: DD-25 install root concept - separates infrastructure base (config, agent_folder, data_dir) from workspace (CWD); resolution: --install-root > LANA_INSTALL_ROOT > CWD fallback
- Changed: FR-01 config resolved from install root, FR-02 agent_folder resolved from install root, FR-16 zero-setup relative to install root, DD-12 agent_folder resolution updated, PromptSystem storage updated, LanaConfig comments, User Actions --install-root flag

**[2026-08-31 01:27]**
- Changed: FR-12 approve-all scope from turn-scoped to session-scoped (`a` persists for the entire session, not just the current turn)

**[2026-08-30 23:30]**
- Changed: FR-01 key source format revised to verbose `Provider (Environment variable: VAR)` or `Provider (.\config\.api-keys.txt: VAR)`; added `PROVIDER_DISPLAY` mapping for correct casing (OpenAI, Anthropic); logging example updated

**[2026-08-30 23:15]**
- Changed: FR-12 approval prompt from `[y/n]` to `[y/n/a]` - `a` (all) approves the current and all remaining approval-gated tool calls for the rest of the current turn; updated User Actions (section 11) and logging example (section 12)

**[2026-08-30 16:50]**
- Added: FR-16 zero-setup startup and runtime resilience (auto-creation + reporting, CR/BL/UX hardening per LANAAGNT-IN03), DD-23 zero-setup philosophy, DD-24 severity-prefixed notice rendering

**[2026-08-30 03:40]**
- Changed (verify IMPL/TEST): thinking payloads carried on `turn_finished` (AgentEvent + FR-08) - keeps the enum at 11 types, payloads stay with their turn

**[2026-08-30 03:20]**
- Added: FR-08 full-recall guarantee - `session_started` event (system prompt, tool definitions, config snapshot, prompt system fingerprint), thinking payload recording, resume-from-JSONL-alone semantics with fingerprint warning; IG-07 full-recall guarantee; DD-22 rationale
- Added (verify pass): FR-08 model-change-on-resume semantics (current config wins for model selection, recorded snapshot is audit-only), provider independence bullet (recall never depends on ephemeral provider caches), cross-provider thinking payload drop rule; DD-22 [ASSUMED] label and cache-dependency correction
- Changed: FR-08 title to "Session Persistence - Full Recall", IG-06 strengthened (no folder dependency for recall), FR-03 system prompt recorded in JSONL, AgentEvent enum + Session domain object + Key Mechanisms + JSONL data structure example updated to 11 event types

**[2026-08-30 06:15]**
- Added: `trajectory_search` as 16th tool (FR-10), FR-15 session trajectory search behavior, DD-21 local-JSONL design decision (resolves deferred candidate D-01; 3 refs in `/remove`)
- Changed: DD-10 drop list, FR-03 capability notice, section 2.2 known limitation (/remove now executable), tool counts in Scenario/roadmap/authority chain

**[2026-08-30 04:10]**
- Changed (`/sync` Code→SPEC): FR-07 trigger wording "reach or exceed" + per-tool-loop-turn checking (matches implementation), FR-09 cache-write tokens added, FR-10 image-refusal behavior added, FR-14 headless built-in dispatch added, section 2.1 marked as evolving snapshot (23 skills by 2026-08-30)
- Changed: label promotions from live evidence - DD-04 [VERIFIED]→[PROVEN], DD-05 [ASSUMED]→[TESTED], DD-19 [VERIFIED]→[PROVEN]

**[2026-08-29 22:20]**
- Added: FR-14 headless mode and test interfaces (prompt injection, exit codes, non-interactive approval denial, config override, non-terminal stdin fallback, scripted adapter hook), FR-08 per-line flush guarantee, DD-20 testability design, headless User Actions (gap closure for `/write-test-plan`: automated CLI testing was unspecified)

**[2026-08-29 22:12]**
- Changed: Tool definition authority constraint now names `LANAAGNT-IN02` (live-session verbatim) above the ebook (`/improve` run 2 consequence; backup `_SPEC_LANA_MVP-1_v2.md`)

**[2026-08-29 21:45]**
- Added: Web research tools `search_web`/`read_url_content`/`view_content_chunk` (FR-10 now 15 tools), FR-13 behavior spec, DD-19, `websearch` role, tool demand evidence in section 2.2 (`/improve` run 1: IPPS scan showed 14+17 refs in deep-research/`/research`)
- Changed: MVP-2 roadmap (web tools moved into MVP-1), capability notice list, NFR-01 network exception for approved fetches, DD-10 drop list + evidence-based rationale

**[2026-08-29 21:35]**
- Changed: DD-04 reversed to Responses API [VERIFIED] (RV01 RF-01); FR-12/IG-03 denylist matching semantics, pwsh aliases, wrapper rule (RF-02); FR-07 usage-anchored projection (RF-05)
- Added: tool result cap + auto_continue in FR-04 and LanaConfig (RF-03, RF-09), `<capability_notice>` + section adaptation in FR-03 (RF-04), cancellation state preservation in FR-04 (RF-06), automatic history caching in FR-06 (RF-07), NFR-05 threat model (RF-08), read-ledger self-edit rule in FR-11 (RF-10)
- Source: `_SPEC_LANA_MVP-1_REVIEW.md [LANAAGNT-SP01-RV01]` per `/reconcile` accepted set

**[2026-08-29 21:15]**
- Fixed: NFR-01 contradiction (run_command network calls outside the no-telemetry guarantee), AgentEvent enum missing `user_message` and checkpoint payload note, Action Flow gate scope aligned with FR-12
- Added: FR-07 fail-safes (Summarizer failure, missing todo state), workspace definition in section 2.2, [ASSUMED] labels on deviation decisions DD-04/DD-05
- Changed: FR-06 cache breakpoint wording to provider-defined prefix order

**[2026-08-29 21:08]**
- Fixed: CLI acronym expanded in Goal; FR-07 anchor count aligned with the three-string checkpoint template (verification pass)

**[2026-08-29 21:05]**
- Initial specification created: 12 FRs, 4 NFRs, 18 DDs resolving all LANAAGNT-IN01 P1 questions for MVP-1 scope, IPPS analysis (8 rules, 46 workflows, 21 skills)
