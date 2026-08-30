---
description: Run Lana selftest - environment, configuration, prompt system, and model health checks
---

# Selftest Workflow

Run the deterministic selftest script and report results. Model tests cost real API tokens - offline categories are free.

## Required Skills

- `skills/selftest/SKILL.md` - script contract, categories, exit codes

## MUST-NOT-FORGET

- The script is deterministic - run it and report its output. Never improvise your own model tests.
- Live categories (04-06) cost money. State the estimated cost BEFORE running them.
- Never print API key material.

## Step 1: Discover Interpreter

Find a Python interpreter that can import lana. Test candidates in this order with `<python> -c "import lana"`:

1. `$env:LANA_PYTHON` (if set)
2. `.venv/Scripts/python.exe` (dev checkout, Windows) or `.venv/bin/python` (POSIX)
3. `python` on PATH

If none works: report to the user with this hint - "Set LANA_PYTHON to the interpreter that runs Lana (binary installs use a PyApp-managed venv)." STOP.

## Step 2: Parse Arguments

- `/selftest` (no arguments) -> run `<python> .lana/skills/selftest/selftest.py --menu`, show the menu to the user, ask which categories to run. Wait for the answer.
- `/selftest <codes|all|offline|live> [options]` -> map user words directly to script arguments. Category names also work: "models" -> `04 05 06`, "environment" -> `01`.

## Step 3: Cost Gate for Live Categories

If the selection includes any of 04, 05, 06 (or `live`, `all`):
- State the estimated cost from the menu (e.g. "This runs live model tests, estimated ~$0.35 total.")
- Include `--budget 5.00` default or the user-provided budget.

## Step 4: Run

```
<python> .lana/skills/selftest/selftest.py <codes> [--provider P] [--model M] [--budget N] [--timeout S]
```

Run blocking from the workspace root. The script prints progress per category and writes `results.json` to `.lana-data/selftest/<timestamp>/`.

## Step 5: Report

Summarize for the user:
- Pass/fail/skip counts per category and total
- Total cost
- Every FAIL with its error message
- Path to `results.json`

Exit codes: 0 = all pass/skip, 1 = failures, 2 = invalid arguments, 3 = environment problem (import, data dir).
