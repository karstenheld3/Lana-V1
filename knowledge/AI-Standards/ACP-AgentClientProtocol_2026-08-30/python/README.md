# ACP Python SDK Verification

SDK verification for the `agent-client-protocol` Python package against `_INFO_*.md` documentation.

## SDK Details

- **Package**: `agent-client-protocol`
- **Version**: 0.12.1
- **Python**: 3.12.0
- **Install**: `pip install agent-client-protocol`

## Test Results

**27 passed, 0 failed, 0 skipped** (3 test files, 2.8s)

- `01_imports_schema_test.py` (11 tests): Package imports, schema model instantiation (IN04-IN08)
- `02_helpers_builders_test.py` (8 tests): Helper builders, serialization, MCP config (IN05-IN12)
- `03_transport_contrib_test.py` (8 tests): Transport classes, contrib modules, elicitation schema (IN10-IN15)

## SDK Introspection

- **Submodules**: 38
- **Public classes**: 633
- **Public functions**: 142
- **Import errors**: 0

See `sdk_methods.json` for full API surface.

## Key SDK Findings

1. **Flat Pydantic models**: Schema classes represent JSON-RPC params directly (not envelope wrappers). `InitializeRequest(protocolVersion=1)`, not `InitializeRequest(id=0, method="initialize", params=...)`.
2. **Literal type aliases**: `PermissionOptionKind`, `StopReason`, `ToolCallKind` are `typing.Literal` aliases, not Python enums. Access values via `.__args__`.
3. **snake_case serialization**: `model_dump()` produces snake_case keys (`protocol_version`), not camelCase (`protocolVersion`). The SDK handles JSON-RPC wire format conversion internally.
4. **Content blocks**: Prompt content uses `TextContentBlock(type="text", text="...")` (discriminated union), while `TextContent` is a simpler model without `type` field.
5. **MCP config as list**: `NewSessionRequest.mcpServers` is a list of `McpServerStdio`/`McpServerHttp` objects (each with `name`), not a dict keyed by name as shown in the wire format examples.
6. **Required fields**: `McpServerStdio` requires `name`, `command`, `args`, `env` (all mandatory). `NewSessionRequest` requires `cwd` and `mcpServers`.
7. **Transport modules**: Both `StdioTransport` and `WebTransport` (HTTP/WS) are importable in v0.12.1.
8. **Elicitation schema**: `ElicitationCreateRequest` is available, confirming v1.19.0 schema support.
9. **Contrib utilities**: `contrib` module available with session accumulator, tool call tracker, permission broker helpers.

## Reproduction

```bash
pip install agent-client-protocol==0.12.1
cd docs/AI-Standards/ACP-AgentClientProtocol_2026-08-30/python
python sdk_methods.py     # SDK introspection
python run_all.py         # All tests
python 01_imports_schema_test.py  # Individual suite
```

## File Structure

```
python/
  _lib.py                          # Shared test harness
  sdk_methods.py                   # SDK introspection script
  sdk_methods.json                 # SDK API surface (633 classes, 142 functions)
  run_all.py                       # Test runner / aggregator
  run_all_summary.json             # Aggregated results
  01_imports_schema_test.py        # Import and schema model tests
  01_imports_schema_results.json   # Results
  02_helpers_builders_test.py      # Helper builder tests
  02_helpers_builders_results.json # Results
  03_transport_contrib_test.py     # Transport and contrib tests
  03_transport_contrib_results.json # Results
  README.md                        # This file
```

## Documentation Bugs Found

None. All INFO file JSON-RPC wire format examples are correct protocol representations. SDK internal representations differ from wire format in expected ways (list vs dict for mcpServers, snake_case vs camelCase). SDK examples in IN05 and IN12 are appropriately marked as simplified with "verify exact API" notes.
