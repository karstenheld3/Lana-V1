<!-- PROMPTS TEMPLATE
Filename: _PROMPTS_[Topic].md
Location: session folder (default), workspace root, or user-specified path
Topic: CamelCase description (e.g., SetupProject, MigrateAuth, AnalyzePerformance)

Read PROMPTS_GUIDES.md BEFORE writing. Verify against all PRMT-* rules in PROMPTS_RULES.md.
Remove ALL XML comments after creating the document. First non-empty line must be frontmatter (optional), Commentary, or opening fence.
Heading recommendation (PRMT-FT-07): use `## Prompt N - [title]` before each prompt for readability.
If headings are used, ALL prompts MUST have headings (consistency enforced).

Execution model (PRMT-EX-01/02): Each prompt is a separate turn for an execution engine. NEVER self-execute prompt files by running all prompts in one response. The writing agent creates the file; the execution engine runs it. -->

<!-- Optional Execution Frontmatter (PRMT-FT-08): YAML block at file start.
Provides execution hints to the execution engine. The engine MAY honor or override.
Omit entirely if no execution hints needed. Remove this block if not used.
Supported keys: intended_model, context_window_size, reasoning_settings, prompt_system -->
---
intended_model: [model identifier, e.g., claude-sonnet-4-5]
context_window_size: [e.g., 200k, 128k, 1M]
reasoning_settings: [medium | high | extra-high]
prompt_system: [e.g., IPPS]
---

<!-- Simple prompt: 3-backtick fence when no inner code blocks.
Heading before the fence is optional but recommended (PRMT-FT-07). -->
## Prompt 1 - [short title]

```
[Objective: what the finished state looks like (1-3 sentences)]

Constraints:
- [What NOT to do]
- [Boundaries to respect]

Verify: [Machine-checkable done criteria]
```

---

<!-- Commentary: purpose of next prompt and expected state from previous step.
For human readers only - never sent to model. Wrap in HTML comments per PRMT-FT-04.
Remove if no commentary needed. -->

<!-- Prompt with inner code blocks: 4-backtick fence. Outer must exceed deepest inner fence. -->
## Prompt 2 - [short title]

<!-- [Expected state from previous step and purpose of this prompt. Max 1 sentence in final files.] -->

````
[Objective referencing output from previous prompt explicitly]

Example output format:
```[language]
[Representative example showing expected structure]
```

Constraints:
- [What NOT to do]

Verify: [Observable success criteria]
````

<!-- EXAMPLE: Reference only. Do not copy into new documents. Shows a completed 2-prompt file with optional frontmatter and headings (PRMT-FT-07/08). -->

## Full Example

`````markdown
---
intended_model: claude-sonnet-4-5
context_window_size: 200k
reasoning_settings: high
prompt_system: IPPS
---

## Prompt 1 - Security analysis

```
Analyze the authentication module in src/auth/ for security vulnerabilities.
Focus on: token validation, session management, and password hashing.

Constraints:
- Do not modify any code in this step
- Limit analysis to src/auth/ directory only

Verify: Output a numbered list of findings with severity (HIGH/MEDIUM/LOW) and file location.
```

---

## Step 2 - Fix highest-severity finding

<!-- Previous step produced a numbered findings list. Fix the highest-severity item. -->

````
Using the analysis from the previous step, fix the highest-severity vulnerability identified.

Example fix pattern:
```typescript
try {
  const token = jwt.verify(input, secret, { algorithms: ['HS256'] })
} catch (err) {
  return res.status(401).json({ error: 'Invalid token' })
}
```

Constraints:
- Fix only the single highest-severity issue
- Do not change the public API of any exported function
- Do not add new dependencies

Verify: Run `pnpm test:auth`. All tests pass. The specific vulnerability from step 1 is no longer present.
````
`````
