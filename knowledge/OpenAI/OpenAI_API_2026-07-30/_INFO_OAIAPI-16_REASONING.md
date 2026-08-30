# Reasoning Models

**Doc ID**: OAIAPI-IN16
**Goal**: Document reasoning models, effort levels, reasoning summaries
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Reasoning models (GPT-5.6, GPT-5.5, GPT-5.4, GPT-5.4-mini) perform internal chain-of-thought reasoning before generating output. GPT-5.6 (2026-07) introduces 6 effort levels: `none`, `low`, `medium` (default), `high`, `xhigh`, `max`. **New features in GPT-5.6**: Pro mode (`reasoning.mode: "pro"`) applies more compute for harder tasks; persisted reasoning (`reasoning.context`) carries chain-of-thought across turns without rebuilding; `max` effort level explores alternatives and revises approach. GPT-5.6 Sol is the current top reasoning model, with Terra and Luna offering the same effort levels at lower cost. GPT-5.5 and GPT-5.5-pro are deprecated (removal 2026-12-11). Reasoning summaries provide visibility into the model's thought process. [VERIFIED] (OAIAPI-SC-OAI-GREASN, OAIAPI-SC-OAI-GLATEST)

## Key Facts

- **Models**: GPT-5.6 Sol/Terra/Luna (flagship), GPT-5.5 (deprecated), GPT-5.4, GPT-5.4-mini [VERIFIED] (OAIAPI-SC-OAI-GLATEST)
- **Effort levels**: none, low, medium, high, xhigh, max (6 levels in GPT-5.6) [VERIFIED] (OAIAPI-SC-OAI-GLATEST)
- **Pro mode**: `reasoning.mode: "pro"` - more compute, higher reliability, increased latency [VERIFIED] (OAIAPI-SC-OAI-GLATEST)
- **Persisted reasoning**: `reasoning.context` carries chain-of-thought across turns [VERIFIED] (OAIAPI-SC-OAI-GLATEST)
- **Thinking tokens**: Internal reasoning not visible by default [VERIFIED] (OAIAPI-SC-OAI-GREASN)
- **Summaries**: Optional reasoning summaries in output [VERIFIED] (OAIAPI-SC-OAI-GREASN)
- **Cost**: Higher effort = more tokens = higher cost [VERIFIED] (OAIAPI-SC-OAI-GREASN)

## Use Cases

- **Complex problem-solving**: Multi-step reasoning tasks
- **Mathematical proofs**: Formal logic and mathematics
- **Code debugging**: Tracing through complex logic
- **Strategic planning**: Analyzing options and trade-offs
- **Research analysis**: Synthesizing information from multiple sources

## Reasoning Effort Levels

### none
- **Reasoning**: Disabled, standard text generation
- **Latency**: Fastest
- **Cost**: Lowest
- **Use case**: Simple tasks not requiring reasoning (GPT-5.5 specific)

### low
- **Reasoning**: Minimal, quick analysis
- **Latency**: Fast
- **Cost**: Low
- **Use case**: Straightforward problems with clear solutions

### medium (default for GPT-5.5)
- **Reasoning**: Balanced reasoning depth
- **Latency**: Moderate
- **Cost**: Moderate
- **Use case**: General problem-solving

### high
- **Reasoning**: Thorough analysis
- **Latency**: Slower
- **Cost**: Higher
- **Use case**: Complex multi-step problems

### xhigh
- **Reasoning**: Very deep analysis
- **Latency**: Slow
- **Cost**: Very high
- **Use case**: Extremely difficult tasks requiring deep analysis

### max (NEW - GPT-5.6)
- **Reasoning**: Maximum exploration, revises approach, tries alternatives
- **Latency**: Slowest
- **Cost**: Highest
- **Use case**: Frontier-difficulty problems where quality trumps speed

## Pro Mode (NEW - GPT-5.6)

Pro mode (`reasoning.mode: "pro"`) applies more model work before returning. Increases reliability on difficult tasks. Tokens from that work billed at standard rates. Available on all GPT-5.6 tiers (Sol, Terra, Luna). Not a separate model - a setting on existing models.

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Analyze the security implications of this protocol design...",
    reasoning={"mode": "pro", "effort": "high"},
)
print(response.output_text)
```

## Persisted Reasoning (NEW - GPT-5.6)

Reasoning context carries across turns without rebuilding the chain of thought:

```python
from openai import OpenAI

client = OpenAI()

# First turn
response1 = client.responses.create(
    model="gpt-5.6-sol",
    input="Design a distributed cache eviction strategy.",
    reasoning={"effort": "high"},
)

# Second turn - reasoning persists via previous_response_id + context mode
response2 = client.responses.create(
    model="gpt-5.6-sol",
    input="Now add fault tolerance to the design.",
    previous_response_id=response1.id,
    reasoning={"effort": "high", "context": "all_turns"},
)
print(response2.output_text)
```

## Thinking Budget

- Budget determines max reasoning tokens
- Models stop reasoning when budget exhausted
- Budget scales with effort level
- Budget not directly controllable - managed by effort level
- GPT-5.6 Pro mode provides extended compute (replaces GPT-5.5-pro approach)

## SDK Examples (Python)

### Basic Reasoning (Responses API)

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Prove that the square root of 2 is irrational.",
    reasoning={"effort": "high"},
)
print(response.output_text)
```

