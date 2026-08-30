"""CLI entry point: arg parsing, startup sequence, REPL, headless mode, exit codes (IS-15, IS-21, FR-14).

Exit codes: 0 = turn completed | 2 = configuration error | 3 = provider/API failure | 4 = stopped without completion.
"""
import argparse, asyncio, contextlib, hashlib, importlib.metadata, os, platform, sys, time
from pathlib import Path
from prompt_toolkit import PromptSession
from lana.agent import Agent, UnknownWorkflowError
from lana.compaction import make_compactor
from lana.config import ConfigError, load_lana_config, materialize_bundled_agent
from lana.cost import CostTracker
from lana.events import PromptStep, SessionStarted
from lana.prompt_queue import PromptQueueError, parse_queue
from lana.loader import BUILTIN_COMMANDS, compute_fingerprint, load_prompt_systems
from lana.prompt import build_system_prompt
from lana.providers import scripted_script_path
from lana.render import Renderer, prompt_approval, prompt_continue, prompt_question
from lana.session import SessionStore, resume as resume_session
from lana.tools import ToolContext, ToolRegistry
from lana.tools.edit_tools import execute_edit, execute_multi_edit, execute_write_to_file
from lana.tools.file_tools import execute_find_by_name, execute_grep_search, execute_list_dir, execute_read_file
from lana.tools.interact_tools import execute_ask_user_question
from lana.tools.shell_tools import execute_command_status, execute_run_command, terminate_tool_processes
from lana.tools.skill_tool import execute_skill
from lana.tools.state_tools import execute_todo_list
from lana.tools.trajectory_tools import execute_trajectory_search
from lana.tools.web_tools import execute_read_url_content, execute_search_web, execute_view_content_chunk

EXIT_OK, EXIT_CONFIG, EXIT_PROVIDER, EXIT_STOPPED = 0, 2, 3, 4


