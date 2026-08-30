# Lana Prompt Queue File Format (PROMPTS*.md)

**Doc ID**: LANAACPB-DOC01
**Goal**: Document the file format Lana accepts via `lana --prompt-file <path>` for headless multi-prompt execution
**Normative source**: `specs/_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` FR-12 (this document explains; the SPEC decides)

## Table of Contents

1. [What a Prompt Queue File Is](#1-what-a-prompt-queue-file-is)
2. [Format Rules](#2-format-rules)
3. [Choosing the Fence Length](#3-choosing-the-fence-length)
4. [Examples](#4-examples)
5. [Execution Behavior](#5-execution-behavior)
6. [Error Cases](#6-error-cases)
7. [Document History](#7-document-history)

## 1. What a Prompt Queue File Is

A prompt queue file (recommended name pattern `PROMPTS*.md`, e.g. `PROMPTS.md`, `PROMPTS_setup.md`) carries an ordered list of prompts. Lana executes them sequentially as turns of ONE session:

```
lana --prompt-file PROMPTS.md --output-format jsonl
```

Each prompt is a fenced code block. Prompts are separated by `---` lines. Text between the separator and the next fence is commentary for human readers - Lana never sends it to the model.

## 2. Format Rules

- **Leading fence**: the first non-empty line of the file MUST be an opening fence
- **Prompt block**: opening fence of N backticks, prompt text, closing fence of >= N backticks
- **Fence length**: 3 <= N <= 9, chosen independently per prompt
- **Info string**: the opening fence may carry an info string (e.g. ```` ```text ````); Lana ignores it
- **Separator**: consecutive prompts are separated by one `---` line (after the closing fence, before the next opening fence)
- **Commentary**: allowed only between the `---` and the next opening fence (headings, notes); never sent to the model
- **Order**: prompts run in file order

## 3. Choosing the Fence Length

A fence closes at the first line with at least as many backticks. If your prompt CONTAINS fenced code blocks, your outer fence must be LONGER than the deepest inner fence:

- Prompt without code blocks → 3 backticks suffice
- Prompt containing ```` ``` ```` code → use 4+ backticks
- Prompt containing ```` ```` ```` markdown examples (which contain ```` ``` ```` code) → use 5+ backticks
- Maximum: 9 backticks

**BAD** (inner fence terminates the prompt early - the parser reports an unclosed structure or splits the prompt):

``````text
```
Write a README containing:
```bash
npm install
```
```
``````

**GOOD** (outer fence longer than inner fences):

``````text
````
Write a README containing:
```bash
npm install
```
````
``````

## 4. Examples

**Single prompt** (simplest valid file):

``````text
```
List all Python files in the project and count their lines.
```
``````

**Multi-prompt with mixed fence lengths and commentary:**

```````text
```
Create `calc.py` with an `add(a, b)` function.
```

---

## Step 2 - extends step 1's file; uses a 5-backtick fence because the prompt contains 4-backtick material

`````
Add a `multiply(a, b)` function to `calc.py`. Use this docstring format:

````markdown
Example:
```python
multiply(2, 3)  # 6
```
````
`````

---

```text
Run the tests and report the results.
```
```````

## 5. Execution Behavior

- All prompts run in ONE session (later prompts see earlier results)
- Before each turn, Lana emits a `prompt_step` event (1-based index, total, prompt digest) - visible in `--output-format jsonl` and persisted in the session file
- A failed turn (provider error, cancellation) abandons the remaining prompts; the exit code is non-zero; completed turns stay persisted and the session is resumable via `--resume`
- `--prompt-file` cannot be combined with `-p`, `--acp`, or `--resume`

## 6. Error Cases

Lana rejects the file with an error on stderr and exit code 2 when:

- The first non-empty line is not an opening fence
- A fence is never closed
- The `---` separator between two prompts is missing
- An opening fence has more than 9 backticks
- The file contains zero prompts

The error message names the violated rule.

## 7. Document History

**[2026-08-30 19:45]**
- Initial format documentation created (format per LANAACPB-SP01 FR-12, user decision 2026-08-30: per-prompt fence 3..9, leading fence, `---` separators)
