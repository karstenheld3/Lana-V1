# INFO: Audio Capabilities Overview

**Doc ID**: GROKAPI-IN25
**Goal**: Audio API overview - Voice Agent (realtime), TTS, audio formats, pricing summary
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API offers two audio capabilities: the Voice Agent API for real-time bidirectional voice conversations over WebSocket, and the Text to Speech (TTS) API for converting text to speech. Both are production-ready with separate pricing models. Voice Agent is billed per-minute ($0.05/min), TTS per-character ($4.20/1M chars). Both support up to 100 concurrent sessions/requests per team. Rate limit increases for audio APIs require manual email request (not covered by automatic tier system). [VERIFIED] (GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models)

## Key Facts

- [VERIFIED] Two audio APIs: Voice Agent (realtime) and TTS (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Voice Agent: $0.05/min, 100 concurrent, 30 min max, WebSocket (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] TTS: $4.20/1M chars, 100 concurrent, MP3/WAV/PCM/mu-law/A-law (GROKAPI-SC-XAI-MODELS)
- [VERIFIED] Rate limits for audio APIs require email request for increases (GROKAPI-SC-XAI-RATELIMITS)

## Quick Reference

### Voice Agent API (Realtime)
- **Protocol**: WebSocket (`wss://api.x.ai/v1/realtime`)
- **Pricing**: $0.05/min ($3.00/hr) + tool costs
- **Max concurrent**: 100 per team
- **Max duration**: 30 minutes
- **Tools**: web_search, x_search, collections, MCP, function calling
- **Details**: See `_INFO_GROKAPI-IN26_VOICE_AGENT.md [GROKAPI-IN26]`

### Text to Speech API
- **Endpoint**: `POST /v1/audio/speech`
- **Pricing**: $4.20/1M characters
- **Max concurrent**: 100 per team
- **Formats**: MP3, WAV, PCM, mu-law, A-law
- **Details**: See `_INFO_GROKAPI-IN27_TEXT_TO_SPEECH.md [GROKAPI-IN27]`

## Differences from Other APIs

### vs OpenAI
- **Voice Agent**: Similar to OpenAI Realtime API (WebSocket-based)
- **TTS**: Compatible endpoint format (`POST /v1/audio/speech`)
- **Pricing advantage**: xAI TTS $4.20/1M chars vs OpenAI $15-30/1M chars
- **Tools in voice**: xAI supports server-side tools (web_search, x_search) in voice sessions

### vs Anthropic
- **UNIQUE**: Anthropic has no audio APIs (no voice, no TTS)

### vs Gemini
- **Voice**: Gemini has Live API for realtime audio (different protocol)
- **TTS**: Gemini has TTS as part of multimodal output (different approach)

## Sources

- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:20]**
- Initial document created with audio capabilities overview
