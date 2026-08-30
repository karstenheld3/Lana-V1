# Token Counting

**Doc ID**: ANTAPI-IN10
**Goal**: Document POST /v1/messages/count_tokens endpoint for pre-request token estimation
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` for Messages API request schema

## Summary

The Token Counting API (`POST /v1/messages/count_tokens`) estimates the number of input tokens a Messages API request will consume before actually sending it. This enables cost estimation, context window budgeting, and rate limit management. The request body mirrors the Messages API request, and the response returns the total input token count.

## Key Facts

- **Endpoint**: `POST /v1/messages/count_tokens`
- **Auth**: `x-api-key` header
- **SDK Method**: `client.messages.count_tokens()`
- **Returns**: `MessageTokensCount` with `input_tokens` field
- **Status**: GA

## Request

The request body accepts the same parameters as POST /v1/messages (model, messages, system, tools, etc.) to accurately count tokens including all content types.

**Required Parameters:**

- **model** (`string`) - Model ID to count tokens for
- **messages** (`array[MessageParam]`) - Input messages to count

**Optional Parameters (affect token count):**

- **system** (`string | array`) - System prompt tokens
- **tools** (`array[ToolUnion]`) - Tool definition tokens
- **thinking** (`ThinkingConfigParam`) - Thinking configuration

## Response

```json
{
  "input_tokens": 2095
}
```

**Response Fields:**

- **input_tokens** (`integer`) - Total input tokens the request would consume

## Python Examples

### Basic Token Count

```python
import anthropic

client = anthropic.Anthropic()

result = client.messages.count_tokens(
    model="claude-opus-5",
    messages=[{"role": "user", "content": "What is the meaning of life?"}],
)
print(f"Input tokens: {result.input_tokens}")
```

### With System Prompt and Tools

```python
import anthropic

client = anthropic.Anthropic()

result = client.messages.count_tokens(
    model="claude-opus-5",
    system="You are a helpful weather assistant.",
    tools=[
        {
            "name": "get_weather",
            "description": "Get weather for a location.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"],
            },
        }
    ],
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
)
print(f"Input tokens (with tools): {result.input_tokens}")
```

### Cost Estimation Before Sending

```python
import anthropic

client = anthropic.Anthropic()

# Pricing per million tokens (example rates)
INPUT_COST_PER_MTOK = 3.00  # $3 per million input tokens for Sonnet

messages = [{"role": "user", "content": "Write a comprehensive analysis..."}]

# Count tokens first
count = client.messages.count_tokens(
    model="claude-opus-5",
    messages=messages,
)

estimated_cost = (count.input_tokens / 1_000_000) * INPUT_COST_PER_MTOK
print(f"Estimated input cost: ${estimated_cost:.4f}")

# Proceed if within budget
if estimated_cost < 0.10:
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=4096,
        messages=messages,
    )
```

## Use Cases

- **Cost estimation** - Calculate expected cost before sending expensive requests
- **Context window budgeting** - Verify messages fit within model context window
- **Rate limit management** - Check token count against TPM limits before sending
- **Dynamic content trimming** - Iteratively remove content until request fits budget

## Tokenizer Differences

Claude Opus 4.7 introduced a new tokenizer that produces approximately 30% more tokens for the same text compared to earlier models (Opus 4.6 and below). Models using the new tokenizer:

- **claude-opus-5**, **claude-opus-4-8**, **claude-opus-4-7**
- **claude-fable-5**, **claude-mythos-5**, **claude-sonnet-5**

The exact increase depends on content and workload shape. Always pass the correct `model` parameter when counting tokens to get accurate results for your target model.

## Gotchas and Quirks

- Token counts include system prompt, tool definitions, and all message content
- The count is for input tokens only; output tokens depend on model generation
- Tool definitions can consume significant tokens; count them to avoid surprises
- The endpoint uses the same auth and version headers as POST /v1/messages
- Opus 4.7+ and Fable/Mythos/Sonnet 5 produce ~30% more tokens than older models for identical text

## Related Endpoints

- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Messages API (same request structure)
- `_INFO_ANTAPI-14_PRICING.md [ANTAPI-IN14]` - Token pricing per model
- `_INFO_ANTAPI-21_CONTEXT_MANAGEMENT.md [ANTAPI-IN21]` - Context window management

## Sources

- ANTAPI-SC-ANTH-MSGCNT - https://platform.claude.com/docs/en/api/messages/count_tokens - Endpoint reference
- ANTAPI-SC-ANTH-TOKCNT - https://platform.claude.com/docs/en/build-with-claude/token-counting - Token counting guide

## SDK Verification

All 3 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `resources/messages/messages.py`: `count_tokens(model, messages, system?, tools?, thinking?)` returns `MessageTokensCount`
- `MessageTokensCount.input_tokens` field confirmed

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: Tokenizer differences section (Opus 4.7+ new tokenizer, ~30% more tokens)
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:50]**
- Added: SDK verification section (anthropic 0.120.0, all 3 examples valid)

**[2026-03-20 02:38]**
- Initial documentation created
