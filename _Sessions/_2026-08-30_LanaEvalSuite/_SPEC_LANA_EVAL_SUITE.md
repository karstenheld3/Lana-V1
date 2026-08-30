# SPEC: Lana External Evaluation Suite

**Doc ID**: LANATEST-SP01
**Feature**: eval-suite
**Goal**: Define a three-tier evaluation suite (structure, process, content quality) that tests the Lana agent with prompt-based test cases against golden references produced by Cascade + IPPS
**Timeline**: Created 2026-08-30
**Target file(s)**:
- `evals/suite/` (test definitions, runner, evaluators)
- `evals/runs/` (immutable run records)

**Depends on:**
- `specs/_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` for headless CLI mode and session event flushing
- `_INFO_CASCADE_RESULT_COMPARISON_SUMMARY.md [CSRCMP-IN10]` (external) for reproducibility evidence driving the evaluation design
- `_INFO_GRUC_GUIDES_RULES_CHECKS.md [GRUC-IN01]` (external) for the RULES/CHECKS evaluation split

**Does not depend on:**
- `tests/` unit test suite (internal correctness tests; this suite evaluates agent behavior end-to-end)

## MUST-NOT-FORGET

- Golden output is a rubric ANCHOR, never a diff target (Cascade-vs-Cascade content overlap is 15%, CSRCMP-IN10)
- Tier 1 and Tier 2 evaluation MUST be deterministic: same run record → same scores
- The agent under test MUST NEVER see `expected/` or `golden/` content (gaming prevention, GRUC-IN01 section 2.3)
- Every test MUST be manually executable by Cascade + IPPS in Windsurf to produce golden output
- Bucket 1 scaffolds contain an EMPTY `.lana/` folder (tests raw tool usage) - the folder MUST exist in the scaffold: a MISSING folder triggers Lana's zero-setup materialization of the bundled prompt library (contamination); an existing empty folder stays untouched [VERIFIED: cli.py first-run behavior]
- Test prompts MUST have predictable, verifiable outcomes - no open-ended creative tasks

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

**Problem:** Lana needs an external evaluation suite proving it executes tool usage, IPPS workflows/skills, and advanced capabilities (deep-research, transcribe) at reference quality. LLM outputs are non-deterministic: identical prompts produce 0% query overlap and 15% source overlap even on the reference agent (CSRCMP-IN10). Exact output comparison is impossible; the suite must evaluate structure, process, and quality instead.

**Solution:**
- Three prompt buckets with per-test scaffolds, expectations, and golden references
- Three-tier evaluation mirroring the IPPS GRUC architecture:
  - Tier 1 STRUCTURE (RULES-style): deterministic manifest checks on delivered files
  - Tier 2 PROCESS (CHECKS-style): deterministic audit of the agent's session event log
  - Tier 3 QUALITY (judge): LLM-as-judge scoring against a rubric anchored in golden output
- Runner executes prompts against headless Lana, records everything into immutable run folders

**What we don't want:**
- Byte-level or content-level diff against golden output (provably invalid, CSRCMP-IN10)
- LLM-judge for Bucket 1 (outcomes are deterministic; judge adds cost and noise)
- Expectations or golden content visible to the agent under test
- Test outcomes depending on live web resources where a local fixture is possible
- A second unit-test framework - the suite evaluates the agent as a black box via its CLI

## 2. Context

Lana (LANAAGNT-SP01) is a Python CLI agent adapting the Cascade architecture. It supports headless prompt execution with JSONL event output and flushes session event logs to `.lana-data/sessions/`. The user runs the same IPPS DevSystem (workflows, skills, rules) in Windsurf Cascade; Cascade + IPPS therefore serves as the reference agent producing golden outputs. `tests/harness.py` already demonstrates the headless spawn-inject-parse pattern the runner will reuse.

## 3. Domain Objects

### Bucket

A **Bucket** groups test cases by capability scope.

**Storage:** `evals/suite/[NN]_[Name]/`

- `01_Basics` - Raw tool usage, independent of `.lana/` content (empty `.lana/` in scaffolds)
- `02_WorkflowsSkills` - IPPS workflow/skill existence and instruction following (populated `.lana/`)
- `03_AdvancedCapabilities` - Full `/deep-research` and `/transcribe` workflow + skill execution

### TestCase

