"""Selftest framework offline tests (LANATEST-TP01 TC-01..13, TC-17..19): menu, selection, discovery, offline categories, results."""
import asyncio, copy, importlib.util, json
from pathlib import Path
import pytest
from tests.conftest import TEST_MAPPING, TEST_PRICING, TEST_REGISTRY, write_config_dir, write_prompt_system

SCRIPT_PATH = Path(__file__).resolve().parents[1] / ".lana" / "skills" / "selftest" / "selftest.py"


def load_selftest_module():
  spec = importlib.util.spec_from_file_location("selftest", SCRIPT_PATH)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


@pytest.fixture(scope="module")
def selftest():
  return load_selftest_module()


def make_ctx(selftest, tmp_path, registry=None, pricing=None, keys=None, **arg_overrides):
  args = selftest.parse_args([])
  for key, value in {"budget": 5.0, "timeout": 60, "no_network": True, **arg_overrides}.items(): setattr(args, key, value)
  ctx = selftest.Context(workspace=tmp_path, config_dir=tmp_path / "config", args=args)
  ctx.registry = copy.deepcopy(registry if registry is not None else TEST_REGISTRY)
  ctx.mapping = copy.deepcopy(TEST_MAPPING)
  ctx.pricing = copy.deepcopy((pricing if pricing is not None else TEST_PRICING)["pricing"])
  ctx.keys = keys if keys is not None else {}
  return ctx


def make_workspace(tmp_path, with_prompt_system=True):
  write_config_dir(tmp_path)
  if with_prompt_system:
    write_prompt_system(tmp_path / ".lana",
      rules={"r.md": "rule"},
      workflows={"prime": "---\ndescription: Prime\n---\n# Prime"},
      skills={"demo": ("---\nname: demo\n---\n# Demo", {})})
  return tmp_path


def run_main(selftest, monkeypatch, workspace, argv, clear_keys=True):
  monkeypatch.chdir(workspace)
  monkeypatch.delenv("LANA_CONFIG", raising=False)
  if clear_keys:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
  return selftest.main(argv)


def latest_results(workspace):
  runs = sorted((workspace / ".lana-data" / "selftest").iterdir())
  return json.loads((runs[-1] / "results.json").read_text(encoding="utf-8"))


# ----------------------------------------- START: Selection and menu (TC-01..04) ---------------------------------------------

def test_tc01_menu_lists_all_categories(selftest, capsys):
  assert selftest.main(["--menu"]) == 0
  output = capsys.readouterr().out
  for code in ("01", "02", "03", "04", "05", "06"): assert f"\n  {code}  " in output
  assert "offline" in output and "live" in output and "~$" in output


def test_tc02_codes_selected_ascending(selftest):
  selected = selftest.select_categories(["04", "01"])
  assert [entry[0] for entry in selected] == ["01", "04"]


def test_tc03_group_selectors(selftest):
  assert [e[0] for e in selftest.select_categories(["offline"])] == ["01", "02", "03"]
  assert [e[0] for e in selftest.select_categories(["live"])] == ["04", "05", "06"]
  assert [e[0] for e in selftest.select_categories(["all"])] == ["01", "02", "03", "04", "05", "06"]


def test_tc04_invalid_code_exit_2(selftest, monkeypatch, tmp_path, capsys):
  assert run_main(selftest, monkeypatch, make_workspace(tmp_path), ["99"]) == 2
  assert "valid: 01, 02, 03, 04, 05, 06" in capsys.readouterr().out

# ----------------------------------------- END: Selection and menu -----------------------------------------------------------


# ----------------------------------------- START: Discovery (TC-05..07) ------------------------------------------------------

def test_tc05_discovery_filters_enabled_available(selftest, tmp_path):
  registry = copy.deepcopy(TEST_REGISTRY)
  registry["models"].append({"provider": "openai", "model_id": "gpt-4.1", "name": "GPT-4.1", "context_window": 1, "enabled": True, "status": "untested"})
  ctx = make_ctx(selftest, tmp_path, registry=registry)
  ids = [m["model_id"] for m in selftest.discover_models(ctx)]
  assert ids == ["claude-sonnet-4-5-20250929", "gpt-4.1-mini", "gpt-5.5"]  # -pro disabled, untested excluded


def test_tc06_no_prefix_match_excluded_with_warning(selftest, tmp_path, capsys):
  registry = copy.deepcopy(TEST_REGISTRY)
  registry["models"].append({"provider": "openai", "model_id": "o9-experimental", "name": "O9", "context_window": 1, "enabled": True, "status": "available"})
  ids = [m["model_id"] for m in selftest.discover_models(make_ctx(selftest, tmp_path, registry=registry))]
  assert "o9-experimental" not in ids and "matches no model_id_startswith prefix" in capsys.readouterr().out


def test_tc07_missing_key_skips_not_fails(selftest, tmp_path):
  ctx = make_ctx(selftest, tmp_path, keys={})  # no keys at all (EC-01)
  model = selftest.discover_models(ctx)[0]
  entry = selftest.live_test(ctx, "04", model["model_id"], model, "medium", [], [])
  assert entry["status"] == "skip" and "API_KEY" in entry["error_message"]

# ----------------------------------------- END: Discovery --------------------------------------------------------------------


