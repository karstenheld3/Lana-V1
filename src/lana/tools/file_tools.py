"""File reading tool executors: read_file, list_dir, grep_search, find_by_name, search (IS-07). Uses ripgrep when available, Python fallback otherwise."""
import fnmatch, os, re, subprocess, time
from pathlib import Path
from lana.tools import ToolContext, ToolError

MAX_LINE_CHARS = 2000
FIND_RESULT_CAP = 50
GREP_LINE_CAP = 200
PATH_HINT_SIBLINGS = 5


def path_not_found_hint(target: Path) -> str:
  """Build a hint showing the closest existing parent and up to N sibling matches (LANALOGS-PR-0002)."""
  parent = target.parent
  while parent != parent.parent and not parent.exists(): parent = parent.parent
  if not parent.exists(): return ""
  missing_name = target.name.lower()
  missing_stem = target.stem.lower().rstrip("0123456789").rstrip("_- ")
  siblings = []
  try:
    siblings = sorted(item.name for item in parent.iterdir()
                      if missing_name in item.name.lower() or (missing_stem and missing_stem in item.name.lower()))[:PATH_HINT_SIBLINGS]
  except OSError:
    pass
  hint = f"\n  HINT: closest existing parent is '{parent}'."
  if siblings: hint += f" Similar entries: {', '.join(siblings)}"
  return hint

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".ico", ".heic", ".heif")
# rg/fd parity: both tool descriptions promise gitignore-style skipping; this fixed set covers the dominant
# noise directories without a gitignore parser dependency (DD-17 closed list) - documented approximation
IGNORED_DIRECTORIES = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache", ".mypy_cache", ".lana", ".lana-data", "dist", "build"}


def is_inside_ignored_directory(path: Path, base: Path) -> bool:
  try:
    relative_parts = path.relative_to(base).parts
  except ValueError:
    relative_parts = path.parts
  return any(part in IGNORED_DIRECTORIES or part.endswith(".egg-info") for part in relative_parts[:-1] if part)


def normalize(path: str | Path) -> str:
  return str(Path(path).resolve()).replace("\\", "/").lower()


# ----------------------------------------- START: read_file ------------------------------------------------------------------

def execute_read_file(args: dict, context: ToolContext) -> str:
  path = Path(args["file_path"])
  if not path.exists(): raise ToolError(f"File not found: '{path}'{path_not_found_hint(path)}")
  if path.is_dir(): raise ToolError(f"'{path}' is a directory - use list_dir")
  if path.suffix.lower() in IMAGE_EXTENSIONS and path.suffix.lower() != ".svg": raise ToolError(f"'{path.name}' is an image - visual presentation is not available in this CLI environment")
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
  if not base.is_dir(): raise ToolError(f"Directory not found: '{base}'{path_not_found_hint(base)}")
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


# ----------------------------------------- START: ripgrep integration ---------------------------------------------------------

def _find_rg(context: ToolContext) -> str | None:
  """Return rg executable path from tools_dir, or None. Highlander: one canonical location."""
  if context.tools_dir is None: return None
  rg = context.tools_dir / ("rg.exe" if os.name == "nt" else "rg")
  return str(rg) if rg.is_file() else None


def _rg_common_flags() -> list[str]:
  """Common rg flags: search hidden files, suppress file-open errors, exclude IGNORED_DIRECTORIES via globs."""
  flags = ["--hidden", "--no-messages"]
  flags.extend(arg for name in IGNORED_DIRECTORIES for arg in ("-g", f"!{name}/"))
  return flags

# ----------------------------------------- END: ripgrep integration -----------------------------------------------------------


# ----------------------------------------- START: grep_search ----------------------------------------------------------------

