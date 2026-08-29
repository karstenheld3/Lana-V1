"""TK-021: session store flush + resume projection (IP01 TC-35, FR-08, IG-06)."""
from lana import events
from lana.session import SessionStore, resume
from tests.conftest import collect_events


def test_per_line_flush_visible_to_external_reader(tmp_path):
  store = SessionStore(tmp_path / "s.jsonl")
  store.append(events.UserMessage(content="hi"))
  content = (tmp_path / "s.jsonl").read_text(encoding="utf-8")  # read WITHOUT closing the writer
  assert '"user_message"' in content and content.endswith("\n")
  store.close()


# TC-35: resume after simulated crash with truncated last line (EC-21)
def test_tc35_resume_skips_truncated_line(agent_factory, tmp_path):
  agent = agent_factory([{"text": "reply one", "usage": {"input": 500, "output": 20}}])
  collect_events(agent, "first prompt")
  with open(agent.session.path, "a", encoding="utf-8") as handle: handle.write('{"ts": "2026-08-30 01:00:00", "type": "text_del')  # crash mid-write
  state = resume(agent.session.path)
  assert state.skipped_lines == 1
  assert [message.role for message in state.messages] == ["user", "assistant"]
  assert state.messages[0].content == "first prompt" and state.messages[1].content == "reply one"
  assert state.usage_by_role["generator"].input_tokens == 500


def test_resume_projection_tool_round_trip(agent_factory, tmp_path):
  workspace_file = tmp_path / "ws" / "data.txt"
  workspace_file.parent.mkdir(exist_ok=True)
  workspace_file.write_text("payload", encoding="utf-8")
  turns = [
    {"text": "reading", "tool_calls": [{"name": "read_file", "args": {"file_path": str(workspace_file)}}], "usage": {"input": 700, "output": 25}},
    {"text": "final answer", "usage": {"input": 900, "output": 15}},
  ]
  agent = agent_factory(turns)
  collect_events(agent, "read it")
  state = resume(agent.session.path)
  roles = [message.role for message in state.messages]
  assert roles == ["user", "assistant", "tool", "assistant"]
  assert state.messages[1].tool_calls[0].name == "read_file" and state.messages[1].tool_calls[0].status == "ok"
  assert "payload" in state.messages[2].content
  assert state.messages[3].content == "final answer"
  assert state.usage_by_role["generator"].input_tokens == 1600  # both turns accumulated


def test_resume_applies_checkpoint(tmp_path):
  store = SessionStore(tmp_path / "s.jsonl")
  store.append(events.UserMessage(content="old prompt"))
  store.append(events.TurnStarted())
  store.append(events.TextDelta(text="old answer"))
  store.append(events.TurnFinished(input_tokens=100, output_tokens=10))
  store.append(events.CheckpointCreated(text="CHECKPOINT BODY", truncated_messages=2, kept_messages=0))
  store.append(events.UserMessage(content="new prompt"))
  store.append(events.TurnStarted())
  store.append(events.TextDelta(text="new answer"))
  store.append(events.TurnFinished(input_tokens=50, output_tokens=5))
  store.close()
  state = resume(tmp_path / "s.jsonl")
  assert [message.role for message in state.messages] == ["user", "user", "assistant"]
  assert state.messages[0].content == "CHECKPOINT BODY"
  assert state.messages[1].content == "new prompt" and state.messages[2].content == "new answer"


def test_session_files_never_deleted_and_unique(tmp_path):
  first = SessionStore.create(tmp_path)
  second = SessionStore.create(tmp_path)
  assert first.path != second.path  # EC-13: two instances, distinct files
  first.close(); second.close()
  assert first.path.exists() and second.path.exists()
