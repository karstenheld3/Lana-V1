# Using GPT-5.5 [DEPRECATED]

**Doc ID**: OAIAPI-IN75
**Goal**: Document GPT-5.5 capabilities, prompting best practices, caching, and migration from earlier models
**Version scope**: API v1, Documentation date 2026-07-30
**Status**: DEPRECATED - GPT-5.5 deprecated 2026-06-11 (removal 2026-12-11). See IN93 for GPT-5.6 guide.

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN03_MODELS.md [OAIAPI-IN03]` for model overview

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

**DEPRECATED (2026-06-11)**: GPT-5.5 is deprecated with removal scheduled 2026-12-11. Migrate to GPT-5.6 (Sol/Terra/Luna). See IN93 for the current flagship model guide.

GPT-5.5 was OpenAI's frontier model released 2026-04-24, designed for the most complex professional work. It features a 1,050,000 token context window, 128K max output, and supports reasoning effort levels (none, low, medium [default], high, xhigh). Key differences from GPT-5.4: reasoning defaults to medium (not high), only extended prompt caching is supported (no in-memory), and image_detail auto behavior changed. GPT-5.5 supports all built-in tools including hosted_shell, apply_patch, Skills, computer_use, MCP, and tool_search. GPT-5.5-pro is a companion model for harder problems that benefit from more compute, available only via Responses API, replacing o3-deep-research and o4-mini-deep-research. [VERIFIED] (OAIAPI-SC-OAI-GLATEST, OAIAPI-SC-OAI-MGP55)

## Key Changes from GPT-5.4

- **Reasoning effort**: Defaults to `medium` (GPT-5.4 default varies). Use `high` or `xhigh` when intelligence matters more than speed
- **Prompt caching**: Extended prompt caching ONLY. In-memory prompt caching NOT supported. Place static content first, dynamic parts last
- **image_detail**: When unset or `auto`, model uses original behavior (may differ from GPT-5.4)
- **Prompting style**: GPT-5.5 is more capable at self-directed reasoning. Reduce step-by-step guidance; let the model choose its path
- **Structured outputs**: Remove output schema definitions from prompts where possible; use Structured Outputs API instead
- **Long context pricing**: >272K input tokens = 2x input, 1.5x output for full session (standard, batch, flex)

## Prompting Best Practices

### Less is More

GPT-5.5 performs best with less prescriptive prompts:

```python
from openai import OpenAI

client = OpenAI()

# BAD: Over-specified process guidance
bad_prompt = """Step 1: Read the code. Step 2: Identify bugs. Step 3: Suggest fixes.
Step 4: Format output as numbered list. Step 5: Add severity ratings."""

# GOOD: Let GPT-5.5 choose its approach
good_prompt = "Review this code for bugs. Prioritize by severity."

response = client.responses.create(
    model="gpt-5.6-sol",
    input=good_prompt + "\n\n```python\ndef calc(x):\n    return x/0\n```",
    reasoning={"effort": "high"},
)
print(response.output_text)
```

### Reasoning Effort Selection

```python
from openai import OpenAI

client = OpenAI()

# none: Skip reasoning entirely (fastest, cheapest)
response_fast = client.responses.create(
    model="gpt-5.6-sol",
    input="What is 2+2?",
    reasoning={"effort": "none"},
)

# medium (default): Good balance for most tasks
response_balanced = client.responses.create(
    model="gpt-5.6-sol",
    input="Explain the CAP theorem and its implications for distributed databases.",
)

# high: Complex analysis requiring deep thought
response_deep = client.responses.create(
    model="gpt-5.6-sol",
    input="Design a consensus algorithm that handles Byzantine faults in a network of 100 nodes.",
    reasoning={"effort": "high"},
)

# xhigh: Hardest problems, maximum compute
response_max = client.responses.create(
    model="gpt-5.6-sol",
    input="Prove or disprove: P != NP for the restricted case of...",
    reasoning={"effort": "xhigh"},
)
```

### Chat Completions with Reasoning

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {"role": "system", "content": "You are an expert data engineer."},
        {"role": "user", "content": "Design an ETL pipeline for processing 10TB of daily log data with sub-minute latency requirements."}
    ],
    reasoning_effort="high",
    max_completion_tokens=8192,
)
print(response.choices[0].message.content)
```

## Extended Prompt Caching

GPT-5.5 ONLY supports extended prompt caching (NOT in-memory caching like GPT-5.4).

### How it Works

- Cache is maintained across requests with matching prompt prefixes
- Static content at the START of prompts gets cached
- Dynamic content should go at the END
- Cached tokens cost 10x less ($0.50 vs $5.00 per MTok)

### Optimizing for Cache Hits

