# Fine-Grained Tool Streaming

**Doc ID**: ANTAPI-IN29
**Goal**: Document incremental tool input streaming and eager_streaming parameter
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-09_STREAMING.md [ANTAPI-IN09]` for SSE streaming events
- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` for tool use architecture

## Summary

Fine-grained tool streaming enables incremental streaming of tool input parameters as they are generated, rather than buffering the full JSON object. When `eager_streaming: true` is set on a tool definition (or the `fine-grained-tool-streaming` beta is active), tool input parameters stream as `input_json_delta` events with partial JSON. Types are inferred on-the-fly rather than waiting for the complete JSON output. This reduces time-to-first-action for tools with large inputs.

## Key Facts

- **Parameter**: `eager_streaming: true` on tool definition
- **Beta Header**: `fine-grained-tool-streaming` (for global activation)
- **Delta Type**: `input_json_delta` with `partial_json` field
- **Default Behavior**: Current models emit one complete key-value at a time
- **Per-Tool Control**: `eager_streaming: false` disables for specific tools even when beta is active
- **Status**: Beta / GA (per-tool)

## Configuration

### Per-Tool Eager Streaming

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    stream=True,
    tools=[
        {
            "name": "generate_report",
            "description": "Generate a detailed report",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "sections": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "content"],
            },
            "eager_streaming": True,  # Enable incremental input streaming
        }
    ],
    messages=[{"role": "user", "content": "Generate a report about AI trends"}],
)
```

### Global Beta Activation

```python
# Via beta header - enables for all tools without eager_streaming: false
response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    stream=True,
    betas=["fine-grained-tool-streaming"],
    tools=[...],
    messages=[...],
)
```

## Streaming Behavior

Without eager streaming, tool inputs arrive as partial JSON strings that can only be parsed after `content_block_stop`. With eager streaming, parameters are streamed incrementally:

```
event: content_block_delta
data: {"type": "content_block_delta", "index": 1, "delta": {"type": "input_json_delta", "partial_json": "{\"title\": \"AI Trends"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 1, "delta": {"type": "input_json_delta", "partial_json": " Report\", \"content\": \"The field of"}}
```

## Processing Incremental Input

```python
import anthropic
import json

client = anthropic.Anthropic()

accumulated_json = ""

with client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    stream=True,
    tools=[
        {
            "name": "process_data",
            "description": "Process data with given parameters",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}},
                "required": ["query"],
            },
            "eager_streaming": True,
        }
    ],
    messages=[{"role": "user", "content": "Search for recent papers"}],
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if event.delta.type == "input_json_delta":
                accumulated_json += event.delta.partial_json
                print(f"Partial: {accumulated_json}")
        elif event.type == "content_block_stop":
            if accumulated_json:
                tool_input = json.loads(accumulated_json)
                print(f"Complete input: {tool_input}")
                accumulated_json = ""
```

## Gotchas and Quirks

- Current models emit one complete key-value pair at a time; future models may offer finer granularity
- There may be delays between `input_json_delta` events while the model generates key-value pairs
- `eager_streaming: false` overrides the beta header for that specific tool
- `eager_streaming: null` (default) uses default behavior based on beta headers
- Always accumulate partial JSON and parse on `content_block_stop` for reliability
- SDKs provide helpers for parsing incremental values

## Related Endpoints

- `_INFO_ANTAPI-09_STREAMING.md [ANTAPI-IN09]` - SSE streaming events and delta types
- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` - Tool use architecture

## Sources

- ANTAPI-SC-ANTH-MSGCRT - https://platform.claude.com/docs/en/api/messages/create - eager_streaming parameter
- ANTAPI-SC-ANTH-STREAM - https://platform.claude.com/docs/en/build-with-claude/streaming - input_json_delta details

## SDK Verification

All 3 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `resources/messages/messages.py`: `stream=True` returns `Stream[RawMessageStreamEvent]` as context manager
- `types/tool_param.py`: `eager_streaming` field confirmed as `Optional[bool]`
- `resources/beta/messages/messages.py`: `betas` param confirmed for beta header activation
- `types/raw_content_block_delta_event.py`: `input_json_delta` delta type confirmed

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 07:00]**
- Added: SDK verification section (anthropic 0.120.0, all 3 examples valid)

**[2026-03-20 04:00]**
- Initial documentation created from Messages API reference and streaming guide
