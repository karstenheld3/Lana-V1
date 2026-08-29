"""TK-003: all 10 AgentEvent types serialize and deserialize (IS-02)."""
from lana import events
from lana.events import from_jsonl

ALL_EVENTS = [
  events.UserMessage(content="/prime", expanded_workflow="prime"),
  events.TurnStarted(role="generator"),
  events.TextDelta(text="Hello"),
  events.ThinkingDelta(text="considering..."),
  events.ToolCallRequested(id="tc_1", tool="read_file", args={"file_path": "x.md"}),
  events.ToolCallFinished(id="tc_1", status="ok", result="line 1", result_chars=6),
  events.ApprovalRequired(action="run_command", detail="git status (cwd: e:/tmp)", approved=True),
  events.CheckpointCreated(text="The following is a summary...", truncated_messages=42),
  events.TurnFinished(input_tokens=21050, output_tokens=412, cache_read_tokens=18200, cost_usd=0.0164),
  events.ErrorEvent(message="provider unavailable"),
]


def test_all_10_types_round_trip():
  assert len({event.type for event in ALL_EVENTS}) == 10
  for event in ALL_EVENTS:
    line = event.to_jsonl()
    assert "\n" not in line
    restored = from_jsonl(line)
    assert restored == event


def test_checkpoint_created_carries_payload():
  line = events.CheckpointCreated(text="FULL CHECKPOINT BODY", truncated_messages=7).to_jsonl()
  assert "FULL CHECKPOINT BODY" in line
  assert from_jsonl(line).text == "FULL CHECKPOINT BODY"


def test_user_message_carries_expanded_workflow():
  restored = from_jsonl(events.UserMessage(content="/prime", expanded_workflow="prime").to_jsonl())
  assert restored.expanded_workflow == "prime"


def test_timestamp_format():
  event = events.TextDelta(text="x")
  assert len(event.ts) == 19 and event.ts[4] == "-" and event.ts[10] == " " and event.ts[13] == ":"
