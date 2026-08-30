# Voice Consent Management

**Doc ID**: OAIAPI-IN92
**Goal**: Document voice consent API for TTS custom voice permissions
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Voice consent API for managing TTS custom voice permissions. CRUD operations: create consent, retrieve, update, delete, list. Required for custom voice creation and usage. Ensures compliance with voice likeness regulations. Endpoints: POST/GET/PUT/DELETE /v1/audio/voice_consents. [VERIFIED] (OAIAPI-SC-OAI-AUDVOI)

## Key Facts

- **Purpose**: Manage consent records for custom voice cloning [VERIFIED]
- **Compliance**: Required before creating custom voices (voice likeness regulations) [VERIFIED]
- **CRUD**: Full create/read/update/delete operations [VERIFIED]
- **Association**: Consent records linked to voice IDs for audit trail

## REST API

### Endpoints

- **Create consent**: `POST /v1/audio/voice_consents`
- **Retrieve consent**: `GET /v1/audio/voice_consents/{consent_id}`
- **Update consent**: `PUT /v1/audio/voice_consents/{consent_id}`
- **Delete consent**: `DELETE /v1/audio/voice_consents/{consent_id}`
- **List consents**: `GET /v1/audio/voice_consents`

### Create Consent Request

```json
{
  "voice_owner_name": "Jane Doe",
  "voice_owner_email": "jane@example.com",
  "consent_type": "verbal",
  "consent_recording_file_id": "file-abc123",
  "usage_scope": "commercial",
  "expiration_date": "2027-01-01"
}
```

### Consent Object Response

```json
{
  "id": "vc_abc123",
  "object": "voice_consent",
  "voice_owner_name": "Jane Doe",
  "consent_type": "verbal",
  "status": "active",
  "created_at": 1716000000,
  "expiration_date": "2027-01-01",
  "associated_voice_ids": ["voice_xyz"]
}
```

## Consent Types

- **verbal**: Audio recording of voice owner granting permission
- **written**: Signed document/agreement
- **electronic**: Digital consent form submission

## Workflow

1. **Collect consent** from voice owner (recording, document, or e-signature)
2. **Upload consent evidence** via Files API (`purpose: "voice_consent"`)
3. **Create consent record** via `POST /v1/audio/voice_consents`
4. **Create custom voice** referencing the consent ID
5. **Use voice** in TTS requests
6. **Revoke** if consent is withdrawn (delete consent → voice disabled)

## SDK Examples (Python)

### Create Voice Consent

```python
from openai import OpenAI

client = OpenAI()

# Upload consent recording
consent_file = client.files.create(
    file=open("consent_recording.mp3", "rb"),
    purpose="voice_consent",
)

# Create consent record
consent = client.audio.voice_consents.create(
    voice_owner_name="Jane Doe",
    voice_owner_email="jane@example.com",
    consent_type="verbal",
    consent_recording_file_id=consent_file.id,
    usage_scope="commercial",
)
print(f"Consent: {consent.id}, Status: {consent.status}")
```

### List and Manage Consents

```python
from openai import OpenAI

client = OpenAI()

# List all consents
consents = client.audio.voice_consents.list()
for consent in consents.data:
    print(f"{consent.id}: {consent.voice_owner_name} ({consent.status})")

# Revoke consent
client.audio.voice_consents.delete("vc_abc123")
```

## Gotchas and Quirks

- **Required before voice creation**: Cannot create custom voice without active consent [VERIFIED]
- **Consent expiration**: Expired consents disable associated voices [VERIFIED]
- **Deletion cascades**: Deleting consent revokes voice access [VERIFIED]
- **Regulatory**: Requirements vary by jurisdiction (EU, US, etc.) [COMMUNITY]

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

- OAIAPI-SC-OAI-AUDVOI - Voice consent API reference

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: REST API, consent types, workflow, SDK examples, gotchas

**[2026-05-22 13:05]**
- Initial documentation (gap found during /improve review)
