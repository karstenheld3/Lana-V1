# Realtime Calls API

**Doc ID**: OAIAPI-IN42
**Goal**: Document the Calls API for managing telephony-style Realtime sessions - create, retrieve, list calls
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN39_REALTIME_OVERVIEW.md [OAIAPI-IN39]` for Realtime API architecture

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Calls API manages telephony-style Realtime sessions via REST endpoints. Create a call (`POST /v1/realtime/calls`) to establish a Realtime session with pre-configured model, voice, tools, and instructions. Retrieve call details (`GET /v1/realtime/calls/{call_id}`) to check status and metadata. List calls (`GET /v1/realtime/calls`) with pagination for auditing and monitoring. Calls encapsulate the full lifecycle of a Realtime session including session configuration, SIP integration for telephony, and server-side session control. Each call has a lifecycle: created, in_progress, completed, failed. Calls support dedicated IP ranges for SIP integration and DTMF tone detection. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-RTCALL)

## Key Facts

- **Endpoints**: Create, Retrieve, List calls [VERIFIED] (OAIAPI-SC-OAI-RTCALL)
- **SIP integration**: Connect calls to telephony via SIP [VERIFIED] (OAIAPI-SC-OAI-RTCALL)
- **Lifecycle**: created -> in_progress -> completed/failed [VERIFIED] (OAIAPI-SC-OAI-RTCALL)
- **DTMF**: Touch-tone detection for IVR navigation [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **Server-side control**: Manage sessions without direct WebSocket [VERIFIED] (OAIAPI-SC-OAI-RTCALL)
- **Dedicated IPs**: SIP integration uses dedicated IP ranges [VERIFIED] (OAIAPI-SC-OAI-GVOICE)

## Quick Reference

```
POST /v1/realtime/calls                # Create a call
GET  /v1/realtime/calls/{call_id}      # Retrieve a call
GET  /v1/realtime/calls                # List calls

Headers:
  Authorization: Bearer $OPENAI_API_KEY
  Content-Type: application/json
```

## Call Object

```json
{
  "id": "call_abc123",
  "object": "realtime.call",
  "created_at": 1699061776,
  "status": "in_progress",
  "model": "gpt-realtime-2",
  "voice": "coral",
  "instructions": "You are a customer service agent.",
  "metadata": {},
  "sip": {
    "uri": "sip:call_abc123@sip.openai.com",
    "headers": {}
  }
}
```

### Status Values

- **created**: Call created, awaiting connection
- **in_progress**: Active call session
- **completed**: Call ended normally
- **failed**: Call failed (error)

## Operations

### Create a Call

```
POST /v1/realtime/calls
```

**Request:**
```json
{
  "model": "gpt-realtime-2",
  "voice": "coral",
  "instructions": "You are a helpful customer service agent for Acme Corp. Be polite and concise.",
  "modalities": ["audio"],
  "input_audio_format": "g711_ulaw",
  "output_audio_format": "g711_ulaw",
  "turn_detection": {
    "type": "server_vad",
    "threshold": 0.5,
    "silence_duration_ms": 600
  },
  "tools": [
    {
      "type": "function",
      "name": "transfer_to_agent",
      "description": "Transfer the call to a human agent",
      "parameters": {
        "type": "object",
        "properties": {
          "department": {"type": "string", "enum": ["sales", "support", "billing"]}
        },
        "required": ["department"]
      }
    }
  ],
  "metadata": {
    "campaign": "spring_2026",
    "queue": "inbound"
  }
}
```

**Parameters:**
- **model** (required): Realtime model identifier (gpt-realtime-2, gpt-realtime-1.5, gpt-realtime-mini)
- **voice** (optional): Voice for audio output
- **instructions** (optional): System prompt for the call
- **modalities** (optional): ["audio"] or ["text", "audio"]
- **input_audio_format** (optional): pcm16, g711_ulaw, g711_alaw
- **output_audio_format** (optional): pcm16, g711_ulaw, g711_alaw
- **turn_detection** (optional): VAD configuration
- **tools** (optional): Function definitions
- **metadata** (optional): Up to 16 key-value pairs

### Retrieve a Call

```
GET /v1/realtime/calls/{call_id}
```

Returns the full call object with current status.

### List Calls

```
GET /v1/realtime/calls
```

**Query Parameters:**
- **limit** (optional): 1-100, default 20
- **order** (optional): `asc` or `desc` by created_at
- **after** (optional): Cursor for forward pagination
- **before** (optional): Cursor for backward pagination

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "call_abc123",
      "object": "realtime.call",
      "created_at": 1699061776,
      "status": "completed",
      "model": "gpt-realtime-2"
    }
  ],
  "first_id": "call_abc123",
  "last_id": "call_xyz789",
  "has_more": true
}
```

## SIP Integration

Calls return a SIP URI for telephony integration:

```
sip:call_abc123@sip.openai.com
```

### Connecting via SIP

1. Create a call via the API
2. Extract the SIP URI from the response
3. Route your SIP trunk to the provided URI
4. Audio flows bidirectionally over SIP

### Dedicated IP Ranges