def _grep_rg(rg: str, args: dict) -> str:
  """grep_search backed by ripgrep subprocess."""
  base = args["SearchPath"]
  query = args["Query"]
  match_per_line = args.get("MatchPerLine", False)
  # Base flags: smart-case (case-insensitive when pattern is all lowercase, case-sensitive otherwise),
  # skip huge files, search hidden files, suppress file-open errors
  cmd = [rg, "--color=never", "--max-filesize=10M"]
  cmd.extend(_rg_common_flags())
  if args.get("CaseSensitive"): cmd.append("--case-sensitive")
  else: cmd.append("--smart-case")
  if args.get("FixedStrings"): cmd.append("--fixed-strings")
  for pattern in args.get("Includes", []): cmd.extend(("-g", pattern))
  if match_per_line:
    cmd.extend(["--no-heading", "--with-filename", "--line-number", "--max-count=200"])
    cmd.extend(["--", query, str(base)])
    try:
      result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace")
    except (subprocess.TimeoutExpired, OSError):
      return ""  # signal caller to fall back to Python
    if result.returncode > 1: return ""  # rg error (not "no match" which is 1)
    if not result.stdout.strip(): return "No matches found."
    lines = result.stdout.strip().splitlines()[:GREP_LINE_CAP]
    output = []
    for line in lines:
      # rg output: path:line_number:content
      parts = line.split(":", 2)
      if len(parts) >= 3: output.append(f"{parts[0]}:{parts[1]}: {parts[2].strip()[:300]}")
      else: output.append(line[:300])
    if len(lines) >= GREP_LINE_CAP: output.append(f"<result truncated at {GREP_LINE_CAP} lines - narrow the search>")
    return "\n".join(output)
  # file-count mode: single rg --count invocation (path:count per file)
  cmd.extend(["--count", "--", query, str(base)])
  try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace")
  except (subprocess.TimeoutExpired, OSError):
    return ""
  if result.returncode > 1: return ""
  output = []
  for line in result.stdout.strip().splitlines():
    parts = line.rsplit(":", 1)
    if len(parts) == 2 and parts[1].strip().isdigit():
      count = int(parts[1].strip())
      output.append(f"{parts[0]} ({count} match" + ("es" if count != 1 else "") + ")")
  return "\n".join(output) if output else "No matches found."


def _grep_python(base: Path, args: dict) -> str:
  """grep_search pure-Python fallback."""
  flags = 0 if args.get("CaseSensitive") else re.IGNORECASE
  query = re.escape(args["Query"]) if args.get("FixedStrings") else args["Query"]
  try:
    pattern = re.compile(query, flags)
  except re.error as error:
    raise ToolError(f"Invalid regex '{args['Query']}': {error}") from None
  match_per_line = args.get("MatchPerLine", False)
  includes = args.get("Includes", [])
  output, total_lines, truncated = [], 0, False
  for candidate in _walk_files(base, includes):
    try:
      text = candidate.read_text(encoding="utf-8", errors="replace")
    except OSError:
      continue
    if "\x00" in text[:1024]: continue
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


def _walk_files(base: Path, includes: list[str]):
  """Yield files under base, skipping ignored dirs during traversal (not after)."""
  if base.is_file(): yield base; return
  stack = [base]
  while stack:
    current = stack.pop()
    try:
      entries = sorted(os.scandir(current), key=lambda e: e.name.lower())
    except OSError:
      continue
    dirs = []
    for entry in entries:
      if entry.is_dir(follow_symlinks=False):
        if entry.name not in IGNORED_DIRECTORIES and not entry.name.endswith(".egg-info"): dirs.append(Path(entry.path))
      elif entry.is_file(follow_symlinks=False):
        path = Path(entry.path)
        if includes:
          relative = str(path.relative_to(base)).replace("\\", "/")
          if not any(fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(path.name, pattern) for pattern in includes): continue
        yield path
    stack.extend(reversed(dirs))


def execute_grep_search(args: dict, context: ToolContext) -> str:
  base = Path(args["SearchPath"])
  if not base.exists(): raise ToolError(f"Search path not found: '{base}'")
  rg = _find_rg(context)
  if rg:
    result = _grep_rg(rg, args)
    if result: return result  # empty string = rg failed, fall through to Python
  return _grep_python(base, args)

# ----------------------------------------- END: grep_search ------------------------------------------------------------------


# ----------------------------------------- START: find_by_name ---------------------------------------------------------------

