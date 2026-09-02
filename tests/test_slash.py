"""TK-022: slash command expansion and unknown-name suggestions (FR-05, EC-05)."""
import pytest
from lana.agent import UnknownWorkflowError, expand_slash_command
from lana.loader import load_prompt_systems


@pytest.fixture
def prompt_system(fake_system):
  return load_prompt_systems([fake_system])


def test_workflow_expansion_cascade_format(prompt_system):
  content, name = expand_slash_command("/prime", prompt_system)
  assert name == "prime"
  assert content.startswith("/prime\n<workflows>")
  assert "@[/prime] is a [Workflow]:" in content
  assert "Step 1: read notes." in content  # full workflow body injected
  assert content.rstrip().endswith("</workflows>")


def test_plain_text_not_expanded(prompt_system):
  content, name = expand_slash_command("just some text", prompt_system)
  assert content == "just some text" and name is None


def test_arguments_preserved_in_user_request(prompt_system):
  content, name = expand_slash_command("/prime with extra args", prompt_system)
  assert name == "prime" and "/prime with extra args" in content


# EC-05: unknown /name -> up to 3 closest matches, never sent to the Generator
def test_unknown_name_suggestions(prompt_system):
  with pytest.raises(UnknownWorkflowError) as error: expand_slash_command("/pri", prompt_system)
  assert error.value.suggestions == ["prime"]
  assert "/prime" in str(error.value)
  with pytest.raises(UnknownWorkflowError) as error: expand_slash_command("/zzz", prompt_system)
  assert error.value.suggestions == []
