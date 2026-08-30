# WebSocket and WebRTC Connections

**Doc ID**: OAIAPI-IN70
**Goal**: Document WebSocket and WebRTC connection patterns for Realtime API - protocols, authentication, lifecycle
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN39_REALTIME_OVERVIEW.md [OAIAPI-IN39]` for Realtime API context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Realtime API supports three connection interfaces: WebSocket (server-side), WebRTC (client-side/browser), and SIP (telephony). WebSocket uses `wss://api.openai.com/v1/realtime` with API key auth. WebRTC enables browser-based connections using ephemeral client secrets. SIP connects telephony via Calls API. WebSocket sends audio as base64 in JSON events; WebRTC handles audio via media tracks. Also available as WebSocket mode for Responses API as alternative to SSE streaming. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-GRTAPI, OAIAPI-SC-OAI-GWSMOD)

## Key Facts

- **WebSocket URL**: `wss://api.openai.com/v1/realtime?model={model}` [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **WebRTC**: Browser-based with ephemeral client secrets [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **SIP**: Telephony via Calls API [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **Auth (WebSocket)**: API key in Authorization header [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **Auth (WebRTC)**: Client secret from realtime.client_secrets.create [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **Audio (WS)**: Base64-encoded in JSON events [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **Audio (WebRTC)**: Media tracks (automatic encoding) [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)

## Connection Interfaces Comparison

- **WebSocket**
  - Best for: Server-side applications, backend audio processing
  - Auth: API key in header
  - Audio: Base64 in JSON events (manual encode/decode)
  - Security: API key on server (safe)

- **WebRTC**
  - Best for: Browser applications, client-side voice UI
  - Auth: Ephemeral client secret (no API key in browser)
  - Audio: Media tracks (browser handles encoding)
  - Latency: Direct peer connection (lowest latency)

- **SIP**
  - Best for: Telephony, call centers, IVR
  - Auth: Via Calls API (REST)
  - Audio: g711 codec over SIP
  - Security: Dedicated IP ranges

## WebSocket Connection

### Connect

```python
import websockets
import json

url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2"
headers = {
    "Authorization": f"Bearer {api_key}",
    "OpenAI-Beta": "realtime=v1"
}

async with websockets.connect(url, extra_headers=headers) as ws:
    event = json.loads(await ws.recv())
    assert event["type"] == "session.created"
    session_id = event["session"]["id"]
```

### Configure Session

```python
await ws.send(json.dumps({
    "type": "session.update",
    "session": {
        "voice": "coral",
        "instructions": "You are a helpful assistant.",
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "silence_duration_ms": 500
        }
    }
}))
```

### Send Audio

```python
import base64

audio_b64 = base64.b64encode(audio_bytes).decode()
await ws.send(json.dumps({
    "type": "input_audio_buffer.append",
    "audio": audio_b64
}))
```

### Receive Events

```python
async for message in ws:
    event = json.loads(message)
    
    if event["type"] == "response.audio.delta":
        audio = base64.b64decode(event["delta"])
        play_audio(audio)
    elif event["type"] == "response.audio.done":
        print("Audio response complete")
    elif event["type"] == "error":
        print(f"Error: {event['error']}")
```

## WebRTC Connection

### Create Client Secret (SDK v2.29.0 verified)

```python
from openai import OpenAI

client = OpenAI()

response = client.realtime.client_secrets.create(
    session={
        "model": "gpt-realtime-2",
        "voice": "coral",
        "instructions": "You are a helpful assistant."
    }
)

client_secret = response.client_secret.value
```

### Browser-Side Connection (JavaScript)

```javascript
const response = await fetch('/api/realtime/session', { method: 'POST' });
const { client_secret } = await response.json();

const pc = new RTCPeerConnection();

const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
stream.getTracks().forEach(track => pc.addTrack(track, stream));

pc.ontrack = (event) => {
  const audio = new Audio();
  audio.srcObject = event.streams[0];
  audio.play();
};

const offer = await pc.createOffer();
await pc.setLocalDescription(offer);

const sdpResponse = await fetch(
  'https://api.openai.com/v1/realtime/sessions/' + sessionId + '/sdp',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${client_secret}`,
      'Content-Type': 'application/sdp'
    },
    body: offer.sdp
  }
);

const answer = await sdpResponse.text();
await pc.setRemoteDescription({ type: 'answer', sdp: answer });
```

## SDK Examples (Python)

### Full WebSocket Voice Loop

```python
import asyncio
import websockets
import json
import base64
import os

async def realtime_voice_session(
    instructions: str,
    voice: str = "coral",
    model: str = "gpt-realtime-2",
    audio_callback=None,
    tools: list = None
):
    """Production WebSocket voice session"""
    url = f"wss://api.openai.com/v1/realtime?model={model}"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    async with websockets.connect(url, extra_headers=headers) as ws:
        event = json.loads(await ws.recv())
        if event["type"] != "session.created":
            raise RuntimeError(f"Expected session.created, got {event['type']}")
        
        print(f"Session: {event['session']['id']}")
        
        session_config = {
            "voice": voice,
            "instructions": instructions,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "silence_duration_ms": 500
            }
        }
        if tools:
            session_config["tools"] = tools
        
        await ws.send(json.dumps({
            "type": "session.update",
            "session": session_config
        }))
        
        try:
            async for message in ws:
                event = json.loads(message)
                event_type = event.get("type", "")
                
                if event_type == "response.audio.delta":
                    if audio_callback:
                        audio = base64.b64decode(event["delta"])
                        await audio_callback(audio)
                
                elif event_type == "response.text.delta":
                    print(event.get("delta", ""), end="", flush=True)
                
                elif event_type == "response.done":
                    print("\n[Response complete]")
                
                elif event_type == "error":
                    print(f"Error: {event['error']['message']}")
                
                elif event_type == "rate_limits.updated":
                    limits = event.get("rate_limits", [])
                    for limit in limits:
                        if limit.get("remaining", 0) < 10:
                            print(f"Warning: {limit['name']} remaining: {limit['remaining']}")
        
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e.code} {e.reason}")

asyncio.run(realtime_voice_session(
    instructions="You are a concise voice assistant.",
    voice="coral"
))
```

## Error Responses

- **WebSocket 401**: Invalid API key or expired client secret
- **WebSocket 429**: Rate limit exceeded
- **WebSocket 1008**: Policy violation (connection closed)
- **WebRTC ICE failure**: Network connectivity issue

## Differences from Other APIs

- **vs Anthropic**: No WebSocket/WebRTC API
- **vs Gemini Live**: Uses BidiGenerateContent RPC (gRPC-based, not WebSocket)
- **vs Grok**: Different WebSocket protocol for voice

## Limitations and Known Issues

- **WebSocket single connection**: One active session per WebSocket connection [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **WebRTC browser support**: Requires modern browser with WebRTC support [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **EU residency**: Only specific model snapshots support EU data residency [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)

## Gotchas and Quirks

- **Model in URL**: Model specified as query parameter in WebSocket URL, not in session config [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **Beta header**: Include `OpenAI-Beta: realtime=v1` for WebSocket connections [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **Client secret expiry**: Ephemeral tokens have short TTL; create fresh for each session [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **Audio format consistency**: Input and output formats must match session config [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)

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

- OAIAPI-SC-OAI-GRTAPI - Realtime API Guide
- OAIAPI-SC-OAI-GWSMOD - WebSocket Mode Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 18:00]**
- Enriched from 2026-03-20 IN70 (19 -> 290 lines)
- Updated model refs to gpt-realtime-2

**[2026-05-22 11:50]**
- Stub created
