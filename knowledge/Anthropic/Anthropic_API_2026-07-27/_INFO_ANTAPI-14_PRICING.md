# Pricing and Model Selection

**Doc ID**: ANTAPI-IN14
**Goal**: Document token pricing, feature-specific pricing multipliers, and model selection guidance
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-13_MODELS.md [ANTAPI-IN13]` for model capabilities

## Summary

Anthropic prices API usage by input and output tokens per million (MTok). Pricing varies by model tier (Mythos/Fable, Opus, Sonnet, Haiku) and is modified by feature-specific multipliers: prompt caching (0.1x for cache reads, 1.25x/2x for cache writes), batch processing (0.5x), data residency (1.1x for US-only), fast mode (2x on Opus 5/4.8), and long context. Tool use adds system prompt tokens. Third-party platforms (Bedrock, Vertex AI, Microsoft Foundry) have their own pricing.

### Base Pricing (per MTok)

- **Claude Fable 5 / Mythos 5**: $10 input / $50 output
- **Claude Opus 5**: $5 input / $25 output
- **Claude Opus 4.8**: $5 input / $25 output
- **Claude Opus 4.7**: $5 input / $25 output
- **Claude Opus 4.6**: $5 input / $25 output
- **Claude Sonnet 5**: $2 input / $10 output (introductory thru Aug 31, 2026; then $3/$15)
- **Claude Sonnet 4.6**: $3 input / $15 output
- **Claude Haiku 4.5**: $0.80 input / $4 output

## Key Facts

- **Unit**: Per million tokens (MTok)
- **Billing**: Input tokens + output tokens, per request
- **Batch Discount**: 50% on all tokens
- **Cache Read**: 10% of base input price
- **Cache Write (5m)**: 125% of base input price
- **Cache Write (1h)**: 200% of base input price
- **Fast Mode**: 2x standard rates (Opus 5 and Opus 4.8 only)
- **Data Residency (US)**: 1.1x multiplier (Opus 4.6+ models)
- **Multipliers Stack**: Cache + batch + data residency + fast mode all compound

## Feature-Specific Pricing

### Prompt Caching Multipliers (relative to base input price)

- **Cache write (5m TTL)**: 1.25x base input price
- **Cache write (1h TTL)**: 2x base input price
- **Cache read**: 0.1x base input price (10% of standard)

Cache reads pay off after 1 read (5m duration) or 2 reads (1h duration).

### Batch Processing

- **All tokens**: 50% discount (0.5x multiplier on input and output)

### Data Residency

- **US-only inference** (`inference_geo`): 1.1x multiplier on all token categories
- **Global routing** (default): Standard pricing
- Applies to Claude Opus 4.6+ models only; earlier models unaffected

### Fast Mode

- **All tokens**: 2x standard rates
- Available for Claude Opus 5 and Opus 4.8 only
- Removed from Opus 4.7 (Jul 24, 2026) and Opus 4.6 (Jun 29, 2026)
- Not available with Batch API or Claude Platform on AWS
- Stacks with caching and data residency multipliers

### Refusal Billing

- Requests returning `stop_reason: "refusal"` without any output are **not billed** (since Jun 2, 2026)
- Fallback requests (Fable 5 -> Opus 4.8) bill at fallback model's rates
- Server-side fallback input tokens billed as cache read (0.1x), not cache write

### Long Context Pricing

All active models (Opus 5, Opus 4.8, Opus 4.7, Opus 4.6, Sonnet 5, Sonnet 4.6, Fable 5, Mythos 5) include the full 1M token context window at standard pricing (no surcharge). A 900k-token request is billed at the same per-token rate as a 9k-token request. Prompt caching and batch discounts apply across the full context window.

**Tokenizer impact**: Fable 5 and Sonnet 5 use an updated tokenizer that produces ~30% more tokens for the same text. Factor this into cost estimates when migrating from pre-4.7 models.

### Claude Platform on AWS Pricing

Claude Platform on AWS bills through AWS Marketplace using Claude Consumption Units (CCUs). Token usage is rated in USD at standard per-model, per-feature rates, converted to CCUs at $0.01 per CCU, and reported hourly. See `_INFO_ANTAPI-44_CLAUDE_PLATFORM_ON_AWS.md [ANTAPI-IN44]` for details.

### Tool Use Pricing

Tool use adds hidden system prompt tokens (varies by model and tool_choice):

- Tool definitions (names, descriptions, schemas) count as input tokens
- `tool_use` and `tool_result` content blocks count normally
- Server-side tools (web search) may incur additional per-use charges
- If no tools provided, `tool_choice: none` uses 0 additional system prompt tokens

## Third-Party Platform Pricing

- **AWS Bedrock**: https://aws.amazon.com/bedrock/pricing/
- **Google Vertex AI**: https://cloud.google.com/vertex-ai/generative-ai/pricing
- **Microsoft Foundry**: https://azure.microsoft.com/en-us/pricing/details/ai-foundry/

Starting with Claude Sonnet 4.5 and Haiku 4.5:

- **Global endpoints**: Dynamic routing, standard pricing
- **Regional endpoints**: Guaranteed geography, 10% premium

## Cost Optimization Strategies

### Use Prompt Caching for Repeated Context

```python
import anthropic

