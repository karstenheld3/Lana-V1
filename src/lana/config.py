"""Configuration loading and validation (LANAAGNT-FR-01, IS-03). All validation at startup (IG-05)."""
import importlib.resources, json, os, shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field, ValidationError

ENV_KEY_NAMES = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
PROVIDER_DISPLAY = {"openai": "OpenAI", "anthropic": "Anthropic"}

# Zero-setup default roles (FR-16, DD-02/DD-23): written to a missing DEFAULT config path at startup
DEFAULT_ROLES = {
  "generator": {"model_id": "claude-sonnet-4-5-20250929", "effort": "medium"},
  "summarizer": {"model_id": "gpt-4.1-mini", "effort": "low"},
  "websearch": {"model_id": "gpt-4.1-mini", "effort": "low"},
}

# Key file template is code-generated, never copied from any workspace (LANADIST-DD-09)
KEY_FILE_TEMPLATE = """# Lana API keys - one KEY=value line per provider. Lines starting with # are ignored.
# Alternative: set the same names as environment variables.
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
"""

BUNDLED_CONFIG_FILES = ("model-registry.json", "model-parameter-mapping.json", "model-pricing.json")


class ConfigError(Exception):
  pass


# ----------------------------------------- START: Schema ---------------------------------------------------------------------

class RoleSpec(BaseModel):
  model_id: str
  effort: str = "medium"


class LanaConfig(BaseModel):
  roles: dict[str, RoleSpec]
  agent_folder: str = ".lana"
  data_dir: str = ".lana-data"
  rule_block_max_chars: int = 6000
  max_tool_calls_per_prompt: int = 40
  auto_continue: bool = False
  tool_result_max_chars: int = 50000
  compaction_threshold_fraction: float = 0.6
  compaction_threshold_max_tokens: int = 150000
  execution_policy: Literal["manual", "auto", "turbo"] = "manual"
  command_denylist: list[str] = Field(default_factory=list)


@dataclass
class ResolvedRole:
  name: str
  model_id: str
  provider: str  # openai | anthropic
  method: str    # temperature | reasoning_effort | thinking | adaptive_thinking | effort
  effort: str
  max_input: int
  max_output: int
  params: dict = field(default_factory=dict)  # provider call params translated from effort
  beta: Optional[str] = None


@dataclass
class AppConfig:
  lana: LanaConfig
  roles: dict[str, ResolvedRole]
  pricing: dict           # provider -> model_id -> rate dict
  keys: dict[str, str]    # provider -> api key (only for providers required at load)
  workspace: Path
  config_dir: Path
  key_sources: dict[str, str] = field(default_factory=dict)  # provider -> source label ("env" or ".api-keys.txt")
  agent_folder: Path = Path(".lana")  # resolved absolute agent folder path (prompt system)
  data_dir: Path = Path(".lana-data")  # resolved absolute runtime data directory (sessions, logs, chunks)
  scripted: bool = False              # LANA_SCRIPTED_ADAPTER active (FR-14)
  debug_dir: Optional[Path] = None    # --debug: redacted API traffic target (NFR-04)
  show_thinking: bool = False         # --show-thinking: stream thinking dim-styled (FR-16 UX-02)
  created_files: list = field(default_factory=list)  # zero-setup artifacts created at startup (FR-16, reported by the CLI)

# ----------------------------------------- END: Schema -----------------------------------------------------------------------


# ----------------------------------------- START: Loading --------------------------------------------------------------------

def read_json(path: Path) -> dict:
  try:
    return json.loads(path.read_text(encoding="utf-8"))
  except FileNotFoundError:
    raise ConfigError(f"Config file not found: '{path}'.\n  HINT: create it or pass --config <path> (env LANA_CONFIG).") from None
  except json.JSONDecodeError as error:
    raise ConfigError(f"Malformed JSON in '{path}' at line {error.lineno}, column {error.colno}: {error.msg}.\n  HINT: repair the JSON syntax at that position.") from None


# Zero-setup (FR-16, DD-23): write the default config to a missing DEFAULT path; explicit overrides never auto-create
def create_default_config(config_path: Path) -> None:
  content = LanaConfig(roles={name: RoleSpec(**spec) for name, spec in DEFAULT_ROLES.items()}).model_dump()
  try:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
  except OSError as error:
    raise ConfigError(f"Cannot create default config '{config_path}': {error}.\n  HINT: check folder permissions or pass --config <path> to a writable location.") from None


