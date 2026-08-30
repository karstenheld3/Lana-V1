"""Lana eval suite runner (LANATEST-SP01 FR-01..09, IP01 P1): discover tests, run headless Lana, evaluate 3 tiers, record.

Usage:
  python run_evals.py <scope> [--scripted <script.jsonl>] [--skip-judge] [--strict-golden]
  scope: test key (01-T01), bucket folder (01_Basics), or All
"""
import argparse, datetime, difflib, importlib.metadata, json, os, re, shutil, subprocess, sys
from pathlib import Path
import yaml
from lana.prompt_queue import PromptQueueError, parse_queue
from evaluators import evaluate_process, evaluate_structure
from judge import evaluate_quality

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")  # check ids may contain non-cp1252 chars (e.g. emoji forbid rules)
sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

RUNNER_DIR = Path(__file__).resolve().parent
SUITE_DIR = RUNNER_DIR.parent
REPO_DIR = SUITE_DIR.parent.parent
RUNS_DIR = REPO_DIR / "evals" / "runs"
DEFAULTS = {"tiers": [1, 2], "thresholds": {"tier1": 0.9, "tier2": 0.7, "tier3": 0.7}, "step_timeout_seconds": 300, "policy": "turbo"}


def load_runner_config() -> dict:
  config = json.loads((RUNNER_DIR / "runner-config.json").read_text(encoding="utf-8"))
  for key in ("judge_python", "call_llm_script", "keys_file", "lana_config", "judge_prompt_template"):
    config[key] = str((REPO_DIR / config[key]).resolve()) if not Path(config[key]).is_absolute() else config[key]
  return config


# TEST.md carries one fenced yaml block with runner metadata (IP01 DC-06)
def parse_test_metadata(test_dir: Path) -> dict:
  metadata = dict(DEFAULTS)
  match = re.search(r"```yaml\n(.*?)\n```", (test_dir / "TEST.md").read_text(encoding="utf-8"), re.DOTALL)
  if match:
    loaded = yaml.safe_load(match.group(1)) or {}
    metadata.update(loaded)
    metadata["thresholds"] = {**DEFAULTS["thresholds"], **(loaded.get("thresholds") or {})}
  return metadata


def discover_tests(scope: str) -> list[Path]:
  buckets = sorted(path for path in SUITE_DIR.iterdir() if path.is_dir() and re.match(r"\d{2}_", path.name))
  tests = [test for bucket in buckets for test in sorted(bucket.glob("T[0-9][0-9]_*")) if test.is_dir()]
  if scope.lower() == "all": return tests
  key_match = re.fullmatch(r"(\d{2})-T(\d{2})", scope)
  if key_match:
    return [t for t in tests if t.parent.name.startswith(key_match.group(1) + "_") and t.name.startswith(f"T{key_match.group(2)}_")]
  return [t for t in tests if t.parent.name == scope]


def test_key(test_dir: Path) -> str:
  return f"{test_dir.parent.name[:2]}-{test_dir.name.split('_')[0]}"


def validate_test(test_dir: Path, strict_golden: bool) -> str | None:
  for required in ("TEST.md", "PROMPTS.md", "workspace", "expected/manifest.yaml", "expected/checks.yaml"):
    if not (test_dir / required).exists(): return f"missing '{required}' (EC-03)"
  try:  # malformed queue file fails BEFORE any agent run (mirrors Lana's own EC-25)
    parse_queue((test_dir / "PROMPTS.md").read_text(encoding="utf-8"))
  except PromptQueueError as error:
    return f"PROMPTS.md invalid: {error}"
  if strict_golden and not any((test_dir / "golden").glob("*")): return "missing golden reference (IG-04)"
  return None


