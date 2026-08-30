# INFO: Gemini API Computer Use

**Doc ID**: GEMAPI-IN22
**Goal**: Document Computer Use model for screen understanding and UI automation
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini Computer Use is a specialized model (`gemini-2.5-computer-use-preview`) that can "see" digital screens and perform UI actions like clicking, typing, scrolling, and navigating. The model accepts screenshots as input and returns structured action commands. It is designed for automating complex browser tasks and desktop workflows. The model processes screenshots to understand UI state and outputs actions in a structured format. This is still in preview status. Computer Use requires an execution environment (browser automation framework or desktop agent) that captures screenshots and executes the model's action commands - the model itself does not control a browser directly via the API. Both Gemini and Anthropic offer Computer Use models; OpenAI does not have an equivalent.

## Key Facts

- [VERIFIED] Model: `gemini-2.5-computer-use-preview` (GEMAPI-SC-GOOG-CMPUSE)
- [VERIFIED] Input: screenshots (images) + task description (GEMAPI-SC-GOOG-CMPUSE)
- [VERIFIED] Output: structured UI action commands (click, type, scroll, etc.) (GEMAPI-SC-GOOG-CMPUSE)
- [VERIFIED] Requires execution environment to capture screens and execute actions (GEMAPI-SC-GOOG-CMPUSE)
- [VERIFIED] Preview status (GEMAPI-SC-GOOG-MODELS)

## Quick Reference

**Model**: `gemini-2.5-computer-use-preview`
**Input**: Screenshots + task description
**Output**: Structured action commands
**Status**: Preview

## Python Examples

### Example 1: Basic Computer Use

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Capture screenshot (from your automation framework)
with open("screenshot.png", "rb") as f:
    screenshot_data = base64.b64encode(f.read()).decode("utf-8")

response = client.models.generate_content(
    model="gemini-2.5-computer-use-preview",
    contents=[
        types.Content(role="user", parts=[
            types.Part(inline_data=types.Blob(
                mime_type="image/png", data=screenshot_data
            )),
            types.Part(text="Click on the search bar and type 'Gemini API documentation'"),
        ])
    ]
)

# Parse action commands from response
print(response.text)
```

## Comparison with Other APIs

### vs OpenAI

- **Computer Use**: Gemini: yes (preview) | OpenAI: **no equivalent**

### vs Anthropic

- **Computer Use**: Gemini: `gemini-2.5-computer-use-preview` | Anthropic: `computer_use` tool with Claude
- **Approach**: Gemini: dedicated model | Anthropic: tool within standard model
- **Actions**: Both: click, type, scroll, screenshot
- **Status**: Both in preview/beta

## Error Responses

- **400**: Invalid screenshot format or resolution
- Model may return "unable to determine action" for ambiguous UI states

## Rate Limiting / Throttling

Preview model has restricted rate limits. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Preview status - API may change (GEMAPI-SC-GOOG-MODELS)
- Requires external execution environment (Playwright, Selenium, etc.)
- Not suitable for production workflows yet

## Gotchas and Quirks

- Model does NOT control a browser directly - you must implement the action execution loop
- Screenshot quality affects action accuracy - use consistent resolution
- Multi-step tasks require iterative screenshot-action-screenshot loops
- Preview model has more restricted rate limits than stable models

## Sources

- GEMAPI-SC-GOOG-CMPUSE: https://ai.google.dev/gemini-api/docs/computer-use [VERIFIED]
- GEMAPI-SC-GOOG-MODELS: https://ai.google.dev/gemini-api/docs/models [VERIFIED]

## Document History

**[2026-03-20 04:30]**
- Initial document created
