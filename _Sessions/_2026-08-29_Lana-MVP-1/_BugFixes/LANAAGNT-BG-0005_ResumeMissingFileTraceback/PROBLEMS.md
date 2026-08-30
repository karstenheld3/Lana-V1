# PROBLEMS: LANAAGNT-BG-0005 ResumeMissingFileTraceback

**Doc ID**: LANAAGNT-BG-0005
**Goal**: Track and fix the raw traceback on --resume with a missing or unreadable session file

### LANAAGNT-BG-0005 `--resume <missing-file>` crashes with Python traceback, exit 1

**Status**: Resolved
**Reported**: 2026-08-30 05:40 (found by /bugfix discovery sweep of untested startup paths)
**Resolved**: 2026-08-30 05:50

**Verbatim reproduction**:
````
exit: 1
stderr tail: FileNotFoundError: [Errno 2] No such file or directory: 'no-such-session.jsonl'
traceback present: True
````

**Initial assessment**: `session.resume()` calls `Path(path).read_text()` unguarded; `cli.build_runtime` only catches `ConfigError`. A mistyped `--resume` path produces a raw traceback and exit 1 instead of a self-contained message naming the file and fix (IG-05) with exit code 2 (FR-14: configuration error).

**Root cause**: The resume branch validates nothing before projecting; startup-input validation was specified for config files (IS-03) but never extended to the `--resume` argument.

**Impact assessment**:
- `cli.build_runtime` resume branch (fix location - wrap in ConfigError like all other startup inputs)
- `session.resume()` untouched (library function; raising on missing file is correct there)
- Tests: `tests/test_headless.py` gains the startup-error regression; existing resume tests (TC-35, TP01-TC-02/06) unaffected (they pass real files)

**Solution**: `build_runtime` verifies the resume path is an existing file before projection; missing -> `ConfigError` naming the path and fix -> existing handler prints self-contained error, exit 2.

**Changed files**:
- `src/lana/cli.py` - resume path validation
- `tests/test_headless.py` - regression test (exit 2 + named file, no traceback)
- `backup/cli.py` - pre-fix state