A **TestCase** is one evaluable unit: a prompt (or prompt sequence) with scaffold, expectations, and golden reference.

**Storage:** `evals/suite/[Bucket]/T[NN]_[Name]/`
**Test key:** `[BucketNN]-T[NN]` (example: `01-T03`)

**Folder contents:**
- `TEST.md` - Human-readable definition: goal, prompt overview, pass criteria, golden production instructions
- `PROMPTS.md` - PromptQueueFile with one or more fenced prompts in execution order
- `workspace/` - Initial workspace scaffold, copied fresh per run
- `expected/manifest.yaml` - Tier 1 structural expectations
- `expected/checks.yaml` - Tier 2 process expectations
- `expected/rubric.md` - Tier 3 judge rubric (only where Tier 3 applies)
- `golden/` - Golden reference output produced by Cascade + IPPS

### PromptQueueFile

A **PromptQueueFile** carries an ordered queue of prompts in one markdown file. Format authority: `docs/PROMPT_FILE_FORMAT.md` (normative: `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` FR-12).

**Format rules (summary):**
- The first non-empty line MUST be an opening fence; single-prompt tests have one fence
- Each prompt is one fenced block: opening fence of N backticks (3 <= N <= 9, per prompt), closed by a line of >= N backticks; inner fences must be shorter than N
- Consecutive prompts are separated by one `---` line; commentary (step labels) is allowed between `---` and the next fence and is never sent to the agent
- Queue order = fence order in the file

### WorkspaceScaffold

A **WorkspaceScaffold** is the initial state a test starts from: folder tree, seed files, fixtures (PDFs, HTML snapshots), and `.lana/` content appropriate for the bucket.

### ExpectationManifest (Tier 1)

An **ExpectationManifest** declares verifiable output properties: required files (globs), forbidden files, required sections per file, format patterns (IDs, dates), minimum counts.

### ProcessChecks (Tier 2)

**ProcessChecks** declare actions the agent must have performed, verified against the session event log. Each check has: action, evidence (event pattern), failure indicator, severity (CRITICAL, HIGH, MEDIUM). Format follows GRUC-IN01 section 9.3.

### Rubric (Tier 3)

A **Rubric** defines content quality criteria for the LLM judge: scored dimensions (0-100), anchor excerpts from golden output illustrating target quality, and the 7 meta-criteria from CSRCMP-IN10 section 7.5 where applicable.

### GoldenReference

A **GoldenReference** is the output folder produced by Cascade + IPPS executing the same prompts on the same scaffold. Roles: 1) source for distilling `manifest.yaml`, 2) anchor excerpts for `rubric.md`, 3) human comparison baseline. Never a diff target.

### Run and TestRunRecord

A **Run** executes a scope (one test, one bucket, or all) and produces one immutable run folder.

**Storage:** `evals/runs/[YYYY-MM-DD]_[HH-MM]_[Scope]/`
**Scope naming:** bucket folder name (`01_Basics`), test key (`01-T03`), or `All`

**Run folder contents:**
- `REPORT.md` - Human-readable results summary
- `results.json` - Machine-readable scores per test and tier
- `[TestFolderName]/` per executed test (**TestRunRecord**):
  - `workspace/` - Final workspace state after all prompt steps
  - `events.jsonl` - Stdout AgentEvents for the full queue run (prompt-boundary events segment steps)
  - `session/` - Copies of `.lana-data/sessions/*.jsonl` from the test workspace
  - `judge/` - Judge request/response transcripts (only if Tier 3 ran)

### Evaluator

An **Evaluator** scores one tier from a TestRunRecord: StructureEvaluator (Tier 1), ProcessEvaluator (Tier 2), QualityEvaluator (Tier 3).

## 4. Functional Requirements

**LANATEST-FR-01: Suite Layout**
- Bucket folders match `[NN]_[Name]/` under `evals/suite/`
- Test folders match `T[NN]_[Name]/` under their bucket
- Runner and evaluator code lives in `evals/suite/runner/`
- Folders not matching the bucket pattern are excluded from test discovery

**LANATEST-FR-02: Test Case Definition**
- Every test has `TEST.md`, a `PROMPTS.md` with at least one fenced prompt, `workspace/` scaffold, and `expected/manifest.yaml`
- `expected/checks.yaml` required for all tests; `expected/rubric.md` required only for tests with Tier 3 enabled
- `TEST.md` states: goal, expected outcome summary, applicable tiers, pass thresholds, golden production instructions
- Prompt sequences: multiple fences in `PROMPTS.md`, executed in file order within the same agent session

