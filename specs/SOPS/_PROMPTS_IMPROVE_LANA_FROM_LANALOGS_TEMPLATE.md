<!-- PROMPTS TEMPLATE: Evidence-Driven Improvement Pipeline (Batch Mode)
Filename convention: _PROMPTS_ImproveLana_[TOPIC]_BATCH[NN].md
Example: _PROMPTS_ImproveLana_LANALOGS_BATCH01.md

PURPOSE: Enforces the batched pipeline from _INFO_HOW_TO_IMPROVE_LANA.md [LANALOGS-IN01]
Sections 4 (Batching Rules) and 5 (Attribution via Check-Level Diff).
One batch = one copy of this template = one prompt sequence.
A single finding is a batch of size 1 - use the same template.

HOW TO USE:
1. Copy this file, rename per convention above
2. Fill ALL [PLACEHOLDER] values with case-specific data
3. Fill the FINDINGS LIST below (1-5 entries)
4. Remove ALL XML comments (lines like this one)
5. Paste prompts into Cascade's prompt queue sequentially
6. After each prompt completes, verify the STOP gate before pasting the next

SHARED PLACEHOLDERS:
- [BATCH_ID]: e.g., LANALOGS-BATCH-01
- [BATCH_TRACK]: source or prompt (all findings in batch must share the same track)
- [TEST_NAME]: eval test name, e.g., T04_SessionLoad
- [TEST_PATH]: eval test path, e.g., evals/suite/02_WorkflowsSkills/T04_SessionLoad
- [TIER]: A-scripted (source changes) or A-live (prompt changes)
- [SPEC_FILE]: path to SPEC file, e.g., specs/_SPEC_LANA_02-AgentCore.md
- [IMPL_FILE]: path to IMPL file, e.g., specs/_IMPL_LANA_02-AgentCore.md
- [SESSION_PROBLEMS]: path to session PROBLEMS.md

FINDINGS LIST (fill 1-5 entries, delete unused rows):
- [F1_ID]: [F1_SUMMARY] | Category: [F1_CATEGORY] | Target: [F1_TARGET_FILES] | Evidence: [F1_EVIDENCE]
- [F2_ID]: [F2_SUMMARY] | Category: [F2_CATEGORY] | Target: [F2_TARGET_FILES] | Evidence: [F2_EVIDENCE]
- [F3_ID]: [F3_SUMMARY] | Category: [F3_CATEGORY] | Target: [F3_TARGET_FILES] | Evidence: [F3_EVIDENCE]
- [F4_ID]: [F4_SUMMARY] | Category: [F4_CATEGORY] | Target: [F4_TARGET_FILES] | Evidence: [F4_EVIDENCE]
- [F5_ID]: [F5_SUMMARY] | Category: [F5_CATEGORY] | Target: [F5_TARGET_FILES] | Evidence: [F5_EVIDENCE]

Remove this comment block after filling all placeholders. -->

## Prompt 1 - OBSERVE and classify all findings

```
**Objective**: OBSERVE - Classify all findings in batch [BATCH_ID] before any implementation work.

Read `[SESSION_PROBLEMS]` entries for each finding listed below.
Read `specs/SOPS/_INFO_HOW_TO_IMPROVE_LANA.md` Section 1 (Improvement Categories).

Classification test per finding: "If the code perfectly matched the SPEC, would the problem still exist?"
- No -> BUG (spec right, behavior wrong)
- Yes -> CHANGE (spec must change)

Findings to classify:
- [F1_ID]: [F1_SUMMARY] | Evidence: [F1_EVIDENCE]
- [F2_ID]: [F2_SUMMARY] | Evidence: [F2_EVIDENCE]

Classify each finding as BUG or CHANGE. Update `[SESSION_PROBLEMS]` with the classification for each.

Constraints:
- Do not modify any source code or workflow files in this step
- Do not start implementing fixes
- Each classification must reference the SPEC to justify BUG vs CHANGE

Verify: [SESSION_PROBLEMS] entries for ALL findings contain explicit `**Category**: BUG` or `**Category**: CHANGE` with one-sentence justification referencing the SPEC.

**STOP.** Report: per-finding table (ID, classification, justification). Do not proceed to implementation.
```