```python
from openai import OpenAI

client = OpenAI()

# Static system prompt (cached across requests)
system_prompt = """You are a senior code reviewer. Follow these guidelines:
1. Check for security vulnerabilities (SQL injection, XSS, CSRF)
2. Verify error handling patterns
3. Assess performance implications
4. Flag deprecated API usage
5. Suggest idiomatic improvements"""

# Dynamic user input (changes per request)
user_code = "def login(user, pw): return db.query(f'SELECT * FROM users WHERE name={user}')"

response = client.responses.create(
    model="gpt-5.6-sol",
    instructions=system_prompt,  # Cached (static, placed first)
    input=f"Review this code:\n```python\n{user_code}\n```",  # Dynamic (placed last)
)
print(response.output_text)
# Check cache usage
print(f"Cached tokens: {response.usage.prompt_tokens_details.cached_tokens}")
```

### Monitoring Cache Performance

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[
        {"role": "system", "content": "Large static system prompt here..."},
        {"role": "user", "content": "Dynamic query"}
    ],
)

usage = response.usage
print(f"Total input tokens: {usage.prompt_tokens}")
print(f"Cached tokens: {usage.prompt_tokens_details.cached_tokens}")
cache_rate = usage.prompt_tokens_details.cached_tokens / usage.prompt_tokens * 100
print(f"Cache hit rate: {cache_rate:.1f}%")
```

## GPT-5.5 Pro

GPT-5.5-pro provides extended compute for harder problems. Available via Responses API only.

```python
from openai import OpenAI

client = OpenAI()

# Use for problems needing deep analysis
response = client.responses.create(
    model="gpt-5.5-pro",
    input="Analyze the complete codebase architecture and suggest a migration plan from monolith to microservices.",
    reasoning={"effort": "xhigh"},
)
print(response.output_text)
```

**Note**: gpt-5.5-pro replaces o3-deep-research and o4-mini-deep-research, which are being deprecated.

## Built-in Tools

GPT-5.5 supports all Responses API built-in tools:

### Hosted Shell (Code Execution)

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Write and run a Python script that generates the first 20 Fibonacci numbers.",
    tools=[{"type": "code_interpreter"}],
)
print(response.output_text)
```

### Apply Patch (Code Editing)

GPT-5.5 can generate and apply patches to code:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Fix the SQL injection vulnerability in the login function and apply the patch.",
    tools=[{"type": "code_interpreter"}],
)
print(response.output_text)
```

### Web Search with Extended Reasoning

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="What are the latest developments in quantum error correction?",
    tools=[{
        "type": "web_search",
        "return_token_budget": 20000,  # Opt in to longer reasoning runs
    }],
    reasoning={"effort": "high"},
)
print(response.output_text)
```

## Migration from GPT-5.4

1. **Update model ID**: `gpt-5.4` -> `gpt-5.5`
2. **Check reasoning effort**: Default changed to `medium`. Add explicit `"high"` if needed
3. **Update caching strategy**: Switch to extended prompt caching patterns
4. **Simplify prompts**: Remove over-specified process guidance
5. **Test image_detail**: If using `auto`, verify behavior matches expectations
6. **Check pricing**: $5/$30 vs $2.50/$15 (2x cost increase for input, 2x for output)
7. **Run evals**: Model behavior differs between snapshots

## Error Responses

- **429 Too Many Requests** - Rate limit (check tier limits, GPT-5.5 not available on Free tier)
- **400 Bad Request** - Invalid reasoning effort value (must be none/low/medium/high/xhigh)

## Gotchas and Quirks

- **No in-memory caching**: Unlike GPT-5.4, ONLY extended prompt caching works. First request to a new prompt prefix will NOT be cached [VERIFIED]
- **Reasoning default medium**: If you relied on higher default reasoning in GPT-5.4, explicitly set `effort: "high"` [VERIFIED]
- **Long context surcharge**: Once you exceed 272K input tokens, the ENTIRE session gets 2x/1.5x pricing, not just the overflow [VERIFIED]
- **Free tier**: GPT-5.5 is NOT available on the Free tier [VERIFIED] (OAIAPI-SC-OAI-MGP55)
- **No fine-tuning**: GPT-5.5 does NOT support fine-tuning [VERIFIED] (OAIAPI-SC-OAI-GFNTN)
- **Regional pricing**: 10% uplift for data residency endpoints [VERIFIED]
- **Predicted Outputs**: Supports predicted outputs for latency optimization in code editing workflows [VERIFIED] (OAIAPI-SC-OAI-GPROUT)

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

- OAIAPI-SC-OAI-GLATEST - Using GPT-5.5 guide
- OAIAPI-SC-OAI-MGP55 - GPT-5.5 model page
- OAIAPI-SC-OAI-MGP55P - GPT-5.5 Pro model page
- OAIAPI-SC-OAI-GPCACH - Prompt caching guide
- OAIAPI-SC-OAI-GCHLOG - Changelog (2026-04)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Changed: Marked DEPRECATED (GPT-5.5 deprecated 2026-06-11, removal 2026-12-11)
- Added: Migration guidance to IN93 (GPT-5.6)
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 09:50]**
- Initial documentation for GPT-5.5 (new topic, not in 2026-03-20 baseline)
