# INFO: Deferred Chat Completions

**Doc ID**: GROKAPI-IN35
**Goal**: Async deferred completions, polling, request lifecycle, use cases
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Deferred Chat Completions is a **UNIQUE Grok feature** (no direct equivalent in OpenAI, Anthropic, or Gemini APIs) that enables asynchronous request processing. Instead of waiting for a synchronous response, the API returns HTTP 202 Accepted with a `request_id`. The client polls `GET /v1/chat/deferred-completion/{request_id}` until the response is ready. This is useful for long-running requests (especially with reasoning models) where HTTP timeouts might be an issue, or for fire-and-forget patterns. Different from the Batch API which processes JSONL files - deferred completions handle individual requests asynchronously. [VERIFIED] (GROKAPI-SC-XAI-DEFERRED | https://docs.x.ai/developers/advanced-api-usage/deferred-chat-completions)

## Key Facts

- [VERIFIED] Returns HTTP 202 Accepted with request_id (GROKAPI-SC-XAI-ERRORS)
- [VERIFIED] Poll endpoint: `GET /v1/chat/deferred-completion/{request_id}` (GROKAPI-SC-XAI-ERRORS)
- [VERIFIED] Useful for long-running reasoning model requests (GROKAPI-SC-XAI-DEFERRED)

## Quick Reference

- **Submit**: `POST /v1/chat/deferred-completion`
- **Poll**: `GET /v1/chat/deferred-completion/{request_id}`
- **Response on submit**: HTTP 202 with `request_id`
- **Response on poll**: HTTP 200 with completion or HTTP 202 if still processing

## Examples

### Deferred Completion (cURL)

```bash
# Step 1: Submit deferred request
REQUEST_ID=$(curl -s https://api.x.ai/v1/chat/deferred-completion \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4.20-beta-latest-non-reasoning",
    "messages": [
      {"role": "user", "content": "Write a detailed analysis of quantum computing applications."}
    ]
  }' | jq -r '.request_id')

echo "Request ID: $REQUEST_ID"

# Step 2: Poll until ready
while true; do
  RESULT=$(curl -s -w "\n%{http_code}" \
    "https://api.x.ai/v1/chat/deferred-completion/$REQUEST_ID" \
    -H "Authorization: Bearer $XAI_API_KEY")
  
  STATUS=$(echo "$RESULT" | tail -1)
  if [ "$STATUS" = "200" ]; then
    echo "$RESULT" | head -n -1
    break
  fi
  echo "Still processing..."
  sleep 5
done
```

## Use Cases

- **Long reasoning tasks**: Avoid HTTP timeout on complex reasoning
- **Fire-and-forget**: Submit request and check back later
- **Queue management**: Submit multiple requests and poll results

## Differences from Other APIs

### vs OpenAI
- **UNIQUE**: OpenAI has no deferred completion endpoint (uses streaming or Batch API)

### vs Anthropic
- **UNIQUE**: Anthropic has no deferred completion (uses streaming or Message Batches)

### vs Gemini
- **UNIQUE**: Gemini has no deferred completion endpoint

### vs Grok Batch API
- **Individual requests**: Deferred is for single requests; Batch is for bulk JSONL
- **Lower latency**: Deferred processes immediately; Batch may queue

## Sources

- GROKAPI-SC-XAI-DEFERRED | https://docs.x.ai/developers/advanced-api-usage/deferred-chat-completions | Accessed: 2026-03-20
- GROKAPI-SC-XAI-ERRORS | https://docs.x.ai/developers/debugging-errors | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:45]**
- Initial document created with deferred completions reference
