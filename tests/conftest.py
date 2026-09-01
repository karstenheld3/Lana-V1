"""Shared fixtures: temp config dir, temp workspace, fake prompt system, in-process agent factory (IS-22)."""
import asyncio, json, platform
import pytest
from lana.agent import Agent
from lana.config import load_lana_config
from lana.cost import CostTracker
from lana.loader import load_prompt_systems
from lana.prompt import build_system_prompt
from lana.providers import reset_adapter_cache
from lana.session import SessionStore
from lana.tools import ToolContext, ToolRegistry

TEST_REGISTRY = {
  "models": [
    {"provider": "anthropic", "model_id": "claude-sonnet-4-5-20250929", "name": "Claude Sonnet 4.5", "context_window": 200000, "enabled": True, "status": "available"},
    {"provider": "openai", "model_id": "gpt-4.1-mini", "name": "GPT-4.1 Mini", "context_window": 1047576, "enabled": True, "status": "available"},
    {"provider": "openai", "model_id": "gpt-5.5", "name": "GPT-5.5", "context_window": 1050000, "enabled": True, "status": "available"},
    {"provider": "openai", "model_id": "gpt-5.5-pro", "name": "GPT-5.5 Pro", "context_window": 1050000, "enabled": False, "status": "available"},
  ],
  "model_id_startswith": [
    {"prefix": "gpt-4.1", "provider": "openai", "method": "temperature", "max_input": 1047576, "max_output": 32768, "temp_max": 2.0, "seed": True},
    {"prefix": "gpt-5.5", "provider": "openai", "method": "reasoning_effort", "max_input": 1050000, "max_output": 128000, "effort": ["none", "low", "medium", "high", "xhigh"], "default": "none", "seed": False},
    {"prefix": "claude-sonnet-4", "provider": "anthropic", "method": "thinking", "max_input": 200000, "max_output": 16384, "thinking_max": 100000},
  ],
}

TEST_MAPPING = {
  "effort_levels": ["none", "minimal", "low", "medium", "high", "xhigh", "max"],
  "effort_mapping": {
    "none":   {"temperature_factor": 0.0, "openai_reasoning_effort": "none", "anthropic_thinking_factor": 0.0, "anthropic_adaptive_effort": "low", "output_length_factor": 0.25},
    "low":    {"temperature_factor": 0.2, "openai_reasoning_effort": "low", "anthropic_thinking_factor": 0.04, "anthropic_adaptive_effort": "low", "output_length_factor": 0.5},
    "medium": {"temperature_factor": 0.35, "openai_reasoning_effort": "medium", "anthropic_thinking_factor": 0.1, "anthropic_adaptive_effort": "medium", "output_length_factor": 0.75},
    "high":   {"temperature_factor": 0.5, "openai_reasoning_effort": "high", "anthropic_thinking_factor": 0.32, "anthropic_adaptive_effort": "high", "output_length_factor": 1.0},
  },
}

TEST_PRICING = {
  "pricing": {
    "anthropic": {"claude-sonnet-4-5-20250929": {"input_per_1m": 3.00, "cached_per_1m": 0.30, "cache_write_per_1m": 3.75, "output_per_1m": 15.00, "context_window_k": 200, "currency": "USD"}},
    "openai": {"gpt-4.1-mini": {"input_per_1m": 0.40, "cached_per_1m": 0.10, "output_per_1m": 1.60, "context_window_k": 1024, "currency": "USD"}},
  }
}

DEFAULT_LANA_CONFIG = {
  "roles": {
    "generator": {"model_id": "claude-sonnet-4-5-20250929", "effort": "medium"},
    "summarizer": {"model_id": "gpt-4.1-mini", "effort": "low"},
    "websearch": {"model_id": "gpt-4.1-mini", "effort": "low"},
  },
  "agent_folder": ".lana",
  "rule_block_max_chars": 6000,
  "max_tool_calls_per_prompt": 40,
  "auto_continue": False,
  "tool_result_max_chars": 50000,
  "compaction_threshold_fraction": 0.6,
  "compaction_threshold_max_tokens": 150000,
  "execution_policy": "manual",
  "command_denylist": ["rm", "del", "rmdir", "erase", "ri", "Remove-Item", "Move-Item", "format", "kill", "pkill", "Stop-Process", "shutdown", "git push --force"],
}


# Write a complete isolated config folder; returns its path. Overrides patch the lana-config content.
def write_config_dir(base_path, lana_overrides=None, key_lines=("OPENAI_API_KEY=sk-test-openai", "ANTHROPIC_API_KEY=sk-test-anthropic")):
  config_dir = base_path / "config"
  config_dir.mkdir(parents=True, exist_ok=True)
  lana_content = json.loads(json.dumps(DEFAULT_LANA_CONFIG))
  if lana_overrides: lana_content.update(lana_overrides)
  (config_dir / "lana-config.json").write_text(json.dumps(lana_content, indent=2), encoding="utf-8")
  (config_dir / "model-registry.json").write_text(json.dumps(TEST_REGISTRY, indent=2), encoding="utf-8")
  (config_dir / "model-parameter-mapping.json").write_text(json.dumps(TEST_MAPPING, indent=2), encoding="utf-8")
  (config_dir / "model-pricing.json").write_text(json.dumps(TEST_PRICING, indent=2), encoding="utf-8")
  if key_lines is not None: (config_dir / ".api-keys.txt").write_text("\n".join(key_lines) + "\n", encoding="utf-8")
  return config_dir


