"""todo_list executor: full-replace state + byte-stable rendering - the deterministic compaction anchor (IS-10, IG-04)."""
import json
from lana.tools import ToolContext

TODO_RESULT_PREFIX = "Todo list updated:"


# Byte-stable rendering: same items always produce identical output (TC-24); compaction extracts this JSON verbatim
def render_todo_result(todos: list[dict]) -> str:
  return TODO_RESULT_PREFIX + "\n" + json.dumps(todos, indent=2, ensure_ascii=False, sort_keys=True)


def execute_todo_list(args: dict, context: ToolContext) -> str:
  context.todo_state = args["todos"]
  return render_todo_result(args["todos"])
