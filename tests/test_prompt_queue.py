"""Prompt queue tests (LANAACPB-IP01 Category 9 TC-45..49, TP01-TC-12/13; SPEC FR-12)."""
import pytest
from lana.prompt_queue import PromptQueueError, parse_queue
from tests.conftest import write_config_dir, write_prompt_system
from tests.harness import LanaProc
from tests.scripted_adapter import write_script


# ------------------------------------------- unit: parse_queue (TC-45..47) -------------------------------------------

# TC-45: 2 prompts, '---' separator, commentary after the separator -> 2 prompts, commentary and separator dropped
def test_tc45_two_prompts_commentary_dropped():
  queue_text = "```\nList files.\n```\n\n---\n\n## Step 2 commentary line\n\n````\nCount them.\n````\n"
  assert parse_queue(queue_text) == ["List files.", "Count them."]


# TC-46: mixed fence lengths (EC-27) and nested-fence content (EC-24) -> inner fences intact as content
def test_tc46_mixed_fences_and_nesting():
  prompt_one = "`````\nUse this docstring format:\n\n````markdown\nExample:\n```python\nadd(1, 2)  # 3\n```\n````\n`````"
  prompt_two = "``````\nSecond prompt containing a 5-backtick line:\n`````\ninside material\n`````\n``````"
  prompts = parse_queue(f"{prompt_one}\n\n---\n\n{prompt_two}\n")
  assert len(prompts) == 2
  assert "````markdown" in prompts[0] and "```python" in prompts[0]
  assert "`````" in prompts[1] and "inside material" in prompts[1]


# TC-46b: minimum 3-backtick fence works and a 3-fence prompt closes at the first >= 3 backtick line
def test_tc46b_three_backtick_minimum():
  assert parse_queue("```text\nplain prompt\n```\n") == ["plain prompt"]


# TC-47: malformed battery -> PromptQueueError naming the violated rule (EC-25)
@pytest.mark.parametrize("queue_text, expected_fragment", [
  ("commentary before any fence\n```\nx\n```\n", "must start with an opening fence"),
  ("```\nnever closed\n", "unclosed fence"),
  ("```\na\n```\n````\nb\n````\n", "expected a '---' separator"),
  ("``````````\nten backticks\n``````````\n", "maximum is 9"),
  ("", "zero prompts"),
  ("   \n\n", "zero prompts"),
  ("```\na\n```\n---\n", "trailing '---' separator"),
])
def test_tc47_malformed_battery(queue_text, expected_fragment):
  with pytest.raises(PromptQueueError) as error:
    parse_queue(queue_text)
  assert expected_fragment in str(error.value)


# ------------------------------------------- harness: queue execution (TC-48..49, TP01-TC-12/13) ---------------------

@pytest.fixture
def queue_workspace(tmp_path):
  workspace = tmp_path / "queue_ws"
  workspace.mkdir()
  system = write_prompt_system(workspace / "ps", rules={"main.md": "Rule body"})
  config_dir = write_config_dir(workspace, lana_overrides={"agent_folder": str(system).replace("\\", "/")}, key_lines=None)
  return workspace, config_dir / "lana-config.json"


def run_queue(workspace, config_path, script_turns, queue_text, extra_args=None):
  queue_file = workspace / "PROMPTS.md"
  queue_file.write_text(queue_text, encoding="utf-8")
  script = write_script(workspace / "script.jsonl", script_turns) if script_turns is not None else None
  proc = LanaProc(workspace, config_path=config_path, script_path=script)
  result = proc.run_piped("", extra_args=["--prompt-file", str(queue_file), "--output-format", "jsonl"] + (extra_args or []))
  return proc, result


# TC-48: 2-prompt queue -> ONE session JSONL, prompt_step 1/2 and 2/2 each followed by its turn events, exit 0
def test_tc48_queue_one_session_with_step_events(queue_workspace):
  workspace, config_path = queue_workspace
  turns = [{"text": "reply one", "usage": {"input": 10, "output": 5}}, {"text": "reply two", "usage": {"input": 12, "output": 6}}]
  proc, result = run_queue(workspace, config_path, turns, "```\nfirst step\n```\n\n---\n\n```\nsecond step\n```\n")
  assert result.returncode == 0, result.stderr
  assert len(proc.session_files()) == 1  # ONE session for the whole queue (FR-12)
  session_events = proc.read_session_events()
  steps = [event for event in session_events if event.type == "prompt_step"]
  assert [(step.index, step.total) for step in steps] == [(1, 2), (2, 2)]
  assert all(len(step.digest) == 12 for step in steps)
  types = [event.type for event in session_events]
  first_step, second_step = types.index("prompt_step"), len(types) - 1 - types[::-1].index("prompt_step")
  user_positions = [position for position, event_type in enumerate(types) if event_type == "user_message"]
  assert first_step < user_positions[0] < second_step < user_positions[1]  # each step precedes its turn
  stdout_steps = [event for event in proc.events(result) if event.type == "prompt_step"]
  assert len(stdout_steps) == 2  # prompt_step lines on stdout jsonl (FR-12)


