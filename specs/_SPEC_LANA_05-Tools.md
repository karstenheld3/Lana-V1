# SPEC: Lana Tool System

**Doc ID**: LANATOOL-SP01
**Goal**: Specify the tool set, edit enforcement gates, web research tools, and trajectory search for the Lana CLI agent
**Timeline**: Created 2026-08-29, Extracted from _SPEC_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `src/lana/tools/definitions.py` (verbatim tool definitions)
- `src/lana/tools/__init__.py` (registry and dispatch)
- `src/lana/tools/file_tools.py` (read_file, list_dir, grep_search, find_by_name)
- `src/lana/tools/edit_tools.py` (edit, multi_edit, write_to_file + ReadLedger)
- `src/lana/tools/shell_tools.py` (run_command, command_status)
- `src/lana/tools/web_tools.py` (search_web, read_url_content, view_content_chunk)
- `src/lana/tools/trajectory_tools.py` (trajectory_search)
- `src/lana/tools/state_tools.py` (todo_list)
- `src/lana/tools/skill_tool.py` (skill)
- `src/lana/tools/interact_tools.py` (ask_user_question)

**Depends on:**
- `_SPEC_LANA_02-AgentCore.md [LANACORE-SP01]` for tool dispatch (FR-04 turn loop)
- `_SPEC_LANA_01-ProductOverview.md [LANAAGNT-SP01]` for domain objects (ToolDefinition, ToolCall)

**Does not depend on:**
- `_SPEC_LANA_04-Providers.md [LANAPRVD-SP01]` (web tools use the websearch role adapter but don't depend on adapter internals)

## Table of Contents

1. [Functional Requirements](#1-functional-requirements)
2. [Design Decisions](#2-design-decisions)
3. [Document History](#3-document-history)

## 1. Functional Requirements

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
- `read_file` and `list_dir` path-not-found errors include a hint showing the closest existing parent directory and up to 5 similarly-named siblings, guiding the Generator toward the correct path without broad searches (LANALOGS-PR-0002)
- Dropped from Cascade's 27 with rationale recorded in LANAAGNT-DD-10

**LANAAGNT-FR-11: Edit Enforcement Gates**
- `edit`/`multi_edit` fail unless the target file was read via `read_file` in the current session after its last external modification (OQ-31)
- `old_string` uniqueness enforced unless `replace_all`; `old_string == new_string` rejected
- `write_to_file` fails on existing target files
- A successful `edit`/`multi_edit`/`write_to_file` updates the read ledger to the post-edit state; "external modification" = any change not performed by Lana's own tools (RV01 RF-10)

**LANAAGNT-FR-13: Web Research Tools**
- `search_web`: implemented as a side-call by the `websearch` role using the provider-native web search tool (OpenAI: `web_search` on the Responses API; Anthropic: `web_search` server tool) - stays within the two allowed backends; result rendered in Cascade's documented format: 5 results with title, URL, ~300-char summary, plus the trailing read-further prompt
- `read_url_content`: local HTTP/HTTPS GET + HTML-to-text conversion + chunking; returns the first chunk and a `document_id`; NOT an LLM backend call - plain fetching, same as Cascade's own tool
- `view_content_chunk`: returns chunk at `position` for a previously fetched `document_id`
- Approval: `read_url_content` always requires interactive approval before fetching (Cascade parity); `search_web` requires none (provider-mediated, no direct site contact)
- Web tool results count against `tool_result_max_chars` like all tool results

**LANAAGNT-FR-15: Session Trajectory Search**
- `trajectory_search` operates on Lana's own session JSONL files - they ARE the trajectories (deferred candidate D-01 design)
- `ID` resolves against `[workspace]/.lana-data/sessions/`: exact filename, filename without extension, or unique prefix; unknown ID -> error listing available session ids
- Each session event renders as one chunk (type + content excerpt); `Query` terms score chunks by case-insensitive term overlap, results sorted by score descending
- Empty `Query` returns all chunks in chronological order (tool contract: "An empty query will return all trajectory steps")
- Maximum 50 chunks returned (tool contract); results pass through `tool_result_max_chars` like all tool results
- `SearchType` `"user"` -> error (no user-activity index in Lana; the tool contract already forbids it)
- Scoring is lexical term overlap, not embedding-based [ASSUMED - adequate for session-scale text; revisit if relevance quality disappoints]

## 2. Design Decisions

**LANAAGNT-DD-10:** 16 tools; dropped from Cascade's 27: deployment tools, browser tools, notebook tools, `read_terminal` (no IDE terminals), `create_memory` (DD-09), `code_search` (needs subagent), MCP meta-tools (no MCP) (OQ-27). (`trajectory_search` moved from dropped to included 2026-08-30 - see DD-21.) Rationale: the IPPS scan (section 2.2) shows every kept tool has demand and every dropped tool has 0 or niche references.

**LANAAGNT-DD-11:** Tool names, descriptions, and schemas verbatim from Cascade (OQ-30). Rationale: IPPS rules and workflows reference exact tool names and embedded behavioral constraints; verbatim copy transfers proven prompt engineering and keeps the prompt system portable between Cascade and Lana.

**LANAAGNT-DD-14:** `skill` tool returns SKILL.md plus a supporting-file listing, not concatenated folder content (OQ-24). Rationale: Cascade-compatible behavior at bounded cost (some DevSystem skills have 160 files); the agent reads supporting files on demand via `read_file`.

**LANAAGNT-DD-19:** Web research tools included in MVP-1 via provider-native web search (revised from MVP-2 deferral per user directive and scan evidence) [PROVEN - live web search TC-43 + Anthropic branch smoke green 2026-08-30]. Rationale: `search_web`/`read_url_content` are the most-referenced non-core tools in IPPS (14 + 17 refs), powering the flagship deep-research skill; OpenAI and Anthropic both offer native web search tools, so the two-backend constraint holds; `read_url_content` is plain HTTP fetching (no LLM backend involved), gated by Cascade-parity user approval.

**LANAAGNT-DD-21:** `trajectory_search` implemented locally over session JSONL files, lexical scoring, no embeddings (resolves deferred candidate D-01; amends the DD-18 deferral). Rationale: the session log is already the event-sourced trajectory (Key Mechanisms); the `/remove` workflow (3 refs) becomes executable; the verbatim Cascade contract (IN02 section 7) is satisfiable without a vector index - semantic ranking quality beyond term overlap is deferred until evidence demands it.

## 3. Document History

**[2026-09-01 21:45]**
- Extracted from `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]`: FR-10, FR-11, FR-13, FR-15, DD-10, DD-11, DD-14, DD-19, DD-21
- Content is verbatim from source with section renumbering and header block update only
