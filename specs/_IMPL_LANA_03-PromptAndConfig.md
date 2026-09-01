# IMPL: Lana Prompt and Configuration

**Doc ID**: LANAPRCF-IP01
**Goal**: Implement configuration loading, prompt system loading, and system prompt assembly per LANAPRCF-SP01
**Timeline**: Created 2026-08-29, Extracted from _IMPL_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `src/lana/config.py` (LanaConfig + registry/mapping/pricing/keys loading, validation)
- `src/lana/loader.py` (PromptSystem loading: rules/workflows/skills, frontmatter)
- `src/lana/prompt.py` (system prompt assembly: sections, MEMORY blocks, capability notice)

**Depends on:**
- `_SPEC_LANA_03-PromptAndConfig.md [LANAPRCF-SP01]` for FR-01, FR-02, FR-03, DD-02, DD-12, DD-16, DD-23, DD-25, IG-01
- `_IMPL_LANA_01-ProductOverview.md [LANAAGNT-IP01]` for IS-01 (skeleton), IS-02 (models/events)

**Does not depend on:**
- `_IMPL_LANA_02-AgentCore.md [LANACORE-IP01]` (AgentCore consumes config and prompt outputs)

## MUST-NOT-FORGET

- System prompt byte-identical across a session (LANAAGNT-IG-01) - no timestamps, no cwd, no variable content in it
- Existing `config/*.json` files are read-only inputs - never write to them
- Small cycles: implement -> test -> green -> commit per phase; never proceed on red

## Table of Contents

