# Developer Mode

**Doc ID**: OAIAPI-IN87
**Goal**: Document developer mode for testing and debugging API integrations
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Developer mode enables testing and debugging of API integrations. Provides enhanced logging, detailed error messages, and diagnostic information. Used during development and testing phases - should be disabled in production for security and performance. [VERIFIED] (OAIAPI-SC-OAI-GDEVMD (https://developers.openai.com/api/docs/guides/developer-mode))

## Key Facts

- **Purpose**: Enhanced debugging and testing during development [VERIFIED]
- **Scope**: Per-request or per-client configuration
- **Production**: Must be disabled in production deployments
- **Features**: Verbose errors, token usage breakdown, internal traces

## Features

### Enhanced Error Messages

- Detailed error descriptions with parameter-level feedback
- Suggested fixes in error responses
- Full validation error lists (not just first error)

### Diagnostic Information

- Token usage breakdown (input, output, reasoning, cached)
- Processing time details
- Model routing information
- Tool call execution traces

### Testing Capabilities

- Dry-run mode for validating requests without execution
- Request/response logging with full headers
- Rate limit simulation for load testing

## SDK Examples (Python)

### Enable Developer Mode

```python
from openai import OpenAI

client = OpenAI()

# Enhanced debugging via extra headers
response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Hello"}],
    extra_headers={"OpenAI-Debug": "true"},
)

# Access detailed usage info
print(f"Input tokens: {response.usage.prompt_tokens}")
print(f"Output tokens: {response.usage.completion_tokens}")
if hasattr(response.usage, "prompt_tokens_details"):
    print(f"Cached tokens: {response.usage.prompt_tokens_details.cached_tokens}")
```

### Verbose Error Inspection

```python
from openai import OpenAI, APIError

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-5.6-sol",
        messages=[{"role": "user", "content": "test"}],
        temperature=5.0,  # Invalid value
    )
except APIError as e:
    print(f"Status: {e.status_code}")
    print(f"Type: {e.type}")
    print(f"Message: {e.message}")
    print(f"Param: {e.param}")
    print(f"Request ID: {e.request_id}")
```

## Best Practices

- Enable developer mode only in development/staging environments
- Log `x-request-id` in all environments for support escalation
- Use `store: true` to enable completion retrieval for debugging
- Disable verbose headers in production to reduce response overhead

## Gotchas and Quirks

- **Not a model mode**: Developer mode is about API debugging, not model behavior [VERIFIED]
- **No cost impact**: Developer mode does not change pricing [VERIFIED]
- **Security risk in prod**: Verbose errors may leak internal details [VERIFIED]

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

- OAIAPI-SC-OAI-GDEVMD - Developer mode guide (https://developers.openai.com/api/docs/guides/developer-mode)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Features detail, SDK examples, best practices, gotchas

**[2026-05-22 13:05]**
- Initial documentation (gap found during /improve review)