OpenAI provides dedicated IP ranges for SIP traffic. Configure your firewall/SBC to allow traffic from these ranges. Contact OpenAI for current IP allocations.

### Audio Codecs for Telephony

- **g711_ulaw**: Standard for North American telephony (PSTN)
- **g711_alaw**: Standard for European/international telephony

## SDK Examples (Python)

### Create a Call

```python
from openai import OpenAI

client = OpenAI()

call = client.realtime.calls.create(
    model="gpt-realtime-2",
    voice="coral",
    instructions="You are a customer service agent. Help callers with their orders.",
    modalities=["audio"],
    input_audio_format="g711_ulaw",
    output_audio_format="g711_ulaw",
    turn_detection={
        "type": "server_vad",
        "threshold": 0.5,
        "silence_duration_ms": 600
    },
    tools=[
        {
            "type": "function",
            "name": "lookup_order",
            "description": "Look up a customer order by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            }
        }
    ],
    metadata={"queue": "support"}
)

print(f"Call ID: {call.id}")
print(f"Status: {call.status}")
print(f"SIP URI: {call.sip.uri}")
```

### Create a Call (SDK v2.45.0 - SDP variant)

```python
from openai import OpenAI

client = OpenAI()

call = client.realtime.calls.create(
    sdp="v=0\r\no=- 0 0 IN IP4 0.0.0.0\r\n...",  # SDP offer from SIP provider
    session={
        "model": "gpt-realtime-2",
        "voice": "coral",
        "instructions": "You are a customer service agent.",
        "modalities": ["audio"],
        "input_audio_format": "g711_ulaw",
        "output_audio_format": "g711_ulaw",
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "silence_duration_ms": 600
        },
        "tools": [
            {
                "type": "function",
                "name": "lookup_order",
                "description": "Look up a customer order by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"}
                    },
                    "required": ["order_id"]
                }
            }
        ]
    }
)

print(f"Call ID: {call.id}")
print(f"Status: {call.status}")
```

### Call Analytics

```python
from openai import OpenAI

client = OpenAI()

def get_call_stats():
    """Get call statistics for monitoring"""
    calls = []
    after = None
    
    while True:
        response = client.realtime.calls.list(limit=100, after=after)
        calls.extend(response.data)
        if not response.has_more:
            break
        after = response.last_id
    
    stats = {
        "total": len(calls),
        "in_progress": sum(1 for c in calls if c.status == "in_progress"),
        "completed": sum(1 for c in calls if c.status == "completed"),
        "failed": sum(1 for c in calls if c.status == "failed"),
    }
    
    return stats

try:
    stats = get_call_stats()
    print(f"Total: {stats['total']}")
    print(f"Active: {stats['in_progress']}")
    print(f"Completed: {stats['completed']}")
    print(f"Failed: {stats['failed']}")
except Exception as e:
    print(f"Error: {e}")
```

## Error Responses

- **400 Bad Request** - Invalid model, voice, or configuration
- **401 Unauthorized** - Invalid API key
- **404 Not Found** - Call not found
- **429 Too Many Requests** - Concurrent call limit exceeded

## Rate Limiting

- **Concurrent calls**: Limited by organization tier
- **Call creation rate**: Standard API rate limits
- **Audio duration**: Billed per minute

## Differences from Other APIs

- **vs Anthropic**: No telephony or call management API
- **vs Gemini**: No SIP/telephony integration
- **vs Grok**: Grok Voice Agent has similar call concept but different API surface
- **vs Twilio**: OpenAI provides AI-native calls; Twilio provides telephony infrastructure. Often used together (Twilio SIP -> OpenAI Calls)

## Limitations and Known Issues

- **No call recording API**: Recording must be handled externally [ASSUMED]
- **No call transfer**: Must implement via function calling and external routing [ASSUMED]
- **SIP only**: No direct PSTN connection; requires SIP provider as intermediary [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **Concurrent limits**: Organization tier limits on active calls [VERIFIED] (OAIAPI-SC-OAI-RTCALL)

## Gotchas and Quirks

- **SIP URI is per-call**: Each call gets a unique SIP URI; do not reuse [VERIFIED] (OAIAPI-SC-OAI-RTCALL)
- **g711 for telephony**: Use g711_ulaw/alaw for SIP; pcm16 adds unnecessary overhead [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **DTMF via events**: Touch-tone input arrives as `input_audio_buffer.dtmf_event_received` server events [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **Call metadata**: Use metadata for tracking campaigns, queues, customer IDs [VERIFIED] (OAIAPI-SC-OAI-RTCALL)

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

- OAIAPI-SC-OAI-RTCALL - Calls API (Create, Retrieve, List)
- OAIAPI-SC-OAI-GVOICE - Voice Agents Guide
- OAIAPI-SC-OAI-GRTAPI - Realtime API Guide
- OAIAPI-SC-OAI-RTSREV - Server events reference (DTMF)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 16:40]**
- Enriched from 2026-03-20 IN42 (19 -> 310 lines)
- Updated model references to gpt-realtime-2

**[2026-05-22 11:45]**
- Stub created
