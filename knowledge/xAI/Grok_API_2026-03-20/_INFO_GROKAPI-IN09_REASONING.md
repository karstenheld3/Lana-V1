# INFO: Reasoning Models

**Doc ID**: GROKAPI-IN09
**Goal**: Reasoning model behavior, encrypted reasoning content, reasoning effort, consumption
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Grok reasoning models think step-by-step before responding, excelling at math, logic, and quantitative problems. Key models: Grok 4 (always-reasoning, no reasoning_effort parameter), Grok 4.20 (reasoning and non-reasoning variants), Grok 3 Mini (supports reasoning_effort: "low"/"high"). Reasoning tokens are tracked in `usage.completion_tokens_details.reasoning_tokens` and add to total consumption. Encrypted reasoning content can be returned via `include: ["reasoning.encrypted_content"]` in the Responses API - this encrypted blob must be passed back in subsequent requests to maintain reasoning continuity across turns. In Chat Completions, only `grok-3-mini` returns `message.reasoning_content`. Grok 3, Grok 4, and Grok 4 Fast Reasoning do NOT return reasoning_content in Chat Completions; use the Responses API with encrypted content instead. Reasoning models require longer timeouts (3600s recommended). [VERIFIED] (GROKAPI-SC-XAI-REASONING | https://docs.x.ai/developers/model-capabilities/text/reasoning)

## Key Facts

- [VERIFIED] `reasoning_effort` only supported by `grok-3-mini` (values: "low", "high") (GROKAPI-SC-XAI-REASONING)
- [VERIFIED] `grok-4` does NOT support reasoning_effort - specifying it returns an error (GROKAPI-SC-XAI-REASONING)
- [VERIFIED] `grok-4` is always-reasoning - no non-reasoning mode (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] `grok-4` does not support presencePenalty, frequencyPenalty, stop params (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Encrypted reasoning: `include: ["reasoning.encrypted_content"]` in Responses API (GROKAPI-SC-XAI-REASONING)
- [VERIFIED] In Chat Completions, only grok-3-mini returns `message.reasoning_content` (GROKAPI-SC-XAI-REASONING)
- [VERIFIED] Reasoning tokens billed as completion tokens (GROKAPI-SC-XAI-REASONING)
- [VERIFIED] Recommended timeout: 3600s for reasoning models (GROKAPI-SC-XAI-GENTEXT)

## Quick Reference

- **Always reasoning**: grok-4, grok-4-fast-reasoning
- **Reasoning + non-reasoning**: grok-4.20 (use `-reasoning` or `-non-reasoning` suffix)
- **Controllable reasoning**: grok-3-mini (`reasoning_effort`: "low" or "high")
- **Encrypted content**: `include: ["reasoning.encrypted_content"]` (Responses API only)
- **Token tracking**: `usage.completion_tokens_details.reasoning_tokens`

## Examples

### Reasoning with Grok 3 Mini (Controllable Effort)

```python
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0),
)

response = client.responses.create(
    model="grok-3-mini",
    reasoning={"effort": "high"},
    input=[
        {"role": "system", "content": "You are a math expert."},
        {"role": "user", "content": "What is 101*3?"},
    ],
)

message = next(item for item in response.output if item.type == "message")
text = next(c.text for c in message.content if c.type == "output_text")

print(f"Answer: {text}")
print(f"Reasoning tokens: {response.usage.output_tokens_details.reasoning_tokens}")
print(f"Total output tokens: {response.usage.output_tokens}")
```

### Encrypted Reasoning Content (Multi-Turn)

```python
# First request with encrypted thinking
r1 = client.responses.create(
    model="grok-4.20-reasoning",
    input=[
        {"role": "user", "content": "Solve: If 3x + 7 = 22, what is x?"},
    ],
    include=["reasoning.encrypted_content"],
)
print(f"Answer: {r1.output_text}")

# Continue with reasoning context preserved
r2 = client.responses.create(
    model="grok-4.20-reasoning",
    previous_response_id=r1.id,
    input=[
        {"role": "user", "content": "Now solve for y if 2y + x = 15"},
    ],
    include=["reasoning.encrypted_content"],
)
print(f"Answer: {r2.output_text}")
```

## Differences from Other APIs

### vs OpenAI

- **Reasoning effort**: xAI only supports on grok-3-mini; OpenAI supports on o1/o3 models
- **Encrypted reasoning**: xAI encrypts reasoning traces; OpenAI exposes reasoning_content/thinking blocks
- **Always-reasoning**: Grok 4 has no non-reasoning mode; OpenAI o1/o3 always reason but have effort control
- **Parameter restrictions**: Grok 4 rejects presencePenalty, frequencyPenalty, stop; OpenAI o1 has similar restrictions

### vs Anthropic

- **Thinking blocks**: Anthropic exposes full thinking in `thinking` blocks; xAI encrypts reasoning
- **Budget tokens**: Anthropic uses `budget_tokens` for thinking control; xAI uses `reasoning_effort` ("low"/"high")
- **Visibility**: Anthropic thinking is readable; xAI reasoning is opaque (encrypted)

### vs Gemini

- **Thinking**: Gemini 2.5 Pro exposes thinking; xAI encrypts reasoning
- **Configuration**: Gemini uses `thinkingConfig.thinkingBudget`; xAI uses `reasoning_effort`

## Limitations and Known Issues

- [VERIFIED] grok-4 always reasons, cannot be disabled (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] reasoning_effort errors on grok-3, grok-4, grok-4-fast-reasoning (GROKAPI-SC-XAI-REASONING)
- [VERIFIED] Reasoning content not visible - only encrypted blob available (GROKAPI-SC-XAI-REASONING)
- [VERIFIED] Reasoning tokens significantly increase total token consumption and cost (GROKAPI-SC-XAI-REASONING)

## Sources

- GROKAPI-SC-XAI-REASONING | https://docs.x.ai/developers/model-capabilities/text/reasoning | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:40]**
- Initial document created with reasoning model reference and encrypted content handling
