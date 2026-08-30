"""IN16: Structured outputs - JSON schema, Pydantic parse, strict tools."""
import json, sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from pydantic import BaseModel
from _lib import client, test, finish, DEFAULT_MODEL

class LeadInfo(BaseModel):
  name: str
  email: str
  plan_interest: str
  demo_requested: bool

def test_json_schema():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=1024,
    output_config={
      "format": {
        "type": "json_schema",
        "schema": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "plan_interest": {"type": "string", "enum": ["Starter", "Pro", "Enterprise"]},
            "demo_requested": {"type": "boolean"},
          },
          "required": ["name", "email", "plan_interest", "demo_requested"],
          "additionalProperties": False,
        },
      }
    },
    messages=[{"role": "user", "content": "Extract: John Smith, john@example.com, Enterprise plan, wants demo"}],
  )
  data = json.loads(msg.content[0].text)
  return {"parsed": data, "has_all_fields": all(k in data for k in ["name", "email", "plan_interest", "demo_requested"])}

test("JSON schema output (output_config.format)", test_json_schema)

def test_pydantic_parse():
  result = client.messages.parse(
    model=DEFAULT_MODEL, max_tokens=1024,
    output_format=LeadInfo,
    messages=[{"role": "user", "content": "Extract: John Smith, john@example.com, Enterprise plan, wants demo"}],
  )
  return {"parsed_type": type(result.parsed_output).__name__, "name": result.parsed_output.name}

test("Pydantic parse (client.messages.parse)", test_pydantic_parse)

def test_strict_tools():
  msg = client.messages.create(
    model=DEFAULT_MODEL, max_tokens=1024,
    tools=[{
      "name": "create_order",
      "description": "Create a new order",
      "input_schema": {
        "type": "object",
        "properties": {
          "product_id": {"type": "string"},
          "quantity": {"type": "integer"},
          "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        },
        "required": ["product_id", "quantity", "priority"],
        "additionalProperties": False,
      },
      "strict": True,
    }],
    tool_choice={"type": "tool", "name": "create_order"},
    messages=[{"role": "user", "content": "Order 5 units of SKU-123, high priority"}],
  )
  tool_block = next((b for b in msg.content if b.type == "tool_use"), None)
  return {"has_tool": tool_block is not None, "input": tool_block.input if tool_block else None}

test("Strict tool use (strict: true)", test_strict_tools)

finish(__file__)
