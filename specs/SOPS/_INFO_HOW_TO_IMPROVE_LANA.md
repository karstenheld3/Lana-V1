# INFO: How to Improve Lana - Evidence-Driven Improvement Pipeline

**Doc ID**: LANALOGS-IN01
**Goal**: Define the pipeline that turns live session observations into proven, regression-safe improvements to Lana source code and IPPS prompt system
**Timeline**: Created 2026-09-01

**Depends on:**
- `specs/_SPEC_LANA_EVAL_SUITE.md [LANATEST-SP01]` for eval suite structure (tiers, tests, run records)
- `T01_BRNDSSNL_SessionLoadPersonalBrand_2026-09-01/_INFO_LANALOGS-BRNDSSNL_01.md [LANALOGS-BRNDSSNL-IN01]` for finding classification examples

## Summary

- Every improvement follows the Evidence-Driven Improvement Loop: OBSERVE → EXTEND → MEASURE → CHANGE → VERIFY → GATE → COMMIT [PROVEN pattern, applied in T01]
- Findings are classified BUG (spec right, behavior wrong) or CHANGE (spec itself must change) - each has its own pipeline branch [VERIFIED against T01 findings: all 8 are CHANGE]
- Pipeline 3 (Spec-Anchored) chosen: SPEC change is a one-line anchor, then IMPL + TEST + code bundled and committed atomically [DECIDED 2026-09-01]
- Findings are batched by test and track for cost-efficient verification. One MEASURE run, one VERIFY run per batch. Attribution is derived from check-level diff (each check is tagged with its finding ID) [DECIDED 2026-09-01, replaces earlier "never bundle" rule]
- Verification cost is controlled by tiers: A-scripted (~$0, source changes), A-live (cents, prompt changes - scripted drives CANNOT verify LLM behavior), B bucket (per 3-5 changes), C full suite (per release) [DESIGNED, RV01 corrected]
- Regression gating uses confirm-before-veto: 1 run default, re-run k=3 only when regression detected - single-run scores vary 2-6pp even at temperature 0 [VERIFIED, arxiv 2602.07150]
- Proof of improvement = eval score comparison in `results.json` before vs after, committed with the change. Per-finding attribution = check-level FAIL→PASS transitions [VERIFIED, eval runner records immutable run folders]
- Conflicting interests resolved by dimension priority: Correctness > Completeness > Autonomy > Cost > Latency [DECIDED 2026-09-01]

## Table of Contents

