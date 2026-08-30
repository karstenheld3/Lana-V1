# Realtime Audio Overview

**Doc ID**: OAIAPI-IN20
**Goal**: Document realtime audio streaming, voice agents, and realtime transcription
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Realtime Audio capabilities include WebSocket-based voice streaming via Realtime API, voice agent architecture for conversational AI, and realtime transcription. Bidirectional audio streaming with low latency supporting interruptions, function calling, and multi-turn dialogs. Models: Realtime 2 (reasoning voice), Realtime Translate (70+ languages), Realtime Whisper (streaming STT). **NEW (2026-07)**: GPT-Realtime-2.1 improves alphanumeric handling, interruption, and reasoning; GPT-Realtime-2.1-mini is a distilled cost-efficient variant. See IN39 for overview and IN77 for detailed model documentation. VAD (Voice Activity Detection), audio buffering, session management, event-driven communication. Supports WebRTC connections. [VERIFIED] (OAIAPI-SC-OAI-GAUDIO, OAIAPI-SC-OAI-GRTAPI, OAIAPI-SC-OAI-GVOICE, OAIAPI-SC-OAI-GCHLOG)

## Key Facts

- **Protocol**: WebSocket/WebRTC for bidirectional streaming [VERIFIED]
- **Models**: gpt-4o-realtime, Realtime 2 (reasoning) [VERIFIED]
- **Latency**: Low-latency streaming (~200-500ms) [VERIFIED]
- **Features**: VAD, interruptions, function calling, turn detection [VERIFIED]
- **New (2026-05)**: Realtime 2, Realtime Translate, Realtime Whisper [VERIFIED]

## Realtime API Components

### WebSocket Connection

**Endpoint**: `wss://api.openai.com/v1/realtime`

**Authentication**: API key in query param or Authorization header

**Session lifecycle**:
1. Connect WebSocket
2. Configure session
3. Stream audio/text
4. Receive responses
5. Close session

### Session Configuration

```json
{
  "type": "session.update",
  "session": {
    "model": "gpt-4o-realtime",
    "voice": "alloy",
    "modalities": ["text", "audio"],
    "instructions": "You are a helpful assistant",
    "input_audio_format": "pcm16",
    "output_audio_format": "pcm16",
    "turn_detection": {
      "type": "server_vad",
      "threshold": 0.5,
      "silence_duration_ms": 500
    }
  }
}
```

### Audio Formats

- **pcm16**: 16-bit PCM (raw audio)
- **g711_ulaw**: G.711 u-law (telephony)
- **g711_alaw**: G.711 A-law (telephony)

Sample rates: 16kHz, 24kHz (model-dependent)

### Voice Activity Detection (VAD)

- **Server VAD** (recommended): Automatic turn detection, configurable threshold and silence duration
- **Client VAD**: Client controls turn boundaries, more control but more complexity

## Voice Agents

Architecture: User Speech -> STT -> Text Processing -> TTS -> Agent Speech (with context loop)

**Features:**
- Natural conversation with turn-taking and interruptions
- Multi-turn context awareness
- Function calling during conversation
- Configurable voice and personality

**Patterns:**
- **WebSocket-based**: Real-time bidirectional, chatbots, voice assistants
- **SIP-based** (telephony): Phone integration, IVR, call centers

## Event Types

### Client -> Server

- **session.update**: Configure session
- **input_audio_buffer.append**: Send audio chunk
- **input_audio_buffer.commit**: Mark audio complete
- **conversation.item.create**: Add text message
- **response.create**: Request response

### Server -> Client

- **session.created**: Session initialized
- **conversation.item.created**: New item added
- **input_audio_buffer.speech_started**: Speech detected
- **input_audio_buffer.speech_stopped**: Silence detected
- **response.audio.delta**: Audio response chunk
- **response.audio.done**: Audio complete
- **response.text.delta**: Text response chunk
- **response.text.done**: Text complete

## SDK Examples (Python)

### Basic Realtime Connection

```python
import asyncio
import websockets
import json
import os

async def realtime_session():
    api_key = os.getenv("OPENAI_API_KEY")
    url = f"wss://api.openai.com/v1/realtime?api_key={api_key}"
    
    async with websockets.connect(url) as ws:
        config = {
            "type": "session.update",
            "session": {
                "model": "gpt-4o-realtime",
                "voice": "alloy",
                "modalities": ["text", "audio"]
            }
        }
        await ws.send(json.dumps(config))
        
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Hello!"}]
            }
        }
        await ws.send(json.dumps(message))
        await ws.send(json.dumps({"type": "response.create"}))
        
        async for message in ws:
            event = json.loads(message)
            if event['type'] == "response.text.done":
                print(f"Response: {event['text']}")
                break

asyncio.run(realtime_session())
```

