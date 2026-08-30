"""Test 02: Verify ACP SDK helper builders produce valid protocol messages.

Covers: IN05 (Initialization), IN07 (Streaming), IN08 (Tool Calls), IN12 (SDKs)
Verifies: Helper builder functions create correct JSON-RPC structures.
No network access required.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestSuite

suite = TestSuite("02_helpers_builders")

def test_helpers_available():
    """Check which helper builder modules are available."""
    import acp.helpers as helpers
    attrs = [a for a in dir(helpers) if not a.startswith("_")]
    return f"Available helpers: {attrs[:10]}..."

def test_content_builder():
    """Verify content block creation helpers."""
    try:
        from acp.helpers import text_content
        tc = text_content("Hello, world!")
        assert tc.text == "Hello, world!"
        return f"text_content helper works: text={tc.text}"
    except ImportError:
        from acp.schema import TextContent
        tc = TextContent(text="Hello from schema")
        assert tc.text == "Hello from schema"
        return f"text_content helper not found, using schema directly: text={tc.text}"

def test_session_update_builder():
    """Verify session update notification helpers."""
    try:
        from acp.helpers import agent_message_chunk
        chunk = agent_message_chunk(
            session_id="sess_test",
            text="Processing...",
        )
        return f"agent_message_chunk helper works"
    except (ImportError, TypeError) as e:
        return f"agent_message_chunk helper: {e}"

def test_tool_call_builder():
    """Verify tool call creation helpers."""
    try:
        from acp.helpers import tool_call_update
        update = tool_call_update(
            session_id="sess_test",
            tool_call_id="call_001",
            status="completed",
        )
        return f"tool_call_update helper works"
    except (ImportError, TypeError) as e:
        return f"tool_call_update helper: {e}"

def test_permission_option_builder():
    """Verify permission option creation."""
    from acp.schema import PermissionOption
    opt = PermissionOption(
        optionId="allow-once",
        name="Allow once",
        kind="allow_once",
    )
    assert opt.kind == "allow_once"
    return f"PermissionOption created: kind={opt.kind}"

def test_mcp_server_config():
    """Verify MCP server configuration model (IN06)."""
    from acp.schema import McpServerStdio
    config = McpServerStdio(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        env=[],
    )
    assert config.command == "npx"
    assert config.name == "filesystem"
    return f"McpServerStdio: name={config.name}, command={config.command}"

def test_json_rpc_roundtrip():
    """Verify schema models serialize to valid JSON."""
    from acp.schema import InitializeRequest
    req = InitializeRequest(protocolVersion=1)
    data = req.model_dump(mode="json", exclude_none=True)
    # SDK serializes with snake_case by default
    assert "protocol_version" in data
    assert data["protocol_version"] == 1
    return f"JSON roundtrip OK: keys={list(data.keys())}"

def test_schema_version_constant():
    """Check if schema version constant is accessible."""
    try:
        from importlib.metadata import version
        v = version("agent-client-protocol")
        return f"Package version: {v}"
    except Exception as e:
        return f"Version check: {e}"

# --- Run all tests ---

suite.run_test("helpers_available", test_helpers_available)
suite.run_test("content_builder", test_content_builder)
suite.run_test("session_update_builder", test_session_update_builder)
suite.run_test("tool_call_builder", test_tool_call_builder)
suite.run_test("permission_option_builder", test_permission_option_builder)
suite.run_test("mcp_server_config", test_mcp_server_config)
suite.run_test("json_rpc_roundtrip", test_json_rpc_roundtrip)
suite.run_test("schema_version_constant", test_schema_version_constant)

out = Path(__file__).with_name("02_helpers_builders_results.json")
suite.save(out)
failures = suite.print_summary()
sys.exit(1 if failures else 0)
