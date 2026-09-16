"""TK-012: safety classifier (IP01 TC-26..31, IG-03)."""
from pathlib import Path
from lana.safety import classify, first_token, is_wrapper_invocation, matches_denylist, write_needs_approval

DENYLIST = ["rm", "del", "rmdir", "erase", "ri", "Remove-Item", "Move-Item", "format", "kill", "pkill", "Stop-Process", "shutdown", "git push --force"]


# TC-26: first-token denylist match -> ASK in auto even with SafeToAutoRun (IG-03)
def test_tc26_first_token_match_auto():
  assert classify("Remove-Item x", "auto", DENYLIST, safe_to_auto_run=True).action == "ASK"
  assert classify("remove-item x", "turbo", DENYLIST).action == "ASK"  # case-insensitive
  assert classify("C:\\tools\\rm.exe -rf y", "turbo", DENYLIST).action == "ASK"  # path + extension stripped


# TC-27: wrapper invocation -> ASK in auto and turbo (IG-03)
def test_tc27_wrapper_ask():
  wrapped = 'pwsh -Command "Remove-Item x"'
  assert classify(wrapped, "auto", DENYLIST, safe_to_auto_run=True).action == "ASK"
  assert classify(wrapped, "turbo", DENYLIST).action == "ASK"
  assert classify('cmd /c "del x"', "turbo", DENYLIST).action == "ASK"
  assert classify("bash -c 'rm -rf /'", "turbo", DENYLIST).action == "ASK"
  innocent_wrapped = 'pwsh -Command "echo hi"'
  assert classify(innocent_wrapped, "turbo", DENYLIST).action == "ASK"  # inner commands never parsed


# TC-28: multi-token entry prefix-matches the command line
def test_tc28_multi_token_prefix():
  assert classify("git push --force-with-lease", "turbo", DENYLIST).action == "ASK"
  assert classify("git push --force origin main", "auto", DENYLIST, safe_to_auto_run=True).action == "ASK"
  assert classify("git push origin main", "turbo", DENYLIST).action == "RUN"  # plain push not matched


# TC-29: safe command in auto with SafeToAutoRun -> RUN
def test_tc29_auto_safe_runs():
  assert classify("echo hi", "auto", DENYLIST, safe_to_auto_run=True).action == "RUN"
  assert classify("echo hi", "auto", DENYLIST, safe_to_auto_run=False).action == "ASK"


# TC-30: manual policy -> ASK for everything
def test_tc30_manual_always_asks():
  for command in ("echo hi", "git status", "Remove-Item x", "pwsh -Command 'echo y'"):
    assert classify(command, "manual", DENYLIST, safe_to_auto_run=True).action == "ASK"


def test_turbo_runs_unmatched():
  assert classify("python script.py", "turbo", DENYLIST).action == "RUN"


def test_first_token_normalization():
  assert first_token('"C:\\Program Files\\Git\\git.exe" status') == "git"
  assert first_token("  Remove-Item  x ") == "remove-item"
  assert first_token("") == ""


def test_wrapper_detection_negative():
  assert not is_wrapper_invocation("pwsh --version")  # no execution flag
  assert not is_wrapper_invocation("echo pwsh -Command x")  # wrapper not first token


# TC-44: wrapper detection edge cases (EC-33, FR-12)
def test_tc44_wrapper_detection_edge_cases():
  # Case variants
  assert is_wrapper_invocation('pwsh -Command "echo hi"')
  assert is_wrapper_invocation('pwsh -command "echo hi"')
  assert is_wrapper_invocation('pwsh -COMMAND "echo hi"')
  assert is_wrapper_invocation('powershell -Command "echo hi"')
  # No space after flag: flag immediately before quote
  assert is_wrapper_invocation('pwsh -c"echo hi"')
  assert is_wrapper_invocation("pwsh -c'echo hi'")
  assert is_wrapper_invocation('pwsh -Command"echo hi"')
  # Flag at end of line with no trailing content
  assert is_wrapper_invocation("pwsh -Command")
  assert is_wrapper_invocation("pwsh -c")
  assert is_wrapper_invocation("cmd /c")
  # cmd /c with no space variant
  assert is_wrapper_invocation('cmd /c"del x"')
  # Negative: -copy is not -c
  assert not is_wrapper_invocation("pwsh -copy file.txt")
  # Negative: --version is not an execution flag
  assert not is_wrapper_invocation("pwsh --version")


def test_denylist_single_token_not_prefix():
  assert not matches_denylist("rmdir2 x", ["rmdir"])  # exact token match, not prefix
  assert matches_denylist("ri x", ["ri"])  # pwsh Remove-Item alias


# TC-31: out-of-workspace write -> approval required
def test_tc31_out_of_workspace_write(tmp_path):
  workspace = tmp_path / "ws"
  workspace.mkdir()
  assert write_needs_approval(workspace / "inside.txt", workspace) is False
  assert write_needs_approval(workspace / "sub" / "deep.txt", workspace) is False
  assert write_needs_approval(tmp_path / "outside.txt", workspace) is True
  assert write_needs_approval(Path("C:/Windows/evil.txt"), workspace) is True


# TC-55: classify with empty command line
def test_tc55_classify_empty_command():
  assert classify("", "turbo", DENYLIST).action == "RUN"  # no denylist match, turbo runs
  assert classify("", "manual", DENYLIST).action == "ASK"
  assert classify("   ", "turbo", DENYLIST).action == "RUN"  # whitespace only


# TC-56: classify with unknown policy defaults to ASK
def test_tc56_classify_unknown_policy():
  assert classify("echo hi", "unknown_policy", DENYLIST, safe_to_auto_run=True).action == "ASK"
  assert classify("echo hi", "nonexistent", DENYLIST).action == "ASK"
