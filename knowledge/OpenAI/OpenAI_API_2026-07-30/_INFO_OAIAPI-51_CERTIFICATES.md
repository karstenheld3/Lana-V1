# mTLS Certificates

**Doc ID**: OAIAPI-IN51
**Goal**: Document mTLS certificate management for secure API communication
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN47_ADMIN_OVERVIEW.md [OAIAPI-IN47]` for admin context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Certificates API manages mTLS (mutual TLS) certificates for securing API communication. mTLS provides an additional authentication layer beyond API keys - the client must present a valid certificate during TLS handshake. Create certificates by uploading PEM-encoded certs, retrieve, list, activate/deactivate, and delete. Certificates managed at organization level and project level. When mTLS is enforced, requests without valid client certificate are rejected regardless of API key validity. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-ADMORG)

## Key Facts

- **Purpose**: Additional authentication layer via client certificates [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **Format**: PEM-encoded X.509 certificates [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **Scopes**: Organization-level or project-level [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **States**: active, inactive [VERIFIED] (OAIAPI-SC-OAI-ADMORG)
- **Enforcement**: When enabled, requests without valid cert are rejected [VERIFIED] (OAIAPI-SC-OAI-ADMORG)

## Quick Reference

```
POST   /v1/organization/certificates                          # Create certificate
GET    /v1/organization/certificates                          # List certificates
GET    /v1/organization/certificates/{cert_id}                # Retrieve
POST   /v1/organization/certificates/{cert_id}/activate       # Activate
POST   /v1/organization/certificates/{cert_id}/deactivate     # Deactivate
DELETE /v1/organization/certificates/{cert_id}                # Delete
```

## Certificate Object

```json
{
  "object": "organization.certificate",
  "id": "cert-abc123",
  "name": "Production mTLS Cert",
  "status": "active",
  "created_at": 1711471533,
  "expires_at": 1743007533,
  "fingerprint": "AB:CD:EF:12:34:56:78:90"
}
```

## SDK Examples (Python)

### Certificate Lifecycle

```python
from openai import OpenAI

client = OpenAI(api_key="sk-admin-...")

# Create certificate
with open("client_cert.pem", "r") as f:
    cert_pem = f.read()

cert = client.organization.certificates.create(
    name="Production mTLS",
    certificate=cert_pem
)
print(f"Certificate: {cert.id}, Status: {cert.status}")

# Activate
client.organization.certificates.activate(cert.id)

# List all certificates
certs = client.organization.certificates.list()
for c in certs.data:
    print(f"  {c.name} ({c.status}) expires {c.expires_at}")
```

### Certificate Lifecycle (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/admin/organization/certificates.py
from openai import OpenAI

client = OpenAI(admin_api_key="sk-admin-...")

# Create certificate
with open("client_cert.pem", "r") as f:
    cert_pem = f.read()

cert = client.admin.organization.certificates.create(
    name="Production mTLS",
    certificate=cert_pem
)
print(f"Certificate: {cert.id}, Status: {cert.status}")

# Activate
client.admin.organization.certificates.activate(cert.id)

# List all certificates
certs = client.admin.organization.certificates.list()
for c in certs.data:
    print(f"  {c.name} ({c.status}) expires {c.expires_at}")
```

## Use Cases

- **Enterprise security**: Enforce mTLS for compliance (SOC2, HIPAA)
- **Zero-trust**: Additional authentication layer beyond API keys
- **Certificate rotation**: Programmatic certificate management

## Differences from Other APIs

- **vs Anthropic**: No mTLS certificate management API
- **vs Gemini**: Uses Google Cloud Certificate Manager (different service)
- **vs Grok**: No mTLS API

## TypeScript Examples

### Admin API

```typescript
import OpenAI from "openai";

// Admin API requires admin API key
const client = new OpenAI();

// List organization members
for await (const user of await client.admin.users.list()) {
  console.log(`${user.email}: ${user.role}`);
}
```

## Sources

- OAIAPI-SC-OAI-ADMORG - Organization Administration API

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:15]**
- Enriched from 2026-03-20 IN51 (19 -> 95 lines)

**[2026-05-22 11:45]**
- Stub created
