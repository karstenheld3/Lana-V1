# ACP: Authentication and Security

**Doc ID**: ACP-IN09
**Goal**: Document ACP authentication flows and security model
**Version scope**: ACP Protocol v1 (as of 2026-06-12)

**Depends on:**
- `_INFO_ACP-02_Sources.md [ACP-IN02]` for source references

## Overview

ACP's authentication system allows agents to require sign-in before creating sessions. Authentication methods are advertised during initialization, and the client triggers the chosen method. The broader security model relies on a "trusted agent" assumption: the editor spawns the agent locally and mediates all destructive actions through the permission system. [VERIFIED] (ACP-SC-ACPORG-AUTH, ACP-SC-ACPORG-ARCH)

## Advertising Authentication

Agents declare available authentication methods in their `initialize` response via the `authMethods` array. Each method has an `id`, `name`, and optional `description`: [VERIFIED] (ACP-SC-ACPORG-AUTH)

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

### Authentication Method Types

The default type is `agent`, meaning the agent itself handles the authentication flow (e.g., opening a browser for OAuth). The `type` field can be omitted when it defaults to `"agent"`. [VERIFIED] (ACP-SC-ACPORG-AUTH)

## Authenticating

The client initiates authentication by sending the `authenticate` request with the chosen `methodId`: [VERIFIED] (ACP-SC-ACPORG-AUTH)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "authenticate",
  "params": {
    "methodId": "agent-login"
  }
}
```

The agent performs its authentication flow (which may involve external steps like browser-based OAuth) and responds when complete:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {}
}
```

After successful authentication, the client proceeds with `session/new` or `session/load`. If a `session/prompt` returns `stopReason: "auth_required"`, the client must re-authenticate before continuing.

## Logging Out

Agents that advertise `agentCapabilities.auth.logout` support explicit logout: [VERIFIED] (ACP-SC-ACPORG-AUTH)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "logout",
  "params": {}
}
```

After logout, any active sessions may return `auth_required` stop reasons. The client must re-authenticate to continue.

The logout method was stabilized as part of ACP protocol updates. [VERIFIED] (ACP-SC-ACPORG-UPDTS)

## Security Model

ACP's security design is built on several assumptions: [VERIFIED] (ACP-SC-ACPORG-ARCH, ACP-SC-MRPH-EXPL)

### Trust Model

- **Trusted subprocess**: ACP assumes the agent is a trusted subprocess spawned by the editor. The protocol does not include mechanisms for untrusted remote agents.
- **Editor as gatekeeper**: The editor mediates all agent actions that affect the local environment (file writes, command execution) through the permission system.
- **User in control**: The `session/request_permission` mechanism ensures users can approve or deny individual operations, even during autonomous agent runs.

### Permission-Based Access Control

- File system access is gated by client capabilities (`fs.readTextFile`, `fs.writeTextFile`)
- Terminal access is gated by `clientCapabilities.terminal`
- Individual tool executions can require explicit user permission
- Permission choices can be persistent (`allow_always`, `reject_always`) or one-time

### Model Context Protocol (MCP) Credential Handling

MCP server credentials (API keys, OAuth tokens) are passed from the editor to the agent at session creation time via `env` variables or HTTP headers. The agent receives these credentials to connect to MCP servers but does not persist them independently.

## Quick Reference

- **Advertise auth**: `authMethods` array in `initialize` response
- **Authenticate**: `authenticate` method (client to agent)
- **Logout**: `logout` method (requires `agentCapabilities.auth.logout`)
- **Auth trigger**: `stopReason: "auth_required"` on `session/prompt` response
- **Default auth type**: `"agent"` (agent handles the flow)

## Limitations and Gotchas

- ACP has no built-in credential storage or token refresh mechanism; agents handle this internally
- The `authenticate` request is blocking - the agent may take significant time if it involves browser-based OAuth
- There is no standard way for the client to check whether the agent is currently authenticated
- The trust model assumes local subprocess execution; remote agents need additional security layers not defined in ACP v1
- `logout` invalidates the session state but does not guarantee cleanup of agent-side cached credentials
- v2 Authentication Methods RFD may add more auth types beyond the default `"agent"` type

## Sources

- ACP-SC-ACPORG-AUTH - Official authentication page
- ACP-SC-ACPORG-ARCH - Design philosophy (trust model)
- ACP-SC-ACPORG-UPDTS - Logout method stabilization
- ACP-SC-MRPH-EXPL - Permission model and security overview

## Document History

**[2026-06-12 10:05]**
- Initial document created
