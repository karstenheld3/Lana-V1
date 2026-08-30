# Apply Patch Tool

**Doc ID**: OAIAPI-IN89
**Goal**: Document apply patch tool for code editing workflows
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Apply Patch is a built-in tool for GPT-5.5 and GPT-5.4 that generates and applies code patches. Used for code editing workflows where the model produces unified diff patches that are applied to source files. Supported in Responses API and Agents SDK. Key tool for agentic coding workflows alongside hosted shell. [VERIFIED] (OAIAPI-SC-OAI-GAPTCH (https://developers.openai.com/api/docs/guides/tools-apply-patch))

## Key Facts

- **Models**: GPT-5.5, GPT-5.4 (trained for patch generation) [VERIFIED]
- **Format**: Unified diff format [VERIFIED]
- **APIs**: Responses API and Agents SDK [VERIFIED]
- **Use case**: Agentic code editing without full file rewrite

## How It Works

1. Model receives file content or context about a codebase
2. Model generates a unified diff patch targeting specific files
3. Patch is applied to the file system (local or hosted)
4. Results returned to model for verification

## Patch Format

```diff
--- a/src/main.py
+++ b/src/main.py
@@ -10,3 +10,5 @@
 def hello():
-    print("Hello")
+    print("Hello, World!")
+    return True
```

## SDK Examples (Python)

### Responses API with Apply Patch

```python
from openai import OpenAI

client = OpenAI()

file_content = '''def calculate(x, y):
    return x + y
'''

response = client.responses.create(
    model="gpt-5.6-sol",
    input=f"Add input validation to this function:\n\n```python\n{file_content}```",
    tools=[{"type": "apply_patch"}],
)

# Model generates patch in response
for item in response.output:
    if item.type == "tool_use" and item.name == "apply_patch":
        print(f"Patch:\n{item.input['patch']}")
```

### Agents SDK with Apply Patch

```python
from openai.agents import Agent, ApplyPatchTool

patch_tool = ApplyPatchTool(
    working_directory="/home/user/project",
    allowed_paths=["src/", "tests/"],
)

agent = Agent(
    model="gpt-5.6-sol",
    instructions="You are a code editor. Make changes using apply_patch.",
    tools=[patch_tool],
)
```

## Comparison with Other Approaches

- **Apply Patch**: Minimal diffs, precise edits, low token cost
- **Full file rewrite**: Complete file in response, high token cost, risk of data loss
- **Hosted shell + sed/awk**: Fragile, depends on exact formatting
- **Codex CLI pattern**: Uses apply_patch internally

## Gotchas and Quirks

- **Model training**: GPT-5.5/5.4 specifically trained for patch generation [VERIFIED]
- **Older models**: GPT-4o and earlier may produce invalid patches [VERIFIED]
- **Context required**: Model needs sufficient file context to generate correct patches [VERIFIED]
- **Conflict handling**: Patches may fail if file was modified since context was provided [VERIFIED]
- **Line endings**: Patches are sensitive to line ending differences (LF vs CRLF) [COMMUNITY]

## TypeScript Examples

### Basic Response

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Explain this concept briefly.",
});

console.log(response.output_text);
```

### With Instructions

```typescript
const response = await client.responses.create({
  model: "gpt-4o-mini",
  instructions: "You are a helpful assistant.",
  input: "What is 2+2?",
});

console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GAPTCH - Apply patch tool guide (https://developers.openai.com/api/docs/guides/tools-apply-patch)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Patch format, SDK examples, comparison with alternatives, gotchas

**[2026-05-22 13:05]**
- Initial documentation (gap found during /improve review)