**LANATEST-FR-03: Workspace Isolation**
- Runner copies `workspace/` scaffold to a fresh working directory per test before execution
- Bucket 1 scaffolds contain empty `.lana/` (rules/, workflows/, skills/ present but empty)
- Buckets 2-3 scaffolds contain the IPPS content under test (workflows, skills, rules)
- No state leaks between tests: each test gets its own working directory and `.lana-data/`

**LANATEST-FR-04: Prompt Queue Execution**
- Runner passes the test's `PROMPTS.md` to headless Lana via a prompt-file option (JSONL output); Lana executes the queue sequentially within ONE session, one turn per prompt
- Lana emits a prompt-boundary event (queue index, prompt digest) before each turn so the runner can segment events per step
- Per-step timeout configurable per test in `TEST.md` metadata; default 300 seconds. Enforcement: the queue runs in ONE process, so the runner monitors stdout event progress and kills the process when no event arrives within the timeout (remaining steps abandoned by construction)
- Runner sets the ExecutionPolicy per test from `TEST.md` metadata (default: `turbo` for unattended runs); the agent-side denylist stays enforced under every policy
- On step failure (crash, timeout, non-zero exit), remaining queue entries are abandoned and the test is scored with recorded evidence

**LANATEST-FR-05: Run Recording**
- Every run creates `evals/runs/[YYYY-MM-DD]_[HH-MM]_[Scope]/` containing REPORT.md, results.json, and one TestRunRecord per executed test
- TestRunRecord captures final workspace, queue stdout events, and session event logs
- Run folders are immutable: the runner never modifies an existing run folder

**LANATEST-FR-06: Tier 1 - Structural Evaluation**
- StructureEvaluator checks the final workspace against `manifest.yaml`: file presence (globs), forbidden files, required sections, format patterns, minimum counts
- Every check yields pass/fail with the violated expectation named
- Tier 1 score = passed checks / total checks

**LANATEST-FR-07: Tier 2 - Process Evaluation**
- ProcessEvaluator audits session event logs against `checks.yaml`: tool calls made, execution order, evidence of required actions (file read before edit, verification executed, sources actually fetched)
- Every check yields pass/fail plus the matched or missing evidence reference
- Tier 2 score = weighted by severity: CRITICAL fail caps the tier score at 0.5

**LANATEST-FR-08: Tier 3 - Content Quality Evaluation**
- QualityEvaluator submits output files plus `rubric.md` to a fixed judge model and receives dimension scores (0-100) with justifications
- Rubric anchors quality expectations with excerpts from `golden/`; the judge never receives the full golden folder as a diff target
- Judge transcripts stored in the TestRunRecord for audit
- Tier 3 score = mean of dimension scores / 100

**LANATEST-FR-09: Scoring and Report**
- Per-test result: tier scores + overall pass/fail against per-test thresholds from `TEST.md`
- Default thresholds: Tier 1 >= 0.9, Tier 2 >= 0.7, Tier 3 >= 0.7 (overridable per test)
- `results.json` contains all scores, check-level details, and run metadata (Lana version, model, timestamps)
- `REPORT.md` lists per-bucket summary, per-test tier scores, and all failed checks

**LANATEST-FR-10: Golden Production Mode**
- Every test is executable by a human driving Cascade + IPPS in Windsurf: open scaffold copy as workspace, paste the fenced prompts from `PROMPTS.md` in order, copy resulting output into `golden/`
- `TEST.md` documents this procedure per test including which files belong in `golden/`
- Manifest distillation: `manifest.yaml` is authored from golden output + prompt requirements, separating normative properties (structure, counts, formats) from incidental ones (wording, tool names)

**LANATEST-FR-11: Bucket 1 Catalog - Basics**
- Single-prompt tests exercising internal tools with increasing difficulty: file creation, file editing, search, shell execution, multi-file refactoring
- Multi-prompt sequences where each step consumes the previous step's output
- Tiers 1-2 only; every outcome deterministic and machine-checkable

