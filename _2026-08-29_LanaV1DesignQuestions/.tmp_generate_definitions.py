# Generate src/lana/tools/definitions.py from LANAAGNT-IN02 (guarantees character-for-character transcription, IS-06)
import json, re
from pathlib import Path

SESSION = Path(__file__).parent
IN02 = SESSION / "_INFO_CASCADE_TOOL_DEFINITIONS.md"
TARGET = SESSION.parent / "src" / "lana" / "tools" / "definitions.py"

TOOL_ORDER = ["read_file", "list_dir", "grep_search", "find_by_name", "edit", "multi_edit", "write_to_file", "run_command", "command_status", "todo_list", "skill", "ask_user_question", "search_web", "read_url_content", "view_content_chunk"]

SCHEMAS = {
  "read_file": {"type": "object", "additionalProperties": False, "properties": {"file_path": {"type": "string"}, "offset": {"type": "integer"}, "limit": {"type": "integer"}}, "required": ["file_path"]},
  "list_dir": {"type": "object", "additionalProperties": False, "properties": {"DirectoryPath": {"type": "string"}}, "required": ["DirectoryPath"]},
  "grep_search": {"type": "object", "additionalProperties": False, "properties": {"SearchPath": {"type": "string"}, "Query": {"type": "string"}, "CaseSensitive": {"type": "boolean"}, "FixedStrings": {"type": "boolean"}, "Includes": {"type": "array", "items": {"type": "string"}}, "MatchPerLine": {"type": "boolean"}}, "required": ["SearchPath", "Query"]},
  "find_by_name": {"type": "object", "additionalProperties": False, "properties": {"SearchDirectory": {"type": "string"}, "Pattern": {"type": "string"}, "Excludes": {"type": "array", "items": {"type": "string"}}, "Extensions": {"type": "array", "items": {"type": "string"}}, "FullPath": {"type": "boolean"}, "MaxDepth": {"type": "integer"}, "Type": {"type": "string", "enum": ["file", "directory", "any"]}}, "required": ["SearchDirectory", "Pattern"]},
  "edit": {"type": "object", "additionalProperties": False, "properties": {"explanation": {"type": "string"}, "file_path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}, "replace_all": {"type": "boolean"}}, "required": ["file_path", "old_string", "new_string"]},
  "multi_edit": {"type": "object", "additionalProperties": False, "properties": {"explanation": {"type": "string"}, "file_path": {"type": "string"}, "edits": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False, "properties": {"old_string": {"type": "string"}, "new_string": {"type": "string"}, "replace_all": {"type": "boolean"}}, "required": ["old_string", "new_string"]}}}, "required": ["file_path", "edits"]},
  "write_to_file": {"type": "object", "additionalProperties": False, "properties": {"TargetFile": {"type": "string"}, "CodeContent": {"type": "string"}, "EmptyFile": {"type": "boolean"}}, "required": ["TargetFile", "CodeContent", "EmptyFile"]},
  "run_command": {"type": "object", "additionalProperties": False, "properties": {"CommandLine": {"type": "string"}, "Cwd": {"type": "string"}, "Blocking": {"type": "boolean"}, "SafeToAutoRun": {"type": "boolean"}, "WaitMsBeforeAsync": {"type": "integer"}}, "required": ["CommandLine"]},
  "command_status": {"type": "object", "additionalProperties": False, "properties": {"CommandId": {"type": "string"}, "OutputCharacterCount": {"type": "integer"}, "WaitDurationSeconds": {"type": "integer", "default": 0}}, "required": ["CommandId", "OutputCharacterCount"]},
  "todo_list": {"type": "object", "additionalProperties": False, "properties": {"todos": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {"id": {"type": "string"}, "content": {"type": "string"}, "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]}, "priority": {"type": "string", "enum": ["high", "medium", "low"]}}, "required": ["id", "content", "status", "priority"]}}}, "required": ["todos"]},
  "skill": {"type": "object", "additionalProperties": False, "properties": {"SkillName": {"type": "string"}}, "required": ["SkillName"]},
  "ask_user_question": {"type": "object", "additionalProperties": False, "properties": {"question": {"type": "string"}, "options": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {"label": {"type": "string"}, "description": {"type": "string"}}, "required": ["label", "description"]}}, "allowMultiple": {"type": "boolean"}}, "required": ["question", "options", "allowMultiple"]},
  "search_web": {"type": "object", "additionalProperties": False, "properties": {"query": {"type": "string"}, "domain": {"type": "string"}}, "required": ["query"]},
  "read_url_content": {"type": "object", "additionalProperties": False, "properties": {"Url": {"type": "string"}}, "required": ["Url"]},
  "view_content_chunk": {"type": "object", "additionalProperties": False, "properties": {"document_id": {"type": "string"}, "position": {"type": "integer"}}, "required": ["document_id", "position"]},
}


# Extract {tool_name: literal description} from IN02: each '### N.N name' section's first ```text fenced block
def extract_descriptions(markdown: str) -> dict:
  descriptions = {}
  sections = re.split(r"^### \d+\.\d+ (\w+)", markdown, flags=re.MULTILINE)
  for index in range(1, len(sections), 2):
    name, body = sections[index], sections[index + 1]
    match = re.search(r"```text\n(.*?)\n```", body, flags=re.DOTALL)
    if match and name in TOOL_ORDER: descriptions[name] = match.group(1)
  return descriptions


def main():
  descriptions = extract_descriptions(IN02.read_text(encoding="utf-8"))
  missing = [name for name in TOOL_ORDER if name not in descriptions]
  if missing: raise SystemExit(f"FAIL: missing descriptions for {missing}")
  lines = ['"""15 verbatim Cascade tool definitions (LANAAGNT-IN02 transcription, IS-06).', "", "GENERATED by .tmp_generate_definitions.py from _INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02].", "Descriptions are [LITERAL] - never hand-edit; regenerate from IN02 instead.", "Substitution points: {OS}/{SHELL} in run_command, {SKILL_LIST} in skill (applied by render_definitions).", '"""', "import json", ""]
  lines.append("DESCRIPTION_TEMPLATES = {")
  for name in TOOL_ORDER: lines.append(f"  {json.dumps(name)}: {json.dumps(descriptions[name], ensure_ascii=False)},")
  lines.append("}")
  lines.append("")
  lines.append("SCHEMAS = {")
  for name in TOOL_ORDER: lines.append(f"  {json.dumps(name)}: {repr(SCHEMAS[name])},")
  lines.append("}")
  lines.append("""

TOOL_NAMES = list(DESCRIPTION_TEMPLATES)


# Deterministic serialization for cache stability (IS-06): sorted keys, compact separators
def schema_json(name: str) -> str:
  return json.dumps(SCHEMAS[name], sort_keys=True, separators=(",", ":"))


def render_skill_list(skills) -> str:
  entries = []
  for skill in skills:
    file_count = len(skill.supporting_files)
    suffix = f" ({file_count} supporting file" + ("s" if file_count != 1 else "") + ")" if file_count else ""
    entries.append(f"- {skill.name}: {skill.description}{suffix}")
  return "\\n".join(entries)


def render_definitions(os_name: str, shell: str, skills) -> list[dict]:
  \"\"\"
  Produce the finalized tool definitions with substitution points filled.

  Example item: {"name": "read_file", "description": "Reads a file...", "schema": {...}}
  \"\"\"
  rendered = []
  for name in TOOL_NAMES:
    description = DESCRIPTION_TEMPLATES[name]
    if name == "run_command": description = description.replace("{OS}", os_name).replace("{SHELL}", shell)
    if name == "skill": description = description.replace("{SKILL_LIST}", render_skill_list(skills))
    rendered.append({"name": name, "description": description, "schema": SCHEMAS[name]})
  return rendered
""")
  TARGET.parent.mkdir(parents=True, exist_ok=True)
  TARGET.write_text("\n".join(lines), encoding="utf-8", newline="\n")
  print(f"OK: wrote {TARGET} with {len(TOOL_ORDER)} tool definitions")


if __name__ == "__main__": main()
