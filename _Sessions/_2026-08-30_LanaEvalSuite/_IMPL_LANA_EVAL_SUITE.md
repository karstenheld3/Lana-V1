# IMPL: Lana Eval Suite - Minimal Working Version (MVP)

**Doc ID**: LANATEST-IP01
**Feature**: eval-suite-mvp
**Goal**: Build a working-but-incomplete eval suite (runner, Tier 1-3 evaluators, one to two tests per bucket) that can be test-driven immediately.
**Timeline**: Created 2026-08-30

**Target file(s)**:
- `evals/suite/runner/run_evals.py` (NEW - discovery, execution, recording, report)
- `evals/suite/runner/evaluators.py` (NEW - Tier 1 structure + Tier 2 process)
- `evals/suite/runner/judge.py` (NEW - Tier 3 via @skills:llm-evaluation `call-llm.py`)
- `evals/suite/runner/runner-config.json` (NEW - paths, judge model, defaults)
- `evals/suite/runner/judge_prompt_template.md` (NEW)
- `evals/suite/01_Basics/T01_CreateFile/`, `T02_EditSequence/` (NEW test cases)
- `evals/suite/02_WorkflowsSkills/T01_WriteSpec/` (NEW test case)
- `evals/suite/03_AdvancedCapabilities/T01_TranscribeLocal/` (NEW test case)

**Depends on:**
- `_SPEC_LANA_EVAL_SUITE.md [LANATEST-SP01]` for architecture, domain objects, FRs
- `specs/_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` FR-12 prompt queue [PROVEN 2026-08-30]
- `@skills:llm-evaluation` for the Tier 3 judge (`call-llm.py`, model registry, effort levels)

**Does not depend on:**
- `tests/` unit suite (the runner spawns the installed `lana`, not the harness)

## MUST-NOT-FORGET

- MVP scope: functionality over exhaustiveness - one thin vertical slice per component
- The agent under test never sees `expected/`, `golden/`, `TEST.md` (LANATEST-IG-01): only `workspace/` content is copied to the working directory
- No API keys in run records (LANATEST-NFR-03): Lana config stays OUTSIDE the test workspace via `LANA_CONFIG`
- Tier 3 judge = @skills:llm-evaluation `call-llm.py` (user decision 2026-08-30) - no custom LLM client
- Runner writes only under `evals/runs/` (LANATEST-IG-03)

## Table of Contents