# TC-49 + TP01-TC-13: provider error on entry 2 of 3 -> abort, exit 3, exactly 2 prompt_step persisted; session resumable
def test_tc49_queue_abort_and_resume(queue_workspace):
  workspace, config_path = queue_workspace
  turns = [{"text": "ok one", "usage": {"input": 10, "output": 5}}, {"error": "simulated outage"}]
  queue_text = "```\none\n```\n\n---\n\n```\ntwo\n```\n\n---\n\n```\nthree\n```\n"
  proc, result = run_queue(workspace, config_path, turns, queue_text)
  assert result.returncode == 3, result.stderr  # provider failure exit code
  assert "Queue aborted at step 2 of 3" in result.stderr
  session_events = proc.read_session_events()
  steps = [event for event in session_events if event.type == "prompt_step"]
  assert [step.index for step in steps] == [1, 2]  # no third prompt_step (EC-26)
  user_messages = [event.content for event in session_events if event.type == "user_message"]
  assert user_messages == ["one", "two"]
  # TP01-TC-13: the aborted session resumes via --resume with a fresh script
  session_file = proc.session_files()[-1]
  resume_proc = LanaProc(workspace, config_path=config_path, script_path=write_script(workspace / "resume_script.jsonl", [{"text": "resumed fine", "usage": {"input": 10, "output": 5}}]))
  resume_result = resume_proc.run_headless("continue", extra_args=["--resume", str(session_file)])
  assert resume_result.returncode == 0, resume_result.stderr
  assert "resumed fine" in resume_result.stdout


# TC-49b: flag exclusivity (EC-28) - --prompt-file with -p, --resume, or --acp -> exit 2
def test_tc49b_prompt_file_exclusivity(queue_workspace):
  workspace, config_path = queue_workspace
  queue_file = workspace / "PROMPTS.md"
  queue_file.write_text("```\nx\n```\n", encoding="utf-8")
  proc = LanaProc(workspace, config_path=config_path, script_path=None)
  with_prompt = proc.run_headless("hello", extra_args=["--prompt-file", str(queue_file)])
  assert with_prompt.returncode == 2 and "mutually exclusive" in with_prompt.stderr
  with_resume = proc.run_piped("", extra_args=["--prompt-file", str(queue_file), "--resume", "x.jsonl"])
  assert with_resume.returncode == 2 and "mutually exclusive" in with_resume.stderr
  with_acp = proc.run_piped("", extra_args=["--acp", "--prompt-file", str(queue_file)])
  assert with_acp.returncode == 2 and "mutually exclusive" in with_acp.stderr


# TC-49c: malformed file -> exit 2 BEFORE any session is created (EC-25)
def test_tc49c_malformed_file_no_session(queue_workspace):
  workspace, config_path = queue_workspace
  proc, result = run_queue(workspace, config_path, None, "no fence at the start\n```\nx\n```\n")
  assert result.returncode == 2
  assert "must start with an opening fence" in result.stderr and "PROMPT_FILE_FORMAT.md" in result.stderr
  assert proc.session_files() == []  # no session created
  missing = LanaProc(workspace, config_path=config_path, script_path=None)
  missing_result = missing.run_piped("", extra_args=["--prompt-file", str(workspace / "does-not-exist.md")])
  assert missing_result.returncode == 2 and "cannot read prompt file" in missing_result.stderr


# TP01-TC-12: queue builds on prior step - nested fences verbatim in the session, commentary appears nowhere
def test_tp01_tc12_nested_fences_verbatim_commentary_excluded(queue_workspace):
  workspace, config_path = queue_workspace
  prompt_two = "Add docs. Use this format:\n\n````markdown\nExample:\n```python\nmultiply(2, 3)  # 6\n```\n````"
  queue_text = f"```\nCreate calc.py\n```\n\n---\n\n## COMMENTARY-MARKER step two label\n\n`````\n{prompt_two}\n`````\n"
  turns = [{"text": "created", "usage": {"input": 10, "output": 5}}, {"text": "documented", "usage": {"input": 12, "output": 6}}]
  proc, result = run_queue(workspace, config_path, turns, queue_text)
  assert result.returncode == 0, result.stderr
  session_events = proc.read_session_events()
  user_messages = [event.content for event in session_events if event.type == "user_message"]
  assert user_messages[1] == prompt_two  # verbatim incl. inner 4/3-backtick fences (DD-10)
  session_text = (proc.session_files()[-1]).read_text(encoding="utf-8")
  assert "COMMENTARY-MARKER" not in session_text  # commentary never reaches the session (FR-12)
