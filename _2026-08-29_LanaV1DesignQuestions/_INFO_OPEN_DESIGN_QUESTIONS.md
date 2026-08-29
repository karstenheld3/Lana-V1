# INFO: Lana-V1 Open Design Questions

**Doc ID**: LANAAGNT-IN01
**Goal**: Collect all open design questions for adapting the Cascade architecture to a Python-only command-line interface (CLI) agent with Agent Client Protocol (ACP) support and OpenAI/Anthropic backends
**Timeline**: Created 2026-08-29, Updated 0 times

**Depends on:**
- `docs/Windsurf/HowCascadeWorks/HowWindsurfCascadeWorks.md` (Cascade architecture reference, V2.3.15 wire capture)
- `docs/AI-Standards/ACP-AgentClientProtocol_2026-06-12/_INFO_ACP-01_Summary.md [ACP-IN01]` and `_INFO_ACP-04_Architecture.md [ACP-IN04]`
- `config/model-registry.json`, `config/model-parameter-mapping.json`, `config/model-pricing.json`, `config/.api-keys.txt`

## Summary

- Cascade's Brain/Generator interplay is architecturally opaque - the source doc marks it [ASSUMED]; Lana-V1 cannot copy it 1:1 and must decide between a single-model loop and an explicit two-model plan/generate pipeline (OQ-01) [VERIFIED]
- Cascade's Summarizer role uses Gemini 2.5 Flash, which violates the OpenAI/Anthropic-only constraint; a replacement model must be chosen from `config/model-registry.json` (OQ-02) [VERIFIED]
- Cascade is a stateless full-context-resend system; with direct API access, prompt caching (Anthropic `cache_control`, OpenAI automatic) becomes the dominant cost lever - a design dimension absent from the Cascade doc (OQ-13) [VERIFIED]
- ACP v2 draft removes the client fs/terminal surface and session modes; investing in v1-only surfaces is a known risk documented in ACP-IN04 (OQ-33, OQ-34) [VERIFIED]
- Cascade's memory retrieval internals (timing, format, backend) are unknown even in the source doc (Appendix A, OQ#2 there); Lana-V1 must design its own retrieval, it cannot copy one (OQ-17) [VERIFIED]
- Skills, workflows, and slash commands are entirely outside ACP scope - slash command text arrives as plain prompt text and must be expanded agent-side (OQ-22) [VERIFIED]
- Existing `config/` files cover model properties, parameter mapping, and pricing, but contain NO role assignment (which model is Brain/Generator/Summarizer/Memory), NO thresholds, and NO safety lists - a new config surface is required (OQ-40) [VERIFIED]
- 43 open questions total: 20 P1 (block the SPEC), 16 P2 (block implementation details), 7 P3 (deferrable to V1.x) [VERIFIED]

## Table of Contents