def package_version() -> str:
  try:
    return importlib.metadata.version("lana")
  except importlib.metadata.PackageNotFoundError:  # running from source without install
    return "0.0.0-dev"

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
  parser.add_argument("--prompt-file", metavar="PATH", help="headless prompt queue: fenced prompts executed sequentially in one session (LANAACPB-FR-12; format: docs/PROMPT_FILE_FORMAT.md)")
  parser.add_argument("--output-format", choices=["text", "jsonl"], default="text", help="headless output: final text (default) or AgentEvent JSON Lines")
  parser.add_argument("--resume", metavar="SESSION_FILE", help="resume a session from its JSONL file")
  parser.add_argument("--config", metavar="PATH", help="config file override (env LANA_CONFIG)")
  parser.add_argument("--policy", choices=["manual", "auto", "turbo"], help="execution policy override")
  parser.add_argument("--debug", action="store_true", help="write redacted request/response JSON to .lana-data/logs/")
  parser.add_argument("--show-thinking", action="store_true", help="stream model thinking dim-styled (FR-16)")
  parser.add_argument("--acp", action="store_true", help="ACP agent mode: JSON-RPC 2.0 over stdio (MVP-2, LANAACPB-SP01)")
  parser.add_argument("--version", action="version", version=f"%(prog)s {package_version()}")  # exits before config load - no zero-setup side effects (LANADIST-IP01-IS-01)
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
  app.show_thinking = getattr(args, "show_thinking", False)
  if args.policy: app.lana.execution_policy = args.policy
  created = list(app.created_files)  # FR-16 zero-setup: create what is missing, report every artifact
  sessions_dir = app.data_dir / "sessions"
  if not sessions_dir.is_dir():
    sessions_dir.mkdir(parents=True, exist_ok=True)
    created.append(str(sessions_dir))
  if not app.agent_folder.is_dir():  # LANADIST-FR-08: materialize bundled default prompt library; existing folder (even empty) stays untouched
    copied = materialize_bundled_agent(app.agent_folder)
    if not copied:  # bundle unavailable (source checkout without sync) - keep the empty scaffold behavior
      for sub in ("rules", "workflows", "skills"): (app.agent_folder / sub).mkdir(parents=True, exist_ok=True)
    created.append(str(app.agent_folder))
  for path in created: print(f"Created '{path}' (zero-setup).")
  if args.debug:
    app.debug_dir = app.data_dir / "logs"
    app.debug_dir.mkdir(parents=True, exist_ok=True)
  roles_banner = " | ".join(f"{name}: {short_model_name(role.model_id)} ({role.effort})" for name, role in app.roles.items())
  scripted_marker = " | SCRIPTED" if scripted else ""
  print(f"Lana MVP-1 | {roles_banner}{scripted_marker}")
  started = time.perf_counter()
  print(f"Loading prompt system '{app.agent_folder}'...")
  prompt_system = load_prompt_systems([app.agent_folder], app.lana.rule_block_max_chars)
  injected = sum(1 for rule in prompt_system.rules if rule.skipped_reason is None)
  skipped_empty = sum(1 for rule in prompt_system.rules if rule.skipped_reason == "empty")
  skip_note = f", {skipped_empty} skipped: empty" if skipped_empty else ""
  print(f"  {len(prompt_system.rules)} rules ({injected} injected{skip_note}), {len(prompt_system.workflows)} workflows, {len(prompt_system.skills)} skills.")
  print(f"  OK. Loaded in {time.perf_counter() - started:.1f} secs.")
  if not (prompt_system.rules or prompt_system.workflows or prompt_system.skills):
    print(f"  NOTICE: prompt system is empty - Lana runs without rules, workflows, or skills. Add content to '{app.agent_folder}'.")
  for warning in prompt_system.warnings: print(f"  WARNING: {warning}")
  print(f"Policy: {app.lana.execution_policy}")
  if app.lana.execution_policy in ("auto", "turbo"):
    print(f"  WARNING: policy '{app.lana.execution_policy}' auto-executes commands - prompt-injection risk.")
    print("  HINT: use this policy only in trusted workspaces; switch back with --policy manual.")
  git_root = find_git_root(workspace)
  workspace_info = {"os": platform.system().lower(), "workspace": str(workspace), "git_root": str(git_root) if git_root else ""}
  system_prompt = build_system_prompt(prompt_system, workspace_info)
  registry = ToolRegistry(os_name=workspace_info["os"], shell="pwsh", skills=prompt_system.skills)
  for name, executor in EXECUTORS.items(): registry.register(name, executor)
  tool_context = ToolContext(workspace=workspace, data_dir=app.data_dir, tool_result_max_chars=app.lana.tool_result_max_chars, prompt_system=prompt_system, app_config=app)
  messages = []
  cost_tracker = CostTracker(app)
  fingerprint = compute_fingerprint(prompt_system, [app.agent_folder])
  config_snapshot = {"roles": {name: {"model_id": role.model_id, "effort": role.effort, "provider": role.provider} for name, role in app.roles.items()},
                     "execution_policy": app.lana.execution_policy, "max_tool_calls_per_prompt": app.lana.max_tool_calls_per_prompt,
                     "tool_result_max_chars": app.lana.tool_result_max_chars, "compaction_threshold_fraction": app.lana.compaction_threshold_fraction,
                     "compaction_threshold_max_tokens": app.lana.compaction_threshold_max_tokens}
  tool_definitions = None
  if args.resume:
    resume_path = Path(args.resume)
    if not resume_path.is_file():  # IG-05: startup inputs fail with self-contained errors, never tracebacks (BG-0005)
      raise ConfigError(f"Session file not found: '{resume_path}'.\n  HINT: pass an existing session JSONL from '<workspace>/{app.lana.data_dir}/sessions/' to --resume.")
    print(f"Resuming '{args.resume}'...")  # FR-16 UX-05: name the file BEFORE the parse
    resumed = resume_session(resume_path)
    messages = resumed.messages
    tool_context.todo_state = resumed.todo_state
    cost_tracker.seed(resumed)  # IG-06: /cost totals survive resume (BG-0002)
    if resumed.skipped_lines: print(f"  WARNING: {resumed.skipped_lines} corrupt line" + ("s" if resumed.skipped_lines != 1 else "") + " skipped during resume.")
    if resumed.system_prompt is not None:  # FR-08 full recall: recorded environment wins for Generator calls
      system_prompt = resumed.system_prompt
      tool_definitions = resumed.tool_definitions or None
      recorded_fp = resumed.prompt_system_fingerprint or {}
      if recorded_fp and recorded_fp.get("content_hash") != fingerprint["content_hash"]:
        recorded_counts, current_counts = recorded_fp.get("counts", {}), fingerprint["counts"]
        print(f"  WARNING: prompt system changed since recording (recorded {recorded_counts.get('rules', '?')}/{recorded_counts.get('workflows', '?')}/{recorded_counts.get('skills', '?')},"
              f" current {current_counts['rules']}/{current_counts['workflows']}/{current_counts['skills']} rules/workflows/skills). Recorded system prompt stays active for this session.")
      recorded_generator = ((resumed.config_snapshot or {}).get("roles", {}).get("generator", {})).get("model_id", "")
      if recorded_generator and recorded_generator != app.roles["generator"].model_id:
        print(f"  WARNING: generator changed (recorded {recorded_generator}, current {app.roles['generator'].model_id}). Full context re-sent - first turn runs without provider cache.")
    else:  # EC-28: legacy session file without session_started
      print("  WARNING: legacy session file - recorded environment unavailable, system prompt assembled from current prompt system.")
    print(f"Resumed session '{args.resume}': {len(messages)} messages.")
    session = SessionStore(Path(args.resume))
  else:
    session = SessionStore.create(app.data_dir)
    session.append(SessionStarted(system_prompt=system_prompt, tool_definitions=registry.definition_list(),
                                  config_snapshot=config_snapshot, prompt_system_fingerprint=fingerprint))  # FR-08: FIRST line
  if interactive:
    tool_context.ask_user = prompt_question
    approve_callback, continue_callback = prompt_approval, prompt_continue
  else:
    approve_callback, continue_callback = None, None  # non-interactive auto-deny (FR-14)
  agent = Agent(app, prompt_system, system_prompt, registry, tool_context, session, messages=messages,
                approve_callback=approve_callback, continue_callback=continue_callback, cost_fn=cost_tracker.record, compactor=make_compactor(app),
                tool_definitions=tool_definitions)
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
    terminated, _ = terminate_tool_processes(agent.tool_context, include_background=False)  # FR-16 BL-02: stop the abandoned foreground child
    stopped = f" Stopped: {', '.join(terminated)}." if terminated else ""
    print(f"\n{note} (results kept in conversation).{stopped}", file=sys.stderr if jsonl_output else sys.stdout)
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
  renderer = None if jsonl_output else Renderer(cost_tracker=cost_tracker, policy=agent.app.lana.execution_policy, show_thinking=agent.app.show_thinking)
  try:
    stop_reason = run_one_prompt(agent, renderer, prompt, jsonl_output)
  except UnknownWorkflowError as error:
    print(str(error), file=sys.stderr if jsonl_output else sys.stdout)
    return EXIT_OK
  except Exception as error:  # FR-16 CR-02/CR-03: self-contained failure, session JSONL survives for --resume
    print(f"ERROR: unexpected failure during this prompt ({type(error).__name__}: {error}). The session file is intact - continue with --resume.", file=sys.stderr)
    report_process_cleanup(agent)
    return EXIT_STOPPED
  if not jsonl_output and agent.final_text and renderer is None: print(agent.final_text)
  report_process_cleanup(agent)
  return stop_reason_to_exit_code(stop_reason)