1. [Improvement Categories](#1-improvement-categories)
2. [Evidence-Driven Improvement Loop](#2-evidence-driven-improvement-loop)
3. [Pipeline per Category](#3-pipeline-per-category)
4. [Batching Rules](#4-batching-rules)
5. [Attribution via Check-Level Diff](#5-attribution-via-check-level-diff)
6. [Verification Tiers](#6-verification-tiers)
7. [Triage Policy (GATE)](#7-triage-policy-gate)
8. [Artifacts and Locations](#8-artifacts-and-locations)
9. [Worked Example](#9-worked-example)

## 1. Improvement Categories

Every observed problem is classified before any work starts:

- **BUG** - Malfunction. Two sub-cases:
  - Code does not implement SPEC correctly → fix code
  - Unforeseen strange behavior, but SPEC, IMPL, TEST are still correct → fix code
  - SPEC/IMPL/TEST stay unchanged (only extended with the new scenario if needed)

- **CHANGE** - Unintended behavior that is "as designed". Two sub-cases:
  - Undesired as-designed functionality coming from SPEC or IMPL → SPEC + IMPL + TEST must change + change implemented
  - Gap in SPEC, IMPL, TEST (behavior never specified) → behavior must be specified + change implemented

Classification test: "If the code perfectly matched the SPEC, would the problem still exist?"
- No → BUG
- Yes → CHANGE

## 2. Evidence-Driven Improvement Loop

Every improvement, both tracks (Lana source code, IPPS prompt system), follows this cycle:

```
OBSERVE → EXTEND → MEASURE → CHANGE → VERIFY → GATE → COMMIT
```

- **OBSERVE** - Analyze live session logs (`.lana-data/sessions/*.jsonl`). Each finding gets a PR-xxxx in the session's PROBLEMS.md with evidence (log line references) and track classification (source code / prompt system / both).
- **EXTEND** - Ensure evals cover the observed problem. Either extend an existing test's `checks.yaml`/`manifest.yaml` or create a new test. The check MUST fail (or score low) on current behavior - it captures the problem. Checks assert OUTCOMES ("zero file-not-found tool failures", "tool_calls_total <= N"), never orderings ("first call is X") - live agent trajectories diverge early even at temperature 0.
- **MEASURE** - Record the baseline: run the affected eval test. The failing/low score IS the baseline. Stored in the immutable run folder. After a batch is accepted, the next batch's baseline = the previous batch's final verify run. If the previous batch had a partial accept (NOT FIXED findings reverted), the post-revert verify run is the baseline, not the pre-revert run.
- **CHANGE** - Implement per category pipeline (section 3). Findings are batched by test and track (section 4).
- **VERIFY** - Single verify run per batch. Compare check-level results against baseline. Attribution derived from which checks flipped (section 5).
- **GATE** - Apply triage policy (section 7). Regression on any check → identify responsible finding via attribution, selectively revert.
- **COMMIT** - Atomic commit per batch: code + SPEC/IMPL/TEST updates + eval extension + before/after score with per-finding attribution.

## 3. Pipeline per Category

### 3.1 Common Steps (both categories)

```
1. Classify finding: BUG or CHANGE
2. EXTEND evals: add check(s) that capture the problem
3. MEASURE: run affected test → record FAIL baseline (run folder = evidence)
```

### 3.2 BUG Pipeline

```
4a. Fix code to match existing SPEC
5a. Add/extend code test covering the fix (unit test or eval check)
6a. VERIFY: run pytest + eval check (Tier A-scripted) → PASS
7a. If new scenario discovered: extend SPEC/IMPL/TEST with the scenario (no semantic change)
8a. COMMIT: fix(TOPIC-BG-NNNN): description
```

### 3.3 CHANGE Pipeline (Spec-Anchored)

```
4b. Update SPEC: one-line requirement addition or modification (FR/DD/IG)
    - This is the anchor: WHY the behavior must change
5b. Implement + update IMPL + update TEST together (one bundle)
    - Code change covered by unit test (source track) or eval check (prompt track)
6b. VERIFY: run tests + eval check (A-scripted for source, A-live for prompt) → PASS
7b. COMMIT: change(TOPIC-PR-NNNN): description
    - Contains: SPEC delta + IMPL delta + TEST delta + code + eval extension
```

Key property: SPEC change is lightweight (a decision, not a review gate), but it exists BEFORE code - the "why" is never lost. IMPL/TEST/code are written from proven reality and committed atomically, so docs never drift from code.

### 3.4 Coverage Rules (the 4 MUSTs)

1. **Evals cover the observed problem** - EXTEND step is mandatory. No fix without a failing check first.
2. **Code changes covered by tests** - Source track: pytest unit test. Prompt track: eval check. Both: the check that failed in MEASURE.
3. **SPEC, IMPL, TEST plans updated** - BUG: extend with scenario. CHANGE: SPEC anchor first, IMPL+TEST in the bundle.
4. **Documented proof of improvement** - Before run folder (FAIL) + after run folder (PASS) + commit message referencing both. Per-finding attribution in commit body. `results.json` check-level diff is the proof.

## 4. Batching Rules

Findings are grouped into batches to reduce eval cost while preserving attribution. One MEASURE run and one VERIFY run per batch.

### 4.1 Batch Formation

Group findings that share:
- Same eval test (e.g., all T04_SessionLoad findings)
- Same track (source, prompt, or both)
- Same tier (A-scripted or A-live)

Batch boundaries:
- **Same test, same track** → single batch, Tier A verify
- **Same bucket, mixed tests** → single batch, Tier B verify
- **Cross-cutting changes** (system prompt, tool infra) → separate batch, Tier C verify
- **Interdependent findings** (fix B depends on fix A) → same batch, ordered implementation

### 4.2 Batch Size Limits

- Maximum **5 findings per batch** (keeps attribution readable and selective revert practical)
- If a batch has >5 findings, split by sub-track or complexity

### 4.3 Batch Pipeline Flow

```
1. OBSERVE: classify ALL findings (done once per analysis)
2. Form batches per rules above
3. Per batch:
   a. EXTEND: add checks for all findings in the batch (one prompt)
   b. MEASURE: single baseline run → all new checks FAIL
   c. CHANGE: implement all fixes in the batch
   d. VERIFY: single verify run → compare check-level results
   e. ATTRIBUTE: derive per-finding contribution from check-level diff
   f. GATE: triage batch; selectively revert findings with regressions
   g. COMMIT: atomic commit with attribution table in body
```

### 4.4 When NOT to Batch

- Finding requires an architectural change that affects many modules → solo batch
- Finding has high revert risk (touches shared infrastructure) → solo batch
- Findings are in different eval buckets with no test overlap → separate batches (natural boundary)

## 5. Attribution via Check-Level Diff

Attribution is derived from a single baseline-vs-verify comparison. No extra eval runs needed.

### 5.1 How It Works

Every check in `checks.yaml` is tagged with the finding ID that motivated it (via the check `id` field). Comparing baseline and verify run results at the check level produces a per-finding status:

```
Baseline run (pre-fix):
  check_PR0001_agent_folder    = FAIL
  check_PR0005_prime_reads     = FAIL
  check_PR0007_topic_scope     = FAIL
  check_existing_session_docs  = PASS    (pre-existing)

Verify run (post-fix):
  check_PR0001_agent_folder    = PASS
  check_PR0005_prime_reads     = PASS
  check_PR0007_topic_scope     = FAIL
  check_existing_session_docs  = PASS    (pre-existing)

Attribution:
  PR-0001 → FIXED      (FAIL → PASS)
  PR-0005 → FIXED      (FAIL → PASS)
  PR-0007 → NOT FIXED  (FAIL → FAIL)  → investigate or defer
  Regressions → none   (no PASS → FAIL)
```

### 5.2 Attribution Categories

- **FIXED** (FAIL → PASS): Finding's check(s) now pass. Fix worked.
- **NOT FIXED** (FAIL → FAIL): Finding's check(s) still fail. Fix was ineffective or incomplete. Investigate before committing.
- **REGRESSION** (PASS → FAIL on pre-existing check): A change in the batch broke something. Identify responsible finding by: 1) check proximity (which files does the regressed check cover? which finding touched those files?), 2) if ambiguous (multiple findings touch the same file), bisect by reverting one finding at a time and re-running VERIFY until the regression disappears.
- **NEUTRAL** (PASS → PASS on pre-existing check): No impact. Expected for unrelated checks.

### 5.3 Score Attribution

Overall score delta can be decomposed per finding:

```
Overall: 60% → 85% (+25pp)

Per finding (equal check weight):
  PR-0001: 2 checks flipped  → +10pp  (40% of improvement)
  PR-0005: 2 checks flipped  → +10pp  (40% of improvement)
  PR-0007: 0 checks flipped  →  +0pp  ( 0% of improvement)
  Regressions:               →  -0pp
  Residual (non-binary scores): +5pp   (20% - from score improvements on existing checks)
```

If checks have unequal weight, use the weighted contribution instead.

### 5.4 Commit Attribution Format

Include attribution table in the commit message body:

```
change(LANALOGS-BATCH-01): session load efficiency improvements

Baseline: evals/runs_gitignore/T04_SessionLoad/run_20260901_150000/
Verify:   evals/runs_gitignore/T04_SessionLoad/run_20260901_153000/
Score:    60% → 85% (+25pp)

Attribution:
  PR-0001  FIXED     +10pp  agent folder resolution
  PR-0005  FIXED     +10pp  prime read limits
  PR-0007  NOT FIXED  +0pp  topic scope (deferred)
```

## 6. Verification Tiers

Cost-controlled verification. Not every change needs the full suite.

### Tier A-scripted: Targeted scripted test (seconds, ~$0) - source code changes

- Run ONLY the new/modified eval test for the specific PR
- Structural + process checks (Tier 1 + Tier 2 evaluators) against scripted drives - no live LLM
- Runner support: `run_evals.py <test> --scripted <drive.jsonl> --skip-judge`
- Valid for: source code changes (paired with pytest unit tests) and evaluator/check development
- **NOT valid for prompt system changes**: scripted drives bypass the LLM - a workflow edit has zero effect on a replayed drive. Verifying a prompt change with a hand-authored drive is circular (the drive and the check come from the same author; see FAILS.md GLOB-FL-0001 for this failure class)
- Gate: new check passes, existing checks in that test unchanged

### Tier A-live: Targeted live test (~1 min, cents) - prompt system changes

- Run ONLY the affected eval test with live LLM: `run_evals.py <test> --skip-judge`
- The only way to prove the LLM actually behaves differently after a workflow/skill/rule change
- Gate: new check passes, existing checks in that test unchanged

### Tier B: Bucket regression (minutes, ~$1-2) - every 3-5 changes

- Run the affected bucket only (e.g., `01_Basics` if tool behavior changed)
- Live LLM, 3-4 tests instead of 9
- Gate: no regression in any test of that bucket

### Tier C: Full suite (~$5-10) - rare

- Before a release (`/project-release`)
- After a batch of changes
- When a change touches cross-cutting infrastructure (system prompt, tool call layer, model routing)
- Gate: no regression anywhere; this run becomes the new reference baseline

### Tier Selection Rule

```
Change touches...                        → minimum tier
Single source module (isolated)          → A-scripted (+ pytest)
Single workflow/skill file               → A-live
Multiple workflows or shared skill       → B (affected bucket)
System prompt, tool infra, model config  → C
Release preparation                      → C
```

### Comparison Validity Rules

- Baseline and verify runs MUST share an identical run tag (`[Agent]-[Version]_[ModelId]_[Effort]`) and prompt system state. Different config = invalid comparison.
- **Confirm-before-veto**: default 1 run. If a regression appears, re-run the affected test 2 more times (k=3). Reject only if the regression reproduces in the majority of runs. Single-run scores vary 2-6pp even at temperature 0 - a lone red run is a sample, not a verdict.
- Binary structural checks (file exists, tool called, no failed calls) gate strictly. Judge scores (Tier 3) gate with tolerance band: `after >= before - 0.05`.

## 7. Triage Policy (GATE)

Dimension measurement (all from the eval run record):

- **Correctness** = Tier 1 + Tier 2 binary check results
- **Completeness** = test pass/fail status
- **Autonomy** = tool-call-count proxy (`tool_calls_total` vs limit); real user interruptions are not observable in headless runs
- **Cost** = per-test $ from run record
- **Latency** = per-test wall time

When a batch improves one dimension but regresses another, decide by priority:

1. **Correctness** - Agent produces right output. NEVER regresses. Hard veto.
2. **Completeness** - Agent finishes the task. Regression requires documented justification.
3. **Autonomy** - No user interruption needed. May regress only if correctness improves.
4. **Cost** - $ per operation. May increase up to 20% if correctness or completeness improves.
5. **Latency** - Wall time. May regress if any higher dimension improves.

Decision rules (agent applies autonomously under `/go`):

- Correctness regression on ANY check (confirmed via confirm-before-veto re-runs) → identify responsible finding via attribution → **selectively revert** that finding's changes, re-run VERIFY, re-attribute
- Completeness regression → **REJECT** the responsible finding unless correctness improved AND justification documented
- Cost +20% or more without correctness/completeness gain → **REJECT** batch
- Only latency regresses → **ACCEPT** with note in commit message
- All dimensions neutral or better + new checks pass → **ACCEPT**
- Mixed batch (some FIXED, some NOT FIXED, no regressions) → **revert NOT FIXED findings' code changes**, re-run VERIFY to confirm FIXED findings still pass, then **ACCEPT**. Defer NOT FIXED findings to next batch.

### Selective Revert Protocol

When a regression is attributed to a specific finding:

1. Revert ONLY that finding's code changes (git-level or manual)
2. Re-run VERIFY (same config) → confirm regression is gone
3. Re-attribute: remaining findings should still show FIXED
4. COMMIT without the reverted finding
5. Log reverted finding in PROBLEMS.md as BLOCKED with regression evidence

## 8. Artifacts and Locations

```
evals/suite/[bucket]/[test]/           # test definitions (tracked in git)
├── PROMPTS.md                         # prompt queue
├── expected/manifest.yaml             # Tier 1 structure checks
├── expected/checks.yaml               # Tier 2 process checks  <- EXTEND target
└── golden/                            # reference output

evals/runs_gitignore/[timestamp]_[agent]_[model]/   # immutable run records (gitignored)
└── results.json                       # before/after comparison source

[SESSION_FOLDER]/T##_[SUBTOPIC]_*/     # per-analysis topic folder
├── PROBLEMS.md                        # PR-xxxx findings with evidence
└── _INFO_*.md                         # analysis document

specs/ or session folders              # SPEC, IMPL, TEST plan documents
```

Commit message formats:
- Solo finding (BUG): `fix([TOPIC]-BG-NNNN): description`
- Solo finding (CHANGE): `change([TOPIC]-PR-NNNN): description`
- Batched findings: `change([TOPIC]-BATCH-NN): description` (list finding IDs in body)
- Body MUST contain the gate evidence line: `Baseline: [run folder] → Verify: [run folder]`
- Body MUST contain per-finding attribution table (see Section 5.4)
- A commit without the evidence line and attribution did not pass the pipeline

## 9. Worked Example

Batch from T01: PR-0001 (source, agent folder), PR-0005 (prompt, prime reads), PR-0007 (prompt, topic scope).

```
1. OBSERVE: all 3 classified as CHANGE
2. BATCH: PR-0001 is source track → solo Tier A-scripted batch
         PR-0005 + PR-0007 are prompt track, same test → one Tier A-live batch

Batch 1 (source): PR-0001
3. EXTEND: add checks to T04 checks.yaml:
   - check_PR0001_no_devinfolder: zero read_file targeting .devin/ when prompt system is .lana/
   - check_PR0001_agent_folder_resolved: agent_folder appears in session metadata
4. MEASURE: run T04 --scripted --skip-judge → both checks FAIL (baseline)
5. CHANGE:
   - SPEC anchor: FR-XX "Agent resolves [AGENT_FOLDER] from prompt system load path"
   - Implement: expose agent_folder in session metadata
   - IMPL step IS-XX, TEST case TC-XX, pytest unit test
6. VERIFY: run T04 --scripted --skip-judge → both checks PASS
7. ATTRIBUTE: PR-0001 FIXED (2/2 checks flipped, +15pp)
8. GATE: no regressions → ACCEPT
9. COMMIT: change(LANALOGS-PR-0001): resolve agent folder from prompt system path
   Body: Baseline: run_20260901_150000 | Verify: run_20260901_151500
   Attribution: PR-0001 FIXED +15pp

Batch 2 (prompt): PR-0005, PR-0007
3. EXTEND: add checks to T04 checks.yaml:
   - check_PR0005_prime_limited: no read_file on FAILS.md without offset/limit
   - check_PR0007_no_topic_reads: zero read_file on T##_*/NOTES.md during session-load
4. MEASURE: run T04 --skip-judge (live) → both checks FAIL (baseline)
5. CHANGE:
   - PR-0005: update /prime workflow with read limits for large files
   - PR-0007: update /session-load Step 3 to exclude topic subfolders
   - SPEC anchors, IMPL steps for both
6. VERIFY: run T04 --skip-judge (live) → check_PR0005 PASS, check_PR0007 FAIL
7. ATTRIBUTE:
   PR-0005 FIXED     (FAIL → PASS, +8pp)
   PR-0007 NOT FIXED (FAIL → FAIL, +0pp) → defer to next batch
8. GATE: no regressions, PR-0005 works, PR-0007 not fixed
   → revert PR-0007 workflow changes
   → re-run VERIFY: check_PR0005 still PASS, check_PR0007 back to FAIL (expected)
   → ACCEPT (PR-0005 only). Defer PR-0007 to next batch.
9. COMMIT: change(LANALOGS-BATCH-02): prime read limits for session load
   Body: Baseline: run_20260901_152000 | Verify: run_20260901_153500 (post-revert)
   Attribution: PR-0005 FIXED +8pp | PR-0007 deferred (reverted, not in this commit)
```

## Sources

- `LANALOGS-IN01-SC-EVALSPEC-SP01`: `_Sessions/_2026-08-30_LanaEvalSuite/_SPEC_LANA_EVAL_SUITE.md` - Three-tier eval design, scripted drives, immutable run records [VERIFIED]
- `LANALOGS-IN01-SC-T01-IN01`: `T01_BRNDSSNL_SessionLoadPersonalBrand_2026-09-01/_INFO_LANALOGS-BRNDSSNL_01.md` - 8 findings, all Category CHANGE, evidence format [VERIFIED]
- `LANALOGS-IN01-SC-RUNNER-PY`: `evals/suite/runner/run_evals.py` - `--scripted` and `--skip-judge` flags enable $0 Tier A verification [VERIFIED]

## Next Steps

1. Create eval test `evals/suite/02_WorkflowsSkills/T04_SessionLoad/` covering the T01 scenario. Fixture = SYNTHETIC session folder (generic topic, fictional content) - NEVER copied from real sessions (privacy: evals/suite/ is git-tracked)
2. Form batches from T01 findings per Section 4 rules (expected: 2-3 batches by track)
3. Per batch: EXTEND all checks → MEASURE baseline → CHANGE all fixes → VERIFY → ATTRIBUTE → GATE → COMMIT
4. After all batches: Tier B run on `02_WorkflowsSkills` bucket
5. Update prompt template (`_PROMPTS_IMPROVE_LANA_FROM_LANALOGS_TEMPLATE.md`) to support batch mode
6. Before next release: Tier C full suite → new reference baseline

## Document History

**[2026-09-01 17:23]**
- Fixed: NOT FIXED findings must be reverted before commit (F-01, SOCAS-06)
- Fixed: regression attribution bisect fallback when multiple findings touch same file (F-02, SOCAS-02)
- Fixed: baseline chaining clarified for partial-accept batches (post-revert verify run = next baseline) (F-03, SOCAS-06)
- Fixed: commit format now distinguishes solo vs batch, attribution table required (F-04, SOCAS-01)
- Changed: worked example Batch 2 now shows revert-before-commit flow for NOT FIXED PR-0007

**[2026-09-01 17:20]**
- Changed: replaced "One finding = one change. Never bundle." with batching rules (Section 4) - findings grouped by test, track, and tier
- Added: Section 5 (Attribution via Check-Level Diff) - per-finding contribution derived from single baseline-vs-verify comparison, no extra eval runs
- Added: Score attribution with percentage decomposition per finding
- Added: Commit attribution format with per-finding table
- Changed: GATE policy updated for batch triage with selective revert protocol
- Changed: Worked example updated to show batched scenario (2 batches from T01: source solo, prompt paired)
- Changed: Section numbering shifted (Verification Tiers now Section 6, Triage now Section 7, etc.)

**[2026-09-01 15:00]**
- Changed: Tier A split into A-scripted (source) and A-live (prompt) - scripted drives cannot verify LLM behavior (RV01 RF-01)
- Added: confirm-before-veto gating, tolerance bands for judge scores, config-pinning rule (RF-02, RF-06)
- Changed: loop order OBSERVE → EXTEND → MEASURE (RF-07); T04_SessionLoad moved to 02_WorkflowsSkills (RF-03)
- Added: triage dimension measurement mapping (RF-04), outcome-not-ordering check rule (RF-05), baseline chaining (RF-08), commit evidence line (RF-09), synthetic fixture constraint (RF-10)

**[2026-09-01 14:50]**
- Initial document created: categories (BUG/CHANGE), Evidence-Driven Improvement Loop, Pipeline 3 (Spec-Anchored), verification tiers A/B/C, triage policy, worked example from T01 PR-0001
