"""CLI entry point: arg parsing, startup sequence, REPL, headless mode, exit codes (IS-15, IS-21, FR-14).

Exit codes: 0 = turn completed | 2 = configuration error | 3 = provider/API failure | 4 = stopped without completion.
"""
import argparse, asyncio, contextlib, os, platform, sys, time
from pathlib import Path
from prompt_toolkit import PromptSession
from lana.agent import Agent, UnknownWorkflowError
from lana.compaction import make_compactor
from lana.config import ConfigError, load_lana_config
from lana.cost import CostTracker
from lana.loader import BUILTIN_COMMANDS, load_prompt_systems
from lana.prompt import build_system_prompt
from lana.providers import scripted_script_path
from lana.render import Renderer, prompt_approval, prompt_continue, prompt_question
from lana.session import SessionStore, resume as resume_session
from lana.tools import ToolContext, ToolRegistry
from lana.tools.edit_tools import execute_edit, execute_multi_edit, execute_write_to_file
from lana.tools.file_tools import execute_find_by_name, execute_grep_search, execute_list_dir, execute_read_file
from lana.tools.interact_tools import execute_ask_user_question
from lana.tools.shell_tools import execute_command_status, execute_run_command
from lana.tools.skill_tool import execute_skill
from lana.tools.state_tools import execute_todo_list
from lana.tools.trajectory_tools import execute_trajectory_search
from lana.tools.web_tools import execute_read_url_content, execute_search_web, execute_view_content_chunk

EXIT_OK, EXIT_CONFIG, EXIT_PROVIDER, EXIT_STOPPED = 0, 2, 3, 4

EXECUTORS = {
  "read_file": execute_read_file, "list_dir": execute_list_dir, "grep_search": execute_grep_search, "find_by_name": execute_find_by_name,
  "edit": execute_edit, "multi_edit": execute_multi_edit, "write_to_file": execute_write_to_file,
  "run_command": execute_run_command, "command_status": execute_command_status,
  "todo_list": execute_todo_list, "skill": execute_skill, "ask_user_question": execute_ask_user_question,
  "search_web": execute_search_web, "read_url_content": execute_read_url_content, "view_content_chunk": execute_view_content_chunk,
  "trajectory_search": execute_trajectory_search,
}


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(prog="lana", description="Lana MVP-1 - CLI agent running a prompt system (rules/workflows/skills) on OpenAI/Anthropic backends.")
  parser.add_argument("-p", "--prompt", help="headless mode: run this single prompt and exit (FR-14)")
  parser.add_argument("--output-format", choices=["text", "jsonl"], default="text", help="headless output: final text (default) or AgentEvent JSON Lines")
  parser.add_argument("--resume", metavar="SESSION_FILE", help="resume a session from its JSONL file")
  parser.add_argument("--config", metavar="PATH", help="config file override (env LANA_CONFIG)")
  parser.add_argument("--policy", choices=["manual", "auto", "turbo"], help="execution policy override")
  parser.add_argument("--debug", action="store_true", help="write redacted request/response JSON to .lana/logs/")
  return parser


def find_git_root(start: Path) -> Path | None:
  current = start.resolve()
  for candidate in (current, *current.parents):
    if (candidate / ".git").exists(): return candidate
  return None


def short_model_name(model_id: str) -> str:
  parts = model_id.rsplit("-", 1)
  if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 8: return parts[0]  # strip -YYYYMMDD suffix
  return model_id


