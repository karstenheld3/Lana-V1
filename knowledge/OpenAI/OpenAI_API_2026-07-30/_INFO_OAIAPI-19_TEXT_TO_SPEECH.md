# Text-to-Speech (TTS)

**Doc ID**: OAIAPI-IN19
**Goal**: Document TTS API with models, voices, custom voices, and consent management
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI TTS API (POST /v1/audio/speech) converts text to spoken audio using neural voices. Models: tts-1 (faster, lower latency), tts-1-hd (higher quality), gpt-audio-1.5 (NEW). Six preset voices: alloy, echo, fable, onyx, nova, shimmer. Custom voices available for eligible accounts via voice consent management. Output formats: mp3, opus, aac, flac, wav, pcm. Speed parameter (0.25-4.0). Maximum input 4096 characters. gpt-4o-mini-tts being deprecated. [VERIFIED] (OAIAPI-SC-OAI-AUDSPK, OAIAPI-SC-OAI-AUDVOI, OAIAPI-SC-OAI-AUDVCS)

## Key Facts

- **Endpoint**: POST /v1/audio/speech [VERIFIED]
- **Models**: tts-1, tts-1-hd, gpt-audio-1.5 [VERIFIED]
- **Preset voices**: alloy, echo, fable, onyx, nova, shimmer [VERIFIED]
- **Custom voices**: Available for eligible accounts [VERIFIED]
- **Max input**: 4096 characters [VERIFIED]

## Models

- **tts-1**: Lower latency, good quality, real-time capable
- **tts-1-hd**: Higher quality, higher latency, audiobooks/production
- **gpt-audio-1.5**: NEW model with improved naturalness

## Preset Voices

- **alloy**: Neutral, balanced - general-purpose
- **echo**: Clear, articulate - educational content
- **fable**: Warm, storytelling - audiobooks, narratives
- **onyx**: Deep, authoritative - announcements, professional
- **nova**: Bright, energetic - engaging content, marketing
- **shimmer**: Soft, gentle - meditation, calming content

## Custom Voices

Available for eligible accounts only. Workflow:
1. Record voice samples (15+ minutes recommended)
2. Submit legal consent form from voice owner
3. OpenAI verifies consent and samples
4. Voice profile generated
5. Use custom voice ID in API calls

Voice profile management:
```
POST /v1/audio/voices       # Create
GET /v1/audio/voices        # List
DELETE /v1/audio/voices/{voice_id}  # Delete
```

## Request Parameters

**Required:**
- **model**: tts-1, tts-1-hd, or gpt-audio-1.5
- **input**: Text to convert (max 4096 chars)
- **voice**: Voice ID (preset or custom)

**Optional:**
- **response_format**: mp3 (default), opus, aac, flac, wav, pcm
- **speed**: Playback speed (0.25-4.0, default: 1.0)

## Response Formats

- **mp3** (default): Good compression, universal compatibility
- **opus**: Excellent compression, optimized for streaming
- **aac**: Good compression, wide mobile compatibility
- **flac**: Lossless, highest quality, large files
- **wav**: Uncompressed, highest quality, largest files
- **pcm**: Raw audio, for audio processing pipelines

## SDK Examples (Python)

### Basic TTS

```python
from openai import OpenAI

client = OpenAI()

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello! This is a test of the text-to-speech system."
)

response.stream_to_file("output.mp3")
```

### High-Quality TTS

```python
from openai import OpenAI

client = OpenAI()

response = client.audio.speech.create(
    model="tts-1-hd",
    voice="fable",
    input="Once upon a time, in a land far away, there lived a brave knight."
)

response.stream_to_file("story.mp3")
```

### Speed Control and Formats

```python
from openai import OpenAI

client = OpenAI()

# Fast playback
response = client.audio.speech.create(
    model="tts-1",
    voice="echo",
    input="This audio will play faster than normal.",
    speed=1.5
)
response.stream_to_file("fast_speech.mp3")

# Opus for streaming
response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input="Streaming-optimized audio.",
    response_format="opus"
)
response.stream_to_file("stream.opus")
```

### Voice Comparison

```python
from openai import OpenAI

client = OpenAI()

text = "Hello, this is a voice comparison test."
voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

for voice in voices:
    response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
    response.stream_to_file(f"voice_{voice}.mp3")
    print(f"Generated {voice}.mp3")
```

### Long Text Chunking

```python
from openai import OpenAI

def text_to_speech_long(text: str, output_file: str, chunk_size: int = 4000):
    client = OpenAI()
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    audio_files = []
    for i, chunk in enumerate(chunks):
        response = client.audio.speech.create(model="tts-1", voice="alloy", input=chunk)
        chunk_file = f"chunk_{i}.mp3"
        response.stream_to_file(chunk_file)
        audio_files.append(chunk_file)
    
    # Concatenate with ffmpeg: ffmpeg -i "concat:file1.mp3|file2.mp3" -acodec copy output.mp3
    return audio_files
```

### Production TTS Service

```python
from openai import OpenAI
from pathlib import Path

class TTSService:
    def __init__(self, model: str = "tts-1", voice: str = "alloy"):
        self.client = OpenAI()
        self.model = model
        self.voice = voice
    
    def generate(self, text: str, output_path: str, speed: float = 1.0, format: str = "mp3"):
        if len(text) > 4096:
            raise ValueError("Text exceeds 4096 character limit")
        
        response = self.client.audio.speech.create(
            model=self.model, voice=self.voice, input=text, speed=speed, response_format=format
        )
        response.stream_to_file(output_path)
        
        return {"path": output_path, "size": Path(output_path).stat().st_size, "format": format}

# Usage
tts = TTSService(model="tts-1-hd", voice="fable")
result = tts.generate("Welcome to our service!", "welcome.mp3")
```

### Custom Voice (Eligible Accounts)

```python
from openai import OpenAI

client = OpenAI()

response = client.audio.speech.create(
    model="tts-1-hd",
    voice="voice_custom_abc123",
    input="This uses a custom voice profile."
)
response.stream_to_file("custom_voice.mp3")
```

## Error Responses

- **400 Bad Request** - Invalid parameters or text too long
- **403 Forbidden** - Custom voice access denied
- **429 Too Many Requests** - Rate limit exceeded

## Differences from Other APIs

- **vs Google Text-to-Speech**: OpenAI simpler, Google more voice options
- **vs Amazon Polly**: Similar capabilities, different pricing
- **vs ElevenLabs**: ElevenLabs specializes in voice cloning, OpenAI general-purpose

## Limitations and Known Issues

- **4096 char limit**: Long text must be chunked [VERIFIED]
- **Custom voices limited**: Only eligible accounts [VERIFIED]
- **No SSML support**: Cannot control pronunciation, pauses [ASSUMED]

## Gotchas and Quirks

- **Voice selection matters**: Different voices better for different content [ASSUMED]
- **Speed affects quality**: Very fast/slow speeds may reduce quality [ASSUMED]
- **Format file extension**: Must use correct extension for format [VERIFIED]

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

- OAIAPI-SC-OAI-AUDSPK - POST Create speech
- OAIAPI-SC-OAI-AUDVOI - Audio voices guide
- OAIAPI-SC-OAI-AUDVCS - Custom voices and consent guide
- OAIAPI-SC-OAI-GAUDIO - Audio guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:55]**
- Enriched: Full models, voices, custom voices, SDK examples, production service from 2026-03-20
- Added: gpt-audio-1.5 model, deprecation note for gpt-4o-mini-tts

**[2026-05-22 11:40]**
- Stub created
