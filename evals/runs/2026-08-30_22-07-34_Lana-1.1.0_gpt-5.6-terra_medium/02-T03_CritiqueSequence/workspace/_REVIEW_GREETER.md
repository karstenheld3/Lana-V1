# Greeter CLI Specification Review

**Doc ID**: GREETER-SP01-RV01
**Goal**: Identify logic, design, and requirement risks in `_SPEC_GREETER.md [GREETER-SP01]`
**Timeline**: Created 2026-08-30, Updated 0 times (2026-08-30 - 2026-08-30)
**Reviewed**: 2026-08-30 22:10
**Context**: Devil's Advocate review of the Greeter CLI specification

## Table of Contents

1. [Critical Issues](#critical-issues)
2. [High Priority](#high-priority)
3. [Medium Priority](#medium-priority)
4. [Low Priority](#low-priority)
5. [Questions That Need Answers](#questions-that-need-answers)
6. [Industry Research Findings](#industry-research-findings)
7. [Recommendations](#recommendations)
8. [Devil's Advocate Summary](#devils-advocate-summary)
9. [Document History](#document-history)

## Critical Issues

### GREETER-RV-001 Contradictory supported-language count

- **Reconciliation**: ACCEPTED - The mutually exclusive language counts make compliance impossible until one authoritative set is chosen.
- **Location**: `_SPEC_GREETER.md [GREETER-SP01]`, lines 12 and 18
- **What**: The scenario says the command supports "exactly two languages: English and German." GREETER-FR-01 requires fixed greeting words for "the three supported languages."
- **Why it went wrong**: The two statements establish incompatible product boundaries. An implementation cannot determine whether to accept two or three language choices.
- **Risk**: Teams can implement and test different interfaces while each claims compliance. A third language may ship unintentionally or valid output may be rejected.
- **Evidence**: SOCAS-01 HIGH. The quoted cardinalities, "exactly two" and "three," contradict each other.
- **Suggested action**: Choose the authoritative supported-language set. List each accepted language identifier and its exact greeting literal in GREETER-FR-01.

## High Priority

### GREETER-RV-002 Language-selection contract is absent

- **Reconciliation**: ACCEPTED - A CLI needs a minimal, deterministic selector syntax and missing-selector behavior for callers and tests to agree.
- **Location**: `_SPEC_GREETER.md [GREETER-SP01]`, lines 11-12 and 16-18
- **What**: The specification does not define how callers supply the language, its accepted identifiers, whether case or region variants are valid, or whether a missing language defaults or fails.
- **Why it went wrong**: "Given name and language" establishes inputs but not their syntax or resolution rules. English and German can be represented by names, ISO 639 codes, or BCP 47 tags, which are distinct contracts.
- **Risk**: `en`, `EN`, `en-US`, `English`, and no argument can produce inconsistent behavior across implementations. Locale-environment fallback can also make output machine-dependent and non-repeatable.
- **Evidence**: SOCAS-06 HIGH: an externally supplied input and its edge cases are unspecified. BCP 47 defines the structure and semantics of language tags, so accepting tags without a stated normalization or matching policy is not self-defining.
- **Suggested action**: Define the command grammar, canonical language identifiers, accepted aliases and case behavior, missing-language behavior, and whether environment locale settings are ignored or used.

### GREETER-RV-003 Name input can corrupt the one-line output contract

- **Reconciliation**: ACCEPTED - At minimum, rejecting empty names and line/control characters is proportionate for a line-oriented demo CLI; length and bidi policies are optional.
- **Location**: `_SPEC_GREETER.md [GREETER-SP01]`, line 17
- **What**: `<name>` is interpolated directly into output without a permitted character set, length limit, or treatment for empty, whitespace-only, newline, escape, and bidirectional-control characters.
- **Why it went wrong**: The requirement assumes a name is a short, printable, single-line string. Command-line arguments can contain arbitrary Unicode and control characters.
- **Risk**: A newline makes one invocation produce multiple terminal or log lines. Terminal escape sequences can alter displayed output. Bidirectional controls can cause displayed text to differ from stored text. Empty input produces a malformed greeting.
- **Evidence**: SOCAS-06 HIGH: input-boundary behavior is not specified. Unicode Technical Standard #39 documents security considerations for confusing Unicode text, and OWASP identifies unneutralized line breaks in logged user input as log injection.
- **Suggested action**: Specify whether names are rejected or escaped when they contain control characters, define empty and whitespace-only behavior, set a maximum length, preserve valid Unicode names, and state the exact newline policy for successful output.

### GREETER-RV-004 Error behavior has no observable contract

- **Reconciliation**: ACCEPTED - Defining invalid-input failure status and error stream is a small requirement that prevents incompatible CLI behavior.
- **Location**: `_SPEC_GREETER.md [GREETER-SP01]`, lines 20-21
- **What**: GREETER-FR-02 only says the tool "handles errors appropriately." It defines neither error classes nor stdout, stderr, exit-code, and usage behavior.
- **Why it went wrong**: The requirement substitutes a quality judgment for observable behavior, so there is no implementable definition of failure.
- **Risk**: Invalid language, absent name, surplus arguments, invalid encoding, and an unavailable output stream can silently succeed, print an error as a greeting, or break shell pipelines that rely on exit status and stderr separation.
- **Evidence**: SOCAS-06 HIGH and SOCAS-10 MEDIUM. The statement provides no reasoning or criteria by which "appropriately" can be tested. POSIX utility documentation distinguishes exit status from standard-error diagnostics.
- **Suggested action**: Enumerate invalid invocations and output failures. For each, define the exit status, whether the diagnostic goes to stderr, whether stdout must remain empty, and the stable diagnostic or usage format.

## Medium Priority

No medium-priority findings.

## Low Priority

No low-priority findings.

## Questions That Need Answers

1. Which exact languages and canonical selectors must the command support?
2. Must a language selector be provided, or is there a deterministic default?
3. What exact greeting literal must each language produce?
4. Does the command accept arbitrary Unicode names, and which non-printing characters must it reject or escape?
5. What exit status and output streams apply to each invalid invocation?

## Industry Research Findings

### 1. Command-line failure signaling

- **Pattern found**: POSIX utilities expose failures through exit status and diagnostics through standard error.
- **How it applies**: GREETER-FR-02 must distinguish successful greeting output from invocation errors so it composes safely in shell pipelines.
- **Source**: [POSIX `exit` utility](https://pubs.opengroup.org/onlinepubs/009695399/utilities/exit.html)

### 2. Language identifiers

- **Pattern found**: BCP 47 standardizes language-tag structure and semantics; language names are not a universal command-line interchange format.
- **How it applies**: The spec must explicitly select and constrain accepted selectors rather than assuming that "English" and "German" are unambiguous inputs.
- **Source**: [RFC 5646: Tags for Identifying Languages](https://www.rfc-editor.org/info/rfc5646/)

### 3. Locale fallback

- **Pattern found**: GNU gettext resolves language preferences using locale-related environment variables, including `LANGUAGE`.
- **How it applies**: If the CLI uses the host locale when the language argument is absent, output differs by environment. The spec must either define that resolution order or prohibit it.
- **Source**: [GNU gettext locale environment variables](https://www.gnu.org/software/gettext/manual/html_node/Locale-Environment-Variables)

### 4. Unicode display safety

- **Pattern found**: Unicode Technical Standard #39 covers security mechanisms for text that can be visually confusing.
- **How it applies**: Name input can contain directional controls and confusables. The CLI needs a policy for controls in terminal output while continuing to support ordinary international names.
- **Source**: [Unicode Technical Standard #39](https://www.unicode.org/reports/tr39/tr39-24.html)

### 5. Log and line-break injection

- **Pattern found**: OWASP identifies user-controlled carriage returns and line feeds as a log-injection vector when output is recorded or parsed as lines.
- **How it applies**: The greeting includes untrusted name text. Allowing line terminators defeats the apparent one-line output format and can contaminate downstream logs.
- **Source**: [OWASP Log Injection](https://owasp.org/www-community/attacks/Log_Injection)

### Alternatives Considered

- **Explicit required selector**: Require `--lang en|de`; deterministic and simple, but less convenient than a default.
- **Environment-derived selector with explicit override**: Use an explicit selector first and a defined locale fallback second; convenient, but adds host-dependent cases that need testing.
- **Name acceptance policy**: Accept Unicode printable text while rejecting control characters; preserves international names and protects line-oriented consumers.

## Recommendations

### Must Do

- [ ] Reconcile lines 12 and 18 of `_SPEC_GREETER.md [GREETER-SP01]` into one authoritative language set.
- [ ] Replace GREETER-FR-02 with a testable error matrix covering invalid inputs, stdout, stderr, and exit statuses.
- [ ] Define the CLI argument grammar, exact greeting literals, and name-input boundaries.

### Should Do

- [ ] State whether locale environment variables influence language selection.
- [ ] Add acceptance criteria for valid, empty, malformed, and control-character-containing names.

### Could Do

- [ ] Add examples for each valid language invocation and each invalid invocation.

## Devil's Advocate Summary

**Reviewed**: `_SPEC_GREETER.md [GREETER-SP01]`
**Time spent**: Approximately 15 minutes

**Research Topics Investigated**:
1. Command-line failure signaling - exit status and standard error are part of a CLI's observable contract.
2. Language identifiers - BCP 47 defines language-tag structure and semantics.
3. Locale fallback - locale environment variables can make output host-dependent.
4. Unicode display safety - visually confusing controls need an explicit policy.
5. Log and line-break injection - untrusted line breaks can alter downstream logs and parsers.

**Findings**:

- CRITICAL: 1
- HIGH: 3
- MEDIUM: 0
- LOW: 0

**Top 3 Risks**:

1. The conflicting two-language and three-language requirements prevent a single compliant implementation.
2. Undefined language selection makes behavior differ by caller and host environment.
3. Unbounded name interpolation permits multiline or display-altering output.

**Industry Alternatives Identified**:

- Use a required, explicit `en` or `de` selector and a Unicode-printable-name policy that rejects control characters.

**SOCAS**: 3/17 violated (SOCAS-01 HIGH, SOCAS-06 HIGH, SOCAS-10 MEDIUM)

**Verdict**: REWORK - exceeds the three-criterion threshold.

**Files Created/Updated**:

- `FAILS.md` - 0 entries; no observed implementation failure
- `_REVIEW_GREETER.md [GREETER-SP01-RV01]` - detailed findings and industry research

**Recommendation**: STOP AND FIX

## Document History

**[2026-08-30 22:10]**

- Initial review created.