---

<!-- EXTEND: Add eval checks for ALL findings in the batch.
Each check is tagged with its finding ID for attribution.
Expected state: checks.yaml has one or more new checks per finding. -->

## Prompt 2 - EXTEND eval coverage for batch

```
**Objective**: EXTEND - Add eval checks capturing ALL problems in batch [BATCH_ID].

Read `[TEST_PATH]/expected/checks.yaml`.
Read `specs/SOPS/_INFO_HOW_TO_IMPROVE_LANA.md` Section 2 (EXTEND step) and Section 3.4 (Coverage Rules).

For EACH finding, add one or more checks to `[TEST_PATH]/expected/checks.yaml`:
- Check `id` field MUST contain the finding ID (e.g., `check_[F1_ID]_description`) for attribution
- Asserts an OUTCOME, not an ordering
- Would FAIL on the pre-fix behavior described in that finding

Findings:
- [F1_ID]: [F1_SUMMARY]
- [F2_ID]: [F2_SUMMARY]

If the eval test `[TEST_NAME]` does not exist yet, create it with `manifest.yaml`, `checks.yaml`, `scaffold.json`, `PROMPTS.md`, and `TEST.md`. Use synthetic fixture data only - no real session data.

Constraints:
- Do not modify source code or workflow files
- Do not fix any problem - only capture them in checks
- Checks assert outcomes, never trajectory orderings
- Check IDs must be traceable to finding IDs (required for attribution in Prompt 5)
- No real user data in eval fixtures (privacy gate)

Verify: `[TEST_PATH]/expected/checks.yaml` contains new checks. Each finding has at least one check with its ID embedded.

**STOP.** Report: per-finding check list (finding ID, check ID, assert type, why it fails on pre-fix behavior). Do not implement fixes.
```

---

<!-- MEASURE: Single baseline run for the entire batch.
All new checks should FAIL. This is the evidence baseline.
Expected state: one run folder with all checks recorded. -->

## Prompt 3 - MEASURE baseline (single run for batch)

```
**Objective**: MEASURE - Record the baseline eval score BEFORE implementing any fixes for batch [BATCH_ID].

Run the `[TEST_NAME]` eval test at Tier [TIER] to capture the current (pre-fix) state. Record the run folder path from the output.

Constraints:
- Do not modify any code before running the baseline
- Do not skip this step - without a baseline, there is no proof of improvement
- If the eval runner fails, fix the runner issue first, then re-run

Verify: Run folder exists. results.json shows check status for ALL finding-tagged checks (expected: all FAIL). Record the baseline run folder path and overall score.

**STOP.** Report: baseline run folder path, per-check status table, overall score. Do not implement fixes yet.
```

---

<!-- CHANGE: Implement fixes for ALL findings in the batch.
Category determines sub-pipeline per finding.
Expected state: all fixes implemented, pytest green, SPEC/IMPL/TEST updated. -->

## Prompt 4 - CHANGE (implement all fixes in batch)

<!-- Conditional per finding: Use BUG or CHANGE sub-pipeline. Remove the one that doesn't apply for each finding. -->

