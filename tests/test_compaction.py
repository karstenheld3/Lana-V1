"""TK-027: compaction - projection, checkpoint, todo splice, fail-safe (IP01 TC-36..39, FR-07, IG-04)."""
import json
from lana.compaction import ANCHOR_NO_ACK, ANCHOR_TODO_FOOTER, ANCHOR_TODO_TITLE, build_checkpoint, extract_todo_json, fits_window, projected_tokens
from lana.models import Message, Usage
from tests.conftest import collect_events

SUMMARY_TEXT = "# Objective:\nFinish the demo.\n# Session Summary:\nWe worked.\n# Code Interaction Summary:\nEdited files."
TODOS = [{"id": "1", "content": "keep going", "status": "in_progress", "priority": "high"}]

# Overrides that force compaction after the first turn: threshold min(0.6 x 200000, 40) = 40 tokens
FIRE_OVERRIDES = {"compaction_threshold_max_tokens": 40}


# TC-36: usage-anchored projection: anchor 100K + 80K chars delta -> 120K projected; fires at 120K threshold
def test_tc36_projection_math():
  assert projected_tokens(100000, 80000) == 120000
  # threshold for the default test registry generator: min(0.6 x 200000, 150000) = 120000 -> 120000 >= 120000 fires


def test_tc36b_compaction_fires_end_to_end(agent_factory):
  turns = [
    {"text": "long answer " * 20, "usage": {"input": 3000, "output": 100}},
    {"text": SUMMARY_TEXT},  # consumed by the summarizer side-call
  ]
  agent = agent_factory(turns, lana_overrides=FIRE_OVERRIDES, use_compactor=True)
  events = collect_events(agent, "please work")
  checkpoints = [event for event in events if event.type == "checkpoint_created"]
  assert len(checkpoints) == 1
  assert agent.messages[0].content == checkpoints[0].text  # history replaced, checkpoint first


# TC-37: checkpoint content: 3 anchors present, todo JSON byte-identical (IG-04)
# FR-07 per-turn semantics: threshold 4000 stays quiet after the small todo turn, fires after the large final turn
def test_tc37_checkpoint_anchors_and_todo(agent_factory):
  turns = [
    {"text": "planning", "tool_calls": [{"name": "todo_list", "args": {"todos": TODOS}}], "usage": {"input": 500, "output": 20}},
    {"text": "turn done", "usage": {"input": 5000, "output": 100}},
    {"text": SUMMARY_TEXT},  # summarizer
  ]
  agent = agent_factory(turns, lana_overrides={"compaction_threshold_max_tokens": 4000}, use_compactor=True)
  events = collect_events(agent, "go")
  checkpoint = [event for event in events if event.type == "checkpoint_created"][0]
  assert ANCHOR_TODO_TITLE in checkpoint.text and ANCHOR_TODO_FOOTER in checkpoint.text and ANCHOR_NO_ACK in checkpoint.text
  expected_json = json.dumps(TODOS, indent=2, ensure_ascii=False, sort_keys=True)
  assert expected_json in checkpoint.text  # byte-identical splice
  assert "Finish the demo." in checkpoint.text and "We worked." in checkpoint.text and "Edited files." in checkpoint.text


# TC-38: Summarizer failure (EC-17) -> no truncation, warning event
def test_tc38_summarizer_failure_fail_safe(agent_factory):
  turns = [
    {"text": "long answer", "usage": {"input": 3000, "output": 100}},
    {"error": "429 rate limit"},  # summarizer call fails
  ]
  agent = agent_factory(turns, lana_overrides=FIRE_OVERRIDES, use_compactor=True)
  message_count_probe = []
  events = collect_events(agent, "go")
  assert not [event for event in events if event.type == "checkpoint_created"]
  error_events = [event for event in events if event.type == "error"]
  assert any(event.message.startswith("NOTICE: Compacting context") for event in error_events)  # FR-16 UX-04: pre-notice BEFORE the paid call
  warning = [event for event in error_events if "Summarizer call failed" in event.message][0]
  assert "429" in warning.message
  assert any(message.content == "long answer" for message in agent.messages)  # nothing truncated
  assert agent.stop_reason is None  # session continues


