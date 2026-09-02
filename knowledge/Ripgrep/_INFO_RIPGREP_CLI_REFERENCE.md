# INFO: Ripgrep CLI Reference for Agent Tool Integration

**Doc ID**: RGREPREF-IN01
**Goal**: Document ripgrep (rg) flags and behaviors relevant to agent file search tools (grep_search, find_by_name)
**Timeline**: Created 2026-09-02, Updated 0 times

## Summary

- [ripgrep](https://github.com/BurntSushi/ripgrep) 15.2.0 respects `.gitignore` by default, skips hidden files and binary files [VERIFIED]
- `--no-ignore` disables ALL ignore-file filtering (.gitignore, .rgignore, .ignore); `--no-ignore-vcs` disables only VCS ignores [VERIFIED]
- `--hidden` (`-.`) searches files and directories starting with `.`; without it, `.gitignore`, `.env`, `.devin/` are invisible [VERIFIED]
- `--smart-case` (`-S`) is case-insensitive when pattern is all lowercase, case-sensitive when pattern contains uppercase [VERIFIED]
- `--files` lists files that WOULD be searched, never directories; directory discovery requires a different approach [VERIFIED]
- `--count` (`-c`) outputs `path:count` per file; single invocation replaces file-list + count double-pass [VERIFIED]
- `--max-filesize=NUM+SUFFIX` skips files exceeding size limit (e.g., `10M`); useful for agent searches [VERIFIED]
- `--no-messages` suppresses file-open error messages (permission denied, broken symlinks) [VERIFIED]
- `--max-depth=NUM` (`-d`) limits directory traversal depth; value 0 = only explicit paths, 1 = direct children [VERIFIED]
- Exit codes: 0 = match found, 1 = no match, 2 = error; code 1 is NOT an error [VERIFIED]

## Table of Contents

1. [Core Usage](#1-core-usage)
2. [Ignore and Visibility Control](#2-ignore-and-visibility-control)
3. [Search Behavior](#3-search-behavior)
4. [Output Modes](#4-output-modes)
5. [Filter Options](#5-filter-options)
6. [Performance](#6-performance)
7. [File Listing Mode](#7-file-listing-mode)
8. [Agent Integration Patterns](#8-agent-integration-patterns)
9. [Next Steps](#9-next-steps)
10. [Sources](#10-sources)
11. [Document History](#11-document-history)

## 1. Core Usage

```
rg [OPTIONS] PATTERN [PATH ...]
rg [OPTIONS] --files [PATH ...]
```

- PATTERN is a regex by default; `-F`/`--fixed-strings` treats it as literal
- Multiple patterns via `-e PATTERN` (OR semantics: line matches if any pattern matches)
- PATH can be file or directory; directories are searched recursively
- File paths specified on the command line override glob and ignore rules

### 1.1 Exit Codes

- **0**: At least one match found
- **1**: No match found (not an error)
- **2**: Error occurred (bad regex, file not found, etc.)

Agent implication: `returncode == 1` means "no matches" and should produce `"No matches found."`, not trigger a fallback.

## 2. Ignore and Visibility Control

Ripgrep's default filtering is aggressive. Understanding the layered ignore system is critical for agent tools.

### 2.1 Default Behavior (No Flags)

- Respects `.gitignore`, `.ignore`, `.rgignore`, and global gitignore (`core.excludesFile`)
- Skips hidden files/directories (names starting with `.`)
- Skips binary files (detected by NUL byte heuristic)
- Requires a `.git` directory to activate gitignore rules (see `--no-require-git`)

### 2.2 Ignore Bypass Flags (Most to Least Aggressive)

- **`--no-ignore`**: Disables ALL ignore files (`.gitignore`, `.ignore`, `.rgignore`, global). Equivalent to `-u` (single unrestricted)
- **`--no-ignore-vcs`**: Disables only `.gitignore` and global git ignores. Still respects `.ignore` and `.rgignore`
- **`--no-ignore-dot`**: Disables only `.ignore` and `.rgignore`. Still respects `.gitignore`
- **`--no-ignore-parent`**: Stops ascending to parent directories for ignore files
- **`--no-ignore-global`**: Disables global gitignore (`core.excludesFile`)

### 2.3 Hidden File Flag

- **`--hidden`** (`-.`): Searches hidden files and directories (names starting with `.`)
- Without `--hidden`, files like `.gitignore`, `.env`, `.devin/`, `.lana/` are invisible
- `--hidden` does NOT imply `--no-ignore`; both are independent axes
- `--hidden` will include `.git/` unless excluded via `-g "!.git/"`

### 2.4 Unrestricted Mode

- `-u` = `--no-ignore`
- `-uu` = `--no-ignore` + `--hidden`
- `-uuu` = `--no-ignore` + `--hidden` + `--binary`

### 2.5 Agent Decision Matrix

```
Scenario                           Flags needed
─────────────────────────────────  ──────────────────────────────
Search within current workspace    (default) + --hidden
Search external workspace          --no-ignore + --hidden
Find gitignored directories        --no-ignore + --hidden
List ALL files including hidden    --files --no-ignore --hidden
```

Always pair `--hidden` with explicit glob excludes for `.git/`, `node_modules/`, etc. to avoid noise.

## 3. Search Behavior

### 3.1 Case Sensitivity

- **`-s`/`--case-sensitive`**: Default. Exact case matching
- **`-i`/`--ignore-case`**: All patterns case-insensitive
- **`-S`/`--smart-case`**: Case-insensitive when pattern is all lowercase; case-sensitive when pattern contains uppercase. Requires at least one literal character in pattern

Agent recommendation: Use `--smart-case` as default. Matches user intent (lowercase = flexible, uppercase = precise).

### 3.2 Pattern Modes

- Default: regex (Rust regex engine)
- **`-F`/`--fixed-strings`**: Literal match, no regex metacharacters interpreted
- **`-w`/`--word-regexp`**: Match surrounded by word boundaries (equivalent to `\b{start}PATTERN\b{end}`)
- **`-x`/`--line-regexp`**: Match entire line (equivalent to `^PATTERN$`)
- **`-P`/`--pcre2`**: Use PCRE2 engine (look-around, backreferences). Optional feature, may not be compiled in

### 3.3 Multiline

- **`-U`/`--multiline`**: Allows patterns to match across line boundaries (`\n` becomes matchable)
- Requires file to be loaded into memory (slower, more memory)
- Not needed for typical agent searches

### 3.4 Encoding

- **`-E`/`--encoding=ENCODING`**: Default `auto` (detects UTF-8/UTF-16 BOM). Use `none` to search raw bytes

## 4. Output Modes

### 4.1 Default (Line Matches)

```
path:line_number:matched_line
```

Relevant flags:
- **`--no-heading`**: Print file path as prefix on each line (not grouped above)
- **`-H`/`--with-filename`**: Force file path in output (default when multiple files)
- **`-n`/`--line-number`**: Show line numbers (default when tty)
- **`--column`**: Show column numbers (1-based)
- **`-m NUM`/`--max-count=NUM`**: Limit matches per file

### 4.2 Count Mode

- **`-c`/`--count`**: Output `path:count` (lines matching per file). Suppress match content
- **`--count-matches`**: Count individual matches, not matching lines
- **`--include-zero`**: Print files with zero matches (useful with `--count`)

Agent optimization: For file-list-with-counts, use `--count` directly instead of a two-pass approach.

### 4.3 File List Mode

- **`-l`/`--files-with-matches`**: Print only paths with at least one match. Stops searching each file at first match (faster than `--count`)
- **`--files-without-match`**: Print paths with zero matches

### 4.4 Context Lines

- **`-A NUM`/`--after-context`**: Show NUM lines after match
- **`-B NUM`/`--before-context`**: Show NUM lines before match
- **`-C NUM`/`--context`**: Show NUM lines before and after
- **`--context-separator`**: String between non-contiguous context blocks (default: `--`)

### 4.5 JSON Output

- **`--json`**: Emit JSON Lines (message types: begin, end, match, context, summary)
- Cannot combine with `--count`, `--files`, `-l`
- Implicitly enables `--stats`

### 4.6 Sorting

- **`--sort=path`**: Sort results by file path (ascending). Forces single-threaded
- **`--sort=modified`**: Sort by last modified time
- **`--sortr=SORTBY`**: Reverse (descending) sort

Agent note: `--sort=path` is used for `find_by_name` deterministic output. Accept the single-thread tradeoff for reproducible results.

### 4.7 Line Truncation

- **`-M NUM`/`--max-columns=NUM`**: Omit lines longer than NUM bytes, print match count instead
- **`--max-columns-preview`**: Show a preview (up to limit) instead of omitting entirely

## 5. Filter Options

### 5.1 Glob Filtering

- **`-g GLOB`/`--glob=GLOB`**: Include or exclude files/directories. Overrides ignore logic
- Precede with `!` to exclude: `-g "!*.log"`
- Glob syntax matches `.gitignore` rules
- Supports alternatives: `-g "ab{c,d}*"` = `-g "abc*" -g "abd*"`
- Later `-g` flags take precedence over earlier ones

Agent pattern: Use `-g "!.git/" -g "!node_modules/"` etc. to exclude noise directories when `--no-ignore` is active.

### 5.2 Depth Limiting

- **`-d NUM`/`--max-depth=NUM`**: Limit directory traversal depth
- 0 = only explicit paths (no recursion)
- 1 = direct children only

### 5.3 File Size Limiting

- **`--max-filesize=NUM+SUFFIX`**: Skip files larger than limit
- Suffixes: K (kilobytes), M (megabytes), G (gigabytes)
- Example: `--max-filesize=10M`

Agent recommendation: Use `--max-filesize=10M` for grep_search to avoid scanning large data files, binaries, or logs.

### 5.4 File Type Filtering

- **`-t TYPE`/`--type=TYPE`**: Only search files of TYPE (e.g., `-t py` for Python)
- **`-T TYPE`/`--type-not=TYPE`**: Exclude files of TYPE
- **`--type-list`**: Show all known types and their globs
- **`--type-add=TYPESPEC`**: Add custom type (e.g., `--type-add "config:*.toml"`)

### 5.5 Binary File Handling

- Default: stop searching file at first NUL byte
- **`--binary`**: Continue searching past NUL bytes, stop at first match after NUL
- **`-a`/`--text`**: Treat binary as text (may print escape codes)

### 5.6 Symlink Following

- **`-L`/`--follow`**: Follow symlinks during traversal. Default: do not follow. Detects loops.

## 6. Performance

### 6.1 Threading

- **`-j NUM`/`--threads=NUM`**: Set thread count. Default 0 = auto (heuristic)
- Sorting (`--sort`, `--sortr`) forces single-threaded mode
- For reproducible output order, use `--sort=path` (accepts the single-thread cost)

### 6.2 Memory Mapping

- **`--mmap`**: Use memory maps when possible (default: auto)
- **`--no-mmap`**: Disable memory maps (useful if files are truncated during search)

### 6.3 Practical Performance Notes

- rg is faster than grep, find, and Python `os.walk` for file traversal and content search
- Parallel by default; sorting disables parallelism
- `--max-filesize` prevents slow scans of huge files
- `-l`/`--files-with-matches` is faster than `-c`/`--count` (stops at first match per file)

## 7. File Listing Mode

`rg --files [PATH ...]` lists files that WOULD be searched, without performing a search.

Key behaviors:
- **Only lists files**, never directories. Directory discovery must use a different tool (`os.scandir`, `list_dir`)
- Respects the same ignore/hidden/glob rules as search mode
- Accepts `--max-depth`, `--sort`, `--type`, `--glob` flags
- Does NOT accept PATTERN (no content filtering)
- With `--no-ignore --hidden`, lists all non-binary files including hidden and gitignored ones
- `-q`/`--quiet` with `--files` stops after finding the first file matching filters

Agent implication: `rg --files` is only useful for `Type="file"` searches. For `Type="directory"` or `Type="any"`, fall through to `os.scandir`-based Python implementation.

## 8. Agent Integration Patterns

### 8.1 grep_search (Content Search)

```
rg --color=never --max-filesize=10M --hidden --no-messages \
   --smart-case \
   -g "!.git/" -g "!node_modules/" -g "!__pycache__/" ... \
   [--no-heading --with-filename --line-number --max-count=200] \
   -- PATTERN PATH
```

- Smart-case for natural user intent
- `--max-filesize=10M` prevents scanning huge files
- `--hidden` finds `.gitignore`, `.env`, `.devin/` content
- `--no-messages` suppresses permission errors
- Glob excludes for IGNORED_DIRECTORIES filter noise
- MatchPerLine mode: add `--no-heading --with-filename --line-number --max-count=200`
- File-count mode: add `--count` (single invocation, no double-pass)

### 8.2 find_by_name (File Listing)

```
rg --files --color=never --sort=path --no-ignore --hidden --no-messages \
   -g "!.git/" -g "!node_modules/" ... \
   [-g "PATTERN"] [--max-depth=N] \
   PATH
```

- `--no-ignore` required: agent needs to find ALL files regardless of `.gitignore` rules
- `--sort=path` for deterministic output (accepts single-thread cost)
- Only use for `Type="file"` searches
- `Type="directory"` and `Type="any"` must fall through to Python `os.scandir`

### 8.3 Cross-Workspace Search

When searching paths outside the current workspace (e.g., session loading from a different workspace):

- grep_search: default behavior (respects target workspace's `.gitignore`) usually works because content matches are file-internal
- find_by_name: `--no-ignore` is essential because target workspace's `.gitignore` may exclude session directories (`_Sessions/`, `dist/`)

## 9. Next Steps

1. Verify rg integration in `file_tools.py` matches patterns documented in Section 8
2. Consider exposing `--type` filtering in the `grep_search` tool schema (currently agent uses glob includes instead)
3. Evaluate adding `--max-columns=2000` to match Lana's `MAX_LINE_CHARS` truncation

## 10. Sources

**Primary Sources:**
- `RGREPREF-IN01-SC-RG-HELP`: `rg.exe --help` (v15.2.0, 1622 lines) - Complete CLI reference including all flags, behaviors, and exit codes [VERIFIED]
- `RGREPREF-IN01-SC-RG-GHUB`: [https://github.com/BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) - Project repository, README, and user guide [VERIFIED]

**Code Sources:**
- `RGREPREF-IN01-SC-LANA-FTLS`: `src/lana/tools/file_tools.py` - Current rg integration implementation (grep_search, find_by_name) [VERIFIED]

## 11. Document History

**[2026-09-02 00:21]**
- Initial reference document created from `rg.exe --help` (v15.2.0)
- Organized into 8 sections covering usage, filtering, output, performance, and agent integration patterns
- Documented agent decision matrix for ignore/visibility flag combinations
