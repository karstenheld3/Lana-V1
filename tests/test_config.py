"""TK-004: configuration loading and validation (IP01 TC-01..06)."""
import json
import pytest
from lana.config import ConfigError, load_lana_config
from tests.conftest import write_config_dir


# TC-01: valid config + registry -> roles resolved with provider params
def test_tc01_valid_config_resolves_roles(workspace, clean_key_env):
  app = load_lana_config(workspace)
  generator, summarizer = app.roles["generator"], app.roles["summarizer"]
  assert generator.provider == "anthropic" and generator.method == "thinking"
  assert generator.params == {"thinking_budget": 10000}  # 0.1 x 100000 (medium)
  assert generator.max_input == 200000 and generator.max_output == 16384
  assert summarizer.provider == "openai" and summarizer.method == "temperature"
  assert summarizer.params == {"temperature": 0.4}  # 0.2 x 2.0 (low)
  assert app.keys == {"anthropic": "sk-test-anthropic", "openai": "sk-test-openai"}


# TC-02: disabled model (EC-14) -> ConfigError names model, role, file
def test_tc02_disabled_model_names_model_role_file(tmp_path, clean_key_env):
  write_config_dir(tmp_path, lana_overrides={"roles": {"generator": {"model_id": "gpt-5.5-pro", "effort": "medium"}}})
  with pytest.raises(ConfigError) as error: load_lana_config(tmp_path)
  message = str(error.value)
  assert "gpt-5.5-pro" in message and "generator" in message and "model-registry.json" in message and "Fix:" in message


def test_tc02b_unknown_model_names_model_role_file(tmp_path, clean_key_env):
  write_config_dir(tmp_path, lana_overrides={"roles": {"generator": {"model_id": "no-such-model", "effort": "low"}}})
  with pytest.raises(ConfigError) as error: load_lana_config(tmp_path)
  assert "no-such-model" in str(error.value) and "model-registry.json" in str(error.value)


# TC-03: missing key -> error; env var wins over key file
def test_tc03_missing_key_errors_and_env_wins(tmp_path, clean_key_env, monkeypatch):
  write_config_dir(tmp_path, key_lines=("ANTHROPIC_API_KEY=file-anthropic",))
  with pytest.raises(ConfigError) as error: load_lana_config(tmp_path)
  assert "OPENAI_API_KEY" in str(error.value) and ".api-keys.txt" in str(error.value)
  monkeypatch.setenv("OPENAI_API_KEY", "env-openai")
  monkeypatch.setenv("ANTHROPIC_API_KEY", "env-anthropic")
  app = load_lana_config(tmp_path)
  assert app.keys["openai"] == "env-openai"
  assert app.keys["anthropic"] == "env-anthropic"  # env wins over file entry


def test_tc03b_require_keys_false_skips_resolution(tmp_path, clean_key_env):
  write_config_dir(tmp_path, key_lines=None)
  app = load_lana_config(tmp_path, require_keys=False)
  assert app.keys == {}


# TC-04: effort translation per provider method
def test_tc04_effort_translation_per_method(tmp_path, clean_key_env):
  write_config_dir(tmp_path, lana_overrides={"roles": {
    "generator": {"model_id": "gpt-5.5", "effort": "high"},
    "summarizer": {"model_id": "gpt-4.1-mini", "effort": "high"},
    "websearch": {"model_id": "claude-sonnet-4-5-20250929", "effort": "high"},
  }})
  app = load_lana_config(tmp_path)
  assert app.roles["generator"].params == {"reasoning_effort": "high"}
  assert app.roles["summarizer"].params == {"temperature": 1.0}  # 0.5 x 2.0
  assert app.roles["websearch"].params == {"thinking_budget": 32000}  # 0.32 x 100000


def test_tc04b_unknown_effort_level_rejected(tmp_path, clean_key_env):
  write_config_dir(tmp_path, lana_overrides={"roles": {"generator": {"model_id": "gpt-5.5", "effort": "ultra"}}})
  with pytest.raises(ConfigError) as error: load_lana_config(tmp_path)
  assert "ultra" in str(error.value)


# TC-05: missing pricing entry (EC-24) tolerated at load
def test_tc05_missing_pricing_tolerated(tmp_path, clean_key_env):
  config_dir = write_config_dir(tmp_path)
  pricing = json.loads((config_dir / "model-pricing.json").read_text(encoding="utf-8"))
  del pricing["pricing"]["anthropic"]["claude-sonnet-4-5-20250929"]
  (config_dir / "model-pricing.json").write_text(json.dumps(pricing), encoding="utf-8")
  app = load_lana_config(tmp_path)
  assert app.pricing["anthropic"].get("claude-sonnet-4-5-20250929") is None  # cost.py renders '?'


# TC-06: malformed lana-config.json -> error with line context
def test_tc06_malformed_json_line_context(tmp_path, clean_key_env):
  config_dir = write_config_dir(tmp_path)
  (config_dir / "lana-config.json").write_text('{\n  "roles": {\n  BROKEN\n}\n', encoding="utf-8")
  with pytest.raises(ConfigError) as error: load_lana_config(tmp_path)
  assert "line 3" in str(error.value) and "lana-config.json" in str(error.value)


def test_missing_generator_role_rejected(tmp_path, clean_key_env):
  write_config_dir(tmp_path, lana_overrides={"roles": {"summarizer": {"model_id": "gpt-4.1-mini", "effort": "low"}}})
  with pytest.raises(ConfigError) as error: load_lana_config(tmp_path)
  assert "generator" in str(error.value)
