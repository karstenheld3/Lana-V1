# Session Notes

**Doc ID**: LANATEST-NOTES

## Initial Request

````text
I want to test all models in model-registry.json that are available.

1. We need to add smoke tests for default models -> Dont we have this already?
2. We need a separate test suite that tests all available models and one (most used) of each provider with all reasoning effort params

Note and stop
````

## Session Info

- **Started**: 2026-08-30
- **Goal**: Create a comprehensive model test suite covering all available models in model-registry.json and effort parameter variants
- **Operation Mode**: IMPL-CODEBASE
- **Output Location**: `.lana/workflows/` + `.lana/skills/selftest/`

## Existing Coverage (from investigation)

`tests/test_adapters.py` has 4 live smoke tests (all behind `@pytest.mark.live`):
- **TC-40**: OpenAI function round trip (hardcoded `claude-sonnet-4-5`, temperature method)
- **TC-41**: Anthropic round trip + cache hit (hardcoded `claude-sonnet-4-5`, thinking method)
- **TC-42**: OpenAI reasoning model tool call (hardcoded `gpt-5-mini`, reasoning_effort method)
- **Anthropic web search**: Hardcoded `claude-haiku-4-5`, thinking method

These test ONE model per provider with ONE method each. They do NOT:
- Test all `enabled: true, status: available` models from model-registry.json
- Test all reasoning effort params (low/medium/high) per model
- Parametrize across the registry

## What Needs to Be Built

1. **Default model smoke tests** (answer to question 1): Already exist in `test_adapters.py` TC-40..42. They cover the happy path for one model per provider. These are sufficient for CI/default smoke.

2. **`/selftest` framework: workflow + skill** (chosen design - Option E, generalized):
   - Ships as part of the prompt system (`.lana/`), zero changes to `src/lana/`
   - Workflow: `.lana/workflows/selftest.md`
   - Skill: `.lana/skills/selftest/` with `SKILL.md` + `selftest.py` runner script
   - `selftest.py` imports from `lana.config` and `lana.providers.*` (already installed)
   - Category menu with codes: 01 Environment, 02 Configuration, 03 Prompt System (offline/free); 04 Model Sweep, 05 Model Effort Matrix, 06 Model Tool Calls (live/paid)
   - Usage: `/selftest` (menu), `/selftest 01 02 04`, `/selftest all|offline|live`, plus `--provider`, `--model`, `--budget`, `--timeout`
   - Results to `.lana-data/selftest/`

## Key Decisions

- **LANATEST-DD-01**: `/selftest` lives entirely in the prompt system (`.lana/`), not in `src/lana/`. Rationale: keeps Lana lean, ships with prompt library, extensible without code changes.
- **LANATEST-DD-02**: Test scripts import from installed `lana` package. Rationale: adapter layer and config resolution already exist, no duplication needed.
- **LANATEST-DD-03**: Agent acts as intermediary (reads script output, reports to user). The script itself is deterministic.
- **LANATEST-DD-09**: Selftest is a category framework -- model testing is categories 04-06, future categories extend the menu.
- **LANATEST-DD-10**: Offline categories free and safe by default; live categories require explicit selection.

## Important Findings

- 20 models with `enabled: true, status: available` in current registry (15 OpenAI, 5 Anthropic) [VERIFIED against registry v1.7.0]
- Registry bug found during /verify: prefix dot/dash mismatch disables `effort` and `adaptive_thinking` methods (LANATEST-PR-0003)
- Binary distribution (PyApp managed venv) requires interpreter discovery for selftest.py (LANATEST-PR-0004)
- Each live test costs real API tokens -- budget awareness needed
- The `model_id_startswith` section defines method/params per model family -- this is the parametrization source for effort variants
- Existing live smoke tests (TC-40..42) cover 3 models with 1 effort each -- sufficient for CI, not for model validation
- `_build.bat` already bundles `.lana/` into the binary -- selftest ships automatically

## Topic Registry

**Global topics** (registered in ID-REGISTRY.md):
- `LANATEST` - Lana External Test Suite

## Topic Folders

- (none)

## Step Folders

- (none)

## Bug List

- (none yet)

## Housekeeping

- `_SPEC_SELFTEST.md`, `_IMPL_SELFTEST.md`, `_TEST_SELFTEST.md` moved to `specs/` (2026-09-01) - central specs folder per workspace convention

## Significant Prompts Log

- (none yet)
