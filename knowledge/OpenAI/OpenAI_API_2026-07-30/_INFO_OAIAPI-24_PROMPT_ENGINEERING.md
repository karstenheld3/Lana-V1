# Prompt Engineering

**Doc ID**: OAIAPI-IN24
**Goal**: Document prompt engineering best practices, reusable prompts, and prompt guidance
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Prompt engineering covers techniques for crafting effective instructions for OpenAI models. Key techniques: clear instructions (developer/system messages), few-shot examples, chain-of-thought reasoning, structured output specification, role-playing, and constraint definition. **DEPRECATED (2026-06-03)**: Reusable Prompts - migrate to application-managed prompt templates. GPT-5.6 performs best with less prescriptive prompts - reduce step-by-step guidance and let the model choose its approach. Pro mode (`reasoning.mode: "pro"`) handles complex tasks autonomously. For reasoning models, use developer messages, avoid chain-of-thought instructions, set `reasoning.effort`. See IN93 for GPT-5.6-specific guidance. [VERIFIED] (OAIAPI-SC-OAI-GPRMPT, OAIAPI-SC-OAI-GPRMGD, OAIAPI-SC-OAI-GCHLOG)

## Key Facts

- **Developer messages**: Replace system messages for o1+ models [VERIFIED]
- **Few-shot**: Include example input-output pairs [VERIFIED]
- **Chain-of-thought**: "Think step by step" for complex reasoning (non-reasoning models only) [VERIFIED]
- **Reusable prompts**: Dashboard-managed templates with variables [VERIFIED]
- **Reasoning models**: Don't instruct to think step-by-step (they do it automatically) [VERIFIED]
- **GPT-5.5**: Less prescriptive prompts work better [VERIFIED]

## Core Techniques

### 1. Clear Instructions

```python
# BAD: vague
messages = [{"role": "user", "content": "Help with my code"}]

# GOOD: specific
messages = [
    {"role": "developer", "content": "You are a Python code reviewer. Identify bugs, suggest fixes, and follow PEP 8."},
    {"role": "user", "content": "Review this function for bugs:\ndef calc(x, y):\n  return x/y"}
]
```

### 2. Few-Shot Examples

```python
messages = [
    {"role": "developer", "content": "Classify customer feedback as positive, negative, or neutral."},
    {"role": "user", "content": "Great product, fast shipping!"},
    {"role": "assistant", "content": "positive"},
    {"role": "user", "content": "Item arrived broken."},
    {"role": "assistant", "content": "negative"},
    {"role": "user", "content": "The package came on time."},
]
```

### 3. Chain-of-Thought (Non-Reasoning Models)

```python
messages = [
    {"role": "developer", "content": "Solve math problems step by step. Show your work."},
    {"role": "user", "content": "If a train travels 120km in 2 hours, and then 180km in 3 hours, what is the average speed?"}
]
```

### 4. Structured Output Specification

```python
messages = [
    {"role": "developer", "content": """Extract product info as JSON:
{"name": string, "price": number, "category": string, "in_stock": boolean}"""},
    {"role": "user", "content": "The MacBook Pro 16-inch starts at $2499 and is available in the laptop category."}
]
```

### 5. Constraint Definition

```python
messages = [
    {"role": "developer", "content": """You are a customer service bot for Acme Corp.
Rules:
- Only answer questions about Acme products
- Never discuss competitors
- If unsure, say "Let me connect you with a specialist"
- Keep responses under 3 sentences"""},
    {"role": "user", "content": "How does your product compare to CompetitorX?"}
]
```

## Reusable Prompts

Dashboard-managed prompt templates with variable substitution:

```python
from openai import OpenAI

client = OpenAI()

# SDK v2.29.0: use prompt= in responses.create (not prompt_id in chat.completions)
response = client.responses.create(
    model="gpt-5.6-sol",
    prompt={"id": "prompt_abc123"},
    input=[
        {"role": "user", "content": "Analyze this feedback: Great service!"}
    ]
)

print(response.output[0].content[0].text)
```

## Reasoning Model Tips

For o3, o4-mini, and other reasoning models:

```python
from openai import OpenAI

client = OpenAI()

# DON'T: instruct to think step-by-step (they already do)
# DO: set reasoning_effort for cost/quality tradeoff
response = client.chat.completions.create(
    model="o3",
    messages=[
        {"role": "developer", "content": "Solve this complex math problem."},
        {"role": "user", "content": "Prove that there are infinitely many primes."}
    ],
    reasoning_effort="high"
)
```

## SDK Examples (Python)

### Prompt Template Pattern

```python
from openai import OpenAI

client = OpenAI()

def create_analysis_prompt(text: str, analysis_type: str, output_format: str = "JSON"):
    return [
        {
            "role": "developer",
            "content": f"""Perform {analysis_type} analysis on the provided text.
Output format: {output_format}
Be specific and cite evidence from the text."""
        },
        {"role": "user", "content": text}
    ]

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=create_analysis_prompt(
        "The new update broke everything. Support was unhelpful.",
        "sentiment",
        "JSON with fields: sentiment, confidence, key_phrases"
    ),
    response_format={"type": "json_object"}
)

print(response.choices[0].message.content)
```

## Differences from Other APIs

- **vs Anthropic**: Similar techniques. Anthropic uses `system` parameter (not in messages), explicit XML tag patterns
- **vs Gemini**: Similar techniques. Uses `system_instruction` parameter
- **Reusable prompts**: Unique to OpenAI (dashboard-managed with variables)

## Limitations and Known Issues

- **Prompt length**: Longer prompts consume more tokens and cost more [VERIFIED]
- **Reusable prompts**: Responses API only, not Chat Completions [ASSUMED]
- **Reasoning models**: Chain-of-thought instructions waste tokens [VERIFIED]

## TypeScript Examples

### Generate Image

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const result = await client.images.generate({
  model: "gpt-image-1",
  prompt: "A serene landscape with mountains",
  size: "1024x1024",
  n: 1,
});

console.log(result.data[0].b64_json ? "Got base64 image" : result.data[0].url);
```

## Sources

- OAIAPI-SC-OAI-GPRMPT - Prompt Engineering Guide
- OAIAPI-SC-OAI-GPRMGD - Prompt Guidance / Reusable Prompts

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Changed: Model references from GPT-5.5 to GPT-5.6
- Changed: Reusable Prompts marked DEPRECATED (2026-06-03)
- Changed: Reasoning parameter format to `reasoning.effort` / `reasoning.mode`
- Added: Pro mode reference, IN93 cross-reference
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 15:10]**
- Enriched: Full techniques, reusable prompts, reasoning tips, SDK examples from 2026-03-20
- Updated: Model refs to gpt-5.5
- Added: GPT-5.5 less-prescriptive prompting note

**[2026-05-22 11:40]**
- Stub created
