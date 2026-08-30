# INFO: Gemini API Live Audio (Native Audio Dialog)

**Doc ID**: GEMAPI-IN33
**Goal**: Document native audio models, affective dialog, barge-in, and real-time voice interaction
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Gemini's native audio models (`gemini-2.5-flash-native-audio-preview`) process and generate audio natively rather than converting through text intermediaries. This enables affective dialog (emotional tone awareness and expression), natural prosody, non-verbal understanding (sighs, laughter, pauses), and speaker diarization. The native audio model supports barge-in (user interrupting model speech) with graceful handling. Audio input is PCM16 at 16kHz mono; output is PCM at 24kHz. The model can detect user emotions from voice tone and respond with appropriate emotional expression. Multiple voice presets are available with different personalities and speaking styles. This is used exclusively through the Live API (WebSocket). Native audio processing is a significant differentiator - OpenAI's Realtime API offers similar capabilities, but Gemini's affective dialog and emotional awareness are more advanced.

## Key Facts

- [VERIFIED] Model: `gemini-2.5-flash-native-audio-preview` (GEMAPI-SC-GOOG-LIVAUD)
- [VERIFIED] Native audio processing (not text-to-speech conversion) (GEMAPI-SC-GOOG-LIVAUD)
- [VERIFIED] Affective dialog: emotional awareness and expression (GEMAPI-SC-GOOG-LIVAUD)
- [VERIFIED] Barge-in support with graceful interruption handling (GEMAPI-SC-GOOG-LIVAUD)
- [VERIFIED] Non-verbal understanding: sighs, laughter, pauses (GEMAPI-SC-GOOG-LIVAUD)
- [VERIFIED] Multiple voice presets (GEMAPI-SC-GOOG-LIVAUD)
- [VERIFIED] Live API only (WebSocket) (GEMAPI-SC-GOOG-LIVAUD)

## Use Cases

- **Empathetic voice agents**: Customer service with emotional awareness
- **Natural conversations**: Casual dialog with natural prosody and timing
- **Accessibility**: Voice interfaces with emotional context
- **Entertainment**: Character voices with personality and emotion

## Quick Reference

**Model**: `gemini-2.5-flash-native-audio-preview`
**Input**: PCM16, 16kHz mono
**Output**: PCM, 24kHz
**Interface**: Live API (WebSocket) only

## Voice Presets

Available voice presets include:
- **Puck** - Playful, energetic
- **Charon** - Deep, authoritative
- **Kore** - Warm, friendly
- **Fenrir** - Bold, dynamic
- **Aoede** - Clear, melodic

## Python Examples

### Example 1: Affective Voice Conversation

```python
import asyncio
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

async def affective_chat():
    async with client.aio.live.connect(
        model="gemini-2.5-flash-native-audio-preview",
        config=types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"
                    )
                )
            ),
            system_instruction=types.Content(
                parts=[types.Part(text="You are an empathetic voice assistant. Match the emotional tone of the user.")]
            ),
        )
    ) as session:
        # Send text (model responds with native audio)
        await session.send(
            input="I just got promoted at work! I'm so excited!",
            end_of_turn=True
        )

        async for msg in session.receive():
            if msg.data:
                # Audio response with matching enthusiasm
                print(f"Audio chunk: {len(msg.data)} bytes")
            if msg.server_content and msg.server_content.turn_complete:
                break

asyncio.run(affective_chat())
```

## Comparison with Other APIs

### vs OpenAI

- **Native audio**: Gemini: native audio model | OpenAI: GPT-4o Realtime (also native)
- **Affective dialog**: Gemini: explicit emotional awareness | OpenAI: natural but less explicit
- **Barge-in**: Both support interruption
- **Voice presets**: Both offer multiple voices
- **Non-verbal**: Gemini: explicit non-verbal understanding | OpenAI: implicit

### vs Anthropic

- **Native audio**: Gemini: yes | Anthropic: **no real-time audio**
- **UNIQUE advantage**: Anthropic has no audio conversation capability

## Error Responses

- WebSocket close on audio processing errors
- Model may not respond to very low quality audio input

## Rate Limiting / Throttling

Preview model has restricted concurrent session limits. See GEMAPI-IN04.

## Limitations and Known Issues

- [VERIFIED] Preview status - API may change (GEMAPI-SC-GOOG-MODELS)
- Live API only - cannot use native audio via REST
- Audio quality depends heavily on input microphone quality

## Gotchas and Quirks

- Input PCM16 at 16kHz but output PCM at 24kHz - different sample rates
- Affective dialog means the model detects AND expresses emotions - can be surprising
- Barge-in cancels current model output - partial audio may be lost
- Native audio model is different from TTS models - processes audio end-to-end
- Cannot save/replay native audio sessions (no built-in recording)

## Sources

- GEMAPI-SC-GOOG-LIVAUD: https://ai.google.dev/gemini-api/docs/live-audio [VERIFIED]
- GEMAPI-SC-GOOG-LIVAPI: https://ai.google.dev/gemini-api/docs/live [VERIFIED]

## Document History

**[2026-03-20 05:25]**
- Initial document created
