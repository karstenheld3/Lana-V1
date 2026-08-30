"""Test 01: Verify ACP SDK imports and schema model instantiation.

Covers: IN04 (Architecture), IN05 (Initialization), IN06 (Session Lifecycle)
Verifies: Package imports, schema models, Pydantic validation.
No network access required.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestSuite

suite = TestSuite("01_imports_schema")

# --- Import tests ---

def test_import_acp():
    import acp
    return f"acp package imported: {dir(acp)[:5]}..."

def test_import_schema():
    import acp.schema as schema
    attrs = [a for a in dir(schema) if not a.startswith("_")]
    return f"acp.schema has {len(attrs)} public attributes"

def test_import_helpers():
    import acp.helpers as helpers
    attrs = [a for a in dir(helpers) if not a.startswith("_")]
    return f"acp.helpers has {len(attrs)} public attributes"

# --- Schema model tests ---

def test_initialize_request():
    """Verify InitializeRequest schema model (IN05)."""
    from acp.schema import InitializeRequest
    req = InitializeRequest(protocolVersion=1)
    assert req.protocolVersion == 1
    return f"InitializeRequest created: protocolVersion={req.protocolVersion}"

def test_initialize_response():
    """Verify InitializeResponse schema model (IN05)."""
    from acp.schema import InitializeResponse
    resp = InitializeResponse(protocolVersion=1)
    assert resp.protocolVersion == 1
    return f"InitializeResponse created: protocolVersion={resp.protocolVersion}"

def test_new_session_request():
    """Verify NewSessionRequest schema model (IN06)."""
    from acp.schema import NewSessionRequest
    req = NewSessionRequest(cwd="/home/user/project", mcpServers=[])
    assert req.cwd == "/home/user/project"
    return f"NewSessionRequest created: cwd={req.cwd}"

def test_prompt_request():
    """Verify PromptRequest schema model (IN07)."""
    from acp.schema import PromptRequest, TextContentBlock
    req = PromptRequest(
        sessionId="sess_abc123",
        prompt=[TextContentBlock(type="text", text="Hello")],
    )
    assert req.sessionId == "sess_abc123"
    assert len(req.prompt) == 1
    return f"PromptRequest created: sessionId={req.sessionId}"

def test_text_content():
    """Verify TextContent schema model (IN07)."""
    from acp.schema import TextContent
    tc = TextContent(text="Hello, world!")
    assert tc.text == "Hello, world!"
    data = tc.model_dump()
    assert "text" in data
    return f"TextContent: text={tc.text[:20]}"

def test_tool_call_start():
    """Verify ToolCallStart schema types exist (IN08)."""
    from acp.schema import ToolCallStart
    update = ToolCallStart(
        sessionUpdate="tool_call",
        toolCallId="call_001",
        title="Reading file",
        kind="read",
        status="pending",
    )
    assert update.toolCallId == "call_001"
    return f"ToolCallStart: id={update.toolCallId}, kind={update.kind}"

def test_permission_kinds():
    """Verify permission option kinds exist (IN08)."""
    from acp.schema import PermissionOptionKind
    # PermissionOptionKind is a Literal type alias, not an enum
    kinds = list(PermissionOptionKind.__args__)
    assert "allow_once" in kinds
    assert "reject_once" in kinds
    return f"PermissionOptionKind values: {kinds}"

def test_stop_reasons():
    """Verify StopReason Literal values (IN07)."""
    from acp.schema import StopReason
    # StopReason is a Literal type alias, not an enum
    reasons = list(StopReason.__args__)
    assert "end_turn" in reasons
    assert "cancelled" in reasons
    return f"StopReason values: {reasons}"

# --- Run all tests ---

suite.run_test("import_acp", test_import_acp)
suite.run_test("import_schema", test_import_schema)
suite.run_test("import_helpers", test_import_helpers)
suite.run_test("initialize_request", test_initialize_request)
suite.run_test("initialize_response", test_initialize_response)
suite.run_test("new_session_request", test_new_session_request)
suite.run_test("prompt_request", test_prompt_request)
suite.run_test("text_content", test_text_content)
suite.run_test("tool_call_start", test_tool_call_start)
suite.run_test("permission_kinds", test_permission_kinds)
suite.run_test("stop_reasons", test_stop_reasons)

out = Path(__file__).with_name("01_imports_schema_results.json")
suite.save(out)
failures = suite.print_summary()
sys.exit(1 if failures else 0)
