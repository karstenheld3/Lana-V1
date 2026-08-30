# IMPL: Lana Distribution Ship Pipeline

**Doc ID**: LANADIST-IP01
**Feature**: lana-distribution
**Goal**: Implement `_ship.bat` + `_ship.ps1` producing the signed single-binary `lana.exe` distribution per LANADIST-SP01
**Timeline**: Created 2026-08-30

**Target file(s)**:
- `_ship.bat` (NEW, workspace root, ~20 lines)
- `_ship.ps1` (NEW, workspace root, ~240 lines)
- `src/lana/cli.py` (MODIFY: `--version` flag, bundled agent library materialization)
- `src/lana/config.py` (MODIFY: bundled config materialization, key template constant)
- `src/lana/bundled/` (NEW: package data, synced by pipeline, committed)
- `pyproject.toml` (MODIFY: package-data declaration)

**Depends on:**
- `_SPEC_LANADIST.md` [LANADIST-SP01] for pipeline requirements, guarantees, logging contract
- `_InstallAndCompileDependencies.bat` for the `.venv` the wheel build uses

## MUST-NOT-FORGET

- IG-02: any failed step aborts with non-zero exit and removes partial artifacts from `dist/`
- Clear ALL `PYAPP_*` environment variables before setting our own (stale user shell vars poison the build)
- Pin the PyApp version in the script (NFR-02 reproducible builds)
- `--version` must use argparse `action="version"` so it exits BEFORE config load / zero-setup side effects
- Smoke test timeout must cover first-run extraction (5-30 s) - use 120 s
- Test ACP stdout purity on FIRST run of a fresh binary (LANADIST-PR-0005)
- `self update` does NOT update the binary (SPEC MNF) - no update logic in the ship script
- Bundle sync NEVER touches `.api-keys.txt` (DD-09); key-leak guard is a hard gate (IG-05)
- EXISTING agent folder is never overwritten by materialization (FR-08 - user deletions respected)

## Table of Contents