# Assemble the whole runtime; returns (app, agent, cost_tracker, prompt_system) or raises ConfigError
def build_runtime(args, workspace: Path, interactive: bool):
  scripted = bool(scripted_script_path())
  config_override = args.config or os.environ.get("LANA_CONFIG") or None
  app = load_lana_config(workspace, Path(config_override) if config_override else None, require_keys=not scripted)
  app.scripted = scripted
  if args.policy: app.lana.execution_policy = args.policy
  if args.debug:
    app.debug_dir = workspace / ".lana" / "logs"
    app.debug_dir.mkdir(parents=True, exist_ok=True)
  roles_banner = " | ".join(f"{name}: {short_model_name(role.model_id)} ({role.effort})" for name, role in app.roles.items())
  scripted_marker = " | SCRIPTED" if scripted else ""
  print(f"Lana MVP-1 | {roles_banner}{scripted_marker}")
  started = time.perf_counter()
  if app.lana.prompt_system_paths:
    for path in app.lana.prompt_system_paths: print(f"Loading prompt system '{path}'...")
  prompt_system = load_prompt_systems(app.lana.prompt_system_paths, app.lana.rule_block_max_chars)
  injected = sum(1 for rule in prompt_system.rules if rule.skipped_reason is None)
  skipped_empty = sum(1 for rule in prompt_system.rules if rule.skipped_reason == "empty")
  skip_note = f", {skipped_empty} skipped: empty" if skipped_empty else ""
  print(f"  {len(prompt_system.rules)} rules ({injected} injected{skip_note}), {len(prompt_system.workflows)} workflows, {len(prompt_system.skills)} skills.")
  print(f"  OK. Loaded in {time.perf_counter() - started:.1f} secs.")
  for warning in prompt_system.warnings: print(f"  WARNING: {warning}")
  print(f"Policy: {app.lana.execution_policy}")
  if app.lana.execution_policy in ("auto", "turbo"):
    print(f"  NOTICE: policy '{app.lana.execution_policy}' auto-executes commands - prompt-injection risk; recommended only for trusted workspaces (NFR-05).")
  git_root = find_git_root(workspace)
  workspace_info = {"os": platform.system().lower(), "workspace": str(workspace), "git_root": str(git_root) if git_root else ""}
  system_prompt = build_system_prompt(prompt_system, workspace_info)
  registry = ToolRegistry(os_name=workspace_info["os"], shell="pwsh", skills=prompt_system.skills)
  for name, executor in EXECUTORS.items(): registry.register(name, executor)
  tool_context = ToolContext(workspace=workspace, tool_result_max_chars=app.lana.tool_result_max_chars, prompt_system=prompt_system, app_config=app)
  messages = []
  cost_tracker = CostTracker(app)
  if args.resume:
    resume_path = Path(args.resume)
    if not resume_path.is_file():  # IG-05: startup inputs fail with self-contained errors, never tracebacks (BG-0005)
      raise ConfigError(f"Session file not found: '{resume_path}'.\n  Fix: pass an existing session JSONL from '<workspace>/.lana/sessions/' to --resume.")
    resumed = resume_session(resume_path)
    messages = resumed.messages
    tool_context.todo_state = resumed.todo_state
    cost_tracker.seed(resumed)  # IG-06: /cost totals survive resume (BG-0002)
    if resumed.skipped_lines: print(f"  WARNING: {resumed.skipped_lines} corrupt line" + ("s" if resumed.skipped_lines != 1 else "") + " skipped during resume.")
    print(f"Resumed session '{args.resume}': {len(messages)} messages.")
    session = SessionStore(Path(args.resume))
  else:
    session = SessionStore.create(workspace)
  if interactive:
    tool_context.ask_user = prompt_question
    approve_callback, continue_callback = prompt_approval, prompt_continue
  else:
    approve_callback, continue_callback = None, None  # non-interactive auto-deny (FR-14)
  agent = Agent(app, prompt_system, system_prompt, registry, tool_context, session, messages=messages,
                approve_callback=approve_callback, continue_callback=continue_callback, cost_fn=cost_tracker.record, compactor=make_compactor(app))
  return app, agent, cost_tracker, prompt_system