# ----------------------------------------- START: Offline categories (TC-08..10) ---------------------------------------------

def test_tc08_configuration_valid_workspace(selftest, tmp_path, capsys):
  workspace = make_workspace(tmp_path)
  ctx = make_ctx(selftest, workspace, keys={"openai": "sk-test", "anthropic": "sk-test"})
  selftest.run_configuration(ctx)
  assert all(t["status"] == "pass" for t in ctx.tests), [t for t in ctx.tests if t["status"] != "pass"]


def test_tc09_missing_pricing_fails_check_not_run(selftest, tmp_path):
  workspace = make_workspace(tmp_path)
  (workspace / "config" / "model-pricing.json").unlink()
  ctx = make_ctx(selftest, workspace, keys={"openai": "sk-test"})
  selftest.run_configuration(ctx)  # EC-14: must not raise
  config_check = [t for t in ctx.tests if t["check"] == "config_and_roles"][0]
  assert config_check["status"] == "fail" and "model-pricing.json" in config_check["error_message"]


def test_tc10_skill_without_skill_md_fails_named(selftest, tmp_path):
  workspace = make_workspace(tmp_path)
  (workspace / ".lana" / "skills" / "broken-skill").mkdir(parents=True)
  ctx = make_ctx(selftest, workspace)
  selftest.run_prompt_system(ctx)
  skill_check = [t for t in ctx.tests if t["check"] == "skill_md"][0]
  assert skill_check["status"] == "fail" and "broken-skill" in skill_check["error_message"]

# ----------------------------------------- END: Offline categories -----------------------------------------------------------


# ----------------------------------------- START: Results, budget, exit codes (TC-11..13) ------------------------------------

def test_tc11_results_json_valid_and_counts_match(selftest, monkeypatch, tmp_path):
  workspace = make_workspace(tmp_path)
  assert run_main(selftest, monkeypatch, workspace, ["offline", "--no-network"]) == 0
  results = latest_results(workspace)
  assert results["categories_run"] == ["01", "02", "03"]
  assert sum(results["summary"].values()) == len(results["tests"])
  assert all(t["status"] == "pass" for t in results["tests"])


def test_tc12_budget_precheck_blocks_before_api(selftest, tmp_path):
  ctx = make_ctx(selftest, tmp_path, keys={"openai": "sk-test"}, budget=0.0)
  model = [m for m in selftest.discover_models(ctx) if m["provider"] == "openai"][0]
  entry = selftest.live_test(ctx, "04", model["model_id"], model, "medium", [], [])
  assert entry["status"] == "budget_exceeded" and not ctx.adapters  # no adapter created -> no API attempt


def test_tc13_exit_codes(selftest, monkeypatch, tmp_path):
  healthy = make_workspace(tmp_path / "healthy")
  assert run_main(selftest, monkeypatch, healthy, ["offline", "--no-network"]) == 0  # pass+skip only -> 0
  broken = make_workspace(tmp_path / "broken", with_prompt_system=False)  # no .lana -> category 03 fails
  assert run_main(selftest, monkeypatch, broken, ["03"]) == 1

# ----------------------------------------- END: Results, budget, exit codes --------------------------------------------------


# ----------------------------------------- START: Supplementary (TC-17..19) --------------------------------------------------

def test_tc17_environment_offline_checks_pass(selftest, tmp_path, capsys):
  ctx = make_ctx(selftest, tmp_path)  # no_network=True excludes endpoint checks
  selftest.run_environment(ctx)
  assert [t["check"] for t in ctx.tests] == ["python_version", "lana_version", "data_dir"]
  assert all(t["status"] == "pass" for t in ctx.tests)
  assert (tmp_path / ".lana-data").is_dir()


def test_tc18_timeout_fails_test_and_continues(selftest, tmp_path):
  class StallingAdapter:
    async def stream_turn(self, system, tools, messages, role):
      await asyncio.sleep(10)
      yield None
  ctx = make_ctx(selftest, tmp_path, keys={"openai": "sk-test"}, timeout=1)
  ctx.adapters["openai"] = StallingAdapter()  # pre-populated cache -> get_adapter never touches the SDK
  model = [m for m in selftest.discover_models(ctx) if m["provider"] == "openai"][0]
  entry = selftest.live_test(ctx, "04", model["model_id"], model, "medium", [], [])
  assert entry["status"] == "fail" and entry["error_message"] == "timeout after 1s"


def test_tc19_effort_matrix_selection(selftest, tmp_path):
  ctx = make_ctx(selftest, tmp_path)
  representatives = selftest.matrix_representatives(ctx, selftest.discover_models(ctx))
  assert representatives["temperature"]["model_id"] == "gpt-4.1-mini"      # priced 0.40 -> cheapest
  assert representatives["thinking"]["model_id"] == "claude-sonnet-4-5-20250929"
  assert representatives["reasoning_effort"]["model_id"] == "gpt-5.5"
  assert representatives["reasoning_effort"]["prefix_entry"]["effort"] == ["none", "low", "medium", "high", "xhigh"]  # from prefix array
  assert (representatives["temperature"]["prefix_entry"].get("effort") or selftest.DEFAULT_EFFORTS) == ["low", "medium", "high"]  # fallback

# ----------------------------------------- END: Supplementary ----------------------------------------------------------------