1. [Impact Analysis](#1-impact-analysis)
2. [MVP Decisions](#2-mvp-decisions)
3. [File Structure](#3-file-structure)
4. [Judge Integration (llm-evaluation)](#4-judge-integration-llm-evaluation)
5. [Edge Cases](#5-edge-cases)
6. [STRUT Plan](#6-strut-plan)
7. [Test Cases](#7-test-cases)
8. [Verification Checklist](#8-verification-checklist)
9. [Document History](#9-document-history)

## 1. Impact Analysis

- **New code only**: everything lives under `evals/suite/` - zero changes to `src/lana/` or `tests/`
- **Consumes**: `lana --prompt-file` (LANAACPB-FR-12, proven), session JSONL event contract (LANAAGNT-FR-08), `lana.events.from_jsonl` (runner imports it read-only)
- **External**: `@skills:llm-evaluation` scripts via the tools venv (`../.tools/llm-venv/Scripts/python.exe`); keys from `config/.api-keys.txt` (env-file format, compatible with `--keys-file`)
- **Regression surface**: none (no production code touched); runner verified by an offline scripted test-drive

## 2. MVP Decisions

- **LANATEST-IP01-DC-01**: Runner runs the test IN the run record folder (scaffold copied once to `[record]/workspace/`, Lana runs there). One copy instead of two; the record is immutable after the run ends. Session logs stay in `workspace/.lana-data/sessions/` - no separate `session/` copy.
- **LANATEST-IP01-DC-02**: Timeout MVP = one overall subprocess timeout (`step_timeout x step count`); the FR-04 stall-monitoring refinement is deferred.
- **LANATEST-IP01-DC-03**: Missing `golden/` downgrades to WARNING (runner default `allow_missing_golden: true`) until golden production happens; flip to INVALID (IG-04) afterwards.
- **LANATEST-IP01-DC-04**: Bucket 2-3 scaffolds reference IPPS content via `scaffold.json` (`copy_lana` list) - the runner copies the listed workflows/skills from the repo `.lana/` at run time. Tests always exercise the CURRENT IPPS, no duplication in the suite.
- **LANATEST-IP01-DC-05**: Runner Python = Lana `.venv` (pyyaml 6.0.3 available - manifest/checks stay YAML per spec). Judge Python = tools llm-venv (llm-evaluation dependency home).
- **LANATEST-IP01-DC-06**: Per-test metadata lives in `TEST.md` as one fenced ```yaml block (tiers, thresholds, timeout, policy) - spec FR-02/FR-09 authority preserved, machine-readable without a second file.
- **LANATEST-IP01-DC-07**: `--scripted <script.jsonl>` runner flag sets `LANA_SCRIPTED_ADAPTER` for offline runner test-drives (zero keys, deterministic).

## 3. File Structure

```
evals/suite/
├── runner/
│   ├── run_evals.py               # CLI: scope, --scripted, --skip-judge, --allow-missing-golden
│   ├── evaluators.py              # StructureEvaluator (manifest.yaml), ProcessEvaluator (checks.yaml)
│   ├── judge.py                   # Tier 3: build judge input, call call-llm.py, parse dimension scores
│   ├── judge_prompt_template.md   # generic judge instructions ({RUBRIC} placeholder, JSON contract)
│   └── runner-config.json         # judge model/venv/keys paths, defaults
├── 01_Basics/
│   ├── T01_CreateFile/            # TEST.md, PROMPTS.md, workspace/, expected/{manifest,checks}.yaml, golden/
│   └── T02_EditSequence/          # 2-prompt queue (FR-12)
├── 02_WorkflowsSkills/
│   └── T01_WriteSpec/             # scaffold.json copies write-spec workflow + write-documents skill
└── 03_AdvancedCapabilities/
    └── T01_TranscribeLocal/       # local HTML fixture, Tier 3 rubric
evals/runs/[YYYY-MM-DD]_[HH-MM]_[Scope]/
├── REPORT.md | results.json
└── [TestFolderName]/{workspace/, events.jsonl, stderr.txt, judge/}
```

## 4. Judge Integration (llm-evaluation)

Tier 3 uses @skills:llm-evaluation scripts exclusively (user decision 2026-08-30):

- **Script**: `call-llm.py` - one judge call per test
- **Python**: `../.tools/llm-venv/Scripts/python.exe` (skill dependency home)
- **Model**: `gpt-5-mini` (skill recommendation: best judge calibration), `--response-format json`, `--reasoning-effort medium`
- **Keys**: `config/.api-keys.txt` via `--keys-file` (env-file format)
- **Input assembly**: `judge.py` concatenates the test's output files (from `manifest.yaml` globs) into `judge/input.md` with per-file headers; prompt = `judge_prompt_template.md` with the test's `rubric.md` inlined
- **Output contract**: `{"dimensions": [{"name": str, "score": 0-100, "justification": str}]}`; Tier 3 score = mean/100
- **Audit**: `judge/input.md`, `judge/prompt.md`, `judge/response.json` stored in the TestRunRecord (LANATEST-FR-08)
- **Retries**: `call-llm.py` built-in (3x exponential backoff); runner adds none (LANATEST-NFR-02)

## 5. Edge Cases

- **LANATEST-IP01-EC-01**: Lana exits non-zero mid-queue -> tiers still evaluated on the partial record, status FAIL with exit code named
- **LANATEST-IP01-EC-02**: Subprocess timeout -> kill, record partial events, status FAIL (timeout named)
- **LANATEST-IP01-EC-03**: Missing mandatory expectation file (manifest.yaml) -> status INVALID, no agent run wasted (checked before spawn)
- **LANATEST-IP01-EC-04**: Judge returns unparseable JSON -> Tier 3 = null, status ERROR noted in REPORT, judge transcript kept for diagnosis
- **LANATEST-IP01-EC-05**: `scaffold.json` references a missing `.lana/` path -> INVALID before spawn, path named
- **LANATEST-IP01-EC-06**: Key values from `config/.api-keys.txt` found in any record file -> run aborted with CRITICAL leak error (NFR-03 scan after each test)

## 6. STRUT Plan

```
[x] P1 [IMPLEMENT]: Runner core - discover, execute, record
├─ Objectives:
│   └─ [x] One command runs a test end-to-end and records everything ← P1-D1, P1-D2
├─ Strategy: Thin vertical slice first - discovery + spawn + record, no evaluation yet
├─ [x] P1-S1 [IMPLEMENT](run_evals.py: scope discovery, TEST.md yaml block parse, scaffold copy + scaffold.json copy_lana)
├─ [x] P1-S2 [IMPLEMENT](spawn lana --prompt-file with LANA_CONFIG external, capture events.jsonl + stderr.txt, timeout)
├─ [x] P1-S3 [IMPLEMENT](results.json + REPORT.md aggregation, secret-leak scan)
├─ Deliverables:
│   ├─ [x] P1-D1: run_evals.py executes a test and writes an immutable run record
│   └─ [x] P1-D2: results.json + REPORT.md written
└─> Transitions:
    - P1-D1, P1-D2 checked → P2

[x] P2 [IMPLEMENT]: Evaluators Tier 1 + Tier 2
├─ Objectives:
│   └─ [x] Deterministic scores from record + expectations ← P2-D1
├─ Strategy: manifest.yaml globs/sections/regex; checks.yaml assert types: tool_called, read_before_edit, forbidden_tool
├─ [x] P2-S1 [IMPLEMENT](evaluators.py StructureEvaluator)
├─ [x] P2-S2 [IMPLEMENT](evaluators.py ProcessEvaluator over session JSONL, severity weighting: CRITICAL fail caps 0.5)
├─ Deliverables:
│   └─ [x] P2-D1: Tier 1 + 2 scores with per-check details in results.json
└─> Transitions:
    - P2-D1 checked → P3

[x] P3 [IMPLEMENT]: Judge (Tier 3) via llm-evaluation
├─ Objectives:
│   └─ [x] Rubric-scored quality dimensions with audit trail ← P3-D1
├─ Strategy: call-llm.py wrapper only - no custom LLM client (user decision)
├─ [x] P3-S1 [IMPLEMENT](judge.py: input assembly, call-llm.py invocation, JSON parse, judge/ audit files)
├─ [x] P3-S2 [IMPLEMENT](judge_prompt_template.md + runner-config.json)
├─ Deliverables:
│   └─ [x] P3-D1: Tier 3 score flows into results.json when rubric.md exists
└─> Transitions:
    - P3-D1 checked → P4

[x] P4 [IMPLEMENT]: First tests per bucket
├─ Objectives:
│   └─ [x] Working test set covering all 3 buckets ← P4-D1, P4-D2, P4-D3
├─ Strategy: Predictable outcomes, minimal fixtures; golden/ pending (DC-03)
├─ [x] P4-S1 [IMPLEMENT](01_Basics/T01_CreateFile + T02_EditSequence: TEST.md, PROMPTS.md, workspace, manifest, checks)
├─ [x] P4-S2 [IMPLEMENT](02_WorkflowsSkills/T01_WriteSpec with scaffold.json copy_lana)
├─ [x] P4-S3 [IMPLEMENT](03_AdvancedCapabilities/T01_TranscribeLocal with HTML fixture + rubric.md)
├─ Deliverables:
│   ├─ [x] P4-D1: Bucket 1 tests complete (Tiers 1-2)
│   ├─ [x] P4-D2: Bucket 2 test complete (Tiers 1-2)
│   └─ [x] P4-D3: Bucket 3 test complete (Tiers 1-3)
└─> Transitions:
    - P4-D1 - P4-D3 checked → P5

[x] P5 [TEST]: Offline test-drive
├─ Objectives:
│   └─ [x] Runner proven end-to-end without keys ← P5-D1
├─ Strategy: --scripted with a script that actually creates T01's expected file; fix until green
├─ [x] P5-S1 [TEST](run 01-T01 with scripted adapter -> expect PASS with Tier 1/2 = 1.0)
├─ [x] P5-S2 [TEST](run 01-T01 with a sabotaged script -> expect FAIL with named check)
├─ [x] P5-S3 [FIX](issues found: none - both drives behaved as expected first run)
├─ Deliverables:
│   └─ [x] P5-D1: Offline drive green (PASS and FAIL paths both proven)
└─> Transitions:
    - P5-D1 checked → [END] (live test-drive is the user's move)
```

## 7. Test Cases

- **LANATEST-IP01-TC-01**: 01-T01 scripted PASS drive - exit 0, Tier 1 = 1.0, Tier 2 = 1.0, status pass in results.json
- **LANATEST-IP01-TC-02**: 01-T01 sabotaged script (wrong filename) - Tier 1 < 1.0, status fail, violated expectation named in REPORT.md
- **LANATEST-IP01-TC-03**: Record immutability - re-running a scope creates a NEW timestamped folder, previous untouched
- **LANATEST-IP01-TC-04**: Secret-leak scan - fake key value planted in scaffold output -> run aborts with CRITICAL (EC-06)

## 8. Verification Checklist

- [x] **LANATEST-IP01-VC-01**: P1-P4 implemented, all STRUT deliverables checked
- [x] **LANATEST-IP01-VC-02**: Offline drive TC-01 (PASS, Tier 1/2 = 1.00) + TC-02 (FAIL, Tier 1 = 0.00, Tier 2 = 0.50 CRITICAL cap, checks named) + TC-03 (immutable `-1` suffix folder) + TC-04 (leak scan: clean -> None, planted synthetic key -> CRITICAL)
- [x] **LANATEST-IP01-VC-03**: No key material in either run record (EC-06 scan ran on both drives)
- [x] **LANATEST-IP01-VC-04**: `/verify` run - IMPL structure (header, MNF, TOC, STRUT template compliance), REPORT.md + results.json inspected on both drive records, privacy scan (fixtures generic: fictional Acme Widgets), IG-03 (runner writes only under `evals/runs/`)

## 9. Document History

**[2026-08-30 20:35]**
- Changed: STRUT P1-P5 executed and checked; VC-01..03 checked
- Added: drive scripts persisted at `evals/suite/runner/drive-scripts/t01_pass.jsonl` and `t01_fail.jsonl` (reusable offline drives, DC-07)
- Runs recorded: `evals/runs/2026-08-30_19-43_01-T01` (PASS) and `..._01-T01-1` (sabotage FAIL)

**[2026-08-30 20:20]**
- Initial implementation plan created: MVP vertical slice (runner + Tier 1-3 + 4 tests), judge via @skills:llm-evaluation per user decision, STRUT plan P1-P5