# Consume one prompt's event stream; returns exit-code-relevant stop reason.
# jsonl mode contract: stdout carries ONLY serialized AgentEvents - diagnostics go to stderr (strict consumers like jq must never see banner text)
def run_one_prompt(agent: Agent, renderer: Renderer | None, text: str, jsonl_output: bool) -> str | None:
  async def consume():
    async for event in agent.run_prompt(text):
      if jsonl_output: print(event.to_jsonl(), flush=True)
      elif renderer: renderer.handle(event)
  try:
    asyncio.run(consume())
  except KeyboardInterrupt:
    note = agent.note_cancellation()
    print(f"\n{note} (results kept in conversation).", file=sys.stderr if jsonl_output else sys.stdout)
  return agent.stop_reason


def stop_reason_to_exit_code(stop_reason: str | None) -> int:
  if stop_reason == "provider_error": return EXIT_PROVIDER
  if stop_reason in ("limit", "cancelled"): return EXIT_STOPPED
  return EXIT_OK


def run_headless(agent: Agent, cost_tracker: CostTracker, prompt: str, output_format: str) -> int:
  jsonl_output = output_format == "jsonl"
  command = prompt.strip().split()[0].lstrip("/") if prompt.strip().startswith("/") else ""
  if command in BUILTIN_COMMANDS:  # built-ins never reach the Generator (FR-05), headless included
    if command == "help": print_help(agent.prompt_system)
    elif command == "cost": print(cost_tracker.summary())
    return EXIT_OK
  renderer = None if jsonl_output else Renderer(cost_tracker=cost_tracker, policy=agent.app.lana.execution_policy)
  try:
    stop_reason = run_one_prompt(agent, renderer, prompt, jsonl_output)
  except UnknownWorkflowError as error:
    print(str(error), file=sys.stderr if jsonl_output else sys.stdout)
    return EXIT_OK
  if not jsonl_output and agent.final_text and renderer is None: print(agent.final_text)
  return stop_reason_to_exit_code(stop_reason)


def print_help(prompt_system) -> None:
  print("Built-ins: /help (this list), /cost (session usage), /exit (quit)")
  print("Workflows:")
  for workflow in prompt_system.workflows: print(f"  /{workflow.name}: {workflow.description}")


def repl(agent: Agent, cost_tracker: CostTracker, prompt_system) -> int:
  renderer = Renderer(cost_tracker=cost_tracker, policy=agent.app.lana.execution_policy)
  prompt_session = PromptSession() if sys.stdin.isatty() else None  # terminal-dependent input only on a real terminal (FR-14)
  while True:
    try:
      text = prompt_session.prompt("> ") if prompt_session else input("> ")
    except (EOFError, KeyboardInterrupt):
      break
    text = text.strip()
    if not text: continue
    command = text.split()[0].lstrip("/") if text.startswith("/") else ""
    if command == "exit": break
    if command == "help": print_help(prompt_system); continue
    if command == "cost": print(cost_tracker.summary()); continue
    try:
      run_one_prompt(agent, renderer, text, jsonl_output=False)
    except UnknownWorkflowError as error:
      print(str(error))
  return EXIT_OK


def main() -> int:
  args = build_arg_parser().parse_args()
  workspace = Path.cwd()
  interactive = args.prompt is None and sys.stdin.isatty()
  jsonl_headless = args.prompt is not None and args.output_format == "jsonl"
  try:
    if jsonl_headless:  # startup banner/warnings to stderr - stdout stays pure JSONL for machine consumers
      with contextlib.redirect_stdout(sys.stderr):
        app, agent, cost_tracker, prompt_system = build_runtime(args, workspace, interactive)
    else:
      app, agent, cost_tracker, prompt_system = build_runtime(args, workspace, interactive)
  except ConfigError as error:
    print(f"ERROR: {error}", file=sys.stderr)
    return EXIT_CONFIG
  if args.prompt is not None: return run_headless(agent, cost_tracker, args.prompt, args.output_format)
  return repl(agent, cost_tracker, prompt_system)


if __name__ == "__main__": sys.exit(main())