1. [Edge Cases](#1-edge-cases)
2. [Implementation Steps](#2-implementation-steps)
3. [Test Cases](#3-test-cases)
4. [Verification Checklist](#4-verification-checklist)
5. [Document History](#5-document-history)

## 1. Edge Cases

**Input boundaries:**
- **LANAAGNT-IP01-EC-01**: Rules file is empty or whitespace (`workspace-rules.md`, 32 bytes) -> inject empty MEMORY block (Cascade parity), count as "skipped: empty" in startup report
- **LANAAGNT-IP01-EC-02**: Frontmatter missing or malformed YAML -> treat file as body-only, `trigger` defaults to always-on, log warning with filename
- **LANAAGNT-IP01-EC-03**: Rule body exceeds `rule_block_max_chars` -> truncate at limit, append `<truncated N chars>` marker

**External failures:**
- **LANAAGNT-IP01-EC-14**: Configured model missing or `enabled: false` in registry -> startup error naming model_id, role, and the registry file
- **LANAAGNT-IP01-EC-15**: API key missing for a configured provider -> startup error naming env var and key file path

**Data anomalies:**
- **LANAAGNT-IP01-EC-30**: Install root resolution (DD-25): `--app-dir <path>` > env `LANA_APP_DIR` > CWD fallback; config, agent_folder, data_dir resolve relative to app directory, not workspace

## 2. Implementation Steps

### Phase A: Configuration

### LANAAGNT-IP01-IS-03: Configuration loading (LANAAGNT-FR-01)

**Location**: `config.py`

**Action**: Add `load_lana_config(workspace, install_root)`:
```python
def load_lana_config(workspace, install_root) -> LanaConfig: ...
# 0. install_root is the base for config, agent_folder, data_dir (DD-25)
# 1. Parse install_root/config/lana-config.json (pydantic schema per SPEC section 10)
# 2. Resolve each role model against model-registry.json: exists + enabled, else ConfigError
# 3. Resolve provider params via model_id_startswith method + effort_mapping factors
# 4. Keys: env var first (OPENAI_API_KEY / ANTHROPIC_API_KEY), then config/.api-keys.txt; track source per provider ("env" or ".api-keys.txt") in key_sources dict
# 5. Load model-pricing.json into cost table (missing model tolerated, EC-24)
# 6. Boot banner prints "Keys: provider (source), ..." line so user knows where keys come from (FR-01)
# 7. agent_folder and data_dir resolved relative to install_root (not workspace)
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

### Phase K: Session Load Improvements

### LANAAGNT-IP01-IS-25: Session load quality improvements (LANAAGNT-FR-03, FR-04, FR-10)

**Location**: `prompt.py`, `cli.py`, `config.py`, `tools/file_tools.py`, `.lana/workflows/session-load.md`, `.lana/workflows/prime.md`

**Action**:
```python
# prompt.py: build_user_information includes agent_folder path from workspace_info (PR-0001, FR-03)
# cli.py: workspace_info dict gains "agent_folder": str(app.agent_folder) (PR-0001)
# config.py: max_tool_calls_per_prompt default 25 -> 40 (PR-0006, FR-04)
# file_tools.py: path_not_found_hint() on read_file/list_dir ToolError (PR-0002, FR-10)
#   - walks parent chain to closest existing dir, fuzzy-matches siblings by stem
# session-load.md Step 1: path decomposition strategy (PR-0003)
# session-load.md Step 2: /prime targets session's parent workspace (PR-0004)
# session-load.md Step 3: root-level docs only (PR-0007)
# prime.md Step 3: large file limits - FAILS.md first 50, ID-REGISTRY.md first 30 (PR-0005)
```

**Edge cases**:
- **LANAAGNT-IP01-EC-31**: `path_not_found_hint` on deeply nested nonexistent paths - parent walk stops at drive root, returns hint with closest existing ancestor

## 3. Test Cases

### Category 1: Configuration (7 tests)

- **LANAAGNT-IP01-TC-01**: Valid config + registry -> roles resolved with provider params
- **LANAAGNT-IP01-TC-02**: Disabled model (EC-14) -> ConfigError names model, role, file
- **LANAAGNT-IP01-TC-03**: Missing key, env fallback order (env wins over file)
- **LANAAGNT-IP01-TC-04**: Effort translation per provider method (temperature vs reasoning_effort vs thinking factors)
- **LANAAGNT-IP01-TC-05**: Missing pricing entry (EC-24) -> cost `?`, no crash
- **LANAAGNT-IP01-TC-06**: Malformed lana-config.json -> error with line context
- **LANAAGNT-IP01-TC-68**: Install root separation (EC-30): config + agent_folder + data_dir resolve relative to install_root, not workspace; workspace used only for tool operations

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

### Category 14: Session Load Improvements (5 tests)

- **LANAAGNT-IP01-TC-69**: `path_not_found_hint` shows closest existing parent and fuzzy-matched siblings when target missing (EC-31)
- **LANAAGNT-IP01-TC-70**: `path_not_found_hint` on deeply nested nonexistent paths returns hint with drive root ancestor
- **LANAAGNT-IP01-TC-71**: `read_file` not-found error message includes HINT with parent path
- **LANAAGNT-IP01-TC-72**: `list_dir` not-found error message includes HINT with parent path
- **LANAAGNT-IP01-TC-73**: `path_not_found_hint` returns empty string when even root doesn't exist (e.g. Z:\ drive)

## 4. Verification Checklist

- [x] **LANAPRCF-IP01-VC-01**: LANAPRCF-SP01 re-read; all 3 FRs, 5 DDs, 1 IG accounted for
- [x] **LANAPRCF-IP01-VC-02**: Phase A green (TC-01..06, TC-68)
- [x] **LANAPRCF-IP01-VC-03**: Phase B green (TC-07..15)
- [x] **LANAPRCF-IP01-VC-04**: Phase K green (TC-69..73)
- [x] **LANAPRCF-IP01-VC-05**: IG-01 test: two consecutive builds byte-identical

## 5. Document History

**[2026-09-01 21:45]**
- Extracted from `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]`: IS-03 (config), IS-04 (loader), IS-05 (prompt assembly), IS-25 (session load improvements)
- Edge cases: EC-01/02/03/14/15/30/31
- Test cases: Categories 1 (Configuration), 2 (Prompt System Loading), 3 (System Prompt), 14 (Session Load Improvements)
- Content is verbatim from source with section renumbering and header block update only
