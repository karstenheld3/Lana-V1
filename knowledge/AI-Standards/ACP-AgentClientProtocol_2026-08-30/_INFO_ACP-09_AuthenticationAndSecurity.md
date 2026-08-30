# ACP: Authentication and Security

**Doc ID**: ACP-IN09
**Goal**: Document ACP authentication flows and security model
**Version scope**: ACP Protocol v1 (stable) + v2 changes noted

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP's authentication system allows agents to require sign-in before creating sessions. Authentication methods are advertised during initialization, and the client triggers the chosen method. The broader security model relies on a "trusted agent" assumption: the editor spawns the agent locally and mediates all destructive actions through the permission system. [VERIFIED] (ACP-SC-ACPORG-AUTH, ACP-SC-ACPORG-ARCH)

## Advertising Authentication

Agents declare available authentication methods in their `initialize` response via the `authMethods` array: [VERIFIED] (ACP-SC-ACPORG-AUTH)

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": 1,
    "agentCapabilities": {
      "auth": { "logout": {} }
    },
    "authMethods": [
      {
        "id": "agent-login",
        "name": "Agent login",
        "description": "Sign in using the agent's login flow"
      }
    ]
  }
}
```

If `authMethods` is omitted or empty, the agent does not require authentication.

## Authenticating (v1)

The client sends `authenticate` with the chosen `methodId`: [VERIFIED] (ACP-SC-ACPORG-AUTH)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "authenticate",
  "params": { "methodId": "agent-login" }
}
```

The agent performs its authentication flow (may involve browser-based OAuth) and responds:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {}
}
```

After successful authentication, the client proceeds with `session/new` or `session/load`.

## Logging Out (v1)

Agents that advertise `agentCapabilities.auth.logout` support explicit logout: [VERIFIED] (ACP-SC-ACPORG-AUTH, ACP-SC-ACPORG-UPDTS)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "logout",
  "params": {}
}
```

## v2 Authentication Changes (Draft)

Key changes in v2: [VERIFIED] (ACP-SC-ACPORG-V2MIG)

- `authenticate` renamed to **`auth/login`**
- `logout` renamed to **`auth/logout`**
- When `authMethods` is non-empty, the agent MUST implement both `auth/login` and `auth/logout` (no separate logout capability marker)
- When `authMethods` is omitted or empty, clients MUST NOT call either method

## Security Model

### Trust Model

- **Trusted subprocess**: ACP assumes the agent is a trusted subprocess spawned by the editor [VERIFIED] (ACP-SC-ACPORG-ARCH)
- **Editor as gatekeeper**: The editor mediates all agent actions affecting the local environment through the permission system
- **User in control**: `session/request_permission` ensures users can approve or deny individual operations

### Permission-Based Access Control

- File system access gated by client capabilities (`fs.readTextFile`, `fs.writeTextFile`)
- Terminal access gated by `clientCapabilities.terminal`
- Individual tool executions can require explicit user permission
- Permission choices can be persistent (`allow_always`, `reject_always`) or one-time

**Note**: Client fs and terminal surfaces are removed in v2. Agents should use MCP-based alternatives.

### MCP Credential Handling

MCP server credentials (API keys, OAuth tokens) are passed from the editor to the agent at session creation time via `env` variables or HTTP headers. The agent receives these credentials to connect to MCP servers but does not persist them independently. [VERIFIED] (ACP-SC-ACPORG-SSSTP)

## Quick Reference

- **Advertise auth**: `authMethods` array in `initialize` response
- **Authenticate**: `authenticate` (v1) / `auth/login` (v2)
- **Logout**: `logout` (v1) / `auth/logout` (v2)
- **Auth trigger**: the agent rejects session methods with an authentication error until `authenticate` succeeds [ASSUMED - exact error code not verified; `auth_required` is NOT a v1 StopReason (verified enum: end_turn, max_tokens, max_turn_requests, refusal, cancelled)]
- **Default auth type**: `"agent"` (agent handles the flow)

## Limitations and Gotchas

- No built-in credential storage or token refresh mechanism
- The `authenticate` request is blocking (may take significant time for browser-based OAuth)
- No standard way to check whether the agent is currently authenticated
- Trust model assumes local subprocess; remote agents need additional security layers
- `logout` does not guarantee cleanup of agent-side cached credentials
- v2 renames both auth methods and changes the requirement model

## Sources

- ACP-SC-ACPORG-AUTH - Official authentication page
- ACP-SC-ACPORG-ARCH - Design philosophy (trust model)
- ACP-SC-ACPORG-UPDTS - Logout method stabilization
- ACP-SC-ACPORG-SSSTP - MCP credential handling
- ACP-SC-ACPORG-V2MIG - v2 authentication method renames
- ACP-SC-MRPH-EXPL - Permission model and security overview

## Document History

**[2026-08-30 14:20]**
- Fixed: removed hallucinated `stopReason: "auth_required"` claim - not part of the verified v1 StopReason enum; auth requirement surfaces as an error on session methods [ASSUMED]

**[2026-08-30 03:50]**
- Updated from ACP-AgentClientProtocol_2026-06-12
- Added: v2 authentication changes (auth/login, auth/logout renames, requirement model)
- Added: Note about client fs/terminal removal in v2

**[2026-06-12 10:05]**
- Initial document created
