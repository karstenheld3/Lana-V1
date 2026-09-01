# IMPL: Lana Tool System

**Doc ID**: LANATOOL-IP01
**Goal**: Implement tool definitions, file/edit/shell tools, web research, trajectory search, and supporting tools per LANATOOL-SP01
**Timeline**: Created 2026-08-29, Extracted from _IMPL_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `src/lana/tools/definitions.py` (verbatim Cascade tool definitions)
- `src/lana/tools/__init__.py` (registry: name -> definition, executor, needs_approval_fn)
- `src/lana/tools/file_tools.py` (read_file, list_dir, grep_search, find_by_name)
- `src/lana/tools/edit_tools.py` (edit, multi_edit, write_to_file + ReadLedger)
- `src/lana/tools/shell_tools.py` (run_command, command_status)
- `src/lana/tools/web_tools.py` (search_web, read_url_content, view_content_chunk)
- `src/lana/tools/trajectory_tools.py` (trajectory_search)
- `src/lana/tools/state_tools.py` (todo_list)
- `src/lana/tools/skill_tool.py` (skill)
- `src/lana/tools/interact_tools.py` (ask_user_question)

**Depends on:**
- `_SPEC_LANA_05-Tools.md [LANATOOL-SP01]` for FR-10, FR-11, FR-13, FR-15, DD-10, DD-11, DD-14, DD-19, DD-21
- `_IMPL_LANA_01-ProductOverview.md [LANAAGNT-IP01]` for IS-02 (canonical models/events)
- `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` for verbatim tool definitions (primary transcription source)

**Does not depend on:**
- `_IMPL_LANA_02-AgentCore.md [LANACORE-IP01]` (AgentCore dispatches through the tool registry; tools are self-contained executors)

## MUST-NOT-FORGET

- Tool names, descriptions, parameter names, JSON Schemas verbatim from `LANAAGNT-IN02` (LANAAGNT-DD-11) - transcribe, never paraphrase; description blocks there are [LITERAL]
- Small cycles: implement -> test -> green -> commit per phase; never proceed on red

## Table of Contents

