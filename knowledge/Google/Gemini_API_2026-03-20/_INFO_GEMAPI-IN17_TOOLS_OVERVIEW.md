# INFO: Gemini API Tools Overview

**Doc ID**: GEMAPI-IN17
**Goal**: Document built-in tool types, tool configuration, and server-side execution
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini API provides several built-in tools that execute server-side on Google's infrastructure without requiring user code: Google Search (grounding with web search results and citations), Google Maps (location-based grounding), URL Context (web page content extraction), Code Execution (Python sandbox), and Computer Use (UI automation). These tools are configured in the `tools` array alongside custom function declarations. For built-in tools, the entire process happens within one API call - the model decides when to use tools and executes them automatically. Gemini 3 models support combining multiple built-in tools with custom function calling in a single request, with context circulation between tool calls. This multi-tool combination capability is unique to Gemini.

## Key Facts

- [VERIFIED] Built-in tools: google_search, google_maps, url_context, code_execution, computer_use (GEMAPI-SC-GOOG-TOOLS)
- [VERIFIED] Server-side execution - no user code needed for built-in tools (GEMAPI-SC-GOOG-TOOLS)
- [VERIFIED] One API call: model decides and executes tools automatically (GEMAPI-SC-GOOG-TOOLS)
- [VERIFIED] Gemini 3: combine built-in tools + custom functions in one request (GEMAPI-SC-GOOG-TOOLCM)
- [VERIFIED] Context circulation between tool calls (GEMAPI-SC-GOOG-TOOLCM)

## Quick Reference

**Built-in Tools:**
- `{"googleSearch": {}}` - Web search grounding
- `{"googleMaps": {}}` - Location grounding
- `{"urlContext": {}}` - Web page extraction
- `{"codeExecution": {}}` - Python sandbox
- `{"computerUse": {}}` - UI automation

## Tool Configuration

### Single Built-in Tool

```json
{
  "tools": [{"googleSearch": {}}],
  "contents": [{"parts": [{"text": "What happened in the news today?"}]}]
}
```

### Multiple Tools Combined (Gemini 3)

```json
{
  "tools": [
    {"googleSearch": {}},
    {"codeExecution": {}},
    {"functionDeclarations": [{"name": "save_result", "description": "Save result", "parameters": {"type": "object", "properties": {"data": {"type": "string"}}, "required": ["data"]}}]}
  ],
  "contents": [{"parts": [{"text": "Search for the latest GDP data, calculate growth rate, and save it."}]}]
}
```

## Python Examples

### Example 1: Google Search Grounding

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What are the latest developments in quantum computing?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
)
print(response.text)

# Access grounding metadata
if response.candidates[0].grounding_metadata:
    gm = response.candidates[0].grounding_metadata
    print(f"\nSearch queries: {gm.web_search_queries}")
    for chunk in gm.grounding_chunks or []:
        print(f"Source: {chunk.web.title} - {chunk.web.uri}")
```

### Example 2: Code Execution

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Calculate the first 20 Fibonacci numbers and plot them.",
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())]
    )
)
print(response.text)
```

### Example 3: Multi-Tool Combination (Gemini 3)

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Search for the current population of Tokyo, then write Python code to compare it with other major cities.",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(code_execution=types.ToolCodeExecution()),
        ]
    )
)
print(response.text)
```

## Comparison with Other APIs

### vs OpenAI

- **Built-in tools**: Gemini: 5 built-in server-side tools | OpenAI: web_search, code_interpreter, file_search (via Assistants)
- **Execution**: Gemini: all in single generateContent call | OpenAI: Assistants API with runs
- **Combination**: Gemini: multi-tool + function calling in one call | OpenAI: multiple tools in Assistants
- **UNIQUE**: Google Search grounding with structured citations, Google Maps grounding

### vs Anthropic

- **Built-in tools**: Gemini: 5 server-side tools | Anthropic: web_search, web_fetch, code_execution, computer_use, bash, text_editor
- **Execution**: Gemini: single call | Anthropic: multi-turn tool use loop
- **Combination**: Gemini 3: multi-tool single request | Anthropic: one tool type per response turn
- **UNIQUE to Gemini**: Google Search/Maps grounding, URL Context, multi-tool combination

## Error Responses

- **400**: Invalid tool configuration, incompatible tool combination
- Tool errors may appear in response content rather than HTTP errors

## Rate Limiting / Throttling

Built-in tool usage may have additional rate limits beyond standard RPM/TPM. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Not all tool combinations supported in all models (GEMAPI-SC-GOOG-TOOLCM)
- [VERIFIED] Built-in tools not available via OpenAI compatibility endpoint (GEMAPI-SC-GOOG-OAICOM)

## Gotchas and Quirks

- Built-in tools execute server-side in a single API call - no tool_use loop needed
- Multi-tool combination only works with Gemini 3+ models
- Tool responses may include `toolCall` and `toolResponse` parts mixed with `functionCall`
- Google Search results include mandatory search suggestions widget (ToS requirement)
- Built-in tools unavailable through OpenAI compat endpoint

## Sources

- GEMAPI-SC-GOOG-TOOLS: https://ai.google.dev/gemini-api/docs/tools [VERIFIED]
- GEMAPI-SC-GOOG-TOOLCM: https://ai.google.dev/gemini-api/docs/tool-combination [VERIFIED]

## Document History

**[2026-03-20 07:35]**
- Fixed: types.CodeExecution() does not exist in SDK. Corrected to types.ToolCodeExecution()
- Source: google-genai v1.68.0, google/genai/types.py

**[2026-03-20 04:05]**
- Initial document created with built-in tools overview
