# Token Counting

**Doc ID**: OAIAPI-IN09
**Goal**: Document input token counting endpoint for pre-request estimation and cost calculation
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Token Counting API (POST /v1/responses/input_tokens/count) provides pre-request token estimation for Responses API inputs. Count tokens before making actual API call to estimate costs, validate against context window limits, and optimize prompt length. Accepts same input structure as Responses API create endpoint but returns token count instead of generating response. Response includes total input tokens and per-item breakdown. Does not consume generation quota. Supports all input types: text, images, tools, system prompts. Model-specific tokenization - different models may tokenize same input differently. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-RESTOK)

## Key Facts

- **Endpoint**: POST /v1/responses/input_tokens/count [VERIFIED] (OAIAPI-SC-OAI-RESTOK)
- **Purpose**: Pre-request token estimation [VERIFIED]
- **No quota usage**: Counting doesn't consume generation limits [VERIFIED]
- **Model-specific**: Tokenization varies by model [VERIFIED]
- **Input structure**: Same as Responses API create request [VERIFIED]

## Request Schema

### Required Parameters

- **model**: Model ID (determines tokenization)
- **input**: Array of input items (same as Responses API)

### Optional Parameters

- **tools**: Tool definitions (to count tool tokens)
- **text**: Text settings (for format-specific counting)

## Response Schema

```json
{
  "total_tokens": 150,
  "breakdown": [
    {
      "type": "message",
      "index": 0,
      "tokens": 50
    },
    {
      "type": "tool",
      "index": 0,
      "tokens": 100
    }
  ]
}
```

**Fields:**
- **total_tokens**: Total input token count
- **breakdown**: Per-item token counts
  - **type**: Item type (message, tool, system)
  - **index**: Item index in input array
  - **tokens**: Token count for this item

## Token Counting Logic

### Text Tokenization

Different models use different tokenizers:
- **GPT-5.x models**: cl100k_base tokenizer
- **o-series models**: o200k_base tokenizer
- **Legacy models**: p50k_base or r50k_base

### Image Tokens

Image tokens depend on:
- Image resolution (low/high)
- Image dimensions
- Detail level parameter

Base formula: `(width/patch_size) * (height/patch_size) * tokens_per_patch + base_tokens`

### Tool Tokens

Tool definitions consume tokens:
- Function name
- Function description
- Parameter schema
- Examples (if provided)

## SDK Examples (Python)

### Basic Token Counting

```python
from openai import OpenAI

client = OpenAI()

count = client.responses.input_tokens.count(
    model="gpt-5.6-sol",
    input=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What is quantum computing?"}
    ]
)

print(f"Total tokens: {count.input_tokens}")
```

### Count with Tools

```python
from openai import OpenAI

client = OpenAI()

count = client.responses.input_tokens.count(
    model="gpt-5.6-sol",
    input=[
        {"role": "user", "content": "What's the weather?"}
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            }
        }
    ]
)

print(f"Total tokens (including tools): {count.input_tokens}")
```

### Cost Estimation Helper

```python
from openai import OpenAI

def estimate_cost(model: str, input_items: list, estimated_output_tokens: int = 500):
    client = OpenAI()
    
    count = client.responses.input_tokens.count(
        model=model,
        input=input_items
    )
    
    pricing = {
        "gpt-5.5": {"input": 5.00, "output": 30.00},
        "gpt-5.4": {"input": 2.50, "output": 15.00},
        "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
        "gpt-5.4-nano": {"input": 0.20, "output": 1.25},
    }
    
    if model not in pricing:
        return f"Unknown model: {model}"
    
    input_cost = (count.input_tokens / 1_000_000) * pricing[model]["input"]
    output_cost = (estimated_output_tokens / 1_000_000) * pricing[model]["output"]
    total_cost = input_cost + output_cost
    
    return {
        "input_tokens": count.input_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "input_cost": f"${input_cost:.6f}",
        "output_cost": f"${output_cost:.6f}",
        "total_cost": f"${total_cost:.6f}"
    }

# Usage
estimate = estimate_cost(
    "gpt-5.5",
    [{"role": "user", "content": "Explain AI in detail"}],
    estimated_output_tokens=1000
)
print(estimate)
```