1. [Edge Cases](#1-edge-cases)
2. [Implementation Steps](#2-implementation-steps)
3. [Test Cases](#3-test-cases)
4. [Verification Checklist](#4-verification-checklist)
5. [Document History](#5-document-history)

## 1. Edge Cases

**Edit enforcement:**
- **LANAAGNT-IP01-EC-07**: `edit` without prior `read_file` in session -> tool error naming the gate and the required action (LANAAGNT-FR-11)
- **LANAAGNT-IP01-EC-08**: File modified externally after last read (mtime newer than ledger) -> gate blocks with "re-read required"
- **LANAAGNT-IP01-EC-09**: `old_string` not unique and `replace_all` false -> error with occurrence count

**Web research:**
- **LANAAGNT-IP01-EC-18**: `read_url_content` network error, non-HTML content, or >5 MB body -> tool error with URL and reason; binary content refused
- **LANAAGNT-IP01-EC-25**: `view_content_chunk` with unknown `document_id` or out-of-range position -> error naming valid range

**File reading:**
- **LANAAGNT-IP01-EC-26**: `read_file` on an image file -> refused with explanatory error (no visual presentation in a CLI); SVG stays readable as text (synced from implementation 2026-08-30)

**Trajectory search:**
- **LANAAGNT-IP01-EC-27**: `trajectory_search` with unknown `ID`, ambiguous prefix, `SearchType: "user"`, or no sessions folder -> error naming available session ids / the contract violation (FR-15)

## 2. Implementation Steps

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

### LANAAGNT-IP01-IS-09: Shell tools (LANAAGNT-FR-12)

**Location**: `tools/shell_tools.py`

**Action**: `run_command` via `subprocess.Popen(["pwsh","-NoProfile","-Command",cmd], cwd=...)` with Blocking/WaitMsBeforeAsync semantics; background process table for `command_status` (OutputCharacterCount, WaitDurationSeconds)

**Note**: Safety classification (safety.py) is in `_IMPL_LANA_02-AgentCore.md [LANACORE-IP01]` IS-09. Approval renders exact command + cwd (render.py)

### LANAAGNT-IP01-IS-10: State, skill, interaction tools

**Location**: `tools/state_tools.py`, `tools/skill_tool.py`, `tools/interact_tools.py`

**Action**: `todo_list` (validate items, store last state on Session, emit result in Cascade's "Todo list updated:" + JSON format - the deterministic extraction anchor), `skill` (SKILL.md body + "Base Directory" header + supporting file list), `ask_user_question` (emits `approval_required`-style blocking event; frontend supplies answer)

**Note**: The exact `todo_list` result format is load-bearing for compaction (IG-04) - test asserts byte-stable rendering

### Phase H: Web Tools

### LANAAGNT-IP01-IS-18: Web research tools (LANAAGNT-FR-13)

**Location**: `tools/web_tools.py`

**Action**: `search_web`: one-shot side-call via `websearch` role adapter with the provider-native web search tool; render Cascade's 5-result format. `read_url_content`: approval gate -> `urllib`/`httpx` GET (5 MB cap, text/HTML only, EC-18) -> HTML-to-text -> chunk (~5K chars) -> store per `document_id`. `view_content_chunk`: chunk lookup (EC-25)

**Note**: Chunk store is session-scoped in-memory + persisted as `.lana-data/chunks/<document_id>.json` files - view_content_chunk survives --resume by lazy disk load (implementation replaced the JSONL-mirroring idea; same guarantee, simpler - synced 2026-08-30). Chunk size ~5K chars [ASSUMED - matches Cascade's observed 2-8 KB chunk cost range]

### LANAAGNT-IP01-IS-23: Session trajectory search tool (LANAAGNT-FR-15)

**Location**: `tools/trajectory_tools.py`, `tools/definitions.py`, `prompt.py`, `cli.py`

**Action**: Transcribe the `trajectory_search` definition verbatim from IN02 section 7 (hand-transcription guarded by the diff test). Executor: resolve `ID` against `[workspace]/.lana-data/sessions/` (exact name, stem, or unique prefix); render each event line as one chunk `[NNN] type: excerpt`; score by case-insensitive query-term overlap, sort descending (stable by position); empty query -> chronological; cap 50 chunks; `SearchType: "user"` -> error. Register executor; REMOVE trajectory_search from the `prompt.py` capability notice

**Note**: Lexical scoring only (DD-21); the current session's own file is searchable too (it is flushed per line, FR-08)

## 3. Test Cases

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

### Category 7: Web Tools (3 tests, live-key smoke, skipped in CI)

- **LANAAGNT-IP01-TC-43**: search_web via websearch role -> 5-result Cascade format
- **LANAAGNT-IP01-TC-44**: read_url_content approval + chunking + view_content_chunk (EC-25 for bad position)
- **LANAAGNT-IP01-TC-45**: read_url_content 5 MB / binary refusal (EC-18)

### Category 11: Synced Regressions (5 tests)

- **LANAAGNT-IP01-TC-56**: Provider "too long" error (EC-20) -> advisory message (larger-window model or new session, not retried), single turn_started (no auto-retry)
- **LANAAGNT-IP01-TC-57**: read_file on image (EC-26) -> refused with explanatory error; SVG readable
- **LANAAGNT-IP01-TC-58**: Headless `-p "/help"` and `-p "/cost"` -> built-in output, exit 0, never sent to the Generator
- **LANAAGNT-IP01-TC-59**: grep_search/find_by_name skip IGNORED_DIRECTORIES (.git, node_modules, ...); explicit search inside an ignored dir still works
- **LANAAGNT-IP01-TC-60**: Renderer prints bracketed untrusted text verbatim - no markup swallowing, no MarkupError (BG-0004); plus mid-prompt compaction fire (FR-07 per-turn check, drift item 02)

### Category 12: Trajectory Search (3 tests)

- **LANAAGNT-IP01-TC-61**: Query-term scoring - matching chunks returned sorted by overlap descending; 50-chunk cap enforced on a 60-event session
- **LANAAGNT-IP01-TC-62**: Empty query returns all chunks chronologically (contract); ID resolution by exact name, stem, and unique prefix
- **LANAAGNT-IP01-TC-63**: Error paths (EC-27) - unknown ID lists available sessions, ambiguous prefix rejected, SearchType "user" rejected, definitions diff test covers the 16th tool

## 4. Verification Checklist

- [x] **LANATOOL-IP01-VC-01**: LANATOOL-SP01 re-read; all 4 FRs, 5 DDs accounted for
- [x] **LANATOOL-IP01-VC-02**: Phase C green (TC-16..25, tools and gates)
- [x] **LANATOOL-IP01-VC-03**: Phase H green (TC-43..45, web tools)
- [x] **LANATOOL-IP01-VC-04**: Category 11 green (TC-56..60, synced regressions)
- [x] **LANATOOL-IP01-VC-05**: Category 12 green (TC-61..63, trajectory search)
- [x] **LANATOOL-IP01-VC-06**: Tool definitions diff-checked against IN02 (zero differences outside substitution points)

## 5. Document History

**[2026-09-01 21:45]**
- Extracted from `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]`: IS-06 (definitions), IS-07 (file tools), IS-08 (edit tools), IS-09 (shell tools portion), IS-10 (state/skill/interact), IS-18 (web tools), IS-23 (trajectory search)
- Edge cases: EC-07/08/09/18/25/26/27
- Test cases: Categories 4 (Tools/Gates), 7 web portion (TC-43..45), 11 (Synced Regressions), 12 (Trajectory Search)
- Content is verbatim from source with section renumbering and header block update only