def bundled_root():  # Traversable for lana.bundled package data, None when bundle absent (source checkout without sync)
  try:
    root = importlib.resources.files("lana.bundled")
  except ModuleNotFoundError:
    return None
  return root


# LANADIST-FR-08: write bundled model JSONs and the key template for every MISSING file; existing files stay untouched (EC-15)
def materialize_bundled_config(config_dir: Path, created: list) -> None:
  root = bundled_root()
  try:
    for name in BUNDLED_CONFIG_FILES:
      target = config_dir / name
      if target.exists(): continue
      source = (root / "config" / name) if root is not None else None
      if source is None or not source.is_file(): continue  # bundle not synced - startup fails later with the existing read_json hint
      config_dir.mkdir(parents=True, exist_ok=True)
      target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
      created.append(str(target))
    key_file = config_dir / ".api-keys.txt"
    if not key_file.exists():
      config_dir.mkdir(parents=True, exist_ok=True)
      key_file.write_text(KEY_FILE_TEMPLATE, encoding="utf-8")
      created.append(str(key_file))
  except OSError as error:
    raise ConfigError(f"Cannot materialize default config files in '{config_dir}': {error}.\n  HINT: check folder permissions.") from None


# LANADIST-FR-08: copy the bundled prompt library to a MISSING agent folder; returns False when no bundle is available
def materialize_bundled_agent(target: Path) -> bool:
  root = bundled_root()
  if root is None: return False
  agent = root / "agent"
  if not agent.is_dir(): return False
  with importlib.resources.as_file(agent) as source:
    shutil.copytree(source, target)
  return True


def parse_key_file(path: Path) -> dict[str, str]:
  entries: dict[str, str] = {}
  if not path.exists(): return entries
  for line in path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    key, _, value = line.partition("=")
    entries[key.strip()] = value.strip()
  return entries


# Resolve API key for a provider: environment variable first, then key file (FR-01)
def resolve_key(provider: str, key_file_entries: dict[str, str], key_file_rel: str) -> tuple[Optional[str], str]:
  env_name = ENV_KEY_NAMES[provider]
  env_val = os.environ.get(env_name)
  if env_val: return env_val, f"Environment variable: {env_name}"
  file_val = key_file_entries.get(env_name)
  if file_val: return file_val, f"{key_file_rel}: {env_name}"
  return None, ""


# Translate effort level to provider call params per registry method (FR-01, TC-04)
def translate_effort(method: str, effort: str, prefix_entry: dict, mapping: dict) -> dict:
  factors = mapping.get("effort_mapping", {}).get(effort)
  if factors is None:
    valid = ", ".join(mapping.get("effort_levels", []))
    raise ConfigError(f"Unknown effort level '{effort}' in 'lana-config.json'.\n  HINT: use one of: {valid}.")
  if method == "temperature": return {"temperature": round(factors["temperature_factor"] * prefix_entry.get("temp_max", 1.0), 2)}
  if method == "reasoning_effort":
    value = factors["openai_reasoning_effort"]
    allowed = prefix_entry.get("effort", [])
    if allowed and value not in allowed: value = prefix_entry.get("default", allowed[-1])
    return {"reasoning_effort": value}
  if method == "thinking": return {"thinking_budget": int(factors["anthropic_thinking_factor"] * prefix_entry.get("thinking_max", 0))}
  if method in ("adaptive_thinking", "effort"): return {"effort": factors["anthropic_adaptive_effort"]}
  raise ConfigError(f"Unknown parameter method '{method}' in 'model-registry.json'.\n  HINT: expected temperature, reasoning_effort, thinking, adaptive_thinking, or effort.")


