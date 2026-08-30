# INFO: Best Practices

**Doc ID**: GROKAPI-IN38
**Goal**: Production patterns, error handling, retry strategies, cost optimization, security
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Best practices for production use of the Grok API covering error handling, retry strategies, cost optimization, and security. Key recommendations: implement exponential backoff with jitter for 429/5xx errors, use streaming for long-running requests to avoid timeouts, leverage prompt caching (`x-grok-conv-id` or `prompt_cache_key`) to reduce costs, choose appropriate models (non-reasoning for simple tasks, reasoning for complex analysis), monitor `server_side_tool_usage` for tool cost tracking, use `store: false` when response storage is not needed, and secure API keys via environment variables. For production reliability: set reasonable `max_tokens`, implement request timeouts, use deferred completions for very long tasks, and monitor rate limit headers. [VERIFIED] (GROKAPI-SC-XAI-BESTPRAC | https://docs.x.ai/developers/best-practices)

## Key Recommendations

### Error Handling
- Implement exponential backoff with jitter for 429 (rate limit) and 5xx errors
- Use `try/except` with SDK-specific error classes (`RateLimitError`, `APIError`)
- Log error details including request ID for debugging

### Cost Optimization
- Use prompt caching: `x-grok-conv-id` (Chat Completions) or `prompt_cache_key` (Responses API)
- Choose non-reasoning models for simple tasks (cheaper, faster)
- Use `store: false` when you don't need server-side response storage
- Monitor `server_side_tool_usage` to track tool invocation costs
- Use Batch API for non-time-sensitive bulk workloads (discounted pricing)
- Set appropriate `max_tokens` to avoid over-generation

### Reliability
- Use streaming for long-running requests to avoid HTTP timeouts
- Use deferred completions for very long reasoning tasks
- Implement request-level timeouts in your client
- Handle 202 Accepted responses (deferred completions)

### Security
- Store API keys in environment variables, never in code
- Use Management API ACLs to restrict key permissions
- Rotate API keys regularly
- Use `api-key:model:*` and `api-key:endpoint:*` ACLs for fine-grained control

### Model Selection
- **Simple tasks**: `grok-4.20-beta-latest-non-reasoning` (fast, cheap)
- **Complex reasoning**: `grok-3-mini` with `reasoning.effort` parameter
- **Multi-agent research**: `grok-4.20-multi-agent` (4 or 16 agents)
- **Vision**: Models with vision capability for image understanding
- **Cost-sensitive**: Use `-fast` model variants when available

## Differences from Other APIs

### vs OpenAI
- **Deferred completions**: Unique fallback for timeout-prone requests
- **Server-side tools**: Monitor `server_side_tool_usage` for cost tracking (no OpenAI equivalent)
- **Management API**: ACL-based key management (OpenAI uses project-level keys)

### vs Anthropic
- **Caching**: Automatic vs explicit `cache_control` blocks
- **Rate limits**: Spend-based tiers vs usage-based tiers

## Sources

- GROKAPI-SC-XAI-BESTPRAC | https://docs.x.ai/developers/best-practices | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:25]**
- Initial document created with production best practices