# TC-39: no todo_list state (EC-12) -> todo section omitted
def test_tc39_no_todo_section_omitted(agent_factory):
  turns = [
    {"text": "long answer", "usage": {"input": 3000, "output": 100}},
    {"text": SUMMARY_TEXT},
  ]
  agent = agent_factory(turns, lana_overrides=FIRE_OVERRIDES, use_compactor=True)
  events = collect_events(agent, "go")
  checkpoint = [event for event in events if event.type == "checkpoint_created"][0]
  assert ANCHOR_TODO_TITLE not in checkpoint.text and ANCHOR_TODO_FOOTER not in checkpoint.text
  assert ANCHOR_NO_ACK in checkpoint.text


# Gap 02 regression (FR-07 "checked after each turn"): compaction fires MID-PROMPT, between tool-loop turns
def test_compaction_fires_mid_prompt(agent_factory, tmp_path):
  target_dir = str(tmp_path / "ws")
  turns = [
    {"text": "big turn with tool call " * 10, "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}], "usage": {"input": 3000, "output": 100}},
    {"text": SUMMARY_TEXT},  # summarizer side-call fired directly after turn 1
    {"text": "second turn continues after compaction", "usage": {"input": 500, "output": 20}},
  ]
  agent = agent_factory(turns, lana_overrides=FIRE_OVERRIDES, use_compactor=True)
  events = collect_events(agent, "go")
  types = [event.type for event in events]
  checkpoint_index = types.index("checkpoint_created")
  assert checkpoint_index < len(types) - 1 and "turn_started" in types[checkpoint_index:], "checkpoint must occur before the next turn, not post-prompt"
  assert agent.final_text == "second turn continues after compaction"
  assert agent.messages[0].content.startswith("The following is a summary")
  assert not any(message.role == "tool" and agent.messages.index(message) == 1 for message in agent.messages[:2])  # no orphan tool result after checkpoint


def test_extract_todo_json_deterministic():
  assert extract_todo_json(None) is None and extract_todo_json([]) is None
  first, second = extract_todo_json(TODOS), extract_todo_json(list(TODOS))
  assert first == second


def test_build_checkpoint_template_shape():
  text = build_checkpoint("obj", "sum", "code", '{"todo": 1}')
  assert text.startswith("The following is a summary of important context from your previous session.\n{{ CHECKPOINT 1 }}")
  assert text.index("# Objective:") < text.index(ANCHOR_TODO_TITLE) < text.index("# Session Summary:") < text.index("# Code Interaction Summary:")
  assert text.rstrip().endswith(ANCHOR_NO_ACK)


# TC-41: fits_window unit test (EC-30, FR-07)
def test_tc41_fits_window():
  assert fits_window([], 200000, 100)  # empty messages: projected = 0, fits
  msg = Message(role="assistant", content="ok", usage=Usage(input_tokens=100, output_tokens=0))
  assert not fits_window([msg], 200000, 500000)  # projected + batch > max_input
  assert fits_window([msg], 200000, 199900)  # projected + batch <= max_input


# TC-40: pre-call compaction retry (EC-30) - post-turn summarizer fails, pre-call check retries before next API call
def test_tc40_pre_call_compaction_retry(agent_factory, tmp_path):
  target_dir = str(tmp_path / "ws")
  turns = [
    {"text": "big answer", "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}], "usage": {"input": 150000, "output": 100}},
    {"error": "429 rate limit"},  # summarizer fails on post-turn attempt
    {"text": SUMMARY_TEXT},  # summarizer succeeds on pre-call retry
    {"text": "after compaction", "usage": {"input": 500, "output": 20}},
  ]
  agent = agent_factory(turns, use_compactor=True)  # default threshold = 120K
  events = collect_events(agent, "go")
  types = [event.type for event in events]
  assert "checkpoint_created" in types
  checkpoint_index = types.index("checkpoint_created")
  turn_started_indices = [i for i, t in enumerate(types) if t == "turn_started"]
  assert checkpoint_index < turn_started_indices[-1], "checkpoint must appear before the final turn_started"


# TC-42: tail integrity - orphaned tool results stripped (EC-31, FR-07)
# When KEEP_TAIL_MESSAGES=6 cuts an assistant+tool group, the orphaned tool results must be stripped
def test_tc42_tail_integrity_strips_orphaned_tool_results(agent_factory, tmp_path, monkeypatch):
  import lana.compaction as compaction_mod
  monkeypatch.setattr(compaction_mod, "KEEP_TAIL_MESSAGES", 4)
  target_dir = str(tmp_path / "ws")
  turns = [
    {"text": "turn1 with tools", "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}, {"name": "list_dir", "args": {"DirectoryPath": target_dir}}], "usage": {"input": 3000, "output": 100}},
    {"text": "turn2 with tools", "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}], "usage": {"input": 3000, "output": 100}},
    {"text": "turn3 text", "usage": {"input": 3000, "output": 100}},
    {"text": SUMMARY_TEXT},
  ]
  agent = agent_factory(turns, lana_overrides=FIRE_OVERRIDES, use_compactor=True)
  events = collect_events(agent, "go")
  assert any(e.type == "checkpoint_created" for e in events)
  for msg in agent.messages:
    if msg.role == "tool":
      parent = any(call.id == msg.tool_call_id for m in agent.messages if m.role == "assistant" for call in m.tool_calls)
      assert parent, f"orphaned tool result {msg.tool_call_id} has no parent assistant in tail"
  assert agent.final_text == "turn3 text"


# TC-43: split_sections fallback - unstructured summarizer output goes into objective (EC-32, FR-07)
def test_tc43_split_sections_fallback_to_objective():
  from lana.compaction import split_sections
  unstructured = "The user was working on a bug fix. They edited three files and ran tests."
  objective, summary, code_history = split_sections(unstructured)
  assert objective == unstructured  # text goes into objective, not session summary
  assert summary == "" and code_history == ""  # other sections empty


# TC-43b: split_sections with headers works normally
def test_tc43b_split_sections_with_headers():
  from lana.compaction import split_sections
  text = "# Objective:\nFix the bug.\n# Session Summary:\nWe worked.\n# Code Interaction Summary:\nEdited files."
  objective, summary, code_history = split_sections(text)
  assert "Fix the bug." in objective and "We worked." in summary and "Edited files." in code_history


# TC-45: render_transcript preserves first user message for long sessions (EC-34, FR-07)
def test_tc45_render_transcript_preserves_first_user_message():
  from lana.compaction import render_transcript
  objective = "Build a web app with React and TailwindCSS"
  messages = [Message(role="user", content=objective)]
  # Add enough messages to exceed 100K chars
  for i in range(500):
    messages.append(Message(role="assistant", content="x" * 300))
    messages.append(Message(role="user", content="y" * 300))
  transcript = render_transcript(messages, limit_chars=10000)
  assert objective in transcript  # first user message preserved
  assert transcript.startswith("[USER] " + objective)  # objective at the start
  assert len(transcript) <= 10000 + len(objective) + 20  # within budget


# TC-45b: render_transcript short session returns full text unchanged
def test_tc45b_render_transcript_short_session():
  from lana.compaction import render_transcript
  messages = [Message(role="user", content="hello"), Message(role="assistant", content="hi there")]
  transcript = render_transcript(messages)
  assert "hello" in transcript and "hi there" in transcript


# TC-47: render_transcript with empty messages (no crash)
def test_tc47_render_transcript_empty_messages():
  from lana.compaction import render_transcript
  transcript = render_transcript([])
  assert transcript == ""


# TC-48: render_transcript with single message (no crash)
def test_tc48_render_transcript_single_message():
  from lana.compaction import render_transcript
  transcript = render_transcript([Message(role="user", content="only message")])
  assert "only message" in transcript


# TC-49: compaction with all-tool tail (tail integrity strips all tools, no crash)
def test_tc49_compaction_all_tool_result_tail(agent_factory, tmp_path, monkeypatch):
  import lana.compaction as compaction_mod
  monkeypatch.setattr(compaction_mod, "KEEP_TAIL_MESSAGES", 4)
  target_dir = str(tmp_path / "ws")
  turns = [
    {"text": "turn1", "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}], "usage": {"input": 3000, "output": 100}},
    {"text": "turn2", "tool_calls": [{"name": "list_dir", "args": {"DirectoryPath": target_dir}}], "usage": {"input": 3000, "output": 100}},
    {"text": "turn3", "usage": {"input": 3000, "output": 100}},
    {"text": SUMMARY_TEXT},
  ]
  agent = agent_factory(turns, lana_overrides=FIRE_OVERRIDES, use_compactor=True)
  events = collect_events(agent, "go")
  assert any(e.type == "checkpoint_created" for e in events)
  # No orphaned tool results in the tail
  for msg in agent.messages:
    if msg.role == "tool":
      parent = any(call.id == msg.tool_call_id for m in agent.messages if m.role == "assistant" for call in m.tool_calls)
      assert parent, f"orphaned tool result {msg.tool_call_id}"
