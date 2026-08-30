"""TK-010: file reading tools (IP01 TC-16..18, TC-23)."""
import pytest
from lana.tools import ToolContext, ToolError, ToolRegistry
from lana.tools.file_tools import execute_find_by_name, execute_grep_search, execute_list_dir, execute_read_file, normalize


@pytest.fixture
def context(tmp_path):
  return ToolContext(workspace=tmp_path, tool_result_max_chars=50000)


# TC-16: cat -n format, offset/limit, long-line truncation
def test_tc16_read_file_cat_n_format(tmp_path, context):
  target = tmp_path / "sample.txt"
  target.write_text("alpha\nbeta\ngamma\n" + "L" * 2500 + "\n", encoding="utf-8")
  result = execute_read_file({"file_path": str(target)}, context)
  lines = result.splitlines()
  assert lines[0] == "     1\talpha" and lines[2] == "     3\tgamma"
  assert lines[3].startswith("     4\t" + "L" * 100) and lines[3].endswith("... <line truncated>")
  assert len(lines[3]) < 2100
  partial = execute_read_file({"file_path": str(target), "offset": 2, "limit": 2}, context)
  assert partial.splitlines() == ["     2\tbeta", "     3\tgamma"]


def test_tc16b_read_file_updates_ledger_and_errors(tmp_path, context):
  target = tmp_path / "sample.txt"
  target.write_text("x", encoding="utf-8")
  execute_read_file({"file_path": str(target)}, context)
  assert normalize(target) in context.read_ledger
  with pytest.raises(ToolError): execute_read_file({"file_path": str(tmp_path / "missing.txt")}, context)


# Gap 08: image files refused with a clear message (no visual presentation in the CLI)
def test_read_file_refuses_images(tmp_path, context):
  image = tmp_path / "shot.png"
  image.write_bytes(b"\x89PNG fake")
  with pytest.raises(ToolError) as error: execute_read_file({"file_path": str(image)}, context)
  assert "image" in str(error.value) and "MVP-1" in str(error.value)
  svg = tmp_path / "diagram.svg"
  svg.write_text("<svg><text>readable</text></svg>", encoding="utf-8")
  assert "readable" in execute_read_file({"file_path": str(svg)}, context)  # SVG stays readable as text


def test_read_file_empty_reminder(tmp_path, context):
  target = tmp_path / "empty.txt"
  target.write_text("", encoding="utf-8")
  assert "system reminder" in execute_read_file({"file_path": str(target)}, context)


def test_list_dir_sizes_and_counts(tmp_path, context):
  (tmp_path / "sub").mkdir()
  (tmp_path / "sub" / "a.txt").write_text("aa", encoding="utf-8")
  (tmp_path / "sub" / "b.txt").write_text("bb", encoding="utf-8")
  (tmp_path / "root.txt").write_text("12345", encoding="utf-8")
  result = execute_list_dir({"DirectoryPath": str(tmp_path)}, context)
  assert "sub/ (2 items)" in result and "root.txt (5 bytes)" in result


# TC-17: grep_search regex + FixedStrings + Includes filtering
def test_tc17_grep_search(tmp_path, context):
  (tmp_path / "one.py").write_text("def alpha():\n  return 1\n", encoding="utf-8")
  (tmp_path / "two.md").write_text("alpha beta\nalpha gamma\n", encoding="utf-8")
  by_regex = execute_grep_search({"SearchPath": str(tmp_path), "Query": r"def \w+"}, context)
  assert "one.py (1 match)" in by_regex and "two.md" not in by_regex
  fixed = execute_grep_search({"SearchPath": str(tmp_path), "Query": "alpha", "FixedStrings": True, "Includes": ["*.md"]}, context)
  assert "two.md (2 matches)" in fixed and "one.py" not in fixed
  per_line = execute_grep_search({"SearchPath": str(tmp_path), "Query": "alpha", "MatchPerLine": True, "Includes": ["*.md"]}, context)
  assert ":1: alpha beta" in per_line and ":2: alpha gamma" in per_line
  assert "No matches" in execute_grep_search({"SearchPath": str(tmp_path), "Query": "zzz_nothing"}, context)


