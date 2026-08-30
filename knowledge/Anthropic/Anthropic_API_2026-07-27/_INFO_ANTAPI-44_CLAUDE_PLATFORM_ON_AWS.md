# Claude Platform on AWS

**Doc ID**: ANTAPI-IN44
**Goal**: Document Claude Platform on AWS - Anthropic-managed infrastructure with AWS billing
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL, auth headers
- `_INFO_ANTAPI-07_SDKS.md [ANTAPI-IN07]` for AnthropicAWS client

## Summary

Claude Platform on AWS provides Anthropic-managed infrastructure accessible through AWS. It combines the full Claude API feature set with AWS billing (via Claude Consumption Units/CCUs), IAM access control, and AWS PrivateLink connectivity. Unlike Amazon Bedrock (AWS-operated), Claude Platform on AWS is operated by Anthropic and supports the same API surface as the direct Claude API, including Messages, Files, Batches, Managed Agents, Agent Skills, and code execution. Launched May 11, 2026. No EU data residency: `inference_geo` only supports `"us"` or global routing. EU customers requiring in-region inference must use AWS Bedrock or Google Vertex AI regional endpoints instead.

## Key Facts

- **SDK Client**: `anthropic.AnthropicAWS(workspace_id="...")`
- **Install**: `pip install "anthropic[aws]"`
- **Auth**: AWS SigV4 or Anthropic API key
- **Billing**: Claude Consumption Units (CCUs) via AWS Marketplace, $0.01 per CCU
- **Model IDs**: Same as direct API (e.g., `claude-opus-5`)
- **PrivateLink**: Supported for VPC connectivity
- **Data Residency**: `inference_geo` parameter supports `"us"` only (no `"eu"` value as of May 2026)
- **Status**: GA (May 2026)

## Quick Reference

```python
# pip install "anthropic[aws]"

import anthropic

client = anthropic.AnthropicAWS(
    workspace_id="your-workspace-id",  # or ANTHROPIC_AWS_WORKSPACE_ID env var
)

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello from Claude Platform on AWS!"}],
)
print(message.content[0].text)
```

## Supported Features

- Messages API (full feature set)
- Files API
- Message Batches API
- Claude Managed Agents
- Agent Skills
- Code execution
- Extended thinking
- Prompt caching
- Streaming

## CCU Billing

Token usage is rated in USD at standard per-model, per-feature rates, then converted to CCUs at $0.01 per CCU and reported hourly through AWS Marketplace. The same pricing multipliers apply (caching, batch, data residency). Fast mode is not available on Claude Platform on AWS.

## Differences from Direct API

- Billing through AWS Marketplace (CCUs) instead of Anthropic billing
- AWS IAM for access control
- AWS PrivateLink for VPC-private connectivity
- Separate capacity pool from direct API and Bedrock
- Zero Data Retention (ZDR) available on request
- Same API surface and model IDs

## Differences from Amazon Bedrock

- Operated by Anthropic (not AWS)
- Same model IDs as direct API (no Bedrock-specific IDs)
- Supports full feature set including Managed Agents, Files API, Skills
- CCU billing (not standard Bedrock pricing)
- Does not use Bedrock InvokeModel or Bedrock Messages API

## Gotchas and Quirks

- Requires `anthropic[aws]` extra for SDK support
- Workspace ID required (from AWS or Anthropic console)
- Fast mode not available on this platform
- Managed Agents on AWS may have different feature availability than direct API

## Related Endpoints

- `_INFO_ANTAPI-38_PLATFORM_COMPAT.md [ANTAPI-IN38]` - All platform options
- `_INFO_ANTAPI-07_SDKS.md [ANTAPI-IN07]` - AnthropicAWS client
- `_INFO_ANTAPI-40_MANAGED_AGENTS.md [ANTAPI-IN40]` - Managed Agents (available on AWS)
- `_INFO_ANTAPI-14_PRICING.md [ANTAPI-IN14]` - CCU pricing details

## Sources

- ANTAPI-SC-ANTH-CPAWS - https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws - Claude Platform on AWS guide

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Initial documentation created from Claude Platform on AWS guide and release notes
