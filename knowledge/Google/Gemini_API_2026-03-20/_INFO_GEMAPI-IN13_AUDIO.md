# INFO: Gemini API Audio Input

**Doc ID**: GEMAPI-IN13
**Goal**: Document audio input methods, supported formats, and audio understanding capabilities
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini models natively process audio as part of multimodal prompts through inline base64 data or File API references. Supported audio formats include MP3, WAV, AIFF, AAC, OGG, and FLAC. Audio is processed as tokens counting toward the context window. The API can perform transcription, audio understanding, summarization, and question answering about audio content. For large audio files, the File API is recommended. Audio processing is integrated into the standard `generateContent` endpoint - no separate audio API. This is a significant differentiator from OpenAI (which uses a separate Whisper API for audio) and Anthropic (which has no native audio input support).

## Key Facts

- [VERIFIED] Two input methods: inlineData (base64) and fileData (File API) (GEMAPI-SC-GOOG-FILINP)
- [VERIFIED] Supported formats: MP3, WAV, AIFF, AAC, OGG, FLAC (GEMAPI-SC-GOOG-FILINP)
- [VERIFIED] Audio processed as tokens in context window (GEMAPI-SC-GOOG-FILPRM)
- [VERIFIED] File API recommended for large audio files (GEMAPI-SC-GOOG-FILAPI)

## Quick Reference

**Inline**: `{"inlineData": {"mimeType": "audio/mp3", "data": "base64..."}}`
**File API**: `{"fileData": {"mimeType": "audio/mp3", "fileUri": "..."}}`
**Supported**: MP3, WAV, AIFF, AAC, OGG, FLAC

## Python Examples

### Example 1: Audio Transcription via File API

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Upload audio file
uploaded = client.files.upload(file="recording.mp3")

while uploaded.state == "PROCESSING":
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[
            types.Part(file_data=types.FileData(
                mime_type=uploaded.mime_type, file_uri=uploaded.uri
            )),
            types.Part(text="Transcribe this audio recording verbatim."),
        ])
    ]
)
print(response.text)
```

### Example 2: Audio Summarization

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

uploaded = client.files.upload(file="podcast_episode.mp3")
while uploaded.state == "PROCESSING":
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="Provide structured summaries with key points and timestamps."
    ),
    contents=[
        types.Content(role="user", parts=[
            types.Part(file_data=types.FileData(
                mime_type=uploaded.mime_type, file_uri=uploaded.uri
            )),
            types.Part(text="Summarize this audio with key topics and approximate timestamps."),
        ])
    ]
)
print(response.text)
```

## Comparison with Other APIs

### vs OpenAI

- **Audio input**: Gemini: native in generateContent | OpenAI: separate Whisper API for transcription
- **Approach**: Gemini: unified multimodal endpoint | OpenAI: dedicated /v1/audio/transcriptions
- **Understanding**: Gemini: transcription + understanding + Q&A | OpenAI: Whisper (transcription only), GPT-4o (audio in Realtime API)
- **Formats**: Similar format support

### vs Anthropic

- **Audio input**: Gemini: native support | Anthropic: **no audio input support**
- **UNIQUE advantage**: Gemini processes audio natively; Anthropic requires external transcription first

## Error Responses

- **400**: Unsupported audio format, file too large for inline
- **404**: Invalid File API reference

## Rate Limiting / Throttling

Standard rate limits apply. Audio files consume tokens proportional to duration. See GEMAPI-IN04.

## Limitations and Known Issues

- Audio duration limited by model's context window (converted to tokens)
- Very long audio files may need to be split

## Gotchas and Quirks

- Audio tokens can be expensive for long recordings - check token count first via countTokens
- No streaming audio input in REST API - for real-time audio use Live API (GEMAPI-IN32)
- Processing state may take time for large files - poll `files.get()` until state is "ACTIVE"

## Sources

- GEMAPI-SC-GOOG-FILINP: https://ai.google.dev/gemini-api/docs/file-input-methods [VERIFIED]
- GEMAPI-SC-GOOG-FILPRM: https://ai.google.dev/gemini-api/docs/file-prompting-strategies [VERIFIED]

## Document History

**[2026-03-20 03:50]**
- Initial document created
