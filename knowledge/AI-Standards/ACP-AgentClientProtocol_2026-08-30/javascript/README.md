# ACP TypeScript SDK Verification

SDK verification for the `@agentclientprotocol/sdk` TypeScript package against `_INFO_*.md` documentation.

## SDK Details

- **Package**: `@agentclientprotocol/sdk`
- **Version**: 1.4.0
- **Node.js**: v22.21.1
- **Install**: `npm install @agentclientprotocol/sdk`

## Test Results

**38 passed, 0 failed, 0 skipped** (2 test files)

- `sdk_examples_test.cjs` (17 tests): Package imports, v1/v2 classes, schemas, error handling
- `sdk_test.cjs` (21 tests): Class structure, methods, transports, v2 comparison, schema definitions

## SDK Introspection

- **Export paths**: 8 (main, experimental/v2, experimental/http-client, experimental/ws-client, experimental/server, experimental/node, schema/schema.json, schema/v2/schema.unstable.json)
- **Total exports**: 76
- **Classes**: 21
- **Functions**: 13
- **Import errors**: 0

See `sdk_methods.json` for full API surface.

## Key SDK Findings

1. **Class naming**: SDK uses `AgentApp` (not `Agent`), `ClientApp` (not `Client`), `ActiveSession` (not `Session`). Also: `SessionBuilder`, `AgentContext`, `ClientContext`, `AgentSideConnection`, `ClientSideConnection`.
2. **Handler pattern**: `AgentApp` uses `onRequest(method, handler)` and `onNotification(method, handler)` pattern, not dedicated `handleInitialize`/`handlePrompt` methods.
3. **Connection**: `app.connect(agent.stdio())` for stdio transport. The `agent` and `client` are namespace exports with transport factories.
4. **Error class**: `RequestError` (not `ProtocolError`). Takes `(code, message)` constructor args.
5. **v2 experimental**: Full v2 support via `@agentclientprotocol/sdk/experimental/v2`. Adds: `AgentProtocolRouter`, `StateUpdate`, `SessionUpdate`, `ContentBlock`, `DiffChange`, `PlanUpdateContent`, `ReplayFrom`, `RequestPermissionSubject`, `RequestPermissionOutcome`.
6. **Transport modules**: HTTP client (`experimental/http-client`), WebSocket client (`experimental/ws-client`), server (`experimental/server`), Node helpers (`experimental/node`) all importable.
7. **Elicitation**: `CreateElicitationRequest`, `CreateElicitationResponse`, `ElicitationPropertySchema` exported from main package.
8. **Schema JSON**: Both v1 (`schema/schema.json`) and v2 unstable (`schema/v2/schema.unstable.json`) schemas are bundled and importable.
9. **v1 vs v2 AgentApp diff**: v2 adds `AgentProtocolRouter` support; core methods are identical (connect, connectWith, onConnect, onRequest, onNotification, request, notification).

## Documentation Bugs Found and Fixed

1. **IN12 TypeScript examples**: `createAcpAgent` function does not exist in v1.4.0 SDK. Fixed to use `AgentApp` with `onRequest` pattern.
2. **IN12 TypeScript examples**: Class names corrected: `Agent` -> `AgentApp`, `Session` -> `ActiveSession`, `ProtocolError` -> `RequestError`.
3. **IN12 TypeScript examples**: Handler pattern corrected from callback-style to `onRequest(method, handler)`.

## Reproduction

```bash
cd docs/AI-Standards/ACP-AgentClientProtocol_2026-08-30/javascript
npm install
node sdk_methods.cjs          # SDK introspection
node sdk_examples_test.cjs    # Import and class tests
node sdk_test.cjs             # Structural tests
```

## File Structure

```
javascript/
  package.json                  # npm package with @agentclientprotocol/sdk dependency
  sdk_methods.cjs               # SDK introspection script
  sdk_methods.json              # SDK API surface (76 exports, 21 classes, 13 functions)
  sdk_examples_test.cjs         # Import and class existence tests (17 tests)
  sdk_examples_results.json     # Results
  sdk_test.cjs                  # Structural and schema tests (21 tests)
  sdk_test_results.json         # Results
  README.md                     # This file
```