client = anthropic.Anthropic()

# Cache a large system prompt (pays off after 1 read with 5m TTL)
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are an expert assistant with deep knowledge of...",
            "cache_control": {"type": "ephemeral"},  # 5m TTL, 1.25x write
        }
    ],
    messages=[{"role": "user", "content": "Question 1"}],
)
# Subsequent calls with same system prompt hit cache at 0.1x
```

### Use Batch API for Non-Urgent Work

```python
# 50% discount on all tokens
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"item-{i}",
            "params": {
                "model": "claude-haiku-4-5-20251001",  # Cheapest model
                "max_tokens": 256,
                "messages": [{"role": "user", "content": f"Process item {i}"}],
            },
        }
        for i in range(1000)
    ]
)
```

### Choose the Right Model

```python
# Cost-sensitive: Use Haiku for simple tasks
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=256,
    messages=[{"role": "user", "content": "Classify this text: ..."}],
)

# Quality-sensitive: Use Sonnet for balanced tasks
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Analyze this document..."}],
)

# Maximum capability: Use Opus for complex reasoning
response = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Design an architecture for..."}],
)

# Frontier intelligence: Use Fable for the hardest problems
response = client.messages.create(
    model="claude-fable-5",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Solve this novel research problem..."}],
)
```

## Gotchas and Quirks

- Tool use adds hidden system prompt tokens even when tool_choice is "auto" or "any"
- Pricing multipliers stack multiplicatively (e.g., batch + cache read = 0.5 * 0.1 = 0.05x base)
- Fast mode (2x) is only on Opus 5 and 4.8; not compatible with Batch API
- Data residency pricing only affects Opus 4.6+ models
- Sonnet 5 introductory pricing ($2/$10) ends Aug 31, 2026; plan for $3/$15 after
- Third-party platform pricing differs from direct API pricing
- Regional endpoints on Bedrock/Vertex have a 10% premium over global endpoints
- Use 1h cache TTL with batches (5m may expire before batch processes)

## Related Endpoints

- `_INFO_ANTAPI-13_MODELS.md [ANTAPI-IN13]` - Model capabilities and context windows
- `_INFO_ANTAPI-20_PROMPT_CACHING.md [ANTAPI-IN20]` - Caching implementation
- `_INFO_ANTAPI-12_BATCHES.md [ANTAPI-IN12]` - Batch processing
- `_INFO_ANTAPI-10_TOKEN_COUNTING.md [ANTAPI-IN10]` - Pre-request cost estimation

## Sources

- ANTAPI-SC-ANTH-PRICING - https://platform.claude.com/docs/en/about-claude/pricing - Full pricing tables, multipliers
- ANTAPI-SC-ANTH-MODCHSE - https://platform.claude.com/docs/en/about-claude/models/choosing-a-model - Model selection
- ANTAPI-SC-ANTH-MODDEP - https://platform.claude.com/docs/en/about-claude/model-deprecations - Deprecation schedule

## SDK Verification

Examples updated for `anthropic` SDK 0.120.0. Pending re-verification in Prompt 3.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: Base pricing table with all current models including Fable 5, Opus 5, Sonnet 5
- Changed: Fast mode pricing from 6x to 2x, now Opus 5/4.8 only
- Added: Refusal billing section (no charge on blocked requests, fallback billing)
- Added: Tokenizer cost impact note for Fable 5/Sonnet 5
- Added: Fable 5 example in model selection
- Changed: Sonnet 5 introductory pricing noted

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Fast mode now available on Opus 4.7 (not just 4.6)
- Changed: Long context pricing updated (1M GA on Opus 4.7/4.6/Sonnet 4.6 at standard rates)
- Added: Claude Platform on AWS CCU pricing section
- Changed: Model references in examples to current active models

**[2026-03-20 06:50]**
- Added: SDK verification section (anthropic 0.120.0, all 3 examples valid)

**[2026-03-20 03:00]**
- Initial documentation created from pricing and model selection pages
