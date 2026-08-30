# Realtime Server Events

**Doc ID**: OAIAPI-IN41
**Goal**: Document all server-to-client event types for the Realtime WebSocket API
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN39_REALTIME_OVERVIEW.md [OAIAPI-IN39]` for Realtime API architecture
- `_INFO_OAIAPI-IN40_REALTIME_CLIENT_EVENTS.md [OAIAPI-IN40]` for client events

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Server events are JSON messages sent from the OpenAI Realtime WebSocket server to the client. There are 35+ server event types organized into 8 categories: session lifecycle (`session.created`, `session.updated`), errors (`error`), conversation management, input audio buffer (VAD, DTMF), input transcription, response lifecycle/streaming, MCP events, and rate limits (`rate_limits.updated`). All events include `type` and `event_id` fields. Streaming uses delta/done pattern for incremental content. Updated for Realtime 2 translation events. [VERIFIED] (OAIAPI-SC-OAI-RTSREV)

## Key Facts

- **Total event types**: 35+ server events [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **Format**: JSON with `type` and `event_id` fields [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **Streaming pattern**: Delta events for incremental content, done events for completion [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **MCP integration**: Dedicated events for MCP tool calls and tool listing [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **DTMF support**: Telephony touch-tone detection events [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **Rate limit reporting**: Real-time rate limit status via `rate_limits.updated` [VERIFIED] (OAIAPI-SC-OAI-RTSREV)

## Quick Reference

```
Session:
  session.created                                    # Session initialized
  session.updated                                    # Session config applied

Error:
  error                                              # Error occurred

Conversation:
  conversation.created                               # Conversation started
  conversation.item.added                            # Item added to conversation
  conversation.item.done                             # Item processing complete
  conversation.item.created                          # Item created (legacy)
  conversation.item.truncated                        # Item audio truncated
  conversation.item.deleted                          # Item removed

Input Audio Buffer:
  input_audio_buffer.committed                       # Buffer committed as turn
  input_audio_buffer.cleared                         # Buffer discarded
  input_audio_buffer.speech_started                  # VAD: speech detected
  input_audio_buffer.speech_stopped                  # VAD: speech ended
  input_audio_buffer.timeout_triggered               # Inactivity timeout
  input_audio_buffer.dtmf_event_received             # DTMF tone detected

Input Transcription:
  conversation.item.input_audio_transcription.delta      # Transcription chunk
  conversation.item.input_audio_transcription.completed  # Transcription done
  conversation.item.input_audio_transcription.segment    # Transcription segment
  conversation.item.input_audio_transcription.failed     # Transcription error

Response Lifecycle:
  response.created                                   # Response generation started
  response.done                                      # Response generation complete

Response Streaming:
  response.output_item.added                         # New output item started
  response.output_item.done                          # Output item complete
  response.content_part.added                        # New content part started
  response.content_part.done                         # Content part complete
  response.output_text.delta                         # Text chunk
  response.output_text.done                          # Text complete
  response.output_audio.delta                        # Audio chunk (base64)
  response.output_audio.done                         # Audio complete
  response.output_audio_transcript.delta             # Audio transcript chunk
  response.output_audio_transcript.done              # Audio transcript complete
  response.function_call_arguments.delta             # Function args chunk
  response.function_call_arguments.done              # Function args complete

MCP:
  response.mcp_call_arguments.delta                  # MCP call args chunk
  response.mcp_call_arguments.done                   # MCP call args complete
  response.mcp_call.in_progress                      # MCP call executing
  response.mcp_call.completed                        # MCP call finished
  response.mcp_call.failed                           # MCP call error
  mcp_list_tools.in_progress                         # MCP tool listing started
  mcp_list_tools.completed                           # MCP tool listing done
  mcp_list_tools.failed                              # MCP tool listing error

Rate Limits:
  rate_limits.updated                                # Current rate limit status