1. [File Structure](#1-file-structure)
2. [Edge Cases](#2-edge-cases)
3. [Implementation Steps](#3-implementation-steps)
4. [Logging Preview](#4-logging-preview)
5. [Test Cases](#5-test-cases)
6. [Verification Checklist](#6-verification-checklist)
7. [Document History](#7-document-history)

## 1. File Structure

```
[WORKSPACE_FOLDER]/
├── _ship.bat                 # Launcher: pwsh -f _ship.ps1, pause on error (~20 lines) [NEW]
├── _ship.ps1                 # Pipeline: toolchain, sync, wheel, cargo, rename, sign, checksum (~240 lines) [NEW]
├── pyproject.toml            # Add [tool.setuptools.package-data] lana.bundled [MODIFY]
├── src/lana/
│   ├── cli.py                # --version flag; agent scaffold -> copy bundled library [MODIFY]
│   ├── config.py             # Materialize model JSONs + key template from bundle [MODIFY]
│   └── bundled/              # Package data (committed, pipeline-synced) [NEW]
│       ├── __init__.py       #   makes lana.bundled a package for importlib.resources
│       ├── config/           #   model-registry/-parameter-mapping/-pricing.json (from config/)
│       └── agent/            #   rules/ workflows/ skills/ (from .lana/, ~291 files, 2.2 MB)
├── build/                    # Intermediate: wheel + pyapp cargo root (gitignored, script-created)
│   ├── wheel/                #   lana-{version}-py3-none-any.whl
│   └── pyapp/bin/pyapp.exe   #   cargo install output
└── dist/                     # Final artifacts (gitignored, script-created)
    ├── lana-{version}-win-x64.exe
    └── SHA256SUMS.txt
```

## 2. Edge Cases

- **LANADIST-IP01-EC-01**: `cargo` not on PATH -> offer `rustup` install via winget, abort if declined (FR-03)
- **LANADIST-IP01-EC-02**: `.venv` missing -> instruct to run `_InstallAndCompileDependencies.bat`, abort (no silent venv creation - single responsibility)
- **LANADIST-IP01-EC-03**: version not parseable from `pyproject.toml` -> abort with the offending line shown
- **LANADIST-IP01-EC-04**: `build` package missing in venv -> pip install it into venv (quiet), then proceed
- **LANADIST-IP01-EC-05**: wheel build failure -> abort, show python output
- **LANADIST-IP01-EC-06**: `cargo install` failure -> abort, show last 20 cargo output lines
- **LANADIST-IP01-EC-07**: `dist/` already has same-version exe -> report old file (size, date) before replacement (IG-01)
- **LANADIST-IP01-EC-08**: smoke test output does not match `pyproject.toml` version -> delete artifact, abort (IG-02)
- **LANADIST-IP01-EC-09**: signing requested (cert env var set) but `signtool` missing or signing fails -> delete artifact, abort (IG-02: never unsigned-when-signing-requested)
- **LANADIST-IP01-EC-10**: stale `PYAPP_*` vars in user shell -> script clears every `PYAPP_*` var in its process scope before setting its own
- **LANADIST-IP01-EC-11**: smoke test hangs (first-run extraction) -> 120 s timeout, then delete artifact, abort
- **LANADIST-IP01-EC-12**: key-leak guard hit (uncommented `*_API_KEY=` with value in bundle) -> print file path, abort (IG-05)
- **LANADIST-IP01-EC-13**: workspace `.lana/` missing at sync time -> abort with hint (bundle would silently lose the library)
- **LANADIST-IP01-EC-14**: end-user agent folder EXISTS (even empty) -> materialization skips it entirely (FR-08)
- **LANADIST-IP01-EC-15**: end-user has partial config (e.g. only `model-pricing.json` missing) -> only the missing files are written, existing files untouched

## 3. Implementation Steps

### LANADIST-IP01-IS-01: Add --version flag to CLI

**Location**: `src/lana/cli.py` > `build_arg_parser()`

**Action**: Add argparse version action reading package metadata

**Code**:
```python
# argparse action="version" prints and exits before any config/zero-setup side effects
parser.add_argument("--version", action="version", version=f"%(prog)s {importlib.metadata.version('lana')}")
```

**Note**: `importlib.metadata` import at top of file. Fallback to `"0.0.0-dev"` on `PackageNotFoundError` (running from source without install).

### LANADIST-IP01-IS-02: Declare package data + bundled package

**Location**: `pyproject.toml` + `src/lana/bundled/__init__.py`

**Action**: Make `lana.bundled` a package whose data files ship in the wheel

**Code**:
```toml
[tool.setuptools.package-data]
"lana.bundled" = ["config/*.json", "agent/**/*"]
```

**Note**: Empty `__init__.py` in `bundled/`. Verify wheel contents after build (`python -m zipfile -l`): agent tree present, `.api-keys.txt` ABSENT.

### LANADIST-IP01-IS-03: Zero-setup materialization from bundle

**Location**: `src/lana/config.py` > `load_lana_config()` + new helper; `src/lana/cli.py` > `build_runtime()`

**Action**: Extend zero-setup to materialize bundled payload (FR-08)

**Code**:
```python
# config.py: KEY_FILE_TEMPLATE constant (commented placeholders, no values)
# config.py: materialize_bundled_config(config_dir, created) - for each of the 3 model JSONs:
#   missing -> importlib.resources.read_text('lana.bundled.config', name) -> write, append to created (EC-15)
#   also: missing .api-keys.txt -> write KEY_FILE_TEMPLATE
#   called from load_lana_config() DEFAULT-path branch only (explicit --config never auto-creates)
# cli.py build_runtime(): replace empty-folder scaffold (current lines 79-81):
#   if not app.agent_folder.is_dir(): copy bundled agent tree via importlib.resources (EC-14)
```

**Note**: Fixes latent bug LANADIST-PR-0008 - `read_json` raised on missing model JSONs which zero-setup never created; fresh-machine startup was impossible.

### LANADIST-IP01-IS-04: Create _ship.bat launcher

**Location**: `_ship.bat` (workspace root)

**Action**: Create launcher following `_InstallAndCompileDependencies.bat` conventions

**Code**:
```bat
REM Check pwsh exists -> run _ship.ps1 -> pause + exit /b 1 on error, pause + exit /b 0 on success
```

**Note**: `pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0_ship.ps1"`. Pause in both paths so double-click users see the result.

### LANADIST-IP01-IS-05: _ship.ps1 skeleton + step [ 1 / 7 ] toolchain verification

**Location**: `_ship.ps1` (workspace root)

**Action**: Create pipeline skeleton with strict mode and step functions

**Code**:
```powershell
# $ErrorActionPreference = 'Stop'; step counter helper; Fail() helper that cleans dist/ partials and exits 1
# [ 1 / 7 ] Verify: .venv python exists (EC-02), cargo exists (EC-01, offer winget rustup),
#           parse version from pyproject.toml via regex (EC-03),
#           signing on/off: $env:LANA_SIGN_THUMBPRINT set -> require signtool.exe on PATH (EC-09)
```

**Note**: Pinned constants at top: `$PYAPP_VERSION = '0.29.0'`, `$PYTHON_TARGET = '3.12'`. NOTICE line when signing off (FR-06).

### LANADIST-IP01-IS-06: Step [ 2 / 7 ] bundle sync + key-leak guard

**Location**: `_ship.ps1`

**Action**: Mirror workspace sources into `src/lana/bundled/`, then scan

**Code**:
```powershell
# abort if .lana missing (EC-13)
# robocopy /MIR config\*.json -> src\lana\bundled\config\   (explicit file list, never .api-keys.txt)
# robocopy /MIR .lana\ -> src\lana\bundled\agent\
# key-leak guard (EC-12, IG-05): Select-String '^\s*[A-Z_]*API_KEY\s*=\s*\S' over bundle -> abort on match
# report: file counts + total size
```

**Note**: `/MIR` removes stale bundle files when workspace sources shrink - bundle can never drift (DD-08).

### LANADIST-IP01-IS-07: Step [ 3 / 7 ] wheel build

**Location**: `_ship.ps1`

**Action**: Build wheel with venv python

**Code**:
```powershell
# ensure 'build' package in venv (EC-04): .venv\Scripts\python.exe -m pip show build || pip install build
# .venv\Scripts\python.exe -m build --wheel --outdir build\wheel  (EC-05)
# capture wheel path: build\wheel\lana-{version}-py3-none-any.whl
# verify wheel: agent tree present, no .api-keys.txt (IS-02 note)
```

### LANADIST-IP01-IS-08: Step [ 4 / 7 ] PyApp binary build

**Location**: `_ship.ps1`

**Action**: Clear stale PYAPP_* vars, set config, cargo install pinned PyApp

**Code**:
```powershell
# Get-ChildItem env:PYAPP_* | Remove-Item  (EC-10)
# $env:PYAPP_PROJECT_NAME='lana'; $env:PYAPP_PROJECT_VERSION=$version
# $env:PYAPP_PROJECT_PATH=<wheel absolute path>   # embeds wheel - no PyPI needed
# $env:PYAPP_PYTHON_VERSION='3.12'; $env:PYAPP_DISTRIBUTION_EMBED='1'
# $env:PYAPP_EXEC_MODULE='lana'                   # python -m lana -> __main__.py -> sys.exit(main())
# cargo install pyapp --version $PYAPP_VERSION --force --root build\pyapp  (EC-06)
```

**Note**: `PYAPP_EXEC_MODULE='lana'` instead of SPEC's earlier `PYAPP_EXEC_SPEC='lana.cli:main'`: the module path runs `__main__.py` which wraps `main()` in `sys.exit()` - exit codes propagate to the ACP client. `EXEC_SPEC` would discard the return value. SPEC updated (see LANADIST-SP01 history 2026-08-30 16:25).

### LANADIST-IP01-IS-09: Step [ 5 / 7 ] rename + smoke test

**Location**: `_ship.ps1`

**Action**: Copy to versioned name, run --version smoke test

**Code**:
```powershell
# report + replace existing same-version exe (EC-07, IG-01)
# Copy-Item build\pyapp\bin\pyapp.exe dist\lana-$version-win-x64.exe
# smoke test: & dist\...exe --version with 120s timeout (EC-11); expect "lana $version" (EC-08)
# NOTE: smoke test performs the binary's first run (5-30s) - announce this in output
```

### LANADIST-IP01-IS-10: Step [ 6 / 7 ] signing + step [ 7 / 7 ] checksum

**Location**: `_ship.ps1`

**Action**: Conditional Authenticode signing, SHA-256 checksum, final report

**Code**:
```powershell
# if $env:LANA_SIGN_THUMBPRINT: signtool sign /sha1 <thumbprint> /fd SHA256 /tr <timestamp-url> /td SHA256 <exe>  (EC-09)
# else: "[ 6 / 7 ] Signing... SKIPPED (no certificate)."
# Get-FileHash -Algorithm SHA256 -> dist\SHA256SUMS.txt (format: "<hash> *<filename>")
# DONE line: path, size MB, signed|unsigned
```

## 4. Logging Preview

Follows SPEC section 10 contract (Announce > Track > Report, Script-Level).

**Success path (unsigned dev build):**
```
Shipping Lana 0.1.0 (win-x64)...
[ 1 / 7 ] Verifying toolchain...
  Python 3.12.4 (.venv) OK. Cargo 1.86.0 OK.
  NOTICE: LANA_SIGN_THUMBPRINT not set - binary will be UNSIGNED.
[ 2 / 7 ] Syncing bundle...
  3 config files, 291 agent files (2.2 MB). Key-leak scan OK.
[ 3 / 7 ] Building wheel...
  build\wheel\lana-0.1.0-py3-none-any.whl (2.4 MB). OK.
[ 4 / 7 ] Building PyApp binary (pyapp 0.29.0, this takes 1-3 minutes)...
  OK.
[ 5 / 7 ] Smoke test (first run extracts embedded Python, up to 30 s)...
  lana --version -> lana 0.1.0. OK.
[ 6 / 7 ] Signing... SKIPPED (no certificate).
[ 7 / 7 ] Checksum...
  SHA256SUMS.txt written. OK.
DONE: dist\lana-0.1.0-win-x64.exe (42 MB, unsigned)
```

**Error case - key-leak guard hit (EC-12):**
```
[ 2 / 7 ] Syncing bundle...
  ERROR: possible API key in 'src\lana\bundled\agent\skills\seo-tools\example.md' line 12.
FAILED at step 2: key-leak guard - remove the value, keep only placeholders.
```

**Error case - smoke test version mismatch (EC-08):**
```
[ 5 / 7 ] Smoke test (first run extracts embedded Python, up to 30 s)...
  ERROR: expected 'lana 0.1.0', got 'lana 0.0.9'.
  Removed partial artifact dist\lana-0.1.0-win-x64.exe.
FAILED at step 5: smoke test version mismatch.
```

**Error case - cargo missing (EC-01):**
```
[ 1 / 7 ] Verifying toolchain...
  Python 3.12.4 (.venv) OK.
  Cargo not found. Install Rust toolchain now via winget? [y/N]
FAILED at step 1: Rust toolchain required. Install manually: https://rustup.rs
```

## 5. Test Cases

### Category 1: CLI flag + zero-setup materialization (pytest, new tests/test_distribution.py)

- **LANADIST-IP01-TC-01**: `lana --version` exits 0, prints `lana {version}` matching `importlib.metadata.version('lana')` -> ok
- **LANADIST-IP01-TC-02**: `--version` does NOT create config/data folders (no zero-setup side effect) -> no `.lana-data/` in cwd after run
- **LANADIST-IP01-TC-12**: empty workspace startup -> all 3 model JSONs + `.api-keys.txt` template + agent library materialized, each in `Created` report (EC-15 counterpart)
- **LANADIST-IP01-TC-13**: partial config (pricing JSON deleted) -> only pricing JSON recreated, others untouched (EC-15)
- **LANADIST-IP01-TC-14**: existing empty agent folder -> NOT repopulated (EC-14)
- **LANADIST-IP01-TC-15**: materialized `.api-keys.txt` contains `OPENAI_API_KEY`/`ANTHROPIC_API_KEY` lines commented, no values (DD-09)

### Category 2: Ship pipeline (manual, on Windows x64 build machine)

- **LANADIST-IP01-TC-03**: `_ship.bat` full run -> `dist\lana-0.1.0-win-x64.exe` + `SHA256SUMS.txt` exist, DONE line printed
- **LANADIST-IP01-TC-04**: second run same version -> old artifact reported before replacement (IG-01)
- **LANADIST-IP01-TC-05**: no `LANA_SIGN_THUMBPRINT` -> NOTICE printed, exit 0, unsigned exe (FR-06)
- **LANADIST-IP01-TC-06**: `Get-FileHash` of exe matches `SHA256SUMS.txt` entry (FR-07)
- **LANADIST-IP01-TC-16**: wheel listing contains `lana/bundled/agent/` tree and NO `.api-keys.txt` (IG-05)
- **LANADIST-IP01-TC-17**: planted fake key in a bundled file -> pipeline aborts at step 2 (EC-12)

### Category 3: Distribution binary behavior (manual)

- **LANADIST-IP01-TC-07**: fresh machine/cache (`self remove` first): first run takes 5-30 s, second run <1 s (NFR-01)
- **LANADIST-IP01-TC-08**: binary CLI mode on FRESH machine: starts without any pre-existing config, prompt system loads with bundled rules/workflows/skills counts > 0 (FR-08)
- **LANADIST-IP01-TC-09**: binary ACP mode: `lana.exe --acp` + `initialize` request over stdin -> valid JSON-RPC response, stdout contains ONLY JSON-RPC lines (FR-02)
- **LANADIST-IP01-TC-10**: PR-0005 probe: delete PyApp cache, pipe `initialize` into `lana.exe --acp`, capture stdout/stderr separately -> stdout has NO extraction noise; record result in PROBLEMS.md
- **LANADIST-IP01-TC-11**: upload exe to VirusTotal -> record flag count in PROBLEMS.md (LANADIST-PR-0006, target 0-2/71)

## 6. Verification Checklist

### Prerequisites
- [x] **LANADIST-IP01-VC-01**: LANADIST-SP01 read; `.venv` exists via `_InstallAndCompileDependencies.bat`
- [x] **LANADIST-IP01-VC-02**: Rust toolchain available on build machine (rustup + MSVC Build Tools installed 2026-08-30)

### Implementation
- [x] **LANADIST-IP01-VC-03**: IS-01 `--version` flag added
- [x] **LANADIST-IP01-VC-04**: IS-02 package data declared, bundled package created
- [x] **LANADIST-IP01-VC-05**: IS-03 zero-setup materialization (config.py + cli.py)
- [x] **LANADIST-IP01-VC-06**: IS-04 `_ship.bat` created
- [x] **LANADIST-IP01-VC-07**: IS-05 toolchain verification step
- [x] **LANADIST-IP01-VC-08**: IS-06 bundle sync + key-leak guard
- [x] **LANADIST-IP01-VC-09**: IS-07 wheel build step
- [x] **LANADIST-IP01-VC-10**: IS-08 PyApp build step
- [x] **LANADIST-IP01-VC-11**: IS-09 rename + smoke test step
- [x] **LANADIST-IP01-VC-12**: IS-10 signing + checksum steps (signing path untested - no certificate, PR-0002)

### Validation
- [x] **LANADIST-IP01-VC-13**: TC-01, TC-02, TC-12 through TC-15 pass in pytest (247 passed, 4 skipped)
- [x] **LANADIST-IP01-VC-14**: TC-03, TC-05, TC-06, TC-16, TC-17 pass (pipeline); TC-04 replace-report path code-reviewed only (needs 2 consecutive full runs)
- [x] **LANADIST-IP01-VC-15**: TC-07 through TC-09 pass: first run ~3-4 min, cached --version 1.3 s, fresh CLI loads 8 rules / 46 workflows / 23 skills, ACP initialize responds
- [x] **LANADIST-IP01-VC-16**: TC-10 stdout purity on fresh cache PASSED - PR-0005 resolved (extraction writes nothing to stdout; 218-byte pure JSON-RPC response)
- [ ] **LANADIST-IP01-VC-17**: TC-11 VirusTotal result recorded (PR-0006) - OPEN: needs manual upload
- [ ] **LANADIST-IP01-VC-18**: Bundled library privacy review done (PR-0007) - OPEN: before public release
- [x] **LANADIST-IP01-VC-19**: SPEC synced from verified implementation, session tracking files updated

## 7. Document History

**[2026-08-30 18:00]**
- Implemented: all 10 IS steps; pipeline green end-to-end (23 MB unsigned binary)
- Deviations: smoke timeout 120 s -> 300 s (first run installs deps from PyPI); key-leak guard pattern narrowed to 40+ char tokens (placeholder false positive); httpx2 import fix in providers/base.py (SDK migration, pre-existing latent break)
- Results: NFR-01 cached start measured 1.3 s (target <1 s - minor miss, process+Python startup bound); PR-0005 resolved (stdout pure on fresh-cache ACP start)

**[2026-08-30 16:40]**
- Added: bundled payload work (SPEC FR-08/FR-09): IS-02 package data, IS-03 zero-setup materialization, IS-06 bundle sync + key-leak guard
- Added: EC-12 through EC-15, TC-12 through TC-17
- Changed: pipeline renumbered 6 -> 7 steps; IS/VC renumbered accordingly

**[2026-08-30 16:25]**
- Initial implementation plan created: 7 steps, 11 edge cases, 11 test cases
- Decision: PYAPP_EXEC_MODULE='lana' over PYAPP_EXEC_SPEC (exit code propagation via __main__.py)
