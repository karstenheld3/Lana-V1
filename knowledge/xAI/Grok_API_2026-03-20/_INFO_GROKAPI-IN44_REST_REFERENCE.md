# INFO: REST API Reference

**Doc ID**: GROKAPI-IN44
**Goal**: Complete endpoint listing, request/response schemas, OpenAI compatibility layer
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok REST API is OpenAI-compatible, using `https://api.x.ai/v1` as the base URL. All endpoints accept JSON with `Authorization: Bearer` header. The API provides endpoints for text generation (Chat Completions, Responses), image generation/editing, video generation, audio (TTS, Voice Agent), files, collections, batches, embeddings, and deferred completions. The Management API at `https://management-api.x.ai` handles team and key management separately. Full API reference available at `https://docs.x.ai/developers/rest-api-reference`. [VERIFIED] (GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/developers/rest-api-reference)

## Endpoint Catalog

### Text Generation
- `POST /v1/chat/completions` - Chat Completions (legacy)
- `POST /v1/responses` - Responses API (recommended)
- `GET /v1/responses/{response_id}` - Retrieve stored response
- `DELETE /v1/responses/{response_id}` - Delete stored response

### Deferred Completions
- `POST /v1/chat/deferred-completion` - Submit async request
- `GET /v1/chat/deferred-completion/{request_id}` - Poll result

### Images
- `POST /v1/images/generations` - Generate images
- `POST /v1/images/edits` - Edit images

### Video
- `POST /v1/videos/generations` - Start video generation
- `GET /v1/videos/{request_id}` - Poll video status

### Audio
- `POST /v1/audio/speech` - Text to speech
- `WSS /v1/realtime` - Voice Agent (WebSocket)

### Files
- `POST /v1/files` - Upload file
- `GET /v1/files` - List files
- `GET /v1/files/{file_id}` - Get file metadata
- `GET /v1/files/{file_id}/content` - Get file content
- `DELETE /v1/files/{file_id}` - Delete file

### Collections
- `POST /v1/collections` - Create collection
- `GET /v1/collections` - List collections
- `GET /v1/collections/{id}` - Get collection
- `PUT /v1/collections/{id}` - Update collection
- `DELETE /v1/collections/{id}` - Delete collection
- `POST /v1/collections/{id}/files` - Upload to collection
- `GET /v1/collections/{id}/files` - List collection files
- `DELETE /v1/collections/{id}/files/{file_id}` - Delete collection file

### Batches
- `POST /v1/batches` - Create batch
- `GET /v1/batches` - List batches
- `GET /v1/batches/{batch_id}` - Get batch status
- `POST /v1/batches/{batch_id}/cancel` - Cancel batch

### Models
- `GET /v1/models` - List available models
- `GET /v1/models/{model_id}` - Get model details

### Embeddings
- `POST /v1/embeddings` - Generate embeddings

### Management API (https://management-api.x.ai)
- `POST /auth/teams/{teamId}/api-keys` - Create API key
- `GET /auth/teams/{teamId}/api-keys` - List keys
- `PUT /auth/teams/{teamId}/api-keys/{keyId}` - Update key
- `DELETE /auth/teams/{teamId}/api-keys/{keyId}` - Delete key

## Common Request Headers

- `Authorization: Bearer $XAI_API_KEY` (required)
- `Content-Type: application/json` (required for JSON body)
- `x-grok-conv-id: <conversation_id>` (optional, for prompt caching)

## Common Response Fields

- `id` - Request/response identifier
- `object` - Object type (e.g., `chat.completion`, `response`)
- `model` - Model used (resolved from alias)
- `usage` - Token usage breakdown
- `system_fingerprint` - Backend configuration identifier

## OpenAI Compatibility

The API is designed to be a drop-in replacement for OpenAI's API. Change only:
```python
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),  # xAI key instead of OpenAI key
    base_url="https://api.x.ai/v1",    # xAI base URL
)
```

All standard OpenAI SDK methods work: `chat.completions.create()`, `responses.create()`, `images.generate()`, `audio.speech.create()`, `files.create()`, `batches.create()`.

## Differences from Other APIs

### vs OpenAI
- **Compatible**: Most endpoints match OpenAI's format
- **Additional**: Deferred completions, video generation, collections, Management API
- **Server-side tools**: Built-in web_search, x_search, code_execution in standard endpoints

### vs Anthropic
- **Different format**: Anthropic uses `/v1/messages` with different request/response structure
- **Not compatible**: Cannot use Anthropic SDK with xAI (use OpenAI SDK)

### vs Gemini
- **Different format**: Gemini uses `generateContent` with different structure
- **Not compatible**: Cannot use Gemini SDK with xAI

## Sources

- GROKAPI-SC-XAI-RESTREF | https://docs.x.ai/developers/rest-api-reference | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:45]**
- Initial document created with complete endpoint catalog