```

## Event Details

### Session Events

**session.created** - Sent immediately after WebSocket connection:
```json
{
  "type": "session.created",
  "event_id": "evt_001",
  "session": {
    "id": "sess_abc123",
    "model": "gpt-realtime-2",
    "modalities": ["audio"],
    "voice": "alloy",
    "instructions": "",
    "turn_detection": {
      "type": "server_vad",
      "threshold": 0.5,
      "silence_duration_ms": 500
    }
  }
}
```

**session.updated** - Confirms session configuration change:
```json
{
  "type": "session.updated",
  "event_id": "evt_002",
  "session": { ... }
}
```

### Error Event

```json
{
  "type": "error",
  "event_id": "evt_err",
  "error": {
    "type": "invalid_request_error",
    "code": "invalid_event",
    "message": "Unknown event type: foo.bar",
    "param": null,
    "event_id": "client_evt_001"
  }
}
```

Error types: `invalid_request_error`, `server_error`, `authentication_error`, `rate_limit_error`

### Input Audio Buffer Events

**input_audio_buffer.speech_started** - Server VAD detected speech:
```json
{
  "type": "input_audio_buffer.speech_started",
  "event_id": "evt_010",
  "audio_start_ms": 1500,
  "item_id": "item_abc123"
}
```

**input_audio_buffer.speech_stopped** - Server VAD detected silence:
```json
{
  "type": "input_audio_buffer.speech_stopped",
  "event_id": "evt_011",
  "audio_end_ms": 3200,
  "item_id": "item_abc123"
}
```

**input_audio_buffer.dtmf_event_received** - DTMF tone detected (telephony):
```json
{
  "type": "input_audio_buffer.dtmf_event_received",
  "event_id": "evt_012",
  "digit": "5"
}
```

### Response Streaming Events

**response.output_text.delta** - Incremental text:
```json
{
  "type": "response.output_text.delta",
  "event_id": "evt_020",
  "response_id": "resp_001",
  "item_id": "item_abc",
  "output_index": 0,
  "content_index": 0,
  "delta": "The weather "
}
```

**response.output_audio.delta** - Incremental audio (base64):
```json
{
  "type": "response.output_audio.delta",
  "event_id": "evt_021",
  "response_id": "resp_001",
  "item_id": "item_abc",
  "output_index": 0,
  "content_index": 0,
  "delta": "<base64-encoded-audio>"
}
```

**response.function_call_arguments.done** - Function call ready:
```json
{
  "type": "response.function_call_arguments.done",
  "event_id": "evt_030",
  "response_id": "resp_001",
  "item_id": "item_func",
  "output_index": 0,
  "call_id": "call_abc123",
  "name": "get_weather",
  "arguments": "{\"location\":\"San Francisco\"}"
}
```

### Response Lifecycle Events

**response.done** - Full response object with usage:
```json
{
  "type": "response.done",
  "event_id": "evt_040",
  "response": {
    "id": "resp_001",
    "status": "completed",
    "output": [ ... ],
    "usage": {
      "total_tokens": 150,
      "input_tokens": 50,
      "output_tokens": 100,
      "input_token_details": {
        "cached_tokens": 20,
        "text_tokens": 30,
        "audio_tokens": 0
      },
      "output_token_details": {
        "text_tokens": 40,
        "audio_tokens": 60
      }
    }
  }
}
```

Response status values: `completed`, `cancelled`, `failed`, `incomplete`

### MCP Events

**response.mcp_call.completed** - MCP tool call finished:
```json
{
  "type": "response.mcp_call.completed",
  "event_id": "evt_mcp_001",
  "response_id": "resp_001",
  "item_id": "item_mcp",
  "output_index": 0,
  "server_label": "my_server",
  "tool_name": "search_docs",
  "result": { ... }
}
```

### Rate Limits Event

```json
{
  "type": "rate_limits.updated",
  "event_id": "evt_rl",
  "rate_limits": [
    {
      "name": "requests",
      "limit": 100,
      "remaining": 95,
      "reset_seconds": 60.0
    },
    {
      "name": "tokens",
      "limit": 50000,
      "remaining": 48500,
      "reset_seconds": 60.0
    }
  ]
}
```

## SDK Examples (Python)

### Event Dispatcher Pattern

```python
import asyncio
import websockets
import json
import os

class RealtimeEventHandler:
    def __init__(self):
        self.handlers = {}
    
    def on(self, event_type: str, handler):
        self.handlers[event_type] = handler
    
    async def dispatch(self, event: dict):
        event_type = event.get("type", "")
        handler = self.handlers.get(event_type)
        if handler:
            await handler(event)