def _find_rg_files(rg: str, args: dict) -> str:
  """find_by_name backed by rg --files. Only handles Type=file; directory/any fall through to Python."""
  type_filter = args.get("Type", "any")
  if type_filter != "file": return ""  # rg --files only lists files, not directories
  base = args["SearchDirectory"]
  pattern = args["Pattern"]
  max_depth = args.get("MaxDepth")
  excludes = args.get("Excludes", [])
  extensions = args.get("Extensions", [])
  # --no-ignore: find ALL files regardless of .gitignore (our glob excludes handle noise)
  cmd = [rg, "--files", "--color=never", "--sort=path", "--no-ignore"]
  cmd.extend(_rg_common_flags())
  if max_depth is not None: cmd.extend(("--max-depth", str(max_depth)))
  if pattern != "*": cmd.extend(("-g", pattern))
  for ext in extensions: cmd.extend(("-g", f"*.{ext}"))
  for exclude in excludes: cmd.extend(("-g", f"!{exclude}"))
  cmd.append(str(base))
  try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace")
  except (subprocess.TimeoutExpired, OSError):
    return ""  # fall back to Python
  if result.returncode > 1: return ""
  if not result.stdout.strip(): return "0 matches found."
  base_path = Path(base)
  results = []
  for line in result.stdout.strip().splitlines():
    path = Path(line.strip())
    try:
      relative = str(path.relative_to(base_path)).replace("\\", "/")
    except ValueError:
      relative = line.strip()
    try:
      stat = path.stat()
    except OSError:
      continue
    modified = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
    results.append(f"{relative} (file, {stat.st_size} bytes, modified {modified})")
    if len(results) >= FIND_RESULT_CAP: results.append(f"<capped at {FIND_RESULT_CAP} results>"); break
  return "\n".join(results) if results else "0 matches found."


def _find_python(base: Path, args: dict) -> str:
  """find_by_name pure-Python fallback with os.scandir (skips ignored dirs during walk)."""
  pattern = args["Pattern"]
  excludes = args.get("Excludes", [])
  extensions = args.get("Extensions", [])
  type_filter = args.get("Type", "any")
  max_depth = args.get("MaxDepth")
  full_path = args.get("FullPath", False)
  results = []
  stack = [(base, 0)]
  while stack:
    current, depth = stack.pop()
    if max_depth is not None and depth >= max_depth: continue
    try:
      entries = sorted(os.scandir(current), key=lambda e: e.name.lower())
    except OSError:
      continue
    dirs = []
    for entry in entries:
      if entry.name in IGNORED_DIRECTORIES or entry.name.endswith(".egg-info"): continue
      path = Path(entry.path)
      relative = str(path.relative_to(base)).replace("\\", "/")
      is_dir = entry.is_dir(follow_symlinks=False)
      is_file = entry.is_file(follow_symlinks=False)
      if is_dir: dirs.append((path, depth + 1))
      if type_filter == "file" and not is_file: continue
      if type_filter == "directory" and not is_dir: continue
      subject = relative if full_path else entry.name
      if not fnmatch.fnmatch(subject, pattern) and not (extensions and is_file and path.suffix.lstrip(".") in extensions): continue
      if extensions and is_file and path.suffix.lstrip(".") not in extensions: continue
      if any(fnmatch.fnmatch(relative, exc) or fnmatch.fnmatch(entry.name, exc) for exc in excludes): continue
      try:
        stat = entry.stat()
      except OSError:
        continue
      kind = "dir" if is_dir else "file"
      modified = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
      size = f", {stat.st_size} bytes" if is_file else ""
      results.append(f"{relative} ({kind}{size}, modified {modified})")
      if len(results) >= FIND_RESULT_CAP: return "\n".join(results + [f"<capped at {FIND_RESULT_CAP} results>"])
    stack.extend(reversed(dirs))
  if not results: return "0 matches found."
  return "\n".join(results)


def execute_find_by_name(args: dict, context: ToolContext) -> str:
  base = Path(args["SearchDirectory"])
  if not base.is_dir(): raise ToolError(f"Search directory not found: '{base}'")
  rg = _find_rg(context)
  if rg:
    result = _find_rg_files(rg, args)
    if result: return result  # empty string = rg failed, fall through to Python
  return _find_python(base, args)

# ----------------------------------------- END: find_by_name -----------------------------------------------------------------


# ----------------------------------------- START: unified search (feature flag: unified_file_search_tool) ------------------

