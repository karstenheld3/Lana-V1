"""TK-005: PromptSystem loader (IP01 TC-07..12)."""
import time
import pytest
from pathlib import Path
from lana.loader import load_prompt_systems
from tests.conftest import write_prompt_system

DEVSYSTEM_PATH = Path("e:/Dev/IPPS/DevSystemV4.2")


# TC-07: fake system -> counts correct (3 rules loaded, 1 trigger-skipped; 2 workflows; 1 skill)
def test_tc07_fake_system_counts(fake_system):
  system = load_prompt_systems([fake_system])
  assert len(system.rules) == 3 and len(system.workflows) == 2 and len(system.skills) == 1
  assert len(system.injected_rules()) == 2  # gamma.md skipped: trigger model_decision
  assert system.find_workflow("prime").description == "Prime context"
  assert system.find_skill("demo-skill").supporting_files == ["GUIDE.md", "sub/EXTRA.md"]


# TC-08: empty rule (EC-01) -> kept with empty content, marked skipped: empty
def test_tc08_empty_rule(tmp_path):
  base = write_prompt_system(tmp_path / "ps", rules={"empty.md": "---\ntrigger: always_on\n---\n   \n", "full.md": "Body"})
  system = load_prompt_systems([base])
  empty_rule = [rule for rule in system.rules if rule.filename == "empty.md"][0]
  assert empty_rule.skipped_reason == "empty" and empty_rule.content == ""
  assert empty_rule in system.injected_rules()  # empty MEMORY block still injected (Cascade parity)


# TC-09: malformed frontmatter (EC-02) -> body-only, warning
def test_tc09_malformed_frontmatter(tmp_path):
  base = write_prompt_system(tmp_path / "ps", rules={"broken.md": "---\ntrigger: [unclosed\n---\nActual body"})
  system = load_prompt_systems([base])
  rule = system.rules[0]
  assert rule.skipped_reason is None and rule.content == "Actual body"
  assert any("broken.md" in warning for warning in system.warnings)


def test_tc09b_missing_closing_fence(tmp_path):
  base = write_prompt_system(tmp_path / "ps", rules={"open.md": "---\ntrigger: always_on\nno closing fence body"})
  system = load_prompt_systems([base])
  assert system.rules[0].content.startswith("---")  # treated as body-only
  assert any("open.md" in warning for warning in system.warnings)


# TC-10: oversized rule (EC-03) -> truncation marker at limit
def test_tc10_oversized_rule_truncated(tmp_path):
  base = write_prompt_system(tmp_path / "ps", rules={"big.md": "X" * 9000})
  system = load_prompt_systems([base], rule_block_max_chars=6000)
  content = system.rules[0].content
  assert content.startswith("X" * 100) and content.endswith("<truncated 3000 chars>")
  assert len(content) == 6000 + len("\n<truncated 3000 chars>")


# TC-11: two paths, colliding workflow name -> later path wins
def test_tc11_later_path_wins(tmp_path):
  first = write_prompt_system(tmp_path / "first", workflows={"deploy": "---\ndescription: First deploy\n---\nfirst body"})
  second = write_prompt_system(tmp_path / "second", workflows={"deploy": "---\ndescription: Second deploy\n---\nsecond body"})
  system = load_prompt_systems([first, second])
  assert len(system.workflows) == 1
  assert system.find_workflow("deploy").description == "Second deploy" and system.find_workflow("deploy").content == "second body"


def test_builtin_collision_warns(tmp_path):
  base = write_prompt_system(tmp_path / "ps", workflows={"help": "---\ndescription: Custom help\n---\nbody"})
  system = load_prompt_systems([base])
  assert any("built-in" in warning for warning in system.warnings)


def test_missing_path_warns(tmp_path):
  system = load_prompt_systems([tmp_path / "does-not-exist"])
  assert any("not found" in warning for warning in system.warnings)
  assert system.rules == [] and system.workflows == []


# TC-12: real DevSystemV4.2 -> 8 rules / 46 workflows / 21 skills in < 2 s
def test_tc12_real_devsystem_counts_and_speed():
  if not DEVSYSTEM_PATH.is_dir(): pytest.skip("DevSystemV4.2 not present on this machine")
  started = time.perf_counter()
  system = load_prompt_systems([DEVSYSTEM_PATH])
  elapsed = time.perf_counter() - started
  assert len(system.rules) == 8 and len(system.workflows) == 46 and len(system.skills) == 21
  assert elapsed < 2.0, f"load took {elapsed:.2f} s"
