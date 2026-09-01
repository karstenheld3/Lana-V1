# Session Problems

**Doc ID**: LANATEST-PROBLEMS

## Open

**LANATEST-PR-0001: Define "predictable outcome" for non-deterministic LLM outputs**
- **History**: Added 2026-08-30 18:46
- **Description**: LLM outputs vary across runs. Need an evaluation strategy that checks structural correctness (file existence, section presence, format compliance) rather than exact text matching.
- **Impact**: Without this, test pass/fail is unreliable and noisy.
- **Next Steps**: Research evaluation approaches: structural checks, rubric-based scoring, LLM-as-judge.

**LANATEST-PR-0002: Identify which workflows/skills qualify as "basic IPPS" for Bucket 2**
- **History**: Added 2026-08-30 18:46
- **Description**: User named verify, critique, reconcile, implement, drift-detect, drift-correct. Need to confirm full list and understand their expected inputs/outputs to design test prompts.
- **Impact**: Incomplete coverage means untested workflows.
- **Next Steps**: Inventory all workflows in `.lana/workflows/` and `.devin/workflows/`, categorize as basic vs. special.

**LANATEST-PR-0003: Golden output portability between Cascade and Lana**
- **History**: Added 2026-08-30 18:46
- **Description**: Reference outputs produced by Cascade + IPPS may contain Cascade-specific artifacts (tool names, system prompt references). Lana's outputs will differ in those details even when correct.
- **Impact**: Evaluation must abstract over agent-specific differences.
- **Next Steps**: Define which aspects of golden output are normative (structure, content quality) vs. incidental (tool names, formatting).

**LANATEST-PR-0004: Test isolation and workspace setup**
- **History**: Added 2026-08-30 18:46
- **Description**: Each test needs a clean, reproducible workspace. Bucket 1 needs an empty `.lana/`, Bucket 2 needs IPPS content in `.lana/`, Bucket 3 needs specific skills + possibly external resources (PDFs, URLs for transcribe, search APIs for deep-research).
- **Impact**: Without isolation, test results depend on prior state.
- **Next Steps**: Design workspace scaffold per bucket.

**LANATEST-PR-0005: Deep-research and transcribe tests need external resources**
- **History**: Added 2026-08-30 18:46
- **Description**: `deep-research.md` requires web search and URL fetching. `transcribe.md` requires PDF/web input. Tests must either use stable external resources or bundle local fixtures.
- **Impact**: Flaky tests if external resources change or become unavailable.
- **Next Steps**: Decide between stable public URLs, bundled fixtures, or mocked responses.

**LANATEST-PR-0006: Evaluation harness design**
- **History**: Added 2026-08-30 18:46
- **Description**: Need a runner that executes prompts (or prompt sequences) against an agent, captures the output folder structure, and compares against golden reference. Must support both Cascade (for generating golden output) and Lana (for evaluation).
- **Impact**: Core infrastructure for the entire test suite.
- **Next Steps**: Design harness architecture in EXPLORE phase.

## Resolved

**LANATEST-PR-0008: Eval suite leaves artifacts on disk outside runs_gitignore**
- **History**: Added 2026-09-01, Resolved 2026-09-01
- **Description**: Running Lana with eval prompts (e.g. 02-T01 WriteSpec) from outside the runner (e.g. from `dist/`) left `_SPEC_WORDCOUNT.md`, `.lana/`, `.lana-data/`, `config/` in the CWD. The runner's eval workdirs (inside `runs_gitignore/`) also leaked the real repo path via `find_git_root` walking up past the workdir to `E:\Dev\Lana-V1\.git`, exposing the repo path in the system prompt.
- **Resolution**: 1) `.git` sentinel directory created in each eval workdir by `copy_scaffold` (prevents `find_git_root` from walking past the sandbox); 2) `detect_workspace_escape` post-test check scans tool call events for paths outside the workdir and marks the test as error if found; 3) Cleaned `dist/` artifacts.
- **Prevention**: The `.git` sentinel ensures the LLM never learns the real repo path. The escape detector catches any future leak as a test error.

**LANATEST-PR-0007: Test environment broken after workspace folder rename**
- **History**: Added 2026-08-30 20:05, Resolved 2026-08-30 20:05
- **Description**: 1) The venv's editable install pointed at the old folder (`__editable__.lana-0.1.0.pth` → `E:\Dev\Lana-V1\src`) → `ModuleNotFoundError: lana`. 2) `src/lana/bundled/` was empty (cleaned by `_build.ps1` step 8) → 5 pre-existing failures in test_distribution.py/test_hardening.py.
- **Resolution**: `pip install -e . --no-deps` re-anchored the editable install; bundle re-synced via robocopy per `_build.ps1` step 2 (config trio + `.lana/` mirror). Full suite 265 green.
- **Prevention**: after renaming the workspace folder, re-run `pip install -e .`; before running distribution tests, ensure the bundle is synced.

## Deferred

- (none yet)

## Problems Changes

**[2026-08-30 18:46]**
- Added: LANATEST-PR-0001 through PR-0006 (initial problem derivation from session goal)
