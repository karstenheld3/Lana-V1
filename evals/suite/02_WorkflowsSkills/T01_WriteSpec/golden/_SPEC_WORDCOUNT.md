# SPEC: WordCount CLI

**Doc ID**: WRDCOUNT-SP01
**Feature**: wordcount-cli
**Goal**: Specify a CLI tool that counts words, lines, and characters in a UTF-8 text file and prints a summary line.
**Timeline**: Created 2026-08-30
**Target file(s)**:
- `wordcount.py`

## MUST-NOT-FORGET

- UTF-8 only - no encoding detection, no fallback encodings
- One summary line on stdout - no extra output on success
- Errors are self-contained messages on stderr with non-zero exit codes

## Table of Contents

1. [Scenario](#1-scenario)
2. [Assumptions](#2-assumptions)
3. [Functional Requirements](#3-functional-requirements)
4. [Design Decisions](#4-design-decisions)
5. [Technical Constraints](#5-technical-constraints)
6. [Document History](#6-document-history)

## 1. Scenario

**Problem:** Teams need a dependency-free way to measure text file size in words, lines, and characters with one predictable command.

**Solution:**
- `wordcount <file>` reads a UTF-8 text file and prints one summary line
- Deterministic counting rules (defined below) so results are comparable across runs and machines

**What we don't want:**
- Encoding detection or non-UTF-8 support
- Recursive folder processing or glob patterns
- Output formats beyond the single summary line

## 2. Assumptions

- **WRDCOUNT-AS-01**: A word is a maximal sequence of non-whitespace characters [ASSUMED]
- **WRDCOUNT-AS-02**: Lines are separated by `\n`; a trailing newline does not create an extra line [ASSUMED]
- **WRDCOUNT-AS-03**: Characters are Unicode code points after decoding, including whitespace [ASSUMED]

## 3. Functional Requirements

**WRDCOUNT-FR-01: Counting**
- Count words (per WRDCOUNT-AS-01), lines (per WRDCOUNT-AS-02), and characters (per WRDCOUNT-AS-03) of the input file
- An empty file counts as 0 words, 0 lines, 0 characters

**WRDCOUNT-FR-02: Summary Output**
- Print exactly one line to stdout: `words: <n> | lines: <n> | characters: <n>`
- Exit code 0 on success

**WRDCOUNT-FR-03: Error Handling**
- Missing file argument: usage line on stderr, exit code 2
- File not found: message naming the path on stderr, exit code 2
- Invalid UTF-8: message naming the path and the byte offset on stderr, exit code 3

## 4. Design Decisions

**WRDCOUNT-DD-01:** Whitespace-split word definition instead of locale-aware tokenization. Rationale: deterministic, dependency-free, matches common `wc -w` expectations.

**WRDCOUNT-DD-02:** Single-file input only. Rationale: composability - shells already provide iteration and globbing.

## 5. Technical Constraints

- Standard library only - no external dependencies
- Reads the file fully into memory (files are expected small; streaming is out of scope)

## 6. Document History

**[2026-08-30 20:00]**
- Initial specification created (golden reference, produced by Cascade + IPPS)
