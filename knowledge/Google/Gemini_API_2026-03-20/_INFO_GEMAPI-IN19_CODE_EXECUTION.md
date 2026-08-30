# INFO: Gemini API Code Execution

**Doc ID**: GEMAPI-IN19
**Goal**: Document server-side Python code execution, sandbox capabilities, and output handling
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini API Code Execution is a built-in tool that runs Python code in a sandboxed server-side environment. When enabled via `{"codeExecution": {}}` in the tools array, the model can write and execute Python code to solve computational problems, generate data, create visualizations, and process information. The execution happens within Google's infrastructure in a secure sandbox with access to common Python libraries (NumPy, Pandas, Matplotlib, etc.) but no network access or file system persistence. The model autonomously decides when code execution would help answer the prompt. Code and results appear in the response as `executableCode` and `codeExecutionResult` part types. This is conceptually similar to OpenAI's Code Interpreter but operates within a single API call rather than the Assistants API.

## Key Facts

- [VERIFIED] Activation: `{"codeExecution": {}}` in tools array (GEMAPI-SC-GOOG-CODEXE)
- [VERIFIED] Server-side Python sandbox execution (GEMAPI-SC-GOOG-CODEXE)
- [VERIFIED] Common libraries available: NumPy, Pandas, Matplotlib, etc. (GEMAPI-SC-GOOG-CODEXE)
- [VERIFIED] No network access in sandbox (GEMAPI-SC-GOOG-CODEXE)
- [VERIFIED] Response includes executableCode and codeExecutionResult parts (GEMAPI-SC-GOOG-CODEXE)
- [VERIFIED] Combinable with other tools in Gemini 3 (GEMAPI-SC-GOOG-TOOLCM)

## Quick Reference

**Tool config**: `{"tools": [{"codeExecution": {}}]}`
**Response parts**: `executableCode` (code), `codeExecutionResult` (output)

## REST API

### Request

```json
{
  "contents": [{"parts": [{"text": "Calculate the standard deviation of [23, 45, 12, 67, 34, 89, 56]"}]}],
  "tools": [{"codeExecution": {}}]
}
```

### Response with Code Execution

```json
{
  "candidates": [{
    "content": {
      "parts": [
        {"text": "I'll calculate the standard deviation using Python."},
        {"executableCode": {"language": "PYTHON", "code": "import numpy as np\ndata = [23, 45, 12, 67, 34, 89, 56]\nstd = np.std(data)\nprint(f'Standard deviation: {std:.2f}')"}},
        {"codeExecutionResult": {"outcome": "OUTCOME_OK", "output": "Standard deviation: 24.77\n"}},
        {"text": "The standard deviation of the dataset is approximately 24.77."}
      ],
      "role": "model"
    }
  }]
}
```

**Part Types:**
- **executableCode**: `{language: "PYTHON", code: "..."}`
- **codeExecutionResult**: `{outcome: "OUTCOME_OK"|"OUTCOME_FAILED"|"OUTCOME_DEADLINE_EXCEEDED", output: "..."}`

## Python Examples

### Example 1: Basic Code Execution

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Generate a bar chart comparing the populations of the 5 most populous countries.",
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())]
    )
)

# Iterate through parts to find code and results
for part in response.candidates[0].content.parts:
    if part.text:
        print(f"Text: {part.text}")
    elif part.executable_code:
        print(f"\nCode:\n{part.executable_code.code}")
    elif part.code_execution_result:
        print(f"\nOutput: {part.code_execution_result.output}")
        print(f"Status: {part.code_execution_result.outcome}")
```

### Example 2: Data Analysis

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

data_prompt = """Analyze this sales data:
Q1: $45,000
Q2: $52,000
Q3: $48,500
Q4: $61,000

Calculate: total revenue, average quarterly revenue, growth rate Q1 to Q4,
and identify the quarter with highest growth."""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=data_prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())]
    )
)
print(response.text)
```

## Comparison with Other APIs

### vs OpenAI

- **Tool name**: Gemini: `codeExecution` | OpenAI: `code_interpreter` (Assistants API)
- **API model**: Gemini: single generateContent call | OpenAI: Assistants API with runs
- **Language**: Both: Python only
- **Libraries**: Similar (NumPy, Pandas, Matplotlib, etc.)
- **Network**: Neither has network access in sandbox
- **File I/O**: Gemini: no file persistence | OpenAI: file upload/download in Assistants
- **Simplicity**: Gemini: much simpler (one API call) | OpenAI: requires Assistant + Thread + Run

### vs Anthropic

- **Tool name**: Gemini: `codeExecution` | Anthropic: `code_execution` (server-side tool)
- **Execution**: Both server-side sandboxed Python
- **API model**: Gemini: single call | Anthropic: tool use loop
- **Libraries**: Similar availability

## Error Responses

- `OUTCOME_FAILED`: Code execution error (syntax error, runtime exception)
- `OUTCOME_DEADLINE_EXCEEDED`: Code took too long to execute

## Rate Limiting / Throttling

Standard rate limits apply. Code execution adds latency. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] No network access in sandbox (GEMAPI-SC-GOOG-CODEXE)
- No file persistence between API calls
- Execution timeout applies (code that runs too long is terminated)
- Python only (no other languages)

## Gotchas and Quirks

- Model decides autonomously whether to use code execution - cannot force it
- Multiple code blocks possible in a single response (iterative problem solving)
- Output includes both code and results as separate parts - iterate through all parts
- Matplotlib plots are generated but returned as text descriptions, not images
- No file upload/download capability unlike OpenAI's Code Interpreter

## Sources

- GEMAPI-SC-GOOG-CODEXE: https://ai.google.dev/gemini-api/docs/code-execution [VERIFIED]
- GEMAPI-SC-GOOG-TOOLCM: https://ai.google.dev/gemini-api/docs/tool-combination [VERIFIED]

## Document History

**[2026-03-20 07:35]**
- Fixed: types.CodeExecution() does not exist in SDK. Corrected to types.ToolCodeExecution()
- Source: google-genai v1.68.0, google/genai/types.py

**[2026-03-20 04:15]**
- Initial document created
