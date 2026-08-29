"""Command safety: ExecutionPolicy, denylist matcher, alias normalization, wrapper detection (LANAAGNT-FR-12, IS-09).

IG-03: a denylist match NEVER runs without interactive approval, regardless of policy or SafeToAutoRun.
Scope: guards against ACCIDENTAL destructive commands - not an adversarial-input defense (NFR-05).
"""
import shlex
from dataclasses import dataclass
from pathlib import Path

SHELL_WRAPPERS = ("pwsh", "powershell", "cmd", "bash")
WRAPPER_EXECUTION_FLAGS = ("-command", "-c", "/c")


@dataclass
class Decision:
  action: str  # RUN | ASK
  reason: str


# First whitespace-delimited token, path and quotes stripped, casefolded (FR-12 matching rules)
def first_token(command_line: str) -> str:
  stripped = command_line.strip()
  if not stripped: return ""
  try:
    tokens = shlex.split(stripped, posix=False)
  except ValueError:
    tokens = stripped.split()
  token = tokens[0].strip("\"'") if tokens else ""
  token = token.replace("\\", "/").rsplit("/", 1)[-1]  # strip path
  if token.lower().endswith(".exe"): token = token[:-4]
  return token.casefold()


def is_wrapper_invocation(command_line: str) -> bool:
  if first_token(command_line) not in SHELL_WRAPPERS: return False
  lowered = command_line.casefold()
  return any(f" {flag} " in lowered + " " or lowered.rstrip().endswith(flag) or f" {flag}" in lowered for flag in WRAPPER_EXECUTION_FLAGS)


# Denylist match: single-token entries match the first token; multi-token entries prefix-match the command line (case-insensitive)
def matches_denylist(command_line: str, denylist: list[str]) -> bool:
  token = first_token(command_line)
  lowered_line = command_line.strip().casefold()
  for entry in denylist:
    entry_folded = entry.strip().casefold()
    if " " in entry_folded:
      if lowered_line.startswith(entry_folded): return True
    elif token == entry_folded: return True
  return False


def classify(command_line: str, policy: str, denylist: list[str], safe_to_auto_run: bool = False) -> Decision:
  """
  Decide RUN or ASK for a command (FR-12 policy matrix).

  └── 1. wrapper invocation (pwsh/powershell/cmd/bash + -Command/-c//c) -> ASK in auto and turbo (inner commands never parsed)
  └── 2. denylist match -> ASK always (IG-03, un-bypassable)
  └── 3. manual -> ASK | auto -> RUN only with SafeToAutoRun | turbo -> RUN
  """
  if matches_denylist(command_line, denylist): return Decision("ASK", f"denylist match on '{first_token(command_line)}'")
  if policy == "manual": return Decision("ASK", "policy manual: every command requires approval")
  if is_wrapper_invocation(command_line): return Decision("ASK", "shell wrapper invocation: inner command is not parsed")
  if policy == "auto":
    if safe_to_auto_run: return Decision("RUN", "policy auto + SafeToAutoRun")
    return Decision("ASK", "policy auto: model did not mark the command SafeToAutoRun")
  if policy == "turbo": return Decision("RUN", "policy turbo")
  return Decision("ASK", f"unknown policy '{policy}' - defaulting to approval")


# write_to_file/edit outside the workspace root requires approval regardless of policy (FR-12, TC-31)
def write_needs_approval(target_path: str | Path, workspace: Path) -> bool:
  try:
    Path(target_path).resolve().relative_to(Path(workspace).resolve())
    return False
  except ValueError:
    return True