**LANATEST-FR-12: Bucket 2 Catalog - Workflows and Skills**
- Single-prompt tests verifying workflow existence and instruction following for basic IPPS workflows (at minimum: `/prime`, `/session-new`, `/write-spec`, `/verify`, `/commit`)
- Multi-prompt sequences testing workflow chains achievable only via sequences: `/verify` → `/improve`, `/critique` → `/reconcile` → `/implement`, `/drift-detect` → `/drift-correct`
- Sequence goals exploit that CRIV findings are prompt-inherent (CSRCMP-IN10 H4): methodological findings are predictable and checkable
- Tiers 1-2 mandatory; Tier 3 for workflow outputs with quality dimensions (critique depth, spec completeness)

**LANATEST-FR-13: Bucket 3 Catalog - Advanced Capabilities**
- Full `/deep-research` test: research question with an unambiguous headline answer (CSRCMP-IN10: unambiguous questions converge, CC-1=1.00), scored on structure (files, sources registry, citation format), process (searches executed, URLs fetched, source archiving), and quality (rubric + meta-criteria)
- Full `/transcribe` test: local fixture inputs (PDF, HTML snapshot) with known content, scored on structural completeness and content fidelity against the fixture
- Tier 3 mandatory for both; content-level golden diffing prohibited

**LANATEST-FR-14: Test Selection**
- Runner accepts a scope argument: single test key, bucket folder name, or all
- Evaluation is re-runnable from an existing run folder without re-executing the agent (re-scoring after evaluator fixes)

## 5. Non-Functional Requirements

**LANATEST-NFR-01: Determinism**
- Tiers 1-2 produce identical scores for identical run records
- Verification: re-evaluate the same run record twice, assert equal results.json scores

**LANATEST-NFR-02: Cost Control**
- LLM cost incurred only by the agent under test and Tier 3 judge calls
- Judge calls bounded: one call per rubric dimension group per test, no retries beyond 2

**LANATEST-NFR-03: Security**
- API keys never written into run records; runner sanitizes recorded environment metadata
- Verification: scan run folder for configured key values after each run (reuse the leak assertion pattern from the existing test harness)

**LANATEST-NFR-04: Portability of Evaluation**
- Tier 1-2 evaluation runs offline (no network)
- Suite runs on Windows (primary) without OS-specific paths in test definitions

## 6. Design Decisions

**LANATEST-DD-01:** Three-tier GRUC-mirrored evaluation (Alternative B). Rationale: reference agent evidence shows output structure (~97%) and process discipline (~45%) are different reliability tiers requiring different measurement; GRUC already separates output rules from process checks (GRUC-IN01).

**LANATEST-DD-02:** Golden output anchors rubrics and distills manifests; it is never a diff target. Rationale: reference agent self-overlap is 15% on sources, 0% on queries (CSRCMP-IN10) - diffing would fail correct outputs.

**LANATEST-DD-03:** Tier 2 evidence source is Lana's flushed session event log. Rationale: session JSONL is the exact "action evidence" GRUC CHECKS require; it exists already and survives agent crashes.

**LANATEST-DD-04:** Expectations split into machine-readable YAML (`manifest.yaml`, `checks.yaml`) and human-readable `TEST.md`. Rationale: evaluators need lookup-ready constants (GRUC core insight); humans need context and golden production instructions.

**LANATEST-DD-05:** Bucket 1 has no Tier 3. Rationale: deterministic outcomes need no judge; keeps most of the suite deterministic and free.

**LANATEST-DD-06:** Run folders are timestamped and immutable; re-evaluation writes a new run folder referencing the source record. Rationale: audit trail; evaluator bugs must not corrupt historical results.

**LANATEST-DD-07:** Runner reuses the headless spawn-inject-parse pattern from the existing test harness. Rationale: proven contract (headless mode, JSONL events, session tail); DRY.

**LANATEST-DD-08:** Fixed judge model with rubric-based scoring per @skills:llm-evaluation patterns. Rationale: reduces judge non-determinism; dimension scores with justifications are auditable.

**LANATEST-DD-09:** Bucket 3 variance-band scoring (multiple golden runs, similarity bands per CSRCMP methodology) is DEFERRED. Rationale: 2-3x golden production cost; single-golden rubric anchoring suffices for MVP of the suite.