def resolve_role(role_name: str, spec: RoleSpec, registry: dict, mapping: dict) -> ResolvedRole:
  entry = None
  for model in registry.get("models", []):
    if model["model_id"] == spec.model_id: entry = model; break
  if entry is None:
    raise ConfigError(f"Role '{role_name}' model '{spec.model_id}' not found in 'config/model-registry.json'.\n  HINT: choose a registered model or add it to the registry.")
  if not entry.get("enabled", False):
    raise ConfigError(f"Role '{role_name}' model '{spec.model_id}' is disabled in 'config/model-registry.json' (enabled=false).\n  HINT: choose an enabled model or set \"enabled\": true in the registry.")
  prefix_entry = None
  for candidate in registry.get("model_id_startswith", []):
    if spec.model_id.startswith(candidate["prefix"]): prefix_entry = candidate; break
  if prefix_entry is None:
    raise ConfigError(f"Role '{role_name}' model '{spec.model_id}' matches no 'model_id_startswith' prefix in 'config/model-registry.json'.\n  HINT: add a prefix entry for this model family.")
  params = translate_effort(prefix_entry["method"], spec.effort, prefix_entry, mapping)
  max_input = prefix_entry.get("max_input") or entry.get("context_window") or 128000
  return ResolvedRole(name=role_name, model_id=spec.model_id, provider=entry["provider"], method=prefix_entry["method"], effort=spec.effort,
                      max_input=max_input, max_output=prefix_entry.get("max_output") or 8192, params=params, beta=prefix_entry.get("beta"))


def load_lana_config(workspace: Path, config_path: Optional[Path] = None, require_keys: bool = True, app_dir: Optional[Path] = None) -> AppConfig:
  """
  Load and validate the full runtime configuration (fails at startup, never at first API call).

  └── app_dir: base for config, agent_folder, data_dir (DD-25); defaults to workspace
  └── config_path default: <app_dir>/config/lana-config.json (override via --config / LANA_CONFIG)
  └── registry/mapping/pricing/.api-keys.txt are read from the config file's folder
  └── require_keys=False skips API key resolution (scripted adapter mode, FR-14)
  """
  if app_dir is None: app_dir = workspace  # dev mode: CWD is both workspace and app dir
  created_files: list[str] = []
  if config_path is None:
    config_path = app_dir / "config" / "lana-config.json"
    if not Path(config_path).exists():  # FR-16 zero-setup: only the DEFAULT path auto-creates
      create_default_config(Path(config_path))
      created_files.append(str(config_path))
    materialize_bundled_config(Path(config_path).parent, created_files)  # LANADIST-FR-08: fill missing model JSONs + key template
  config_path = Path(config_path)
  config_dir = config_path.parent
  raw = read_json(config_path)
  try:
    lana = LanaConfig.model_validate(raw)
  except ValidationError as error:
    first = error.errors()[0]
    location = ".".join(str(part) for part in first["loc"])
    raise ConfigError(f"Invalid value in '{config_path}' at '{location}': {first['msg']}.\n  HINT: correct that key.") from None
  registry = read_json(config_dir / "model-registry.json")
  mapping = read_json(config_dir / "model-parameter-mapping.json")
  pricing = read_json(config_dir / "model-pricing.json").get("pricing", {})
  roles = {}
  for role_name, spec in lana.roles.items(): roles[role_name] = resolve_role(role_name, spec, registry, mapping)
  if "generator" not in roles:
    raise ConfigError(f"Missing role 'generator' in '{config_path}'.\n  HINT: add a \"generator\" entry under \"roles\".")
  keys: dict[str, str] = {}
  key_sources: dict[str, str] = {}
  if require_keys:
    key_file = config_dir / ".api-keys.txt"
    key_file_entries = parse_key_file(key_file)
    for provider in sorted({role.provider for role in roles.values()}):
      try:
        key_file_rel = '.' + os.sep + str(key_file.relative_to(workspace))
      except ValueError:  # DD-25: config in app_dir, not workspace
        key_file_rel = str(key_file)
      key, source = resolve_key(provider, key_file_entries, key_file_rel)
      if key is None:
        raise ConfigError(f"No API key for provider '{provider}'.\n  HINT: set env var {ENV_KEY_NAMES[provider]} or add a line '{ENV_KEY_NAMES[provider]}=<key>' to '{key_file}'.")
      keys[provider] = key
      key_sources[provider] = source
  resolved_data_dir = (app_dir / lana.data_dir).resolve()  # DD-25: resolve relative to app_dir
  agent_path = Path(lana.agent_folder)
  resolved_agent_folder = agent_path if agent_path.is_absolute() else (app_dir / agent_path).resolve()  # DD-25
  return AppConfig(lana=lana, roles=roles, pricing=pricing, keys=keys, key_sources=key_sources, workspace=Path(workspace), config_dir=config_dir, agent_folder=resolved_agent_folder, data_dir=resolved_data_dir,
                   created_files=created_files)

# ----------------------------------------- END: Loading ----------------------------------------------------------------------
