# IMPL: Lana MVP-1 - CLI Agent Running IPPS

**Doc ID**: LANAAGNT-IP01
**Feature**: lana-mvp-1
**Goal**: Implement the Lana MVP-1 command-line interface (CLI) agent per LANAAGNT-SP01 (rev 2026-08-30 03:40) in 10 verifiable phases
**Timeline**: Created 2026-08-29, Updated 0 times

**Target file(s)**:
- `pyproject.toml` (NEW)
- `README.md` (NEW)
- `config/lana-config.json` (NEW)
- `src/lana/` - 22 new Python modules (NEW, see File Structure)
- `tests/` - test package mirroring `src/lana/` (NEW)

**Depends on:**
- `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` for all requirements (FR-01 to FR-15, NFR-01 to NFR-05, DD-01 to DD-22, IG-01 to IG-07)
- `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` for verbatim tool definitions (primary transcription source; the ebook chapters 8-9 lack full text for `multi_edit`, `command_status`, `skill`)
- `HowWindsurfCascadeWorks.md` chapters 8-9 as cross-check for the 12 tools it covers verbatim
- `config/model-registry.json`, `config/model-parameter-mapping.json`, `config/model-pricing.json` (read-only inputs)

## MUST-NOT-FORGET

- Tool names, descriptions, parameter names, JSON Schemas verbatim from `LANAAGNT-IN02` (LANAAGNT-DD-11) - transcribe, never paraphrase; description blocks there are [LITERAL]
- System prompt byte-identical across a session (LANAAGNT-IG-01) - no timestamps, no cwd, no variable content in it
- Every AgentEvent appended to the JSON Lines (JSONL) session file at occurrence, user events before the turn starts (LANAAGNT-IG-02)
- Denylist checks the FIRST token after alias normalization; wrappers are never parsed, always approved (LANAAGNT-FR-12)
- Deterministic todo extraction - never let the Summarizer touch todo state (LANAAGNT-IG-04)
- OpenAI = Responses API only (LANAAGNT-DD-04); Anthropic = Messages + cache_control + top-level automatic caching (LANAAGNT-FR-06)
- Existing `config/*.json` files are read-only inputs - never write to them
- IMPL-CODEBASE mode: output goes to `src/`, `tests/`, `config/`, workspace root (`pyproject.toml`, `README.md`)
- Small cycles: implement -> test -> green -> commit per phase; never proceed on red

## Impact Analysis

- **Greenfield**: `src/` is empty; no existing code paths, callers, or tests are affected
- **Shared file surface**: `config/` gains one NEW file (`lana-config.json`); the 4 existing config files are opened read-only - zero modification risk
- **Workspace root**: gains `pyproject.toml`, `README.md`, `tests/`; no collision with existing files (verified: none exist)
- **External surface**: IPPS folder is read-only input at runtime; never written
- **Regression checkpoints**: each phase ends with its offline test group green (LANAAGNT-IP01-TC groups); phases A-C and E-G run without API keys, isolating provider risk to phases D and H

## Table of Contents