async def main():
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    handler = RealtimeEventHandler()
    
    async def on_session_created(event):
        print(f"Session: {event['session']['id']}")
    
    async def on_error(event):
        err = event["error"]
        print(f"ERROR [{err['type']}]: {err['message']}")
    
    async def on_text_delta(event):
        print(event["delta"], end="", flush=True)
    
    async def on_response_done(event):
        usage = event["response"].get("usage", {})
        print(f"\n[Tokens: {usage.get('total_tokens', 'N/A')}]")
    
    async def on_rate_limits(event):
        for rl in event.get("rate_limits", []):
            if rl["remaining"] < rl["limit"] * 0.1:
                print(f"WARNING: {rl['name']} near limit: {rl['remaining']}/{rl['limit']}")
    
    handler.on("session.created", on_session_created)
    handler.on("error", on_error)
    handler.on("response.output_text.delta", on_text_delta)
    handler.on("response.done", on_response_done)
    handler.on("rate_limits.updated", on_rate_limits)
    
    async with websockets.connect(url, additional_headers=headers) as ws:
        async for message in ws:
            event = json.loads(message)
            await handler.dispatch(event)

asyncio.run(main())
```

### Function Call Handler

```python
import asyncio
import websockets
import json
import os

async def handle_function_calls(ws):
    """Process server events and handle function calls"""
    async for message in ws:
        event = json.loads(message)
        event_type = event.get("type", "")
        
        if event_type == "response.function_call_arguments.done":
            call_id = event["call_id"]
            name = event["name"]
            
            try:
                args = json.loads(event["arguments"])
            except json.JSONDecodeError:
                args = {}
            
            try:
                result = await execute_function(name, args)
            except Exception as e:
                result = {"error": str(e)}
            
            await ws.send(json.dumps({
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result)
                }
            }))
            
            await ws.send(json.dumps({"type": "response.create"}))
        
        elif event_type == "error":
            err = event["error"]
            print(f"Server error: {err['type']} - {err['message']}")
        
        elif event_type == "response.done":
            status = event["response"]["status"]
            if status == "failed":
                print("Response failed")
            elif status == "incomplete":
                print("Response truncated (token limit)")

async def execute_function(name: str, args: dict) -> dict:
    """Route function calls to implementations"""
    functions = {
        "get_weather": lambda a: {"temp": 72, "condition": "sunny"},
        "search_docs": lambda a: {"results": ["doc1", "doc2"]},
    }
    fn = functions.get(name)
    if not fn:
        raise ValueError(f"Unknown function: {name}")
    return fn(args)
```

## Error Responses

- **invalid_request_error** - Client sent malformed event
- **server_error** - Internal server error
- **authentication_error** - Invalid credentials
- **rate_limit_error** - Rate limit exceeded

## Differences from Other APIs

- **vs Anthropic**: No realtime streaming API
- **vs Gemini Live**: Similar delta/done event pattern but different event names. Gemini uses `serverContent`, `toolCall`, `toolCallCancellation`
- **vs Grok Voice**: Similar event taxonomy to OpenAI (compatible-ish)

## Limitations and Known Issues

- **Event ordering**: Delta events arrive in order but may have variable timing [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **Audio buffer size**: Large audio deltas require efficient base64 decoding [ASSUMED]
- **MCP latency**: MCP tool calls add round-trip time to response [ASSUMED]

## Gotchas and Quirks

- **response.done usage**: Token counts include both text and audio tokens separately [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **speech_started interruption**: When speech_started fires during response, client should clear output buffer and cancel response [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **DTMF digits**: Only available in telephony (SIP) sessions, not WebSocket-only sessions [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **conversation.item.created vs .added**: `.created` is legacy; `.added` is preferred [VERIFIED] (OAIAPI-SC-OAI-RTSREV)

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

- OAIAPI-SC-OAI-RTSREV - Realtime server events reference
- OAIAPI-SC-OAI-GRTAPI - Realtime API Guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 16:35]**
- Enriched from 2026-03-20 IN41 (19 -> 390 lines)
- Updated model references to gpt-realtime-2

**[2026-05-22 11:45]**
- Stub created