**LANATEST-DD-10:** Multi-prompt delivery via PromptQueueFile (per-prompt fence 3..9 backticks, `---` separators), not per-step CLI invocations. Rationale: one Lana invocation = one session by construction (no session-resume dependency); per-prompt fence length carries any inner fence material without escaping; commentary between separators documents steps without polluting prompts.

## 7. Implementation Guarantees

**LANATEST-IG-01:** The agent under test never reads `expected/`, `golden/`, or any evaluation criteria - scaffold copies exclude them by construction.

**LANATEST-IG-02:** A TestRunRecord contains everything needed to re-score all tiers without re-running the agent.

**LANATEST-IG-03:** Suite and runs folders are strictly separated: the runner writes only under `evals/runs/` and temp working directories, never under `evals/suite/`.

**LANATEST-IG-04:** A test with missing golden reference or missing mandatory expectation files is reported as INVALID, not as failed or passed.

## 8. Key Mechanisms

- **Manifest distillation**: golden output → human authors normative expectations (files, sections, patterns, counts) into `manifest.yaml`; incidental properties (wording, tool names) are deliberately excluded. Solves golden portability between Cascade and Lana (different agents, same standards).
- **Process audit over event logs**: `checks.yaml` entries match against session events (tool call types, arguments, ordering). Mirrors `/drift-detect` consuming CHECKS files, automated.
- **Rubric anchoring**: judge sees the run output + rubric with short golden excerpts as quality anchors, scores dimensions independently, must justify each score.
- **Threshold gating**: per-test thresholds convert tier scores into pass/fail; CRITICAL process check failures cap Tier 2 (a passed-looking output with faked process must not pass).
- **Unambiguous-answer prompt design**: Bucket 3 research questions are chosen so headline conclusions converge across runs, making conclusion checks stable despite content variance.

## 9. Action Flow

```
User runs suite with scope
├─> Discover tests matching scope in evals/suite/
├─> Create run folder evals/runs/[timestamp]_[Scope]/
├─> Per test:
│   ├─> Copy workspace/ scaffold to fresh working directory
│   ├─> Execute headless Lana with PROMPTS.md queue in working directory
│   │   ├─> Lana: per queue entry, emit prompt-boundary event + run turn
│   │   └─> Record stdout events to events.jsonl
│   ├─> Copy final workspace + session logs into TestRunRecord
│   ├─> Tier 1: StructureEvaluator(workspace, manifest.yaml)
│   ├─> Tier 2: ProcessEvaluator(session logs, checks.yaml)
│   ├─> Tier 3 (if rubric.md exists): QualityEvaluator(output, rubric) via judge
│   └─> Score against thresholds → pass | fail | invalid
└─> Aggregate → results.json + REPORT.md
```

## 10. Data Structures

**manifest.yaml (Tier 1) example:**
```yaml
required_files:
  - "_INFO_*.md"
  - "_SOURCES/*.md"
forbidden_files:
  - "*.tmp"
file_rules:
  - glob: "_INFO_*.md"
    required_sections: ["## Summary", "## Sources", "## Document History"]
    patterns:
      - name: doc_id
        regex: "\\*\\*Doc ID\\*\\*: [A-Z]{2,14}-IN[0-9]{2}"
    min_count:
      "## Summary": 1
```

**checks.yaml (Tier 2) example:**
```yaml
checks:
  - id: read_before_edit
    action: "Agent read target file before editing it"
    evidence: "tool_call read on path precedes tool_call edit on same path"
    failure_indicator: "edit event without prior read event for path"
    severity: CRITICAL
  - id: web_search_executed
    action: "Agent executed at least 3 web searches"
    evidence: "3+ tool_call events of type web_search"
    failure_indicator: "fewer than 3 web_search events"
    severity: HIGH
```

**PROMPTS.md (PromptQueueFile) example (full format: `docs/PROMPT_FILE_FORMAT.md`):**

`````````text
`````
Create `calc.py` with an `add(a, b)` function. Use this docstring format:

````markdown
Example:
```python
add(1, 2)  # 3
```
````
`````

---

## Step 2: extend it

```
Add a `multiply(a, b)` function to `calc.py` following the same docstring format.
```
`````````

**results.json (excerpt) example:**
```json
{"run": "2026-08-30_19-00_01_Basics", "tests": [{"key": "01-T01", "tier1": 1.0, "tier2": 0.83, "tier3": null, "status": "pass", "failed_checks": ["web_search_executed"]}]}
```

