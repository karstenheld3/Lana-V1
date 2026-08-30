"""Tier 3 QualityEvaluator: rubric-anchored judge via @skills:llm-evaluation call-llm.py (LANATEST-SP01 FR-08, IP01 P3)."""
import json, subprocess
from pathlib import Path


def build_judge_input(workspace: Path, manifest: dict, judge_dir: Path, golden_dir: Path | None) -> Path:
  sections = ["# AGENT OUTPUT"]
  for pattern in manifest.get("required_files", []):
    for path in sorted(workspace.glob(pattern)):
      if ".lana-data" in path.parts: continue
      sections.append(f"## FILE: {path.relative_to(workspace)}\n\n{path.read_text(encoding='utf-8', errors='replace')}")
  if len(sections) == 1: sections.append("(no output files found)")
  if golden_dir and golden_dir.exists():  # reference-guided judging: golden calibrates, never dictates (see template Reference Handling)
    golden_files = sorted(p for p in golden_dir.rglob("*") if p.is_file())
    if golden_files:
      sections.append("# GOLDEN REFERENCE")
      for path in golden_files:
        sections.append(f"## REFERENCE FILE: {path.relative_to(golden_dir)}\n\n{path.read_text(encoding='utf-8', errors='replace')}")
  input_path = judge_dir / "input.md"
  input_path.write_text("\n\n".join(sections), encoding="utf-8")
  return input_path


def build_judge_prompt(template_path: Path, rubric_path: Path, judge_dir: Path) -> Path:
  prompt = template_path.read_text(encoding="utf-8").replace("{RUBRIC}", rubric_path.read_text(encoding="utf-8"))
  prompt_path = judge_dir / "prompt.md"
  prompt_path.write_text(prompt, encoding="utf-8")
  return prompt_path


# Returns {"score": float|None, "dimensions": [...], "error": str|None}; transcripts land in judge_dir (FR-08 audit)
def evaluate_quality(workspace: Path, manifest: dict, rubric_path: Path, judge_dir: Path, config: dict, golden_dir: Path | None = None) -> dict:
  judge_dir.mkdir(parents=True, exist_ok=True)
  input_path = build_judge_input(workspace, manifest, judge_dir, golden_dir)
  prompt_path = build_judge_prompt(Path(config["judge_prompt_template"]), rubric_path, judge_dir)
  response_path = judge_dir / "response.json"
  command = [config["judge_python"], config["call_llm_script"],
             "--model", config["judge_model"], "--input-file", str(input_path), "--prompt-file", str(prompt_path),
             "--output-file", str(response_path), "--response-format", "json",
             "--reasoning-effort", config.get("judge_effort", "medium"), "--keys-file", config["keys_file"]]
  try:
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=config.get("judge_timeout_seconds", 300))
  except subprocess.TimeoutExpired:
    return {"score": None, "dimensions": [], "error": "judge call timed out"}
  (judge_dir / "call.log").write_text(f"command: {' '.join(command)}\nexit: {completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}", encoding="utf-8")
  if completed.returncode != 0:
    return {"score": None, "dimensions": [], "error": f"call-llm.py exit {completed.returncode} (see judge/call.log)"}
  try:  # EC-04: unparseable judge output -> Tier 3 null, transcript kept
    payload = json.loads(response_path.read_text(encoding="utf-8"))
    dimensions = payload["dimensions"]
    score = sum(d["score"] for d in dimensions) / len(dimensions) / 100.0
  except (OSError, KeyError, TypeError, ValueError, ZeroDivisionError) as error:
    return {"score": None, "dimensions": [], "error": f"judge response unparseable ({type(error).__name__}: {error})"}
  return {"score": round(score, 3), "dimensions": dimensions, "error": None}
