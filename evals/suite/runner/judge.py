"""Tier 3 QualityEvaluator: rubric-anchored judge via @skills:llm-evaluation call-llm.py (LANATEST-SP01 FR-08, IP01 P3)."""
import json, re, subprocess
from pathlib import Path


# Fence with one backtick more than the longest backtick run inside (min 3) - content can safely contain fences
def fenced(text: str) -> str:
  longest = max((len(run) for run in re.findall("`+", text)), default=0)
  ticks = "`" * max(3, longest + 1)
  return f"{ticks}\n{text.rstrip()}\n{ticks}"


def file_block(name: str, text: str) -> str:
  return f"{name}\n{fenced(text)}"


def render_tree(relative_paths: list[str]) -> str:
  tree: dict = {}
  for relative in sorted(relative_paths):
    node = tree
    for part in relative.split("/"): node = node.setdefault(part, {})
  lines = []
  def walk(node: dict, prefix: str) -> None:
    entries = sorted(node)
    for position, name in enumerate(entries):
      last = position == len(entries) - 1
      lines.append(f"{prefix}{'└─ ' if last else '├─ '}{name}")
      walk(node[name], prefix + ("   " if last else "│  "))
  walk(tree, "")
  return "\n".join(lines)


def collect_files(root: Path, patterns: list[str] | None = None) -> list[Path]:
  paths = [p for pattern in patterns for p in root.glob(pattern)] if patterns is not None else list(root.rglob("*"))
  return sorted(p for p in set(paths) if p.is_file() and ".lana-data" not in p.parts and ".lana" not in p.parts)


def build_judge_input(workspace: Path, manifest: dict, judge_dir: Path, golden_dir: Path | None, prompts_path: Path | None) -> Path:
  sections = []
  if prompts_path and prompts_path.exists():
    sections.append("# PROMPTS\n\nThe task the agent received (prompt-queue format: fenced prompts separated by ---).\n\n"
                    + file_block("PROMPTS.md", prompts_path.read_text(encoding="utf-8", errors="replace")))
  golden_files = collect_files(golden_dir) if golden_dir and golden_dir.exists() else []
  if golden_files:  # reference-guided judging: golden calibrates, never dictates (see template Reference Handling)
    blocks = [file_block(str(p.relative_to(golden_dir)).replace("\\", "/"), p.read_text(encoding="utf-8", errors="replace")) for p in golden_files]
    tree = render_tree([str(p.relative_to(golden_dir)).replace("\\", "/") for p in golden_files])
    sections.append("# REFERENCE OUTPUT\n\nOne known-good solution produced by a reference agent. Folder structure:\n\n"
                    + fenced(tree) + "\n\n" + "\n\n---\n\n".join(blocks))
  agent_files = collect_files(workspace, manifest.get("required_files", []))
  all_workspace_files = collect_files(workspace)
  tree = render_tree([str(p.relative_to(workspace)).replace("\\", "/") for p in all_workspace_files]) or "(empty workspace)"
  blocks = [file_block(str(p.relative_to(workspace)).replace("\\", "/"), p.read_text(encoding="utf-8", errors="replace")) for p in agent_files]
  sections.append("# AGENT OUTPUT\n\nThe output to judge. Full workspace folder structure:\n\n" + fenced(tree) + "\n\n"
                  + ("\n\n---\n\n".join(blocks) or "(no output files found)"))
  input_path = judge_dir / "input.md"
  input_path.write_text("\n\n".join(sections), encoding="utf-8")
  return input_path


def build_judge_prompt(template_path: Path, rubric_path: Path, judge_dir: Path) -> Path:
  prompt = template_path.read_text(encoding="utf-8").replace("{RUBRIC}", rubric_path.read_text(encoding="utf-8"))
  prompt_path = judge_dir / "prompt.md"
  prompt_path.write_text(prompt, encoding="utf-8")
  return prompt_path


# Returns {"score": float|None, "dimensions": [...], "error": str|None, "usage": dict|None}; transcripts land in judge_dir (FR-08 audit)
def evaluate_quality(workspace: Path, manifest: dict, rubric_path: Path, judge_dir: Path, config: dict, golden_dir: Path | None = None, prompts_path: Path | None = None) -> dict:
  judge_dir.mkdir(parents=True, exist_ok=True)
  input_path = build_judge_input(workspace, manifest, judge_dir, golden_dir, prompts_path)
  prompt_path = build_judge_prompt(Path(config["judge_prompt_template"]), rubric_path, judge_dir)
  response_path = judge_dir / "response.json"
  command = [config["judge_python"], config["call_llm_script"],
             "--model", config["judge_model"], "--input-file", str(input_path), "--prompt-file", str(prompt_path),
             "--output-file", str(response_path), "--response-format", "json",
             "--reasoning-effort", config.get("judge_effort", "medium"), "--keys-file", config["keys_file"],
             "--write-json-metadata"]
  try:
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=config.get("judge_timeout_seconds", 300))
  except subprocess.TimeoutExpired:
    return {"score": None, "dimensions": [], "error": "judge call timed out", "usage": None}
  (judge_dir / "call.log").write_text(f"command: {' '.join(command)}\nexit: {completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}", encoding="utf-8")
  if completed.returncode != 0:
    return {"score": None, "dimensions": [], "error": f"call-llm.py exit {completed.returncode} (see judge/call.log)", "usage": None}
  try:  # EC-04: unparseable judge output -> Tier 3 null, transcript kept
    payload = json.loads(response_path.read_text(encoding="utf-8"))
    dimensions = payload["dimensions"]
    score = sum(d["score"] for d in dimensions) / len(dimensions) / 100.0
  except (OSError, KeyError, TypeError, ValueError, ZeroDivisionError) as error:
    return {"score": None, "dimensions": [], "error": f"judge response unparseable ({type(error).__name__}: {error})", "usage": None}
  usage = None
  meta_path = response_path.with_suffix(".meta.json")
  if meta_path.exists():
    try: usage = json.loads(meta_path.read_text(encoding="utf-8")).get("usage")
    except (OSError, json.JSONDecodeError): pass
  return {"score": round(score, 3), "dimensions": dimensions, "error": None, "usage": usage}
