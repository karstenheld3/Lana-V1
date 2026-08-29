"""File reading tool executors: read_file, list_dir, grep_search, find_by_name (IS-07). Pure-Python grep - no ripgrep dependency."""
import fnmatch, re, time
from pathlib import Path
from lana.tools import ToolContext, ToolError

MAX_LINE_CHARS = 2000
FIND_RESULT_CAP = 50
GREP_LINE_CAP = 200


def normalize(path: str | Path) -> str:
  return str(Path(path).resolve()).replace("\\", "/").lower()


# ----------------------------------------- START: read_file ------------------------------------------------------------------

def execute_read_file(args: dict, context: ToolContext) -> str:
  path = Path(args["file_path"])
  if not path.exists(): raise ToolError(f"File not found: '{path}'")
  if path.is_dir(): raise ToolError(f"'{path}' is a directory - use list_dir")
  try:
    text = path.read_text(encoding="utf-8", errors="replace")
  except OSError as error:
    raise ToolError(f"Cannot read '{path}': {error}") from None
  context.read_ledger[normalize(path)] = path.stat().st_mtime  # FR-11 read gate ledger
  if not text.strip(): return f"<system reminder: '{path.name}' exists but has empty contents>"
  lines = text.splitlines()
  offset = max(args.get("offset", 1), 1)
  limit = args.get("limit", len(lines))
  selected = lines[offset - 1:offset - 1 + limit]
  rendered = []
  for index, line in enumerate(selected, start=offset):
    if len(line) > MAX_LINE_CHARS: line = line[:MAX_LINE_CHARS] + "... <line truncated>"
    rendered.append(f"{index:6d}\t{line}")
  return "\n".join(rendered)

# ----------------------------------------- END: read_file --------------------------------------------------------------------


# ----------------------------------------- START: list_dir -------------------------------------------------------------------

def execute_list_dir(args: dict, context: ToolContext) -> str:
  base = Path(args["DirectoryPath"])
  if not base.is_dir(): raise ToolError(f"Directory not found: '{base}'")
  entries = []
  for item in sorted(base.iterdir(), key=lambda candidate: (candidate.is_file(), candidate.name.lower())):
    if item.is_dir():
      count = sum(1 for _ in item.rglob("*"))
      entries.append(f"{item.name}/ ({count} item" + ("s" if count != 1 else "") + ")")
    else:
      entries.append(f"{item.name} ({item.stat().st_size} bytes)")
  if not entries: return f"'{base}' is empty."
  return "\n".join(entries)

# ----------------------------------------- END: list_dir ---------------------------------------------------------------------


# ----------------------------------------- START: grep_search ----------------------------------------------------------------

def iter_search_files(base: Path, includes: list[str]):
  if base.is_file(): yield base; return
  for candidate in sorted(base.rglob("*")):
    if not candidate.is_file(): continue
    if includes:
      relative = str(candidate.relative_to(base)).replace("\\", "/")
      if not any(fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(candidate.name, pattern) for pattern in includes): continue
    yield candidate


def execute_grep_search(args: dict, context: ToolContext) -> str:
  base = Path(args["SearchPath"])
  if not base.exists(): raise ToolError(f"Search path not found: '{base}'")
  flags = 0 if args.get("CaseSensitive") else re.IGNORECASE
  query = re.escape(args["Query"]) if args.get("FixedStrings") else args["Query"]
  try:
    pattern = re.compile(query, flags)
  except re.error as error:
    raise ToolError(f"Invalid regex '{args['Query']}': {error}") from None
  match_per_line = args.get("MatchPerLine", False)
  output, total_lines, truncated = [], 0, False
  for candidate in iter_search_files(base, args.get("Includes", [])):
    try:
      text = candidate.read_text(encoding="utf-8", errors="replace")
    except OSError:
      continue
    if "\x00" in text[:1024]: continue  # skip binary content
    file_matches = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
      if pattern.search(line):
        file_matches += 1
        if match_per_line:
          output.append(f"{candidate}:{line_number}: {line.strip()[:300]}")
          total_lines += 1
          if total_lines >= GREP_LINE_CAP: truncated = True; break
    if not match_per_line and file_matches: output.append(f"{candidate} ({file_matches} match" + ("es" if file_matches != 1 else "") + ")")
    if truncated: break
  if not output: return "No matches found."
  if truncated: output.append(f"<result truncated at {GREP_LINE_CAP} lines - narrow the search>")
  return "\n".join(output)

# ----------------------------------------- END: grep_search ------------------------------------------------------------------


# ----------------------------------------- START: find_by_name ---------------------------------------------------------------

def execute_find_by_name(args: dict, context: ToolContext) -> str:
  base = Path(args["SearchDirectory"])
  if not base.is_dir(): raise ToolError(f"Search directory not found: '{base}'")
  pattern = args["Pattern"]
  excludes = args.get("Excludes", [])
  extensions = args.get("Extensions", [])
  type_filter = args.get("Type", "any")
  max_depth = args.get("MaxDepth")
  full_path = args.get("FullPath", False)
  results = []
  for candidate in sorted(base.rglob("*")):
    relative = str(candidate.relative_to(base)).replace("\\", "/")
    if max_depth is not None and relative.count("/") >= max_depth: continue
    if type_filter == "file" and not candidate.is_file(): continue
    if type_filter == "directory" and not candidate.is_dir(): continue
    subject = relative if full_path else candidate.name
    if not fnmatch.fnmatch(subject, pattern) and not (extensions and candidate.suffix.lstrip(".") in extensions): continue
    if extensions and candidate.is_file() and candidate.suffix.lstrip(".") not in extensions: continue
    if any(fnmatch.fnmatch(relative, exclude) or fnmatch.fnmatch(candidate.name, exclude) for exclude in excludes): continue
    stat = candidate.stat()
    kind = "dir" if candidate.is_dir() else "file"
    modified = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
    size = f", {stat.st_size} bytes" if candidate.is_file() else ""
    results.append(f"{relative} ({kind}{size}, modified {modified})")
    if len(results) >= FIND_RESULT_CAP: results.append(f"<capped at {FIND_RESULT_CAP} results>"); break
  if not results: return "0 matches found."
  return "\n".join(results)

# ----------------------------------------- END: find_by_name -----------------------------------------------------------------
