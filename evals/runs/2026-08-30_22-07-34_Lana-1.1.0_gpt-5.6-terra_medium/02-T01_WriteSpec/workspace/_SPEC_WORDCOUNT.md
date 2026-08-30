# SPEC: WordCount CLI

**Doc ID**: WRDCOUNT-SP01
**Feature**: wordcount
**Goal**: Specify a command-line tool that reports line, word, and character counts for one UTF-8 text file.
**Timeline**: Created 2026-08-30, Updated 0 times (2026-08-30 - 2026-08-30)
**Target file**: `wordcount` command-line application

## MUST-NOT-FORGET

- Count decoded Unicode code points, not UTF-8 bytes.
- Print exactly one success summary line to standard output.
- Reject unreadable or malformed UTF-8 input without printing a success summary.

## Assumptions

- The command accepts exactly one positional file path and no options.
- A word is a non-empty sequence of characters separated by Unicode whitespace.
- A line is a logical line in counted text, after excluding an initial byte order mark. Its count is one plus the number of line terminators when counted text is non-empty; empty counted text has zero lines. `CRLF` is one terminator, while `CR` and `LF` are each one terminator.
- Characters include all decoded Unicode code points, including whitespace and line terminators. An initial UTF-8 byte order mark is not text and is excluded.
- The summary format is `lines=<N> words=<N> characters=<N> file=<path>`.

## Table of Contents

0. [Assumptions](#assumptions)
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

**Problem:** You need a consistent command-line summary of the textual size of a UTF-8 file.

**Solution:**
- Accept one file path and analyze its decoded text.
- Report lines, words, and characters in one stable summary line.

**What we don't want:**
- Byte counts presented as character counts.
- Locale-dependent or platform-dependent count semantics.
- Partial success output after an input or decoding error.
- Extra progress, diagnostic, or banner text on successful execution.

## 2. Context

WordCount CLI is a standalone command-line utility. It has no configuration, network interaction, persistent state, or interactive mode.

## 3. Domain Objects

### Input File

An **Input File** is the single filesystem file selected by the user.

- `path`: user-supplied positional path
- `content`: complete file content decoded as UTF-8 text
- `byte order mark`: optional initial UTF-8 marker excluded from text counts

### Count Summary

A **Count Summary** is the result for one successfully decoded Input File.

- `lines`: logical line count
- `words`: Unicode-whitespace-delimited word count
- `characters`: decoded Unicode code point count
- `file`: Input File path as supplied by the user

### Command Result

A **Command Result** is the observable outcome of one invocation.

- `status`: success or failure
- `standard output`: one Count Summary line on success
- `standard error`: one actionable error message on failure

## 4. Functional Requirements

**WRDCOUNT-FR-01: Accept one input path**
- The command must accept exactly one positional path to an Input File.
- The command must reject invocations with zero paths or more than one path.

**WRDCOUNT-FR-02: Read UTF-8 text**
- The command must read the selected Input File as UTF-8 text.
- The command must reject a path that does not identify a readable regular file.
- The command must reject content that is not valid UTF-8.

**WRDCOUNT-FR-03: Count lines**
- The command must count logical lines using the definition in Assumptions.
- A trailing line terminator must not create an additional empty logical line.

**WRDCOUNT-FR-04: Count words**
- The command must count each maximal non-empty sequence of non-whitespace Unicode characters as one word.
- Consecutive whitespace must not create empty words.

**WRDCOUNT-FR-05: Count characters**
- The command must count decoded Unicode code points, not source bytes.
- The command must include whitespace and line terminators in the character count.
- The command must exclude one initial UTF-8 byte order mark when present.

**WRDCOUNT-FR-06: Print the success summary**
- The command must print exactly one line to standard output after successful counting.
- The line must use `lines=<N> words=<N> characters=<N> file=<path>` field order.
- The command must use non-negative decimal integers for each count.

**WRDCOUNT-FR-07: Report failures**
- The command must print an actionable error message to standard error for invalid invocation, inaccessible input, non-regular input, or malformed UTF-8.
- The command must return a non-zero exit status on failure.
- The command must not print a Count Summary on failure.

## 5. Non-Functional Requirements

**WRDCOUNT-NFR-01: Deterministic results**
- Given identical decoded text, the command must return identical counts on all supported platforms.
- Platform-native line endings must follow the line definition in Assumptions.

**WRDCOUNT-NFR-02: Usable command output**
- A successful invocation must write only the required summary line to standard output.
- A failed invocation must identify the cause and, when applicable, the supplied path.

**WRDCOUNT-NFR-03: Input preservation**
- The command must not modify the Input File.

## 6. Design Decisions

**WRDCOUNT-DD-01:** UTF-8 is the only accepted encoding. Rationale: the requested scope identifies UTF-8 and one encoding removes detection ambiguity.

**WRDCOUNT-DD-02:** Character count means decoded Unicode code points. Rationale: users receive text-character counts instead of encoding-dependent byte counts.

**WRDCOUNT-DD-03:** The success line uses named fields in a fixed order. Rationale: humans can read it and automation can parse it without positional ambiguity.

**WRDCOUNT-DD-04:** The command analyzes one file per invocation. Rationale: this matches the requested scope and keeps failures attributable to one path.

## 7. Implementation Guarantees

**WRDCOUNT-IG-01:** The command never reports a successful count before it has validated the complete input as UTF-8.

**WRDCOUNT-IG-02:** The command returns exactly one count for each required measure on successful execution.

**WRDCOUNT-IG-03:** The command keeps standard output free of non-summary text on successful execution.

## 8. Key Mechanisms

- Decode the Input File as UTF-8 before deriving the Count Summary.
- Apply the shared whitespace definition to word boundaries.
- Normalize only line-terminator recognition for line counting; preserve all decoded code points for character counting.
- Keep successful output and failed output on separate standard streams.

## 9. Action Flow

```text
You run `wordcount <file>`
├── The command validates that one path was supplied
├── The command reads and validates the Input File as UTF-8
│   ├── On validation failure: write an error to standard error and return failure
│   └── On success: derive the Count Summary
└── The command writes one summary line to standard output and returns success
```

## 10. Data Structures

**Count Summary format:**

```text
lines=2 words=3 characters=14 file=sample.txt
```

This example illustrates field order only. Counts depend on the actual decoded text.

**Counting examples:**
- Empty counted text: `lines=0 words=0 characters=0`.
- Counted text `one`: `lines=1 words=1 characters=3`.
- Counted text `one\n`: `lines=1 words=1 characters=4`.
- Counted text `one\r\ntwo`: `lines=2 words=2 characters=8`.

## 11. Logging Requirements

**Applicable logging types:**
- [x] User-Facing (UF) - command output
- [ ] App-Level (AP) - no server or background application exists
- [ ] Script-Level (SC) - no verification script is in scope

**User-Facing logging:**
- **Audience**: people and automation invoking the command
- **Goal**: receive the requested counts on success or a clear cause on failure
- **Key operations**: successful count reporting, argument validation, file access, UTF-8 validation

**Expected output for a successful count:**

```text
lines=2 words=3 characters=14 file=sample.txt
```

**Expected error form:**

```text
ERROR: Cannot decode file 'sample.txt' as UTF-8.
```

## 12. Technical Constraints

- The input encoding must be UTF-8.
- The interface is a command-line invocation with one positional file path.
- The command must use standard output for a successful Count Summary and standard error for errors.
- The scope excludes directories, multiple-file aggregation, glob expansion, encoding detection, configuration files, and persistent storage.

## 13. Document History

**[2026-08-30 22:08]**
- Initial specification created.
