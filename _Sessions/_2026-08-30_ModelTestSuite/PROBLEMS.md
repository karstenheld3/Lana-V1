# Session Problems

**Doc ID**: LANATEST-PROBLEMS

Track problems using ID format: `LANATEST-PR-[NNNN]`

## Open

**LANATEST-PR-0001: No test coverage for most available models**
- **History**: Added 2026-08-30 22:06
- **Description**: Only 3 models tested (claude-sonnet-4-5, claude-haiku-4-5, gpt-5-mini). Registry has 20 enabled+available models (15 OpenAI, 5 Anthropic); 17 have zero coverage.
- **Impact**: Regressions in adapter code for untested model families go undetected
- **Next Steps**: Create parametrized test reading from model-registry.json

**LANATEST-PR-0002: No effort parameter variant testing**
- **History**: Added 2026-08-30 22:06
- **Description**: Each model family supports different effort params (temperature, reasoning_effort, thinking_budget). Only one effort level tested per model.
- **Impact**: Effort-dependent code paths (e.g., reasoning_effort mapping, thinking budget calc) untested
- **Next Steps**: For one representative model per provider, test all supported effort levels

## Resolved

**LANATEST-PR-0004: Interpreter discovery for selftest.py in binary distribution**
- **History**: Added 2026-08-30 22:18 (found during /verify of LANATEST-SP01) | Resolved 2026-08-30 22:32
- **Description**: PyApp installs the lana wheel into a managed venv, not system Python. `python selftest.py` via run_command uses whatever `python` is on PATH -- `import lana` may fail in binary installs.
- **Fix**: `_IMPL_SELFTEST.md [LANATEST-IP01]` DC-01: workflow discovery order LANA_PYTHON env var > `.venv/Scripts/python.exe` > PATH python, each tested with `-c "import lana"`. Script import guard prints LANA_PYTHON hint, exit 3 (EC-03).

**LANATEST-PR-0003: Registry prefix dot/dash mismatch disables effort and adaptive_thinking methods**
- **History**: Added 2026-08-30 22:18 (found during /verify of LANATEST-SP01) | Resolved 2026-08-30 22:28
- **Description**: Prefix entries `claude-opus-4.5`, `claude-sonnet-4.5`, `claude-3.7`, `claude-3.5` in `model-registry.json` used dots, but model IDs use dashes -- `startswith()` never matched. Opus 4.5 lost its `effort` method + beta header, Haiku 4.5 fell to `claude-` fallback (temperature), Sonnet 4.6 had no dedicated entry.
- **Fix**: [ACTOR approved] Registry v1.7.1: dot prefixes -> dash (`claude-opus-4-5`, `claude-sonnet-4-5`, `claude-3-7`, `claude-3-5`), added `claude-haiku-4-5` (thinking) and `claude-sonnet-4-6` (adaptive_thinking, 1M context mirroring opus-4-7 pattern [ASSUMED - confirm effort levels against Anthropic docs]).
- **Verification**: [TESTED] `.tmp_verify_registry.py` -- all 20 available models resolve, all 5 methods represented, all 3 config JSONs valid. Offline pytest: 261 passed, 0 regressions.

## Deferred

**LANATEST-PR-0005: Pre-existing failures in bundle materialization tests (not session-caused)**
- **History**: Added 2026-08-30 22:28 (observed while verifying registry fix)
- **Description**: 5 tests fail (`test_distribution.py` TC-12..15, `test_hardening.py` TC-01) because `src/lana/bundled/agent/` and `bundled/config/` are empty -- `_build.ps1` step 8 cleans them after build. Tests require a synced bundle. Failures reproduced with unmodified registry (pre-existing).
- **Impact**: `pytest -m "not live"` is red on a fresh checkout until a build syncs the bundle
- **Next Steps**: Out of session scope -- sync to workspace !PROBLEMS.md on /session-finalize