1. [Method and Priorities](#1-method-and-priorities)
2. [Multi-Model Pipeline](#2-multi-model-pipeline)
3. [Agent Loop and Turn Lifecycle](#3-agent-loop-and-turn-lifecycle)
4. [Context Management and Compaction](#4-context-management-and-compaction)
5. [Memory System](#5-memory-system)
6. [Extensibility: Rules, Workflows, Skills, MCP](#6-extensibility-rules-workflows-skills-mcp)
7. [Internal Tools](#7-internal-tools)
8. [ACP Integration](#8-acp-integration)
9. [System Prompt Design](#9-system-prompt-design)
10. [Config Folder Integration](#10-config-folder-integration)
11. [Python Implementation](#11-python-implementation)
12. [Next Steps](#12-next-steps)
13. [Sources](#13-sources)
14. [Document History](#14-document-history)

## 1. Method and Priorities

Each question has:
- **Cascade baseline** - what the reference system does (with evidence label from the source doc)
- **Question** - what Lana-V1 must decide
- **Options** - enumerated alternatives
- **Leaning** - recommendation where one is inferable (marked [ASSUMED] when judgment-based)

Priorities:
- **P1** - structural, blocks the architecture SPEC
- **P2** - important, blocks implementation details but not overall structure
- **P3** - deferrable to V1.x without architectural risk

Question IDs `OQ-NN` are document-local and stable for referencing in the follow-up SPEC.

## 2. Multi-Model Pipeline

### OQ-01 (P1): Keep the Brain/Generator split or use a single-model loop?

- **Cascade baseline**: Brain (GPT-4.1) plans actions and selects tools; Generator (Claude Opus 4.6 Thinking) produces visible output. How they interplay is [ASSUMED] in the source doc - "The client sends one request and receives one streaming response - it has no visibility into whether 1 or 2 models processed the request internally" (Ch1 s4). Even the source's Appendix A lists the Brain as "the hidden layer" with 6 unresolved questions.
- **Question**: Is a separate planning model worth it when the mechanism cannot be copied and modern generator models do native tool calling well?
- **Options**:
  1. Single-model loop: one Generator does planning + tool calls + output (Claude Code / Codex CLI style)
  2. Explicit two-step pipeline: Brain call returns a tool plan (JSON), Generator executes it
  3. Router: cheap Brain classifies the request and picks the Generator model + effort level per turn, but does not plan tools
- **Leaning**: Option 1 for V1, with the role abstraction kept in config so Option 3 can be added later without restructuring. Option 2 doubles latency and cost per turn for unproven benefit [ASSUMED].

### OQ-02 (P1): Which models fill the 4 roles?

- **Cascade baseline**: Brain = GPT-4.1, Generator = Claude Opus 4.6 Thinking, Summarizer = Gemini 2.5 Flash + GPT-4.1 Mini, Memory = GPT-5 Nano [PROVEN in source].
- **Question**: Gemini is not allowed. Which enabled models from `config/model-registry.json` map to which role?
- **Options** (from currently `enabled: true` entries):
  - Generator: `claude-opus-4-5-20251101`, `claude-sonnet-4-5-20250929`, `gpt-5.6-*`, `gpt-5.5`, `gpt-5.4`
  - Brain (if kept, OQ-01): `gpt-4.1`, `gpt-5-mini`, `claude-haiku-4-5-20251001`
  - Summarizer: `gpt-4.1-mini`, `gpt-5-mini`, `claude-haiku-4-5-20251001`
  - Memory: `gpt-5-nano`, `gpt-4.1-nano`
- **Leaning**: Make role → model mapping pure configuration (new config file, OQ-40) with per-role fallback chains. Do not hardcode. Default suggestion: Generator = `claude-sonnet-4-5`, Summarizer = `gpt-4.1-mini`, Memory = `gpt-5-nano` [ASSUMED].

### OQ-03 (P1): How to abstract the two provider APIs?

- **Cascade baseline**: N/A - Cascade's platform hides all provider differences server-side.
- **Question**: OpenAI and Anthropic differ in: tool call format, system prompt placement, thinking/reasoning blocks (Anthropic requires resending thinking blocks in multi-turn tool use), token counting, streaming event shapes, `reasoning_effort` vs `thinking` budget (see `config/model-parameter-mapping.json` effort mapping). Where does the abstraction live?
- **Options**:
  1. Own thin adapter layer: internal canonical message/tool-call model + one adapter per provider (official `openai` and `anthropic` Python SDKs underneath)
  2. Third-party abstraction (LiteLLM or similar)
  3. OpenAI-format-everywhere + translation shim for Anthropic
- **Leaning**: Option 1. Two providers is a small enough N that owning the adapter beats a heavyweight dependency; `model-parameter-mapping.json` already defines the per-provider parameter translation [ASSUMED].

### OQ-04 (P2): Which OpenAI API - Chat Completions or Responses?

- **Question**: The Responses API is OpenAI's strategic direction (built-in tool use state, reasoning persistence); Chat Completions is the stable classic. The choice affects the adapter design (OQ-03) and conversation persistence format (OQ-32).
- **Leaning**: Responses API, since reasoning-model support (gpt-5.x effort levels in the registry) is first-class there [ASSUMED].

### OQ-05 (P2): Per-role effort/verbosity defaults?

- **Cascade baseline**: Generator runs with extended thinking; Summarizer has none; Memory budget was 337 tokens [PROVEN in source, Ch3 s3.6].
- **Question**: `config/model-parameter-mapping.json` defines 7 effort levels with per-provider factors. Which default effort per role, and can the user override per invocation (`--reasoning-effort`)?
- **Leaning**: Role defaults in the new Lana config (e.g., Generator = medium, Brain = low, Summarizer = low, Memory = none); CLI flag overrides the Generator only [ASSUMED].

### OQ-06 (P3): Mid-conversation model switching?

- **Cascade baseline**: Model locked per response; switch takes effect on next user message [VERIFIED in source].
- **Question**: Allow `/model` switching between turns? Switching between providers mid-conversation requires re-encoding history (thinking blocks are provider-specific).
- **Leaning**: Allow between turns; drop provider-specific thinking blocks on provider switch [ASSUMED].

## 3. Agent Loop and Turn Lifecycle

### OQ-07 (P1): Turn loop shape and tool-call limit

- **Cascade baseline**: Up to 20 tool calls per prompt, then trajectory stops and requires continue; Auto-Continue setting exists [VERIFIED in source, Ch7].
- **Question**: Copy the N-calls-then-pause safety valve? What is N? Is auto-continue default on or off in a CLI (where the user may walk away)?
- **Leaning**: Configurable limit, default 25, auto-continue off by default in interactive CLI, on under ACP where the client owns cancellation [ASSUMED].

### OQ-08 (P1): Parallel tool execution

- **Cascade baseline**: Model may emit parallel tool calls in one turn; `code_search` is the only tool with a parallelism ban [PROVEN in source].
- **Question**: Execute parallel tool calls concurrently (asyncio) or sequentially? Concurrency helps reads but is dangerous for writes/commands.
- **Options**: 1) all sequential, 2) concurrent with a per-tool `parallel_safe` flag (reads concurrent, writes/commands sequential), 3) fully concurrent.
- **Leaning**: Option 2 [ASSUMED].

### OQ-09 (P1): Internal event model for streaming

- **Question**: The same agent core must feed two frontends: CLI rendering and ACP `session/update` notifications (agent_message_chunk, tool_call, tool_call_update, plan). Should the core emit a canonical internal event stream that both frontends consume?
- **Leaning**: Yes - one async event bus; CLI renderer and ACP server are two subscribers. This is the key structural decision enabling "one codebase, two frontends" (OQ-32) [ASSUMED].

### OQ-10 (P2): Turn persistence granularity

- **Cascade baseline**: Full conversation history resent every call; history is a flat sequence including tool call IDs, args, results, thinking blobs [PROVEN in source, Ch7].
- **Question**: What is the on-disk unit of a turn (needed for ACP `session/load`, OQ-32)? Append-only JSON Lines (JSONL) of canonical events vs provider-native message arrays?
- **Leaning**: Append-only JSONL of the canonical internal model; provider adapters re-encode on load [ASSUMED].

### OQ-11 (P3): Rate limiting and retry policy

- **Cascade baseline**: Platform-side `CheckUserMessageRateLimit` [PROVEN in source]. Lana-V1 has no platform - it hits provider rate limits directly.
- **Question**: Retry policy (429/529 exponential backoff), token bucket per provider, fallback to alternate role model?
- **Leaning**: Standard SDK retries + per-role fallback chain from OQ-02 [ASSUMED].

## 4. Context Management and Compaction

### OQ-12 (P1): Checkpoint architecture - copy the 3-summarizer design?

- **Cascade baseline**: 3 parallel summarizer calls (A: title+objective, B: 9-section summary, C: code interaction history) + deterministic platform extraction of the last todo_list JSON; checkpoint assembled from a fixed template with 3 hardcoded behavioral anchors [PROVEN in source, Ch11].
- **Question**: Copy exactly (3 parallel calls), or collapse into 1 structured call returning all sections as JSON?
- **Options**: 1) 3 parallel calls (redundancy, verbatim-compatible prompts), 2) 1 call with structured output (cheaper, single point of failure), 3) 1 call + separate deterministic todo extraction (keep the no-LLM todo path either way).
- **Leaning**: Option 3. The deterministic todo extraction is the highest-value part of Cascade's design and costs nothing to keep [ASSUMED].

### OQ-13 (P1): Prompt caching strategy

- **Cascade baseline**: None visible - full resend every call, ~91 KB fixed overhead [PROVEN in source].
- **Question**: With direct API access, Anthropic `cache_control` breakpoints and OpenAI automatic prefix caching cut input cost 5-10x on the stable prefix (system prompt + tools + rules). This REQUIRES a stable prefix ordering: system prompt and tool definitions must not vary between calls in a session. Does the design commit to a cache-friendly prompt layout, and where do the cache breakpoints go?
- **Leaning**: Yes, mandatory. Layout: [system prompt incl. rules | tool definitions | conversation]. This also decides OQ-19 (memory injection point must not invalidate the prefix) [ASSUMED].

### OQ-14 (P1): Truncation threshold - fixed or model-relative?

- **Cascade baseline**: Fixed `truncation_threshold_tokens: 100000` regardless of model [PROVEN in source].
- **Question**: Registry models range from 200K (`claude-sonnet-4-5`) to 1.05M (`gpt-5.6`) input tokens. Fixed threshold wastes the large windows; percentage-based (e.g., 60% of `context_window`/`max_input`) adapts automatically but changes behavior when switching models.
- **Leaning**: Percentage of the Generator's `max_input` from `model-registry.json`, capped by an absolute value in Lana config [ASSUMED].

### OQ-15 (P2): Proactive vs reactive summarization

- **Cascade baseline**: Summarizers fire proactively at multiple points (from 231 KB onward) but the checkpoint is applied only when the threshold is crossed; the trigger heuristic is an open question even in the source (Appendix A #4).
- **Question**: Run summarizers in the background ahead of the threshold (lower perceived latency, wasted calls) or on demand when crossing it (simpler, one visible pause)?
- **Leaning**: Reactive for V1 - simpler, and CLI users tolerate a visible "compacting..." step [ASSUMED].

### OQ-16 (P2): What survives a checkpoint, and where is it injected?

- **Cascade baseline**: Checkpoint replaces the memory slot AND truncated history; memories are lost after checkpoint until next conversation (documented limitation, Ch2 s5.3) [PROVEN in source].
- **Question**: Copy the dual-purpose-slot limitation, or give checkpoint and memories independent slots so retrieved memories survive compaction?
- **Leaning**: Independent slots - the shared slot is an artifact of Cascade's protobuf layout, not a design virtue [ASSUMED].

## 5. Memory System

### OQ-17 (P1): Storage backend and scope

- **Cascade baseline**: Structured record store (Id, Title, Content, CorpusNames, Tags, Action, UserTriggered); backend unknown [PROVEN interface / unknown backend in source].
- **Question**: SQLite vs JSON-per-record files? Workspace-scoped (`.lana/memories/` in repo, committable) vs user-global (`~/.lana/`) vs both with CorpusNames-style filtering?
- **Leaning**: SQLite user-global + workspace tag filtering (mirrors CorpusNames); revisit if memories should be git-shareable [ASSUMED].

### OQ-18 (P2): Retrieval mechanism

- **Cascade baseline**: GPT-5 Nano decides relevance server-side; agent has zero control; no read/query tool exists [PROVEN in source]. Retrieval internals unknown (source Appendix A #2).
- **Question**: LLM-based relevance (nano-class model per turn = cost/latency), OpenAI embeddings + vector similarity (extra dependency, but OpenAI-only so allowed), or plain tag/keyword match for V1?
- **Leaning**: V1: tag/keyword match at session start only; V1.x: nano-model reranking. Skip embeddings until proven necessary [ASSUMED].

### OQ-19 (P2): Retrieval timing

- **Question**: Per user message (Cascade's apparent behavior, unconfirmed) vs once at session start? Per-message retrieval invalidates the prompt cache prefix if injected early (interacts with OQ-13).
- **Leaning**: Session start + explicit refresh; inject AFTER the cached prefix [ASSUMED].

### OQ-20 (P3): Automated memories in V1?

- **Cascade baseline**: `CASCADE_ENABLE_AUTOMATED_MEMORIES` enabled; triggers unknown [PROVEN flag / unknown mechanism in source].
- **Question**: Platform-initiated memory writes without user request - include, and with what trigger?
- **Leaning**: Defer to V1.x. V1 keeps only the explicit `create_memory` tool with Cascade's strong prohibition ("DO NOT call unless explicitly requested") [ASSUMED].

## 6. Extensibility: Rules, Workflows, Skills, MCP

### OQ-21 (P1): Config folder convention

- **Cascade baseline**: `.windsurf/{rules,workflows,skills}/` + `.windsurf/mcp.json` + `.windsurf/hooks.json` [PROVEN in source].
- **Question**: `.lana/` (own convention), reuse this workspace's `.devin/` layout, or the emerging cross-agent `.agents/` standard (mentioned in ACP-IN01 as the portability convention)? Also: user-global fallback (`~/.lana/rules/`) in addition to workspace-level?
- **Leaning**: `.lana/` with the same subfolder names as Cascade (rules/, workflows/, skills/) so existing content is copy-compatible; optional user-global layer merged beneath workspace layer [ASSUMED].

### OQ-22 (P1): Workflow (slash command) expansion path

- **Cascade baseline**: Client-side expansion - the IDE injects the full workflow .md into the user message `<workflows>` block [PROVEN in source, Ch4 s6].
- **Question**: In standalone CLI, Lana owns the input line and can expand client-side like Cascade. Under ACP, slash commands arrive as plain prompt text (out of ACP scope per ACP-IN01) - expansion must happen agent-side. Two code paths or one?
- **Leaning**: One agent-side expansion path used by both frontends (detect leading `/name` in the incoming prompt, wrap expanded content in `<workflows>` like Cascade). ACP also supports advertising available commands via `session/update` - use it so ACP clients can offer autocomplete [ASSUMED].

### OQ-23 (P2): Rules injection and truncation policy

- **Cascade baseline**: Each rules file becomes a `<MEMORY[filename]>` block inside `<user_rules>` with highest-precedence preamble; large files truncated at ~4000 chars per block [PROVEN in source, Ch6 s11].
- **Question**: Copy the MEMORY-block format verbatim (prompt-transfer fidelity with existing rule files) or simplify? What per-block and total budget?
- **Leaning**: Copy the format verbatim including the precedence preamble; per-block limit configurable, default 6000 chars [ASSUMED].

### OQ-24 (P2): Skill loading semantics

- **Cascade baseline**: `skill` tool returns SKILL.md content; skill list with descriptions embedded in tool description; supporting files read separately; 3-40 KB per load [PROVEN in source, Ch9 s4].
- **Question**: Return SKILL.md only (agent reads supporting files via read_file) vs concatenate everything? Cache within session to avoid repeat cost?
- **Leaning**: SKILL.md only + in-session dedup warning on repeat loads [ASSUMED].

### OQ-25 (P1): MCP client scope for V1

- **Cascade baseline**: MCP tools injected conditionally with `mcp1_`/`mcp2_` numeric prefixes; ~25-28 KB definition overhead; hard limit 100 total tools [PROVEN in source, Ch10].
- **Question**: V1 scope of the Model Context Protocol (MCP) client: stdio only or also HTTP/Server-Sent Events (SSE)? Tool namespacing: numeric `mcp1_` (Cascade) vs readable `mcp_{server}_{tool}`? Tool count cap? Per-tool enable/disable? Config location (`.lana/mcp.json` vs Lana config file vs ACP-provided, see OQ-36)?
- **Leaning**: V1: stdio only via the official [`mcp` Python SDK](https://github.com/modelcontextprotocol/python-sdk); readable prefixes; cap 100; `.lana/mcp.json` [ASSUMED].

### OQ-26 (P3): Hooks in scope?

- **Cascade baseline**: 12 hook events, pre-hooks can block via exit code 2 [VERIFIED in source from docs].
- **Leaning**: Defer to V1.x; the safety gate (OQ-29) covers the critical pre-command case [ASSUMED].

## 7. Internal Tools

### OQ-27 (P1): V1 tool subset

- **Cascade baseline**: 27 native tools [PROVEN in source, Ch8-9].
- **Question**: Which to implement, drop, or replace in a CLI context?
- **Proposed cut** (to be confirmed):
  - Keep (core, 14): `read_file`, `list_dir`, `grep_search`, `find_by_name`, `edit`, `multi_edit`, `write_to_file`, `run_command`, `command_status`, `todo_list`, `create_memory`, `skill`, `ask_user_question`, `search_web`*
  - Keep-maybe (5): `read_url_content` + `view_content_chunk` (needs own fetcher/chunker), `code_search` (needs subagent, see OQ-28), `trajectory_search`, `list_resources`/`read_resource` (comes with MCP)
  - Drop (8): `browser_preview`, `deploy_web_app`, `read_deployment_config`, `check_deploy_status`, `read_terminal` (no IDE terminals), `edit_notebook`, `read_notebook`, IDE-specific metadata tools
  - *`search_web` requires a search backend - Brave API behind Cascade's. Strictly "OpenAI and Anthropic only" would drop it, unless OpenAI web_search built-in tool counts as OpenAI backend. NEEDS USER DECISION.
- **Leaning**: 14 core + MCP meta-tools; `search_web` via OpenAI's built-in web search tool if the constraint permits [ASSUMED].

### OQ-28 (P2): code_search subagent ("Fast Context")

- **Cascade baseline**: Separate subagent running parallel grep/read over multiple turns; only tool banned from parallel invocation [PROVEN in source].
- **Question**: A subagent = its own mini agent loop with its own model and budget. Include in V1, and with which role model?
- **Leaning**: V1.x. V1 relies on `grep_search` + `find_by_name` + the Generator's own iteration [ASSUMED].

### OQ-29 (P1): Command safety model

- **Cascade baseline**: Dual consent (`SafeToAutoRun` self-classification + user approval), 4 auto-execution levels, platform allowlist (`echo`, `ls`) and denylist (`git`, `rm`, `kill`, ...) [PROVEN in source, Ch1 s4.2/5.3].
- **Question**: Copy all three layers? Where do allow/deny lists live (Lana config)? In ACP mode, does `SafeToAutoRun` map to skipping `session/request_permission`, or does the ACP client always decide (its permission model has allow_always persistence)?
- **Leaning**: Copy all three layers; lists in Lana config. Under ACP: always send `session/request_permission` for unsafe-classified calls, pass safe-classified ones through the client's allow_always mechanism [ASSUMED].

### OQ-30 (P2): Tool naming - copy Cascade's inconsistency or clean up?

- **Cascade baseline**: Mixed `file_path` / `TargetFile` / `DirectoryPath` / `SearchPath` naming, documented as inconsistent [PROVEN in source, Ch8 s5.3].
- **Question**: Verbatim copy maximizes transfer of Cascade-tuned prompts/rules (this workspace's rules reference exact tool names); clean snake_case is better engineering.
- **Leaning**: Verbatim copy of names AND descriptions for kept tools - the behavioral constraints embedded in descriptions are proven prompt engineering; deviations documented per tool [ASSUMED].

### OQ-31 (P2): Edit tool enforcement gates

- **Cascade baseline**: Read-before-edit is a platform runtime check, not just a prompt rule; uniqueness check; no-op rejection [PROVEN in source].
- **Question**: Enforce read-before-edit in Lana's tool runtime (track per-file read state per session)? Include the fuzzy-match fallback (`max_fuzzy_edit_distance_fraction` in Cascade's flags)?
- **Leaning**: Enforce read-before-edit and uniqueness at runtime; no fuzzy fallback in V1 [ASSUMED].

## 8. ACP Integration

### OQ-32 (P1): Process architecture - one binary, two frontends

- **Question**: `lana` (interactive CLI read-eval-print loop, REPL) and `lana --acp` (ACP agent on stdio, spawned by [Zed](https://zed.dev), [JetBrains](https://www.jetbrains.com), or Neovim)? Or separate entry points? The internal event bus (OQ-09) and session store (OQ-10) must serve both.
- **Leaning**: One package, one core, two frontends selected by flag; ACP mode logs to stderr/file only (stdout is the JSON-RPC channel) [ASSUMED].

### OQ-33 (P1): ACP version target and v2 risk posture

- **ACP baseline**: v1 stable; v2 draft removes session modes and the client fs/terminal surface, unifies tool_call updates, restructures capabilities [VERIFIED, ACP-IN01/ACP-IN13].
- **Question**: Implement v1 fully, or v1-minus-the-surfaces-v2-deletes?
- **Leaning**: Target v1 baseline (initialize, session/new, session/prompt, session/update, session/request_permission, session/cancel) + `session/load`. Skip session modes and DO NOT rely on client fs/terminal (OQ-34) - exactly the surfaces v2 removes [ASSUMED].

### OQ-34 (P2): Client capability delegation

- **ACP baseline**: Clients MAY offer `fs/read_text_file`, `fs/write_text_file`, `terminal/*`; agents cannot assume availability; v2 proposes removing them [VERIFIED, ACP-IN04].
- **Question**: When the client advertises fs capabilities, route Lana's file tools through the client (gets unsaved editor buffer contents - the main benefit) or always operate on disk directly?
- **Leaning**: Always local disk in V1 (v2-proof, one code path); revisit if unsaved-buffer access proves necessary [ASSUMED].

### OQ-35 (P2): Mapping internal events to ACP updates

- **Question**: Concrete mapping decisions: `todo_list` state → ACP `plan` updates? Tool categories → ACP's 9 tool kinds (read/edit/delete/move/search/execute/think/fetch/other)? Edit results → diff content (oldText/newText)? Thinking output → agent_message_chunk vs agent_thought_chunk?
- **Leaning**: Yes to all four mappings; they are what makes Lana render natively in Zed/JetBrains [ASSUMED].

### OQ-36 (P2): MCP server config merge under ACP

- **ACP baseline**: Client passes MCP server configs at `session/new` [VERIFIED, ACP-IN06 summary].
- **Question**: Merge client-provided MCP servers with `.lana/mcp.json`? Precedence on name collision? Can the user disable client-provided servers?
- **Leaning**: Union, client wins on collision, Lana config can blocklist [ASSUMED].

### OQ-37 (P3): ACP auth

- **ACP baseline**: Agents advertise auth methods; authenticate/logout flow [VERIFIED, ACP-IN09 summary].
- **Question**: Lana's auth is local API keys (`config/.api-keys.txt`) - advertise no auth methods, or an auth method that validates key presence and reports a useful error?
- **Leaning**: No auth methods; fail `session/prompt` with a clear error when keys are missing [ASSUMED].

## 9. System Prompt Design

### OQ-38 (P1): Section inventory - keep, adapt, drop

- **Cascade baseline**: Identity preamble + 12 XML sections + injected behaviors (~10 KB Windsurf-authored) [PROVEN in source, Ch6].
- **Question**: Per-section decision needed:
  - Keep near-verbatim: `<tool_calling>`, `<making_code_changes>`, `<running_commands>` (safety), `<debugging>`, `<calling_external_apis>`, `<user_rules>` mechanism, `<memory_system>`, `<workflows>`
  - Adapt: identity ("You are Lana..."), `<communication_style>` (CLI rendering, keep citation format?), `<user_information>` (cwd/git instead of workspace URIs)
  - Drop: `<ide_metadata>` (replace with CLI/ACP client metadata?), browser/deployment references
  - Undecided: injected behaviors block (Cascade's 6 post-XML rules) - static config-driven list?
- **Leaning**: Copy the priority chain design (user rules highest, explicit precedence statement); make the injected-behaviors block a configurable list in Lana config [ASSUMED].

### OQ-39 (P3): Feature-flag analog

- **Cascade baseline**: 47 flags controlling models, tool configs, prompt injection, A/B tests [PROVEN in source].
- **Question**: Lana needs no A/B infrastructure, but the useful subset (tool config overrides, section content appends, capability toggles) could be a `flags` section in Lana config.
- **Leaning**: No flag system in V1; plain config keys instead [ASSUMED].

## 10. Config Folder Integration

### OQ-40 (P1): New config surface - what and where

- **Existing** (input constraints): `model-registry.json` (properties/boundaries), `model-parameter-mapping.json` (CLI param → provider param), `model-pricing.json` (costs), `.api-keys.txt` (keys).
- **Missing** (must be created): role → model mapping + fallbacks (OQ-02), per-role effort defaults (OQ-05), truncation threshold (OQ-14), tool-call limit (OQ-07), command allow/deny lists (OQ-29), tool enable/disable, MCP config location, injected behaviors list (OQ-38), memory settings (OQ-17).
- **Question**: One new `config/lana-config.json` next to the existing files, or split (`config/` = models, `.lana/` = agent behavior)? Which existing file conventions does Lana read verbatim vs re-parse?
- **Leaning**: `config/lana-config.json` for machine/user-level settings; `.lana/` for workspace-level extensibility content. Existing 4 files read as-is, never duplicated [ASSUMED].

### OQ-41 (P2): API key loading and precedence

- **Question**: `.api-keys.txt` format must be parsed (format not inspected - contains secrets). Precedence: env vars (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) vs file? Per the workspace rule, default key file location is `[WORKSPACE_FOLDER]/../.tools/.api-keys.txt` - but this project has `config/.api-keys.txt`. Which wins?
- **Leaning**: Precedence: env var > `config/.api-keys.txt`. Never log key material [ASSUMED].

### OQ-42 (P3): Cost tracking

- **Question**: Use `model-pricing.json` to compute and display per-turn/per-session cost in the CLI (Cascade only had opaque server-side telemetry)? Include cache-hit pricing (interacts with OQ-13)?
- **Leaning**: Yes - a differentiator that direct API access makes trivial; show per-turn cost line + session total [ASSUMED].

## 11. Python Implementation

### OQ-43 (P1): Runtime and dependency baseline

- **Question**: Python version floor (3.11+ for asyncio maturity? 3.12+?), core dependencies (`openai`, `anthropic`, `mcp`, CLI/terminal user interface (TUI) framework - `rich`+`prompt_toolkit` vs `textual` vs plain), packaging (`pyproject.toml`, `pip install -e`, entry point `lana`), package layout under `src/`.
- **Leaning**: Python 3.12+, asyncio core, deps: `openai`, `anthropic`, `mcp`, `rich`, `pydantic` (canonical message model), `src/lana/` layout with `core/`, `providers/`, `tools/`, `frontends/{cli,acp}/`, `memory/`, `config/` modules [ASSUMED].

Additional P3 items not numbered separately: test strategy for LLM interactions (record/replay fixtures vs live smoke tests), logging format and location, telemetry (recommendation: none - local logs only, a deliberate privacy improvement over Cascade's full-context telemetry echo documented in the source).

## 12. Next Steps

1. User answers the 20 P1 questions: OQ-01, OQ-02, OQ-03, OQ-07, OQ-08, OQ-09, OQ-12, OQ-13, OQ-14, OQ-17, OQ-21, OQ-22, OQ-25, OQ-27, OQ-29, OQ-32, OQ-33, OQ-38, OQ-40, OQ-43
2. `/write-spec` for the Lana-V1 architecture (`_SPEC_LANA_ARCHITECTURE.md [LANAAGNT-SP01]`) from the decided questions
3. Decide `search_web` backend question (OQ-27 asterisk) - explicit user call on whether OpenAI built-in web search satisfies the "OpenAI and Anthropic only" constraint
4. Optional: `/critique` this document to surface missed question areas

## 13. Sources

**Primary Sources:**
- `LANAAGNT-IN01-SC-CSMP-EBK`: `docs/Windsurf/HowCascadeWorks/HowWindsurfCascadeWorks.md` - Complete Cascade architecture (V2.3.15 wire capture): 4-model pipeline, 47 flags, 27+25 tools, checkpoint mechanism, system prompt, context budget [VERIFIED - read in full, 4810 lines]
- `LANAAGNT-IN01-SC-ACP-SUMRY`: `docs/AI-Standards/ACP-AgentClientProtocol_2026-06-12/_INFO_ACP-01_Summary.md` - ACP v1 scope, v2 draft changes, skills/slash-commands out of protocol scope [VERIFIED]
- `LANAAGNT-IN01-SC-ACP-ARCH`: `docs/AI-Standards/ACP-AgentClientProtocol_2026-06-12/_INFO_ACP-04_Architecture.md` - Three-actor model, baseline methods, client capabilities, v2 fs/terminal removal risk [VERIFIED]
- `LANAAGNT-IN01-SC-CFG-MDLREG`: `config/model-registry.json` v1.7.0 - Enabled models, context windows, provider parameter methods [VERIFIED]
- `LANAAGNT-IN01-SC-CFG-PARMAP`: `config/model-parameter-mapping.json` v2.3.0 - 7 effort levels, per-provider factor mapping [VERIFIED]

**Note on evidence labels inside questions:** [PROVEN in source] / [VERIFIED in source] / [ASSUMED in source] refer to the evidence labels of the Cascade ebook itself; bare [ASSUMED] on Leanings marks this document's own judgment.

## 14. Document History

**[2026-08-29 20:52]**
- Fixed: Stale cross-references (OQ-35 → OQ-40 in OQ-02, OQ-18 → OQ-19 in OQ-13)
- Fixed: Arrow spacing, Timeline format, acronym expansion on first use (ACP, MCP, CLI, JSONL, REPL, TUI, SSE)
- Changed: Source ref EBOOK → EBK; added inline links for Zed, JetBrains, mcp Python SDK

**[2026-08-29 20:46]**
- Initial research document created: 43 open design questions in 10 areas, priorities P1-P3, leanings for each

