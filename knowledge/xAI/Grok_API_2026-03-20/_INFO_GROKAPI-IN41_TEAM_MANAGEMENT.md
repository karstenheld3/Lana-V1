# INFO: Team and Account Management

**Doc ID**: GROKAPI-IN41
**Goal**: Team structure, console access, API key management, roles
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

xAI uses a team-based organization model. Teams are created via the xAI Console (https://console.x.ai). Each team has its own API keys, billing, rate limits, and collections. The Management API (https://management-api.x.ai) provides programmatic team and API key management including creating, listing, updating, and deleting keys, managing ACLs, and checking propagation status. Team members have roles that control access to console features. API key ACLs control model and endpoint access granularly. Rate limits and tier progression are per-team based on cumulative spend. [VERIFIED] (GROKAPI-SC-XAI-MGMTAPI | https://docs.x.ai/developers/management-api)

## Key Facts

- [VERIFIED] Team-based organization model (GROKAPI-SC-XAI-MGMTAPI)
- [VERIFIED] Console: https://console.x.ai (GROKAPI-SC-XAI-QUICKSTART)
- [VERIFIED] Management API: https://management-api.x.ai (GROKAPI-SC-XAI-MGMTAPI)
- [VERIFIED] ACLs: `api-key:model:*`, `api-key:endpoint:*` patterns (GROKAPI-SC-XAI-MGMTAPI)
- [VERIFIED] Rate limits are per-team based on cumulative spend (GROKAPI-SC-XAI-RATELIMITS)
- [VERIFIED] Propagation status trackable for key changes (GROKAPI-SC-XAI-MGMTAPI)

## Quick Reference

### Console Operations
- Create/manage teams
- Generate API keys
- View usage and billing
- Manage collections
- Access tokenizer playground

### Management API Operations
- `POST /auth/teams/{teamId}/api-keys` - Create API key
- `GET /auth/teams/{teamId}/api-keys` - List keys
- `PUT /auth/teams/{teamId}/api-keys/{keyId}` - Update key
- `DELETE /auth/teams/{teamId}/api-keys/{keyId}` - Delete key
- ACL management for model and endpoint access
- QPS/QPM/TPM per-key rate limits

## Differences from Other APIs

### vs OpenAI
- **Management API**: xAI has a separate Management API at different URL; OpenAI manages keys via Dashboard/API
- **ACLs**: xAI has granular ACL patterns; OpenAI uses project-level scoping
- **Rate limits**: xAI per-team spend-based tiers; OpenAI per-organization usage-based

### vs Anthropic
- **Console**: Both have web consoles for team management
- **No Management API**: Anthropic has no programmatic key management API

## Sources

- GROKAPI-SC-XAI-MGMTAPI | https://docs.x.ai/developers/management-api | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:30]**
- Initial document created with team management reference
