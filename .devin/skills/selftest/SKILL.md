# Skill: Selftest

Deterministic health checks for a Lana installation. Invoked by the `/selftest` workflow.

## Purpose

Validate environment, configuration, prompt system, and model connectivity with one command. Model categories double as the model validation suite: every enabled+available registry model can be round-tripped.

## Categories

- **01 Environment** (offline, free): Python >= 3.12, Lana version, `.lana-data/` writable, provider endpoints reachable (TLS connect, no auth)
- **02 Configuration** (offline, free): `lana-config.json` valid, roles resolve, registry/mapping/pricing parse, API keys present, pricing coverage
- **03 Prompt System** (offline, free): `.lana/` folders, workflow frontmatter, `SKILL.md` per skill
- **04 Model Sweep** (live, ~$0.10): one round trip per available model at default effort
- **05 Model Effort Matrix** (live, ~$0.20): cheapest model per parameter method, all supported effort levels
- **06 Model Tool Calls** (live, ~$0.05): read_file function-calling round trip per provider

## Script Contract

```
selftest.py --menu
selftest.py <codes...> | all | offline | live [--provider openai|anthropic] [--model ID] [--budget USD] [--timeout SECONDS]
```

- Runs from the workspace root (uses cwd; honors `LANA_CONFIG` env var like Lana itself)
- Categories run in ascending code order, serially
- Budget (default $5.00) checked BEFORE each live test; exceeding tests get status `budget_exceeded`
- Results: stdout progress + `.lana-data/selftest/<YYYY-MM-DD_HH-MM-SS>/results.json` (written even on interrupt)

**Exit codes:**
- 0 - all tests pass or skip
- 1 - at least one fail or error
- 2 - invalid arguments
- 3 - environment problem (lana not importable, data dir not writable)

## Interpreter

The script imports the installed `lana` package. Run it with the interpreter that runs Lana:
- Dev checkout: `.venv/Scripts/python.exe`
- pip install: `python` on PATH
- Binary (PyApp): set `LANA_PYTHON` to the managed-venv interpreter

## Files

- `selftest.py` - runner script (all categories, menu, budget, results)
