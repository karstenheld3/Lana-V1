# INFO: Gemini API Live Video (Screen Sharing and Camera Input)

**Doc ID**: GEMAPI-IN34
**Goal**: Document real-time video/screen input via Live API for visual understanding agents
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

The Gemini Live API supports real-time video input by accepting JPEG frames sent as `realtimeInput` media chunks over the WebSocket connection. This enables use cases like screen sharing analysis, camera-based visual assistance, live video monitoring, and interactive visual tutoring. Video frames are sent at a configurable rate (typically 1-5 FPS) as base64-encoded JPEG images. The model processes frames in context with audio/text input, enabling multimodal real-time interaction ("What am I looking at?" while pointing a camera). This capability is unique to Gemini's Live API - OpenAI's Realtime API does not support video input, and Anthropic has no real-time API.

## Key Facts

- [VERIFIED] Video frames sent as JPEG via realtimeInput media chunks (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] Combined with audio/text for multimodal real-time interaction (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] Recommended 1-5 FPS for practical use (GEMAPI-SC-GOOG-LIVAPI)
- [VERIFIED] UNIQUE to Gemini - OpenAI Realtime has no video input (GEMAPI-SC-GOOG-LIVAPI)

## Use Cases

- **Screen sharing assistant**: Real-time help while viewing user's screen
- **Camera-based visual aid**: Point camera at objects for identification/description
- **Live monitoring**: Security camera or process monitoring with alerts
- **Interactive tutoring**: Watch student work and provide real-time feedback
- **Accessibility**: Describe surroundings for visually impaired users

## Quick Reference

**Frame format**: JPEG (base64-encoded)
**Send rate**: 1-5 FPS recommended
**Interface**: Live API WebSocket only
**Combined with**: Audio and/or text simultaneously

## Video Frame Input

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

## Python Examples

### Example 1: Screen Sharing Analysis

```python
import asyncio
import base64
from google import genai
from google.genai import types
from PIL import ImageGrab
import io
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def capture_screen_jpeg():
    screenshot = ImageGrab.grab()
    screenshot = screenshot.resize((1024, 768))  # Reduce size for efficiency
    buffer = io.BytesIO()
    screenshot.save(buffer, format="JPEG", quality=60)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

async def screen_assistant():
    async with client.aio.live.connect(
        model="gemini-2.5-flash",
        config=types.LiveConnectConfig(
            response_modalities=["TEXT"],
            system_instruction=types.Content(
                parts=[types.Part(text="You are a screen sharing assistant. Describe what you see and help the user.")]
            ),
        )
    ) as session:
        # Send a screen frame
        frame_data = capture_screen_jpeg()
        await session.send(
            input=types.LiveClientRealtimeInput(
                media_chunks=[types.Blob(
                    mime_type="image/jpeg",
                    data=frame_data
                )]
            )
        )

        # Ask about what's on screen
        await session.send(input="What application am I using?", end_of_turn=True)

        async for msg in session.receive():
            if msg.text:
                print(msg.text, end="")
            if msg.server_content and msg.server_content.turn_complete:
                break
        print()

asyncio.run(screen_assistant())
```

### Example 2: Camera Feed with Voice

```python
import asyncio
import base64
import cv2
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def capture_camera_frame():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return base64.b64encode(buffer).decode("utf-8")
    return None

async def visual_assistant():
    async with client.aio.live.connect(
        model="gemini-2.5-flash",
        config=types.LiveConnectConfig(
            response_modalities=["TEXT", "AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                )
            ),
        )
    ) as session:
        frame = capture_camera_frame()
        if frame:
            await session.send(
                input=types.LiveClientRealtimeInput(
                    media_chunks=[types.Blob(mime_type="image/jpeg", data=frame)]
                )
            )
            await session.send(input="What do you see?", end_of_turn=True)

            async for msg in session.receive():
                if msg.text:
                    print(msg.text, end="")
                if msg.server_content and msg.server_content.turn_complete:
                    break

asyncio.run(visual_assistant())
```

## Comparison with Other APIs

### vs OpenAI

- **Live video input**: Gemini: yes (JPEG frames via WebSocket) | OpenAI: **no video in Realtime API**
- **UNIQUE to Gemini**: Real-time video input is a major differentiator

### vs Anthropic

- **Live video input**: Gemini: yes | Anthropic: **no real-time API at all**

## Error Responses

- Large frames may cause latency or be rejected
- Too-frequent frames may overwhelm the connection

## Rate Limiting / Throttling

Live API session limits apply. Video frames consume significant bandwidth. See GEMAPI-IN04.

## Limitations and Known Issues

- Higher FPS = more tokens consumed = higher cost
- Large resolution frames increase latency
- No built-in recording of video sessions

## Gotchas and Quirks

- Reduce frame resolution and JPEG quality for efficiency (1024x768 at quality 60 is sufficient)
- 1-5 FPS is practical; higher rates waste tokens without much benefit
- Video frames are processed as images - not true video encoding
- Model sees individual frames, not motion - rapid changes may be missed between frames
- Combine video frames with audio for natural multimodal interaction

## Sources

- GEMAPI-SC-GOOG-LIVAPI: https://ai.google.dev/gemini-api/docs/live [VERIFIED]
- GEMAPI-SC-GOOG-LIVREF: https://ai.google.dev/api/live [VERIFIED]

## Document History

**[2026-03-20 05:30]**
- Initial document created
