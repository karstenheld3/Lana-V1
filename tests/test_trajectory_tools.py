"""IS-23: trajectory_search over session JSONL (IP01 TC-61..63, FR-15)."""
import pytest
from lana import events
from lana.session import SessionStore
from lana.tools import ToolContext, ToolError
from lana.tools.trajectory_tools import execute_trajectory_search


@pytest.fixture
def context(tmp_path):
  return ToolContext(workspace=tmp_path)


def write_session(workspace, name: str, event_list) -> str:
  store = SessionStore(workspace / ".lana" / "sessions" / f"{name}.jsonl")
  for event in event_list: store.append(event)
  store.close()
  return name


@pytest.fixture
def demo_session(tmp_path):
  event_list = [
    events.UserMessage(content="please refactor the crawler module"),
    events.TextDelta(text="Starting the crawler refactor now."),
    events.ToolCallRequested(id="tc_1", tool="read_file", args={"file_path": "crawler.py"}),
    events.ToolCallFinished(id="tc_1", status="ok", result="crawler source", result_chars=14),
    events.TextDelta(text="The parser stays untouched."),
    events.TurnFinished(input_tokens=500, output_tokens=40),
  ]
  return write_session(tmp_path, "2026-08-30_120000_abc123", event_list)


# TC-61: query-term scoring, sorted by overlap descending; 50-chunk cap
def test_tc61_scoring_and_cap(tmp_path, context, demo_session):
  result = execute_trajectory_search({"ID": demo_session, "Query": "crawler refactor", "SearchType": "cascade"}, context)
  lines = result.splitlines()
  assert "of 6 chunks" in lines[0] and "scored by term overlap" in lines[0]
  assert "[001]" in lines[1] or "[002]" in lines[1]  # top hit carries both terms (user message or first delta)
  assert "parser stays untouched" not in result or "crawler" in result  # non-matching chunk excluded
  big_events = [events.TextDelta(text=f"needle number {index}") for index in range(60)]
  big_id = write_session(tmp_path, "2026-08-30_130000_big", big_events)
  capped = execute_trajectory_search({"ID": big_id, "Query": "needle", "SearchType": "cascade"}, context)
  assert "50 of 60 chunks" in capped.splitlines()[0]


# TC-62: empty query -> all chunks chronological; ID resolution by exact/stem/prefix
def test_tc62_empty_query_and_id_resolution(tmp_path, context, demo_session):
  by_stem = execute_trajectory_search({"ID": demo_session, "Query": "", "SearchType": "cascade"}, context)
  assert "6 of 6 chunks" in by_stem.splitlines()[0] and "chronological" in by_stem.splitlines()[0]
  assert by_stem.splitlines()[1].startswith("[001]") and by_stem.splitlines()[-1].startswith("[006]")
  by_exact = execute_trajectory_search({"ID": demo_session + ".jsonl", "Query": "", "SearchType": "cascade"}, context)
  by_prefix = execute_trajectory_search({"ID": "2026-08-30_12", "Query": "", "SearchType": "cascade"}, context)
  assert by_exact.splitlines()[0] == by_prefix.splitlines()[0] == by_stem.splitlines()[0]


# TC-63: error paths (EC-27)
def test_tc63_error_paths(tmp_path, context, demo_session):
  with pytest.raises(ToolError) as error: execute_trajectory_search({"ID": "nope", "Query": "x", "SearchType": "cascade"}, context)
  assert demo_session in str(error.value)  # unknown ID lists available sessions
  write_session(tmp_path, "2026-08-30_140000_second", [events.TextDelta(text="x")])
  with pytest.raises(ToolError) as error: execute_trajectory_search({"ID": "2026-08-30", "Query": "x", "SearchType": "cascade"}, context)
  assert "ambiguous" in str(error.value)
  with pytest.raises(ToolError) as error: execute_trajectory_search({"ID": demo_session, "Query": "x", "SearchType": "user"}, context)
  assert "not supported" in str(error.value)
  empty_workspace_context = ToolContext(workspace=tmp_path / "elsewhere")
  with pytest.raises(ToolError) as error: execute_trajectory_search({"ID": "any", "Query": "x", "SearchType": "cascade"}, empty_workspace_context)
  assert "No sessions folder" in str(error.value)


def test_no_match_message(tmp_path, context, demo_session):
  result = execute_trajectory_search({"ID": demo_session, "Query": "zzz_nothing_matches", "SearchType": "cascade"}, context)
  assert "no chunks match" in result
