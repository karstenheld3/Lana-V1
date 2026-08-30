# Rate Limits API

**Doc ID**: ANTAPI-IN43
**Goal**: Document the Rate Limits API for programmatic querying of configured rate limits
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-36_RATE_LIMITS.md [ANTAPI-IN36]` for rate limit concepts and handling
- `_INFO_ANTAPI-32_ADMIN_ORGS.md [ANTAPI-IN32]` for Admin API overview

## Summary

The Rate Limits API (`GET /v1/organizations/rate_limits`) provides programmatic access to an organization's configured rate limits. This allows applications to query their current RPM, input TPM, and output TPM limits per model without making test requests and inspecting response headers. The endpoint returns the configured maximums for each model the organization has access to.

## Key Facts

- **Endpoint**: `GET /v1/organizations/rate_limits`
- **Auth**: Admin API key or organization-scoped key
- **Response**: List of rate limit configurations per model
- **Limit Types**: RPM, input TPM, output TPM
- **Status**: GA (launched April 24, 2026)

## Quick Reference

```python
import anthropic

client = anthropic.Anthropic()

# Query rate limits for your organization
rate_limits = client.organizations.rate_limits.list()
for limit in rate_limits:
    print(f"Model: {limit.model}")
    print(f"  RPM: {limit.requests_per_minute}")
    print(f"  Input TPM: {limit.input_tokens_per_minute}")
    print(f"  Output TPM: {limit.output_tokens_per_minute}")
```

## Use Cases

- Pre-flight capacity checks before launching batch workloads
- Dynamic rate limiting in client applications
- Monitoring and alerting on rate limit changes
- Capacity planning dashboards

## Gotchas and Quirks

- Returns configured maximums, not current remaining capacity (use response headers for remaining)
- Requires admin-level API key access
- Rate limits may change as organization tier changes

## Related Endpoints

- `_INFO_ANTAPI-36_RATE_LIMITS.md [ANTAPI-IN36]` - Rate limit concepts, headers, handling
- `_INFO_ANTAPI-32_ADMIN_ORGS.md [ANTAPI-IN32]` - Admin API overview

## Sources

- ANTAPI-SC-ANTH-RTLMTAPI - https://platform.claude.com/docs/en/api/rate-limits - Rate limits documentation (includes API endpoint)

## SDK Verification

> **REST-only**: `client.organizations.rate_limits` namespace does NOT exist in SDK 0.120.0. The code example in Quick Reference is aspirational (from API docs). Use `httpx` with direct HTTP calls until SDK support is added.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Initial documentation created from rate limits documentation and release notes
- Added: SDK verification section (REST-only, not in SDK 0.120.0)
