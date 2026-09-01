"""Lana selftest runner (LANATEST-SP01, IP01): category menu, offline health checks, live model tests.

Categories: 01 Environment, 02 Configuration, 03 Prompt System (offline) | 04 Sweep, 05 Effort Matrix, 06 Tool Calls (live).
Runs from the workspace root. Results: stdout + .lana-data/selftest/<timestamp>/results.json (written even on interrupt, IG-04).
Exit codes: 0 all pass/skip, 1 any fail/error, 2 invalid arguments, 3 environment problem.
"""
import argparse, asyncio, datetime, json, os, socket, ssl, sys, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

try:
  from lana.config import RoleSpec, load_lana_config, parse_key_file, read_json, resolve_key, resolve_role
  from lana.models import Message, ToolCall
except ImportError:  # EC-03: wrong interpreter
  print(f"ERROR: cannot import 'lana' with this interpreter ({sys.version.split()[0]}, {sys.executable}).")
  print("  HINT: set LANA_PYTHON to the interpreter that runs Lana, or use .venv\\Scripts\\python.exe in a dev checkout.")
  sys.exit(3)

PROVIDERS = ("openai", "anthropic")
ENDPOINTS = {"openai": "api.openai.com", "anthropic": "api.anthropic.com"}
ENV_KEY_NAMES = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
SYSTEM_PROMPT = "You are a test agent. Respond with exactly: SELFTEST OK"
USER_PROMPT = "Respond now."
TOOL_SYSTEM_PROMPT = "You are a test agent. Use the read_file tool once, then answer DONE."
TOOL_PROMPT = "Read the file 'notes.md' using the read_file tool."
READ_FILE_TOOL = {"name": "read_file", "description": "Reads a file", "schema": {"type": "object", "additionalProperties": False, "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}
DEFAULT_EFFORTS = ["low", "medium", "high"]  # FR-08: methods without an effort array


@dataclass
class Context:
  workspace: Path
  config_dir: Path
  args: argparse.Namespace
  registry: dict = field(default_factory=dict)
  mapping: dict = field(default_factory=dict)
  pricing: dict = field(default_factory=dict)
  keys: dict = field(default_factory=dict)      # provider -> key (present providers only)
  adapters: dict = field(default_factory=dict)  # provider -> adapter (created lazily)
  tests: list = field(default_factory=list)     # result dicts
  cost_usd: float = 0.0


def record(ctx: Context, category: str, check: str, status: str, duration: float = 0.0, error: Optional[str] = None, **extra) -> dict:
  entry = {"category": category, "check": check, "status": status, "duration_seconds": round(duration, 1), "error_message": error, **extra}
  ctx.tests.append(entry)
  return entry


# ----------------------------------------- START: Offline categories ---------------------------------------------------------

def check_endpoint(host: str) -> None:
  with socket.create_connection((host, 443), timeout=5) as raw:
    with ssl.create_default_context().wrap_socket(raw, server_hostname=host):
      pass


def environment_checks(ctx: Context) -> list:  # injectable for tests (TP01-TC-17)
  def python_version():
    if sys.version_info < (3, 12): raise RuntimeError(f"Python {sys.version.split()[0]} < 3.12")
    return f"{sys.version.split()[0]}...OK"
  def lana_version():
    import importlib.metadata
    try: return importlib.metadata.version("lana")
    except importlib.metadata.PackageNotFoundError: return "0.0.0-dev (source)"
  def data_dir():
    target = ctx.workspace / ".lana-data"
    target.mkdir(parents=True, exist_ok=True)
    probe = target / ".selftest_probe"
    probe.write_text("ok", encoding="utf-8"); probe.unlink()
    return "writable...OK"
  checks = [("python_version", python_version), ("lana_version", lana_version), ("data_dir", data_dir)]
  if not ctx.args.no_network:
    checks += [(host, lambda h=host: (check_endpoint(h), "reachable...OK")[1]) for host in ENDPOINTS.values()]
  return checks


def run_environment(ctx: Context) -> None:
  for name, check in environment_checks(ctx):
    started = time.monotonic()
    try:
      detail = check()
      record(ctx, "01", name, "pass", time.monotonic() - started)
      print(f"  {name}: {detail}")
    except Exception as error:
      record(ctx, "01", name, "fail", time.monotonic() - started, str(error))
      print(f"  {name}: FAIL - {error}")


def run_configuration(ctx: Context) -> None:
  started = time.monotonic()
  try:  # EC-14: any config problem fails the check, never crashes the run
    app = load_lana_config(ctx.workspace, ctx.config_dir / "lana-config.json", require_keys=False)
    record(ctx, "02", "config_and_roles", "pass", time.monotonic() - started)
    print(f"  lana-config.json: valid...OK | roles: {len(app.roles)} resolved...OK")
  except Exception as error:
    record(ctx, "02", "config_and_roles", "fail", time.monotonic() - started, str(error))
    print(f"  config_and_roles: FAIL - {error}")
  key_states = [f"{provider} {'present' if provider in ctx.keys else 'MISSING'}" for provider in PROVIDERS]
  record(ctx, "02", "keys_present", "pass" if ctx.keys else "fail", 0.0, None if ctx.keys else "no API key for any provider")
  print(f"  keys: {', '.join(key_states)}")
  enabled = [m for m in ctx.registry.get("models", []) if m.get("enabled")]
  unpriced = [m["model_id"] for m in enabled if not price_rates(ctx, m["provider"], m["model_id"])]
  record(ctx, "02", "pricing_coverage", "pass", 0.0, None, unpriced=unpriced)  # warning only (FR-04)
  suffix = f" (missing: {', '.join(unpriced)})" if unpriced else ""
  print(f"  pricing: {len(enabled) - len(unpriced)} of {len(enabled)} enabled models priced{suffix}")


def run_prompt_system(ctx: Context) -> None:
  agent = ctx.workspace / ".lana"
  for sub in ("rules", "workflows", "skills"):
    exists = (agent / sub).is_dir()
    record(ctx, "03", f"folder_{sub}", "pass" if exists else "fail", 0.0, None if exists else f".lana/{sub}/ missing")
    print(f"  .lana/{sub}/: {'OK' if exists else 'FAIL - missing'}")
  bad_workflows = [f.name for f in sorted((agent / "workflows").glob("*.md")) if not f.read_text(encoding="utf-8").lstrip().startswith("---")] if (agent / "workflows").is_dir() else []
  record(ctx, "03", "workflow_frontmatter", "pass" if not bad_workflows else "fail", 0.0, f"missing frontmatter: {', '.join(bad_workflows)}" if bad_workflows else None)
  print(f"  workflows: {'all have frontmatter...OK' if not bad_workflows else 'FAIL - no frontmatter: ' + ', '.join(bad_workflows)}")
  missing_skill_md = [d.name for d in sorted((agent / "skills").iterdir()) if d.is_dir() and d.name != "__pycache__" and not (d / "SKILL.md").exists()] if (agent / "skills").is_dir() else []
  record(ctx, "03", "skill_md", "pass" if not missing_skill_md else "fail", 0.0, f"folders without SKILL.md: {', '.join(missing_skill_md)}" if missing_skill_md else None)
  print(f"  skills: {'all have SKILL.md...OK' if not missing_skill_md else 'FAIL - no SKILL.md: ' + ', '.join(missing_skill_md)}")

# ----------------------------------------- END: Offline categories -----------------------------------------------------------


# ----------------------------------------- START: Model helpers --------------------------------------------------------------

def prefix_entry_for(ctx: Context, model_id: str) -> Optional[dict]:
  for candidate in ctx.registry.get("model_id_startswith", []):
    if model_id.startswith(candidate["prefix"]): return candidate
  return None


def price_rates(ctx: Context, provider: str, model_id: str) -> Optional[dict]:
  provider_pricing = ctx.pricing.get(provider, {})
  if model_id in provider_pricing: return provider_pricing[model_id]
  for key, rates in provider_pricing.items():  # prefix fallback for dated anthropic IDs
    if isinstance(rates, dict) and "input_per_1m" in rates and model_id.startswith(key): return rates
  return None


def compute_cost(ctx: Context, provider: str, model_id: str, usage) -> Optional[float]:
  rates = price_rates(ctx, provider, model_id)
  if rates is None or usage is None: return None
  plain_input = max(usage.input_tokens - usage.cache_read_tokens, 0)
  cost = plain_input * rates.get("input_per_1m", 0.0) / 1e6 + usage.cache_read_tokens * rates.get("cached_per_1m", rates.get("input_per_1m", 0.0)) / 1e6
  cost += usage.cache_write_tokens * rates.get("cache_write_per_1m", 0.0) / 1e6 + usage.output_tokens * rates.get("output_per_1m", 0.0) / 1e6
  return round(cost, 6)


def discover_models(ctx: Context) -> list[dict]:  # FR-06 + FR-11 filters; key presence checked at test time (EC-01)
  models = []
  for model in ctx.registry.get("models", []):
    if not (model.get("enabled") and model.get("status") == "available"): continue
    if ctx.args.provider and model["provider"] != ctx.args.provider: continue
    if ctx.args.model and model["model_id"] != ctx.args.model: continue
    entry = prefix_entry_for(ctx, model["model_id"])
    if entry is None:
      print(f"  WARNING: '{model['model_id']}' matches no model_id_startswith prefix - excluded (EC-08)")
      continue
    models.append({**model, "prefix_entry": entry})
  return models


def get_adapter(ctx: Context, provider: str):
  if provider not in ctx.adapters:
    if provider == "openai":
      from lana.providers.openai_adapter import OpenAIAdapter
      ctx.adapters[provider] = OpenAIAdapter(api_key=ctx.keys[provider])
    else:
      from lana.providers.anthropic_adapter import AnthropicAdapter
      ctx.adapters[provider] = AnthropicAdapter(api_key=ctx.keys[provider])
  return ctx.adapters[provider]


def run_model_turn(ctx: Context, adapter, role, messages: list, tools: list, system: str = SYSTEM_PROMPT) -> list:  # EC-07 timeout, EC-13 one retry
  from lana.providers.base import is_retryable_error
  async def consume():
    return [delta async for delta in adapter.stream_turn(system, tools, messages, role)]
  for attempt in (1, 2):
    try:
      return asyncio.run(asyncio.wait_for(consume(), ctx.args.timeout))
    except asyncio.TimeoutError:
      raise TimeoutError(f"timeout after {ctx.args.timeout}s") from None
    except Exception as error:
      if attempt == 1 and is_retryable_error(error):
        print(f"    transient error ({type(error).__name__}), retrying in 3s...")
        time.sleep(3)
        continue
      raise
  return []  # unreachable


def budget_left(ctx: Context) -> bool:
  return ctx.args.budget - ctx.cost_usd >= 0.01


def live_test(ctx: Context, category: str, check: str, model: dict, effort: str, messages: list, tools: list, expect_tool_call: bool = False, system: str = SYSTEM_PROMPT) -> dict:
  """One budget-checked live round trip: resolve role, stream, verify deltas, record cost."""
  base = {"model_id": model["model_id"], "name": model.get("name", model["model_id"]), "provider": model["provider"], "method": model["prefix_entry"]["method"], "effort": effort}
  if model["provider"] not in ctx.keys:
    return record(ctx, category, check, "skip", 0.0, f"no {ENV_KEY_NAMES[model['provider']]}", **base)
  if not budget_left(ctx):
    return record(ctx, category, check, "budget_exceeded", 0.0, f"budget ${ctx.args.budget:.2f} exhausted", **base)
  started = time.monotonic()
  try:
    role = resolve_role("selftest", RoleSpec(model_id=model["model_id"], effort=effort), ctx.registry, ctx.mapping)
    deltas = run_model_turn(ctx, get_adapter(ctx, model["provider"]), role, messages, tools, system)
    duration = time.monotonic() - started
    usage_deltas = [d for d in deltas if d.kind == "usage" and d.usage]
    usage = usage_deltas[-1].usage if usage_deltas else None
    cost = compute_cost(ctx, model["provider"], model["model_id"], usage)
    if cost: ctx.cost_usd += cost
    if expect_tool_call:
      calls = [d for d in deltas if d.kind == "tool_call" and d.tool_call]
      if not calls or calls[0].tool_call.name != "read_file": raise AssertionError("no read_file tool_call emitted (EC-11)")
      json.loads(calls[0].tool_call.args_json)  # arguments must parse
    elif not any(d.kind == "text" and d.text for d in deltas):
      raise AssertionError("no text delta received")
    if usage is None or usage.input_tokens <= 0: raise AssertionError("no usage reported")
    usage_dict = {"input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens, "cache_read_tokens": usage.cache_read_tokens}
    entry = record(ctx, category, check, "pass", duration, None, usage=usage_dict, cost_usd=cost, **base)
    entry["deltas"] = deltas  # transient, stripped before serialization (tool call turn 2 needs them)
    return entry
  except Exception as error:
    return record(ctx, category, check, "fail", time.monotonic() - started, f"{type(error).__name__}: {error}" if not isinstance(error, (AssertionError, TimeoutError)) else str(error), **base)


def print_result(entry: dict) -> None:
  if entry["status"] == "pass":
    usage, cost = entry.get("usage", {}), entry.get("cost_usd")
    cost_text = f"${cost:.4f}" if cost is not None else "$?"
    print(f"    OK. {usage.get('input_tokens', 0)}in/{usage.get('output_tokens', 0)}out {cost_text} {entry['duration_seconds']}s")
  else:
    print(f"    {entry['status'].upper()}: {entry['error_message']}")

# ----------------------------------------- END: Model helpers ----------------------------------------------------------------


# ----------------------------------------- START: Live categories ------------------------------------------------------------

def sweep_effort(model: dict) -> str:  # DD-04: default effort from prefix entry
  return model["prefix_entry"].get("default") or "medium"


def run_sweep(ctx: Context) -> None:
  models = discover_models(ctx)
  counts = {p: sum(1 for m in models if m["provider"] == p) for p in PROVIDERS}
  print(f"  {counts['openai']} OpenAI, {counts['anthropic']} Anthropic | Budget: ${ctx.args.budget:.2f}")
  for index, model in enumerate(models, 1):
    effort = sweep_effort(model)
    print(f"  [ {index} / {len(models)} ] {model['model_id']} ({model['prefix_entry']['method']}, {effort})...")
    entry = live_test(ctx, "04", model["model_id"], model, effort, [Message(role="user", content=USER_PROMPT)], [])
    entry.pop("deltas", None)
    print_result(entry)


def matrix_representatives(ctx: Context, models: list[dict]) -> dict:  # DD-05: cheapest per method (input rate, fallback context size)
  def price_key(model):
    rates = price_rates(ctx, model["provider"], model["model_id"])
    return (rates.get("input_per_1m", 999.0) if rates else 999.0, model.get("context_window") or 10**9)
  representatives = {}
  for model in sorted(models, key=price_key):
    representatives.setdefault(model["prefix_entry"]["method"], model)
  return representatives


def run_effort_matrix(ctx: Context) -> None:
  representatives = matrix_representatives(ctx, discover_models(ctx))
  print(f"  {len(representatives)} methods")
  for method, model in representatives.items():
    efforts = model["prefix_entry"].get("effort") or DEFAULT_EFFORTS
    print(f"  {model['model_id']} ({method}): {len(efforts)} efforts...")
    for effort in efforts:
      entry = live_test(ctx, "05", f"{model['model_id']}@{effort}", model, effort, [Message(role="user", content=USER_PROMPT)], [])
      entry.pop("deltas", None)
      print(f"    {effort}: " + ("OK" if entry["status"] == "pass" else f"{entry['status'].upper()} - {entry['error_message']}"))


def tool_call_models(ctx: Context, models: list[dict]) -> list[dict]:  # DD-06: configured generator per provider, fallback cheapest
  generator_id = None
  try:
    generator_id = read_json(ctx.config_dir / "lana-config.json").get("roles", {}).get("generator", {}).get("model_id")
  except Exception:
    pass
  selected = []
  for provider in PROVIDERS:
    provider_models = [m for m in models if m["provider"] == provider]
    if not provider_models: continue
    configured = [m for m in provider_models if m["model_id"] == generator_id]
    cheapest = sorted(provider_models, key=lambda m: (price_rates(ctx, provider, m["model_id"]) or {}).get("input_per_1m", 999.0))[0]
    selected.append(configured[0] if configured else cheapest)
  return selected


def run_tool_calls(ctx: Context) -> None:
  models = tool_call_models(ctx, discover_models(ctx))
  print(f"  {len(models)} models")
  for model in models:
    effort = sweep_effort(model)
    first = live_test(ctx, "06", f"{model['model_id']}:call", model, effort, [Message(role="user", content=TOOL_PROMPT)], [READ_FILE_TOOL], expect_tool_call=True, system=TOOL_SYSTEM_PROMPT)
    if first["status"] != "pass":
      print(f"  {model['model_id']}: call...{first['status'].upper()} - {first['error_message']}")
      first.pop("deltas", None)
      continue
    deltas = first.pop("deltas")
    call = [d for d in deltas if d.kind == "tool_call"][0].tool_call
    thinking = [d.thinking for d in deltas if d.kind == "thinking" and d.thinking]
    followup = [Message(role="user", content=TOOL_PROMPT),
                Message(role="assistant", content="", tool_calls=[call], thinking=thinking),
                Message(role="tool", content="notes body: all fine", tool_call_id=call.id)]
    second = live_test(ctx, "06", f"{model['model_id']}:result", model, effort, followup, [READ_FILE_TOOL], system=TOOL_SYSTEM_PROMPT)
    second.pop("deltas", None)
    print(f"  {model['model_id']}: call...OK | result...{'OK' if second['status'] == 'pass' else second['status'].upper() + ' - ' + str(second['error_message'])}")

# ----------------------------------------- END: Live categories --------------------------------------------------------------


CATEGORIES = [
  ("01", "Environment", "offline", "free", run_environment),
  ("02", "Configuration", "offline", "free", run_configuration),
  ("03", "Prompt System", "offline", "free", run_prompt_system),
  ("04", "Model Sweep", "live", "~$0.10 (all available models)", run_sweep),
  ("05", "Model Effort Matrix", "live", "~$0.20 (cheapest model per method)", run_effort_matrix),
  ("06", "Model Tool Calls", "live", "~$0.05 (generator model per provider)", run_tool_calls),
]


def print_menu() -> None:
  print("SELFTEST MENU")
  for code, name, cost_class, estimate, _ in CATEGORIES:
    print(f"  {code}  {name:<20} {cost_class:<8} {estimate}")
  print("\nUsage: selftest.py <codes...> | all | offline | live [--provider P] [--model M] [--budget N] [--timeout S]")


def select_categories(selectors: list[str]) -> list[tuple]:  # FR-02
  valid = {code for code, *_ in CATEGORIES}
  selected = set()
  for selector in selectors:
    word = selector.lower()
    if word == "all": selected |= valid
    elif word in ("offline", "live"): selected |= {code for code, _, cost_class, _, _ in CATEGORIES if cost_class == word}
    elif selector in valid: selected.add(selector)
    else: raise ValueError(f"invalid category '{selector}' - valid: {', '.join(sorted(valid))}, all, offline, live")
  return [entry for entry in CATEGORIES if entry[0] in selected]


def write_results(ctx: Context, run_dir: Path, selected: list, started: float) -> None:  # IG-04/05
  summary = {status: sum(1 for t in ctx.tests if t["status"] == status) for status in ("pass", "fail", "skip", "error", "budget_exceeded")}
  payload = {"timestamp": datetime.datetime.now().isoformat(timespec="seconds"), "lana_version": lana_version_text(),
             "categories_run": [code for code, *_ in selected], "budget_usd": ctx.args.budget, "cost_usd": round(ctx.cost_usd, 6),
             "duration_seconds": round(time.monotonic() - started, 1), "summary": summary,
             "tests": [{k: v for k, v in t.items() if k != "deltas"} for t in ctx.tests]}
  run_dir.mkdir(parents=True, exist_ok=True)
  (run_dir / "results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def lana_version_text() -> str:
  import importlib.metadata
  try: return importlib.metadata.version("lana")
  except importlib.metadata.PackageNotFoundError: return "0.0.0-dev"


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
  parser = argparse.ArgumentParser(prog="selftest.py", description="Lana selftest (LANATEST-SP01)")
  parser.add_argument("selectors", nargs="*", help="category codes, all, offline, live")
  parser.add_argument("--menu", action="store_true", help="print category menu and exit")
  parser.add_argument("--provider", choices=PROVIDERS, help="live categories: only this provider")
  parser.add_argument("--model", help="live categories: only this model_id")
  parser.add_argument("--budget", type=float, default=5.0, help="live budget cap in USD (default 5.00)")
  parser.add_argument("--timeout", type=int, default=60, help="per-test timeout seconds (default 60)")
  parser.add_argument("--no-network", action="store_true", help="category 01: skip endpoint reachability checks")
  return parser.parse_args(argv)


def main(argv: Optional[list] = None) -> int:
  args = parse_args(argv)
  if args.menu or not args.selectors:
    print_menu()
    return 0
  try:
    selected = select_categories(args.selectors)
  except ValueError as error:
    print(f"ERROR: {error}")
    return 2
  workspace = Path.cwd()
  config_override = os.environ.get("LANA_CONFIG")
  config_dir = Path(config_override).parent if config_override else workspace / "config"
  ctx = Context(workspace=workspace, config_dir=config_dir, args=args)
  if args.model and not any(m["model_id"] == args.model and m.get("enabled") and m.get("status") == "available" for m in read_json_safe(config_dir / "model-registry.json").get("models", [])):
    print(f"ERROR: model '{args.model}' not found as enabled+available in model-registry.json")
    return 2
  try:
    ctx.registry = read_json(config_dir / "model-registry.json")
    ctx.mapping = read_json(config_dir / "model-parameter-mapping.json")
    ctx.pricing = read_json(config_dir / "model-pricing.json").get("pricing", {})
  except Exception as error:
    if any(cost_class == "live" for _, _, cost_class, _, _ in selected):
      print(f"ERROR: cannot load model config: {error}")
      return 3
  key_file_entries = parse_key_file(config_dir / ".api-keys.txt")
  ctx.keys = {p: k for p in PROVIDERS if (k := resolve_key(p, key_file_entries, "")[0])}
  run_dir = workspace / ".lana-data" / "selftest" / datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  try:  # EC-09: data dir must be writable before any API call
    run_dir.mkdir(parents=True, exist_ok=True)
  except OSError as error:
    print(f"ERROR: cannot create '{run_dir}': {error}")
    return 3
  started = time.monotonic()
  exit_code = 0
  try:
    for code, name, cost_class, _, runner in selected:
      print(f"SELFTEST: {code} {name}")
      runner(ctx)
      category_tests = [t for t in ctx.tests if t["category"] == code]
      counts = {s: sum(1 for t in category_tests if t["status"] == s) for s in ("pass", "fail", "skip", "budget_exceeded")}
      parts = [f"{counts['pass']} passed"] + [f"{counts[s]} {s.replace('budget_exceeded', 'over budget')}" for s in ("fail", "skip", "budget_exceeded") if counts[s]]
      print(f"  {code} {name}: {', '.join(parts).replace('fail', 'failed').replace('skip', 'skipped')}.\n")
  except KeyboardInterrupt:  # EC-06
    print("\nINTERRUPTED - writing partial results...")
    exit_code = 130
  finally:
    write_results(ctx, run_dir, selected, started)
  summary = {s: sum(1 for t in ctx.tests if t["status"] == s) for s in ("pass", "fail", "skip", "error", "budget_exceeded")}
  print(f"RESULT: {summary['pass']} passed, {summary['fail']} failed, {summary['skip']} skipped" + (f", {summary['budget_exceeded']} over budget" if summary['budget_exceeded'] else "") + f". Cost: ${ctx.cost_usd:.4f}.")
  print(f"Results: {run_dir / 'results.json'}")
  if exit_code == 0 and (summary["fail"] or summary["error"]): exit_code = 1  # IG-03
  return exit_code


def read_json_safe(path: Path) -> dict:
  try: return read_json(path)
  except Exception: return {}


if __name__ == "__main__":
  sys.exit(main())
