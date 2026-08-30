"""Tool registry: name -> (definition, executor, needs_approval); dispatch with schema validation (IS-06)."""
import inspect, platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional
from lana.tools.definitions import SCHEMAS, render_definitions


# Session-scoped context passed to every executor
@dataclass
class ToolContext:
  workspace: Path
  data_dir: Optional[Path] = None     # resolved runtime data directory; falls back to workspace/.lana-data
  tool_result_max_chars: int = 50000
  read_ledger: dict[str, float] = field(default_factory=dict)         # path -> mtime at last read/edit by Lana (FR-11)
  background_processes: dict[str, Any] = field(default_factory=dict)  # command id -> BackgroundProcess (IS-09)
  foreground_process: Any = None                                      # live foreground BackgroundProcess during a blocking run_command (FR-16 BL-02)
  chunk_store: dict[str, list[str]] = field(default_factory=dict)     # document_id -> chunks (FR-13)
  todo_state: Optional[list[dict]] = None                             # last todo_list items (IG-04)
  prompt_system: Any = None                                           # PromptSystem for the skill tool
  app_config: Any = None                                              # AppConfig for web tools (websearch role)
  ask_user: Optional[Callable[[dict], str]] = None                    # frontend answer callback; None -> non-interactive fallback (FR-14)


class ToolError(Exception):
  pass


JSON_TYPE_CHECKS = {"string": str, "integer": int, "boolean": bool, "number": (int, float), "array": list, "object": dict}


# Minimal JSON Schema validation: required, unknown keys, type, enum, array items (EC-23; no external dependency per DD-17)
def validate_args(args: dict, schema: dict, path: str = "") -> None:
  properties = schema.get("properties", {})
  for required_name in schema.get("required", []):
    if required_name not in args: raise ToolError(f"missing required parameter '{path}{required_name}'")
  for key, value in args.items():
    if key not in properties: raise ToolError(f"unknown parameter '{path}{key}'")
    spec = properties[key]
    expected = JSON_TYPE_CHECKS.get(spec.get("type", ""))
    if expected is not None and not isinstance(value, expected): raise ToolError(f"parameter '{path}{key}' must be {spec['type']}, got {type(value).__name__}")
    if expected is int and isinstance(value, bool): raise ToolError(f"parameter '{path}{key}' must be integer, got bool")
    if "enum" in spec and value not in spec["enum"]: raise ToolError(f"parameter '{path}{key}' must be one of {spec['enum']}, got '{value}'")
    if spec.get("type") == "array" and isinstance(spec.get("items"), dict):
      item_spec = spec["items"]
      for index, item in enumerate(value):
        if item_spec.get("type") == "object" and isinstance(item, dict): validate_args(item, item_spec, path=f"{path}{key}[{index}].")
        else:
          item_expected = JSON_TYPE_CHECKS.get(item_spec.get("type", ""))
          if item_expected is not None and not isinstance(item, item_expected): raise ToolError(f"parameter '{path}{key}[{index}]' must be {item_spec['type']}")
  if schema.get("minItems") and isinstance(args, list) and len(args) < schema["minItems"]: raise ToolError(f"'{path}' requires at least {schema['minItems']} items")


# Cap tool result at limit, tail-truncated with marker (EC-04, FR-04)
def cap_result(text: str, max_chars: int) -> str:
  if len(text) <= max_chars: return text
  removed = len(text) - max_chars
  return text[:max_chars] + f"\n<truncated {removed} chars>"


@dataclass
class RegisteredTool:
  name: str
  definition: dict
  executor: Callable[[dict, ToolContext], str]


class ToolRegistry:
  def __init__(self, os_name: str = "", shell: str = "pwsh", skills: Optional[list] = None):
    self.os_name = os_name or platform.system().lower()
    self.shell = shell
    self.tools: dict[str, RegisteredTool] = {}
    self.definitions = {item["name"]: item for item in render_definitions(self.os_name, self.shell, skills or [])}

  def register(self, name: str, executor: Callable[[dict, ToolContext], str]):
    if name not in self.definitions: raise ValueError(f"Unknown tool name '{name}' - not in the 16 registered definitions")
    self.tools[name] = RegisteredTool(name=name, definition=self.definitions[name], executor=executor)

  def definition_list(self) -> list[dict]:
    return [self.tools[name].definition for name in self.tools]

  # Dispatch by name with schema validation; raises ToolError for unknown tool (EC-22) or invalid args (EC-23)
  def dispatch(self, name: str, args: dict, context: ToolContext) -> str:
    tool = self.tools.get(name)
    if tool is None: raise ToolError(f"Unknown tool '{name}'. Available tools: {', '.join(self.tools)}")
    try:
      validate_args(args, SCHEMAS[name])
    except ToolError as error:
      raise ToolError(f"Invalid arguments for '{name}': {error}") from None
    result = tool.executor(args, context)
    if inspect.isawaitable(result):  # async frontend callback (ACP elicitation, LANAACPB-IP01 IS-08) - cap after resolution
      async def resolve():
        return cap_result(await result, context.tool_result_max_chars)
      return resolve()
    return cap_result(result, context.tool_result_max_chars)