### Chat Completions API

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "Solve this optimization problem..."}],
    reasoning_effort="high",
    max_completion_tokens=8192,
)
print(response.choices[0].message.content)
```

### Reasoning Summaries

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Analyze the complexity of this algorithm...",
    reasoning={"effort": "high", "summary": "auto"},
)
# Access reasoning summary
for item in response.output:
    if hasattr(item, "summary"):
        print(f"Reasoning: {item.summary}")
```

### Reasoning for Code Analysis

```python
from openai import OpenAI

client = OpenAI()

code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

response = client.responses.create(
    model="gpt-5.6-sol",
    input=f"Analyze this code for bugs and performance issues:\n\n{code}",
    reasoning={"effort": "high", "summary": "auto"},
)
print(response.output_text)
```

### Comparing Effort Levels

```python
from openai import OpenAI
import time

client = OpenAI()

problem = "Design an efficient algorithm to find the longest palindromic substring."

for effort in ["low", "medium", "high"]:
    start = time.time()

    response = client.responses.create(
        model="gpt-5.6-sol",
        input=problem,
        reasoning={"effort": effort}
    )

    elapsed = time.time() - start

    print(f"\n=== Effort: {effort} ===")
    print(f"Time: {elapsed:.2f}s")
    print(f"Tokens: {response.usage.total_tokens}")
    print(f"Response length: {len(response.output_text)} chars")
```

### Reasoning with Conversation State (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/responses/responses.py
# SDK uses conversation={"id": "..."} not conversation_id="..."
from openai import OpenAI

client = OpenAI()

conversation = client.conversations.create()

response1 = client.responses.create(
    model="gpt-5.6-sol",
    conversation={"id": conversation.id},
    input="I'm building a distributed cache. What are the key design considerations?",
    reasoning={"effort": "high"}
)

print("=== Initial Analysis ===")
print(response1.output_text)

response2 = client.responses.create(
    model="gpt-5.6-sol",
    conversation={"id": conversation.id},
    input="Now compare consistent hashing vs. rendezvous hashing for this use case",
    reasoning={"effort": "high", "summary": "auto"}
)

print("\n=== Comparison with Reasoning ===")
print(response2.output_text)
```

## Error Responses

- **400 Bad Request** - Invalid reasoning configuration (e.g., unsupported effort level)
- **Model not supported** - Non-reasoning model with reasoning parameters returns error

## Rate Limiting

- **Thinking tokens count**: Internal reasoning tokens count toward TPM limits [VERIFIED]
- **Higher costs**: Reasoning models consume more tokens per request
- **Effort impacts limits**: Higher effort consumes more quota per request

## Limitations and Known Issues

- **Thinking not always visible**: Internal reasoning hidden unless summaries enabled [VERIFIED] (OAIAPI-SC-OAI-GREASN)
- **Effort not guaranteed**: Model may use less reasoning if problem is simple [COMMUNITY]
- **Latency variability**: High effort can vary significantly in response time [COMMUNITY]

## Gotchas and Quirks

- **GPT-5.5 default is medium**: Not high like some older o-series models [VERIFIED]
- **o-series deprecated**: o4-mini, o3-pro, o3-mini replaced by GPT-5.6/5.5 (o-series removed 2026-12-11) [VERIFIED]
- **Token cost**: Higher reasoning effort = more reasoning tokens consumed (can 2-3x total cost) [VERIFIED]
- **Simple tasks don't benefit**: Reasoning overhead not worth it for basic questions [VERIFIED] (OAIAPI-SC-OAI-GREASN)
- **No thinking token visibility**: Cannot see raw thinking without summaries [VERIFIED] (OAIAPI-SC-OAI-GREASN)
- **conversation param**: Use `conversation={"id": "..."}` not `conversation_id="..."` [TESTED] (SDK v2.45.0)

## TypeScript Examples

### Reasoning with Effort Control

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "o4-mini",
  input: "What is the square root of 144?",
  reasoning: { effort: "low" },
});

console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-GREASN - Reasoning Models guide
- OAIAPI-SC-OAI-MGP55 - GPT-5.5 model page
- OAIAPI-SC-OAI-GMODLS - Models overview

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 13:19]**
- Fixed: Persisted reasoning example (reasoning_context attribute does not exist, use previous_response_id + context: "all_turns")
- Fixed: SDK version references v2.38.0 → v2.45.0
- Fixed: Informal date in summary
- Fixed: o-series deprecation text updated for GPT-5.6 era

**[2026-07-13 12:00]**
- Added: GPT-5.6 as flagship reasoning model (Sol/Terra/Luna)
- Added: `max` effort level (6th level, GPT-5.6 only)
- Added: Pro mode (`reasoning.mode: "pro"`)
- Added: Persisted reasoning (`reasoning.context`) across turns
- Changed: GPT-5.5 marked deprecated, o-series being retired
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 22:00]**
- Enriched: Full effort levels detail, thinking budget, code analysis example, comparison example, conversation state, gotchas

**[2026-05-22 11:00]**
- Updated from 2026-03-20 version
- Changed: GPT-5.5 is now top reasoning model (default medium)
- Added: o-series deprecation notice
