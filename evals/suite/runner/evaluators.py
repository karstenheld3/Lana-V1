"""Tier 1 StructureEvaluator (manifest.yaml) and Tier 2 ProcessEvaluator (checks.yaml) - LANATEST-SP01 FR-06/07."""
import json, re
from pathlib import Path

CRITICAL_CAP = 0.5  # a failed CRITICAL check caps Tier 2 at 0.5 (FR-07)


def check_result(check_id: str, passed: bool, detail: str) -> dict:
  return {"id": check_id, "passed": passed, "detail": detail}


# ---------------------------------------------------------------------------- Tier 1: structure (FR-06)
def evaluate_structure(workspace: Path, manifest: dict) -> dict:
  results = []
  for pattern in manifest.get("required_files", []):
    matches = list(workspace.glob(pattern))
    results.append(check_result(f"required:{pattern}", bool(matches), f"{len(matches)} {'match' if len(matches) == 1 else 'matches'}" if matches else f"no file matches '{pattern}'"))
  for pattern in manifest.get("forbidden_files", []):
    matches = [path for path in workspace.glob(pattern) if ".lana-data" not in path.parts]
    results.append(check_result(f"forbidden:{pattern}", not matches, "clean" if not matches else f"forbidden {'file' if len(matches) == 1 else 'files'}: {', '.join(str(p.relative_to(workspace)) for p in matches)}"))
  for rule in manifest.get("file_rules", []):
    glob_pattern = rule["glob"]
    files = [path for path in workspace.glob(glob_pattern) if ".lana-data" not in path.parts]
    if not files:
      results.append(check_result(f"file_rules:{glob_pattern}", False, f"no file matches '{glob_pattern}'"))
      continue
    text = "\n\n".join(path.read_text(encoding="utf-8", errors="replace") for path in files)
    for section in rule.get("required_sections", []):
      # Match both '## Title' and '## N. Title' (agents may number headings)
      if section.startswith("## "):
        escaped = re.escape(section[3:])
        found = bool(re.search(rf"^##\s+(?:\d+\.\s+)?{escaped}", text, re.MULTILINE))
      else:
        found = section in text
      results.append(check_result(f"{glob_pattern}:section:{section}", found, "present" if found else f"section '{section}' missing"))
    for spec in rule.get("patterns", []):
      found = re.search(spec["regex"], text, re.MULTILINE) is not None
      results.append(check_result(f"{glob_pattern}:pattern:{spec['name']}", found, "matched" if found else f"regex '{spec['regex']}' not found"))
    for needle in rule.get("forbid_content", []):
      absent = needle not in text
      results.append(check_result(f"{glob_pattern}:forbid:{needle}", absent, "absent" if absent else f"forbidden content '{needle}' present"))
  score = (sum(1 for r in results if r["passed"]) / len(results)) if results else 1.0
  return {"score": round(score, 3), "checks": results}


# ---------------------------------------------------------------------------- Tier 2: process (FR-07)
def load_session_events(workspace: Path) -> list[dict]:
  sessions_dir = workspace / ".lana-data" / "sessions"
  events = []
  for session_file in sorted(sessions_dir.glob("*.jsonl")) if sessions_dir.is_dir() else []:
    for line in session_file.read_text(encoding="utf-8").splitlines():
      try:
        events.append(json.loads(line))
      except json.JSONDecodeError:
        continue
  return events


EDIT_TOOLS = {"edit", "multi_edit"}  # both are edit operations on existing files; write_to_file creates new files - no prior read required
PATH_KEYS = ("file_path", "TargetFile", "AbsolutePath")


def tool_events(events: list[dict]) -> list[dict]:
  return [event for event in events if event.get("type") == "tool_call_requested"]


def event_path(event: dict) -> str:
  for key in PATH_KEYS:
    value = event.get("args", {}).get(key)
    if value: return str(value).replace("\\", "/").lower()
  return ""


def assert_tool_called(events, spec) -> tuple[bool, str]:
  target = spec["tool"]
  match_tools = EDIT_TOOLS if target in EDIT_TOOLS else {target}
  calls = [event for event in tool_events(events) if event.get("tool") in match_tools]
  if spec.get("args_regex"):
    calls = [event for event in calls if re.search(spec["args_regex"], json.dumps(event.get("args", {}), ensure_ascii=False))]
  minimum = spec.get("min", 1)
  return len(calls) >= minimum, f"{len(calls)} {'call' if len(calls) == 1 else 'calls'} of '{target}' (need >= {minimum})"


def assert_forbidden_tool(events, spec) -> tuple[bool, str]:
  calls = [event for event in tool_events(events) if event.get("tool") == spec["tool"]]
  return not calls, ("never called" if not calls else f"'{spec['tool']}' called {len(calls)} {'time' if len(calls) == 1 else 'times'}")


def assert_read_before_edit(events, spec) -> tuple[bool, str]:
  read_paths = set()
  for event in tool_events(events):
    if event.get("tool") in ("read_file", "write_to_file"):  # a write establishes known content like a read
      path = event_path(event)
      if path: read_paths.add(path)
    elif event.get("tool") in EDIT_TOOLS:
      path = event_path(event)
      if path and path not in read_paths:
        return False, f"edit on '{path}' without prior read"
      if path: read_paths.add(path)
  return True, "every edit preceded by a read or create"


ASSERTS = {"tool_called": assert_tool_called, "forbidden_tool": assert_forbidden_tool, "read_before_edit": assert_read_before_edit}


def evaluate_process(workspace: Path, checks: dict) -> dict:
  events = load_session_events(workspace)
  results, critical_failed = [], False
  for check in checks.get("checks", []):
    assert_spec = check["assert"]
    assert_fn = ASSERTS.get(assert_spec["type"])
    if assert_fn is None:
      results.append(check_result(check["id"], False, f"unknown assert type '{assert_spec['type']}'"))
      continue
    passed, detail = assert_fn(events, assert_spec)
    results.append(check_result(check["id"], passed, detail))
    if not passed and check.get("severity", "MEDIUM") == "CRITICAL": critical_failed = True
  score = (sum(1 for r in results if r["passed"]) / len(results)) if results else 1.0
  if critical_failed: score = min(score, CRITICAL_CAP)
  return {"score": round(score, 3), "checks": results, "event_count": len(events)}
