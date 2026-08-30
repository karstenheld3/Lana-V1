"""TK-008/009: definitions.py descriptions match LANAAGNT-IN02 with zero diff outside substitution points (IS-06)."""
import re
import pytest
from pathlib import Path
from lana.tools.definitions import DESCRIPTION_TEMPLATES, SCHEMAS, TOOL_NAMES, schema_json

IN02_PATH = Path(__file__).parent.parent / "_2026-08-29_LanaV1DesignQuestions" / "_INFO_CASCADE_TOOL_DEFINITIONS.md"

EXPECTED_TOOLS = ["read_file", "list_dir", "grep_search", "find_by_name", "edit", "multi_edit", "write_to_file", "run_command", "command_status", "todo_list", "skill", "ask_user_question", "search_web", "read_url_content", "view_content_chunk", "trajectory_search"]


def extract_in02_descriptions() -> dict:
  markdown = IN02_PATH.read_text(encoding="utf-8")
  descriptions = {}
  sections = re.split(r"^### \d+\.\d+ (\w+)", markdown, flags=re.MULTILINE)
  for index in range(1, len(sections), 2):
    match = re.search(r"```text\n(.*?)\n```", sections[index + 1], flags=re.DOTALL)
    if match: descriptions[sections[index]] = match.group(1)
  return descriptions


def test_all_16_tools_present():
  assert TOOL_NAMES == EXPECTED_TOOLS


def test_zero_diff_against_in02():
  if not IN02_PATH.exists(): pytest.skip("IN02 source document not present")
  source = extract_in02_descriptions()
  for name in EXPECTED_TOOLS:
    assert name in source, f"IN02 missing section for {name}"
    assert DESCRIPTION_TEMPLATES[name] == source[name], f"description diff vs IN02 for '{name}'"


def test_substitution_points_present():
  assert "{OS}" in DESCRIPTION_TEMPLATES["run_command"] and "{SHELL}" in DESCRIPTION_TEMPLATES["run_command"]
  assert "{SKILL_LIST}" in DESCRIPTION_TEMPLATES["skill"]
  for name in EXPECTED_TOOLS:
    if name not in ("run_command", "skill"):
      assert "{OS}" not in DESCRIPTION_TEMPLATES[name] and "{SKILL_LIST}" not in DESCRIPTION_TEMPLATES[name]


def test_schemas_draft_2020_12_shape():
  for name in EXPECTED_TOOLS:
    schema = SCHEMAS[name]
    assert schema["type"] == "object" and schema["additionalProperties"] is False
    assert isinstance(schema.get("required"), list) and schema["required"], f"{name} has no required array"
    for required_name in schema["required"]: assert required_name in schema["properties"]


def test_schema_serialization_deterministic():
  for name in EXPECTED_TOOLS: assert schema_json(name) == schema_json(name)
  assert schema_json("read_file").index('"file_path"') < schema_json("read_file").index('"limit"')  # sorted keys
