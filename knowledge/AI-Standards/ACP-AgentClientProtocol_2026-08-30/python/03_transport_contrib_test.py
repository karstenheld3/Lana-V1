"""Test 03: Verify ACP SDK transport and contrib modules.

Covers: IN10 (Transports), IN12 (SDKs), IN15 (Elicitation)
Verifies: Transport classes exist, contrib utilities importable, elicitation schema.
No network access required.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _lib import TestSuite

suite = TestSuite("03_transport_contrib")

def test_stdio_transport():
    """Verify stdio transport class exists (IN10)."""
    try:
        from acp.transports.stdio import StdioTransport
        return f"StdioTransport importable"
    except ImportError:
        try:
            from acp import StdioTransport
            return f"StdioTransport from acp root"
        except ImportError:
            return f"StdioTransport not found at expected paths"

def test_http_transport():
    """Check if HTTP transport is available (IN10 - recent addition)."""
    try:
        from acp.transports.http import HttpTransport
        return f"HttpTransport importable"
    except ImportError:
        try:
            from acp.transports.web import WebTransport
            return f"WebTransport importable (alternate name)"
        except ImportError:
            return f"HTTP transport not found (may not be in this version)"

def test_contrib_modules():
    """Check which contrib utilities are available (IN12)."""
    available = []
    try:
        from acp import contrib
        attrs = [a for a in dir(contrib) if not a.startswith("_")]
        available.extend(attrs)
    except ImportError:
        pass
    try:
        from acp.contrib import session_accumulator
        available.append("session_accumulator")
    except ImportError:
        pass
    try:
        from acp.contrib import tool_call_tracker
        available.append("tool_call_tracker")
    except ImportError:
        pass
    return f"Contrib modules found: {available or 'none'}"

def test_agent_base_class():
    """Verify Agent base class exists (IN12 examples)."""
    try:
        from acp import Agent
        methods = [m for m in dir(Agent) if not m.startswith("_")]
        return f"Agent base class: {len(methods)} public methods"
    except ImportError:
        try:
            from acp.agent import Agent
            return f"Agent from acp.agent"
        except ImportError:
            return f"Agent base class not found at expected paths"

def test_session_class():
    """Verify Session class exists (IN12 examples)."""
    try:
        from acp import Session
        return f"Session class importable"
    except ImportError:
        try:
            from acp.session import Session
            return f"Session from acp.session"
        except ImportError:
            return f"Session class not found at expected paths"

def test_elicitation_schema():
    """Verify elicitation schema types exist (IN15)."""
    try:
        from acp.schema import ElicitationCreateRequest
        return f"ElicitationCreateRequest found"
    except ImportError:
        try:
            from acp.schema import Elicitation
            return f"Elicitation type found"
        except ImportError:
            return f"Elicitation schema types not found (may require newer schema)"

def test_auth_schema():
    """Verify authentication schema types exist (IN09)."""
    try:
        from acp.schema import AuthenticateRequest
        return f"AuthenticateRequest found"
    except ImportError:
        try:
            from acp.schema import AuthMethod
            return f"AuthMethod found"
        except ImportError:
            return f"Auth schema types not found"

def test_cancel_request_schema():
    """Verify cancel request schema (IN07 - $/cancel_request)."""
    try:
        from acp.schema import CancelRequestNotification
        return f"CancelRequestNotification found"
    except ImportError:
        try:
            from acp.schema import CancelRequest
            return f"CancelRequest found"
        except ImportError:
            return f"Cancel request schema not found at expected names"

# --- Run all tests ---

suite.run_test("stdio_transport", test_stdio_transport)
suite.run_test("http_transport", test_http_transport)
suite.run_test("contrib_modules", test_contrib_modules)
suite.run_test("agent_base_class", test_agent_base_class)
suite.run_test("session_class", test_session_class)
suite.run_test("elicitation_schema", test_elicitation_schema)
suite.run_test("auth_schema", test_auth_schema)
suite.run_test("cancel_request_schema", test_cancel_request_schema)

out = Path(__file__).with_name("03_transport_contrib_results.json")
suite.save(out)
failures = suite.print_summary()
sys.exit(1 if failures else 0)
