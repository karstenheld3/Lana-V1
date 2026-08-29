"""TK-014: todo_list byte-stable rendering (IP01 TC-24, IG-04 anchor)."""
from lana.tools import ToolContext
from lana.tools.state_tools import execute_todo_list, render_todo_result

TODOS = [
  {"id": "1", "content": "Implement loader", "status": "completed", "priority": "high"},
  {"id": "2", "content": "Wire agent loop", "status": "in_progress", "priority": "high"},
  {"id": "3", "content": "Polish renderer", "status": "pending", "priority": "low"},
]


# TC-24: byte-stable rendering - identical input always produces identical bytes (compaction extraction anchor)
def test_tc24_byte_stable_rendering(tmp_path):
  context = ToolContext(workspace=tmp_path)
  first = execute_todo_list({"todos": TODOS}, context)
  second = execute_todo_list({"todos": TODOS}, context)
  assert first == second == render_todo_result(TODOS)
  assert first.startswith("Todo list updated:\n")
  assert context.todo_state == TODOS


def test_todo_state_full_replace(tmp_path):
  context = ToolContext(workspace=tmp_path)
  execute_todo_list({"todos": TODOS}, context)
  replacement = [{"id": "9", "content": "Only item", "status": "pending", "priority": "medium"}]
  execute_todo_list({"todos": replacement}, context)
  assert context.todo_state == replacement
