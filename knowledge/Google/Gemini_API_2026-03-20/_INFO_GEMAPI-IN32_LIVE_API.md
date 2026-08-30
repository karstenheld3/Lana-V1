# INFO: Gemini API Live API

**Doc ID**: GEMAPI-IN32
**Goal**: Document the WebSocket-based Live API for real-time bidirectional streaming
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini Live API (`BidiGenerateContent`) provides a stateful WebSocket-based interface for real-time bidirectional streaming. Unlike REST endpoints, the Live API maintains a persistent connection enabling continuous audio/video/text exchange between client and model. The WebSocket endpoint is `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent`. The API supports real-time voice conversations, video processing, screen sharing analysis, and multi-turn interactions with sub-second latency. Sessions have a 15-minute default duration with 10-minute reconnection windows via session resumption. Input modalities include text, audio (PCM16, 16kHz), and video frames. Output modalities include text and audio. The Live API supports function calling, allowing voice agents to interact with external systems. Ephemeral tokens provide secure client-side authentication. This is Gemini's most unique feature - while OpenAI has a Realtime API, the Gemini Live API offers native audio processing, barge-in support, affective dialog, and context circulation between tools.

## Key Facts

- [VERIFIED] WebSocket endpoint: `wss://generativelanguage.googleapis.com/ws/...BidiGenerateContent` (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] Stateful persistent connection (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] Input: text, audio (PCM16 16kHz), video frames (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] Output: text, audio (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] 15-minute default session, 10-minute reconnection window (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] Session resumption for reconnection (GEMAPI-SC-GOOG-LIVSESS)
- [VERIFIED] Barge-in support (interrupt model while speaking) (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] Function calling within live sessions (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] Ephemeral tokens for client-side auth (GEMAPI-SC-GOOG-EPHTKN)

## Use Cases

- **Voice assistants**: Real-time conversational AI agents
- **Customer service**: Live voice support with tool integration
- **Accessibility**: Real-time transcription and audio description
- **Education**: Interactive tutoring with voice and screen sharing
- **Gaming**: Real-time NPC dialog and game master interactions

## Quick Reference

**WebSocket URL**: `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent`
**Auth**: `x-goog-api-key` query parameter or ephemeral token
**Audio format**: PCM16, 16kHz mono
**Session duration**: 15 min audio-only, 2 min audio+video (extensible via session management)
**Context window**: 128k tokens (native audio models), 32k tokens (other Live API models)

## Connection Flow

1. **Setup message**: Send configuration (model, system instruction, tools, generation config)
2. **Client sends**: Text messages, audio chunks, video frames
3. **Server sends**: Text responses, audio chunks, function calls, turn completion signals
4. **Barge-in**: Client can interrupt model output by sending new input
5. **Session end**: Connection closes after timeout or explicit close

## Setup Message Schema

```json
{
  "setup": {
    "model": "models/gemini-2.5-flash",
    "generationConfig": {
      "responseModalities": ["AUDIO"],
      "speechConfig": {
        "voiceConfig": {
          "prebuiltVoiceConfig": {
            "voiceName": "Aoede"
          }
        }
      }
    },
    "systemInstruction": {
      "parts": [{"text": "You are a helpful voice assistant."}]
    },
    "tools": [
      {"functionDeclarations": [{"name": "get_weather", "description": "...", "parameters": {}}]}
    ],
    "sessionResumption": {
      "handle": "previous-session-handle"
    }
  }
}
```

## Client Messages

**Text input:**
```json
{
  "clientContent": {
    "turns": [{"role": "user", "parts": [{"text": "Hello"}]}],
    "turnComplete": true
  }
}
```

**Audio input:**
```json
{
  "realtimeInput": {
    "mediaChunks": [{
      "mimeType": "audio/pcm;rate=16000",
      "data": "base64-encoded-pcm16-audio"
    }]
  }
}
```

**Video frame:**
```json
{
  "realtimeInput": {
    "mediaChunks": [{
      "mimeType": "image/jpeg",
      "data": "base64-encoded-jpeg-frame"
    }]
  }
}
```

**Function response:**
```json
{
  "toolResponse": {
    "functionResponses": [{
      "name": "get_weather",
      "response": {"temperature": 22, "condition": "sunny"},
      "id": "call_001"
    }]
  }
}
```

## Server Messages

**Text output:**
```json
{
  "serverContent": {
    "modelTurn": {
      "parts": [{"text": "Hello! How can I help?"}]
    },
    "turnComplete": true
  }
}
```

**Audio output:**
```json
{
  "serverContent": {
    "modelTurn": {
      "parts": [{
        "inlineData": {
          "mimeType": "audio/pcm;rate=24000",
          "data": "base64-encoded-pcm24-audio"
        }
      }]
    }
  }
}
```

**Function call:**
```json
{
  "toolCall": {
    "functionCalls": [{
      "name": "get_weather",
      "args": {"location": "Paris"},
      "id": "call_001"
    }]
  }
}
```

## Python Examples

### Example 1: Basic Live Session

```python
import asyncio
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

async def main():
    async with client.aio.live.connect(
        model="gemini-2.5-flash",
        config=types.LiveConnectConfig(
            response_modalities=["TEXT"],
            system_instruction=types.Content(
                parts=[types.Part(text="You are a helpful assistant.")]
            ),
        )
    ) as session:
        # Send text
        await session.send(input="What is the capital of France?", end_of_turn=True)

        # Receive response
        async for message in session.receive():
            if message.text:
                print(message.text, end="")
            if message.server_content and message.server_content.turn_complete:
                break
        print()

asyncio.run(main())
```

### Example 2: Voice Conversation

