# INFO: Text to Speech API

**Doc ID**: GROKAPI-IN27
**Goal**: TTS endpoint, voices, audio formats, streaming, pricing
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Text to Speech (TTS) API converts text into natural speech. Billed at $4.20 per 1 million input characters. Supports multiple voices, both streaming and batch output, and multiple audio formats: MP3, WAV, PCM, mu-law, A-law. Up to 100 concurrent requests per team. Compatible with OpenAI's TTS endpoint format (`POST /v1/audio/speech`). [VERIFIED] (GROKAPI-SC-XAI-TTS | https://docs.x.ai/developers/model-capabilities/audio/text-to-speech)

## Key Facts

- [VERIFIED] Pricing: $4.20 per 1M characters (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Concurrent requests: 100 per team (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Audio formats: MP3, WAV, PCM, mu-law, A-law (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Multiple voices available (GROKAPI-SC-XAI-TTS)
- [VERIFIED] Supports streaming and batch output (GROKAPI-SC-XAI-MODELS)

## Quick Reference

- **Endpoint**: `POST /v1/audio/speech`
- **Pricing**: $4.20 / 1M characters
- **Formats**: MP3, WAV, PCM, mu-law, A-law
- **Max concurrent**: 100 per team

## Examples

### Basic TTS (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello! This is a test of the Grok text-to-speech API.",
)

response.stream_to_file("output.mp3")
```

### cURL

```bash
curl https://api.x.ai/v1/audio/speech \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "voice": "alloy",
    "input": "Hello world!"
  }' \
  --output speech.mp3
```

## Differences from Other APIs

### vs OpenAI TTS
- **Compatible endpoint**: Same `POST /v1/audio/speech` format
- **Same SDK**: `client.audio.speech.create()` works for both
- **Pricing**: xAI $4.20/1M chars vs OpenAI $15.00/1M chars (TTS) or $30.00/1M chars (TTS HD)

### vs Anthropic
- **UNIQUE**: Anthropic has no TTS API

### vs Gemini
- **Different approach**: Gemini has text-to-speech as part of multimodal output

## Sources

- GROKAPI-SC-XAI-TTS | https://docs.x.ai/developers/model-capabilities/audio/text-to-speech | Accessed: 2026-03-20
- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:15]**
- Initial document created with TTS reference and pricing
