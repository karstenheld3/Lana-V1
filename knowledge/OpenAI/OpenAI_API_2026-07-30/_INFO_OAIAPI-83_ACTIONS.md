# Actions (GPT Actions)

**Doc ID**: OAIAPI-IN83
**Goal**: Document GPT Actions for custom GPT integrations
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Actions enable custom GPTs to interact with external APIs and services. Defined via OpenAPI specifications, actions allow GPTs to make authenticated API calls, retrieve data, and send files. Actions are distinct from the Responses API tools - they are specific to Custom GPT configurations in ChatGPT. Seven sub-guides cover the full lifecycle: Introduction, Getting Started, Actions Library, Authentication, Production, Data Retrieval, and Sending Files. [VERIFIED] (OAIAPI-SC-OAI-GACTN)

## Guides

- **Introduction**: https://developers.openai.com/api/docs/actions/introduction
- **Getting Started**: https://developers.openai.com/api/docs/actions/getting-started
- **Actions Library**: https://developers.openai.com/api/docs/actions/actions-library
- **Authentication**: https://developers.openai.com/api/docs/actions/authentication
- **Production**: https://developers.openai.com/api/docs/actions/production
- **Data Retrieval**: https://developers.openai.com/api/docs/actions/data-retrieval
- **Sending Files**: https://developers.openai.com/api/docs/actions/sending-files

## Key Concepts

- **OpenAPI spec**: Actions defined via OpenAPI 3.x specification
- **Authentication**: OAuth 2.0 or API key authentication for external services
- **Rate limiting**: Subject to ChatGPT usage limits, not API rate limits
- **Scope**: Actions are for Custom GPTs, NOT for API-based agents (use function calling/MCP instead)

## Action Lifecycle

1. **Define**: Write OpenAPI 3.x spec for external API
2. **Configure**: Set up authentication (OAuth 2.0 or API key)
3. **Test**: Validate in Custom GPT builder
4. **Publish**: Make available in GPT Store or share privately
5. **Monitor**: Track usage via GPT analytics

## Authentication Options

### API Key

- Simple bearer token authentication
- Key stored securely in GPT configuration
- Sent as header or query parameter per OpenAPI spec

### OAuth 2.0

- Full OAuth flow for user-level authorization
- Supports authorization code grant
- Token refresh handled automatically
- User prompted to authorize on first use

## Comparison: Actions vs API Tools

- **Actions**: ChatGPT UI only, Custom GPTs, OpenAPI-based, no code needed
- **Function calling**: API-based, requires code to handle tool calls
- **MCP**: API-based, remote server protocol, real-time tool discovery
- **Use Actions when**: Building Custom GPTs for ChatGPT users
- **Use function calling/MCP when**: Building API-integrated applications

## Limitations

- **ChatGPT only**: Not available via API - use function calling or MCP for API-based agents
- **OpenAPI required**: External service must have OpenAPI spec
- **No streaming**: Action responses are not streamed
- **Response size**: Limited response payload size from external APIs
- **Timeout**: External API calls must respond within timeout

## Gotchas and Quirks

- **Not for API developers**: If building with the API, use function calling or MCP instead [VERIFIED]
- **OpenAPI 3.x required**: Swagger 2.0 not supported [VERIFIED]
- **Auth secrets**: Stored per-GPT, not transferable [VERIFIED]
- **Rate limits differ**: Subject to ChatGPT limits, not API tier limits [VERIFIED]

## Sources

- OAIAPI-SC-OAI-GACTN - Actions guides (https://developers.openai.com/api/docs/actions/introduction)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Lifecycle, auth options, comparison with API tools, gotchas

**[2026-05-22 13:00]**
- Initial documentation (gap found during /improve review)