### Context Window Validation

```python
from openai import OpenAI

def validate_context_window(model: str, input_items: list):
    client = OpenAI()
    
    limits = {
        "gpt-5.5": 1_048_576,
        "gpt-5.4": 1_000_000,
        "gpt-5.4-mini": 400_000,
        "gpt-5.4-nano": 400_000,
    }
    
    count = client.responses.input_tokens.count(
        model=model,
        input=input_items
    )
    
    limit = limits.get(model, 128_000)
    remaining = limit - count.input_tokens
    
    return {
        "input_tokens": count.input_tokens,
        "context_limit": limit,
        "remaining_tokens": remaining,
        "fits": remaining > 0,
        "utilization": f"{(count.input_tokens / limit) * 100:.1f}%"
    }

# Usage
validation = validate_context_window(
    "gpt-5.5",
    [{"role": "user", "content": "Long prompt..."}]
)
print(validation)
```

### Batch Token Estimation

```python
from openai import OpenAI

client = OpenAI()

prompts = [
    "Explain quantum computing",
    "What is machine learning?",
    "Describe neural networks"
]

total_tokens = 0
for prompt in prompts:
    count = client.responses.input_tokens.count(
        model="gpt-5.6-sol",
        input=[{"role": "user", "content": prompt}]
    )
    total_tokens += count.input_tokens
    print(f"{prompt[:30]}... : {count.input_tokens} tokens")

print(f"\nTotal for batch: {total_tokens} tokens")
```

## Error Responses

- **400 Bad Request** - Invalid model or input structure
- **404 Not Found** - Model does not exist
- **429 Too Many Requests** - Rate limit exceeded (counting has limits too)

## Rate Limiting / Throttling

- **Counting has limits**: Token counting requests count toward RPM
- **Lower quota impact**: Doesn't consume generation quota but has own limits

## Differences from Other APIs

- **vs Anthropic**: Anthropic has beta message counting API with different structure
- **vs Gemini**: Gemini uses `countTokens` method with similar purpose
- **vs tiktoken library**: Server-side counting vs client-side estimation

## Limitations and Known Issues

- **Output estimation not included**: Only counts input tokens, not predicted output [VERIFIED] (OAIAPI-SC-OAI-RESTOK)
- **Image token approximation**: Image tokens may vary slightly from actual [ASSUMED]
- **Tool token variability**: Tool usage tokens not included in count [ASSUMED]

## Gotchas and Quirks

- **Model must match**: Use same model for counting and generation [VERIFIED] (OAIAPI-SC-OAI-RESTOK)
- **Conversation context not counted**: Only counts input array, not conversation history [VERIFIED]
- **Special tokens included**: System tokens and formatting tokens counted [ASSUMED]

## TypeScript Examples

### Count Input Tokens

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const count = await client.responses.inputTokens.count({
  model: "gpt-4o-mini",
  input: [
    { role: "system", content: "You are helpful." },
    { role: "user", content: "What is quantum computing?" },
  ],
});

console.log(`Input tokens: ${count.input_tokens}`);
```

## Sources

- OAIAPI-SC-OAI-RESTOK - POST Count input tokens
- OAIAPI-SC-OAI-RESCRT - POST Create a response (for input structure)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:15]**
- Enriched: Full request/response schema, SDK examples, cost estimation, gotchas from 2026-03-20
- Updated: Model refs to gpt-5.5, pricing to current ($5/$30, $2.50/$15)
- Updated: Context window limits (GPT-5.5: 1M+)

**[2026-05-22 11:40]**
- Stub created
