# INFO: Security

**Doc ID**: GROKAPI-IN43
**Goal**: API key security, ACLs, data handling, encryption, compliance
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Security for the Grok API covers API key management, ACL-based access control, data handling policies, and encrypted reasoning content. API keys should be stored in environment variables, never hardcoded. The Management API enables granular ACL control per key: `api-key:model:{model_name}` restricts which models a key can access, `api-key:endpoint:{endpoint}` restricts which endpoints. Per-key rate limits (QPS, QPM, TPM) provide additional throttling. Encrypted reasoning content (`reasoning.encrypted_content`) allows replaying reasoning without exposing internal thought processes. Response storage can be disabled with `store: false`. Data is transmitted over HTTPS/TLS. [VERIFIED] (GROKAPI-SC-XAI-MGMTAPI | https://docs.x.ai/developers/management-api)

## Key Security Features

- **ACL patterns**: `api-key:model:*`, `api-key:endpoint:*` for fine-grained access
- **Per-key rate limits**: QPS, QPM, TPM configurable per API key
- **Encrypted reasoning**: `reasoning.encrypted_content` for secure reasoning replay
- **Storage control**: `store: false` to disable server-side response storage
- **Transport**: HTTPS/TLS for all API communication
- **Key rotation**: Management API supports key creation and deletion for rotation
- **Propagation tracking**: Monitor key changes with propagation status

## Best Practices

- Store API keys in environment variables (`XAI_API_KEY`)
- Use minimum necessary ACLs per key
- Set per-key rate limits to prevent runaway costs
- Use `store: false` for sensitive data
- Rotate keys regularly via Management API
- Monitor usage via Console dashboard
- Use encrypted reasoning for auditable but secure reasoning chains

## Differences from Other APIs

### vs OpenAI
- **ACLs**: xAI has granular model/endpoint ACLs; OpenAI uses project-level scoping
- **Management API**: xAI has a separate programmatic Management API; OpenAI manages via Dashboard
- **Encrypted reasoning**: UNIQUE - xAI encrypts reasoning content for secure replay

### vs Anthropic
- **No Management API**: Anthropic has no programmatic key management
- **No encrypted reasoning**: Anthropic's extended thinking is not encrypted

## Sources

- GROKAPI-SC-XAI-MGMTAPI | https://docs.x.ai/developers/management-api | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:40]**
- Initial document created with security reference
