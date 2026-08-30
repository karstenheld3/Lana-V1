# Realtime 2, Realtime Translate, and Realtime Whisper

**Doc ID**: OAIAPI-IN77
**Goal**: Document new Realtime 2 voice model, Realtime Translate for live translation, and Realtime Whisper for streaming STT
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN39_REALTIME_OVERVIEW.md [OAIAPI-IN39]` for Realtime API overview

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Three new Realtime models released 2026-05 unlock a new class of voice applications. **GPT-Realtime-2** is the most intelligent voice model with GPT-5-class reasoning, supporting speech-to-speech agents that can listen, reason, handle interruptions, use tools, and sustain longer conversations. **GPT-Realtime-Translate** provides live speech translation from 70+ input languages to 13 output languages while keeping pace with the speaker. **GPT-Realtime-Whisper** provides streaming speech-to-text that transcribes speech live as the speaker talks. All three connect via WebSocket or WebRTC, use the existing Realtime API infrastructure, and support configurable reasoning. The Translations API adds CRUD endpoints for managing translation sessions. [VERIFIED] (OAIAPI-SC-OAI-GCHLOG, OAIAPI-SC-OAI-GRTTRL, OAIAPI-SC-OAI-GRTMDL)

## Models

### GPT-Realtime-2
- **Purpose**: Voice agents with GPT-5-class reasoning
- **Capabilities**: Listen, reason, handle interruptions, use tools, sustain conversations
- **Reasoning**: Configurable reasoning effort for speech-to-speech
- **Model ID**: `gpt-realtime-2`
- **Use case**: Customer service agents, interactive tutors, voice assistants needing reasoning

### GPT-Realtime-Translate
- **Purpose**: Live speech translation
- **Input languages**: 70+ languages
- **Output languages**: 13 languages (including English, Spanish, French, German, Chinese, Japanese, Korean, Portuguese, Italian, Russian, Arabic, Hindi, Tamil)
- **Behavior**: Keeps pace with speaker in real-time
- **Model ID**: `gpt-realtime-translate`
- **Use case**: Real-time interpreter apps, multilingual customer support, live event translation

### GPT-Realtime-1.5
- **Purpose**: Best voice model for audio in, audio out (non-reasoning)
- **Pricing**: Audio $32/$64, Text $4/$16 per MTok
- **Model ID**: `gpt-realtime-1.5`
- **Use case**: High-quality voice interactions without reasoning overhead

### GPT-Realtime-Mini
- **Purpose**: Cost-efficient realtime voice
- **Pricing**: Audio $10/$20, Text $0.60/$2.40 per MTok
- **Model ID**: `gpt-realtime-mini`
- **Use case**: High-volume, cost-sensitive voice applications

### GPT-Realtime-Whisper
- **Purpose**: Streaming speech-to-text
- **Behavior**: Transcribes speech live as speaker talks
- **Model ID**: `gpt-realtime-whisper`
- **Use case**: Live captioning, meeting transcription, real-time note-taking

## Pricing Comparison

- **gpt-realtime-2**: Audio $32/$64, Text $4/$24, Image $5/- per MTok (most capable, most expensive)
- **gpt-realtime-1.5**: Audio $32/$64, Text $4/$16 per MTok (best non-reasoning voice)
- **gpt-realtime-mini**: Audio $10/$20, Text $0.60/$2.40 per MTok (budget option)
- **gpt-realtime-translate**: $0.034/minute (flat rate per minute)
- **gpt-realtime-whisper**: See transcription pricing

## REST API

### Translations (NEW endpoints)

#### Create a Translation

**Endpoint**: `POST /v1/realtime/translations`

Creates a new translation session.

**Request**:

```json
{
  "model": "gpt-realtime-translate",
  "input_language": "auto",
  "output_language": "en",
  "voice": "alloy"
}
```

**Parameters**:

- **model** (string, required) - Model to use: `gpt-realtime-translate`
- **input_language** (string, optional) - Source language code or `auto` for detection. Default: `auto`
- **output_language** (string, required) - Target language code (e.g., `en`, `es`, `fr`, `de`, `zh`, `ja`, `ko`)
- **voice** (string, optional) - Voice for translated audio output

#### Retrieve a Translation

**Endpoint**: `GET /v1/realtime/translations/{translation_id}`

#### Delete a Translation

**Endpoint**: `DELETE /v1/realtime/translations/{translation_id}`

#### List Translations

**Endpoint**: `GET /v1/realtime/translations`

### Transcription Sessions

**Endpoint**: `POST /v1/realtime/transcription_sessions`

Creates a streaming transcription session using Realtime Whisper.

**Request**:

```json
{
  "model": "gpt-realtime-whisper",
  "language": "en"
}
```

## SDK Examples (Python)

### Realtime 2 Voice Agent (WebSocket)

```python
import asyncio
import websockets
import json
import base64

