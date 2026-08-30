# API Optimization

**Doc ID**: OAIAPI-IN74
**Goal**: Document strategies for optimizing API cost, latency, and throughput
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

API optimization covers cost reduction, latency improvement, and throughput maximization. Cost strategies: prompt caching (automatic + explicit with breakpoints/TTL for GPT-5.6, up to 90% input discount), flex processing (50% discount), Batch API (50% discount, 24h window), model selection, max_completion_tokens, structured outputs. Latency: streaming, caching, shorter prompts, predicted outputs, model routing, Programmatic Tool Calling (reduces multi-tool round-trips). Model selection: GPT-5.6 Sol (best), GPT-5.6 Terra (balanced), GPT-5.6 Luna (efficient). [VERIFIED] (OAIAPI-SC-OAI-GBPRD, OAIAPI-SC-OAI-GCACH, OAIAPI-SC-OAI-GFLEX, OAIAPI-SC-OAI-GOPTIM, OAIAPI-SC-OAI-GCHLOG)

## Key Facts

- **Prompt caching**: Up to 90% cost, 80% latency reduction (automatic) [VERIFIED] (OAIAPI-SC-OAI-GCACH)
- **Flex processing**: 50% cost reduction [VERIFIED] (OAIAPI-SC-OAI-GFLEX)
- **Batch API**: 50% cost reduction, separate rate pool [VERIFIED] (OAIAPI-SC-OAI-GBATCH)
- **Model routing**: Use appropriate model size per task [VERIFIED] (OAIAPI-SC-OAI-GBPRD)
- **Streaming**: Reduces perceived latency via TTFT [VERIFIED] (OAIAPI-SC-OAI-GSTRM)
- **Predicted outputs**: Faster for edit-style tasks [VERIFIED] (OAIAPI-SC-OAI-CHATC)

## Sub-Guides

- **Latency optimization**: https://developers.openai.com/api/docs/guides/latency-optimization
- **Predicted Outputs**: https://developers.openai.com/api/docs/guides/predicted-outputs (IN81)
- **Priority processing**: https://developers.openai.com/api/docs/guides/priority-processing (IN84)
- **Cost optimization**: https://developers.openai.com/api/docs/guides/cost-optimization
- **Batch**: https://developers.openai.com/api/docs/guides/batch (IN32)
- **Flex processing**: https://developers.openai.com/api/docs/guides/flex-processing (IN72)
- **Accuracy optimization**: https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy

## Cost Optimization Matrix

- **Prompt caching** - Automatic, 50-90% input discount. Best for: repeated prompts, static context
- **Flex processing** - 50% discount, higher latency. Best for: background jobs, pipelines
- **Batch API** - 50% discount, 24h window. Best for: bulk offline processing
- **Smaller models** - Cheaper per token. Best for: classification, extraction, simple tasks
- **max_completion_tokens** - Prevent runaway costs. Best for: all requests
- **Structured outputs** - Constrain output format. Best for: data extraction

## SDK Examples (Python)

### Streaming (Latency Optimization)

```python
from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Explain async/await"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Predicted Outputs (Edit Tasks)

```python
from openai import OpenAI

client = OpenAI()

existing_code = """def hello():
    print("hello world")
"""

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {"role": "user", "content": f"Add type hints to this function:\n{existing_code}"}
    ],
    prediction={
        "type": "content",
        "content": existing_code
    }
)

print(response.choices[0].message.content)
```

### Parallel Requests (Throughput)

```python
from openai import AsyncOpenAI
import asyncio

async def parallel_completions(prompts: list, model: str = "gpt-5.5"):
    """Process multiple prompts concurrently"""
    client = AsyncOpenAI()
    
    sem = asyncio.Semaphore(20)
    
    async def single(prompt):
        async with sem:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=200
            )
            return response.choices[0].message.content
    
    return await asyncio.gather(*[single(p) for p in prompts])

results = asyncio.run(parallel_completions([
    "Summarize: topic A",
    "Summarize: topic B",
    "Summarize: topic C"
]))
```

### Model Routing Strategy

```python
from openai import OpenAI

client = OpenAI()

def route_model(task_type: str) -> str:
    """Select optimal model based on task complexity"""
    routing = {
        "classification": "gpt-5.4-nano",
        "extraction": "gpt-5.4-mini",
        "summarization": "gpt-5.4-mini",
        "code_generation": "gpt-5.5",
        "reasoning": "gpt-5.5",
        "research": "gpt-5.5-pro",
    }
    return routing.get(task_type, "gpt-5.5")

def smart_completion(task_type: str, prompt: str, **kwargs):
    model = route_model(task_type)
    return client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **kwargs
    )

result = smart_completion("classification", "Is this review positive? 'Great product!'")
result = smart_completion("reasoning", "Prove that sqrt(2) is irrational.")
```

## Token Optimization Tips

- **Concise system prompts**: Every token counts; trim instructions to essentials
- **Reference, don't repeat**: Use previous_response_id instead of re-sending history
- **Structured context**: Use JSON or bullet points instead of prose for context data
- **Token counting**: Use `tiktoken` library to estimate costs before sending
- **Image detail**: Use `detail: "low"` for images when high detail isn't needed
- **Stop sequences**: Set stop sequences to prevent unnecessary generation

### Token Counting

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-5.5") -> int:
    """Estimate token count for cost planning"""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

prompt = "Your prompt text here..."
tokens = count_tokens(prompt)
print(f"Estimated tokens: {tokens}")
```

## Cost Comparison (Relative)

```
Standard request:     100% cost, lowest latency
Flex processing:       50% cost, variable latency
Batch API:             50% cost, up to 24h latency
Cached tokens:      10-50% cost, lower latency
Cached + Flex:       5-25% cost, variable latency
```

## Differences from Other APIs

- **vs Anthropic**: Similar optimization patterns. Anthropic has explicit cache_control. No flex tier
- **vs Gemini**: Google has context caching (explicit TTL). Batch prediction API available
- **vs Grok**: Limited optimization options

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

- OAIAPI-SC-OAI-GBPRD - Production Best Practices
- OAIAPI-SC-OAI-GCACH - Prompt Caching Guide
- OAIAPI-SC-OAI-GFLEX - Flex Processing Guide
- OAIAPI-SC-OAI-GBATCH - Batch API Guide
- OAIAPI-SC-OAI-GOPTIM - Optimization Guide
- OAIAPI-SC-OAI-GPRMGD - Model Guide
- OAIAPI-SC-OAI-GPROUT - Predicted Outputs Guide
- OAIAPI-SC-OAI-GPRIO - Priority Processing Guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Changed: Model selection from GPT-5.5/5.4-mini/5.4-nano to GPT-5.6 Sol/Terra/Luna
- Added: Explicit caching with breakpoints/TTL (GPT-5.6)
- Added: Programmatic Tool Calling as latency optimization
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 18:10]**
- Enriched from 2026-03-20 IN74 (30 -> 210 lines)
- Updated model refs to gpt-5.5, gpt-5.4-mini, gpt-5.4-nano, gpt-5.5-pro

**[2026-05-22 13:25]**
- Expanded: Sub-guide links

**[2026-05-22 11:50]**
- Stub created
