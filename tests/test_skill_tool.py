"""TK-014: skill tool returns SKILL.md + supporting file list (IP01 TC-25)."""
import pytest
from lana.loader import load_prompt_systems
from lana.tools import ToolContext, ToolError
from lana.tools.skill_tool import execute_skill


@pytest.fixture
def context(tmp_path, fake_system):
  return ToolContext(workspace=tmp_path, prompt_system=load_prompt_systems([fake_system]))


# TC-25: SKILL.md body + Base Directory header + supporting file list
def test_tc25_skill_returns_content_and_files(context):
  result = execute_skill({"SkillName": "demo-skill"}, context)
  assert result.startswith("Skill: demo-skill")
  assert "Base Directory:" in result and "Use wisely." in result
  assert "Supporting files (2 files" in result and "- GUIDE.md" in result and "- sub/EXTRA.md" in result


def test_unknown_skill_lists_available(context):
  with pytest.raises(ToolError) as error: execute_skill({"SkillName": "nope"}, context)
  assert "demo-skill" in str(error.value)


def test_no_prompt_system(tmp_path):
  with pytest.raises(ToolError): execute_skill({"SkillName": "x"}, ToolContext(workspace=tmp_path))
