"""TK-006/007: system prompt assembly (IP01 TC-13..15)."""
import re
from lana.loader import load_prompt_systems
from lana.prompt import build_capability_notice, build_system_prompt

WORKSPACE_INFO = {"os": "windows", "workspace": "e:/Dev/Sample", "git_root": "e:/Dev/Sample"}

# Tools dropped from Cascade's set (DD-10) - must not appear outside <capability_notice> (RV01 RF-04)
DROPPED_TOOL_NAMES = ["code_search", "create_memory", "trajectory_search", "read_terminal", "browser_preview", "deploy_web_app", "read_deployment_config", "check_deploy_status", "edit_notebook", "read_notebook", "list_resources", "read_resource", "mcp1_", "mcp2_"]

FR03_SECTION_ORDER = ["You are Lana", "<communication_style>", "<tool_calling>", "<making_code_changes>", "<task_management>", "<running_commands>", "<debugging>", "<calling_external_apis>", "<workflows>", "<user_rules>", "<capability_notice>", "<user_information>"]


# TC-13: two consecutive builds byte-identical (IG-01)
def test_tc13_byte_identity(fake_system):
  system = load_prompt_systems([fake_system])
  first, second = build_system_prompt(system, WORKSPACE_INFO), build_system_prompt(system, WORKSPACE_INFO)
  assert first == second


def test_tc13b_no_datetime_or_variable_content(fake_system):
  prompt = build_system_prompt(load_prompt_systems([fake_system]), WORKSPACE_INFO)
  assert not re.search(r"\d{4}-\d{2}-\d{2}", prompt)  # no dates anywhere (IG-01)


# TC-14: dropped-tool names appear ONLY inside <capability_notice> (RF-04 regression)
def test_tc14_no_dropped_tool_references_outside_notice(fake_system):
  prompt = build_system_prompt(load_prompt_systems([fake_system]), WORKSPACE_INFO)
  notice = build_capability_notice()
  outside = prompt.replace(notice, "")
  for name in DROPPED_TOOL_NAMES: assert name not in outside, f"dropped tool '{name}' referenced outside capability notice"


# TC-15: section order matches FR-03 exactly
def test_tc15_section_order(fake_system):
  prompt = build_system_prompt(load_prompt_systems([fake_system]), WORKSPACE_INFO)
  positions = [prompt.index(marker) for marker in FR03_SECTION_ORDER]
  assert positions == sorted(positions), "FR-03 section order violated"


def test_memory_blocks_and_preamble(fake_system):
  prompt = build_system_prompt(load_prompt_systems([fake_system]), WORKSPACE_INFO)
  assert "<MEMORY[alpha.md]>" in prompt and "Alpha rule body" in prompt
  assert "<MEMORY[gamma.md]>" not in prompt  # trigger-skipped rule not injected
  assert "MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION" in prompt
  assert "- /prime: Prime context" in prompt and "- /verify: Verify work" in prompt


def test_capability_notice_lists_fallback():
  notice = build_capability_notice()
  assert "code_search" in notice and "grep_search" in notice
