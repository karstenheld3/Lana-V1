# Failure Log

Records mistakes and lessons learned to prevent repetition.

**Goal**: Document failures, mistakes, and lessons learned to prevent repetition

## Active Issues

- (none)

## Resolved Issues

### 2026-08-29 - IMPL plan improvement run

#### [RESOLVED] `LANAAGNT-FL-0003` Edit old_string composed from memory hit the wrong document region

- **Original severity**: [MEDIUM]
- **Resolved**: 2026-08-29 22:12
- **Solution**: During `/improve` run 2, a multi_edit targeted a constraint line from the SPEC while editing the IMPL; the fuzzy matcher rewrote the wrong bullet. Lesson: before multi_edit, confirm each old_string against the CURRENT file, especially when two session documents share similar phrasing; always read the returned diff views
- **Link**: `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` Document History 2026-08-29 22:08

### 2026-08-29 - Lana MVP-1 SPEC creation

#### [RESOLVED] `LANAAGNT-FL-0002` DD-04 decided without researching the gpt-5.4+ Chat Completions restriction

- **Original severity**: [HIGH]
- **Resolved**: 2026-08-29 21:35
- **Solution**: DD-04 reversed to the Responses API in SP01. Lesson: any design decision that DEVIATES from a researched leaning requires its own verification research
- **Link**: `LANAAGNT-SP01` DD-04
