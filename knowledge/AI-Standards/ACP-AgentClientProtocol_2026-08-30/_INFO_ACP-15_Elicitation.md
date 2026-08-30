# ACP: Elicitation

**Doc ID**: ACP-IN15
**Goal**: Document the ACP elicitation feature for structured user input
**Version scope**: ACP Protocol v1 (stabilized July 24, 2026)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

Elicitation allows agents to request structured, non-sensitive information from users through form mode or direct users to secure out-of-band flows through URL mode. Clients explicitly advertise the modes they support during initialization. Stabilized on July 24, 2026 via the Elicitation RFD. [VERIFIED] (ACP-SC-ANN-ELCTN, ACP-SC-ACPORG-ELCTN)

## Client Capability Advertising

Clients declare elicitation support during initialization: [VERIFIED] (ACP-SC-ANN-ELCTN)

```json
{
  "clientCapabilities": {
    "elicitation": {
      "form": {},
      "url": {}
    }
  }
}
```

- `form`: Client supports structured form-based input
- `url`: Client supports URL-based flows (redirect to external page)

Both modes are optional. Agents must check for their presence before using them. A mode counts as supported only when its field is present AND non-null - unlike MCP, ACP does NOT treat an empty `elicitation: {}` object as form support. [VERIFIED] (ACP-SC-ACPORG-INIT)

## Form Mode

Form mode lets agents request structured input via a form displayed in the editor UI.

### Creating an Elicitation (Agent to Client)

The request uses `mode: "form"` (string discriminator), a human-readable `message`, and a `requestedSchema` - a RESTRICTED flat JSON Schema (top-level object with primitive properties only; the client renders the form UI from it):

```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "elicitation/create",
  "params": {
    "sessionId": "sess_abc123def456",
    "mode": "form",
    "message": "Select deployment options for your application",
    "requestedSchema": {
      "type": "object",
      "properties": {
        "environment": {
          "type": "string",
          "enum": ["staging", "production"]
        },
        "dryRun": {
          "type": "boolean",
          "default": true
        }
      },
      "required": ["environment"]
    }
  }
}
```

Supported property schemas: string (with optional `format`), boolean, integer, number, enum (single select), multi-select (array of enum items, plain or titled). No nested objects, no custom field types. [VERIFIED] (ACP-SC-ACPORG-ELCTN, ACP-SC-ACPORG-SCHM)

### Client Response

The client displays the form and responds with one of three ACTIONS - `accept`, `decline`, or `cancel` - plus the submitted values in `content` on accept:

```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "action": "accept",
    "content": {
      "environment": "staging",
      "dryRun": true
    }
  }
}
```

- **`accept`**: User submitted or consented; `content` SHOULD conform to `requestedSchema` (optional - omission and `null` are equivalent)
- **`decline`**: User explicitly declined
- **`cancel`**: User dismissed without choosing (`content` ignored for decline/cancel)

[VERIFIED] (ACP-SC-ACPORG-ELCTN)

### Optional Completion Notification (URL mode)

URL-mode requests carry an `elicitationId`; the agent MAY follow up with `elicitation/complete` when the out-of-band interaction finishes, so the client can dismiss its UI. The `elicitationId` MUST be unique per elicitation. Form mode needs no completion notification - the response itself completes it: [VERIFIED] (ACP-SC-ACPORG-ELCTN)

```json
{
  "jsonrpc": "2.0",
  "method": "elicitation/complete",
  "params": {
    "sessionId": "sess_abc123def456",
    "elicitationId": "github-oauth-001"
  }
}
```

## URL Mode

URL mode directs users to an external page for secure out-of-band interactions (e.g., OAuth consent, payment flows). [VERIFIED] (ACP-SC-ANN-ELCTN)

```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "elicitation/create",
  "params": {
    "sessionId": "sess_abc123def456",
    "mode": "url",
    "elicitationId": "github-oauth-001",
    "url": "https://auth.example.com/consent?elicitationId=github-oauth-001",
    "message": "Please authorize access to your repositories."
  }
}
```

The client MUST display the target host and obtain consent before navigating. An `accept` response means the user consented to OPEN the URL - not that the external interaction completed (use `elicitation/complete` for that). Inputs entered out-of-band never transit over ACP or enter the model context. [VERIFIED] (ACP-SC-ACPORG-ELCTN)

## Scoping

Elicitation requests define their scope, which determines when they are automatically dismissed: [VERIFIED] (ACP-SC-ANN-ELCTN)

- **Session scope**: Dismissed when the session ends
- **Tool-call scope**: Dismissed when the associated tool call completes
- **Request scope**: Dismissed when the associated request completes

## Use Cases

### Configuration Gathering

Agents can ask users for deployment targets, feature flags, or environment-specific settings before executing complex operations.

### Confirmation Dialogs

Before destructive operations, agents can present a structured confirmation form with specific options rather than relying on the binary permission model.

### External Authentication

URL mode enables OAuth or other browser-based authentication flows that require secure, out-of-band user interaction.

## Quick Reference

- **Create**: `elicitation/create` (agent to client, request)
- **Complete**: `elicitation/complete` (agent to client, notification, optional)
- **Modes**: form (structured input), url (external redirect)
- **Client capability**: `clientCapabilities.elicitation.form` / `.url`
- **Scopes**: session, tool-call, request
- **Stabilized**: July 24, 2026

## Limitations and Gotchas

- Elicitation is for **non-sensitive** information only; form mode MUST NOT request secrets or credentials (passwords, API keys, tokens, payment credentials) - use URL mode; if the client lacks URL support, the agent MUST NOT fall back to form mode for sensitive data
- Clients may support only one mode (form or url); agents MUST NOT send elicitation requests with unsupported modes
- `elicitation: {}` in client capabilities advertises NO modes - each mode must be explicitly present and non-null
- The restricted JSON Schema allows only flat objects with primitive/enum/multi-select properties; custom field types are not supported
- `accept` on URL mode only confirms consent to navigate; completion is signalled separately via `elicitation/complete`
- Elicitation is not a replacement for `session/request_permission`; use permissions for action approval, elicitation for data gathering
- Clients MUST let users review and modify form responses before sending; agents SHOULD validate submitted values against the schema again

## Sources

- ACP-SC-ANN-ELCTN - Elicitation stabilization announcement (July 24, 2026)
- ACP-SC-ACPORG-ELCTN - Official elicitation protocol documentation (https://agentclientprotocol.com/rfds/elicitation)
- ACP-SC-ACPORG-SCHM - Official v1 schema (https://agentclientprotocol.com/protocol/v1/schema) - ElicitationSchema, ElicitationPropertySchema, MultiSelectPropertySchema, action/content response
- ACP-SC-ACPORG-INIT - Official initialization documentation - elicitation capability advertising rules

## Document History

**[2026-08-30 14:20]**
- Fixed: request shape corrected against official docs (https://agentclientprotocol.com/rfds/elicitation) - `mode` is a string discriminator with top-level `message` + `requestedSchema` (restricted JSON Schema); the `mode: {type, title, fields[]}` object shape was hallucinated
- Fixed: response is `action` (accept/decline/cancel) + `content` - the `outcome: "completed"` + `values` shape was hallucinated
- Fixed: URL-mode example (elicitationId + url + message at params level); elicitation/complete clarified as URL-mode completion signal
- Added: restricted schema property types, `{}` advertises no modes, sensitive-data rules, consent semantics

**[2026-08-30 03:50]**
- Initial document created (new topic for v1 stabilization)
