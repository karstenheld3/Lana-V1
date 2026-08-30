# Amazon Bedrock Integration

**Doc ID**: OAIAPI-IN97
**Goal**: Document OpenAI models available via Amazon Bedrock through OpenAI-compatible Responses API endpoint
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Overview

Since 2026-06, OpenAI models are available in Amazon Bedrock through an OpenAI-compatible Responses API endpoint. This allows AWS customers to use OpenAI models while keeping data within their AWS environment, using existing AWS billing, and leveraging AWS IAM for access control.

Supported models and features vary by AWS Region. The SDK supports setting Bedrock API keys directly on the client (added in v2.40.0).

## SDK Examples

### Python - Bedrock Configuration

```python
from openai import OpenAI

# Configure client for Amazon Bedrock endpoint
client = OpenAI(
    base_url="https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1",
    # AWS credentials handled via default credential chain
)

response = client.responses.create(
    model="gpt-5.6-terra",
    input="Explain the benefits of serverless architecture.",
)
print(response.output_text)
```

### Python - Direct API Key on Client

```python
from openai import OpenAI

# Set Bedrock API keys directly (SDK v2.40.0+)
client = OpenAI(
    base_url="https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1",
    api_key="bedrock-api-key-here",
)

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Summarize Q2 revenue trends.",
)
print(response.output_text)
```

## AWS Credential Chain

The default AWS credential chain supports:
- Environment credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- Shared credentials and config files
- Named profiles
- SSO and assume-role profiles
- Workload credentials (ECS task roles, EC2 instance profiles)

AWS controls which endpoints and features are supported. Unsupported calls surface the provider's normal HTTP errors through the SDK.

## Supported Features

- Responses API (primary interface)
- Standard text generation
- Reasoning (effort levels vary by region)
- Tool calling / function calling

**Not yet confirmed on Bedrock:**
- Programmatic Tool Calling
- Multi-Agent beta
- Realtime API
- Image/video generation

## Gotchas and Quirks

- Feature availability varies by AWS Region - check Bedrock documentation for current status
- Billing goes through AWS, not OpenAI directly
- Rate limits are AWS-managed, may differ from direct OpenAI limits
- Requires SDK v2.40.0+ for proper Bedrock support
- Some newer features (PTC, Multi-Agent) may not be immediately available on Bedrock

## TypeScript Examples

### Client Setup and Basic Usage

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  organization: process.env.OPENAI_ORG_ID,
});

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Hello!",
});
console.log(response.output_text);
```

## Sources

- https://developers.openai.com/api/docs/guides/amazon-bedrock
- SDK changelog v2.40.0 (Amazon Bedrock Responses support)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Initial documentation for Amazon Bedrock integration
