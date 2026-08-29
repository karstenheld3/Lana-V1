"""PromptSystem loading: rules, workflows, skills with frontmatter parsing and path precedence (LANAAGNT-FR-02, IS-04)."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml

BUILTIN_COMMANDS = ("help", "cost", "exit")


@dataclass
class RuleFile:
  filename: str
  trigger: Optional[str]
  content: str
  skipped_reason: Optional[str] = None  # None (injected) | "empty" | "trigger"


@dataclass
class WorkflowFile:
  name: str
  description: str
  content: str
  path: Path


@dataclass
class SkillFolder:
  name: str
  description: str
  content: str
  supporting_files: list[str]
  path: Path


@dataclass
class PromptSystem:
  rules: list[RuleFile] = field(default_factory=list)
  workflows: list[WorkflowFile] = field(default_factory=list)
  skills: list[SkillFolder] = field(default_factory=list)
  warnings: list[str] = field(default_factory=list)

  def injected_rules(self) -> list[RuleFile]:
    return [rule for rule in self.rules if rule.skipped_reason in (None, "empty")]  # empty rules keep an empty MEMORY block (EC-01)

  def find_workflow(self, name: str) -> Optional[WorkflowFile]:
    for workflow in self.workflows:
      if workflow.name == name: return workflow
    return None

  def find_skill(self, name: str) -> Optional[SkillFolder]:
    for skill in self.skills:
      if skill.name == name: return skill
    return None


# ----------------------------------------- START: Frontmatter ----------------------------------------------------------------

# Split YAML frontmatter from body; tolerant per EC-02: missing or malformed -> body-only + warning
def parse_frontmatter(text: str, source_name: str) -> tuple[dict, str, Optional[str]]:
  if not text.startswith("---"): return {}, text, None
  lines = text.splitlines(keepends=True)
  closing_index = None
  for index in range(1, len(lines)):
    if lines[index].strip() == "---": closing_index = index; break
  if closing_index is None: return {}, text, f"Frontmatter in '{source_name}' has no closing '---' - treated as body-only"
  raw_meta = "".join(lines[1:closing_index])
  body = "".join(lines[closing_index + 1:])
  try:
    meta = yaml.safe_load(raw_meta)
  except yaml.YAMLError:
    return {}, body, f"Malformed YAML frontmatter in '{source_name}' - treated as body-only"
  if not isinstance(meta, dict): return {}, body, f"Frontmatter in '{source_name}' is not a mapping - treated as body-only"
  return meta, body, None

# ----------------------------------------- END: Frontmatter ------------------------------------------------------------------


# ----------------------------------------- START: Loading --------------------------------------------------------------------

# Truncate rule body at limit with marker (EC-03)
def truncate_block(content: str, max_chars: int) -> str:
  if len(content) <= max_chars: return content
  removed = len(content) - max_chars
  return content[:max_chars] + f"\n<truncated {removed} chars>"


def load_rule(path: Path, max_chars: int, warnings: list[str]) -> RuleFile:
  meta, body, warning = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"), path.name)
  if warning: warnings.append(warning)
  trigger = meta.get("trigger")
  if trigger is not None and trigger != "always_on": return RuleFile(filename=path.name, trigger=trigger, content="", skipped_reason="trigger")
  body = body.strip()
  if not body: return RuleFile(filename=path.name, trigger=trigger, content="", skipped_reason="empty")
  return RuleFile(filename=path.name, trigger=trigger, content=truncate_block(body, max_chars))


def load_workflow(path: Path, warnings: list[str]) -> WorkflowFile:
  meta, body, warning = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"), path.name)
  if warning: warnings.append(warning)
  return WorkflowFile(name=path.stem, description=str(meta.get("description", "")).strip(), content=body.strip(), path=path)


def load_skill(skill_md: Path, warnings: list[str]) -> SkillFolder:
  folder = skill_md.parent
  meta, body, warning = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"), str(skill_md))
  if warning: warnings.append(warning)
  supporting_files = sorted(str(candidate.relative_to(folder)).replace("\\", "/") for candidate in folder.rglob("*") if candidate.is_file() and candidate != skill_md)
  return SkillFolder(name=str(meta.get("name", folder.name)).strip() or folder.name, description=str(meta.get("description", "")).strip(), content=body.strip(), supporting_files=supporting_files, path=folder)


def load_prompt_systems(paths: list[str | Path], rule_block_max_chars: int = 6000) -> PromptSystem:
  """
  Load rules/workflows/skills from each path; later paths override earlier on name collision (FR-02 precedence).

  └── rules/*.md      -> RuleFile   (trigger always_on or missing injected; others skipped)
  └── workflows/*.md  -> WorkflowFile (name = filename stem, invoked as /name)
  └── skills/*/SKILL.md -> SkillFolder (supporting files listed, not read)
  """
  system = PromptSystem()
  rules_by_name: dict[str, RuleFile] = {}
  workflows_by_name: dict[str, WorkflowFile] = {}
  skills_by_name: dict[str, SkillFolder] = {}
  for raw_path in paths:
    base = Path(raw_path)
    if not base.is_dir(): system.warnings.append(f"Prompt system path not found: '{base}' - skipped"); continue
    for rule_path in sorted((base / "rules").glob("*.md")): rule = load_rule(rule_path, rule_block_max_chars, system.warnings); rules_by_name[rule.filename] = rule
    for workflow_path in sorted((base / "workflows").glob("*.md")): workflow = load_workflow(workflow_path, system.warnings); workflows_by_name[workflow.name] = workflow
    skills_dir = base / "skills"
    if skills_dir.is_dir():
      for skill_md in sorted(skills_dir.glob("*/SKILL.md")): skill = load_skill(skill_md, system.warnings); skills_by_name[skill.name] = skill
  for name in BUILTIN_COMMANDS:
    if name in workflows_by_name: system.warnings.append(f"Workflow '{name}.md' collides with built-in command /{name} - built-in wins (EC-06)")
  system.rules = list(rules_by_name.values())
  system.workflows = list(workflows_by_name.values())
  system.skills = list(skills_by_name.values())
  return system

# ----------------------------------------- END: Loading ----------------------------------------------------------------------
