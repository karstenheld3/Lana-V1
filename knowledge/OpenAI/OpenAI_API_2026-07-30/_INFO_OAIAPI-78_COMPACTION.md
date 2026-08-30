# Compaction

**Doc ID**: OAIAPI-IN78
**Goal**: Document Compaction for context management in long-running agent workflows
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Compaction is a native context management feature for long-running agent workflows, supported by GPT-5.4 (all variants) and GPT-5.5. When a conversation grows beyond the model's effective processing range, compaction condenses the conversation history while preserving key information. It can be triggered explicitly via `POST /v1/responses/{response_id}/compact` or configured to run automatically. This is essential for multi-turn agent loops that would otherwise exceed context limits or degrade in quality as context grows. [VERIFIED] (OAIAPI-SC-OAI-GCMPCT, OAIAPI-SC-OAI-GCHLOG)

## REST API

### Compact a Response

**Endpoint**: `POST /v1/responses/{response_id}/compact`

Compacts the conversation history of an existing response, condensing it into a shorter representation.

**Parameters**:

- **response_id** (string, required) - ID of the response to compact

**Response** (`200 OK`):

```json
{
  "id": "resp_compact_abc123",
  "object": "response",
  "status": "completed"
}
```

## How Compaction Works

1. Model analyzes full conversation history
2. Key information (facts, decisions, tool results) is extracted
3. Redundant context (intermediate reasoning, repeated instructions) is condensed
4. A new, shorter context replaces the original while preserving semantic continuity

## Supported Models

- **GPT-5.5**: Full compaction support
- **GPT-5.4**: Full compaction support
- **GPT-5.4 mini**: Compaction + tool_search + computer_use
- **GPT-5.4 nano**: Compaction only (no tool_search, no computer_use)

## SDK Examples (Python)

### Explicit Compaction

```python
from openai import OpenAI

client = OpenAI()

# After a long multi-turn conversation
response = client.responses.create(
    model="gpt-5.6-sol",
    input="Continue analyzing the codebase...",
    previous_response_id="resp_abc123",
)

# Compact when context grows too large
compacted = client.responses.compact(response.id)
print(f"Compacted response: {compacted.id}")

# Continue with compacted context
next_response = client.responses.create(
    model="gpt-5.6-sol",
    input="What patterns did you identify?",
    previous_response_id=compacted.id,
)
print(next_response.output_text)
```

### Agent Loop with Compaction

```python
from openai import OpenAI

client = OpenAI()

previous_id = None
turn_count = 0

tasks = [
    "Analyze the authentication module for security vulnerabilities.",
    "Now check the database layer for SQL injection risks.",
    "Review the API rate limiting implementation.",
    "Summarize all findings and prioritize fixes.",
]

for task in tasks:
    response = client.responses.create(
        model="gpt-5.6-sol",
        input=task,
        previous_response_id=previous_id,
        reasoning={"effort": "high"},
    )
    print(f"Turn {turn_count}: {response.output_text[:200]}...")

    turn_count += 1
    previous_id = response.id

    # Compact every 3 turns to manage context growth
    if turn_count % 3 == 0:
        compacted = client.responses.compact(response.id)
        previous_id = compacted.id
        print(f"  [Compacted at turn {turn_count}]")
```

## Use Cases

- **Multi-turn agent workflows**: Prevent context overflow in long-running analysis sessions
- **Iterative code review**: Maintain review context across many files without losing earlier findings
- **Research agents**: Compress accumulated research notes while keeping key facts
- **Customer support agents**: Condense conversation history in long support sessions

## Error Responses

- **404 Not Found** - Response ID does not exist
- **400 Bad Request** - Response not eligible for compaction (too short, wrong model)
- **429 Too Many Requests** - Rate limit exceeded

## Gotchas and Quirks

- **Information loss**: Compaction necessarily loses some detail. Critical facts should be reinforced in subsequent prompts [VERIFIED]
- **Not retroactive**: Cannot compact a response that has already been used as `previous_response_id` by another response [ASSUMED]
- **Model-specific**: Only GPT-5.4+ models support compaction. Older models return errors [VERIFIED]
- **Cost**: Compaction itself consumes tokens (both input reading and output generation) [ASSUMED]

## TypeScript Examples

### Realtime Session

```typescript
import OpenAI from "openai";

const client = new OpenAI();

// Create ephemeral session token for client-side use
const session = await client.realtime.sessions.create({
  model: "gpt-4o-mini-realtime-preview",
});
console.log(`Session token created: ${session.id}`);
```

## Sources

- OAIAPI-SC-OAI-GCMPCT - Compaction guide
- OAIAPI-SC-OAI-RESCMP - POST Compact a response API reference
- OAIAPI-SC-OAI-GCHLOG - Changelog (2026-03 - Compaction release)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 10:05]**
- Initial documentation for Compaction (new topic)
