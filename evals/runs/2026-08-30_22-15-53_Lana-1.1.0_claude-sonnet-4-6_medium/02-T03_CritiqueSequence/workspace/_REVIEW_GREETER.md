# _SPEC_GREETER_REVIEW.md

**Doc ID**: GREETER-SP01-RV01
**Goal**: Document potential issues, risks, and logic flaws in `_SPEC_GREETER.md [GREETER-SP01]`
**Timeline**: Created 2026-08-30
**Reviewed**: 2026-08-30 22:19
**Context**: Devil's Advocate review of CLI greeter tool specification

## Table of Contents

1. [Critical Issues](#critical-issues)
2. [High Priority](#high-priority)
3. [Medium Priority](#medium-priority)
4. [Low Priority](#low-priority)
5. [Industry Research Findings](#industry-research-findings)
6. [Recommendations](#recommendations)
7. [Document History](#document-history)

## Critical Issues

### `GREETER-RV-001` Language Count Contradiction — ✅ ACCEPTED

> Rationale: Direct textual contradiction confirmed in spec lines 12 and 18; no interpretation resolves it without choosing a side.

- **Location**: Section 1 ("Supports exactly two languages: English and German") vs GREETER-FR-01 ("The three supported languages each have a fixed greeting word")
- **What**: The scenario declares exactly two languages. GREETER-FR-01 refers to "three supported languages." These are contradictory statements in the same document.
- **Risk**: Any implementation will resolve this ambiguity silently by picking one count. The result is a tool that either implements 2 or 3 languages with no way to verify which is correct. Both implementations can claim compliance with part of the spec.
- **Evidence**: SOCAS-01 HIGH - direct contradiction within one document. "exactly two" vs "three supported languages."
- **Suggested action**: Pick one count, remove the other claim. If three languages are intended, name all three explicitly in Section 1.

### `GREETER-RV-002` Third Language Never Defined — ✅ ACCEPTED

> Rationale: The spec names a count of three but supplies only two languages; the third is entirely absent, making GREETER-FR-01 unimplementable.

- **Location**: GREETER-FR-01
- **What**: GREETER-FR-01 references "three supported languages each have a fixed greeting word" but only two languages (English, German) are named anywhere in the spec. The third language and its greeting word are completely absent.
- **Risk**: An implementer cannot implement a requirement for a language that has no definition. This requirement is unimplementable as written. Any implementation must invent the third language, making the result arbitrary.
- **Evidence**: SOCAS-06 HIGH - implicit assumption left unstated; the spec is incomplete on a named feature.
- **Suggested action**: Name the third language explicitly and provide its greeting word, or correct the count to two.

## High Priority

### `GREETER-RV-003` Error Handling Is Unmeasurable — ✅ ACCEPTED

> Rationale: "Handles errors appropriately" is a placeholder, not a requirement; it specifies no conditions, outputs, or exit codes, and cannot be tested.

- **Location**: GREETER-FR-02
- **What**: "The tool handles errors appropriately" provides zero specification. It names no error conditions, specifies no exit codes, no error messages, and no behavior distinctions between error types (e.g., missing name argument, unsupported language, invalid input).
- **Risk**: This requirement cannot be tested. Two implementations with entirely opposite error-handling behaviors both satisfy "handles errors appropriately." The word "appropriately" is undefined relative to any standard or expectation.
- **Evidence**: SOCAS-06 HIGH - no distinction between MUST, SHOULD, MAY; edge case behavior unspecified. Industry standard (POSIX) requires exit code 0 for success, non-zero for failure; none of this is referenced.
- **Suggested action**: Enumerate each error condition (unknown language, missing name, empty name), specify the exact output (stderr vs stdout), and specify the exit code for each case.

### `GREETER-RV-004` CLI Interface Not Specified — ✅ ACCEPTED

> Rationale: A CLI spec with no invocation syntax guarantees interface divergence; this is the most actionable single fix in the document.

- **Location**: Entire document
- **What**: The spec names a `greeter` command but never specifies how it is invoked. No argument names, no flags, no positional vs named arguments, no required vs optional parameters, and no usage example are given.
- **Risk**: Implementations will diverge on the interface. One implementer may write `greeter --name Alice --lang en`, another `greeter en Alice`, another `greeter Alice en`. None can be called wrong because the spec provides no constraint.
- **Evidence**: SOCAS-06 HIGH - implicit assumptions left unstated. SOCAS-10 - conclusion (it is a CLI tool) is not supported by any described mechanism.
- **Suggested action**: Add a CLI interface section specifying argument names, order, whether flags or positional, and at least one usage example: `greeter --name <name> --lang <en|de>`.

## Medium Priority

### `GREETER-RV-005` No Acceptance Criteria — ✅ ACCEPTED (reduced scope)

> Rationale: Real gap, but largely resolved once RV-003 and RV-004 are fixed; retain the stdout/encoding sub-point only — drop the broader "definition of done" framing as redundant.

- **Location**: Entire document
- **What**: Neither functional requirement has a testable success condition. There is no definition of done. GREETER-FR-01 says what to print but does not specify to which stream (stdout vs stderr), does not specify character encoding, and does not specify what happens for a valid name with trailing whitespace.
- **Risk**: Without acceptance criteria, QA and automated tests have no ground truth. A test suite cannot be written that is guaranteed to match the specifier's intent.
- **Evidence**: SOCAS-06 MEDIUM - success criteria not measurable or testable.
- **Suggested action**: Add an "Acceptance Criteria" subsection per requirement, or add a "Done When" section at the spec level with at least one passing and one failing example per requirement.

### `GREETER-RV-006` Output Format Ambiguity — ✅ ACCEPTED (partial)

> Rationale: Name pass-through vs normalisation is a real silent divergence risk; the angle-bracket template syntax concern is dismissed — convention makes the intent clear enough for a simple format string.

- **Location**: GREETER-FR-01 - "Prints `<greeting>, <name>!`"
- **What**: The format pattern uses angle-bracket placeholders but does not define whether `<greeting>` and `<name>` are literal angle-bracket tokens or template variable syntax. More importantly, it does not specify case normalization: if the user provides `alice`, does the tool print `Hello, alice!` or `Hello, Alice!`? Trailing/leading whitespace in the name is also unaddressed.
- **Risk**: Implementations will disagree silently. Output format divergence is a breaking change to any downstream consumer (scripts, tests, shell pipelines) consuming the output.
- **Evidence**: SOCAS-02 MEDIUM - template syntax undefined; SOCAS-06 MEDIUM - edge cases not specified.
- **Suggested action**: Specify the output encoding, name handling (pass-through vs normalization), and provide a concrete example: `greeter --name Alice --lang en` outputs `Hello, Alice!` to stdout.

## Low Priority

### `GREETER-RV-007` "Demo CLI" Framing Leaks Into Functional Requirements — ❌ REJECTED

> Rationale: The spec is so underspecified that fixing RV-003 and RV-004 eliminates the underlying risk; debating the "demo" label adds words without improving correctness.

- **Location**: Section 1 - "Teams want a demo CLI"
- **What**: The tool is described as a "demo," which implies reduced quality expectations. However, GREETER-FR-01 and GREETER-FR-02 are written as functional requirements without any demo-scope qualifier. This creates a gap: should production-quality error handling be implemented, or demo-level? The framing is ambiguous.
- **Risk**: Implementers building the "demo" may cut corners on error handling and edge cases, then be surprised when the spec is later used as a real deliverable baseline.
- **Evidence**: SOCAS-02 LOW - "demo CLI" is undefined; its scope implications are unstated.
- **Suggested action**: Either clarify that this is a demo with reduced quality expectations (and adjust requirements accordingly), or remove the "demo" qualifier and treat it as a production spec.

## Industry Research Findings

### CLI Error Handling Standards

- **Pattern found**: POSIX convention mandates exit code 0 for success, 1 for general errors, 2 for misuse (wrong arguments). Tools like `grep`, `curl`, and `git` all follow this. Many CLI frameworks (Click, Cobra, argparse) encode these as defaults.
- **How it applies**: GREETER-FR-02 ("handles errors appropriately") is non-functional without exit code definitions. Industry baseline requires at minimum: 0 = success, non-zero = error.
- **Source**: POSIX.1-2017, exit(3); GNU Coding Standards section 4.7

### Localization Design Patterns

- **Pattern found**: Production i18n CLIs use locale codes (en, de, fr) mapped to translation files, not hardcoded greeting strings. This keeps the language count consistent with a registry, preventing the count-definition mismatch found in this spec.
- **How it applies**: Hardcoding greeting words without a defined registry makes the count easy to get wrong (as happened here: 2 vs 3). A simple language map makes the supported set self-documenting and eliminates the contradiction.
- **Source**: GNU gettext manual; i18n-rosetta.com

### German Greeting Formality

- **Pattern found**: German greetings carry a formality dimension absent in English. "Hallo" is informal; "Guten Tag" is formal. For a tool addressing users by name, the register choice affects perceived appropriateness in corporate contexts.
- **How it applies**: The spec specifies "a fixed greeting word" per language but does not specify German register. This is an unstated design decision that will be made implicitly by whoever implements it first.
- **Source**: Teknora blog on i18n for DACH products; Elon.io German grammar

### Vague Requirements as a Root Cause of Defects

- **Pattern found**: Research on requirement defects (Berry 2002, NASA/SEI studies) consistently identifies vague requirements ("appropriately," "correctly," "as needed") as the top source of implementation divergence and late-stage defects.
- **How it applies**: GREETER-FR-02 is textbook vague. Without enumerated error cases, implementations cannot be verified and tests cannot be written.
- **Source**: Berry, D. "Ambiguity in Natural Language Requirements Documents." IEEE, 2002.

### Alternatives Considered

- **Locale-file approach**: Rather than listing languages in the spec, define a locale registry (a JSON or YAML file with language code to greeting mapping). The spec then specifies the registry format, not the language list. This eliminates count-definition contradictions entirely.
- **Usage-example-first spec style**: Some CLI specs lead with `$ greeter --name Alice --lang en` examples before requirements, making the interface unambiguous before any formal requirement is stated. Would have prevented GREETER-RV-004.

## Recommendations

### Must Do

- [ ] Resolve the 2-vs-3 language count contradiction (GREETER-RV-001) - pick one count in `_SPEC_GREETER.md`
- [ ] Name and define the third language and its greeting word, or remove the "three" reference (GREETER-RV-002)
- [ ] Replace GREETER-FR-02 with enumerated error conditions, exit codes, and error message targets (GREETER-RV-003)
- [ ] Add CLI invocation syntax to the spec (GREETER-RV-004)

### Should Do

- [ ] Add measurable acceptance criteria per requirement (GREETER-RV-005)
- [ ] Specify output format edge cases: name case normalization, whitespace handling, target stream (GREETER-RV-006)

### Could Do

- [ ] Clarify or remove the "demo" qualifier to avoid scope ambiguity (GREETER-RV-007)
- [ ] Specify German greeting register (formal "Guten Tag" vs informal "Hallo")

## SOCAS Summary

SOCAS violations: 4/17 (SOCAS-01 HIGH, SOCAS-02 MEDIUM, SOCAS-06 HIGH, SOCAS-10 HIGH)
Verdict: REWORK - exceeds 3-criterion threshold

## Document History

**2026-08-30 22:21**
- Reconciliation pass: 6 findings accepted (RV-001 through RV-006), 1 rejected (RV-007)

**2026-08-30 22:19**
- Initial review created
