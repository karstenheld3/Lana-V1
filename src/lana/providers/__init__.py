"""Adapter selection by registry provider field + LANA_SCRIPTED_ADAPTER env hook (IS-11, IS-22, DD-03)."""
import os
from lana.config import AppConfig, ResolvedRole
from lana.providers.base import ProviderError
from lana.providers.scripted_adapter import ScriptedAdapter

SCRIPTED_ENV_VAR = "LANA_SCRIPTED_ADAPTER"


def scripted_script_path() -> str | None:
  return os.environ.get(SCRIPTED_ENV_VAR) or None


_ADAPTER_CACHE: dict = {}


# One adapter per provider per process (shared client); scripted mode returns one shared replay adapter for every role
def get_adapter(role: ResolvedRole, app: AppConfig):
  script = scripted_script_path()
  if script:
    if "scripted" not in _ADAPTER_CACHE: _ADAPTER_CACHE["scripted"] = ScriptedAdapter(script)
    return _ADAPTER_CACHE["scripted"]
  if role.provider in _ADAPTER_CACHE: return _ADAPTER_CACHE[role.provider]
  if role.provider == "openai":
    from lana.providers.openai_adapter import OpenAIAdapter  # deferred: SDK client construction only when a live role needs it
    _ADAPTER_CACHE["openai"] = OpenAIAdapter(api_key=app.keys["openai"], debug_dir=getattr(app, "debug_dir", None))
  elif role.provider == "anthropic":
    from lana.providers.anthropic_adapter import AnthropicAdapter  # deferred: SDK client construction only when a live role needs it
    _ADAPTER_CACHE["anthropic"] = AnthropicAdapter(api_key=app.keys["anthropic"], debug_dir=getattr(app, "debug_dir", None))
  else:
    raise ProviderError(f"Unknown provider '{role.provider}' for model '{role.model_id}' - expected openai or anthropic")
  return _ADAPTER_CACHE[role.provider]


def reset_adapter_cache() -> None:
  _ADAPTER_CACHE.clear()
