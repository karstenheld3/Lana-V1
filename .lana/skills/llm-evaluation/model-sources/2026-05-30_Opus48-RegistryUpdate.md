# Registry Update: Claude Opus 4.8

**Date**: 2026-05-30
**Model**: Claude Opus 4.8
**Released**: 2026-05-28
**Model ID**: `claude-opus-4-8` (dateless canonical ID, 4.6+ convention)

## Sources

- Announcement: https://www.anthropic.com/news/claude-opus-4-8
- Models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Model IDs: https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions
- Effort docs: https://platform.claude.com/docs/en/build-with-claude/effort
- Pricing: https://platform.claude.com/docs/en/about-claude/pricing

## Pricing (Standard, unchanged from Opus 4.7)

- Input: $5.00 / 1M tokens
- Cached input: $0.50 / 1M tokens
- Output: $25.00 / 1M tokens
- Batch input: $2.50 / 1M tokens
- Batch output: $12.50 / 1M tokens
- Fast mode: $10 / $50 (1.1x for US-only inference)

## Model Parameters

- Context window: 1,000,000 tokens (200k on Microsoft Foundry)
- Max output: 128,000 tokens (sync), 300k (batch with `output-300k-2026-03-24` beta header)
- Method: `adaptive_thinking` (same as Opus 4.7)
- Effort levels: `low`, `medium`, `high`, `xhigh`, `max`
- Default effort: `high` on all surfaces (API, Claude Code)

## API Changes Launched Alongside Opus 4.8

- **Mid-conversation system messages**: Messages API accepts `system` entries inside the `messages` array for mid-task instruction updates without breaking prompt cache.
- **Manual extended thinking removed**: `thinking: {type: "enabled", budget_tokens: N}` returns 400 error on Opus 4.8. Must use `thinking: {type: "adaptive"}`.
- **Dynamic workflows**: Claude Code feature (not API-level), allows hundreds of parallel subagents.

## Registry Changes Applied

- `model-registry.json` v1.5.0 -> v1.6.0
  - Added `claude-opus-4-8` to models array (status: untested)
  - Added `claude-opus-4-8` prefix to `model_id_startswith` with effort `["low", "medium", "high", "xhigh", "max"]`
  - Fixed `claude-opus-4-7` prefix: added missing `xhigh` to effort array
- `model-pricing.json` updated 2026-05-22 -> 2026-05-30
  - Added `claude-opus-4-8` pricing entry ($5/$0.50/$25, 1000k context)
- `model-parameter-mapping.json` updated 2026-05-22 -> 2026-05-30
  - No structural changes (effort mapping already covers xhigh -> anthropic_adaptive_effort: "max")
- `LLM_EVALUATION_CLAUDE_MODELS.md` updated
  - Added Opus 4.8 to verified model IDs
  - Renamed family section to "4.6 / 4.7 / 4.8 Family"