def _search_content_rg(rg: str, query: str, base: str, args: dict) -> str:
  """Unified content search via rg: --no-ignore --hidden, hardcoded excludes, smart-case."""
  cmd = [rg, "--color=never", "--no-ignore", "--max-filesize=10M"]
  cmd.extend(_rg_common_flags())
  if args.get("CaseSensitive"): cmd.append("--case-sensitive")
  else: cmd.append("--smart-case")
  if args.get("FixedStrings"): cmd.append("--fixed-strings")
  for pattern in args.get("Includes", []): cmd.extend(("-g", pattern))
  if args.get("MaxDepth") is not None: cmd.extend(("--max-depth", str(args["MaxDepth"])))
  if args.get("MatchPerLine"):
    cmd.extend(["--no-heading", "--with-filename", "--line-number", "--max-count=200"])
    cmd.extend(["--", query, base])
    result = _run_rg(cmd)
    if result is None: return ""
    if not result.strip(): return "No matches found."
    lines = result.strip().splitlines()[:GREP_LINE_CAP]
    output = []
    for line in lines:
      parts = line.split(":", 2)
      if len(parts) >= 3: output.append(f"{parts[0]}:{parts[1]}: {parts[2].strip()[:300]}")
      else: output.append(line[:300])
    if len(lines) >= GREP_LINE_CAP: output.append(f"<result truncated at {GREP_LINE_CAP} lines>")
    return "\n".join(output)
  cmd.extend(["--count", "--", query, base])
  result = _run_rg(cmd)
  if result is None: return ""
  if not result.strip(): return "No matches found."
  output = []
  for line in result.strip().splitlines():
    parts = line.rsplit(":", 1)
    if len(parts) == 2 and parts[1].strip().isdigit():
      count = int(parts[1].strip())
      output.append(f"{parts[0]} ({count} match{'es' if count != 1 else ''})")
  return "\n".join(output) if output else "No matches found."


def _search_content_python(base: Path, query: str, args: dict) -> str:
  """Unified content search fallback: Python regex walk."""
  flags = 0 if args.get("CaseSensitive") else re.IGNORECASE
  q = re.escape(query) if args.get("FixedStrings") else query
  try:
    pattern = re.compile(q, flags)
  except re.error as error:
    raise ToolError(
      f"Invalid regex pattern '{query}' -> {error}. "
      f"Set FixedStrings=true to search for the literal text instead of treating it as a regex."
    ) from None
  match_per_line = args.get("MatchPerLine", False)
  includes = args.get("Includes", [])
  max_depth = args.get("MaxDepth")
  output, total, truncated = [], 0, False
  for candidate in _walk_files_depth(base, includes, max_depth):
    try:
      text = candidate.read_text(encoding="utf-8", errors="replace")
    except OSError:
      continue
    if "\x00" in text[:1024]: continue
    file_matches = 0
    for ln, line in enumerate(text.splitlines(), 1):
      if pattern.search(line):
        file_matches += 1
        if match_per_line:
          output.append(f"{candidate}:{ln}: {line.strip()[:300]}")
          total += 1
          if total >= GREP_LINE_CAP: truncated = True; break
    if not match_per_line and file_matches:
      output.append(f"{candidate} ({file_matches} match{'es' if file_matches != 1 else ''})")
    if truncated: break
  if not output: return "No matches found."
  if truncated: output.append(f"<result truncated at {GREP_LINE_CAP} lines>")
  return "\n".join(output)


def _search_name_rg(rg: str, query: str, base: str, args: dict) -> str:
  """Unified name search via rg --files: list files, extract dirs from paths, filter by glob."""
  type_filter = args.get("Type", "any")
  cmd = [rg, "--color=never", "--no-ignore", "--files", "--sort=path"]
  cmd.extend(_rg_common_flags())
  if args.get("MaxDepth") is not None: cmd.extend(("--max-depth", str(args["MaxDepth"])))
  cmd.append(base)
  result = _run_rg(cmd)
  if result is None: return ""
  base_path = Path(base)
  file_results, seen_dirs = [], {}  # seen_dirs: relative_str -> Path
  for line in result.strip().splitlines():
    path = Path(line.strip())
    try:
      rel = path.relative_to(base_path)
    except ValueError:
      continue
    for parent in rel.parents:
      if parent != Path("."):
        key = str(parent).replace("\\", "/")
        if key not in seen_dirs: seen_dirs[key] = base_path / parent
    if type_filter != "directory" and fnmatch.fnmatch(path.name, query):
      try:
        st = path.stat()
      except OSError:
        continue
      mod = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
      file_results.append(f"{str(rel).replace(chr(92), '/')} (file, {st.st_size} bytes, modified {mod})")
  output = []
  if type_filter != "file":
    for key in sorted(seen_dirs):
      dirname = Path(key).name
      if fnmatch.fnmatch(dirname, query):
        try:
          st = seen_dirs[key].stat()
        except OSError:
          continue
        mod = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
        output.append(f"{key} (dir, modified {mod})")
  output.extend(file_results)
  if not output: return "0 matches found."
  if len(output) > FIND_RESULT_CAP:
    output = output[:FIND_RESULT_CAP] + [f"<capped at {FIND_RESULT_CAP} results>"]
  return "\n".join(output)


