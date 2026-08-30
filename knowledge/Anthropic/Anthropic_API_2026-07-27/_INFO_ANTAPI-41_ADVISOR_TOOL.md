# Advisor Tool

**Doc ID**: ANTAPI-IN41
**Goal**: Document the advisor tool for pairing executor and advisor models
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` for Messages API request schema
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` for beta header usage

## Summary

The advisor tool (beta) pairs an executor model with a more capable advisor model. The executor model can consult the advisor during complex tasks, getting guidance without the cost of running the advisor model for the entire conversation. This is useful for agentic workflows where a smaller, faster model handles routine work but can escalate to a more capable model for difficult decisions. Since June 2, 2026, the advisor tool supports a `max_tokens` parameter to cap advisor output length and cost. Requires the `advisor-tool-2026-03-01` beta header.

## Key Facts

- **Beta Header**: `advisor-tool-2026-03-01`
- **Tool Type**: `advisor_20260301`
- **Executor**: The model running the conversation (e.g., Sonnet 4.6)
- **Advisor**: A more capable model consulted on demand (e.g., Opus 4.7)
- **SDK Namespace**: `client.beta.messages.create()` with advisor tool in tools list
- **max_tokens**: Optional cap on advisor output (since Jun 2, 2026)
- **Status**: Beta

## Quick Reference

```python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-sonnet-4-6",  # Executor model
    max_tokens=4096,
    tools=[
        {
            "type": "advisor_20260301",
            "advisor_model": "claude-opus-5",  # More capable advisor
            "max_tokens": 2048,  # Cap advisor output
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Review this complex architecture proposal and identify issues...",
        }
    ],
    betas=["advisor-tool-2026-03-01"],
)
```

## How It Works

1. Executor model receives the user message and processes it
2. When facing a complex decision, executor invokes the advisor tool
3. Advisor model receives context and provides guidance
4. Executor incorporates advisor's guidance into its response
5. User sees the final response from the executor

## Use Cases

- Agentic coding: Sonnet handles routine code, Opus reviews architecture decisions
- Document analysis: Haiku processes pages, Opus handles complex reasoning
- Cost optimization: Use cheaper model for 90% of work, expensive model for 10%

## Limitations

- Advisor model invocations add latency and cost for each consultation
- The executor decides when to consult; it may not always escalate appropriately
- Not all model combinations may be supported
- `max_tokens` on advisor caps output; without it, advisor may produce long responses

## Gotchas and Quirks

- The advisor tool counts as a tool use; tool_choice settings apply
- Advisor model tokens are billed at the advisor model's rates
- The executor model must support tool use to invoke the advisor

## Related Endpoints

- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` - Tool use (advisor is a tool type)
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` - Beta header configuration
- `_INFO_ANTAPI-14_PRICING.md [ANTAPI-IN14]` - Pricing (mixed model billing)

## Sources

- ANTAPI-SC-ANTH-ADVSR - https://platform.claude.com/docs/en/build-with-claude/advisor - Advisor tool guide

## SDK Verification

2 client calls verified against `anthropic` SDK 0.120.0:
- `client.beta.messages.create` - OK (params: model, max_tokens, tools, messages)

Note: `betas=["advisor-tool-2026-03-01"]` param is passed as a keyword argument. The SDK accepts `betas` on beta endpoints.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: max_tokens parameter on advisor tool (Jun 2, 2026)
- Changed: Model references to claude-opus-5

**[2026-05-22]**
- Initial documentation created from advisor tool guide and release notes
- Added: SDK verification section (2 calls verified against 0.104.0)
