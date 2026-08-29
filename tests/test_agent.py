"""TK-019/020: agent turn loop (IP01 TC-32..34)."""
from lana.session import resume
from tests.conftest import collect_events, collect_until
from tests.harness import assert_event_order


# TC-32: scripted 3-tool-call turn -> correct event sequence, complete JSONL (IG-02)
def test_tc32_three_tool_call_turn(agent_factory, tmp_path):
  workspace_file = tmp_path / "ws" / "notes.md"
  workspace_file.parent.mkdir(exist_ok=True)
  workspace_file.write_text("note body\n", encoding="utf-8")
  turns = [
    {"text": "Reading.", "tool_calls": [
      {"name": "read_file", "args": {"file_path": str(workspace_file)}},
      {"name": "list_dir", "args": {"DirectoryPath": str(workspace_file.parent)}},
      {"name": "todo_list", "args": {"todos": [{"id": "1", "content": "step", "status": "pending", "priority": "high"}]}},
    ], "usage": {"input": 900, "output": 30}},
    {"text": "All done.", "usage": {"input": 1100, "output": 12}},
  ]
  agent = agent_factory(turns)
  events = collect_events(agent, "check the notes")
  assert_event_order(events, ["user_message", "turn_started", "text_delta", "tool_call_requested", "tool_call_finished", "tool_call_requested", "tool_call_finished", "tool_call_requested", "tool_call_finished", "turn_finished", "turn_started", "text_delta", "turn_finished"])
  finished = [event for event in events if event.type == "tool_call_finished"]
  assert all(event.status == "ok" for event in finished)
  assert agent.final_text == "All done." and agent.stop_reason is None
  persisted = resume(agent.session.path)  # IG-02: every event in the JSONL
  assert [event.type for event in persisted.events] == [event.type for event in events]
  assert persisted.todo_state == [{"id": "1", "content": "step", "status": "pending", "priority": "high"}]


# TC-33: call limit (EC-11) -> stop with error event; auto_continue -> no pause
def test_tc33_call_limit_and_auto_continue(agent_factory, tmp_path):
  target_dir = str(tmp_path / "ws")
  calls = [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}] * 3
  turns = [{"text": "burst", "tool_calls": calls}, {"text": "never reached"}]
  agent = agent_factory(turns, lana_overrides={"max_tool_calls_per_prompt": 2})
  events = collect_events(agent, "go")
  assert agent.stop_reason == "limit"
  assert any(event.type == "error" and "limit" in event.message for event in events)
  assert sum(1 for event in events if event.type == "tool_call_finished") == 2  # third call never executed


def test_tc33b_auto_continue_skips_pause(agent_factory, tmp_path):
  target_dir = str(tmp_path / "ws")
  calls = [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}] * 3
  turns = [{"text": "burst", "tool_calls": calls}, {"text": "finished"}]
  agent = agent_factory(turns, lana_overrides={"max_tool_calls_per_prompt": 2, "auto_continue": True})
  events = collect_events(agent, "go")
  assert agent.stop_reason is None and agent.final_text == "finished"
  assert sum(1 for event in events if event.type == "tool_call_finished") == 3


def test_continue_callback_resumes(agent_factory, tmp_path):
  target_dir = str(tmp_path / "ws")
  calls = [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}] * 3
  turns = [{"text": "burst", "tool_calls": calls}, {"text": "finished"}]
  asked = []
  agent = agent_factory(turns, lana_overrides={"max_tool_calls_per_prompt": 2}, continue_callback=lambda count: asked.append(count) or True)
  collect_events(agent, "go")
  assert asked == [2] and agent.stop_reason is None


# TC-34: cancellation mid-loop (EC-10) -> completed calls kept + synthetic note; resume reflects it
def test_tc34_cancellation_keeps_results(agent_factory, tmp_path):
  target_dir = str(tmp_path / "ws")
  calls = [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}] * 3
  turns = [{"text": "burst", "tool_calls": calls}, {"text": "never"}]
  agent = agent_factory(turns)
  seen = {"count": 0}

  def after_second_result(event):
    if event.type == "tool_call_finished": seen["count"] += 1
    return seen["count"] == 2

  collect_until(agent, "go", after_second_result)
  note = agent.note_cancellation()
  assert note == "turn cancelled after 2 tool calls" and agent.stop_reason == "cancelled"
  assert any(message.role == "user" and "cancellation_note" in message.content for message in agent.messages)
  resumed = resume(agent.session.path)
  tool_messages = [message for message in resumed.messages if message.role == "tool"]
  assert len(tool_messages) == 2  # completed results kept
  assert any("turn cancelled after 2 tool calls" in message.content for message in resumed.messages)


def test_unknown_tool_and_bad_args_keep_loop_alive(agent_factory):
  turns = [
    {"text": "trying", "tool_calls": [{"name": "read_file", "args": {"file_path": "e:/definitely/missing.txt"}}]},
    {"text": "recovered"},
  ]
  agent = agent_factory(turns)
  events = collect_events(agent, "go")
  error_result = [event for event in events if event.type == "tool_call_finished"][0]
  assert error_result.status == "error" and "not found" in error_result.result
  assert agent.final_text == "recovered" and agent.stop_reason is None


def test_provider_error_stops_with_error_event(agent_factory):
  agent = agent_factory([{"error": "simulated 500"}])
  events = collect_events(agent, "go")
  assert agent.stop_reason == "provider_error"
  assert any(event.type == "error" and "simulated 500" in event.message for event in events)


def test_denylisted_command_denied_without_callback(agent_factory, tmp_path):
  turns = [
    {"text": "removing", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "Remove-Item x", "SafeToAutoRun": True}}]},
    {"text": "done anyway"},
  ]
  agent = agent_factory(turns, lana_overrides={"execution_policy": "turbo"})
  events = collect_events(agent, "go")
  denial = [event for event in events if event.type == "tool_call_finished"][0]
  assert denial.status == "error" and "approval denied (non-interactive session)" in denial.result
  assert any(event.type == "approval_required" and event.approved is False for event in events)
  assert agent.final_text == "done anyway"  # loop continues after denial (TC-52 semantics)


def test_user_metadata_in_user_message_not_system_prompt(agent_factory):
  agent = agent_factory([{"text": "ok"}])
  collect_events(agent, "hello")
  assert "<user_metadata>" in agent.messages[0].content and "date:" in agent.messages[0].content
  assert "<user_metadata>" not in agent.system_prompt
