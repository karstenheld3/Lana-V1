# Session Problems

**Doc ID**: LANATEST-PROBLEMS

Track problems using ID format: `LANATEST-PR-[NNNN]`

## Open

## Resolved

**LANATEST-PR-0001: No test coverage for most available models**
- **History**: Added 2026-08-30 22:06 | Resolved 2026-08-30 22:44
- **Description**: Only 3 models tested. Registry has 20 enabled+available models (15 OpenAI, 5 Anthropic); 17 had zero coverage.
- **Fix**: `/selftest` category 04 (Model Sweep) round-trips every enabled+available model dynamically from the registry. [PROVEN] Live-verified on common models: gpt-5-nano, gpt-5-mini, gpt-4.1-mini, gpt-4o-mini, claude-sonnet-4-5, claude-haiku-4-5, claude-sonnet-4-6 -- all pass. Full 20-model sweep available via `selftest.py 04`.

**LANATEST-PR-0002: No effort parameter variant testing**
- **History**: Added 2026-08-30 22:06 | Resolved 2026-08-30 22:44
- **Description**: Each model family supports different effort params. Only one effort level tested per model.
- **Fix**: `/selftest` category 05 (Effort Matrix) tests cheapest model per method at every supported effort level. [PROVEN] Live run: 5 methods, 18 effort combinations, 17 pass + 1 registry correction (sonnet-4-6 xhigh unsupported -- fixed in registry v1.7.2, re-run 4/4 pass).

**LANATEST-PR-0004: Interpreter discovery for selftest.py in binary distribution**
- **History**: Added 2026-08-30 22:18 (found during /verify of LANATEST-SP01) | Resolved 2026-08-30 22:32
- **Description**: PyApp installs the lana wheel into a managed venv, not system Python. `python selftest.py` via run_command uses whatever `python` is on PATH -- `import lana` may fail in binary installs.
- **Fix**: `_IMPL_SELFTEST.md [LANATEST-IP01]` DC-01: workflow discovery order LANA_PYTHON env var > `.venv/Scripts/python.exe` > PATH python, each tested with `-c "import lana"`. Script import guard prints LANA_PYTHON hint, exit 3 (EC-03).

**LANATEST-PR-0003: Registry prefix dot/dash mismatch disables effort and adaptive_thinking methods**
- **History**: Added 2026-08-30 22:18 (found during /verify of LANATEST-SP01) | Resolved 2026-08-30 22:28
- **Description**: Prefix entries `claude-opus-4.5`, `claude-sonnet-4.5`, `claude-3.7`, `claude-3.5` in `model-registry.json` used dots, but model IDs use dashes -- `startswith()` never matched. Opus 4.5 lost its `effort` method + beta header, Haiku 4.5 fell to `claude-` fallback (temperature), Sonnet 4.6 had no dedicated entry.
- **Fix**: [ACTOR approved] Registry v1.7.1: dot prefixes -> dash (`claude-opus-4-5`, `claude-sonnet-4-5`, `claude-3-7`, `claude-3-5`), added `claude-haiku-4-5` (thinking) and `claude-sonnet-4-6` (adaptive_thinking, 1M context mirroring opus-4-7 pattern [ASSUMED - confirm effort levels against Anthropic docs]).
- **Verification**: [PROVEN] All 20 available models resolve, all 5 methods represented. Live effort matrix confirmed opus-4-5 `effort` method with beta header and sonnet-4-6 `adaptive_thinking`. Correction from live run: sonnet-4-6 supports low/medium/high/max but NOT xhigh -- registry v1.7.2 removed it (API error message was the source).

## Deferred

**LANATEST-PR-0005: Pre-existing failures in bundle materialization tests (not session-caused)**
- **History**: Added 2026-08-30 22:28 (observed while verifying registry fix)
- **Description**: 5 tests fail (`test_distribution.py` TC-12..15, `test_hardening.py` TC-01) because `src/lana/bundled/agent/` and `bundled/config/` are empty -- `_build.ps1` step 8 cleans them after build. Tests require a synced bundle. Failures reproduced with unmodified registry (pre-existing).
- **Impact**: `pytest -m "not live"` is red on a fresh checkout until a build syncs the bundle
- **Next Steps**: Out of session scope -- sync to workspace !PROBLEMS.md on /session-finalize
