# INFO: Gemini API Audio Generation (TTS and Lyria)

**Doc ID**: GEMAPI-IN31
**Goal**: Document text-to-speech models, Lyria music generation, and audio output configuration
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini API offers audio generation through TTS (Text-to-Speech) models and Lyria (music generation). TTS models (`gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-preview-tts`) convert text to natural-sounding speech with configurable voice, language, and style. Lyria Experimental generates music and audio content. TTS is accessed via `generateContent` with `responseModalities: ["AUDIO"]` and voice configuration in `speechConfig`. Output audio is returned as base64-encoded data in response parts. Multiple voice presets are available. The Live API also supports real-time audio output for conversational agents. This is unique compared to Anthropic (no audio generation) but comparable to OpenAI's TTS API (which uses a separate endpoint).

## Key Facts

- [VERIFIED] TTS models: gemini-2.5-flash-preview-tts, gemini-2.5-pro-preview-tts (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Lyria Experimental: music/audio generation (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] responseModalities: ["AUDIO"] for audio output (GEMAPI-SC-GOOG-TTSDOC)
- [VERIFIED] Voice configuration via speechConfig (GEMAPI-SC-GOOG-TTSDOC)
- [VERIFIED] Output as base64-encoded audio in response parts (GEMAPI-SC-GOOG-TTSDOC)

## Quick Reference

**TTS Models**: `gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-preview-tts`
**Music**: `lyria-realtime-exp`
**Config**: `responseModalities: ["AUDIO"]`, `speechConfig: {voiceConfig: {prebuiltVoiceConfig: {voiceName: "..."}}}`

## Python Examples

### Example 1: Text-to-Speech

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            )
        ),
    ),
    contents="Hello! Welcome to the Gemini API. Let me show you what I can do."
)

# Save audio output
for part in response.candidates[0].content.parts:
    if part.inline_data:
        audio_bytes = base64.b64decode(part.inline_data.data)
        with open("speech_output.wav", "wb") as f:
            f.write(audio_bytes)
        print(f"Audio saved ({len(audio_bytes)} bytes)")
```

### Example 2: Multi-Speaker TTS

```python
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

script = """
Speaker 1: Good morning! How was your weekend?
Speaker 2: It was great! I went hiking in the mountains.
Speaker 1: That sounds wonderful. What trail did you take?
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
    ),
    contents=script
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("dialogue.wav", "wb") as f:
            f.write(base64.b64decode(part.inline_data.data))
```

## Comparison with Other APIs

### vs OpenAI

- **TTS**: Gemini: TTS via generateContent | OpenAI: `/v1/audio/speech` (separate endpoint)
- **Integration**: Gemini: same endpoint as text gen | OpenAI: dedicated audio API
- **Voices**: Both offer multiple voice presets
- **Music**: Gemini: Lyria (experimental) | OpenAI: no music generation

### vs Anthropic

- **Audio generation**: Gemini: TTS + Lyria | Anthropic: **no audio generation**
- **UNIQUE advantage**: Anthropic has no audio output capability

## Error Responses

- **400**: Invalid voice name, unsupported responseModalities
- Safety filters may block audio generation

## Rate Limiting / Throttling

TTS models have preview-level rate limits. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] TTS models are preview status (GEMAPI-SC-GOOG-MODELS)
- [VERIFIED] Lyria is experimental (GEMAPI-SC-GOOG-MODELS)
- Audio output can be large (base64 encoding)

## Gotchas and Quirks

- Must set `responseModalities: ["AUDIO"]` - model returns text by default
- TTS uses the generateContent endpoint, not a separate audio endpoint
- Audio output is base64-encoded in response - can be large for long speech
- Voice names are case-sensitive
- Multi-speaker capability is built-in (model detects speaker labels in text)

## Sources

- GEMAPI-SC-GOOG-TTSDOC: https://ai.google.dev/gemini-api/docs/text-to-speech [VERIFIED]
- GEMAPI-SC-GOOG-MODELS: https://ai.google.dev/gemini-api/docs/models [VERIFIED]

## Document History

**[2026-03-20 05:15]**
- Initial document created
