"""Edit tool executors with ReadLedger gate: edit, multi_edit, write_to_file (LANAAGNT-FR-11, IS-08)."""
from pathlib import Path
from lana.tools import ToolContext, ToolError
from lana.tools.file_tools import normalize


# Read gate (EC-07/08): file must have been read this session and be unmodified since (mtime check); raises on violation
def enforce_read_gate(path: Path, context: ToolContext) -> None:
  key = normalize(path)
  if key not in context.read_ledger:
    raise ToolError(f"Cannot edit '{path}': the file was not read in this session. Read it with read_file first (edit gate, FR-11).")
  if path.stat().st_mtime > context.read_ledger[key]:
    raise ToolError(f"Cannot edit '{path}': the file was modified externally after the last read. Re-read it with read_file first (edit gate, FR-11).")


# Update ledger to post-edit state so Lana's own edits pass the gate (RF-10)
def update_ledger(path: Path, context: ToolContext) -> None:
  context.read_ledger[normalize(path)] = path.stat().st_mtime


# Apply one replacement to text; raises ToolError on gate violations (EC-09)
def apply_replacement(text: str, old_string: str, new_string: str, replace_all: bool, path: Path) -> str:
  if old_string == new_string: raise ToolError(f"Edit rejected for '{path}': old_string and new_string are identical (no-op).")
  occurrences = text.count(old_string)
  if occurrences == 0: raise ToolError(f"Edit failed for '{path}': old_string not found in file.")
  if occurrences > 1 and not replace_all: raise ToolError(f"Edit failed for '{path}': old_string occurs {occurrences} times. Provide more context to make it unique or set replace_all.")
  if replace_all: return text.replace(old_string, new_string)
  return text.replace(old_string, new_string, 1)


def execute_edit(args: dict, context: ToolContext) -> str:
  path = Path(args["file_path"])
  if not path.exists(): raise ToolError(f"File not found: '{path}'")
  enforce_read_gate(path, context)
  text = path.read_text(encoding="utf-8")
  updated = apply_replacement(text, args["old_string"], args["new_string"], args.get("replace_all", False), path)
  path.write_text(updated, encoding="utf-8", newline="")
  update_ledger(path, context)
  return f"Edit applied to '{path}'."


def execute_multi_edit(args: dict, context: ToolContext) -> str:
  path = Path(args["file_path"])
  if not path.exists(): raise ToolError(f"File not found: '{path}'")
  enforce_read_gate(path, context)
  text = path.read_text(encoding="utf-8")
  updated = text
  for index, edit_item in enumerate(args["edits"], start=1):  # atomic: all in memory, write once (TC-21)
    try:
      updated = apply_replacement(updated, edit_item["old_string"], edit_item["new_string"], edit_item.get("replace_all", False), path)
    except ToolError as error:
      raise ToolError(f"multi_edit failed at edit {index} of {len(args['edits'])}; no changes were applied. {error}") from None
  path.write_text(updated, encoding="utf-8", newline="")
  update_ledger(path, context)
  count = len(args["edits"])
  return f"{count} edit" + ("s" if count != 1 else "") + f" applied to '{path}'."


def execute_write_to_file(args: dict, context: ToolContext) -> str:
  path = Path(args["TargetFile"])
  if path.exists(): raise ToolError(f"Cannot create '{path}': the file already exists. Use edit or multi_edit to modify existing files.")
  path.parent.mkdir(parents=True, exist_ok=True)
  content = "" if args.get("EmptyFile") else args["CodeContent"]
  path.write_text(content, encoding="utf-8", newline="")
  update_ledger(path, context)
  return f"Created '{path}' ({len(content)} chars)."