# Create a temporary bundled root with test config files and a minimal agent library (rules/workflows/skills).
# Used by tests that exercise materialization from `bundled_root()` (LANADIST-FR-08).
def make_fake_bundle(base_path):
  bundle = base_path / "_test_bundle"
  config = bundle / "config"
  config.mkdir(parents=True)
  (config / "model-registry.json").write_text(json.dumps(TEST_REGISTRY), encoding="utf-8")
  (config / "model-parameter-mapping.json").write_text(json.dumps(TEST_MAPPING), encoding="utf-8")
  (config / "model-pricing.json").write_text(json.dumps(TEST_PRICING), encoding="utf-8")
  write_prompt_system(bundle / "agent",
    rules={"default.md": "---\ntrigger: always_on\n---\nDefault rule"},
    workflows={"default": "---\ndescription: Default workflow\n---\n# Default"},
    skills={"default-skill": ("---\nname: default\ndescription: Default\n---\n# Default", {})})
  return bundle


@pytest.fixture
def populated_bundle(tmp_path, monkeypatch):
  """Monkeypatch bundled_root() to return a temp directory with test content so materialization tests pass even when src/lana/bundled/ is empty."""
  bundle = make_fake_bundle(tmp_path)
  import lana.config as config_module
  monkeypatch.setattr(config_module, "bundled_root", lambda: bundle)
  return bundle


@pytest.fixture
def workspace(tmp_path):
  write_config_dir(tmp_path)
  return tmp_path


# Build a prompt system folder: rules/workflows = {filename_or_name: content}, skills = {name: (frontmatter+body, {relpath: content})}
def write_prompt_system(base_path, rules=None, workflows=None, skills=None):
  base_path.mkdir(parents=True, exist_ok=True)
  for filename, content in (rules or {}).items(): (base_path / "rules").mkdir(exist_ok=True); (base_path / "rules" / filename).write_text(content, encoding="utf-8")
  for name, content in (workflows or {}).items(): (base_path / "workflows").mkdir(exist_ok=True); (base_path / "workflows" / f"{name}.md").write_text(content, encoding="utf-8")
  for name, (skill_md, supporting) in (skills or {}).items():
    folder = base_path / "skills" / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(skill_md, encoding="utf-8")
    for relative_path, content in (supporting or {}).items():
      target = folder / relative_path
      target.parent.mkdir(parents=True, exist_ok=True)
      target.write_text(content, encoding="utf-8")
  return base_path


@pytest.fixture
def fake_system(tmp_path):
  base = write_prompt_system(tmp_path / "fake_system",
    rules={"alpha.md": "---\ntrigger: always_on\n---\nAlpha rule body", "beta.md": "Beta rule body without frontmatter", "gamma.md": "---\ntrigger: model_decision\n---\nGamma body"},
    workflows={"prime": "---\ndescription: Prime context\n---\n# Prime Workflow\n\nStep 1: read notes.", "verify": "---\ndescription: Verify work\n---\n# Verify Workflow\n\nStep 1: check."},
    skills={"demo-skill": ("---\nname: demo-skill\ndescription: Demo skill\n---\n# Demo Skill\n\nUse wisely.", {"GUIDE.md": "guide", "sub/EXTRA.md": "extra"})})
  return base


@pytest.fixture
def clean_key_env(monkeypatch):
  monkeypatch.delenv("OPENAI_API_KEY", raising=False)
  monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
  monkeypatch.delenv("LANA_SCRIPTED_ADAPTER", raising=False)
  monkeypatch.delenv("LANA_CONFIG", raising=False)


# Collect all events of one prompt run synchronously
def collect_events(agent: Agent, text: str) -> list:
  async def consume():
    return [event async for event in agent.run_prompt(text)]
  return asyncio.run(consume())


# Consume events until predicate matches (returns consumed list); then the generator is closed (cancellation simulation)
def collect_until(agent: Agent, text: str, predicate) -> list:
  async def consume():
    consumed = []
    generator = agent.run_prompt(text)
    async for event in generator:
      consumed.append(event)
      if predicate(event): await generator.aclose(); break
    return consumed
  return asyncio.run(consume())


@pytest.fixture
def agent_factory(tmp_path, monkeypatch, fake_system):
  from lana.cli import EXECUTORS
  from tests.scripted_adapter import write_script

  def make(turns: list[dict], lana_overrides: dict = None, approve_callback=None, continue_callback=None, use_compactor=False) -> Agent:
    workspace = tmp_path / "ws"
    workspace.mkdir(exist_ok=True)
    write_config_dir(workspace, lana_overrides=lana_overrides)
    script = write_script(workspace / "script.jsonl", turns)
    monkeypatch.setenv("LANA_SCRIPTED_ADAPTER", str(script))
    reset_adapter_cache()
    app = load_lana_config(workspace, require_keys=False)
    app.scripted = True
    prompt_system = load_prompt_systems([fake_system])
    system_prompt = build_system_prompt(prompt_system, {"os": platform.system().lower(), "workspace": str(workspace), "git_root": ""})
    registry = ToolRegistry(os_name="windows", shell="pwsh", skills=prompt_system.skills)
    for name, executor in EXECUTORS.items(): registry.register(name, executor)
    tool_context = ToolContext(workspace=workspace, data_dir=app.data_dir, tool_result_max_chars=app.lana.tool_result_max_chars, prompt_system=prompt_system, app_config=app)
    session = SessionStore.create(app.data_dir)
    cost_tracker = CostTracker(app)
    compactor = None
    if use_compactor:
      from lana.compaction import make_compactor
      compactor = make_compactor(app)
    agent = Agent(app, prompt_system, system_prompt, registry, tool_context, session, approve_callback=approve_callback, continue_callback=continue_callback, cost_fn=cost_tracker.record, compactor=compactor)
    agent.cost_tracker = cost_tracker  # test convenience
    return agent

  yield make
  reset_adapter_cache()
