# Platform Compatibility (AWS, Bedrock, Vertex AI, Foundry)

**Doc ID**: ANTAPI-IN38
**Goal**: Document Claude availability on Claude Platform on AWS, Amazon Bedrock, Google Vertex AI, and Microsoft Foundry
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for direct API baseline

## Summary

Claude models are available on four cloud platforms in addition to the direct Anthropic API: Claude Platform on AWS (Anthropic-managed, AWS billing), Amazon Bedrock (AWS-operated), Google Vertex AI, and Microsoft Azure AI Foundry. The Python SDK provides five platform clients: `AnthropicAWS`, `AnthropicBedrockMantle` (new Messages API), `AnthropicBedrock` (legacy InvokeModel), `AnthropicVertex`, and `AnthropicFoundry`. Feature availability varies by platform.

## Key Facts

- **Claude Platform on AWS**: `AnthropicAWS` client (beta), Anthropic-managed infra, AWS SigV4/API key auth
- **Amazon Bedrock (Messages API)**: `AnthropicBedrockMantle` client, endpoint at `/anthropic/v1/messages`
- **Amazon Bedrock (legacy)**: `AnthropicBedrock` client, InvokeModel API
- **Google Vertex AI**: `AnthropicVertex` client, Google Cloud auth
- **Microsoft Foundry**: `AnthropicFoundry` client, Azure authentication
- **SDK Install**: `anthropic[aws]`, `anthropic[bedrock]`, or `anthropic[vertex]`
- **Pricing**: Platform-specific (10% regional premium on Bedrock/Vertex for 4.5+ models; CCU billing on Platform on AWS)
- **Status**: GA (Platform on AWS GA since May 2026)

## Claude Platform on AWS

Anthropic-managed infrastructure accessible through AWS with SigV4 or API key authentication, IAM access control, and AWS Marketplace billing via Claude Consumption Units (CCUs).

```python
# pip install "anthropic[aws]"

import anthropic

client = anthropic.AnthropicAWS(
    workspace_id="your-workspace-id",  # or ANTHROPIC_AWS_WORKSPACE_ID env var
)

message = client.messages.create(
    model="claude-opus-5",  # Same model IDs as direct API
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello from Claude Platform on AWS!"}],
)
print(message.content[0].text)
```

### Platform on AWS Specifics

- Same API surface as direct Claude API (same model IDs, same endpoints)
- Supports Messages API, Files API, Batches API, Managed Agents, Agent Skills, code execution
- AWS PrivateLink supported for VPC connectivity
- `inference_geo` parameter for data residency
- Separate capacity pool from direct API and Bedrock
- Zero Data Retention (ZDR) available on request

## Amazon Bedrock

### Messages API (recommended for new projects)

```python
# pip install "anthropic[bedrock]"

import anthropic

client = anthropic.AnthropicBedrockMantle()

message = client.messages.create(
    model="claude-opus-5",  # Uses same model IDs as direct API
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello from Bedrock Messages API!"}],
)
print(message.content[0].text)
```

### Legacy InvokeModel API

```python
import anthropic

client = anthropic.AnthropicBedrock(
    aws_region="us-east-1",
)

message = client.messages.create(
    model="us.anthropic.claude-opus-5-v1:0",  # Bedrock-specific model IDs
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello from Bedrock!"}],
)
print(message.content[0].text)
```

### Bedrock Specifics

- **Messages API** (AnthropicBedrockMantle): Same request shape as direct API, endpoint at `/anthropic/v1/messages`, available in 27 AWS regions
- **Legacy** (AnthropicBedrock): Model IDs differ (e.g., `us.anthropic.claude-opus-5-v1:0`), uses InvokeModel API
- Authentication via AWS IAM (credentials, roles, profiles)
- Global vs regional endpoints available (4.5+ models)
- Opus 4.7 and Haiku 4.5 available self-serve from Bedrock console

## Google Vertex AI

### Installation and Setup

```python
# Install with Vertex support
# pip install anthropic[vertex]

import anthropic

client = anthropic.AnthropicVertex(
    project_id="my-gcp-project",
    region="us-east5",
    # Uses Google Cloud credentials from environment or application default credentials
)

message = client.messages.create(
    model="claude-sonnet-4@20250514",  # Vertex model ID
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello from Vertex AI!"}],
)
print(message.content[0].text)
```

### Vertex AI Specifics

- Model IDs use `@` format (e.g., `claude-sonnet-4@20250514`)
- Authentication via Google Cloud Application Default Credentials
- Global vs regional endpoints available (4.5+ models)
- Project and region must be specified

## Microsoft Azure AI Foundry

```python
import anthropic

client = anthropic.AnthropicFoundry()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello from Foundry!"}],
)
print(message.content[0].text)
```

- Claude available via Azure AI Foundry
- Azure authentication mechanisms
- Microsoft Foundry support included in base `anthropic` package (no extras needed)
- See Microsoft Foundry pricing documentation for details

## Feature Availability

Not all features available on direct API are available on third-party platforms. Check platform-specific documentation for:

- Beta features (may not be available)
- Streaming support
- Tool use capabilities
- Extended thinking
- Batch processing
- Files API

## Gotchas and Quirks

- Model IDs differ across platforms; use platform-specific identifiers
- Auth mechanisms are platform-native (AWS IAM, Google Cloud, Azure AD)
- Regional endpoints on Bedrock/Vertex have a 10% price premium (Sonnet 4.5+ models)
- Beta features may lag behind the direct API
- Rate limits are set by the platform, not Anthropic
- The Anthropic SDK wraps platform-specific APIs for consistent interface
- Some Admin API features are not available on third-party platforms

## Related Endpoints

- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` - Direct API baseline
- `_INFO_ANTAPI-07_SDKS.md [ANTAPI-IN07]` - SDK platform-specific clients
- `_INFO_ANTAPI-14_PRICING.md [ANTAPI-IN14]` - Third-party platform pricing

## Sources

- ANTAPI-SC-ANTH-CPAWS - https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws - Claude Platform on AWS guide
- ANTAPI-SC-ANTH-BEDRM - https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock - Bedrock Messages API guide
- ANTAPI-SC-ANTH-BEDROCK - https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy - Bedrock legacy guide
- ANTAPI-SC-ANTH-VERTEX - https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai - Vertex AI guide
- ANTAPI-SC-ANTH-FOUNDRY - https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry - Foundry guide

## SDK Verification

Examples updated for `anthropic` SDK 0.120.0. Pending re-verification in Prompt 3.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Added: Claude Platform on AWS (AnthropicAWS client, CCU billing, PrivateLink)
- Added: Amazon Bedrock Messages API (AnthropicBedrockMantle client)
- Added: AnthropicFoundry client code example
- Changed: Title expanded to include AWS platform
- Changed: Summary and key facts updated for 5 platform clients

**[2026-03-20 07:05]**
- Added: SDK verification section (anthropic 0.120.0, all 2 examples valid)

**[2026-03-20 04:30]**
- Initial documentation created from platform integration guides