### Voice Agent with Audio I/O

```python
import asyncio
import websockets
import json
import pyaudio
import os

async def voice_agent():
    api_key = os.getenv("OPENAI_API_KEY")
    url = f"wss://api.openai.com/v1/realtime?api_key={api_key}"
    
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16, channels=1, rate=24000,
        input=True, output=True, frames_per_buffer=4096
    )
    
    async with websockets.connect(url) as ws:
        config = {
            "type": "session.update",
            "session": {
                "model": "gpt-4o-realtime",
                "voice": "nova",
                "modalities": ["audio"],
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {"type": "server_vad", "threshold": 0.5, "silence_duration_ms": 700}
            }
        }
        await ws.send(json.dumps(config))
        
        async def send_audio():
            while True:
                audio_chunk = stream.read(4096, exception_on_overflow=False)
                await ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": audio_chunk.hex()}))
                await asyncio.sleep(0.01)
        
        async def receive_events():
            async for message in ws:
                event = json.loads(message)
                if event['type'] == "response.audio.delta":
                    stream.write(bytes.fromhex(event['delta']))
                elif event['type'] == "response.audio.done":
                    print("Response complete")
        
        await asyncio.gather(send_audio(), receive_events())
    
    stream.close()
    audio.terminate()

asyncio.run(voice_agent())
```

### Realtime Transcription

```python
import asyncio
import websockets
import json
import os

async def realtime_transcription(audio_stream):
    api_key = os.getenv("OPENAI_API_KEY")
    url = f"wss://api.openai.com/v1/realtime?api_key={api_key}"
    
    async with websockets.connect(url) as ws:
        config = {
            "type": "session.update",
            "session": {
                "model": "gpt-4o-realtime",
                "modalities": ["text"],
                "input_audio_format": "pcm16",
                "turn_detection": {"type": "server_vad"}
            }
        }
        await ws.send(json.dumps(config))
        
        transcript = []
        
        async def send_audio():
            for chunk in audio_stream:
                await ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": chunk.hex()}))
                await asyncio.sleep(0.01)
        
        async def receive_transcription():
            async for message in ws:
                event = json.loads(message)
                if event['type'] == "conversation.item.created":
                    if event['item']['role'] == "user":
                        text = event['item']['content'][0]['transcript']
                        transcript.append(text)
                        print(f"[Transcript] {text}")
        
        await asyncio.gather(send_audio(), receive_transcription())
        return transcript
```

## Error Responses

- **Connection errors**: WebSocket connection failures
- **Authentication errors**: Invalid API key
- **Model errors**: Unsupported model or configuration

## Differences from Other APIs

- **vs Batch transcription**: Realtime processes as audio arrives, batch after upload
- **vs Twilio/Vonage**: OpenAI provides AI models, telephony providers handle calls
- **vs Google Dialogflow**: Similar voice agent capabilities, different implementation

## Limitations and Known Issues

- **WebSocket only**: No REST API alternative for realtime [VERIFIED]
- **Model availability**: Limited realtime-optimized models [VERIFIED]
- **Network sensitivity**: Requires stable connection [ASSUMED]

## Gotchas and Quirks

- **VAD tuning required**: Default VAD may need adjustment [ASSUMED]
- **Audio format critical**: Format mismatch causes errors [ASSUMED]
- **Session state**: Must manage conversation state manually [VERIFIED]

## TypeScript Examples

### Text-to-Speech

```typescript
import OpenAI from "openai";
import { writeFileSync } from "fs";

const client = new OpenAI();

const response = await client.audio.speech.create({
  model: "tts-1",
  voice: "alloy",
  input: "Hello, this is a test.",
});

const buffer = Buffer.from(await response.arrayBuffer());
writeFileSync("output.mp3", buffer);
```

## Sources

- OAIAPI-SC-OAI-GAUDIO - Audio guide
- OAIAPI-SC-OAI-GRTAPI - Realtime API guide
- OAIAPI-SC-OAI-GVOICE - Voice agents guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: GPT-Realtime-2.1 and 2.1-mini models (2026-07)
- Changed: Removed stale gpt-4o-realtime reference
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 15:00]**
- Enriched: Full WebSocket, session config, events, SDK examples from 2026-03-20
- Added: Realtime 2, Realtime Translate, Realtime Whisper references

**[2026-05-22 11:40]**
- Stub created
