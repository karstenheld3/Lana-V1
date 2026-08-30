# SPEC: Greeter CLI

**Doc ID**: GREETER-SP01
**Goal**: Specify a CLI tool that prints localized greetings.
**Depends on**: none

## 1. Scenario

**Problem:** Teams want a demo CLI that greets users in their language.

**Solution:**
- A `greeter` command that prints a greeting for a given name and language
- Supports exactly two languages: English and German

## 2. CLI Interface

Invocation: `greeter <name> <lang>`

- `<name>` — the person to greet; required; any non-empty string
- `<lang>` — language code; required; one of: `en`, `de`

Example: `greeter Alice en` prints `Hello, Alice!` to stdout.

## 3. Functional Requirements

**GREETER-FR-01: Greeting Output**
- Prints `<greeting>, <name>!` to stdout (UTF-8) for the selected language
- The two supported languages each have a fixed greeting word: `en` prints `Hello`, `de` prints `Hallo`
- `<name>` is printed as provided (no case normalization, no whitespace trimming)
- Exit code: 0

**GREETER-FR-02: Error Handling**

All errors write a descriptive message to stderr and exit with a non-zero code.

- Missing argument(s) — print usage line to stderr; exit code 1
- Unsupported language code — print `Unsupported language: <lang>. Supported: en, de` to stderr; exit code 1
- Empty name (empty string or whitespace only) — print `Name must not be empty` to stderr; exit code 1