def copy_scaffold(test_dir: Path, workdir: Path) -> str | None:
  shutil.copytree(test_dir / "workspace", workdir)
  scaffold_file = test_dir / "scaffold.json"
  if scaffold_file.exists():  # DC-04: copy CURRENT IPPS content from the repo .lana/
    for relative in json.loads(scaffold_file.read_text(encoding="utf-8")).get("copy_lana", []):
      source = REPO_DIR / ".lana" / relative
      if not source.exists(): return f"scaffold.json references missing '.lana/{relative}' (EC-05)"
      target = workdir / ".lana" / relative
      target.parent.mkdir(parents=True, exist_ok=True)
      shutil.copytree(source, target) if source.is_dir() else shutil.copy2(source, target)
  for sub in ("rules", "workflows", "skills"): (workdir / ".lana" / sub).mkdir(parents=True, exist_ok=True)  # empty folder stays untouched by zero-setup
  return None


def run_lana(test_dir: Path, workdir: Path, record_dir: Path, metadata: dict, config: dict, scripted: str | None) -> dict:
  env = dict(os.environ)
  env["LANA_CONFIG"] = config["lana_config"]  # config + keys stay OUTSIDE the workspace (NFR-03)
  if scripted: env["LANA_SCRIPTED_ADAPTER"] = str(Path(scripted).resolve())
  else: env.pop("LANA_SCRIPTED_ADAPTER", None)
  prompt_count = len(parse_queue((test_dir / "PROMPTS.md").read_text(encoding="utf-8")))  # exact count (validated in validate_test)
  timeout = metadata["step_timeout_seconds"] * prompt_count  # DC-02: overall timeout, stall monitoring deferred
  command = [sys.executable, "-m", "lana", "--prompt-file", str(test_dir / "PROMPTS.md"), "--output-format", "jsonl", "--policy", metadata["policy"]]
  print(f"    Running lana ({prompt_count} step(s), timeout {timeout}s, policy {metadata['policy']}{', SCRIPTED' if scripted else ''})...")
  try:
    completed = subprocess.run(command, cwd=workdir, env=env, capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    exit_code, stdout, stderr, timed_out = completed.returncode, completed.stdout, completed.stderr, False
  except subprocess.TimeoutExpired as expired:
    exit_code, stdout, stderr, timed_out = -1, expired.stdout or "", (expired.stderr or "") + "\nRUNNER: timeout - process killed (EC-02)", True
  (record_dir / "events.jsonl").write_text(stdout, encoding="utf-8")
  (record_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
  return {"exit_code": exit_code, "timed_out": timed_out}


def scan_secret_leak(record_dir: Path, keys_file: Path) -> str | None:
  values = [line.split("=", 1)[1].strip() for line in keys_file.read_text(encoding="utf-8").splitlines()
            if "=" in line and not line.strip().startswith("#") and len(line.split("=", 1)[1].strip()) >= 20]
  for path in record_dir.rglob("*"):
    if not path.is_file(): continue
    try:
      text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
      continue
    for value in values:
      if value in text: return f"CRITICAL: key material found in '{path.relative_to(record_dir)}' (EC-06)"
  return None


# Benchmark comparison: golden files are anchors, not pass/fail gates (CSRCMP: exact diff impossible for LLM output)
def compare_golden(test_dir: Path, workdir: Path) -> list[dict] | None:
  golden_dir = test_dir / "golden"
  golden_files = sorted(p for p in golden_dir.rglob("*") if p.is_file()) if golden_dir.exists() else []
  if not golden_files: return None
  comparison = []
  for golden_file in golden_files:
    relative = golden_file.relative_to(golden_dir)
    produced = workdir / relative
    entry = {"file": str(relative).replace("\\", "/"), "status": "missing", "similarity": 0.0}
    if produced.exists():
      try:
        golden_text = golden_file.read_text(encoding="utf-8").replace("\r\n", "\n")
        produced_text = produced.read_text(encoding="utf-8").replace("\r\n", "\n")
        entry["similarity"] = round(difflib.SequenceMatcher(None, golden_text, produced_text).ratio(), 3)
        entry["status"] = "match" if golden_text == produced_text else "differs"
      except UnicodeDecodeError:  # binary golden: byte equality only
        identical = golden_file.read_bytes() == produced.read_bytes()
        entry["status"], entry["similarity"] = ("match", 1.0) if identical else ("differs", 0.0)
    comparison.append(entry)
  return comparison


def run_test(test_dir: Path, run_dir: Path, config: dict, args) -> dict:
  key = test_key(test_dir)
  result = {"key": key, "name": test_dir.name, "tier1": None, "tier2": None, "tier3": None, "status": "invalid", "failed_checks": [], "notes": []}
  invalid_reason = validate_test(test_dir, args.strict_golden)
  if invalid_reason:
    result["notes"].append(invalid_reason)
    print(f"    INVALID: {invalid_reason}")
    return result
  if not any((test_dir / "golden").glob("*")) if (test_dir / "golden").exists() else True:
    result["notes"].append("golden reference pending (DC-03 warning)")
  metadata = parse_test_metadata(test_dir)
  record_dir = run_dir / key  # one subfolder per test key: runs/<timestamp>/01-T01/
  record_dir.mkdir(parents=True)
  workdir = record_dir / "workspace"
  scaffold_error = copy_scaffold(test_dir, workdir)
  if scaffold_error:
    result["notes"].append(scaffold_error)
    print(f"    INVALID: {scaffold_error}")
    return result
  run_info = run_lana(test_dir, workdir, record_dir, metadata, config, args.scripted)
  result["exit_code"] = run_info["exit_code"]
  manifest = yaml.safe_load((test_dir / "expected" / "manifest.yaml").read_text(encoding="utf-8")) or {}
  checks = yaml.safe_load((test_dir / "expected" / "checks.yaml").read_text(encoding="utf-8")) or {}
  tier1 = evaluate_structure(workdir, manifest)
  tier2 = evaluate_process(workdir, checks)
  result["tier1"], result["tier2"] = tier1["score"], tier2["score"]
  result["failed_checks"] = [c["id"] for c in tier1["checks"] + tier2["checks"] if not c["passed"]]
  result["check_details"] = {"tier1": tier1["checks"], "tier2": tier2["checks"]}
  result["golden"] = compare_golden(test_dir, workdir)
  rubric_path = test_dir / "expected" / "rubric.md"
  if 3 in metadata["tiers"] and rubric_path.exists() and not args.skip_judge:
    print(f"    Judging (model {config['judge_model']})...")
    quality = evaluate_quality(workdir, manifest, rubric_path, record_dir / "judge", config, golden_dir=test_dir / "golden")
    result["tier3"] = quality["score"]
    result["judge_dimensions"] = quality["dimensions"]
    if quality["error"]: result["notes"].append(f"judge: {quality['error']} (EC-04)")
  thresholds = metadata["thresholds"]
  passed = (result["tier1"] >= thresholds["tier1"] and result["tier2"] >= thresholds["tier2"]
            and (result["tier3"] is None or result["tier3"] >= thresholds["tier3"])
            and run_info["exit_code"] == 0)
  if run_info["exit_code"] != 0: result["notes"].append(f"lana exit code {run_info['exit_code']}" + (" (timeout)" if run_info["timed_out"] else "") + " (EC-01/EC-02)")
  result["status"] = "pass" if passed else "fail"
  leak = scan_secret_leak(record_dir, Path(config["keys_file"]))
  if leak:
    result["status"], result["notes"] = "error", result["notes"] + [leak]
  tier_line = " | ".join(f"Tier {n}: {result[f'tier{n}']:.2f}" for n in (1, 2, 3) if result[f"tier{n}"] is not None)
  print(f"    {tier_line}")
  print(f"    {result['status'].upper()}." + (f" Failed: {', '.join(result['failed_checks'])}." if result["failed_checks"] else ""))
  return result


def write_report(run_dir: Path, scope: str, agent_tag: str, results: list[dict]) -> None:
  lines = [f"# Eval Run Report: {scope}", "", f"**Run**: `{run_dir.name}`", f"**Agent**: {agent_tag}", f"**Executed**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
  counts = {status: sum(1 for r in results if r["status"] == status) for status in ("pass", "fail", "invalid", "error")}
  lines += [f"**Result**: {counts['pass']} passed, {counts['fail']} failed, {counts['invalid']} invalid, {counts['error']} error", "", "## Tests", ""]
  for r in results:
    tiers = " | ".join(f"Tier {n}: {r[f'tier{n}']:.2f}" for n in (1, 2, 3) if r.get(f"tier{n}") is not None) or "not evaluated"
    lines.append(f"- **{r['key']} {r['name']}**: {r['status'].upper()} ({tiers})")
    for check_id in r.get("failed_checks", []): lines.append(f"  - FAILED: `{check_id}`")
    for note in r.get("notes", []): lines.append(f"  - NOTE: {note}")
  lines += ["", "## Golden Benchmark Comparison", "", "Golden files are Cascade + IPPS reference anchors - similarity is informational, not a pass/fail gate.", ""]
  for r in results:
    golden = r.get("golden")
    if golden is None:
      lines.append(f"- **{r['key']}**: no golden reference (pending)")
      continue
    matches = sum(1 for g in golden if g["status"] == "match")
    average = sum(g["similarity"] for g in golden) / len(golden)
    lines.append(f"- **{r['key']}**: {matches}/{len(golden)} files match golden, avg similarity {average:.2f}")
    for g in golden:
      detail = "" if g["status"] == "match" else f" (similarity {g['similarity']:.2f})" if g["status"] == "differs" else ""
      lines.append(f"  - `{g['file']}`: {g['status'].upper()}{detail}")
  (run_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
  parser = argparse.ArgumentParser(description="Lana eval suite runner (LANATEST-SP01)")
  parser.add_argument("scope", help="test key (01-T01), bucket folder (01_Basics), or All")
  parser.add_argument("--scripted", help="LANA_SCRIPTED_ADAPTER script for offline runner test-drives (DC-07)")
  parser.add_argument("--skip-judge", action="store_true", help="skip Tier 3 judge calls")
  parser.add_argument("--strict-golden", action="store_true", help="missing golden/ -> INVALID (IG-04); default: warning (DC-03)")
  args = parser.parse_args()
  config = load_runner_config()
  tests = discover_tests(args.scope)
  if not tests:
    print(f"ERROR: no tests match scope '{args.scope}'. Buckets live in '{SUITE_DIR}'.", file=sys.stderr)
    return 2
  agent_tag = f"Lana-{importlib.metadata.version('lana')}"  # agent under test + its installed version
  run_dir = RUNS_DIR / f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{agent_tag}"  # scope lives in results.json/REPORT.md
  suffix = 1
  while run_dir.exists(): run_dir = run_dir.with_name(f"{run_dir.name}-{suffix}"); suffix += 1  # immutability (FR-05)
  run_dir.mkdir(parents=True)
  print(f"Running scope '{args.scope}' ({len(tests)} test(s))...")
  results = []
  for position, test_dir in enumerate(tests, 1):
    print(f"  [ {position} / {len(tests)} ] {test_key(test_dir)} {test_dir.name}...")
    results.append(run_test(test_dir, run_dir, config, args))
  (run_dir / "results.json").write_text(json.dumps({"run": run_dir.name, "agent": agent_tag, "scope": args.scope, "tests": results}, indent=2, ensure_ascii=False), encoding="utf-8")
  write_report(run_dir, args.scope, agent_tag, results)
  counts = {status: sum(1 for r in results if r["status"] == status) for status in ("pass", "fail", "invalid", "error")}
  print(f"Run recorded: {run_dir}")
  print(f"RESULT: {counts['pass']} passed, {counts['fail']} failed, {counts['invalid']} invalid, {counts['error']} error.")
  return 0 if counts["fail"] == counts["invalid"] == counts["error"] == 0 else 1


if __name__ == "__main__": sys.exit(main())
