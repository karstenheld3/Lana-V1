# SPEC: WordCount CLI

**Doc ID**: WRDCOUNT-SP01
**Feature**: WORDCOUNT
**Goal**: Specify a CLI tool that counts words, lines, and characters in a UTF-8 text file and prints a summary line.
**Timeline**: Created 2026-08-30
**Target file(s)**:
- `wordcount` (executable entry point, language TBD at IMPL)

**Depends on:** N/A

## MUST-NOT-FORGET

- SPEC defines WHAT the tool does and WHY - no code, no function signatures, no line numbers.
- All counts must be computed from the raw UTF-8 byte stream; do not normalize line endings before counting.
- Word, line, and character definitions are fixed in WRDCOUNT-DD-01 through WRDCOUNT-DD-03 - do not redefine in IMPL.

## Table of Contents

1. [Scenario](#1-scenario)
2. [Assumptions](#2-assumptions)
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

**Problem:** Developers and operators need a fast, scriptable way to measure the size of a UTF-8 text file in three dimensions - words, lines, and characters - without launching a heavyweight editor or relying on platform-specific shell commands (`wc` is POSIX-only; PowerShell equivalents are verbose).

**Solution:**
- Accept a single file path as a positional CLI argument.
- Read the file as UTF-8 text.
- Count lines, words, and characters according to the definitions in section 6.
- Print one summary line to standard output in a fixed, machine-parseable format.
- Exit with code 0 on success, non-zero on error.

**What we don't want:**
- Interactive prompts or menus - the tool is non-interactive.
- Support for reading from standard input (stdin) in this version.
- Processing multiple files in one invocation.
- Recursive directory scanning.
- Binary file handling or encoding auto-detection - UTF-8 only.
- Colored or decorated output - plain text only for easy piping.

## 2. Assumptions

The following assumptions were made without user input. Flag any that do not match intent.

- **A-01**: The tool is a standalone command-line executable (not a library or web service).
- **A-02**: The target platform is any OS with a UTF-8 capable filesystem (Linux, macOS, Windows).
- **A-03**: "Word" means a maximal sequence of non-whitespace Unicode characters, separated by one or more whitespace characters (Unicode definition of whitespace). This matches POSIX `wc -w` semantics.
- **A-04**: "Line" means a sequence of characters terminated by a newline character (`\n`). A file with no trailing newline still counts its last non-empty sequence as a line. An empty file has 0 lines.
- **A-05**: "Character" means a Unicode code point (not a byte). A file containing the single character `é` (U+00E9, 2 UTF-8 bytes) counts as 1 character.
- **A-06**: The summary line format is: `<lines> lines  <words> words  <chars> chars  <filepath>` with two spaces between each field group.
- **A-07**: Maximum supported file size is 2 GB. Files larger than this produce an error.
- **A-08**: The tool does not follow symbolic links - it reads the file at the exact path provided.

## 3. Domain Objects

### InputFile

An **InputFile** is a UTF-8 encoded plain-text file provided by the user as the target for counting.

- Path: absolute or relative filesystem path supplied as CLI argument
- Encoding: UTF-8 (required; BOM optional and stripped before counting)
- Max size: 2 GB
- Type: regular file (directories and device files rejected)

### CountResult

A **CountResult** is the set of three integer metrics derived from one InputFile.

- Line count: non-negative integer
- Word count: non-negative integer
- Character count: non-negative integer

### SummaryLine

A **SummaryLine** is the single line of text printed to standard output after successful counting.

- Format: `<lines> lines  <words> words  <chars> chars  <filepath>`
- Fields separated by two spaces
- `<filepath>` is the path exactly as supplied by the user (no normalization)

## 4. Functional Requirements

**WRDCOUNT-FR-01: Accept File Path Argument**
- Accept exactly one positional argument: the path to the file to count.
- Reject invocations with zero arguments or more than one positional argument with a usage error message and exit code 1.

**WRDCOUNT-FR-02: Read File as UTF-8**
- Open and read the file at the provided path as UTF-8 text.
- Strip a leading UTF-8 BOM (U+FEFF) if present before counting.
- Reject files that contain invalid UTF-8 byte sequences with an error message and exit code 2.

**WRDCOUNT-FR-03: Count Lines**
- Count lines as sequences of characters terminated by `\n`.
- A non-empty file with no trailing `\n` counts its last sequence as a line.
- An empty file (zero bytes after BOM strip) produces a line count of 0.

**WRDCOUNT-FR-04: Count Words**
- Count words as maximal sequences of non-whitespace Unicode characters.
- Whitespace is any character with the Unicode property `White_Space=Yes` (includes space, tab, newline, carriage return, and other Unicode spaces).
- A file containing only whitespace produces a word count of 0.

**WRDCOUNT-FR-05: Count Characters**
- Count characters as Unicode code points (not bytes, not grapheme clusters).
- The BOM, if stripped per WRDCOUNT-FR-02, is not counted.

**WRDCOUNT-FR-06: Print Summary Line**
- On success, print exactly one line to standard output:
  `<lines> lines  <words> words  <chars> chars  <filepath>`
- Use two spaces between each field group.
- `<filepath>` is the path string exactly as the user supplied it.
- No trailing spaces; terminated by a single newline.

**WRDCOUNT-FR-07: Error Handling**
- File not found: print error message to standard error, exit code 2.
- Path is a directory or non-regular file: print error message to standard error, exit code 2.
- File exceeds 2 GB: print error message to standard error, exit code 2.
- Invalid UTF-8 content: print error message to standard error, exit code 2.
- Permission denied: print error message to standard error, exit code 2.
- Wrong argument count: print usage line to standard error, exit code 1.

**WRDCOUNT-FR-08: Help Flag**
- Respond to `--help` or `-h` by printing a brief usage description to standard output and exiting with code 0.
- Help output must include: tool name, synopsis, argument description, output format example, and exit code table.

## 5. Non-Functional Requirements

**WRDCOUNT-NFR-01: Performance - Throughput**
- Process a 100 MB UTF-8 text file in under 5 seconds on commodity hardware (single-core, 2 GHz equivalent).
- Verification: timed run against a generated 100 MB file.

**WRDCOUNT-NFR-02: Reliability - Determinism**
- Identical input always produces identical output. No randomness, no timestamps in output.

**WRDCOUNT-NFR-03: Usability - Exit Codes**
- Exit codes are stable across versions: 0 = success, 1 = usage error, 2 = runtime error.
- Downstream scripts may depend on these codes.

**WRDCOUNT-NFR-04: Localization - Encoding**
- Character counting operates on Unicode code points, not locale-dependent byte counts.
- The tool does not depend on the OS locale setting for counting.

## 6. Design Decisions

**WRDCOUNT-DD-01:** Count lines by `\n` terminator only (not `\r\n` or `\r`). Rationale: UTF-8 text files use `\n` as the canonical line terminator on all modern platforms. Supporting `\r` as a terminator would require normalization that changes the character count and complicates edge cases.

**WRDCOUNT-DD-02:** Count characters as Unicode code points, not bytes or grapheme clusters. Rationale: Code points are the most predictable unit - neither too low-level (bytes vary by encoding) nor too high-level (grapheme clusters require complex Unicode segmentation). Matches Python `len()` and Go `rune` count semantics.

**WRDCOUNT-DD-03:** Count words using Unicode `White_Space` property, not ASCII whitespace only. Rationale: Input files may contain non-ASCII whitespace (e.g., non-breaking space U+00A0, ideographic space U+3000). Treating only ASCII whitespace as a separator would produce inflated word counts for such files.

**WRDCOUNT-DD-04:** Use two-space separator between summary fields. Rationale: Single space is ambiguous when filenames contain spaces. Two spaces provide visual grouping without quoting requirements. The filepath is always the last field, so trailing spaces in the name do not create parsing ambiguity.

**WRDCOUNT-DD-05:** Reject stdin input in this version. Rationale: Stdin support requires piping infrastructure and changes the output format (no filepath to print). Scope is kept minimal; stdin support can be added in a future version.

**WRDCOUNT-DD-06:** Strip UTF-8 BOM before counting and do not include BOM in any count. Rationale: BOM is a file encoding marker, not content. Including it would cause the character count to differ by 1 between BOM and non-BOM files with identical content, confusing users.

## 7. Implementation Guarantees

**WRDCOUNT-IG-01:** The summary line format `<lines> lines  <words> words  <chars> chars  <filepath>` is stable. No version of this tool may change the field order or separator without a major version increment.

**WRDCOUNT-IG-02:** Exit codes 0, 1, 2 are stable. Scripts may rely on them.

**WRDCOUNT-IG-03:** The tool writes nothing to standard output on error. All error messages go exclusively to standard error.

**WRDCOUNT-IG-04:** The tool does not modify the input file under any circumstance.

## 8. Key Mechanisms

**UTF-8 Stream Reading:** The tool reads the file as a UTF-8 character stream. The BOM detection pass occurs before any counting. The remaining stream is iterated once, updating line, word, and character counters in a single pass to avoid loading the entire file into memory.

**Single-Pass Counting:** All three metrics (lines, words, characters) are computed in one sequential read of the file. This keeps memory usage proportional to the line buffer size, not the file size.

**Word Boundary Detection:** The word counter transitions between "in-word" and "out-of-word" states as it iterates characters. A word increment occurs on every transition from "out-of-word" to "in-word". This state machine approach handles arbitrary runs of whitespace without building a word list.

**Error Channel Discipline:** Standard output carries only the summary line (on success). Standard error carries only error and usage messages. This discipline makes the tool safe to use in shell pipelines (`wordcount file.txt | awk '{print $1}'`).

## 9. Action Flow

```
User invokes: wordcount <filepath>
├─> Parse arguments
│   ├─> Zero or multiple positional args -> print usage to stderr, exit 1
│   ├─> --help or -h -> print help to stdout, exit 0
│   └─> Exactly one positional arg -> proceed
├─> Validate file
│   ├─> File not found -> print error to stderr, exit 2
│   ├─> Path is directory or non-regular file -> print error to stderr, exit 2
│   ├─> File > 2 GB -> print error to stderr, exit 2
│   └─> Permission denied -> print error to stderr, exit 2
├─> Open file as UTF-8 stream
│   └─> Invalid UTF-8 byte encountered -> print error to stderr, exit 2
├─> Strip BOM if present (U+FEFF as first code point)
├─> Single-pass count: iterate code points
│   ├─> Increment char_count per code point
│   ├─> Increment line_count on each \n
│   └─> Update word state machine per Unicode White_Space property
│       └─> Increment word_count on out->in-word transition
└─> Print summary line to stdout, exit 0
```

## 10. Data Structures

**Summary line output (success):**
```
4 lines  12 words  67 chars  ./sample.txt
```

**Error output examples (to stderr):**
```
wordcount: error: file not found: './missing.txt'
wordcount: error: not a regular file: './somedir'
wordcount: error: file too large (max 2 GB): './huge.bin'
wordcount: error: invalid UTF-8 sequence at byte offset 1024: './bad.txt'
wordcount: error: permission denied: './locked.txt'
```

**Usage error output (to stderr):**
```
wordcount: error: expected exactly one file argument
Usage: wordcount <file>
```

**Help output (to stdout, --help or -h):**
```
wordcount - count lines, words, and characters in a UTF-8 text file

Usage:
  wordcount <file>

Arguments:
  <file>    Path to a UTF-8 encoded text file (max 2 GB)

Output:
  <lines> lines  <words> words  <chars> chars  <file>

  Example: 4 lines  12 words  67 chars  ./sample.txt

Exit codes:
  0  Success
  1  Usage error (wrong number of arguments)
  2  Runtime error (file not found, invalid UTF-8, permission denied, etc.)
```

## 11. Logging Requirements

**Applicable logging type:** User-Facing (UF) - the tool produces console output consumed by end users and scripts.

**User-Facing (UF):**
- Audience: developers and operators running the tool directly or in shell pipelines.
- Goal: know the three counts for the file on success; know the exact failure reason on error.
- Key operations: argument validation, file open, BOM detection, counting, output.

**Expected output for successful count:**
```
4 lines  12 words  67 chars  ./sample.txt
```

**Expected output for file-not-found error:**
```
wordcount: error: file not found: './missing.txt'
```
(Printed to stderr; nothing printed to stdout.)

## 12. Technical Constraints

- The tool is a single executable with no required runtime dependencies beyond the standard library of its implementation language.
- The tool must not write any temporary files to disk.
- The tool must not make network calls.
- The summary line must be terminated by a single `\n` (LF), even on Windows.
- Character counting must operate on Unicode code points, independent of OS locale settings.
- The 2 GB file size limit must be checked before reading begins (via filesystem metadata), not discovered mid-stream.
- The tool must be invocable as `wordcount <file>` from the directory containing the executable, or from any directory if the executable is on the system `PATH`.

## 13. Document History

**[2026-08-30 22:16]**
- Initial specification created
