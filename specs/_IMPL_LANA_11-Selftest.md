# IMPL: Selftest Framework

**Doc ID**: LANASTST-IP01
**Goal**: Implement the `/selftest` workflow, skill, and runner script specified in `_SPEC_LANA_11-Selftest.md [LANASTST-SP01]`
**Timeline**: Created 2026-08-30

**Target file(s)**:
- `.lana/workflows/selftest.md` (NEW)
- `.lana/skills/selftest/SKILL.md` (NEW)
- `.lana/skills/selftest/selftest.py` (NEW ~320 lines)
- `tests/test_selftest_script.py` (NEW ~80 lines)

**Depends on:**
- `_SPEC_LANA_11-Selftest.md [LANASTST-SP01]` for all FR/DD/IG/NFR requirements
- `src/lana/config.py` (read-only reuse: `load_lana_config`, `resolve_role`, `resolve_key`, `parse_key_file`, `RoleSpec`, `read_json`)
- `src/lana/providers/` (read-only reuse: `OpenAIAdapter`, `AnthropicAdapter`, `is_retryable_error`)
- `src/lana/models.py`, `src/lana/cost.py` (read-only reuse)

**Does not depend on:**
- `evals/` (separate framework, agent-level evaluation)
- `tests/test_adapters.py` (existing live smokes stay unchanged)

## MUST-NOT-FORGET

- Zero changes to `src/lana/` (LANASTST-DD-01)
- Budget check BEFORE each live test (LANASTST-IG-01)
- Missing key = skip, not crash (LANASTST-IG-02)
- `results.json` written on partial runs, always valid JSON (IG-04, IG-05)
- Never print key material (FR-04)
- Script must be importable as module for offline tests

## Table of Contents

