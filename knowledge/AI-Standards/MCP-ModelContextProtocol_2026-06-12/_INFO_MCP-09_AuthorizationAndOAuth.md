# MCP: Authorization and OAuth

**Doc ID**: MCP-IN09
**Goal**: Document the MCP authorization framework including OAuth 2.1, discovery, and client registration
**Version scope**: Spec 2025-11-25 (current)

**Depends on:**
- `_INFO_MCP-07_TransportsAndUtilities.md [MCP-IN07]` for transport context
- `_INFO_MCP-02_Sources.md [MCP-IN02]` for source references

## Summary

MCP uses OAuth 2.1 with Proof Key for Code Exchange (PKCE) for authorization on Streamable HTTP transports. Authorization server discovery follows OpenID Connect (OIDC) and RFC 9728 patterns. Three client registration approaches are supported: Client ID Metadata Documents (added 2025-11-25), dynamic registration (RFC 7591), and pre-registration. Incremental scope consent allows servers to request additional permissions as needed. Enterprise deployments can use managed authorization servers. Machine-to-machine communication uses OAuth client credentials flow.

## Overview

MCP authorization is based on OAuth 2.1, added in spec version 2025-06-18. [VERIFIED, spec]

**Roles** (mapping to OAuth 2.1):
- **MCP server** = OAuth 2.1 Resource Server (accepts protected resource requests with access tokens)
- **MCP client** = OAuth 2.1 Client (makes protected resource requests on behalf of resource owner)
- **Authorization server** = Issues access tokens (may be hosted with resource server or separate)

## Requirements

[VERIFIED, spec]
1. Authorization servers MUST implement OAuth 2.1 with appropriate security for confidential and public clients
2. Authorization servers and clients SHOULD support OAuth Client ID Metadata Documents
3. Authorization servers and clients MAY support Dynamic Client Registration (RFC 7591)
4. MCP servers MUST implement OAuth 2.0 Protected Resource Metadata (RFC 9728)
5. MCP authorization servers MUST provide at least one discovery mechanism:
   - OAuth 2.0 Authorization Server Metadata (RFC 8414), or
   - OpenID Connect Discovery 1.0

## Authorization Server Discovery

MCP servers advertise their authorization servers via Protected Resource Metadata. [VERIFIED, spec]

**Discovery sequence**:
1. Client sends MCP request without token
2. Server responds HTTP 401 with `WWW-Authenticate` header containing `resource_metadata` URL
3. Client fetches Protected Resource Metadata from server
4. Client extracts authorization server URL(s)
5. Client discovers authorization server metadata (try OAuth 2.0 and OIDC endpoints in priority order)

If `WWW-Authenticate` is absent, client falls back to `.well-known` endpoint discovery (RFC 9728). [VERIFIED, spec: SEP-985]

## Client Registration

Three approaches, in priority order: [VERIFIED, spec]

### 1. Pre-registration (highest priority)

Use when client and server have existing relationship. Client has pre-registered `client_id`.

### 2. Client ID Metadata Documents (recommended, 2025-11-25)

When client and server have no prior relationship. [VERIFIED, spec: SEP-991]

- Client uses an HTTPS URL as its `client_id`
- Authorization server detects URL-formatted client_id
- Server fetches metadata document from client_id URL
- Document contains redirect URIs and other client metadata
- Server validates metadata and redirect URIs

**Innovation**: Server-controlled trust without pre-coordination. Eliminates need for dynamic registration in most cases.

### 3. Dynamic Client Registration (fallback)

Uses RFC 7591. Client POSTs to registration endpoint, receives client credentials. Used for backwards compatibility or specific requirements.

### 4. User-provided (last resort)

Prompt user to enter client information manually.

## Authorization Flow

[VERIFIED, spec] Complete flow:

1. Client sends MCP request without token
2. Server responds 401 with `WWW-Authenticate`
3. Client discovers authorization server metadata
4. Client registers (via one of 3 approaches)
5. Client generates PKCE parameters
6. Client opens browser with authorization URL + code_challenge + `resource` parameter
7. User authorizes at authorization server
8. Authorization server redirects with authorization code
9. Client exchanges code for access token (+ refresh token) with code_verifier + `resource`
10. Client makes MCP requests with access token

**Resource Parameter**: Clients MUST implement RFC 8707 Resource Indicators. `resource` parameter MUST be included in both authorization and token requests, identifying the MCP server.

## Scope Selection Strategy

[VERIFIED, spec] Principle of least privilege:
1. Use `scope` from initial `WWW-Authenticate` header if provided
2. Otherwise use all scopes from `scopes_supported` in Protected Resource Metadata
3. Additional scopes requested incrementally via step-up authorization (scope challenge handling)

## OAuth Client Credentials Extension

For machine-to-machine authentication without user interaction. [VERIFIED, spec]

**Use cases**: Background services, CI/CD pipelines, server-to-server integrations, daemon processes.

**Two credential formats**:
- **JWT Bearer Assertions** (recommended): Client signs JWT with private key, sends as assertion
- **Client Secrets**: Traditional client_id + client_secret pair

No browser redirect or user interaction required.

## Enterprise-Managed Authorization

For organizations that want centralized control over MCP authorization. [VERIFIED, spec]

Enables enterprise IdP policy controls during MCP OAuth flows. Organizations can enforce:
- Which MCP servers users can connect to
- What scopes are permitted
- Single sign-on via existing identity providers

## Token Handling

[VERIFIED, spec]
- Clients MUST include access token in Authorization header: `Authorization: Bearer <token>`
- Servers MUST validate token audience and scope
- Clients MUST handle token refresh when tokens expire
- Clients MUST handle 401 responses by re-initiating authorization flow if token is invalid

## Security Considerations

[VERIFIED, spec]
- **Token Audience Binding**: Tokens MUST be scoped to specific resource server (prevents token reuse across servers)
- **Token Theft**: Use short-lived tokens, TLS for all communication
- **Authorization Code Protection**: PKCE required for all flows
- **Open Redirection**: Validate redirect URIs strictly
- **Client ID Metadata Security**: Validate fetched metadata documents
- **Confused Deputy**: See `_INFO_MCP-11_SecurityAndBestPractices.md` for detailed attack description

## Limitations and Known Issues

- Authorization applies only to Streamable HTTP transport - stdio has no built-in auth mechanism
- PKCE is required but does not protect against compromised authorization servers
- Client ID Metadata Documents require HTTPS hosting and cross-origin fetch - adds deployment complexity
- No standard for revoking tokens across all MCP sessions simultaneously
- Server-Side Request Forgery (SSRF) risk during authorization server discovery if URL validation is insufficient

## Sources

- MCP-SC-MCPIO-SPEC2511 (Authorization section)
- MCP-SC-MCPIO-LLMSFULL (positions 105-118, 151-162, 184-201)

## Document History

**[2026-06-12 10:05]**
- Initial topic file with OAuth 2.1 framework, discovery, registration, flow, and extensions
