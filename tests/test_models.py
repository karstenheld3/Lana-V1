"""TK-002: canonical model validation and round-trip."""
import pytest
from lana.models import Message, ThinkingBlock, ToolCall, Usage


def test_message_round_trip():
  message = Message(role="assistant", content="hello", tool_calls=[ToolCall(id="tc_1", name="read_file", args_json='{"file_path": "x.md"}')],
                    thinking=[ThinkingBlock(provider="anthropic", payload={"signature": "abc", "thinking": "hmm"})], usage=Usage(input_tokens=10, output_tokens=5))
  restored = Message.model_validate_json(message.model_dump_json())
  assert restored == message
  assert restored.tool_calls[0].args() == {"file_path": "x.md"}


def test_tool_call_invalid_args_raises():
  call = ToolCall(id="tc_1", name="edit", args_json="{not json")
  with pytest.raises(Exception): call.args()


def test_tool_call_non_object_args_raises():
  call = ToolCall(id="tc_1", name="edit", args_json='[1, 2]')
  with pytest.raises(ValueError): call.args()


def test_usage_add():
  total = Usage(input_tokens=100, output_tokens=10, cache_read_tokens=80).add(Usage(input_tokens=50, output_tokens=5, cache_read_tokens=40))
  assert (total.input_tokens, total.output_tokens, total.cache_read_tokens) == (150, 15, 120)
