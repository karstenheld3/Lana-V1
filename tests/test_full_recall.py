"""TC-64..67 + TP01-TC-11: full-recall session log (SP01 FR-08/IG-07/DD-22, IP01 IS-24)."""
import json
from tests.conftest import collect_events, write_config_dir
from tests.scenario_utils import build_scenario_proc
from lana.providers.anthropic_adapter import build_messages
from lana.models import Message, ThinkingBlock
from lana.session import resume


# TC-64: session_started is the FIRST line and carries the full environment (FR-08, IG-07)
def test_tc64_session_started_first_line_with_environment(tmp_path):
  proc = build_scenario_proc(tmp_path, "tc64", [{"text": "hi", "usage": {"input": 100, "output": 5}}])
  result = proc.run_headless("hello")
  assert result.returncode == 0, result.stdout + result.stderr
  events = proc.read_session_events()
  assert events[0].type == "session_started"
  started = events[0]
  assert "Be helpful." in started.system_prompt  # assembled prompt recorded byte-verbatim (rule body present)
  tool_names = [definition["name"] for definition in started.tool_definitions]
  assert len(tool_names) == 16 and "read_file" in tool_names and "trajectory_search" in tool_names
  assert started.config_snapshot["roles"]["generator"]["model_id"] == "claude-sonnet-4-5-20250929"
  assert started.config_snapshot["execution_policy"] == "manual"
  counts = started.prompt_system_fingerprint["counts"]
  assert counts == {"rules": 3, "workflows": 3, "skills": 1}
  assert started.prompt_system_fingerprint["content_hash"].startswith("sha256:")


# TC-65 + TP01-TC-11: recorded environment wins on resume despite disk mutation + model change (IG-01/IG-06/IG-07, DD-22)
def test_tc65_tp01_tc11_resume_authority_and_warnings(tmp_path):
  from tests.scripted_adapter import write_script
  proc = build_scenario_proc(tmp_path, "tc65", [{"text": "first", "usage": {"input": 100, "output": 5}}])
  capture_1 = proc.workspace / "capture1.jsonl"
  proc.extra_env = {"LANA_SCRIPTED_CAPTURE": str(capture_1)}
  result = proc.run_headless("hello")
  assert result.returncode == 0, result.stdout + result.stderr
  session_file = proc.session_files()[0]
  request_1 = json.loads(capture_1.read_text(encoding="utf-8").splitlines()[0])

  # Mutate the environment: delete a rule file AND switch the generator model
  (proc.workspace / "fake_system" / "rules" / "normal.md").unlink()
  system_path = str(proc.workspace / "fake_system").replace("\\", "/")
  write_config_dir(proc.workspace, lana_overrides={"prompt_system_paths": [system_path],
                                                   "roles": {"generator": {"model_id": "gpt-4.1-mini", "effort": "low"},
                                                             "summarizer": {"model_id": "gpt-4.1-mini", "effort": "low"},
                                                             "websearch": {"model_id": "gpt-4.1-mini", "effort": "low"}}}, key_lines=None)
  capture_2 = proc.workspace / "capture2.jsonl"
  proc.extra_env = {"LANA_SCRIPTED_CAPTURE": str(capture_2)}
  proc.script_path = write_script(proc.workspace / "script2.jsonl", [{"text": "second", "usage": {"input": 100, "output": 5}}])
  resumed = proc.run_piped("continue please\n/exit\n", extra_args=["--resume", str(session_file)])
  assert resumed.returncode == 0, resumed.stdout + resumed.stderr
  assert "WARNING: prompt system changed since recording" in resumed.stdout
  assert "WARNING: generator changed (recorded claude-sonnet-4-5-20250929, current gpt-4.1-mini)" in resumed.stdout
  request_2 = json.loads(capture_2.read_text(encoding="utf-8").splitlines()[0])
  assert request_2["system"] == request_1["system"]  # recorded prompt byte-identical despite disk mutation (IG-01 across resume)
  assert request_2["tools"] == request_1["tools"]    # recorded tool definitions are the resume authority


# TC-66: thinking payloads persisted on turn_finished, reprojected on resume, dropped cross-provider (EC-29)
def test_tc66_thinking_payload_round_trip(agent_factory):
  agent = agent_factory([{"text": "done", "thinking": "pondering the request", "usage": {"input": 100, "output": 5}}])
  collect_events(agent, "think about it")
  lines = agent.session.path.read_text(encoding="utf-8").splitlines()
  finished = [json.loads(line) for line in lines if '"turn_finished"' in line]
  assert finished and finished[0]["thinking_payloads"] == [{"provider": "scripted", "payload": {"thinking": "pondering the request"}}]
  agent.session.close()
  state = resume(agent.session.path)
  assistant = [message for message in state.messages if message.role == "assistant"][0]
  assert assistant.thinking and assistant.thinking[0].provider == "scripted"
  assert assistant.thinking[0].payload == {"thinking": "pondering the request"}
  # EC-29: adapters resend only provider-matching payloads - a 'scripted' payload never reaches an Anthropic request
  rebuilt = build_messages([Message(role="assistant", content="done", thinking=[ThinkingBlock(provider="scripted", payload={"thinking": "x"})])])
  assert all(block["type"] != "thinking" for block in rebuilt[0]["content"])


# TC-67: legacy session file without session_started -> disk assembly fallback + warning (EC-28)
def test_tc67_legacy_session_fallback(tmp_path):
  proc = build_scenario_proc(tmp_path, "tc67", [{"text": "resumed", "usage": {"input": 100, "output": 5}}])
  sessions_dir = proc.workspace / ".lana" / "sessions"
  sessions_dir.mkdir(parents=True)
  legacy = sessions_dir / "2026-01-01_000000_legacy.jsonl"
  legacy.write_text('{"ts":"2026-01-01 00:00:00","type":"user_message","content":"old question"}\n'
                    '{"ts":"2026-01-01 00:00:01","type":"turn_started","role":"generator"}\n'
                    '{"ts":"2026-01-01 00:00:02","type":"text_delta","text":"old answer"}\n'
                    '{"ts":"2026-01-01 00:00:03","type":"turn_finished","role":"generator","input_tokens":50,"output_tokens":5}\n', encoding="utf-8")
  state = resume(legacy)
  assert state.system_prompt is None and state.tool_definitions is None  # legacy: no recorded environment
  assert len(state.messages) == 2  # projection unchanged
  result = proc.run_piped("/exit\n", extra_args=["--resume", str(legacy)])
  assert result.returncode == 0, result.stdout + result.stderr
  assert "WARNING: legacy session file" in result.stdout