```python
import asyncio
import pyaudio
import base64
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

async def voice_chat():
    async with client.aio.live.connect(
        model="gemini-2.5-flash",
        config=types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Puck"
                    )
                )
            ),
        )
    ) as session:
        # Send audio chunk (PCM16, 16kHz)
        audio_data = b"\x00" * 3200  # placeholder: 100ms of silence
        await session.send(
            input=types.LiveClientRealtimeInput(
                media_chunks=[types.Blob(
                    mime_type="audio/pcm;rate=16000",
                    data=base64.b64encode(audio_data).decode()
                )]
            )
        )

        # Receive audio response
        async for message in session.receive():
            if message.data:
                # Play audio response (PCM24, 24kHz)
                print(f"Received audio chunk: {len(message.data)} bytes")
            if message.server_content and message.server_content.turn_complete:
                break

asyncio.run(voice_chat())
```

### Example 3: Session Resumption

```python
import asyncio
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

async def resumable_session():
    session_handle = None

    # First session
    async with client.aio.live.connect(
        model="gemini-2.5-flash",
        config=types.LiveConnectConfig(
            response_modalities=["TEXT"],
            session_resumption=types.SessionResumptionConfig(handle=None),
        )
    ) as session:
        await session.send(input="Remember: my name is Alice.", end_of_turn=True)
        async for msg in session.receive():
            if msg.text:
                print(msg.text, end="")
            if msg.session_resumption_update:
                session_handle = msg.session_resumption_update.handle
            if msg.server_content and msg.server_content.turn_complete:
                break
        print(f"\nSession handle: {session_handle}")

    # Resume session
    async with client.aio.live.connect(
        model="gemini-2.5-flash",
        config=types.LiveConnectConfig(
            response_modalities=["TEXT"],
            session_resumption=types.SessionResumptionConfig(handle=session_handle),
        )
    ) as session:
        await session.send(input="What is my name?", end_of_turn=True)
        async for msg in session.receive():
            if msg.text:
                print(msg.text, end="")
            if msg.server_content and msg.server_content.turn_complete:
                break

asyncio.run(resumable_session())
```

## Comparison with Other APIs

### vs OpenAI

- **Real-time API**: Gemini: Live API (WebSocket) | OpenAI: Realtime API (WebSocket)
- **Audio**: Gemini: native audio processing | OpenAI: native audio (GPT-4o Realtime)
- **Video input**: Gemini: live video frames | OpenAI: no video in Realtime API
- **Session persistence**: Gemini: session resumption handles | OpenAI: session management
- **Barge-in**: Both support interruption
- **Function calling**: Both support function calling in real-time
- **Ephemeral tokens**: Gemini: yes | OpenAI: ephemeral keys
- **UNIQUE to Gemini**: Video frame input, native audio models, affective dialog

### vs Anthropic

- **Real-time API**: Gemini: Live API | Anthropic: **no real-time/WebSocket API**
- **UNIQUE advantage**: Anthropic has no equivalent to the Live API

## Error Responses

- WebSocket close codes indicate error type
- Session timeout after 15 minutes (reconnect via session resumption)
- Connection drops may occur during high load

## Rate Limiting / Throttling

Live API has specific concurrent session limits per project. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Audio-only sessions: 15 minutes; audio+video sessions: **2 minutes** (GEMAPI-SC-GOOG-LIVGUI)
- [VERIFIED] Context window: 128k tokens (native audio), **32k tokens** (other Live models) - NOT the 1M of REST API (GEMAPI-SC-GOOG-LIVGUI)
- [VERIFIED] Native audio models ONLY support AUDIO response modality - use output transcription for text (GEMAPI-SC-GOOG-LIVGUI)
- [VERIFIED] 10-minute reconnection window for session resumption (GEMAPI-SC-GOOG-LIVSESS)
- [VERIFIED] 70 supported languages for Live API conversations (GEMAPI-SC-GOOG-LIVGUI)
- WebSocket connections are stateful - requires persistent connection management
- Audio quality depends on input quality (16kHz PCM recommended)

## Gotchas and Quirks

- WebSocket URL is very long - easy to copy incorrectly
- Audio input: PCM16 at 16kHz; audio output: PCM at 24kHz (different rates!)
- Session resumption requires preserving the handle between connections
- Ephemeral tokens require v1alpha API version for creation
- Barge-in support means client can interrupt - must handle partial responses
- Video frames should be sent at reasonable intervals (not every frame)
- `turnComplete: true` signals end of input - without it, model waits for more
- **2-minute video limit is severe** - use session management techniques for longer video interactions
- 32k context window for non-native-audio models is much smaller than REST API's 1M - plan accordingly
- Voice Activity Detection (VAD) is automatic by default but configurable (sensitivity, silence thresholds)
- Proactive audio feature controls when the model responds and in what contexts
- Audio transcription feature provides text transcripts of both user input and model output

## Sources

- GEMAPI-SC-GOOG-LIVAPI: https://ai.google.dev/gemini-api/docs/live [VERIFIED]
- GEMAPI-SC-GOOG-LIVGUI: https://ai.google.dev/gemini-api/docs/live-guide [VERIFIED]
- GEMAPI-SC-GOOG-LIVSESS: https://ai.google.dev/gemini-api/docs/live-session [VERIFIED]
- GEMAPI-SC-GOOG-LIVREF: https://ai.google.dev/api/live [VERIFIED]
- GEMAPI-SC-GOOG-EPHTKN: https://ai.google.dev/gemini-api/docs/ephemeral-tokens [VERIFIED]

## Document History

**[2026-03-20 06:25]**
- Added: 2-minute video session limit, 32k/128k context windows, native audio AUDIO-only modality
- Added: VAD configuration, proactive audio, audio transcription, 70 languages

**[2026-03-20 05:20]**
- Initial document created with full Live API documentation