1. [File Structure](#1-file-structure)
2. [Edge Cases](#2-edge-cases)
3. [Implementation Steps](#3-implementation-steps)
4. [Logging Preview](#4-logging-preview)
5. [Test Cases](#5-test-cases)
6. [Verification Checklist](#6-verification-checklist)
7. [Document History](#7-document-history)

## 1. File Structure

```
e:\Dev\Lana-V1\
├── pyproject.toml                    # Package metadata, deps, entry point 'lana' (~40 lines) [NEW]
├── README.md                         # Install + quickstart (~60 lines) [NEW]
├── config/
│   └── lana-config.json              # LanaConfig per SPEC section 10 (~20 lines) [NEW]
├── src/lana/
│   ├── __init__.py                   # Version constant (~5 lines) [NEW]
│   ├── __main__.py                   # python -m lana -> cli.main() (~5 lines) [NEW]
│   ├── cli.py                        # Arg parsing, startup sequence, read-eval-print loop (REPL) (~200 lines) [NEW]
│   ├── config.py                     # LanaConfig + registry/mapping/pricing/keys loading, validation (~220 lines) [NEW]
│   ├── models.py                     # Canonical types: Message, ToolCall, ToolResult, ThinkingBlock, Usage (pydantic) (~120 lines) [NEW]
│   ├── events.py                     # AgentEvent union (11 types per SPEC incl. session_started), serialization (~130 lines) [NEW]
│   ├── session.py                    # JSONL append store, resume projection, cancellation note (~180 lines) [NEW]
│   ├── loader.py                     # PromptSystem loading: rules/workflows/skills, frontmatter, precedence (~180 lines) [NEW]
│   ├── prompt.py                     # System prompt assembly: sections, MEMORY blocks, capability notice (~200 lines) [NEW]
│   ├── agent.py                      # Turn loop, tool dispatch, limits, cancellation, compaction trigger (~280 lines) [NEW]
│   ├── compaction.py                 # Usage-anchored projection, Summarizer call, todo extraction, checkpoint (~180 lines) [NEW]
│   ├── safety.py                     # ExecutionPolicy, denylist matcher, alias normalization, wrapper detection (~120 lines) [NEW]
│   ├── cost.py                       # Pricing lookup, per-turn line, session totals per role (~100 lines) [NEW]
│   ├── render.py                     # rich renderer: event subscriber, approval prompts, question prompts (~220 lines) [NEW]
│   ├── providers/
│   │   ├── __init__.py               # get_adapter(model) via registry provider field (~20 lines) [NEW]
│   │   ├── base.py                   # ProviderAdapter protocol: stream_turn(), count hints (~60 lines) [NEW]
│   │   # (synced 2026-08-30: providers/ also holds scripted_adapter.py - the installed executable loads it via LANA_SCRIPTED_ADAPTER; tests/scripted_adapter.py re-exports + script helpers)
│   │   ├── openai_adapter.py         # Responses API: items, reasoning passthrough, web_search side-call (~260 lines) [NEW]
│   │   └── anthropic_adapter.py      # Messages API: thinking blocks, cache_control, automatic caching, web_search (~260 lines) [NEW]
│   └── tools/
│       ├── __init__.py               # Registry: name -> (definition, executor); dispatch (~60 lines) [NEW]
│       ├── definitions.py            # 15 verbatim Cascade tool definitions (name, description, JSON Schema) (~500 lines) [NEW]
│       ├── file_tools.py             # read_file, list_dir, grep_search, find_by_name (~260 lines) [NEW]
│       ├── edit_tools.py             # edit, multi_edit, write_to_file + ReadLedger (~240 lines) [NEW]
│       ├── shell_tools.py            # run_command, command_status; background process table (~200 lines) [NEW]
│       ├── web_tools.py              # search_web (websearch role side-call), read_url_content, view_content_chunk (~220 lines) [NEW]
│       ├── trajectory_tools.py       # trajectory_search over .lana-data/sessions JSONL (lexical scoring, 50-chunk cap) (~80 lines) [NEW 2026-08-30]
│       ├── state_tools.py            # todo_list (full-replace, event emission) (~60 lines) [NEW]
│       ├── skill_tool.py             # skill: SKILL.md + supporting file listing (~60 lines) [NEW]
│       └── interact_tools.py         # ask_user_question (blocks on frontend response) (~60 lines) [NEW]
└── tests/
    ├── conftest.py                   # Fixtures: tmp workspace, fake prompt system, scripted adapter wiring (~120 lines) [NEW]
    ├── scripted_adapter.py           # Deterministic replay adapter for LANA_SCRIPTED_ADAPTER (FR-14) (~120 lines) [NEW]
    ├── harness.py                    # LanaProc: spawn real CLI, inject prompts, parse stdout JSONL, tail session file (~160 lines) [NEW]
    ├── test_config.py … test_e2e_offline.py   # One test module per phase group (~14 files) [NEW]
```

Estimated total: ~3,900 lines source + ~1,800 lines tests [ASSUMED - per-module estimates, +-30%].

## 2. Edge Cases

**Input boundaries:**
- **LANAAGNT-IP01-EC-01**: Rules file is empty or whitespace (`workspace-rules.md`, 32 bytes) -> inject empty MEMORY block (Cascade parity), count as "skipped: empty" in startup report
- **LANAAGNT-IP01-EC-02**: Frontmatter missing or malformed YAML -> treat file as body-only, `trigger` defaults to always-on, log warning with filename
- **LANAAGNT-IP01-EC-03**: Rule body exceeds `rule_block_max_chars` -> truncate at limit, append `<truncated N chars>` marker
- **LANAAGNT-IP01-EC-04**: Tool result exceeds `tool_result_max_chars` -> tail-truncate, append `<truncated N chars>` marker (LANAAGNT-FR-04)
- **LANAAGNT-IP01-EC-05**: Unknown `/name` input -> list up to 3 closest workflow names (prefix + edit distance), do not call the Generator
- **LANAAGNT-IP01-EC-06**: Workflow filename collides with built-in (`help.md`, `cost.md`, `exit.md`) -> built-in wins, warn once at startup

**State transitions:**
- **LANAAGNT-IP01-EC-07**: `edit` without prior `read_file` in session -> tool error naming the gate and the required action (LANAAGNT-FR-11)
- **LANAAGNT-IP01-EC-08**: File modified externally after last read (mtime newer than ledger) -> gate blocks with "re-read required"
- **LANAAGNT-IP01-EC-09**: `old_string` not unique and `replace_all` false -> error with occurrence count
- **LANAAGNT-IP01-EC-10**: Ctrl+C during tool loop -> completed ToolCalls kept, synthetic cancellation note appended, REPL prompt returns (LANAAGNT-FR-04)
- **LANAAGNT-IP01-EC-11**: `max_tool_calls_per_prompt` reached -> pause with continue prompt; `auto_continue: true` skips the pause
- **LANAAGNT-IP01-EC-12**: Compaction fires with zero `todo_list` events -> checkpoint omits the todo section (LANAAGNT-FR-07)
- **LANAAGNT-IP01-EC-13**: Two Lana instances, same workspace -> distinct session files (timestamp+id in name); no lock needed; ReadLedger divergence caught by EC-08 mtime check

**External failures:**
- **LANAAGNT-IP01-EC-14**: Configured model missing or `enabled: false` in registry -> startup error naming model_id, role, and the registry file
- **LANAAGNT-IP01-EC-15**: API key missing for a configured provider -> startup error naming env var and key file path
- **LANAAGNT-IP01-EC-16**: Provider API error (429/5xx) -> SDK default retries; final failure surfaces as `error` event with provider message, turn discarded like cancellation
- **LANAAGNT-IP01-EC-17**: Summarizer call fails during compaction -> no truncation, warning, session continues (LANAAGNT-FR-07)
- **LANAAGNT-IP01-EC-18**: `read_url_content` network error, non-HTML content, or >5 MB body -> tool error with URL and reason; binary content refused
- **LANAAGNT-IP01-EC-19**: `search_web` role model's provider tool unavailable -> tool error advising a different `websearch` model
- **LANAAGNT-IP01-EC-20**: Context overflow despite projection (provider 400 "too long") -> error event advising model switch or new session; no auto-retry with same payload

**Data anomalies:**
- **LANAAGNT-IP01-EC-21**: JSONL last line truncated (crash mid-write) -> skip invalid line on resume, log count of skipped lines
- **LANAAGNT-IP01-EC-22**: Generator emits unknown tool name -> tool error listing available tools (no crash)
- **LANAAGNT-IP01-EC-23**: Generator emits invalid JSON args -> tool error with schema validation message
- **LANAAGNT-IP01-EC-24**: Model absent from `model-pricing.json` -> cost rendered as `?`, tokens still shown (LANAAGNT-FR-09)
- **LANAAGNT-IP01-EC-25**: `view_content_chunk` with unknown `document_id` or out-of-range position -> error naming valid range
- **LANAAGNT-IP01-EC-26**: `read_file` on an image file -> refused with explanatory error (no visual presentation in a CLI); SVG stays readable as text (synced from implementation 2026-08-30)
- **LANAAGNT-IP01-EC-27**: `trajectory_search` with unknown `ID`, ambiguous prefix, `SearchType: "user"`, or no sessions folder -> error naming available session ids / the contract violation (FR-15)
- **LANAAGNT-IP01-EC-28**: `--resume` on a legacy session file without `session_started` (pre-FR-08 full recall) -> fall back to disk prompt assembly, warn "legacy session file - recorded environment unavailable, system prompt assembled from current prompt system"
- **LANAAGNT-IP01-EC-29**: `--resume` with a generator provider differing from a recorded thinking payload's provider -> payload dropped from the adapter resend (signatures are provider-bound, SPEC FR-08); rendered thinking text stays in the log

## 3. Implementation Steps

Phases A-J. Each phase ends green on its test group before the next starts. Phases A-C, E-G, I-J run offline (fake adapters); only D and H need API keys.

```
OFFLINE (fake adapters, no keys)                LIVE (API keys required)
A skeleton+config ─> B loader+prompt ─> C tools ─┬─> D provider adapters
                                                 │
E loop+session+CLI <─────────────────────────────┘   (E uses fake adapters,
│                                                      D only unblocks smoke tests)
├─> F cost ─> G compaction ──────────────────────┬─> H web tools (live)
│                                                │
I hardening (offline NFR fixtures) <─────────────┘
└─> J acceptance (offline e2e + live manual run)
```

### Phase A: Package Skeleton and Configuration

### LANAAGNT-IP01-IS-01: Create package skeleton

**Location**: workspace root, `src/lana/`

**Action**: Add `pyproject.toml` (name `lana`, Python >=3.12, deps: `openai`, `anthropic`, `pydantic>=2`, `rich`, `prompt_toolkit`, `pyyaml`; entry point `lana = lana.cli:main`; `pytest` dev dep), `README.md`, `src/lana/__init__.py`, `__main__.py`, empty module files

**Note**: `pip install -e .` must succeed and `lana --help` must print before any feature work

### LANAAGNT-IP01-IS-02: Canonical models and events

**Location**: `models.py`, `events.py`

**Action**: Add pydantic types:
```python
# models.py - provider-neutral conversation model
class ToolCall: id, name, args_json, status          # status: pending|ok|error|cancelled
class ThinkingBlock: provider, payload               # opaque, resent per provider rules
class Message: role, content, tool_calls, thinking, usage
# events.py - the 11 AgentEvent types from SPEC Domain Objects, each with ts + to_jsonl()/from_jsonl()
```

**Note**: `checkpoint_created` carries full checkpoint text (resume replay); `user_message` carries `expanded_workflow` name when applicable; `session_started` carries the full-recall environment (FR-08, see IS-24)

### LANAAGNT-IP01-IS-03: Configuration loading (LANAAGNT-FR-01)

**Location**: `config.py`

**Action**: Add `load_lana_config(workspace)`:
```python
def load_lana_config(workspace) -> LanaConfig: ...
# 1. Parse config/lana-config.json (pydantic schema per SPEC section 10)
# 2. Resolve each role model against model-registry.json: exists + enabled, else ConfigError
# 3. Resolve provider params via model_id_startswith method + effort_mapping factors
# 4. Keys: env var first (OPENAI_API_KEY / ANTHROPIC_API_KEY), then config/.api-keys.txt; track source per provider ("env" or ".api-keys.txt") in key_sources dict
# 5. Load model-pricing.json into cost table (missing model tolerated, EC-24)
# 6. Boot banner prints "Keys: provider (source), ..." line so user knows where keys come from (FR-01)
```

**Note**: ALL validation at startup (IG-05); ConfigError messages name file, key, and corrective action. Never log key material

### Phase B: Prompt System Loading and System Prompt

### LANAAGNT-IP01-IS-04: PromptSystem loader (LANAAGNT-FR-02)

**Location**: `loader.py`

**Action**: Add `load_prompt_systems(paths) -> PromptSystem`:
```python
# Per path: rules/*.md, workflows/*.md, skills/*/SKILL.md
# Frontmatter: yaml between leading '---' fences; tolerate absence (EC-02)
# Rules: keep trigger always_on or missing; record skipped count
# Later paths override earlier on same filename (SPEC precedence)
# Skills: record supporting file relative paths (recursive, excluding SKILL.md)
```

**Note**: Must load IPPS (8 rules / 46 workflows / 21 skills) in < 2 s (NFR-03); read files lazily where possible - workflow bodies are needed only on invocation

### LANAAGNT-IP01-IS-05: System prompt assembly (LANAAGNT-FR-03)

**Location**: `prompt.py`

**Action**: Add `build_system_prompt(prompt_system, workspace_info) -> str` with the fixed section order from FR-03. Adapted Cascade section texts stored as module constants; every dropped-tool reference removed; `<capability_notice>` generated from the constant unavailable-tool list with fallbacks

**Note**: NO datetime, NO cwd inside the system prompt (IG-01) - per-turn variability goes into the user message metadata block assembled in `agent.py`. Unit test asserts two consecutive builds are byte-identical

### Phase C: Tools (offline set)

### LANAAGNT-IP01-IS-06: Tool definitions and registry

**Location**: `tools/definitions.py`, `tools/__init__.py`

**Action**: Transcribe the 15 tool definitions verbatim from `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` (12 native + 3 web). Substitution points: `{OS}`/`{SHELL}` in `run_command`, `{SKILL_LIST}` in `skill` (per IN02 section 1). Registry maps name -> (definition, executor, needs_approval_fn)

**Note**: This is transcription work, not authoring - diff-check each description against IN02 (zero differences outside substitution points = IN02 acceptance rule); cross-check the 12 ebook-covered tools against chapters 8-9. Serialize schemas deterministically (sorted keys) for cache stability

### LANAAGNT-IP01-IS-07: File reading tools

**Location**: `tools/file_tools.py`

**Action**: Add executors: `read_file` (cat -n format, 1-indexed, offset/limit, 2000-char line truncation), `list_dir` (sizes, recursive item counts), `grep_search` (regex/fixed, includes, case flag, MatchPerLine; pure-Python line scan - no external rg dependency), `find_by_name` (glob, excludes, type, depth, 50-result cap)

**Note**: All results pass through the shared `cap_result()` (EC-04). `read_file` success updates the ReadLedger; image files refused with explanatory error (EC-26). Pure-Python grep instead of bundling ripgrep [TESTED - full suite + real-system scans green 2026-08-30]. grep_search/find_by_name skip a fixed IGNORED_DIRECTORIES set (.git, node_modules, __pycache__, .lana, .lana-data, ...) as a gitignore approximation - the tool descriptions promise rg/fd ignore semantics (synced 2026-08-30)

### LANAAGNT-IP01-IS-08: Edit tools with ReadLedger (LANAAGNT-FR-11)

**Location**: `tools/edit_tools.py`

**Action**: Add `ReadLedger` (path -> mtime at last read/edit by Lana) and executors: `edit` (uniqueness, no-op rejection, gate per EC-07/08), `multi_edit` (atomic: apply all in memory, write once), `write_to_file` (fail on existing, create parents)

**Note**: Successful edits update the ledger to post-edit mtime (RF-10 rule). Out-of-workspace writes route through the approval gate (FR-12)

### LANAAGNT-IP01-IS-09: Shell tools and safety gate (LANAAGNT-FR-12)

**Location**: `tools/shell_tools.py`, `safety.py`

**Action**: `safety.py`: `classify(command, policy, config) -> RUN | ASK`:
```python
# 1. first_token = first whitespace-delimited token, strip path/quotes, casefold
# 2. wrapper? (pwsh|powershell|cmd|bash + -Command|-c|/c present) -> ASK in auto/turbo
# 3. denylist: single-token entries match first_token; multi-token entries prefix-match full line
# 4. policy: manual -> always ASK; auto -> ASK unless SafeToAutoRun and no match; turbo -> RUN unless match
```
`shell_tools.py`: `run_command` via `subprocess.Popen(["pwsh","-NoProfile","-Command",cmd], cwd=...)` with Blocking/WaitMsBeforeAsync semantics; background process table for `command_status` (OutputCharacterCount, WaitDurationSeconds)

**Note**: Approval renders exact command + cwd (render.py); IG-03 test: `Remove-Item` and `pwsh -Command "Remove-Item x"` both stop in auto policy

### LANAAGNT-IP01-IS-10: State, skill, interaction tools

**Location**: `tools/state_tools.py`, `tools/skill_tool.py`, `tools/interact_tools.py`

**Action**: `todo_list` (validate items, store last state on Session, emit result in Cascade's "Todo list updated:" + JSON format - the deterministic extraction anchor), `skill` (SKILL.md body + "Base Directory" header + supporting file list), `ask_user_question` (emits `approval_required`-style blocking event; frontend supplies answer)

**Note**: The exact `todo_list` result format is load-bearing for compaction (IG-04) - test asserts byte-stable rendering

### Phase D: Provider Adapters

### LANAAGNT-IP01-IS-11: Adapter protocol and OpenAI Responses adapter

**Location**: `providers/base.py`, `providers/openai_adapter.py`

**Action**: `base.py`: `stream_turn(system, tools, messages, role_params) -> AsyncIterator[AdapterDelta]` (text/thinking/tool_call/usage deltas) + `supports_web_search()`. OpenAI: canonical messages -> Responses `input` items; function tools; `reasoning_effort`/`temperature` per registry method; reasoning items stored as ThinkingBlock and resent next call; parse typed `output` array (message | reasoning | function_call)

**Note**: Never read only the first output item (typed array parsing per migration guide); `store: false`

### LANAAGNT-IP01-IS-12: Anthropic Messages adapter with caching

**Location**: `providers/anthropic_adapter.py`

**Action**: Canonical -> Messages: `tools` array with `cache_control` on last tool, `system` block with `cache_control`, top-level automatic caching for history (FR-06); `thinking` budget from effort mapping; thinking blocks resent in tool-use turns; usage fields captured incl. `cache_read_input_tokens`

**Note**: Deterministic tool serialization (IS-06) is a cache-hit precondition; smoke test asserts `cache_read_input_tokens > 0` on call 2 (NFR-03)

### Phase E: Agent Loop, Events, CLI

### LANAAGNT-IP01-IS-13: Turn loop (LANAAGNT-FR-04)

**Location**: `agent.py`

**Action**: `run_prompt(user_input)`: expand slash command (FR-05, via loader), build user message with metadata block (date, cwd - HERE, not in system prompt), then loop: adapter stream -> events -> execute tool calls sequentially through registry + safety -> append results -> repeat. Enforce call limit + auto_continue (EC-11), tool result cap (EC-04), Ctrl+C handling (EC-10), unknown tool / bad args (EC-22/23)

**Note**: The loop is a pure async generator over AgentEvents - frontends only consume events (DD-06)

### LANAAGNT-IP01-IS-14: Session store and resume (LANAAGNT-FR-08)

**Location**: `session.py`

**Action**: Append-only JSONL writer (`user_message` flushed synchronously, every line flushed at write per FR-08 - the external tail contract); `resume(path)` projects events -> canonical messages: replay user/assistant/tool events, apply last `checkpoint_created` (truncate prior history, splice checkpoint text; the event carries `kept_messages` so the retained tail reprojects exactly - synced 2026-08-30), skip corrupt lines with count (EC-21), inject cancellation notes for turns ending in cancellation; resume also restores usage/cost/turn totals per role for CostTracker seeding (BG-0002)

### LANAAGNT-IP01-IS-15: CLI frontend and renderer

**Location**: `cli.py`, `render.py`

**Action**: `cli.py`: args (`--resume`, `--debug`, `--policy`), startup sequence (config -> prompt system -> banner + auto/turbo risk notice per NFR-05), REPL via prompt_toolkit, built-ins `/help` `/cost` `/exit`. `render.py`: subscribes to events; streams text; tool lines + approval y/n/a prompts (FR-12: `a` sets an approve-all flag for the rest of the turn, resetting on next user prompt) + numbered `ask_user_question` prompts per SPEC section 12 format; per-turn cost line via `cost.py`

**Note**: `--debug` writes redacted request/response JSON to `.lana-data/logs/` (NFR-04). Renderer constraint (BG-0004, synced 2026-08-30): event payload text (model output, tool results, provider messages) is UNTRUSTED and never enters rich markup parsing - markup=False on all payload prints, styling via style= parameters only

### Phase F: Cost Tracking

### LANAAGNT-IP01-IS-16: Cost engine (LANAAGNT-FR-09)

**Location**: `cost.py`

**Action**: Per-turn cost from usage x pricing (input/output/cache-read/cache-write rates); accumulate per role; `/cost` summary; unknown model -> `?` (EC-24). Usage normalization contract: adapters report input_tokens INCLUDING cache reads (Anthropic normalized up, OpenAI native) (synced 2026-08-30)

### Phase G: Compaction

### LANAAGNT-IP01-IS-17: Usage-anchored projection and checkpoint (LANAAGNT-FR-07)

**Location**: `compaction.py`

**Action**:
```python
def projected_tokens(anchor_tokens, chars_since_anchor): ...   # anchor + chars/4 delta
def extract_last_todo(events): ...                             # deterministic, byte-verbatim
def build_checkpoint(summary_sections, todo_json): ...         # SPEC section 10 template, 3 anchors
def compact(session, summarizer_adapter): ...                  # one call, 3 labeled sections; failure -> warn + no-op (EC-17)
```

**Note**: Threshold = `min(fraction x generator max_input, max_tokens)`, fires at >= (TC-36 boundary); checked after EVERY turn in `agent.py` including between tool-loop turns (drift item 02). Truncation keeps the last 6 messages; leading orphan tool-result messages are trimmed from the tail so no tool_result survives without its tool_use partner (provider 400 guard) (synced 2026-08-30)

### Phase H: Web Tools

### LANAAGNT-IP01-IS-18: Web research tools (LANAAGNT-FR-13)

**Location**: `tools/web_tools.py`

**Action**: `search_web`: one-shot side-call via `websearch` role adapter with the provider-native web search tool; render Cascade's 5-result format. `read_url_content`: approval gate -> `urllib`/`httpx` GET (5 MB cap, text/HTML only, EC-18) -> HTML-to-text -> chunk (~5K chars) -> store per `document_id`. `view_content_chunk`: chunk lookup (EC-25)

**Note**: Chunk store is session-scoped in-memory + persisted as `.lana-data/chunks/<document_id>.json` files - view_content_chunk survives --resume by lazy disk load (implementation replaced the JSONL-mirroring idea; same guarantee, simpler - synced 2026-08-30). Chunk size ~5K chars [ASSUMED - matches Cascade's observed 2-8 KB chunk cost range]

### LANAAGNT-IP01-IS-23: Session trajectory search tool (LANAAGNT-FR-15, added 2026-08-30)

**Location**: `tools/trajectory_tools.py`, `tools/definitions.py`, `prompt.py`, `cli.py`

**Action**: Transcribe the `trajectory_search` definition verbatim from IN02 section 7 (hand-transcription guarded by the diff test). Executor: resolve `ID` against `[workspace]/.lana-data/sessions/` (exact name, stem, or unique prefix); render each event line as one chunk `[NNN] type: excerpt`; score by case-insensitive query-term overlap, sort descending (stable by position); empty query -> chronological; cap 50 chunks; `SearchType: "user"` -> error. Register executor; REMOVE trajectory_search from the `prompt.py` capability notice

**Note**: Lexical scoring only (DD-21); the current session's own file is searchable too (it is flushed per line, FR-08)

### LANAAGNT-IP01-IS-24: Full-recall session log (LANAAGNT-FR-08, DD-22, IG-07; added 2026-08-30)

**Location**: `events.py`, `session.py`, `cli.py`, `agent.py`, `providers/scripted_adapter.py`

**Action**:
```python
# events.py: SessionStarted event - system_prompt (byte-verbatim), tool_definitions (verbatim array),
#            config_snapshot (role -> model_id/effort/provider, policy, thresholds, limits),
#            prompt_system_fingerprint (paths, per-folder counts, sha256 content hash)
# events.py: TurnFinished gains optional thinking_payloads: [{provider, payload}] - the turn's
#            resendable ThinkingBlocks (Anthropic signature blocks, OpenAI reasoning items); enum stays at 11
# cli.py:   new session -> session_started written as the FIRST line before any user event
# session.py resume: read session_started -> recorded system prompt + tool definitions REPLACE disk assembly
#            for Generator calls; projector rebuilds Message.thinking from turn_finished.thinking_payloads
# session.py resume: fingerprint compare vs freshly loaded prompt system -> one-line WARNING on mismatch
# cli.py resume: recorded vs current generator model differ -> one-line report (model change, FR-08)
# agent.py:  drop resurrected thinking payloads whose provider != resumed generator provider (EC-29)
# scripted_adapter.py: LANA_SCRIPTED_CAPTURE=<path> dumps each received (system, tools) to a JSONL file -
#            the TC-65/TP01-TC-11 byte-identity oracle for what the Generator actually received
```

**Note**: Fingerprint hash over sorted (path, content) pairs - deterministic across machines [ASSUMED - mtime excluded to survive copies/checkouts]. Legacy files without `session_started` follow EC-28. The recorded tool definitions are the resume authority - a tool added after recording is absent from resumed Generator calls until a new session (IG-01 byte-identity extends to the tool block)

### Phase I: Hardening

### LANAAGNT-IP01-IS-19: NFR verification fixtures

**Location**: `tests/`

**Action**: Startup timing test against real IPPS path (skipped when absent); kill-and-resume test (NFR-02) via subprocess; byte-identity test for system prompt (IG-01); JSONL completeness audit test (IG-02)

### Phase J: End-to-End Acceptance

### LANAAGNT-IP01-IS-20: Live acceptance run

**Location**: manual + `tests/test_e2e_offline.py`

**Action**: Offline e2e with scripted fake adapter (full /prime-like flow). Then manual live run: `lana` in this workspace with `agent_folder` including IPPS, execute `/prime`, one `edit` round trip, one `run_command` approval, `/cost`, Ctrl+C, `--resume`

**Note**: Acceptance criteria = Verification Checklist Validation block

### Phase E addendum (executed with Phase E)

### LANAAGNT-IP01-IS-21: Headless mode and exit codes (LANAAGNT-FR-14)

**Location**: `cli.py`, `agent.py`

**Action**: Add `-p/--prompt`, `--output-format text|jsonl`, `--config`/`LANA_CONFIG` override; exit codes 0/2/3/4 per FR-14; non-terminal stdin detection (`sys.stdin.isatty()`) switches to plain line input and auto-denies `approval_required`/`ask_user_question` with the FR-14 messages; built-ins (/help /cost /exit) dispatched before slash expansion in headless mode too (synced 2026-08-30)

**Note**: The jsonl output stream writes the same serialized AgentEvents as the session file - one serializer, two sinks. jsonl purity contract (`/improve` run 3, 2026-08-30): stdout carries ONLY event lines - startup banner, warnings, and error notices route to stderr so strict consumers (jq, log shippers, the MVP-2 ACP frontend) parse stdout directly

### LANAAGNT-IP01-IS-22: Scripted adapter and CLI test harness (LANAAGNT-DD-20)

**Location**: `tests/scripted_adapter.py`, `tests/harness.py`, `providers/__init__.py` (env hook)

**Action**: Script format = JSONL, one line per Generator turn: `{"text": str, "thinking": str?, "tool_calls": [{"name": str, "args": {}}]?, "usage": {"input": int, "output": int}?}` or `{"error": str}` (adapter raises a simulated provider failure - deterministic exit-code-3 testing, TP01-TC-10) - the adapter replays lines in order, errors if the script is exhausted. Harness `LanaProc`: spawn `lana` via subprocess with temp workspace + `--config` + `LANA_SCRIPTED_ADAPTER`, inject prompts (`-p` or stdin pipe), collect stdout JSONL events, `tail_session(predicate, timeout)` polling the flushed session file, assert exit codes

**Note**: Resolves deferred candidate D-02 (LANAAGNT-DF01). The env hook in `providers/__init__.py` is 5 lines: if `LANA_SCRIPTED_ADAPTER` set, return the scripted adapter for every role

## 4. Logging Preview

**Startup (success path):**
```text
Lana MVP-1 | generator: claude-sonnet-4-5 (medium) | summarizer: gpt-4.1-mini (low) | websearch: gpt-4.1-mini
Loading prompt system '.lana'...
  8 rules (7 injected, 1 skipped: empty), 46 workflows, 21 skills.
  OK. Loaded in 0.4 secs.
Policy: manual
```

**Startup (error path - EC-14):**
```text
ERROR: Role 'generator' model 'gpt-5.5-pro' is disabled in 'config/model-registry.json' (enabled=false).
  HINT: choose an enabled model or set "enabled": true in the registry.
```

**Tool loop with approval and cap:**
```text
> /prime
Running workflow 'prime'...
  [tool] read_file '!NOTES.md'...
    OK. 34 lines.
  [tool] run_command 'git log -n 5 --oneline' (policy: manual)
    Approve? [y/n/a] y
    OK. Exit code 0.
  [tool] run_command 'Get-Content big.log'
    Approve? [y/n/a] a
    [run_command] approved.
    OK. Output truncated: <truncated 412089 chars>.
  Turn: in=21050 (cache 18200) out=412 | $0.0164 | session $0.0164
```

**Compaction (success and failure paths):**
```text
Compacting context (projected 124K tokens > 120K threshold)...
  Summarizer call (gpt-4.1-mini)...
  OK. History 118 messages -> checkpoint + last 6 messages. Todo state preserved (7 items).

Compacting context (projected 124K tokens > 120K threshold)...
  WARNING: Summarizer call failed (429 rate limit). Continuing uncompacted - next turn may be expensive.
```

**Cancellation (EC-10):**
```text
^C
Turn cancelled after 3 tool calls (results kept in conversation).
>
```

**Resume startup (FR-08 full recall - fingerprint mismatch and model change):**
```text
Resuming session '.lana-data/sessions/2026-08-30_025545_54286c.jsonl'...
  118 events replayed, 0 lines skipped. Environment restored from session_started.
  WARNING: prompt system changed since recording (recorded 8/46/21, current 8/46/23 rules/workflows/skills). Recorded system prompt stays active for this session.
  WARNING: generator changed (recorded claude-sonnet-4-5-20250929, current gpt-5.2). Full context re-sent - first turn runs without provider cache.
  OK. Resumed with 12 messages.
```

## 5. Test Cases

### Category 1: Configuration (6 tests)

- **LANAAGNT-IP01-TC-01**: Valid config + registry -> roles resolved with provider params
- **LANAAGNT-IP01-TC-02**: Disabled model (EC-14) -> ConfigError names model, role, file
- **LANAAGNT-IP01-TC-03**: Missing key, env fallback order (env wins over file)
- **LANAAGNT-IP01-TC-04**: Effort translation per provider method (temperature vs reasoning_effort vs thinking factors)
- **LANAAGNT-IP01-TC-05**: Missing pricing entry (EC-24) -> cost `?`, no crash
- **LANAAGNT-IP01-TC-06**: Malformed lana-config.json -> error with line context

### Category 2: Prompt System Loading (6 tests)

- **LANAAGNT-IP01-TC-07**: Fake system (3 rules, 2 workflows, 1 skill) -> counts correct
- **LANAAGNT-IP01-TC-08**: Empty rule (EC-01) -> empty MEMORY block + skip count
- **LANAAGNT-IP01-TC-09**: Malformed frontmatter (EC-02) -> body-only, warning
- **LANAAGNT-IP01-TC-10**: Oversized rule (EC-03) -> truncation marker at limit
- **LANAAGNT-IP01-TC-11**: Two paths, colliding workflow name -> later path wins
- **LANAAGNT-IP01-TC-12**: Real IPPS (skip if absent) -> loader counts equal filesystem-derived counts (8/46/21 at analysis; the external system evolves - 23 skills by 2026-08-30) in < 2 s

### Category 3: System Prompt (3 tests)

- **LANAAGNT-IP01-TC-13**: Two builds byte-identical (IG-01)
- **LANAAGNT-IP01-TC-14**: No dropped-tool names anywhere in assembled prompt (RF-04 regression)
- **LANAAGNT-IP01-TC-15**: Section order matches FR-03 exactly

### Category 4: Tools and Gates (10 tests)

- **LANAAGNT-IP01-TC-16**: read_file cat-n format, offset/limit, long-line truncation
- **LANAAGNT-IP01-TC-17**: grep_search regex + FixedStrings + Includes filtering
- **LANAAGNT-IP01-TC-18**: find_by_name 50-result cap
- **LANAAGNT-IP01-TC-19**: edit without read (EC-07) -> gate error
- **LANAAGNT-IP01-TC-20**: external modification (EC-08) -> gate error; self-edit then edit again -> passes
- **LANAAGNT-IP01-TC-21**: multi_edit atomicity - failing edit 3 of 3 leaves file untouched
- **LANAAGNT-IP01-TC-22**: write_to_file on existing file -> error
- **LANAAGNT-IP01-TC-23**: tool result cap (EC-04) -> marker present, length exact
- **LANAAGNT-IP01-TC-24**: todo_list result byte-stable rendering (IG-04 anchor)
- **LANAAGNT-IP01-TC-25**: skill tool returns SKILL.md + supporting file list

### Category 5: Safety (6 tests)

- **LANAAGNT-IP01-TC-26**: `Remove-Item x` first-token match -> ASK in auto
- **LANAAGNT-IP01-TC-27**: `pwsh -Command "Remove-Item x"` wrapper -> ASK in auto and turbo (IG-03)
- **LANAAGNT-IP01-TC-28**: `git push --force-with-lease` prefix-matches `git push --force` entry -> ASK
- **LANAAGNT-IP01-TC-29**: `echo hi` in auto with SafeToAutoRun -> RUN
- **LANAAGNT-IP01-TC-30**: manual policy -> ASK for everything
- **LANAAGNT-IP01-TC-31**: out-of-workspace write_to_file -> approval required

### Category 6: Loop, Session, Compaction (8 tests, fake adapter)

- **LANAAGNT-IP01-TC-32**: Scripted 3-tool-call turn -> event sequence and JSONL complete (IG-02)
- **LANAAGNT-IP01-TC-33**: Call limit 25 (EC-11) -> pause; auto_continue -> no pause
- **LANAAGNT-IP01-TC-34**: Cancellation mid-loop (EC-10) -> kept results + synthetic note; resume reflects it
- **LANAAGNT-IP01-TC-35**: Resume after simulated crash with truncated last line (EC-21)
- **LANAAGNT-IP01-TC-36**: Projection: anchor 100K + 80K chars delta -> 120K projected, compaction fires
- **LANAAGNT-IP01-TC-37**: Checkpoint content: 3 anchors present, todo JSON byte-identical (IG-04)
- **LANAAGNT-IP01-TC-38**: Summarizer failure (EC-17) -> no truncation, warning event
- **LANAAGNT-IP01-TC-39**: No-todo compaction (EC-12) -> todo section omitted

### Category 7: Adapters and Web (6 tests, live-key smoke, skipped in CI)

- **LANAAGNT-IP01-TC-40**: OpenAI Responses: 1 function call round trip on gpt-4.1-mini
- **LANAAGNT-IP01-TC-41**: Anthropic: tool round trip + `cache_read_input_tokens > 0` on call 2 (NFR-03)
- **LANAAGNT-IP01-TC-42**: OpenAI reasoning model (gpt-5.x, effort medium): tool call works on Responses (RF-01 regression)
- **LANAAGNT-IP01-TC-43**: search_web via websearch role -> 5-result Cascade format
- **LANAAGNT-IP01-TC-44**: read_url_content approval + chunking + view_content_chunk (EC-25 for bad position)
- **LANAAGNT-IP01-TC-45**: read_url_content 5 MB / binary refusal (EC-18)

### Category 8: End-to-End (2 tests)

- **LANAAGNT-IP01-TC-46**: Offline e2e: fake-adapter /prime flow -> transcript matches SPEC section 12 log format
- **LANAAGNT-IP01-TC-47**: Live manual acceptance (IS-20 script) -> all steps pass, recorded in PROGRESS.md

### Category 9: Cost (2 tests)

- **LANAAGNT-IP01-TC-48**: Per-turn cost math: input/output/cache-read rates from `model-pricing.json` -> cost matches hand-computed value to 4 decimals
- **LANAAGNT-IP01-TC-49**: Per-role accumulation across 3 turns + 1 compaction -> `/cost` output shows generator, summarizer, websearch totals and session sum

### Category 10: Automated CLI Harness (6 tests, real executable, scripted adapter)

- **LANAAGNT-IP01-TC-50**: `lana -p "hello"` with 1-turn script -> final text on stdout, exit 0
- **LANAAGNT-IP01-TC-51**: Missing config -> stderr names file and fix, exit 2
- **LANAAGNT-IP01-TC-52**: Script requests denylisted `run_command` headless -> "approval denied (non-interactive session)" in tool result event, loop continues, exit 0
- **LANAAGNT-IP01-TC-53**: Same script run twice -> byte-identical event sequences modulo timestamps/ids (determinism)
- **LANAAGNT-IP01-TC-54**: `tail_session` observes each `tool_call_finished` within 1 s of stdout appearance (FR-08 flush contract)
- **LANAAGNT-IP01-TC-55**: Piped stdin session (`echo /help | lana`) -> workflow list printed, clean exit (non-terminal fallback)

### Category 11: Synced Regressions (5 tests, added from drift-correct/improve/bugfix runs 2026-08-30)

- **LANAAGNT-IP01-TC-56**: Provider "too long" error (EC-20) -> advisory message (larger-window model or new session, not retried), single turn_started (no auto-retry)
- **LANAAGNT-IP01-TC-57**: read_file on image (EC-26) -> refused with explanatory error; SVG readable
- **LANAAGNT-IP01-TC-58**: Headless `-p "/help"` and `-p "/cost"` -> built-in output, exit 0, never sent to the Generator
- **LANAAGNT-IP01-TC-59**: grep_search/find_by_name skip IGNORED_DIRECTORIES (.git, node_modules, ...); explicit search inside an ignored dir still works
- **LANAAGNT-IP01-TC-60**: Renderer prints bracketed untrusted text verbatim - no markup swallowing, no MarkupError (BG-0004); plus mid-prompt compaction fire (FR-07 per-turn check, drift item 02)

### Category 12: Trajectory Search (3 tests, added 2026-08-30)

- **LANAAGNT-IP01-TC-61**: Query-term scoring - matching chunks returned sorted by overlap descending; 50-chunk cap enforced on a 60-event session
- **LANAAGNT-IP01-TC-62**: Empty query returns all chunks chronologically (contract); ID resolution by exact name, stem, and unique prefix
- **LANAAGNT-IP01-TC-63**: Error paths (EC-27) - unknown ID lists available sessions, ambiguous prefix rejected, SearchType "user" rejected, definitions diff test covers the 16th tool

### Category 13: Full-Recall Session Log (4 tests, added 2026-08-30)

- **LANAAGNT-IP01-TC-64**: `session_started` is the first JSONL line of every new session and carries system prompt byte-identical to the assembled one, the verbatim tool definitions array, config snapshot, and fingerprint (FR-08, IG-07)
- **LANAAGNT-IP01-TC-65**: Resume authority - modify the fake prompt system on disk, `--resume` -> Generator receives the RECORDED system prompt byte-identically (scripted adapter captures the request); fingerprint mismatch warning printed; changed generator model in config -> model-change report line (IG-01 across resume)
- **LANAAGNT-IP01-TC-66**: Thinking payload round trip - scripted turn yields a thinking payload -> `turn_finished.thinking_payloads` in JSONL; resume reprojects it into Message.thinking on provider match; provider mismatch drops it from the resend while the event stays in the log (EC-29)
- **LANAAGNT-IP01-TC-67**: Legacy session file without `session_started` (EC-28) -> resume succeeds via disk assembly, legacy warning printed, conversation projection unchanged

## 6. Verification Checklist

### Prerequisites
- [x] **LANAAGNT-IP01-VC-01**: LANAAGNT-SP01 rev 21:45 re-read; tool definitions source `LANAAGNT-IN02` open during IS-06
- [x] **LANAAGNT-IP01-VC-02**: Python 3.12+ available; `pip install -e .` clean
- [x] **LANAAGNT-IP01-VC-03**: API keys resolvable for both providers (live phases only)

### Implementation
- [x] **LANAAGNT-IP01-VC-04**: Phase A green (TC-01..06)
- [x] **LANAAGNT-IP01-VC-05**: Phase B green (TC-07..15)
- [x] **LANAAGNT-IP01-VC-06**: Phase C green (TC-16..31)
- [x] **LANAAGNT-IP01-VC-07**: Phase D green (TC-40..42)
- [x] **LANAAGNT-IP01-VC-08**: Phase E green (TC-32..35, TC-50..55 incl. IS-21/IS-22)
- [x] **LANAAGNT-IP01-VC-09**: Phases F-G green (TC-36..39, TC-48..49)
- [x] **LANAAGNT-IP01-VC-10**: Phase H green (TC-43..45)
- [x] **LANAAGNT-IP01-VC-11**: Commit after each green phase (`/commit`)

### Validation
- [x] **LANAAGNT-IP01-VC-12**: All 67 test cases pass (live ones with keys present; TC-56..60 synced, TC-61..63 trajectory search, TC-64..67 full recall implemented and green 2026-08-30)
- [x] **LANAAGNT-IP01-VC-13**: NFR-01 verified by code review (only api.openai.com/api.anthropic.com contacted; `urllib` fetch gated by approval) + secret-leak sweeps in every black-box scenario - a literal packet capture was NOT performed [ASSUMED clean]; NFR-02 kill/resume (TP01-TC-06); NFR-03 startup < 2 s + cache hits (TC-41 live); NFR-05 risk notice on auto/turbo
- [x] **LANAAGNT-IP01-VC-14**: Live acceptance (TC-47) executed and logged
- [x] **LANAAGNT-IP01-VC-15**: `/verify` run on implementation against this plan; `/sync` SPEC if implementation deviated

## 7. Document History

**[2026-08-30 23:15]**
- Changed: IS-15 approval prompt from `[y/n]` to `[y/n/a]` (FR-12: `a` sets approve-all for remainder of turn, resets on next user prompt); logging preview updated with approve-all example

**[2026-08-30 03:50]**
- Changed: IS-24 implemented and green - 179 offline tests (TC-64..67 in tests/test_full_recall.py, TC-46b + TP01-TC-01 session-log assertions extended by the leading session_started line); VC-12 checked

**[2026-08-30 03:40]**
- Changed (verify pass): thinking payloads carried on `turn_finished.thinking_payloads` instead of a 12th event type (SP01 AgentEvent consistency); LANA_SCRIPTED_CAPTURE request-dump mechanism added to IS-24 (the TC-65/TP01-TC-11 byte-identity oracle was unspecified); fingerprint determinism [ASSUMED] label; Goal repointed to SP01 rev 03:40

**[2026-08-30 03:30]**
- Added: IS-24 full-recall session log (session_started event, turn_finished thinking payloads, resume environment authority, fingerprint warning, model-change report, cross-provider thinking drop) per SP01 FR-08/DD-22/IG-07 rev 03:20; EC-28 legacy session fallback, EC-29 provider-mismatch thinking drop; Category 13 TC-64..67; Resume startup logging preview
- Changed: events.py to 11 event types (File Structure + IS-02), Depends-on ranges to FR-15/DD-22/IG-07, VC-12 count 63 -> 67 and unchecked (TC-64..67 pending implementation)

**[2026-08-30 06:45]**
- Changed (`/verify` logging audit): status keywords aligned with LOGGING-RULES - `Fix:` -> `HINT:` in all ConfigError messages and the preview, `NOTICE:` -> `WARNING:` + `HINT:` for the auto/turbo risk notice, loader warnings end with periods (LOG-GN-11); deviations from UF headers/timestamps documented in Logging Preview note below
- Added (Logging Preview note): Lana's interactive chat stream intentionally deviates from LOG-UF-01 timestamps and LOG-UF-06 100-char headers - a conversational REPL is not a batch script; timestamps live in the session JSONL (every AgentEvent carries ts per NFR-04), and turn boundaries are visible via the prompt and Turn: lines. SPEC section 12 expected output is the binding format.

**[2026-08-30 06:20]**
- Added: IS-23 trajectory_search implementation step (FR-15/DD-21), EC-27 error paths, Category 12 TC-61..63, trajectory_tools.py in File Structure; VC-12 count 60 → 63

**[2026-08-30 04:55]**
- Changed (`/improve` run 3): IS-21 jsonl stdout purity - diagnostics to stderr in headless jsonl mode (evidence: tests/harness.py carried a skip-non-JSON workaround for the contamination); purity regression tests added; 4 unused test imports removed

**[2026-08-30 04:15]**
- Changed (`/sync` Code→IMPL, body sweep): File Structure notes scripted_adapter package location; IS-07 ignore-directories + image refusal + grep [ASSUMED]→[TESTED]; IS-14 kept_messages + cost seeding; IS-15 BG-0004 markup constraint; IS-16 cache-write rate + usage normalization contract; IS-17 >= threshold, per-turn check, 6-message tail + orphan-tool trim; IS-18 .lana-data/chunks persistence (replaces JSONL mirroring); IS-21 headless built-ins; TC-12 filesystem-derived counts
- Added: EC-26 (image read refusal), Category 11 TC-56..60 (synced regressions); VC-12 count 55 → 60

**[2026-08-30 03:58]**
- Fixed: LANAAGNT-BG-0004 - renderer parsed untrusted event text as rich markup (Markdown links swallowed, MarkupError crash on `[/tag]`-like content); all payload prints now markup=False with style= parameters (IS-15 constraint: untrusted text never enters markup parsing). Verified non-bug: Anthropic auto-combines consecutive same-role messages (ANTAPI-IN08) - cancellation-note/checkpoint sequences safe

**[2026-08-30 02:50]**
- Changed (`/drift-correct`): FR-07 compaction check moved inside the tool loop (after every turn), EC-20 overflow advisory added, PAGER=cat set, image reads refused with notice, headless built-ins dispatched; VC-13 reworded to the evidence actually collected; BG-0003 fixed (Anthropic web_search allowed_domains is a web_fetch-only parameter per ANTAPI-IN24)

**[2026-08-30 02:10]**
- Changed (implementation sync): scripted adapter lives in `src/lana/providers/scripted_adapter.py` (not `tests/`) - the installed executable must load it via LANA_SCRIPTED_ADAPTER; `tests/scripted_adapter.py` re-exports it plus script helpers (IS-22 deviation)
- Changed (implementation sync): IS-18 chunk store persisted via `.lana-data/chunks/<document_id>.json` files instead of JSONL event mirroring - same resume guarantee, simpler mechanism
- Changed (implementation sync): IS-06 arg validation implemented as minimal built-in validator (no `jsonschema` dependency - DD-17 list is closed); TC-36 threshold comparison is `>=` (fires at exactly 120K)
- Fixed: LANAAGNT-BG-0001 (approval_required not yielded to the event stream), LANAAGNT-BG-0002 (/cost empty after --resume) - see `_BugFixes/`
- All 15 VC items checked: 161 offline + 4 live tests green; live acceptance automated portion passed against IPPS

**[2026-08-29 22:20]**
- Added: IS-21 (headless mode, exit codes), IS-22 (scripted adapter + LanaProc harness, resolves DF01 D-02), Category 10 harness tests TC-50..55, harness files in File Structure, flush contract in IS-14 (SPEC FR-14/DD-20 gap closure)
- Changed: VC-08 range, VC-12 count 49 -> 55

**[2026-08-29 22:08]**
- Changed: IS-06/VC-01/Depends-on/MNF repointed to `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` as primary transcription source (`/improve` run 2: ebook lacks full verbatim text for multi_edit, command_status, skill - broken source dependency)

**[2026-08-29 22:00]**
- Added: Category 9 Cost tests TC-48/49 (Phase F had no dedicated tests - SOCAS-06 gap), phase flow diagram in section 3 (MW-VR-03), [ASSUMED] labels on line estimates, pure-Python grep, and chunk size
- Changed: VC-09 test range, VC-12 count 47 -> 49

**[2026-08-29 21:55]**
- Initial implementation plan created: 10 phases, 20 implementation steps, 25 edge cases, 47 test cases, 15 verification items, from LANAAGNT-SP01 rev 21:45