def print_help(prompt_system) -> None:
  print("Built-ins: /help (this list), /cost (session usage), /exit (quit)")
  print("Workflows:")
  for workflow in prompt_system.workflows: print(f"  /{workflow.name}: {workflow.description}")


# FR-12: run the parsed prompt queue as sequential turns of ONE session; abort on the first failed step
def run_headless_queue(agent: Agent, cost_tracker: CostTracker, prompts: list[str], output_format: str) -> int:
  jsonl_output = output_format == "jsonl"
  total = len(prompts)
  for index, prompt in enumerate(prompts, 1):
    step = PromptStep(index=index, total=total, digest=hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12])
    agent.session.append(step)  # persisted like every event (FR-12)
    if jsonl_output: print(step.to_jsonl(), flush=True)
    else: print(f"[ {index} / {total} ] Prompt step (digest {step.digest})...")
    exit_code = run_headless(agent, cost_tracker, prompt, output_format)
    if exit_code != EXIT_OK:  # EC-26: remaining queue entries abandoned, completed turns stay persisted
      print(f"Queue aborted at step {index} of {total} (exit code {exit_code}). Completed steps are persisted - continue with --resume.", file=sys.stderr)
      return exit_code
  return EXIT_OK


# FR-16 BL-02/BL-06: terminate live tool child processes at exit; name what was stopped and what survived
def report_process_cleanup(agent: Agent) -> None:
  terminated, survivors = terminate_tool_processes(agent.tool_context)
  if terminated: print(f"Stopped {len(terminated)} running command(s): {', '.join(terminated)}.", file=sys.stderr)
  if survivors: print(f"WARNING: still running after terminate: {', '.join(survivors)}.", file=sys.stderr)


