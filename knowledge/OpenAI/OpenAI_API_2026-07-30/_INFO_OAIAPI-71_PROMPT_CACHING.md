# Prompt Caching

**Doc ID**: OAIAPI-IN71
**Goal**: Document automatic prompt caching, extended prompt caching (GPT-5.5), pricing discounts
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI provides multiple types of prompt caching: automatic in-memory caching (GPT-5.4 and older), extended prompt caching (GPT-5.5), and **explicit caching with TTL (GPT-5.6, NEW 2026-07)**. GPT-5.6 introduces explicit cache breakpoints (`cache_control: {"type": "breakpoint"}`) and configurable TTL, giving developers direct control over what gets cached and for how long. Cache writes billed at 1.25x standard input rate; cache reads retain 90% discount. Cached content lives at least 30 minutes (minimum guarantee). For organizations without ZDR, `prompt_cache_retention` defaults to 24h (changed 2026-05). Usage visible via `prompt_tokens_details.cached_tokens` in response. [VERIFIED] (OAIAPI-SC-OAI-GPCACH, OAIAPI-SC-OAI-GLATEST, OAIAPI-SC-OAI-GCHLOG)

## Caching Types

### In-Memory Prompt Caching
- **Supported by**: GPT-5.4, GPT-5.4-mini, GPT-5.4-nano, GPT-4o models
- **Behavior**: Automatic for repeated prompt prefixes within short time window
- **Duration**: Short-lived (minutes)
- **NOT supported by**: GPT-5.5

### Extended Prompt Caching
- **Supported by**: GPT-5.5, GPT-5.4 (both types)
- **Behavior**: Longer persistence, works across requests
- **Duration**: Longer-lived (hours to days, depending on usage)
- **Default retention**: 24h for non-ZDR orgs (changed from in-memory, 2026-05)

### Explicit Caching (NEW - GPT-5.6, 2026-07)
- **Supported by**: GPT-5.6 Sol, Terra, Luna
- **Behavior**: Developer-controlled breakpoints + TTL
- **Breakpoints**: `cache_control: {"type": "breakpoint"}` on input items
- **TTL**: Configurable, minimum 30 minutes guaranteed
- **Write cost**: 1.25x standard input rate
- **Read discount**: 90% (same as extended caching)
- **Use case**: Predictable caching for system prompts, large contexts, multi-turn agents
- **Key for GPT-5.5**: This is the ONLY caching type available

## Pricing Impact

- **GPT-5.5**: Cached input $0.50/MTok (vs $5.00 regular) = 90% savings
- **GPT-5.4**: Cached input varies by model tier
- **General rule**: Cached tokens are 10x cheaper than regular input tokens

## Optimization Strategies

### Static-First Pattern

Place unchanging content at the start of prompts:

```python
from openai import OpenAI

client = OpenAI()

# GOOD: Static instructions first (cached), dynamic query last
SYSTEM = """You are a medical coding specialist. Follow ICD-10-CM guidelines strictly.
Always provide the code, description, and supporting rationale.
Cross-reference with CPT codes when procedures are mentioned.
Flag any coding conflicts or ambiguities."""

# This prefix gets cached across all requests
response = client.responses.create(
    model="gpt-5.6-sol",
    instructions=SYSTEM,  # Static (cached)
    input="Patient presents with acute bronchitis and type 2 diabetes",  # Dynamic
)
print(f"Cached tokens: {response.usage.prompt_tokens_details.cached_tokens}")
```

### Large Context with Caching

For applications that reuse large documents:

```python
from openai import OpenAI

client = OpenAI()

# Load a large document once
with open("api_spec.md", "r") as f:
    spec_content = f.read()

# All queries against this document benefit from caching
questions = [
    "What authentication methods are supported?",
    "List all POST endpoints.",
    "What are the rate limits?",
]

for q in questions:
    response = client.responses.create(
        model="gpt-5.6-sol",
        instructions=f"Answer questions about this API specification:\n\n{spec_content}",
        input=q,
    )
    cached = response.usage.prompt_tokens_details.cached_tokens
    total = response.usage.input_tokens
    print(f"Q: {q}")
    print(f"  Cache: {cached}/{total} tokens ({cached/total*100:.0f}%)")
```

### Monitoring Cache Performance

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {"role": "system", "content": "Large static prompt..."},
        {"role": "user", "content": "Dynamic query"},
    ],
)

usage = response.usage
cached = usage.prompt_tokens_details.cached_tokens
total = usage.prompt_tokens
cache_rate = (cached / total * 100) if total > 0 else 0
savings = cached * (5.00 - 0.50) / 1_000_000  # Approximate savings for GPT-5.5

print(f"Cache rate: {cache_rate:.1f}%")
print(f"Approximate savings: ${savings:.4f}")
```

## Error Responses

- No specific error codes for caching (transparent feature)
- Cache misses silently fall back to full-price input tokens

## Gotchas and Quirks

- **GPT-5.5 ONLY extended**: In-memory caching does NOT work with GPT-5.5 [VERIFIED] (OAIAPI-SC-OAI-MGP55)
- **Prefix matching**: Cache keys match from the START of the prompt. Any change in the prefix invalidates the cache [VERIFIED]
- **First request**: First request to a new prompt prefix is never cached (must build cache first) [VERIFIED]
- **Cache eviction**: Extended cache can be evicted if not used for extended periods [ASSUMED]
- **Batch/Flex**: Caching also applies to Batch and Flex processing modes [ASSUMED]

## TypeScript Examples

### Client Setup and Basic Usage

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  organization: process.env.OPENAI_ORG_ID,
});

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Hello!",
});
console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GPCACH - Prompt Caching guide
- OAIAPI-SC-OAI-MGP55 - GPT-5.5 model page (caching specifics)
- OAIAPI-SC-OAI-GLATEST - Using GPT-5.5 guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: GPT-5.6 explicit caching with breakpoints and TTL
- Added: prompt_cache_retention default change to 24h (2026-05)
- Added: Write cost (1.25x) and minimum 30-min guarantee
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 10:55]**
- Major update from 2026-03-20 version
- Added: Extended prompt caching as distinct type
- Added: GPT-5.5 caching limitation (no in-memory)
- Added: Pricing impact calculations
- Added: Monitoring and optimization examples