async def voice_agent():
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1",
    }

    async with websockets.connect(url, additional_headers=headers) as ws:
        # Configure session with reasoning
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "You are a helpful customer service agent. Reason through complex problems before responding.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "tools": [
                    {
                        "type": "function",
                        "name": "lookup_order",
                        "description": "Look up order status by order ID",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string"}
                            },
                            "required": ["order_id"]
                        }
                    }
                ],
            }
        }))

        # Process events
        async for message in ws:
            event = json.loads(message)
            if event["type"] == "response.audio.delta":
                audio_chunk = base64.b64decode(event["delta"])
                # Play audio chunk
            elif event["type"] == "response.function_call_arguments.done":
                # Handle tool call
                pass

asyncio.run(voice_agent())
```

### Live Translation (WebSocket)

```python
import asyncio
import websockets
import json

async def live_translator():
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-translate"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1",
    }

    async with websockets.connect(url, additional_headers=headers) as ws:
        # Configure translation session
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["audio"],
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "voice": "nova",
                "input_audio_transcription": {
                    "model": "gpt-realtime-whisper",
                },
            }
        }))

        # Stream audio input and receive translated audio output
        async for message in ws:
            event = json.loads(message)
            if event["type"] == "response.audio.delta":
                translated_audio = event["delta"]
                # Play translated audio
            elif event["type"] == "conversation.item.input_audio_transcription.completed":
                print(f"Source: {event['transcript']}")

asyncio.run(live_translator())
```

### Streaming Transcription

```python
import asyncio
import websockets
import json

async def stream_transcription():
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-whisper"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1",
    }

    async with websockets.connect(url, additional_headers=headers) as ws:
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "input_audio_format": "pcm16",
            }
        }))

        async for message in ws:
            event = json.loads(message)
            if event["type"] == "conversation.item.input_audio_transcription.completed":
                print(f"Transcript: {event['transcript']}")

asyncio.run(stream_transcription())
```

### REST Translation API

> **SDK note (v2.45.0)**: `client.realtime.translations.*` methods are not available in
> the openai Python SDK. Translations are managed via WebSocket events, not REST endpoints.
> The examples below show the intended REST API pattern from documentation.

```python
from openai import OpenAI

client = OpenAI()

# Create a translation session
translation = client.realtime.translations.create(
    model="gpt-realtime-translate",
    input_language="auto",
    output_language="en",
)
print(f"Translation ID: {translation.id}")

# List active translations
translations = client.realtime.translations.list()
for t in translations.data:
    print(f"{t.id}: {t.input_language} -> {t.output_language}")

# Delete a translation session
client.realtime.translations.delete(translation.id)
```

## Connection Methods

### WebSocket

Direct WebSocket connection with API key in headers:

```
wss://api.openai.com/v1/realtime?model=gpt-realtime-2
Authorization: Bearer sk-...
OpenAI-Beta: realtime=v1
```

### WebRTC (Browser)

For browser clients, use ephemeral client secrets:

```python
from openai import OpenAI

client = OpenAI()

# Create ephemeral token for browser client
session = client.realtime.sessions.create(
    model="gpt-realtime-2",
    voice="alloy",
)
# session.client_secret.value contains the ephemeral token
```

### WebRTC (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/beta/realtime/sessions.py
# Note: sessions.create is under client.beta.realtime, not client.realtime
from openai import OpenAI

client = OpenAI()

session = client.beta.realtime.sessions.create(
    model="gpt-realtime-2",
    voice="alloy",
)
# session.client_secret.value contains the ephemeral token
```

## Error Responses

- **400 Bad Request** - Invalid model, unsupported language pair
- **401 Unauthorized** - Invalid API key
- **429 Too Many Requests** - Rate limit exceeded
- **503 Service Unavailable** - Model temporarily unavailable

## Gotchas and Quirks

- **Realtime Beta removed**: The old beta interface was removed 2026-05-12. Must use GA Realtime API [VERIFIED]
- **Language support asymmetry**: 70+ input languages but only 13 output languages for Translate [VERIFIED]
- **WebRTC client secrets**: Ephemeral tokens expire, create new ones per session [VERIFIED]
- **Combined transcription**: When using Translate, configure `input_audio_transcription.model: "gpt-realtime-whisper"` to get source-language transcripts alongside translated audio [VERIFIED]

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

- OAIAPI-SC-OAI-GCHLOG - Changelog (2026-05)
- OAIAPI-SC-OAI-GRTTRL - Realtime Translation guide
- OAIAPI-SC-OAI-GRTMDL - Realtime Models Prompting guide
- OAIAPI-SC-OAI-RTTRNSL - Realtime Translations API reference
- OAIAPI-SC-OAI-MGRT2 - Realtime 2 model info
- OAIAPI-SC-OAI-MGRTW - Realtime Whisper model page

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 10:00]**
- Initial documentation for Realtime 2, Translate, and Whisper (new topic)
