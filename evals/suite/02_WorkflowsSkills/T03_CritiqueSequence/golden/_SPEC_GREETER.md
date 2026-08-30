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
- Prints `<greeting>, <name>!` for the selected language
- Both supported languages (English, German) have a fixed greeting word

**GREETER-FR-02: Error Handling**
- Unknown language code: exit code 2 with a message naming the code and the supported languages
- Missing name argument: exit code 2 with a usage line
