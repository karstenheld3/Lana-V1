"""Shared builder for black-box scenario workspaces (TP01 section 5 Test Data)."""
from pathlib import Path
from tests.conftest import write_config_dir, write_prompt_system
from tests.harness import LanaProc
from tests.scripted_adapter import write_script

SCENARIO_WORKFLOWS = {
  "hello": "---\ndescription: Say hello\n---\nGreet the user.",
  "tooluse": "---\ndescription: Tool use demo\n---\nRead input.md and create output.md.",
  "prime-like": "---\ndescription: Prime-like flow\n---\nRead the notes file, update the todo list, summarize.",
}


# Build a complete scenario workspace: fake prompt system + isolated config + optional script; returns a ready LanaProc
def build_scenario_proc(tmp_path: Path, name: str, turns: list[dict] | None, lana_overrides: dict | None = None, policy: str | None = None) -> LanaProc:
  workspace = tmp_path / name
  workspace.mkdir(parents=True, exist_ok=True)
  system = write_prompt_system(workspace / "fake_system",
    rules={"normal.md": "---\ntrigger: always_on\n---\nBe helpful.", "empty.md": "---\ntrigger: always_on\n---\n", "oversized.md": "R" * 9000},
    workflows=SCENARIO_WORKFLOWS,
    skills={"demo-skill": ("---\nname: demo-skill\ndescription: Demo\n---\nBody.", {"GUIDE.md": "guide"})})
  overrides = {"agent_folder": str(system).replace("\\", "/")}
  if lana_overrides: overrides.update(lana_overrides)
  config_dir = write_config_dir(workspace, lana_overrides=overrides, key_lines=None)
  script = write_script(workspace / "script.jsonl", turns) if turns is not None else None
  return LanaProc(workspace, config_path=config_dir / "lana-config.json", script_path=script, policy=policy)
