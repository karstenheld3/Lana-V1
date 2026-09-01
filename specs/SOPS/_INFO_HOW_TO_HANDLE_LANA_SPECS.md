# INFO: How to Handle Lana Specs

**Doc ID**: LANASPEC-IN02
**Goal**: Define the target spec file structure and how to extend it with new features, components, and topics
**Timeline**: Created 2026-09-01

## Summary

- Every component has exactly 3 files with identical naming: `_SPEC_LANA_[NN]-[Name].md`, `_IMPL_LANA_[NN]-[Name].md`, `_TEST_LANA_[NN]-[Name].md`. No exceptions. [VERIFIED]
- 11 numbered component specs, each with its own topic ID registered in `ID-REGISTRY.md` [VERIFIED]
- SPECs define WHAT and WHY (FRs, DDs, IGs, NFRs). IMPLs define HOW (steps, edge cases). TESTs define HOW TO VERIFY (test cases) [VERIFIED]
- New features add items to existing spec triplets. New components get a new numbered triplet [VERIFIED]
- Changes follow the BUG/CHANGE classification from `_INFO_HOW_TO_IMPROVE_LANA.md [LANALOGS-IN01]`: BUGs fix code, CHANGEs anchor in SPEC first [VERIFIED]

## Table of Contents

1. [Target File Structure](#1-target-file-structure)
2. [The Pairing Rule](#2-the-pairing-rule)
3. [Topic IDs and Doc IDs](#3-topic-ids-and-doc-ids)
4. [Spec Item Types](#4-spec-item-types)
5. [Adding a Feature to an Existing Component](#5-adding-a-feature-to-an-existing-component)
6. [Adding a New Component](#6-adding-a-new-component)
7. [The Spec-IMPL-TEST Lifecycle](#7-the-spec-impl-test-lifecycle)
8. [Sources](#8-sources)
9. [Document History](#9-document-history)

## 1. Target File Structure

```
specs/
├── _SPEC_LANA_01-ProductOverview.md       [LANAAGNT-SP01]
├── _IMPL_LANA_01-ProductOverview.md       [LANAAGNT-IP01]
├── _TEST_LANA_01-ProductOverview.md       [LANAAGNT-TP01]
│
├── _SPEC_LANA_02-AgentCore.md             [LANACORE-SP01]
├── _IMPL_LANA_02-AgentCore.md             [LANACORE-IP01]
├── _TEST_LANA_02-AgentCore.md             [LANACORE-TP01]
│
├── _SPEC_LANA_03-PromptAndConfig.md       [LANAPRCF-SP01]
├── _IMPL_LANA_03-PromptAndConfig.md       [LANAPRCF-IP01]
├── _TEST_LANA_03-PromptAndConfig.md       [LANAPRCF-TP01]
│
├── _SPEC_LANA_04-Providers.md             [LANAPRVD-SP01]
├── _IMPL_LANA_04-Providers.md             [LANAPRVD-IP01]
├── _TEST_LANA_04-Providers.md             [LANAPRVD-TP01]
│
├── _SPEC_LANA_05-Tools.md                 [LANATOOL-SP01]
├── _IMPL_LANA_05-Tools.md                 [LANATOOL-IP01]
├── _TEST_LANA_05-Tools.md                 [LANATOOL-TP01]
│
├── _SPEC_LANA_06-CLI.md                   [LANACLI-SP01]
├── _IMPL_LANA_06-CLI.md                   [LANACLI-IP01]
├── _TEST_LANA_06-CLI.md                   [LANACLI-TP01]
│
├── _SPEC_LANA_07-ACP.md                   [LANAACPB-SP01]
├── _IMPL_LANA_07-ACP.md                   [LANAACPB-IP01]
├── _TEST_LANA_07-ACP.md                   [LANAACPB-TP01]
│
├── _SPEC_LANA_08-DebugConsole.md          [LANADEBG-SP01]
├── _IMPL_LANA_08-DebugConsole.md          [LANADEBG-IP01]
├── _TEST_LANA_08-DebugConsole.md          [LANADEBG-TP01]
│
├── _SPEC_LANA_09-Distribution.md          [LANADIST-SP01]
├── _IMPL_LANA_09-Distribution.md          [LANADIST-IP01]
├── _TEST_LANA_09-Distribution.md          [LANADIST-TP01]
│
├── _SPEC_LANA_10-EvalSuite.md             [LANATEST-SP01]
├── _IMPL_LANA_10-EvalSuite.md             [LANATEST-IP01]
├── _TEST_LANA_10-EvalSuite.md             [LANATEST-TP01]
│
├── _SPEC_LANA_11-Selftest.md              [LANASTST-SP01]
├── _IMPL_LANA_11-Selftest.md              [LANASTST-IP01]
├── _TEST_LANA_11-Selftest.md              [LANASTST-TP01]
│
├── _Archive/                              (superseded monolithic specs)
├── SOPS/                                  (operational guides, unchanged)
└── UXDesign/                              (design system, unchanged)
```

## 2. The Pairing Rule

**Every SPEC has exactly one IMPL and one TEST with the same filename scheme.** No exceptions.

```
_SPEC_LANA_[NN]-[Name].md     # WHAT and WHY (FRs, DDs, IGs, NFRs)
_IMPL_LANA_[NN]-[Name].md     # HOW (implementation steps, edge cases)
_TEST_LANA_[NN]-[Name].md     # HOW TO VERIFY (test cases)
```

- `[NN]` is a 2-digit number (01-99), sequential, never reused
- `[Name]` is PascalCase, identical across all 3 files
- All 3 files share the same topic ID and reference each other in their headers

**When you create a SPEC, you create the IMPL and TEST at the same time.** An unpaired SPEC is incomplete. An IMPL without a SPEC is unauthorized. A TEST without an IMPL is unanchored.

### What goes where

- **SPEC** - Requirements (FR-NN), design decisions (DD-NN), guarantees (IG-NN), non-functional requirements (NFR-NN), domain objects, key mechanisms
- **IMPL** - Implementation steps (IS-NN), edge cases (EC-NN), verification checklist (VC-NN). Each IS references the FR(s) it implements
- **TEST** - Test cases (TC-NN). Each TC references FR(s) and IS(s). Expected outcomes, test infrastructure

## 3. Topic IDs and Doc IDs

Every component has a **topic** (7-14 uppercase chars) registered in `ID-REGISTRY.md`:

```
LANAAGNT  - Product Overview (domain model, architecture)
LANACORE  - Agent Core (turn loop, session, compaction, safety)
LANAPRCF  - Prompt and Configuration
LANAPRVD  - Provider Adapters
LANATOOL  - Tool System
LANACLI  - CLI Frontend
LANAACPB  - ACP Bridge
LANADEBG  - Debug Console
LANADIST  - Distribution
LANATEST  - Eval Suite
LANASTST  - Selftest
```

### Doc IDs per file type

```
[TOPIC]-SP[NN]    SPEC         e.g. LANACORE-SP01
[TOPIC]-IP[NN]    IMPL plan    e.g. LANACORE-IP01
[TOPIC]-TP[NN]    TEST plan    e.g. LANACORE-TP01
```

### Item IDs within specs

```
[TOPIC]-FR-[NN]   Functional Requirement     e.g. LANACORE-FR-04
[TOPIC]-DD-[NN]   Design Decision            e.g. LANACORE-DD-05
[TOPIC]-IG-[NN]   Implementation Guarantee   e.g. LANACORE-IG-02
[TOPIC]-NFR-[NN]  Non-Functional Requirement e.g. LANACORE-NFR-01
```

Items are numbered sequentially within their type. Never renumber existing IDs -- source code references them.

## 4. Spec Item Types

- **FR (Functional Requirement)** - What the system does. Observable behavior. "When X happens, Y results." Each FR is testable.
- **DD (Design Decision)** - Why a specific approach was chosen over alternatives. Records the rationale so future developers do not re-debate settled questions.
- **IG (Implementation Guarantee)** - Invariants the code MUST maintain. Stronger than FRs -- these are contracts. "X is ALWAYS true, regardless of [conditions]."
- **NFR (Non-Functional Requirement)** - Quality attributes: security, performance, reliability, observability.

### Verification labels

Items carry labels showing their verification state. Progression: `[ASSUMED]` -> `[VERIFIED]` -> `[TESTED]` -> `[PROVEN]`.

## 5. Adding a Feature to an Existing Component

**When**: The new feature belongs to an existing component (same source files, same change boundary).

1. **Identify the triplet** - Which component owns the source files this feature touches?
2. **SPEC** - Append FR with next sequential number. Add DDs and IGs if needed.
3. **IMPL** - Add implementation steps (IS-NN), edge cases (EC-NN), verification checklist items (VC-NN).
4. **TEST** - Add test cases (TC-NN) covering the new FR.
5. **Document History** - Update in all 3 files.

**Example**: Adding a new tool to Lana:
- SPEC: Add `LANATOOL-FR-05` to `_SPEC_LANA_05-Tools.md`
- IMPL: Add steps to `_IMPL_LANA_05-Tools.md`
- TEST: Add cases to `_TEST_LANA_05-Tools.md`

## 6. Adding a New Component

**When**: The feature has its own source files, changes independently, and is large enough (>5 FRs or >10KB estimated spec size).

1. **Register topic** - Add a new 7-14 char topic to `ID-REGISTRY.md`.
2. **Pick the next number** - Use the next available `[NN]` (currently 12+).
3. **Create all 3 files** - SPEC, IMPL, TEST with identical `_[TYPE]_LANA_[NN]-[Name].md` naming.
4. **SPEC** - Use `/write-spec`. Header: Doc ID, Goal, Timeline, Target files, Depends on, Does not depend on.
5. **IMPL** - Use `/write-impl-plan`. Reference SPEC item IDs.
6. **TEST** - Use `/write-test-plan`. Reference both SPEC and IMPL items.

**Decision guide: extend existing vs. new component**

```
Does the feature share source files with an existing spec?
├── Yes -> extend existing triplet (section 5)
└── No ->
    Does it change independently from all existing specs?
    ├── Yes -> new triplet (section 6)
    └── No -> extend the triplet it changes with most often
```

## 7. The Spec-IMPL-TEST Lifecycle

### New feature lifecycle

```
1. SPEC anchor   - Add FR/DD/IG to the SPEC (the "why")
2. IMPL update   - Add IS/EC/VC steps (the "how")
3. TEST update   - Add TC cases (the "verify")
4. Implement     - Write code following IMPL steps
5. Test          - Run tests following TEST plan
6. Sync back     - Update SPEC/IMPL/TEST if implementation revealed gaps
7. Commit        - All 3 docs + code in one atomic commit
```

### Sync rules

- **SPEC is the authority** for what the system should do
- **Code changes that contradict SPEC** -> fix the code (BUG) or update the SPEC first (CHANGE). See `_INFO_HOW_TO_IMPROVE_LANA.md [LANALOGS-IN01]` for the full pipeline.
- **Never change code without updating the corresponding SPEC/IMPL/TEST**
- **Document History** sections in all 3 files must reflect every change

### When to update vs. when to create new

- **New FR in existing component** -> update all 3 files
- **New component** -> create all 3 files
- **Bug fix** -> SPEC stays (unless fix reveals a gap), update IMPL/TEST with new scenario
- **Refactor** -> no SPEC change if behavior is unchanged, update IMPL if steps changed

## 8. Sources

- `LANASPEC-IN02-SC-SPECINFO`: `_INFO_LANASPEC_01.md [LANASPEC-IN01]` - Spec restructure analysis, Option C (10 component specs) [VERIFIED]
- `LANASPEC-IN02-SC-IDREG`: `ID-REGISTRY.md` - Topic registration, ID format rules [VERIFIED]
- `LANASPEC-IN02-SC-IMPROVE`: `specs/SOPS/_INFO_HOW_TO_IMPROVE_LANA.md [LANALOGS-IN01]` - BUG/CHANGE classification, evidence-driven pipeline [VERIFIED]

## Document History

**[2026-09-01 21:55]**
- Changed: 10 -> 11 components (11-Selftest separated from 06-CLI per LANASTST topic)
- Added: LANASTST to topic registry, 11-Selftest to file tree, _Archive/ folder
- Removed: Next Steps section (migration complete)
- Changed: Next available NN from 11+ to 12+

**[2026-09-01 21:25]**
- Rewritten: Focus on target state (10 component triplets), strict pairing rule, target file tree
- Removed: Current-state listing (documented in `_INFO_LANASPEC_01.md`)

**[2026-09-01 21:00]**
- Initial document created