def repl(agent: Agent, cost_tracker: CostTracker, prompt_system) -> int:
  renderer = Renderer(cost_tracker=cost_tracker, policy=agent.app.lana.execution_policy, show_thinking=agent.app.show_thinking)
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
    except Exception as error:  # FR-16 CR-02: the REPL survives any turn failure; the session file allows --resume
      print(f"ERROR: unexpected failure during this turn ({type(error).__name__}: {error}). The session stays alive - continue typing, or exit and --resume later.")
  report_process_cleanup(agent)
  return EXIT_OK


def main() -> int:
  args = build_arg_parser().parse_args()
  if args.acp:
    if args.prompt is not None or args.resume or args.prompt_file:  # DD-09: one process serves either the CLI or ACP, never both
      print("ERROR: --acp is mutually exclusive with -p, --resume, and --prompt-file (ACP sessions come from session/new and session/load).", file=sys.stderr)
      return EXIT_CONFIG
    from lana.acp.server import run_acp  # lazy: acp.server imports build_runtime lazily as well
    return asyncio.run(run_acp(args))
  prompts = None
  if args.prompt_file:
    if args.prompt is not None or args.resume:  # FR-12 exclusivity (EC-28): the queue always starts a fresh session
      print("ERROR: --prompt-file is mutually exclusive with -p and --resume (the queue always starts a fresh session).", file=sys.stderr)
      return EXIT_CONFIG
    try:
      queue_text = Path(args.prompt_file).read_text(encoding="utf-8")
    except OSError as error:
      print(f"ERROR: cannot read prompt file '{args.prompt_file}': {error}.\n  HINT: pass an existing PROMPTS*.md file (format: docs/PROMPT_FILE_FORMAT.md).", file=sys.stderr)
      return EXIT_CONFIG
    try:  # EC-25: malformed file fails BEFORE any session is created
      prompts = parse_queue(queue_text)
    except PromptQueueError as error:
      print(f"ERROR: invalid prompt file '{args.prompt_file}': {error}.\n  HINT: format rules in docs/PROMPT_FILE_FORMAT.md.", file=sys.stderr)
      return EXIT_CONFIG
  workspace = Path.cwd()
  headless = args.prompt is not None or prompts is not None
  interactive = not headless and sys.stdin.isatty()
  jsonl_headless = headless and args.output_format == "jsonl"
  try:
    if jsonl_headless:  # startup banner/warnings to stderr - stdout stays pure JSONL for machine consumers
      with contextlib.redirect_stdout(sys.stderr):
        app, agent, cost_tracker, prompt_system = build_runtime(args, workspace, interactive)
    else:
      app, agent, cost_tracker, prompt_system = build_runtime(args, workspace, interactive)
  except ConfigError as error:
    print(f"ERROR: {error}", file=sys.stderr)
    return EXIT_CONFIG
  except OSError as error:  # FR-16 CR-01: filesystem failures at startup are self-contained, never tracebacks
    print(f"ERROR: startup failed on a filesystem operation: {error}.\n  HINT: check that the workspace is writable and no path is locked by another process.", file=sys.stderr)
    return EXIT_CONFIG
  if prompts is not None: return run_headless_queue(agent, cost_tracker, prompts, args.output_format)
  if args.prompt is not None: return run_headless(agent, cost_tracker, args.prompt, args.output_format)
  return repl(agent, cost_tracker, prompt_system)


if __name__ == "__main__": sys.exit(main())