```
**Objective**: CHANGE - Implement fixes for ALL findings in batch [BATCH_ID].

Read `specs/SOPS/_INFO_HOW_TO_IMPROVE_LANA.md` Section 3 (Pipeline per Category).

For each finding, apply the correct pipeline:

**CHANGE pipeline (Spec-Anchored):**
1. Update SPEC: add one-line requirement to `[SPEC_FILE]` (FR/DD/IG anchor)
2. Implement the fix in target files
3. Update IMPL plan in `[IMPL_FILE]`: add implementation step (IS-NN)
4. Update IMPL test cases: add test case (TC-NN)
5. Add/extend pytest test (source track) or eval check (prompt track)

**BUG pipeline:**
1. Fix code to match existing SPEC in target files
2. Add/extend pytest test covering the fix
3. If new scenario: extend SPEC/IMPL/TEST

Findings to fix:
- [F1_ID]: [F1_SUMMARY] | Category: [F1_CATEGORY] | Target: [F1_TARGET_FILES]
- [F2_ID]: [F2_SUMMARY] | Category: [F2_CATEGORY] | Target: [F2_TARGET_FILES]

Constraints:
- Fix ONLY findings listed above - do not fix unrelated issues
- SPEC anchor must exist BEFORE code changes (CHANGE category)
- Do not skip IMPL/TEST plan updates for any finding
- Workflow files: sync .lana/ -> .devin/ -> dist/.lana/ after changes

Verify: Full pytest suite passes. SPEC/IMPL updated for each CHANGE finding. All target files modified.

**STOP.** Report: per-finding files changed, pytest result, SPEC anchors. Do not run eval yet.
```

---

<!-- VERIFY + ATTRIBUTE: Single verify run, then derive per-finding attribution.
Attribution = check-level diff between baseline and verify.
Expected state: attribution table showing FIXED/NOT FIXED/REGRESSION per finding. -->

## Prompt 5 - VERIFY and ATTRIBUTE

````
**Objective**: VERIFY + ATTRIBUTE - Re-run the eval test and derive per-finding attribution for batch [BATCH_ID].

Read `specs/SOPS/_INFO_HOW_TO_IMPROVE_LANA.md` Section 5 (Attribution via Check-Level Diff).

**Step 1: VERIFY** - Re-run the `[TEST_NAME]` eval test at Tier [TIER] (same configuration as the MEASURE step).

**Step 2: ATTRIBUTE** - Compare verify results against baseline (Prompt 3) at the check level:

For each check, determine transition:
```
FAIL -> PASS  = FIXED (finding's fix worked)
FAIL -> FAIL  = NOT FIXED (fix was ineffective)
PASS -> FAIL  = REGRESSION (a fix broke something)
PASS -> PASS  = NEUTRAL (unaffected)
```

Map each transition to its finding ID via the check `id` field. Calculate score delta per finding.

Constraints:
- Use the exact same eval configuration as the baseline
- Do not modify code between CHANGE and VERIFY
- If a check still fails, report it as NOT FIXED - do not re-implement

Verify: Run folder exists. Attribution table covers every finding in the batch.

**STOP.** Report: verify run folder path, attribution table (finding ID, status, score delta), regressions (any PASS -> FAIL). Do not commit yet.
````

---

<!-- GATE: Apply triage policy to the batch.
Selectively revert NOT FIXED and REGRESSION findings before commit.
Expected state: clean batch with only FIXED findings, re-verified. -->

## Prompt 6 - GATE (batch triage)

```
**Objective**: GATE - Apply triage policy to batch [BATCH_ID] and prepare clean commit.

Read `specs/SOPS/_INFO_HOW_TO_IMPROVE_LANA.md` Section 7 (Triage Policy) and Selective Revert Protocol.

Using the attribution table from Prompt 5, apply these rules:

**REGRESSION** (PASS -> FAIL on any pre-existing check):
1. Identify responsible finding by check proximity
2. If ambiguous, bisect: revert one finding at a time, re-run VERIFY
3. Revert responsible finding's changes
4. Log finding as BLOCKED in `[SESSION_PROBLEMS]` with regression evidence

**NOT FIXED** (FAIL -> FAIL):
1. Revert that finding's code/prompt changes
2. Log finding in `[SESSION_PROBLEMS]` as deferred to next batch

**After all reverts** (if any):
1. Re-run the `[TEST_NAME]` eval at Tier [TIER] to confirm FIXED findings still pass
2. Record post-revert verify run folder path

Dimension priority: Correctness > Completeness > Autonomy > Cost > Latency.
Correctness regression = hard veto after confirm-before-veto (k=3).

Constraints:
- Do not add new code in this step - only revert
- If uncertain about regression, re-run eval 2 more times (k=3 total)

Verify: Only FIXED findings remain. No regressions. Post-revert verify run (if reverts occurred) confirms clean state.

**STOP.** Report: final ACCEPT/REJECT per finding, reverted findings (if any), final verify run folder path.
```

