# Audio Transcription and Translation

**Doc ID**: OAIAPI-IN18
**Goal**: Document audio transcription and translation APIs with Whisper and GPT-4o transcribe models
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI provides audio transcription via POST /v1/audio/transcriptions (speech-to-text) and POST /v1/audio/translations (speech-to-English). Models: whisper-1 (multilingual, high accuracy), gpt-4o-transcribe, gpt-4o-mini-transcribe (faster, lower cost). Supports multiple audio formats (mp3, mp4, mpeg, mpga, m4a, wav, webm), optional timestamps, prompt for context, language specification, and response formats (json, text, srt, verbose_json, vtt). Translations convert non-English audio to English text. Maximum file size 25MB. [VERIFIED] (OAIAPI-SC-OAI-AUDTRN, OAIAPI-SC-OAI-AUDTRL)

## Key Facts

- **Endpoints**: POST /v1/audio/transcriptions, POST /v1/audio/translations [VERIFIED]
- **Models**: whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe [VERIFIED]
- **Formats**: mp3, mp4, mpeg, mpga, m4a, wav, webm [VERIFIED]
- **Max file size**: 25MB [VERIFIED]
- **Languages**: 50+ languages (Whisper), English only (translations) [VERIFIED]

## Transcription API

### Endpoint

```
POST /v1/audio/transcriptions
```

### Parameters

**Required:**
- **file**: Audio file (multipart/form-data)
- **model**: Model ID (whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe)

**Optional:**
- **language**: ISO-639-1 code (e.g., "en", "fr", "de")
- **prompt**: Context for better accuracy
- **response_format**: Output format (json, text, srt, verbose_json, vtt)
- **temperature**: Sampling temperature (0-1)
- **timestamp_granularities**: ["word"] or ["segment"] for timestamps

### Response Formats

**json** (default):
```json
{"text": "Hello, how are you?"}
```

**verbose_json** (with timestamps):
```json
{
  "task": "transcribe",
  "language": "english",
  "duration": 2.5,
  "text": "Hello, how are you?",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 2.0,
      "text": "Hello, how are you?",
      "temperature": 0.0,
      "avg_logprob": -0.3,
      "no_speech_prob": 0.01
    }
  ]
}
```

**srt** (SubRip subtitles), **vtt** (WebVTT subtitles), **text** (plain text)

## Translation API

```
POST /v1/audio/translations
```

Translates audio to English regardless of input language. Same parameters as transcription except no language parameter.

## SDK Examples (Python)

### Basic Transcription

```python
from openai import OpenAI

client = OpenAI()

with open("audio.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

print(transcription.text)
```

### Transcription with Language and Timestamps

```python
from openai import OpenAI

client = OpenAI()

with open("meeting.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en",
        response_format="verbose_json",
        timestamp_granularities=["segment"]
    )

for segment in transcription.segments:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
```

### Context Prompt for Technical Audio

```python
from openai import OpenAI

client = OpenAI()

with open("technical_talk.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        prompt="This is a discussion about machine learning, neural networks, and transformers."
    )

print(transcription.text)
```

### Generate Subtitles (SRT)

```python
from openai import OpenAI

client = OpenAI()

with open("video_audio.mp3", "rb") as audio_file:
    subtitles = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="srt"
    )

with open("subtitles.srt", "w") as f:
    f.write(subtitles)
```

### Translation to English

```python
from openai import OpenAI

client = OpenAI()

with open("spanish_audio.mp3", "rb") as audio_file:
    translation = client.audio.translations.create(
        model="whisper-1",
        file=audio_file
    )

print(translation.text)
```

### Using gpt-4o-transcribe Models

```python
from openai import OpenAI

client = OpenAI()

with open("audio.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=audio_file
    )

print(transcription.text)
```

### Production Transcription Pipeline

```python
from openai import OpenAI
import os

class TranscriptionService:
    def __init__(self):
        self.client = OpenAI()
    
    def transcribe_file(self, file_path: str, language: str = None, with_timestamps: bool = False):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        if file_size > 25 * 1024 * 1024:
            raise ValueError("File exceeds 25MB limit")
        
        with open(file_path, "rb") as audio_file:
            params = {"model": "whisper-1", "file": audio_file}
            if language:
                params["language"] = language
            if with_timestamps:
                params["response_format"] = "verbose_json"
                params["timestamp_granularities"] = ["segment"]
            
            return self.client.audio.transcriptions.create(**params)

# Usage
service = TranscriptionService()
result = service.transcribe_file("podcast.mp3", language="en", with_timestamps=True)
for segment in result.segments:
    print(f"{segment.start:.1f}s: {segment.text}")
```

## Error Responses

- **400 Bad Request** - Invalid audio format or parameters
- **413 Payload Too Large** - File exceeds 25MB
- **415 Unsupported Media Type** - Unsupported audio format

## Differences from Other APIs

- **vs Google Speech-to-Text**: OpenAI simpler API, Google more features
- **vs Assembly AI**: Similar capabilities, different pricing
- **vs AWS Transcribe**: OpenAI easier setup, AWS more customization

## Limitations and Known Issues

- **25MB file limit**: Large files must be split [VERIFIED]
- **No speaker diarization**: Cannot identify different speakers [ASSUMED]
- **Accuracy varies**: Depends on audio quality and accents [ASSUMED]

## Gotchas and Quirks

- **Language helps accuracy**: Specifying language improves results [VERIFIED]
- **Prompt for context**: Technical terms benefit from context prompts [ASSUMED]
- **File format matters**: WAV provides best quality, MP3 most compatible [ASSUMED]

## TypeScript Examples

### Audio Transcription

```typescript
import OpenAI from "openai";
import { createReadStream } from "fs";

const client = new OpenAI();

const transcription = await client.audio.transcriptions.create({
  model: "whisper-1",
  file: createReadStream("audio.mp3"),
});

console.log(transcription.text);
```

## Sources

- OAIAPI-SC-OAI-AUDTRN - POST Create a transcription
- OAIAPI-SC-OAI-AUDTRL - POST Create a translation
- OAIAPI-SC-OAI-GAUDIO - Audio guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:50]**
- Enriched: Full parameters, response formats, SDK examples, production pipeline from 2026-03-20
- Added: gpt-4o-transcribe model

**[2026-05-22 11:40]**
- Stub created
