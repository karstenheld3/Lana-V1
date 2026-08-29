"""Scripted adapter test helpers (IS-22). The adapter itself lives in lana.providers.scripted_adapter
so the installed `lana` executable can load it via LANA_SCRIPTED_ADAPTER (subprocesses cannot import tests/)."""
import json
from pathlib import Path
from lana.providers.scripted_adapter import ScriptedAdapter  # noqa: F401 - re-export per IP01 file structure


# Write a turn script: each item is a dict per the IS-22 JSONL format
def write_script(path: Path, turns: list[dict]) -> Path:
  path = Path(path)
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text("\n".join(json.dumps(turn, ensure_ascii=False) for turn in turns) + "\n", encoding="utf-8")
  return path


# Common script: one turn with tool calls, then a closing text turn
def tool_calls_then_text(calls: list[dict], first_text: str = "Working on it.", final_text: str = "Done.") -> list[dict]:
  return [{"text": first_text, "tool_calls": calls, "usage": {"input": 1000, "output": 50}}, {"text": final_text, "usage": {"input": 1200, "output": 20}}]