def _search_name_python(base: Path, query: str, args: dict) -> str:
  """Unified name search fallback: os.scandir walk with glob matching."""
  type_filter = args.get("Type", "any")
  max_depth = args.get("MaxDepth")
  results = []
  stack = [(base, 0)]
  while stack:
    current, depth = stack.pop()
    if max_depth is not None and depth >= max_depth: continue
    try:
      entries = sorted(os.scandir(current), key=lambda e: e.name.lower())
    except OSError:
      continue
    dirs = []
    for entry in entries:
      if entry.name in IGNORED_DIRECTORIES or entry.name.endswith(".egg-info"): continue
      is_dir = entry.is_dir(follow_symlinks=False)
      is_file = entry.is_file(follow_symlinks=False)
      if is_dir: dirs.append((Path(entry.path), depth + 1))
      if type_filter == "file" and not is_file: continue
      if type_filter == "directory" and not is_dir: continue
      if not fnmatch.fnmatch(entry.name, query): continue
      try:
        st = entry.stat()
      except OSError:
        continue
      rel = str(Path(entry.path).relative_to(base)).replace("\\", "/")
      kind = "dir" if is_dir else "file"
      size = f", {st.st_size} bytes" if is_file else ""
      mod = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
      results.append(f"{rel} ({kind}{size}, modified {mod})")
      if len(results) >= FIND_RESULT_CAP:
        return "\n".join(results + [f"<capped at {FIND_RESULT_CAP} results>"])
    stack.extend(reversed(dirs))
  return "\n".join(results) if results else "0 matches found."


def _run_rg(cmd: list[str]) -> str | None:
  """Run rg subprocess, return stdout or None (signals Python fallback)."""
  try:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace")
  except subprocess.TimeoutExpired:
    return None  # fallback to Python; rg exceeded 60s timeout
  except OSError:
    return None  # rg binary not executable or missing
  if r.returncode > 1:  # exit 2 = rg error (bad regex, permission, etc.); stderr has details
    return None
  return r.stdout


def _walk_files_depth(base: Path, includes: list[str], max_depth: int | None = None):
  """Yield files under base with depth limit, skipping IGNORED_DIRECTORIES."""
  if base.is_file(): yield base; return
  stack = [(base, 0)]
  while stack:
    current, depth = stack.pop()
    if max_depth is not None and depth >= max_depth: continue
    try:
      entries = sorted(os.scandir(current), key=lambda e: e.name.lower())
    except OSError:
      continue
    dirs = []
    for entry in entries:
      if entry.is_dir(follow_symlinks=False):
        if entry.name not in IGNORED_DIRECTORIES and not entry.name.endswith(".egg-info"):
          dirs.append((Path(entry.path), depth + 1))
      elif entry.is_file(follow_symlinks=False):
        path = Path(entry.path)
        if includes:
          rel = str(path.relative_to(base)).replace("\\", "/")
          if not any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(path.name, p) for p in includes): continue
        yield path
    stack.extend(reversed(dirs))


def execute_search(args: dict, context: ToolContext) -> str:
  """Unified search: content or name mode, one exclude list, predictable behavior."""
  base = Path(args["SearchPath"])
  if not base.exists(): raise ToolError(f"Search path not found: '{base}'{path_not_found_hint(base)}")
  mode = args.get("Mode", "content")
  query = args["Query"]
  if not query or not query.strip():
    raise ToolError("Query is empty. Provide a search pattern (regex for Mode='content', glob for Mode='name').")
  rg = _find_rg(context)
  if mode == "name":
    if not base.is_dir():
      raise ToolError(
        f"SearchPath '{base}' is not a directory -> Mode='name' requires a directory. "
        f"Use Mode='content' to search inside a file, or pass a directory path."
      )
    if rg:
      result = _search_name_rg(rg, query, str(base), args)
      if result: return result
    return _search_name_python(base, query, args)
  else:
    if rg:
      result = _search_content_rg(rg, query, str(base), args)
      if result: return result
    return _search_content_python(base, query, args)

# ----------------------------------------- END: unified search ---------------------------------------------------------------