## 11. Logging Requirements

**Applicable logging types:**
- [x] Script-Level (SC) - `LOGGING-RULES-SCRIPT-LEVEL.md`

**Script-Level logging:**
- **Audience**: User running the suite from the terminal
- **Goal**: Know which test is executing, step progress, tier scores, and every failure reason from logs alone
- **Key operations**: test discovery, scaffold copy, prompt step execution, tier evaluation, report writing

**Expected output for a suite run:**
```
Running scope '01_Basics' (5 tests)...
  [ 1 / 5 ] 01-T01 CreateFile...
    Step [ 1 / 1 ] executed (12.4s).
    Tier 1: 1.00 (8/8 checks) | Tier 2: 1.00 (3/3 checks)
    PASS.
  [ 2 / 5 ] 01-T02 EditSequence...
    Step [ 2 / 3 ] FAILED: timeout after 300s.
    Tier 1: 0.50 (4/8 checks) | Tier 2: 0.67 (2/3 checks)
    FAIL: step timeout, manifest violations: missing '_INFO_RESULT.md'.
Run recorded: evals/runs/2026-08-30_19-00_01_Basics
RESULT: 4 passed, 1 failed, 0 invalid.
```

## 12. Technical Constraints

- Lana headless contract: prompt injection via CLI flag, JSONL AgentEvents on stdout, session events flushed to `.lana-data/sessions/` (LANAAGNT-SP01)
- The agent under test requires live LLM backend credentials; evaluators (Tiers 1-2) must not
- Golden production is a manual Windsurf procedure - no Cascade API exists; TEST.md instructions are the automation boundary
- Prompt queue support is specced as `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` FR-12 (`--prompt-file`, fence parsing, `prompt_step` events) - implemented and tested 2026-08-30 (LANAACPB-IP01 Phase 7, VC-13) [PROVEN]
- Bucket 3 transcribe fixtures are stored inside the test's `workspace/` (local PDFs, HTML snapshots) to remove network flakiness
- Existing `tests/harness.py` patterns (spawn, JSONL parse, session tail, secret-leak assertion) constrain runner design as prior art
- Lana zero-setup: a MISSING `.lana/` folder is auto-filled with the bundled prompt library; an existing (even empty) folder stays untouched - Bucket 1 scaffolds therefore ship the empty folder [VERIFIED: cli.py]
- `ask_user_question` in headless mode returns the non-interactive fallback ("no answer") without blocking [VERIFIED: interact_tools.py] - test prompts must not depend on interactive answers
- Session JSONL tool events carry full arguments (`tool_call_requested`: tool + args; `tool_call_finished`: status + result) - Tier 2 path-level and count-level checks are evaluable [VERIFIED: events.py]

## 13. Document History

**[2026-08-30 19:55]**
- Changed (`/verify` findings): FR-04 - per-step timeout enforcement mechanism (stdout progress monitoring) and per-test ExecutionPolicy added
- Changed: MNF Bucket 1 line - empty `.lana/` MUST exist in scaffold (missing folder triggers bundled-library materialization)
- Added: 3 verified technical constraints (zero-setup interplay, headless ask_user_question fallback, tool-event argument completeness)

**[2026-08-30 19:50]**
- Changed: PromptQueueFile format synced to LANAACPB-SP01 FR-12 rework [user decision] - per-prompt fence 3..9 backticks, mandatory leading fence, `---` separators; DD-10 and PROMPTS.md example updated; format authority now `docs/PROMPT_FILE_FORMAT.md`

**[2026-08-30 19:15]**
- Added: PromptQueueFile domain object (5-backtick fence format, commentary outside fences)
- Added: LANATEST-DD-10 (queue file delivery instead of per-step CLI invocations)
- Changed: LANATEST-FR-04 renamed to Prompt Queue Execution (one Lana invocation, prompt-boundary events)
- Changed: `prompts/[NN].md` replaced by `PROMPTS.md` in TestCase, FR-02, FR-10
- Changed: TestRunRecord `events/[NN].jsonl` replaced by single `events.jsonl`
- Changed: Session-resume constraint replaced by prompt-queue-as-new-Lana-capability constraint
- Added: PROMPTS.md example in Data Structures

**[2026-08-30 19:10]**
- Initial specification created (Alternative B: three-tier GRUC-mirrored evaluation)