1. [File Structure](#1-file-structure)
2. [Design Choices](#2-design-choices)
3. [Edge Cases](#3-edge-cases)
4. [Implementation Steps](#4-implementation-steps)
5. [Logging Preview](#5-logging-preview)
6. [Test Cases](#6-test-cases)
7. [Verification Checklist](#7-verification-checklist)
8. [Document History](#8-document-history)

## 1. File Structure

```
.lana/
├── workflows/
│   └── selftest.md              # Workflow: arg mapping, interpreter discovery, menu flow [NEW]
└── skills/
    └── selftest/
        ├── SKILL.md             # Skill doc: usage, script contract, interpreter discovery [NEW]
        └── selftest.py          # Runner: categories, menu, budget, results (~320 lines) [NEW]
tests/
└── test_selftest_script.py      # Offline tests: menu, selection, discovery, offline cats [NEW]
```

## 2. Design Choices

**LANASTST-IP01-DC-01: Interpreter discovery (resolves LANASTST-PR-0004)**
The workflow instructs Lana to find a working interpreter in this order, testing each with `<python> -c "import lana"`:
1. `LANA_PYTHON` environment variable (explicit override, works for PyApp installs)
2. `.venv/Scripts/python.exe` relative to workspace (dev checkout)
3. `python` on PATH (pip install)

If none imports `lana`: report to the user with the hint to set `LANA_PYTHON`. Additionally `selftest.py` starts with an import guard (EC-03) so a wrong interpreter fails with a clear message, exit code 3.

**LANASTST-IP01-DC-02: Single-file script, importable module**
All categories live in `selftest.py` with a `main(argv)` entry point and pure helper functions. Offline tests import it via `importlib` from the skill path -- no packaging needed.

**LANASTST-IP01-DC-03: Category registry as data**
Categories are a list of dataclass entries (code, name, cost_class, estimate, runner function). Menu, selection validation, and dispatch all derive from this list (FR-01).

**LANASTST-IP01-DC-04: Unpriced models count $0 toward budget**
Models missing from `model-pricing.json` run with `cost_usd: null` and a warning; budget accumulation treats them as $0 (mirrors `lana.cost` EC-24 behavior of flagging, not blocking).

**LANASTST-IP01-DC-05: Workspace resolution**
Script resolves the workspace as the current working directory (Lana runs `run_command` with workspace cwd). Config path override honored via `LANA_CONFIG` env var, matching Lana's own behavior.

## 3. Edge Cases

- **LANASTST-IP01-EC-01**: No API key for any provider -> all live tests skip, offline categories still run, exit 0
- **LANASTST-IP01-EC-02**: Invalid category code argument -> print valid codes, exit 2
- **LANASTST-IP01-EC-03**: `import lana` fails -> print interpreter hint (LANA_PYTHON), exit 3
- **LANASTST-IP01-EC-04**: Model missing from pricing file -> cost null, warning, budget +$0, continue (DC-04)
- **LANASTST-IP01-EC-05**: Budget exhausted mid-run -> remaining live tests status `budget_exceeded`, results.json written, exit per pass/fail rule
- **LANASTST-IP01-EC-06**: KeyboardInterrupt -> finally-block writes results.json with completed tests, exit 130
- **LANASTST-IP01-EC-07**: Per-model timeout -> status fail with duration, continue next model
- **LANASTST-IP01-EC-08**: Available model matches no prefix entry -> status skip with warning (FR-06)
- **LANASTST-IP01-EC-09**: `.lana-data/` not writable -> print error, exit 3 (before any API call)
- **LANASTST-IP01-EC-10**: Provider endpoint unreachable in category 01 -> that check fails, run continues
- **LANASTST-IP01-EC-11**: Tool call category: model answers without tool_call -> status fail "no tool_call emitted"
- **LANASTST-IP01-EC-12**: `--model <id>` not in registry or not available -> print error, exit 2
- **LANASTST-IP01-EC-13**: Transient API error (429, 5xx) -> one retry after 3s (NFR-03), second failure = fail
- **LANASTST-IP01-EC-14**: Config files missing/malformed in category 02 -> checks fail with ConfigError text, run continues

## 4. Implementation Steps

### LANASTST-IP01-IS-01: Create workflow file

**Location**: `.lana/workflows/selftest.md` (NEW)

**Action**: Add workflow with frontmatter `description: Run Lana selftest - environment, configuration, prompt system, and model health checks`

**Content outline**:
- Step 1: Interpreter discovery (DC-01 order, test with `-c "import lana"`)
- Step 2: No user args -> run `selftest.py --menu`, show menu, ask user for selection
- Step 3: `live` or `all` requested -> state estimated cost, ask confirmation (execution policy handles the rest)
- Step 4: Run `<python> .lana/skills/selftest/selftest.py <codes> [options]` (blocking)
- Step 5: Summarize pass/fail/skip counts and total cost from script output; point to results.json path

### LANASTST-IP01-IS-02: Create skill documentation

**Location**: `.lana/skills/selftest/SKILL.md` (NEW)

**Action**: Add skill doc: purpose, category table (codes 01-06 as list), script CLI contract (args, exit codes 0/1/2/3), interpreter discovery, results.json location

### LANASTST-IP01-IS-03: Script scaffold - categories, menu, arg parsing

**Location**: `.lana/skills/selftest/selftest.py` (NEW)

**Action**: Add module docstring, imports (stdlib + lana import guard EC-03), category dataclass + registry (DC-03), `parse_args()`, `print_menu()`, `main(argv)`

**Code**:
```python
@dataclass
class Category:
  code: str; name: str; cost_class: str; estimate: str; runner: Callable
def print_menu(categories): ...      # FR-01 menu format from SP01 section 10
def select_categories(args): ...     # FR-02: codes | all | offline | live, exit 2 on invalid
def main(argv=None) -> int: ...
```

### LANASTST-IP01-IS-04: Offline categories 01-03

**Location**: `selftest.py`

**Action**: Add `run_environment()`, `run_configuration()`, `run_prompt_system()`

**Code**:
```python
def run_environment(ctx): ...    # FR-03: python>=3.12, lana version, data dir writable, TLS connect api.openai.com/api.anthropic.com:443
def run_configuration(ctx): ...  # FR-04: load_lana_config(require_keys=False), per-role resolve, key presence, pricing coverage
def run_prompt_system(ctx): ...  # FR-05: folders exist, workflow frontmatter parses, SKILL.md per skill folder
```

**Note**: category 01 endpoint check uses `socket.create_connection` + TLS wrap with 5s timeout -- no SDK, no auth (DD-10)

### LANASTST-IP01-IS-05: Model discovery + shared turn runner

**Location**: `selftest.py`

**Action**: Add `discover_models()` (FR-06 filters) and `run_model_turn()` shared by categories 04-06

**Code**:
```python
def discover_models(ctx, provider_filter, model_filter): ...  # enabled+available+prefix+key (EC-08, EC-12)
def run_model_turn(ctx, role, messages, tools): ...           # asyncio.run + timeout (EC-07) + one retry (EC-13), returns deltas/usage/duration
```

### LANASTST-IP01-IS-06: Category 04 Model Sweep

**Location**: `selftest.py`

**Action**: Add `run_sweep()` -- per model: resolve role at default effort (FR-07), minimal prompt, verify text + usage deltas, budget precheck (FR-10)

### LANASTST-IP01-IS-07: Category 05 Effort Matrix

**Location**: `selftest.py`

**Action**: Add `run_effort_matrix()` -- cheapest model per method (pricing lookup, fallback: fewest context_window), effort levels per prefix entry or low/medium/high (FR-08)

### LANASTST-IP01-IS-08: Category 06 Tool Calls

**Location**: `selftest.py`

**Action**: Add `run_tool_calls()` -- generator model per provider (fallback cheapest), turn 1 expects tool_call delta, turn 2 sends result, expects text (FR-09, EC-11). Tool definition copied from Lana's `read_file` schema shape.

### LANASTST-IP01-IS-09: Cost tracking, results, exit codes

**Location**: `selftest.py`

**Action**: Add `compute_cost()` (same formula as `lana.cost`, DC-04), `write_results()` (IG-04: called in finally-block, EC-06), summary printing, exit code logic (IG-03)

### LANASTST-IP01-IS-10: Offline tests

**Location**: `tests/test_selftest_script.py` (NEW)

**Action**: Add offline tests importing `selftest.py` via importlib from `.lana/skills/selftest/`. Cover: menu output, selection parsing (EC-02), discovery filters (EC-08), offline categories in tmp workspace (reuse `tests/conftest.py` config writers), results.json schema, budget precheck unit test

**Note**: no live tests here -- live coverage is the selftest itself

## 5. Logging Preview

Success, failure, and skip paths (SP01 section 11 is the contract):

**Offline category (02) with one failure:**
```
SELFTEST: 02 Configuration
  lana-config.json: valid...OK | roles: 3 resolved...OK
  keys: openai present, anthropic MISSING
  pricing: 18 of 20 enabled models priced (missing: gpt-5.6-luna, claude-sonnet-4-6)
  02 Configuration: 3 passed, 1 warning.
```

**Live category (04) with skip (no anthropic key):**
```
SELFTEST: 04 Model Sweep (15 OpenAI, 5 Anthropic) | Budget: $5.00
  [ 1 / 20 ] gpt-5.6-sol (reasoning_effort, none)...
    OK. 127in/23out $0.0012 1.3s
  [ 16 / 20 ] claude-sonnet-4-6 (adaptive_thinking, medium)...
    SKIP: no ANTHROPIC_API_KEY
  04 Model Sweep: 15 passed, 0 failed, 5 skipped.
```

**Interpreter guard (EC-03):**
```
ERROR: cannot import 'lana' with this interpreter (python 3.12.6, C:\Python312\python.exe).
  HINT: set LANA_PYTHON to the interpreter that runs Lana, or use .venv\Scripts\python.exe in a dev checkout.
```

## 6. Test Cases

### Category 1: Selection and menu (4 tests)

- **LANASTST-IP01-TC-01**: `--menu` output contains all 6 codes with cost class -> ok
- **LANASTST-IP01-TC-02**: `select_categories(["01","04"])` -> exactly those two, ascending
- **LANASTST-IP01-TC-03**: `offline` -> 01-03; `live` -> 04-06; `all` -> 01-06
- **LANASTST-IP01-TC-04**: invalid code `99` -> exit 2, message lists valid codes

### Category 2: Discovery (3 tests)

- **LANASTST-IP01-TC-05**: registry fixture with disabled/unavailable models -> only enabled+available returned
- **LANASTST-IP01-TC-06**: model without prefix match -> excluded, warning recorded (EC-08)
- **LANASTST-IP01-TC-07**: provider without key -> models listed with skip status (EC-01)

### Category 3: Offline categories (3 tests)

- **LANASTST-IP01-TC-08**: category 02 on valid tmp workspace config -> all checks pass
- **LANASTST-IP01-TC-09**: category 02 with missing pricing file -> check fails, no exception (EC-14)
- **LANASTST-IP01-TC-10**: category 03 with skill folder missing SKILL.md -> check fails, named folder in message

### Category 4: Results and budget (3 tests)

- **LANASTST-IP01-TC-11**: results.json written with summary counts matching test list (IG-05)
- **LANASTST-IP01-TC-12**: budget precheck: remaining < $0.01 -> `budget_exceeded` status (EC-05)
- **LANASTST-IP01-TC-13**: exit code 1 when any fail, 0 when only pass/skip (IG-03)

## 7. Verification Checklist

### Prerequisites
- [ ] **LANASTST-IP01-VC-01**: SP01 read, all FR/IG cross-checked against steps
- [ ] **LANASTST-IP01-VC-02**: No `src/lana/` file modified (DD-01)

### Implementation
- [ ] **LANASTST-IP01-VC-03**: IS-01 workflow created
- [ ] **LANASTST-IP01-VC-04**: IS-02 SKILL.md created
- [ ] **LANASTST-IP01-VC-05**: IS-03..09 selftest.py complete
- [ ] **LANASTST-IP01-VC-06**: IS-10 offline tests created

### Validation
- [ ] **LANASTST-IP01-VC-07**: All offline test cases TC-01..13 pass
- [ ] **LANASTST-IP01-VC-08**: Manual: `/selftest` menu flow in Lana (scripted or live)
- [ ] **LANASTST-IP01-VC-09**: Manual: `selftest.py offline` green on dev checkout
- [ ] **LANASTST-IP01-VC-10**: Live run `selftest.py 04` within budget, results.json valid (user-approved spend)

## 8. Document History

**[2026-08-30 22:32]**
- Initial implementation plan created
- DC-01 resolves LANASTST-PR-0004 (interpreter discovery: LANA_PYTHON > .venv > PATH)