def test_grep_search_case_sensitivity(tmp_path, context):
  (tmp_path / "a.txt").write_text("Alpha\n", encoding="utf-8")
  assert "a.txt" in execute_grep_search({"SearchPath": str(tmp_path), "Query": "alpha"}, context)
  assert "No matches" in execute_grep_search({"SearchPath": str(tmp_path), "Query": "alpha", "CaseSensitive": True}, context)


# TC-18: find_by_name 50-result cap
def test_tc18_find_by_name_cap(tmp_path, context):
  for index in range(60): (tmp_path / f"file_{index:03d}.txt").write_text("x", encoding="utf-8")
  result = execute_find_by_name({"SearchDirectory": str(tmp_path), "Pattern": "*.txt"}, context)
  assert "<capped at 50 results>" in result
  assert result.count(".txt") == 50


def test_find_by_name_filters(tmp_path, context):
  (tmp_path / "keep.py").write_text("x", encoding="utf-8")
  (tmp_path / "skip.md").write_text("x", encoding="utf-8")
  (tmp_path / "nested").mkdir()
  (tmp_path / "nested" / "deep.py").write_text("x", encoding="utf-8")
  by_extension = execute_find_by_name({"SearchDirectory": str(tmp_path), "Pattern": "*", "Extensions": ["py"], "Type": "file"}, context)
  assert "keep.py" in by_extension and "skip.md" not in by_extension and "nested/deep.py" in by_extension
  excluded = execute_find_by_name({"SearchDirectory": str(tmp_path), "Pattern": "*.py", "Excludes": ["nested/*"]}, context)
  assert "deep.py" not in excluded and "keep.py" in excluded
  depth_limited = execute_find_by_name({"SearchDirectory": str(tmp_path), "Pattern": "*.py", "MaxDepth": 1}, context)
  assert "deep.py" not in depth_limited


# Improve run 1 (C1): grep_search and find_by_name skip noise directories (rg/fd parity per tool descriptions)
def test_search_tools_skip_ignored_directories(tmp_path, context):
  (tmp_path / "src").mkdir()
  (tmp_path / "src" / "real.py").write_text("needle here\n", encoding="utf-8")
  for noise_dir in (".git", "node_modules", "__pycache__", ".lana", ".lana-data"):
    (tmp_path / noise_dir / "sub").mkdir(parents=True)
    (tmp_path / noise_dir / "sub" / "noise.py").write_text("needle here\n", encoding="utf-8")
  grep_result = execute_grep_search({"SearchPath": str(tmp_path), "Query": "needle"}, context)
  assert "real.py" in grep_result and "node_modules" not in grep_result and ".git" not in grep_result
  find_result = execute_find_by_name({"SearchDirectory": str(tmp_path), "Pattern": "*.py"}, context)
  assert "src/real.py" in find_result and "noise.py" not in find_result
  direct = execute_grep_search({"SearchPath": str(tmp_path / "node_modules"), "Query": "needle"}, context)
  assert "noise.py" in direct  # explicit search INSIDE an ignored dir still works (base is the ignored dir itself)


# TC-23: tool result cap via registry (EC-04) - exact marker length
def test_tc23_result_cap_marker(tmp_path):
  registry = ToolRegistry(os_name="windows", shell="pwsh")
  registry.register("read_file", execute_read_file)
  small_context = ToolContext(workspace=tmp_path, tool_result_max_chars=200)
  target = tmp_path / "big.txt"
  target.write_text("\n".join(f"line {index}" for index in range(200)), encoding="utf-8")
  result = registry.dispatch("read_file", {"file_path": str(target)}, small_context)
  marker_start = result.index("<truncated ")
  removed = int(result[marker_start:].split()[1])
  assert len(result) == 200 + len(f"\n<truncated {removed} chars>")
