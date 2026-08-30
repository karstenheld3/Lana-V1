# Session Progress

**Doc ID**: LANATEST-PROGRESS

## Phase Plan

- [x] **EXPLORE** - done: read IPPS concept docs + CSRCMP-IN10 research, inventoried 46 workflows / 23 skills, proposed 3 alternatives, user chose B
- [ ] **DESIGN** - in_progress: `_SPEC_LANA_EVAL_SUITE.md [LANATEST-SP01]` created; pending: user review, then IMPL + prompt catalogs
- [ ] **IMPLEMENT** - pending: create test prompts, workspace scaffolds, evaluation scripts
- [ ] **VERIFY** - pending: produce golden outputs with Cascade + IPPS, validate evaluation harness
- [ ] **RELEASE** - pending: integrate into CI or manual test run process

## To Do

- [ ] Inventory all workflows and skills in `.lana/` and `.devin/`
- [ ] Categorize workflows into Bucket 2 (basic IPPS) vs. Bucket 3 (special Lana)
- [ ] Research evaluation approaches for non-deterministic LLM outputs
- [ ] Design folder structure for test suite (prompts, scaffolds, golden outputs)
- [ ] Design evaluation harness architecture
- [ ] Define Bucket 1 prompt catalog (tool usage, increasing difficulty)
- [ ] Define Bucket 2 prompt catalog (workflow/skill testing)
- [ ] Define Bucket 3 prompt catalog (deep-research, transcribe)
- [ ] Produce golden reference outputs using Cascade + IPPS

## In Progress

- (none yet)

## Done

- [x] 2026-08-30: Lana prompt queue implemented (LANAACPB-SP01 FR-12, IP01 Phase 7 IS-14/15) - parser, --prompt-file, prompt_step event; 15 new tests, full suite 265 offline green (VC-13, TP01-VC-07)
- [x] Session initialized (2026-08-30)

## Tried But Not Used

- (none yet)
