"""IN38: Platform compatibility - Bedrock/Vertex class existence."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import anthropic
from _lib import test, finish

def test_bedrock_class():
  return {"exists": hasattr(anthropic, "AnthropicBedrock"), "async_exists": hasattr(anthropic, "AsyncAnthropicBedrock")}

test("AnthropicBedrock class exists", test_bedrock_class)

def test_vertex_class():
  return {"exists": hasattr(anthropic, "AnthropicVertex"), "async_exists": hasattr(anthropic, "AsyncAnthropicVertex")}

test("AnthropicVertex class exists", test_vertex_class)

def test_async_client():
  return {"exists": hasattr(anthropic, "AsyncAnthropic")}

test("AsyncAnthropic class exists", test_async_client)

def test_sdk_version():
  return {"version": anthropic.__version__}

test("SDK version", test_sdk_version)

finish(__file__)