---

<!-- COMMIT: Atomic commit for the batch with attribution table.
Expected state: one commit with all FIXED findings, attribution in body. -->

## Prompt 7 - COMMIT (batch commit with attribution)

````
**Objective**: COMMIT - Create atomic commit for batch [BATCH_ID] with per-finding attribution.

If ALL findings were reverted in Prompt 6, skip this prompt entirely.

Create a single commit containing ALL artifacts for FIXED findings:
- Code changes (source and/or prompt files)
- SPEC deltas (CHANGE category findings)
- IMPL/TEST plan updates
- Eval check extensions
- Workflow syncs (.lana/ -> .devin/ -> dist/.lana/)

Do NOT include reverted findings' changes.

Commit message format:
```
change([BATCH_ID]): [one-line batch description]

Baseline: [baseline run folder from Prompt 3]
Verify:   [final verify run folder from Prompt 5 or 6]
Score:    [baseline score] -> [verify score] (+Npp)

Attribution:
  [F1_ID]  FIXED     +Npp  [F1_SUMMARY]
  [F2_ID]  FIXED     +Npp  [F2_SUMMARY]
  [F3_ID]  deferred  +0pp  [F3_SUMMARY] (reverted, not in this commit)
```

For solo BUG batches, use `fix` instead of `change`.

Constraints:
- Commit body MUST contain Baseline, Verify, Score, and Attribution sections
- Do not include reverted findings' code in the commit
- Stage only files related to FIXED findings

Verify: `git log -1 --format="%s%n%b"` shows correct format with attribution. `git diff HEAD~1 --stat` shows only FIXED findings' files.

**Record**: Append attribution results to the source INFO document that produced the findings. Add a new section with: per-finding table (check ID, baseline, verify, delta, status), run folder paths, score delta, cost delta, commit hash. This closes the loop: analysis doc → pipeline → results back to analysis doc.

**STOP.** Report: commit hash, commit message, file count, per-finding status. Batch complete.
````

<!-- EXAMPLE: Reference only. Shows a filled instance for Batch 02 (prompt track).

## Full Example

A filled instance would be saved as:
_PROMPTS_ImproveLana_LANALOGS_BATCH02.md

With these shared placeholders resolved:
- [BATCH_ID] = LANALOGS-BATCH-02
- [BATCH_TRACK] = prompt
- [TEST_NAME] = T04_SessionLoad
- [TEST_PATH] = evals/suite/02_WorkflowsSkills/T04_SessionLoad
- [TIER] = A-live
- [SPEC_FILE] = specs/_SPEC_LANA_02-AgentCore.md
- [IMPL_FILE] = specs/_IMPL_LANA_02-AgentCore.md
- [SESSION_PROBLEMS] = _PrivateSessions_gitignore/_2026-09-01_LanaLogAnalysis/T01_.../PROBLEMS.md

Findings list:
- PR-0005: /prime reads FAILS.md (50K) and ID-REGISTRY.md (34K) in full | CHANGE | .lana/workflows/prime.md | L93-100
- PR-0007: /session-load reads topic subfolders unnecessarily | CHANGE | .lana/workflows/session-load.md | L117-124

Result: PR-0005 FIXED (+8pp), PR-0007 NOT FIXED (reverted, deferred).
Commit includes only PR-0005's changes with attribution table. -->
