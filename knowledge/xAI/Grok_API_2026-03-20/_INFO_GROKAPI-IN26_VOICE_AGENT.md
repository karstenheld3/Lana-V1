# INFO: Voice Agent API

**Doc ID**: GROKAPI-IN26
**Goal**: Real-time voice conversations via WebSocket, authentication, tools, events, pricing
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Voice Agent API enables real-time bidirectional voice conversations with Grok over WebSocket (`wss://api.x.ai/v1/realtime`). Billed at a flat $0.05/minute ($3.00/hour). Supports up to 100 concurrent sessions per team with a max session duration of 30 minutes. The API supports tool integration including function calling, web search, X search, collections search, and MCP tools - tool invocations are billed separately from the per-minute voice cost. This is comparable to OpenAI's Realtime API but uses a different event model. [VERIFIED] (GROKAPI-SC-XAI-VOICEAGENT | https://docs.x.ai/developers/model-capabilities/audio/voice-agent)

## Key Facts

- [VERIFIED] Protocol: WebSocket at `wss://api.x.ai/v1/realtime` (GROKAPI-SC-XAI-VOICEAGENT)
- [VERIFIED] Pricing: $0.05/minute ($3.00/hour) flat rate (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Max concurrent sessions: 100 per team (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Max session duration: 30 minutes (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Capabilities: Function calling, web search, X search, collections, MCP (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Tool invocations billed separately from per-minute cost (GROKAPI-SC-XAI-MODELS)

## Quick Reference

- **WebSocket URL**: `wss://api.x.ai/v1/realtime`
- **Auth**: Bearer token in WebSocket handshake
- **Pricing**: $0.05/min + tool invocation costs
- **Max sessions**: 100 concurrent per team
- **Max duration**: 30 minutes per session
- **Tools**: web_search, x_search, collections_search, MCP, function calling

## Examples

### Basic Voice Agent Connection (Python)

```python
import os
import asyncio
import websockets
import json

async def voice_session():
    api_key = os.getenv("XAI_API_KEY")
    url = "wss://api.x.ai/v1/realtime"

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    async with websockets.connect(url, extra_headers=headers) as ws:
        # Send session configuration
        config = {
            "type": "session.update",
            "session": {
                "model": "grok-4.20-beta-latest-non-reasoning",
                "tools": [
                    {"type": "web_search"},
                ],
            },
        }
        await ws.send(json.dumps(config))

        # Handle events
        async for message in ws:
            event = json.loads(message)
            print(f"Event: {event['type']}")

            if event["type"] == "response.audio.delta":
                # Process audio chunk
                pass
            elif event["type"] == "response.done":
                break

asyncio.run(voice_session())
```

## Differences from Other APIs

### vs OpenAI Realtime API

- **Similar concept**: Both use WebSocket for real-time voice
- **Different event model**: Different event types and structures
- **Pricing**: xAI $0.05/min flat vs OpenAI per-token audio pricing
- **Tools**: xAI supports server-side tools (web_search, x_search) in voice sessions
- **X Search**: UNIQUE - can search X during voice conversations

### vs Anthropic

- **UNIQUE**: Anthropic has no real-time voice API

### vs Gemini

- **Similar concept**: Gemini has Live API for real-time audio
- **Different protocol**: Different WebSocket event models

## Limitations and Known Issues

- [VERIFIED] Max 30 minutes per session (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Max 100 concurrent sessions per team (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Rate limit increases for Voice API require email request (GROKAPI-SC-XAI-RATELIMITS)

## Sources

- GROKAPI-SC-XAI-VOICEAGENT | https://docs.x.ai/developers/model-capabilities/audio/voice-agent | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 04:30]**
- Initial document created with Voice Agent API reference and pricing
