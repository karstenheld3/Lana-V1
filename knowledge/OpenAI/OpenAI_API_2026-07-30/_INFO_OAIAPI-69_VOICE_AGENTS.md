# Voice Agents Guide

**Doc ID**: OAIAPI-IN69
**Goal**: Document building voice agents with OpenAI - architecture, Agents SDK, telephony, production patterns
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

Voice agents are AI-powered conversational systems that communicate via speech. Three paths: Agents SDK (fastest for common patterns), Realtime API (full control over audio streaming), and Calls API (telephony/SIP). Models: `gpt-realtime-2` with configurable reasoning for speech-to-speech agents. Supports translation and Whisper integration. SIP integration for telephony with dedicated IP ranges for enterprise. Voices: alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse. Audio formats: pcm16, g711_ulaw, g711_alaw. [VERIFIED] (OAIAPI-SC-OAI-GVOICE)

## Key Facts

- **Three paths**: Agents SDK, Realtime API, Calls API [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **Models**: gpt-realtime-2 [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **Voices**: alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **Audio formats**: pcm16, g711_ulaw, g711_alaw [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **VAD**: Server-side voice activity detection with configurable thresholds [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **Telephony**: SIP integration via Calls API [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **DTMF**: Touch-tone detection for IVR menus [VERIFIED] (OAIAPI-SC-OAI-RTSREV)

## Use Cases

- **Call center automation**: AI agents handling inbound/outbound calls
- **IVR systems**: Voice menus with natural language understanding
- **Virtual receptionist**: Answer calls, route, take messages
- **Voice assistants**: In-app voice interaction
- **Language tutoring**: Conversational language practice
- **Translation**: Real-time speech translation via Whisper integration

## Architecture Options

### Option 1: Agents SDK (Recommended for Common Patterns)

```
User Audio -> Agents SDK VoiceAgent -> Tools/Handoffs -> Audio Response
```

Fastest path. Handles audio encoding, VAD, turn management automatically.

### Option 2: Realtime API (Full Control)

```
User Audio -> WebSocket -> Realtime API -> Audio Stream
                             |
                        Tool Calls / Function Results
```

Full control over audio streaming, custom VAD, event handling.

### Option 3: Calls API (Telephony)

```
Phone Call -> SIP Trunk -> Calls API -> AI Agent -> Audio Response
                             |
                        Tool Calls / DTMF
```

SIP-connected telephony with REST-based call management.

## SDK Examples (Python)

### Voice Agent with Agents SDK

```python
from agents import Agent, Runner, function_tool
from agents.voice import VoiceAgent

@function_tool
def check_order_status(order_id: str) -> str:
    """Check the status of a customer order"""
    return f"Order {order_id}: Shipped, arriving tomorrow"

@function_tool
def transfer_to_human(department: str) -> str:
    """Transfer the call to a human agent"""
    return f"Transferring to {department}..."

voice_agent = VoiceAgent(
    name="Customer Service",
    instructions="""You are a friendly customer service agent for Acme Corp.
    Help customers check orders, answer questions, and transfer to humans when needed.
    Be concise - voice conversations should be brief and clear.""",
    model="gpt-realtime-2",
    voice="coral",
    tools=[check_order_status, transfer_to_human]
)

result = Runner.run_sync(voice_agent, audio_stream=audio_input)
```

### Realtime API Voice Agent

```python
import asyncio
import websockets
import json
import base64

async def voice_agent():
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    async with websockets.connect(url, extra_headers=headers) as ws:
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "voice": "coral",
                "instructions": "You are a helpful voice assistant. Be concise.",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "silence_duration_ms": 500
                },
                "tools": [
                    {
                        "type": "function",
                        "name": "get_weather",
                        "description": "Get weather for a location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string"}
                            },
                            "required": ["location"]
                        }
                    }
                ]
            }
        }))
        
        async for message in ws:
            event = json.loads(message)
            
            if event["type"] == "response.audio.delta":
                audio_data = base64.b64decode(event["delta"])
                play_audio(audio_data)
            
            elif event["type"] == "response.function_call_arguments.done":
                args = json.loads(event["arguments"])
                result = handle_tool(event["name"], args)
                
                await ws.send(json.dumps({
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": event["call_id"],
                        "output": json.dumps(result)
                    }
                }))
                
                await ws.send(json.dumps({
                    "type": "response.create"
                }))
            
            elif event["type"] == "error":
                print(f"Error: {event['error']['message']}")

asyncio.run(voice_agent())
```

### Telephony Voice Agent via Calls API (SDK v2.29.0 verified)

```python
from openai import OpenAI

client = OpenAI()

def create_voice_call(sdp_offer: str, instructions: str, tools: list = None):
    """Create a telephony voice agent call via SDK"""
    call = client.realtime.calls.create(
        sdp=sdp_offer,
        session={
            "model": "gpt-realtime-2",
            "voice": "coral",
            "instructions": instructions,
            "modalities": ["audio"],
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "silence_duration_ms": 600
            },
            "tools": tools or []
        }
    )
    print(f"Call ID: {call.id}")
    return call

call = create_voice_call(
    sdp_offer="v=0\r\no=- 0 0 IN IP4 0.0.0.0\r\n...",
    instructions="You are the automated receptionist for Acme Corp.",
    tools=[
        {
            "type": "function",
            "name": "transfer_call",
            "description": "Transfer to a department",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {"type": "string", "enum": ["sales", "support", "billing"]}
                },
                "required": ["department"]
            }
        }
    ]
)
```

## Production Best Practices

- **VAD tuning**: Adjust silence_duration_ms (shorter for fast interactions, longer for thoughtful queries)
- **Latency**: Minimize tool execution time; users notice >2s pauses
- **Interruption**: Handle barge-in gracefully (user speaking over agent)
- **Error recovery**: If speech is misheard, prompt for clarification
- **g711 for telephony**: Use g711_ulaw/alaw for SIP; pcm16 adds overhead
- **Monitoring**: Track call duration, tool usage, and error rates

## Error Responses

- **WebSocket errors**: Connection timeout, authentication failure
- **Tool execution timeout**: Function call taking too long
- **Audio format mismatch**: Sending wrong audio format

## Differences from Other APIs

- **vs Anthropic**: No voice/audio API
- **vs Gemini Live**: Google has Gemini Live for real-time audio; different API surface
- **vs Twilio**: Twilio provides telephony infrastructure; OpenAI provides AI. Often used together

## Limitations and Known Issues

- **Long conversation degradation**: Quality may degrade in very long conversations [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **Edge case silence**: Model may struggle with extended silence periods [VERIFIED] (OAIAPI-SC-OAI-GVOICE)
- **Tool-driven flows**: Precision in tool use during voice conversations still improving [VERIFIED] (OAIAPI-SC-OAI-GVOICE)

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

- OAIAPI-SC-OAI-GVOICE - Voice Agents Guide
- OAIAPI-SC-OAI-GRTAPI - Realtime API Guide
- OAIAPI-SC-OAI-RTSREV - Server Events Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 18:00]**
- Enriched from 2026-03-20 IN69 (19 -> 280 lines)
- Updated model refs to gpt-realtime-2, added translation/Whisper info

**[2026-05-22 11:50]**
- Stub created
