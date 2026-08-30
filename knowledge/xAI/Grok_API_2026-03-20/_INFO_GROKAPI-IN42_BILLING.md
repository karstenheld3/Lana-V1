# INFO: Billing and Pricing

**Doc ID**: GROKAPI-IN42
**Goal**: Pricing model, token costs, tool costs, media costs, billing dashboard
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Grok API billing has multiple components: token-based pricing (input, output, cached, reasoning, image tokens), per-invocation tool costs, per-second media generation costs, per-minute voice costs, and per-character TTS costs. Billing is tracked via the xAI Console. Prepaid credits system with automatic top-up. Rate limit tiers advance based on cumulative spend ($0, $50, $100, $500, $1000 thresholds). Token costs vary by model - see Models page for current pricing. Cached prompt tokens are discounted (~25% of regular rate). Reasoning tokens are billed at output token rates. [VERIFIED] (GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models)

## Pricing Components

### Token Costs (per model)
- **Input tokens**: Standard per-model rate
- **Output tokens**: Standard per-model rate (typically higher than input)
- **Cached tokens**: ~25% of input token rate
- **Reasoning tokens**: Billed at output token rate
- **Image tokens**: Based on resolution and detail level

### Tool Invocation Costs (per 1K invocations)
- **web_search**: $5
- **x_search**: $5
- **code_execution / code_interpreter**: $5
- **attachment_search**: $10
- **collections_search / file_search**: $2.50
- **view_image**: Token-based only (no invocation fee)
- **view_x_video**: Token-based only (no invocation fee)
- **Remote MCP**: Token-based only (no invocation fee)

### Media Costs
- **Video generation**: Per-second pricing (model-dependent)
- **Image generation**: Per-image pricing (model-dependent)

### Audio Costs
- **Voice Agent**: $0.05/minute ($3.00/hour)
- **TTS**: $4.20 per 1M characters

### Billing Notes
- Only successful tool executions are billed (failed attempts free)
- Batch API requests at discounted rates
- Cached tokens automatically discounted

## Differences from Other APIs

### vs OpenAI
- **Similar structure**: Token-based + tool costs
- **Tool pricing**: xAI has explicit per-invocation pricing; OpenAI bundles differently
- **TTS pricing**: xAI $4.20/1M chars vs OpenAI $15-30/1M chars
- **Spend-based tiers**: xAI advances tiers by cumulative spend; OpenAI by usage history

### vs Anthropic
- **Simpler tools**: Anthropic has no tool invocation costs (all token-based)
- **No media**: Anthropic has no image/video/audio generation costs
- **Caching**: Different discount structures

## Sources

- GROKAPI-SC-XAI-MODELS | https://docs.x.ai/developers/models | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:35]**
- Initial document created with comprehensive billing reference
