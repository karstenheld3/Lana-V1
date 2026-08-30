# Session Notes

**Doc ID**: LANATEST-NOTES

## Initial Request

````text
we need an evaluation suite for our agent. 

That means we need 3 buckets of prompts with predictable outcomes:

Bucket 1: Independent of used DevSystem and rules in .lana folder
1. Single prompts that ask the agent to do something using its tools with increasing difficulty
2. Multi-prompt sequences that build on the outout of the previous step

Bucket 2: Basic workflows and skills
1. Single prompts that test the existence and instruction following quality of the basic IPPS workflows and skills
2. Multi-prompt sequences that test workflows like verify.md, critique.md, reconcile.md, implement.md, drift-detect.md and drift-correct.md as sequences. The goal here is to state goals that can only be achieved using a sequence of workflows

Bucket 3: Special Lana capabilities
1. Full test of deep-research.md workflow and skill
2. Full test of transcribe.md workflow and skill

For each test (prompt or prompt sequence we need a reference output folder structure that was created using a state-of-the-art agent like Devin Cascade.

That means the entire test suite must be designed so that we can produce the reference "golden" outout using Cascade + IPPS.
````

## Session Info

- **Started**: 2026-08-30
- **Goal**: Design an external test suite for the Lana agent with 3 prompt buckets, predictable outcomes, and golden reference outputs produced by Cascade + IPPS
- **Operation Mode**: IMPL-ISOLATED
- **Output Location**: [SESSION_FOLDER]

## Agent Instructions

- This is a DESIGN session. Do not implement until user confirms the design.
- Golden reference outputs must be producible by Cascade + IPPS (the DevSystem the user already runs in Windsurf).
- Test prompts must have predictable, verifiable outcomes - not open-ended creative tasks.
- Bucket 1 must work without any `.lana/` content (tests raw agent tool usage).
- Bucket 2 tests IPPS workflows/skills that exist in `.lana/` (or `.devin/`).
- Bucket 3 tests Lana-specific deep-research and transcribe capabilities.
- Evaluation must handle LLM non-determinism (structural checks, not exact string matching).

## References

**IPPS** (`e:\Dev\IPPS`):
- How Drift Prevention works: `e:\Dev\IPPS\Docs\Concepts\_INFO_AGENT_DRIFT_PREVENTION_APPROACH.md`
- What to look for when detecting weak audit trails: `e:\Dev\IPPS\Docs\Concepts\_INFO_HOW_TO_CREATE_AUDITABLE_RESEARCH_SUMMARIES.md`
- How IPPS guarantees high instruction following: `e:\Dev\IPPS\Docs\Concepts\_INFO_GRUC_GUIDES_RULES_CHECKS.md`
- APAPALAN principle: `e:\Dev\IPPS\Docs\Concepts\_INFO_APAPALAN_PRINCIPLE.md`
- MECT philosophy: `e:\Dev\IPPS\Docs\Concepts\_INFO_MECT_PHILOSOPHY.md`

**Existing research** (deep-research workflow + skill instruction following, different agents):
- `E:\Dev\KarstensWorkspace\_Sessions\_Archive\_2026-05-30_WindsurfDevinResearchComparison\T01_CascadeResultComparison\_INFO_CASCADE_RESULT_COMPARISON_SUMMARY.md`

## Key Decisions

- **[2026-08-30]** Alternative B chosen: three-tier GRUC-mirrored evaluation (Tier 1 STRUCTURE manifest checks, Tier 2 PROCESS audit over session event logs, Tier 3 QUALITY LLM-judge with golden-anchored rubric). Spec: `_SPEC_LANA_EVAL_SUITE.md [LANATEST-SP01]`
- **[2026-08-30]** Suite location `evals/suite/`, run records `evals/runs/[YYYY-MM-DD]_[HH-MM]_[Scope]/` (user-created scaffolds define naming)
- **[2026-08-30]** Bucket folders: `01_Basics`, `02_WorkflowsSkills`, `03_AdvancedCapabilities`
- **[2026-08-30]** Golden output = rubric anchor + manifest distillation source, never diff target (CSRCMP-IN10 evidence)
- **[2026-08-30]** Bucket 3 variance-band scoring (multiple golden runs) deferred (LANATEST-DD-09)
- **[2026-08-30]** Multi-prompt tests use PromptQueueFile `PROMPTS.md`: per-prompt fence 3..9 backticks (author picks fence longer than deepest inner fence), file MUST start with a fence, `---` separator between prompts, commentary only between separator and next fence, one Lana invocation runs the whole queue in one session (LANATEST-DD-10). Specced as LANAACPB-FR-12 (`--prompt-file`, `prompt_step` event) with IMPL Phase 7 (IS-14/15, TC-45..49) and TEST Category 6 (TP01-TC-12/13) - implementation pending. Format doc: `docs/PROMPT_FILE_FORMAT.md`

## Important Findings

**From `_INFO_CASCADE_RESULT_COMPARISON_SUMMARY.md [CSRCMP-IN10]` (4 identical Cascade runs):**
- Output structure compliance ~97%, process discipline ~45% → two tiers need different evaluation methods
- Deep-research content is non-reproducible: Query Jaccard 0.000, Source Jaccard 0.147, Event Jaccard 0.242 → exact golden-output diff is IMPOSSIBLE for Bucket 3
- Headline conclusions reproducible (CC-1=1.00) when question has unambiguous answer → design prompts with unambiguous answers
- 7 prompt-independent meta-criteria predict instruction-following quality (Prompt Decomposition, Current/Target Comparison, Constraint Re-reading, Self-Correction, Backtracking, Strategy Justification, Quantitative Completeness Threshold)
- CRIV findings are prompt-inherent (methodological), not content-dependent → critique/reconcile outputs ARE predictable

**From `_INFO_GRUC_GUIDES_RULES_CHECKS.md [GRUC-IN01]`:**
- RULES = verifiable from output alone (maps to structural evaluation); CHECKS = requires action evidence (maps to process evaluation over session logs)
- Boundary Test: "Can I verify this by reading the delivered files?" Yes → RULES-style check; No → CHECKS-style audit

**Workspace facts:**
- `tests/harness.py` `LanaProc` already runs headless Lana (`-p` + `--output-format jsonl`), captures AgentEvents, reads flushed `.lana-data/sessions/*.jsonl` → action evidence for process audits exists
- `.lana/workflows/` has 46 workflows; `.lana/skills/` has 23 skills (deep-research fully populated: SKILL.md, RULES, strategies, templates)

## Topic Registry

**Global topics** (registered in ID-REGISTRY.md):
- `LANATEST` - Lana External Test Suite

**Subtopics** (session-local):
- (none yet)

## Topic Folders

- (none yet)

## Step Folders

- (none yet)

## Bug List

- (none yet)

## Significant Prompts Log

- (none yet)

## Current Phase

**Phase**: EXPLORE
**Workflow**: (pending assessment)
**Assessment**: (pending)
