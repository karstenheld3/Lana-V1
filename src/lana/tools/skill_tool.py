"""skill executor: SKILL.md body + Base Directory header + supporting file listing (IS-10, DD-14)."""
from lana.tools import ToolContext, ToolError


def execute_skill(args: dict, context: ToolContext) -> str:
  prompt_system = context.prompt_system
  if prompt_system is None: raise ToolError("No prompt system loaded - the skill tool is unavailable.")
  skill = prompt_system.find_skill(args["SkillName"])
  if skill is None:
    available = ", ".join(item.name for item in prompt_system.skills) or "(none)"
    raise ToolError(f"Unknown skill '{args['SkillName']}'. Available skills: {available}")
  lines = [f"Skill: {skill.name}", f"Base Directory: {skill.path}", "Instructions:", skill.content]
  if skill.supporting_files:
    count = len(skill.supporting_files)
    lines.append("")
    lines.append(f"Supporting files ({count} file" + ("s" if count != 1 else "") + ", read them with read_file relative to the base directory):")
    for relative_path in skill.supporting_files: lines.append(f"- {relative_path}")
  return "\n".join(lines)
