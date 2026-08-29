# Failure Log

Records mistakes and lessons learned in this session to prevent repetition.

**Goal**: Document failures, mistakes, and lessons learned to prevent repetition

## Table of Contents

1. [Active Issues](#active-issues)
2. [Resolved Issues](#resolved-issues)
3. [Document History](#document-history)

## Active Issues

- (none)

## Resolved Issues

### 2026-08-29 - IMPL plan improvement run

#### [RESOLVED] `LANAAGNT-FL-0003` Edit old_string composed from memory hit the wrong document region

- **Original severity**: [MEDIUM]
- **Resolved**: 2026-08-29 22:12
- **Solution**: During `/improve` run 2, a multi_edit targeted a "wire-capture derived" constraint line that exists in the SPEC, not in the IMPL being edited; the fuzzy matcher rewrote the IMPL's Depends-on bullet instead, leaving hybrid garbage text. Same pattern as the earlier FR-13 insert that consumed the section 5 heading. Both caught by post-edit review of returned file views. Lesson: before multi_edit, confirm each old_string against the CURRENT file (read or search the exact line), especially when two session documents share similar phrasing; always read the returned diff views instead of assuming success
- **Link**: `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` Document History 2026-08-29 22:08; repair at 22:12

### 2026-08-29 - Lana MVP-1 SPEC creation

#### [RESOLVED] `LANAAGNT-FL-0002` DD-04 decided without researching the gpt-5.4+ Chat Completions restriction

- **Original severity**: [HIGH]
- **Resolved**: 2026-08-29 21:35
- **Solution**: DD-04 reversed to the Responses API in `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` (Document History 2026-08-29 21:35), verified against the OpenAI migration guide. Lesson retained: any design decision that DEVIATES from a researched leaning requires its own verification research, not just a rationale sentence
- **Link**: `LANAAGNT-SP01` DD-04; original analysis was in `_SPEC_LANA_MVP-1_REVIEW.md [LANAAGNT-SP01-RV01]` RF-01 (review file deleted by `/cleanup` after implementation)

### 2026-08-29 - Design questions INFO document

#### [RESOLVED] `LANAAGNT-FL-0001` Stale cross-references after question renumbering

- **Original severity**: [MEDIUM]
- **Resolved**: 2026-08-29 20:52
- **Solution**: While drafting `LANAAGNT-IN01`, question IDs were renumbered during writing but 3 prose cross-references kept old numbers (OQ-35 vs OQ-40, OQ-27/30 vs OQ-33/34, OQ-26 vs OQ-32); `/verify` caught and fixed all. Lesson: after renumbering any ID scheme, sweep ALL prose references with a search before finishing (`Select-String 'OQ-\d\d'`)
- **Link**: `_INFO_OPEN_DESIGN_QUESTIONS.md [LANAAGNT-IN01]` Document History 2026-08-29 20:52

## Document History

**[2026-08-29 21:35]**
- Changed: LANAAGNT-FL-0002 marked [RESOLVED] (DD-04 reversed to Responses API)

**[2026-08-29 21:28]**
- Initial failure log created: LANAAGNT-FL-0001 (resolved), LANAAGNT-FL-0002 (active)
