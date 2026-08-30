# Video Generation

**Doc ID**: OAIAPI-IN23
**Goal**: Document Videos API, Sora models, edit/extend/remix, deprecation
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Video generation via `POST /v1/videos` using Sora models. 2026-03 expanded with character references, 20-second generations, 1080p for sora-2-pro ($0.70/s), video extensions, and Batch API support. New `POST /v1/videos/edits` endpoint replaces `POST /v1/videos/{id}/remix` (deprecated). **CRITICAL**: All Sora 2 models (sora-2, sora-2-pro, snapshots) were deprecated 2026-03-24 and will be **shut down 2026-09-24**. [VERIFIED] (OAIAPI-SC-OAI-VIDCRT, OAIAPI-SC-OAI-GVIDEO, OAIAPI-SC-OAI-GDEPR)

## Key Facts

- **Models**: sora-2, sora-2-pro (deprecated 2026-03-24; shutdown 2026-09-24) [VERIFIED]
- **Max duration**: 20 seconds (sora-2-pro) [VERIFIED]
- **Max resolution**: 1080p (sora-2-pro, $0.70/second) [VERIFIED]
- **Character references**: Upload character images for consistent characters across videos [VERIFIED]
- **Batch support**: Videos can be created via Batch API at 50% discount [VERIFIED]
- **Edit endpoint**: `POST /v1/videos/edits` replaces deprecated remix [VERIFIED]

## Use Cases

- **Content creation**: Generate video clips from text prompts
- **Video editing**: Edit/extend existing videos with new content
- **Character consistency**: Use character references across multiple generations
- **Batch video**: Generate many videos at 50% cost via Batch API

## REST API

### Endpoints

- **Create video**: `POST /v1/videos`
- **Edit video**: `POST /v1/videos/edits` (NEW - replaces remix)
- **Extend video**: `POST /v1/videos/{id}/extend`
- **Remix**: `POST /v1/videos/{id}/remix` (DEPRECATED - 6 month sunset)
- **Characters**: `POST /v1/videos/characters`, `GET /v1/videos/characters/{id}`
- **Retrieve**: `GET /v1/videos/{id}`
- **Delete**: `DELETE /v1/videos/{id}`
- **List**: `GET /v1/videos`
- **Download**: `GET /v1/videos/{id}/download`

### Create Video Request

```json
{
  "model": "sora-2-pro",
  "prompt": "A golden retriever playing in autumn leaves, cinematic lighting",
  "seconds": 10,
  "size": "1080p"
}
```

**Parameters:**
- **model** (string, required) - `sora-2` or `sora-2-pro`
- **prompt** (string, required) - Text description of video
- **seconds** (integer, optional) - Duration: 5, 10, 15, 20 (max depends on model)
- **size** (string, optional) - Resolution: `480p`, `720p`, `1080p`
- **character_ids** (array, optional) - Character reference IDs for consistency

### Video Edit Request

```json
{
  "model": "sora-2-pro",
  "video_id": "video_abc123",
  "prompt": "Change the background to a snowy landscape",
  "seconds": 10
}
```

## Pricing

- **sora-2**: $0.20/second (720p), $0.35/second (1080p)
- **sora-2-pro**: $0.40/second (720p), $0.70/second (1080p)
- **Batch**: 50% discount on all pricing

## SDK Examples (Python)

### Create Video (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/videos.py
# IMPORTANT: SDK uses "seconds" (not "duration") and "size" (not "resolution")
from openai import OpenAI

client = OpenAI()

video = client.videos.create(
    model="sora-2-pro",
    prompt="A golden retriever playing in autumn leaves, cinematic lighting",
    seconds=10,
    size="1080p",
)
print(f"Video: {video.id}, Status: {video.status}")
```

### Poll Until Complete and Download

```python
from openai import OpenAI
import time

client = OpenAI()

video = client.videos.create(
    model="sora-2-pro",
    prompt="Ocean waves crashing on rocky coast at sunset",
    seconds=5,
    size="720p",
)

# Poll status
while video.status not in ("completed", "failed"):
    time.sleep(10)
    video = client.videos.retrieve(video.id)
    print(f"Status: {video.status}")

if video.status == "completed":
    # Download video
    content = client.videos.download(video.id)
    with open("output.mp4", "wb") as f:
        f.write(content)
    print("Video saved to output.mp4")
```

### Edit Video (Replaces Remix)

```python
from openai import OpenAI

client = OpenAI()

edited = client.videos.edits.create(
    model="sora-2-pro",
    video_id="video_abc123",
    prompt="Change season to winter with falling snow",
    seconds=10,
)
print(f"Edit: {edited.id}, Status: {edited.status}")
```

### Extend Video

```python
from openai import OpenAI

client = OpenAI()

extended = client.videos.extend(
    video_id="video_abc123",
    seconds=10,  # Extend by 10 additional seconds
    prompt="Continue the scene with the dog catching a frisbee",
)
print(f"Extended: {extended.id}")
```

### Character References

```python
from openai import OpenAI

client = OpenAI()

# Create character from reference image
character = client.videos.characters.create(
    name="hero_character",
    image=open("character_ref.png", "rb"),
)

# Use character in video
video = client.videos.create(
    model="sora-2-pro",
    prompt="The character walks through a futuristic city",
    seconds=10,
    character_ids=[character.id],
)
```

## Deprecation Notice

**CRITICAL**: All Sora 2 models deprecated 2026-03-24:
- `sora-2` - shutdown 2026-09-24
- `sora-2-pro` - shutdown 2026-09-24
- All dated snapshots (sora-2-*) - same shutdown date

No replacement announced at time of writing. Migrate workloads before 2026-09.

## Limitations and Known Issues

- **Generation time**: Videos take 30s-5min depending on duration and resolution [COMMUNITY]
- **Prompt adherence**: Complex multi-action prompts may not render perfectly [COMMUNITY]
- **Character consistency**: Works best with front-facing, well-lit reference images [VERIFIED]

## Gotchas and Quirks

- **SDK param names**: Use `seconds` not `duration`, `size` not `resolution` [TESTED] (SDK v2.45.0)
- **Sora 2 deprecated**: All models shutdown 2026-09-24 [VERIFIED]
- **POST /v1/videos/edits**: New endpoint, replaces `POST /v1/videos/{id}/remix` [VERIFIED]
- **1080p only sora-2-pro**: Standard sora-2 maxes at 720p [VERIFIED]
- **Batch support**: Videos via Batch API get 50% discount [VERIFIED]

## TypeScript Examples

### Generate Image

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const result = await client.images.generate({
  model: "gpt-image-1",
  prompt: "A serene landscape with mountains",
  size: "1024x1024",
  n: 1,
});

console.log(result.data[0].b64_json ? "Got base64 image" : result.data[0].url);
```

## Sources

- OAIAPI-SC-OAI-VIDCRT - POST Create video
- OAIAPI-SC-OAI-GVIDEO - Video generation guide
- OAIAPI-SC-OAI-GDEPR - Deprecations

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Full REST API, pricing, SDK examples (poll, edit, extend, characters), deprecation notice

**[2026-05-22 11:30]**
- Added: POST /v1/videos/edits, Sora deprecation, 1080p/20s, Batch support
