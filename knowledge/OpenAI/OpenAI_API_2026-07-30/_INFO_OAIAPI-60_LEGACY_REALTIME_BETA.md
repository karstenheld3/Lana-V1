# Realtime API Beta (Legacy) [REMOVED 2026-05-12]

**Doc ID**: OAIAPI-IN60
**Goal**: Document the removed Realtime API beta and migration to GA Realtime API
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN39_REALTIME_OVERVIEW.md [OAIAPI-IN39]` for current Realtime API

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Realtime API beta was the initial preview of OpenAI's WebSocket-based real-time audio/text streaming. Originally launched with `gpt-4o-realtime-preview` models, it provided bidirectional audio streaming, VAD, and function calling. The beta evolved through several model snapshots before GA with `gpt-realtime` and `gpt-realtime-2` models. **REMOVED 2026-05-12** - all beta endpoints are offline. Key additions from beta to GA: MCP tool support, DTMF detection, Calls API (SIP), transcription sessions, improved audio codecs, enhanced VAD, client secrets. [VERIFIED] (OAIAPI-SC-OAI-GRTAPI, OAIAPI-SC-OAI-LGRTBM)

## Key Facts

- **Status**: REMOVED 2026-05-12 [VERIFIED] (OAIAPI-SC-OAI-LGRTBM)
- **Beta models**: gpt-4o-realtime-preview, dated snapshots [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)
- **GA models**: gpt-realtime, gpt-realtime-2 [VERIFIED] (OAIAPI-SC-OAI-RTSREV)
- **GA additions**: MCP, DTMF, Calls API, transcription sessions, client secrets [VERIFIED] (OAIAPI-SC-OAI-RTSREV)

## Evolution: Beta to GA

### Beta (2024)
- Models: `gpt-4o-realtime-preview`
- Events: Core session, audio buffer, conversation, response events
- VAD: Basic server_vad
- Audio: pcm16 only initially
- Auth: API key only

### GA (2025-2026)
- Models: `gpt-realtime`, `gpt-realtime-2`, dated variants
- Events: Added MCP events, DTMF, transcription delta/segment events
- VAD: Enhanced with prefix_padding_ms, timeout_triggered
- Audio: pcm16, g711_ulaw, g711_alaw
- Auth: API key + client secrets (ephemeral tokens)
- New features: Calls API, SIP integration, transcription sessions

## Migration

### Model Update

```python
# Before (beta)
url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"

# After (GA)
url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2"
```

### Client Secrets (GA)

```python
from openai import OpenAI
client = OpenAI()

response = client.realtime.client_secrets.create(
    session={
        "model": "gpt-realtime-2",
        "voice": "alloy"
    }
)
# Send response.client_secret.value to frontend
```

### Session Config Changes

Most session configuration is backwards-compatible. New fields added in GA:
- `input_audio_transcription.model` - Specify transcription model
- MCP server configuration in tools
- Enhanced turn_detection options

## Differences from Other APIs

- **vs Current GA**: Beta was subset of GA. All beta events worked in GA
- **vs Anthropic**: No realtime audio API at any stage
- **vs Gemini Live**: Gemini launched Live API (BidiGenerateContent) with similar timeline

## Limitations and Known Issues

- **Removed**: Beta endpoints are fully offline since 2026-05-12 [VERIFIED] (OAIAPI-SC-OAI-LGRTBM)
- **Preview model deprecation**: gpt-4o-realtime-preview snapshots are deprecated [VERIFIED] (OAIAPI-SC-OAI-GRTAPI)

## TypeScript Examples

### Basic Chat Completion

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const completion = await client.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Hello!" },
  ],
});

console.log(completion.choices[0].message.content);
```

### Streaming

```typescript
const stream = await client.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [{ role: "user", content: "Count to 5." }],
  stream: true,
});

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content;
  if (content) process.stdout.write(content);
}
```

## Sources

- OAIAPI-SC-OAI-GRTAPI - Realtime API Guide
- OAIAPI-SC-OAI-RTSREV - Server events reference
- OAIAPI-SC-OAI-LGRTBM - Legacy Realtime Beta Reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:45]**
- Enriched from 2026-03-20 IN60 (19 -> 100 lines)
- Updated GA model refs to gpt-realtime-2, status to REMOVED

**[2026-05-22 11:50]**
- Stub created
