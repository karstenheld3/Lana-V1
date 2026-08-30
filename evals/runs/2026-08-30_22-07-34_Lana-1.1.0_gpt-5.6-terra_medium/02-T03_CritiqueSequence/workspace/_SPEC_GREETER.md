# SPEC: Greeter CLI

**Doc ID**: GREETER-SP01
**Goal**: Specify a CLI tool that prints localized greetings.

## 1. Scenario

**Problem:** Teams want a demo CLI that greets users in their language.

**Solution:**
- A `greeter` command that prints a greeting for a given name and language
- Supports exactly two languages: English and German

## 2. Functional Requirements

**GREETER-FR-01: Greeting Output**
- Invocation: `greeter --lang <en|de> <name>`
- `--lang` is required. The command accepts only lowercase `en` and `de`; it accepts no aliases or region variants and ignores locale environment variables.
- `en` prints `Hello`; `de` prints `Hallo`.
- `<name>` must be nonempty and contain no Unicode control characters.
- On success, write exactly `<greeting>, <name>!` followed by one line feed to standard output and exit with status `0`.

**GREETER-FR-02: Invalid Invocation Handling**
- An invocation is invalid when it omits `--lang`, supplies a language other than `en` or `de`, omits `<name>`, supplies an empty `<name>`, supplies a `<name>` containing a Unicode control character, or supplies extra arguments.
- For an invalid invocation, write `Usage: greeter --lang <en|de> <name>` followed by one line feed to standard error, write nothing to standard output, and exit with status `2`.
