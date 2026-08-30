# SPEC: Selftest Framework

**Doc ID**: LANATEST-SP01
**Goal**: Specify a `/selftest` workflow that ships with the prompt system and validates Lana's environment, configuration, prompt system, and models via a deterministic runner script with a selectable test category menu
**Timeline**: Created 2026-08-30

**Target file(s)**:
- `.lana/workflows/selftest.md`
- `.lana/skills/selftest/SKILL.md`
- `.lana/skills/selftest/selftest.py`

**Depends on:**
- `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` for adapter protocol, config resolution, tool definitions
- `config/model-registry.json` for model catalog (runtime input)
- `config/model-parameter-mapping.json` for effort translation (runtime input)
- `config/model-pricing.json` for cost computation (runtime input)

## MUST-NOT-FORGET

- Zero changes to `src/lana/` -- selftest lives entirely in the prompt system
- Script imports from the installed `lana` package -- no code duplication
- Budget cap must be enforced before each test, not after
- Models with missing API keys are skipped, not failed
- Cost tracking uses the same formula as `lana.cost.CostTracker`

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
11. [Logging Requirements](#11-logging-requirements)
12. [Technical Constraints](#12-technical-constraints)
13. [Document History](#13-document-history)

## 1. Scenario

**Problem:** Users and developers have no one-command health check for a Lana installation. Model coverage is the most acute gap: the registry contains ~50 models, only 3 are tested via existing live smoke tests (TC-40..42 in `test_adapters.py`). But installation problems are broader: missing API keys, malformed config files, broken prompt system folders, unreachable provider APIs -- each surfaces only when a user hits it mid-session.

**Solution:**
- Ship a `/selftest` workflow in the prompt system (`.lana/`)
- The workflow instructs Lana to run a deterministic Python script (`selftest.py`) that imports from the installed `lana` package
- The script organizes checks into selectable test categories with numeric codes, shown as a menu
- Free offline categories (environment, configuration, prompt system) run without API calls; live model categories (sweep, effort matrix, tool calls) cost real tokens and are selected explicitly
- Budget cap prevents runaway costs on live categories
- Category list is extensible -- future categories (e.g., session storage integrity, ACP handshake) plug into the same menu

**What we don't want:**
- Changes to `src/lana/` -- Lana stays lean, the selftest is a prompt system artifact
- Agent-improvised tests -- the script is deterministic, the agent only runs it and reports output
- Full agent loop testing -- that belongs in `evals/`. Selftest validates infrastructure, not agent behavior.
- Hard-coded model lists in the script -- model discovery is dynamic from the registry
- Running live (paid) categories implicitly -- `all` without confirmation of cost, or model tests bundled into a default run

## 2. Context

Lana uses two provider adapters (`OpenAIAdapter`, `AnthropicAdapter`) behind a common `ProviderAdapter` protocol. Each adapter implements `stream_turn()` returning `AsyncIterator[AdapterDelta]`. The config system resolves model IDs to `ResolvedRole` objects containing provider, method, effort params, and token limits.

The existing `config/model-registry.json` defines models with `enabled` and `status` fields. The `model_id_startswith` section maps model families to parameter methods (temperature, reasoning_effort, thinking, adaptive_thinking, effort). The `config/model-parameter-mapping.json` translates effort levels to provider-specific call parameters.

Existing live smoke tests (`@pytest.mark.live` in `test_adapters.py`) cover one model per provider with one effort level each. They are sufficient for CI gating but not for model validation.

The `.lana/` prompt system already ships with the binary via `_build.bat`. Adding files to `.lana/skills/selftest/` requires no build pipeline changes.

## 3. Domain Objects

### Test Category

A selectable unit in the selftest menu. Each category has a two-digit code, a name, a cost class, and a runner.

**Built-in categories:**
- `01` - **Environment** (offline, free): Python version, Lana version, platform, `.lana-data/` writable, provider API endpoints reachable
- `02` - **Configuration** (offline, free): `lana-config.json` valid, all roles resolve, registry/mapping/pricing parse, API keys present, pricing coverage for enabled models
- `03` - **Prompt System** (offline, free): `.lana/` folder structure present, workflows parseable, each skill folder contains `SKILL.md`
- `04` - **Model Sweep** (live, ~$0.10): one round trip per available model
- `05` - **Model Effort Matrix** (live, ~$0.20): representative model per method, all effort levels
- `06` - **Model Tool Calls** (live, ~$0.05): function calling round trip per provider

**Key properties:**
- `code` - two-digit selector (e.g., `04`)
- `name` - menu display name
- `cost_class` - `offline` (free) or `live` (paid API calls)
- Categories are independent: any subset can run in any order

### Testable Model

A model from the registry that passes all filters: `enabled: true`, `status: available`, matching `model_id_startswith` prefix entry exists, and API key present for its provider.

**Key properties:**
- `model_id` - registry identifier (e.g., `gpt-5-mini`)
- `name` - human-readable name (e.g., `GPT-5 Mini`)
- `provider` - `openai` or `anthropic`
- `method` - parameter method from prefix entry (temperature, reasoning_effort, thinking, adaptive_thinking, effort)
- `default_effort` - the effort level used for sweep tests

### Test Result

The outcome of a single test case.

**Key properties:**
- `category` - category code (e.g., `04`)
- `check` - check identifier within the category (e.g., model_id for model tests, `keys_present` for configuration)
- `effort` - effort level used (model tests only)
- `status` - `pass`, `fail`, `skip`, `error`
- `duration_seconds` - wall clock time
- `usage` - token counts (input, output, cache_read)
- `cost_usd` - computed cost for this test
- `error_message` - populated on fail/error

### Run Report

Aggregated results from a selftest invocation.

**Storage:** `.lana-data/selftest/YYYY-MM-DD_HH-MM-SS/`

**Key properties:**
- `results.json` - machine-readable full results
- stdout output - human-readable progress and summary (Lana captures and displays)

## 4. Functional Requirements

**LANATEST-FR-01: Test Category Menu**
- Invoked with no arguments (or `--menu`), the script prints the category menu: code, name, cost class, estimated cost for live categories
- Menu is generated from the category list in the script -- adding a category automatically extends the menu
- The workflow instructs Lana to present the menu to the user and ask which categories to run

**LANATEST-FR-02: Category Selection by Code**
- Accept category codes as positional arguments: `selftest.py 01 02 04`
- Accept `all` for every category; `offline` for all free categories; `live` for all paid categories
- Invalid code: print error with valid codes, exit code 2
- Selected categories run in ascending code order

**LANATEST-FR-03: Environment Category (01)**
- Check Python version meets Lana's requirement (3.12+)
- Report Lana package version
- Check `.lana-data/` exists or is creatable and writable
- Check provider API endpoints reachable (TCP/TLS connect, no authenticated call)

**LANATEST-FR-04: Configuration Category (02)**
- Load and validate `lana-config.json` (schema validation)
- Resolve every configured role against registry + mapping
- Verify registry, mapping, and pricing files parse
- Report API key presence per provider (present/missing, never print key material)
- Report enabled registry models missing from pricing file (warning, not failure)

**LANATEST-FR-05: Prompt System Category (03)**
- Verify `.lana/` contains `rules/`, `workflows/`, `skills/` folders
- Verify every workflow file has a parseable frontmatter/description
- Verify every skill folder contains `SKILL.md`

**LANATEST-FR-06: Dynamic Model Discovery**
- Read `config/model-registry.json` at runtime
- Filter: `enabled == true` AND `status == "available"`
- Match each model to its `model_id_startswith` prefix entry
- Skip models with no matching prefix (log warning)
- Skip models whose provider has no API key (status: `skip`, not `fail`)

**LANATEST-FR-07: Model Sweep Category (04)**
- For each testable model: send a minimal text prompt, consume the full response stream
- Verify: at least one `text` delta received, `usage` delta received with `input_tokens > 0`
- Use the `default` effort from the prefix entry, falling back to `medium`

**LANATEST-FR-08: Model Effort Matrix Category (05)**
- Select one representative model per distinct method type among testable models
- Representative selection: prefer the cheapest available model in each method family
- For each representative: test every effort level listed in the prefix entry's `effort` array; when the prefix entry has no `effort` array (temperature, thinking methods), test `low`, `medium`, `high`
- Verify: response received, no error, usage reported

**LANATEST-FR-09: Model Tool Call Category (06)**
- Select one model per provider (prefer the model configured as `generator` in `lana-config.json`, falling back to cheapest available)
- Send a prompt that requires a tool call (a `read_file` call with a specific path)
- Provide one tool definition matching Lana's `read_file` schema
- Verify: `tool_call` delta received with `name == "read_file"`, arguments parseable as JSON
- Send tool result back, verify final `text` delta received

**LANATEST-FR-10: Budget Cap (live categories)**
- Accept a `--budget` argument (float, USD). Default: `5.00`
- Before each live test case: check cumulative cost so far. If remaining budget < $0.01, skip all remaining live tests with status `budget_exceeded`
- Use `model-pricing.json` rates and the same cost formula as `lana.cost`

**LANATEST-FR-11: Model Filtering (live categories)**
- `--provider openai|anthropic` - test only models from one provider
- `--model <model_id>` - test a single model (sweep-style, default effort)
- Filters combine with category codes: `selftest.py 04 --provider openai` runs only the OpenAI sweep

**LANATEST-FR-12: Results Output**
- Write `results.json` to `.lana-data/selftest/YYYY-MM-DD_HH-MM-SS/`
- Print progress and summary to stdout (Lana captures via `run_command`)
- Exit code: 0 = all passed/skipped, 1 = any failed/errored

**LANATEST-FR-13: Timeout Per Test**
- Default: 60 seconds per model call
- Accept `--timeout` argument (integer, seconds)
- On timeout: status `fail`, error message includes duration

**LANATEST-FR-14: Workflow Integration**
- `/selftest` in Lana invokes the workflow
- `/selftest` without arguments: workflow runs the menu, presents categories to the user, asks for selection
- `/selftest <codes|all|offline|live>` with arguments: workflow maps them to script arguments and runs directly
- Workflow reads the skill, then runs: `python <skill_path>/selftest.py [args]`
- Lana displays script stdout, then summarizes pass/fail/skip counts and total cost
- Before running `live` or `all`: workflow states the estimated cost to the user

## 5. Non-Functional Requirements

**LANATEST-NFR-01: Performance - Serial Execution**
- Tests run sequentially (one model at a time) to avoid rate limits and simplify cost tracking

**LANATEST-NFR-02: Cost - Minimal Token Usage** [ASSUMED - verify on first live run]
- Sweep prompt: ~20 tokens input, expect ~20-50 tokens output per model
- Estimated sweep cost for 20 models: < $0.10
- Effort matrix (~3 methods x 3-4 efforts): < $0.20
- Tool call suite (2 models, 2 turns each): < $0.05
- Total estimated full run: < $0.50

**LANATEST-NFR-03: Reliability - Retry on Transient Failures**
- Use the same retryable status codes as `lana.providers.base` (408, 429, 500, 502, 503, 504)
- One retry with 3-second delay on transient failure. Second failure = test fails.

## 6. Design Decisions

**LANATEST-DD-01:** Selftest lives in the prompt system (`.lana/skills/selftest/`), not in `src/lana/`. Rationale: keeps Lana lean, ships automatically with the prompt library, extensible without code changes.

**LANATEST-DD-02:** Script imports from installed `lana` package (`lana.config`, `lana.providers.*`, `lana.models`, `lana.cost`). Rationale: reuses existing config resolution, adapter creation, and cost computation. No code duplication.

**LANATEST-DD-03:** Agent is the intermediary -- Lana reads script output and reports to user. The script is deterministic. Rationale: script reliability over agent improvisation for infrastructure validation.

**LANATEST-DD-04:** Sweep uses default effort per model, not medium. Rationale: tests the model at its intended operating point. Default effort comes from the prefix entry's `default` field, falling back to `medium`.

**LANATEST-DD-05:** Effort matrix picks the cheapest model per method, not the most capable. Rationale: effort translation is identical across models in the same method family -- testing the cheapest one validates the code path at minimal cost.

**LANATEST-DD-06:** Tool call category uses the configured generator model per provider when available. Rationale: validates the exact model the user is working with, catching misconfigurations.

**LANATEST-DD-07:** Serial execution, no parallelism. Rationale: rate limit safety, deterministic cost accumulation, simpler script.

**LANATEST-DD-08:** Results written to `.lana-data/selftest/` (runtime data dir), not `.lana/` (prompt system). Rationale: `.lana/` is configuration; `.lana-data/` is runtime artifacts.

**LANATEST-DD-09:** Selftest is a category framework, model testing is categories 04-06. Rationale: one `/selftest` entry point for all installation health checks; future categories (session storage, ACP handshake) extend the menu without new workflows.

**LANATEST-DD-10:** Offline categories (01-03) never make authenticated API calls and never cost money. Live categories (04-06) require explicit selection. Rationale: safe default -- a user exploring `/selftest` cannot accidentally spend tokens.

## 7. Implementation Guarantees

**LANATEST-IG-01:** Budget cap checked before each test, never exceeded by more than one test's cost.

**LANATEST-IG-02:** Missing API key for a provider causes skip (not crash) for all that provider's models.

**LANATEST-IG-03:** Script exit code is 0 only when zero tests have status `fail` or `error`. Skips do not affect exit code.

**LANATEST-IG-04:** `results.json` is written even on partial runs (budget exceeded, Ctrl+C). The file reflects all tests completed up to that point.

**LANATEST-IG-05:** `results.json` is always valid JSON regardless of how many tests completed.

## 8. Key Mechanisms

### Config Resolution

The script reuses `lana.config.load_lana_config()` with `require_keys=False` to load registry, mapping, and pricing without failing on missing keys. API keys are resolved separately per provider via `lana.config.resolve_key()` and `lana.config.parse_key_file()`.

### Adapter Creation

For each provider with a valid key, the script creates one adapter instance (`OpenAIAdapter` or `AnthropicAdapter`). Adapter instances are reused across all tests for that provider.

### Role Construction

For each test case, the script calls `lana.config.resolve_role()` with a synthetic role spec (model ID + effort level) to get a fully resolved `ResolvedRole` with correct method, params, and token limits.

### Stream Consumption

Each test calls the adapter's `stream_turn()` and collects all `AdapterDelta` objects. The async iterator is consumed to completion per test.

### Cost Computation

Per-test cost uses the same formula as `lana.cost.CostTracker.turn_cost()`: look up rates by `(provider, model_id)` in `model-pricing.json`, compute `(input - cache_read) * input_rate + cache_read * cached_rate + output * output_rate`.

## 9. Action Flow

```
User types /selftest (no arguments)
├─> Lana reads .lana/workflows/selftest.md
│   └─> Workflow invokes selftest skill
│       ├─> run_command python .lana/skills/selftest/selftest.py --menu
│       ├─> Lana presents menu to user, asks for category selection
│       └─> User answers (e.g., "01 02 04")
│           └─> continue as below with selected codes

User types /selftest 01 02 04 (or all | offline | live)
├─> Lana reads .lana/workflows/selftest.md
│   ├─> live/all selected: Lana states estimated cost first (FR-14)
│   └─> run_command python .lana/skills/selftest/selftest.py 01 02 04
│       ├─> selftest.py loads config (registry, mapping, pricing, keys)
│       ├─> Runs selected categories in ascending code order
│       │   ├─> Offline categories: local checks, no API calls
│       │   ├─> Live categories: discover models (FR-06), per test resolve role,
│       │   │   create/reuse adapter, stream_turn, verify, record
│       │   ├─> Budget check before each live test (FR-10)
│       │   └─> Progress printed to stdout as checks complete
│       ├─> Writes results.json to .lana-data/selftest/
│       └─> Exits with code 0 (all pass/skip) or 1 (any fail/error)
└─> Lana reads stdout, summarizes results to user
```

## 10. Data Structures

### results.json

```json
{
  "timestamp": "2026-08-30T22:15:00",
  "lana_version": "1.1.0",
  "categories_run": ["01", "02", "04"],
  "budget_usd": 5.0,
  "cost_usd": 0.0234,
  "duration_seconds": 45.2,
  "summary": {"pass": 19, "fail": 1, "skip": 2, "error": 0, "budget_exceeded": 0},
  "tests": [
    {
      "category": "01",
      "check": "python_version",
      "status": "pass",
      "duration_seconds": 0.0,
      "error_message": null
    },
    {
      "category": "04",
      "check": "gpt-5-mini",
      "model_id": "gpt-5-mini",
      "name": "GPT-5 Mini",
      "provider": "openai",
      "method": "reasoning_effort",
      "effort": "medium",
      "status": "pass",
      "duration_seconds": 1.3,
      "usage": {"input_tokens": 127, "output_tokens": 23, "cache_read_tokens": 0},
      "cost_usd": 0.0012,
      "error_message": null
    }
  ]
}
```

### Menu Output

```
SELFTEST MENU
  01  Environment          offline  free
  02  Configuration        offline  free
  03  Prompt System        offline  free
  04  Model Sweep          live     ~$0.10 (20 models)
  05  Model Effort Matrix  live     ~$0.20 (3 methods)
  06  Model Tool Calls     live     ~$0.05 (2 models)

Usage: selftest.py <codes...> | all | offline | live [--provider P] [--model M] [--budget N] [--timeout S]
```

### Minimal Test Prompt

Sweep and effort categories use a fixed system prompt and user message:

- **System**: `"You are a test agent. Respond with exactly: SELFTEST OK"`
- **User**: `"Respond now."`
- **Tools**: empty list (sweep/effort) or single `read_file` tool (tool call category)

### Tool Call Test Messages

The tool call category sends two turns:

- **Turn 1**: system + user message requesting a tool call + one tool definition
- **Turn 2**: turn 1 messages + assistant response with tool_call + tool result message

## 11. Logging Requirements

**Applicable type:** Script-Level (SC) -- selftest.py is a verification script.

**Script-Level (SC):**
- **Audience**: User running `/selftest` via Lana, or developer running `selftest.py` directly
- **Goal**: Know which checks passed, which failed and why, total cost
- **Key operations**: category start, per-check progress, category summary, run result

**Expected output for a run of categories 01, 02, 04:**
```
SELFTEST: 01 Environment
  python_version: 3.12.6...OK | lana_version: 1.1.0 | data_dir: writable...OK
  api.openai.com: reachable...OK | api.anthropic.com: reachable...OK
  01 Environment: 4 passed.

SELFTEST: 02 Configuration
  lana-config.json: valid...OK | roles: 3 resolved...OK
  keys: openai present, anthropic present...OK
  pricing: 20 of 20 enabled models priced...OK
  02 Configuration: 4 passed.

SELFTEST: 04 Model Sweep (15 OpenAI, 5 Anthropic) | Budget: $5.00
  [ 1 / 20 ] gpt-5.6-sol (reasoning_effort, none)...
    OK. 127in/23out $0.0012 1.3s
  [ 2 / 20 ] gpt-5.6-terra (reasoning_effort, none)...
    OK. 131in/19out $0.0011 1.1s
  ...
  [ 16 / 20 ] claude-sonnet-4-5 (thinking, medium)...
    OK. 145in/31out $0.0008 2.1s
  [ 17 / 20 ] claude-opus-4-5 (thinking, medium)...
    FAIL: timeout after 60s
  ...
  04 Model Sweep: 19 passed, 1 failed, 0 skipped.

RESULT: 27 passed, 1 failed, 0 skipped. Cost: $0.0198.
Results: .lana-data/selftest/2026-08-30_22-15-00/results.json
```

## 12. Technical Constraints

- Script requires `lana` package importable by the invoking Python interpreter
- [ASSUMED] Binary distribution: PyApp installs the wheel into a managed venv, NOT the system Python -- plain `python` on PATH may not import `lana`. Interpreter discovery strategy must be defined in IMPL (see LANATEST-PR-0004)
- Script requires network access to provider APIs
- Script requires API keys for tested providers (env vars or `config/.api-keys.txt`)
- Script reuses `lana.providers.base.PROVIDER_TIMEOUT` for HTTP timeouts
- Adapter creation requires provider SDK packages (`openai`, `anthropic`) -- these are Lana dependencies
- `.lana-data/` directory must be writable (created by Lana's zero-setup if missing)
- Workflow runs the script via Lana's `run_command` tool -- subject to execution policy (manual/auto/turbo)

## 13. Document History

**[2026-08-30 22:22]**
- Changed: generalized from model-only test to selftest framework with category menu (codes 01-06)
- Added: offline categories 01 Environment, 02 Configuration, 03 Prompt System (FR-03..05)
- Added: FR-01 menu, FR-02 category selection, DD-09 category framework, DD-10 offline/live cost safety
- Changed: model tests became categories 04-06, FRs renumbered (FR-01..09 -> FR-06..09 for model concerns)
- Changed: results.json and log examples restructured per category

**[2026-08-30 22:18]**
- Fixed: log examples used method `effort` for claude-opus-4-5 -- registry prefix `claude-opus-4.5` (dot) never matches model ID `claude-opus-4-5-20251101` (dash), model resolves to `thinking` (LANATEST-PR-0003)
- Fixed: effort matrix example corrected to 3 methods (only temperature, reasoning_effort, thinking have available models)
- Changed: FR-03 defines low/medium/high default when prefix entry has no effort array
- Changed: Technical Constraints -- binary scenario importability marked [ASSUMED], interpreter discovery deferred to IMPL (LANATEST-PR-0004)
- Changed: Key Mechanisms -- removed function parameter lists (SPEC-CT-02)
- Changed: IG-05 reworded, NFR-02 labeled [ASSUMED]

**[2026-08-30 22:14]**
- Initial specification created

