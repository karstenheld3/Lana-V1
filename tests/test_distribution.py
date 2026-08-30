"""Distribution tests: --version flag, bundled payload materialization (LANADIST-IP01 TC-01/02/12..15, LANADIST-FR-08)."""
import json, subprocess, sys
import pytest
from lana.config import KEY_FILE_TEMPLATE, load_lana_config, parse_key_file
from tests.conftest import TEST_MAPPING, TEST_PRICING, TEST_REGISTRY


def make_args(*argv):
  from lana.cli import build_arg_parser
  return build_arg_parser().parse_args(list(argv))


def run_scripted_runtime(tmp_path, monkeypatch):
  from lana.cli import build_runtime
  from lana.providers import reset_adapter_cache
  monkeypatch.setenv("LANA_SCRIPTED_ADAPTER", str(tmp_path / "unused-script.jsonl"))
  monkeypatch.delenv("LANA_CONFIG", raising=False)
  reset_adapter_cache()
  result = build_runtime(make_args(), tmp_path, interactive=False)
  reset_adapter_cache()
  return result


# ----------------------------------------- START: --version flag (TC-01, TC-02) ----------------------------------------------

# TC-01: --version exits 0 and prints the installed package version
def test_tc01_version_flag_prints_version(capsys):
  from lana.cli import package_version
  with pytest.raises(SystemExit) as exit_info:
    make_args("--version")
  assert exit_info.value.code == 0
  assert f"lana {package_version()}" in capsys.readouterr().out


# TC-02: --version has no zero-setup side effects (subprocess in a pristine cwd)
def test_tc02_version_flag_no_side_effects(tmp_path):
  result = subprocess.run([sys.executable, "-m", "lana", "--version"], cwd=tmp_path, capture_output=True, text=True, timeout=60)
  assert result.returncode == 0
  assert result.stdout.startswith("lana ")
  assert list(tmp_path.iterdir()) == []  # no config/, .lana-data/, .lana/ scaffolded

# ----------------------------------------- END: --version flag ---------------------------------------------------------------


# ----------------------------------------- START: bundled materialization (TC-12..15) ----------------------------------------

# TC-12: empty workspace -> full payload materialized (config trio + key template + agent library), each reported
def test_tc12_empty_workspace_full_materialization(tmp_path, monkeypatch, capsys, populated_bundle):
  app, agent, cost_tracker, prompt_system = run_scripted_runtime(tmp_path, monkeypatch)
  out = capsys.readouterr().out
  config_dir = tmp_path / "config"
  for name in ("lana-config.json", "model-registry.json", "model-parameter-mapping.json", "model-pricing.json", ".api-keys.txt"):
    assert (config_dir / name).is_file(), f"missing {name}"
    assert str(config_dir / name) in out  # every artifact reported (FR-08)
  assert (tmp_path / ".lana" / "skills").is_dir()
  assert len(prompt_system.rules) > 0 and len(prompt_system.workflows) > 0 and len(prompt_system.skills) > 0  # bundled library loaded
  assert "NOTICE: prompt system is empty" not in out


# TC-13: partial config (only pricing missing) -> only pricing recreated, existing files untouched (EC-15)
def test_tc13_partial_config_only_missing_recreated(tmp_path, monkeypatch, populated_bundle):
  config_dir = tmp_path / "config"
  config_dir.mkdir(parents=True)
  registry_content = json.dumps(TEST_REGISTRY)
  (config_dir / "model-registry.json").write_text(registry_content, encoding="utf-8")
  (config_dir / "model-parameter-mapping.json").write_text(json.dumps(TEST_MAPPING), encoding="utf-8")
  monkeypatch.delenv("LANA_CONFIG", raising=False)
  app = load_lana_config(tmp_path, require_keys=False)
  assert (config_dir / "model-pricing.json").is_file()  # recreated from bundle
  assert (config_dir / "model-registry.json").read_text(encoding="utf-8") == registry_content  # untouched
  created_names = {p.rsplit("\\", 1)[-1] for p in app.created_files}
  assert "model-pricing.json" in created_names and "model-registry.json" not in created_names


# TC-14: existing agent folder (even empty) -> never repopulated (EC-14)
def test_tc14_existing_agent_folder_untouched(tmp_path, monkeypatch, capsys, populated_bundle):
  (tmp_path / ".lana").mkdir()
  app, agent, cost_tracker, prompt_system = run_scripted_runtime(tmp_path, monkeypatch)
  out = capsys.readouterr().out
  assert list((tmp_path / ".lana").iterdir()) == []  # stays empty - user deletions respected
  assert "NOTICE: prompt system is empty" in out


# TC-15: materialized key template is keyless - commented provider lines, parse yields no entries (DD-09)
def test_tc15_key_template_is_keyless(tmp_path, monkeypatch, populated_bundle):
  run_scripted_runtime(tmp_path, monkeypatch)
  key_file = tmp_path / "config" / ".api-keys.txt"
  content = key_file.read_text(encoding="utf-8")
  assert content == KEY_FILE_TEMPLATE
  assert "# OPENAI_API_KEY=" in content and "# ANTHROPIC_API_KEY=" in content
  assert parse_key_file(key_file) == {}  # nothing uncommented, no values


# Bundle absent (source checkout without sync) -> empty-folder scaffold fallback keeps startup working
def test_bundle_absent_falls_back_to_empty_scaffold(tmp_path, monkeypatch, capsys):
  import lana.config as config_module
  monkeypatch.setattr(config_module, "bundled_root", lambda: None)
  from tests.conftest import write_config_dir
  write_config_dir(tmp_path)  # bundle unavailable - config must pre-exist
  app, agent, cost_tracker, prompt_system = run_scripted_runtime(tmp_path, monkeypatch)
  out = capsys.readouterr().out
  assert (tmp_path / ".lana" / "rules").is_dir() and (tmp_path / ".lana" / "skills").is_dir()
  assert "NOTICE: prompt system is empty" in out

# ----------------------------------------- END: bundled materialization ------------------------------------------------------
