# SPEC: Lana Distribution Mechanism

**Doc ID**: LANADIST-SP01
**Feature**: lana-distribution
**Goal**: Define how Lana is built, packaged, signed, and shipped as a single Windows x64 binary serving both CLI and Agent Client Protocol (ACP) client use
**Timeline**: Created 2026-08-30
**Target file(s)**:
- `_build.bat` (workspace root)
- `_build.ps1` (workspace root)

**Depends on:**
- `_SPEC_LANA_06-CLI.md [LANACLI-SP01]` for CLI entry point and zero-setup behavior
- `_SPEC_LANA_07-ACP.md [LANAACPB-SP01]` for ACP mode (`lana --acp`)

**Does not depend on:**
- `/deploy` workflow (web hosting deployment - different domain; only the `.bat` + `.ps1` script pattern is reused)

## MUST-NOT-FORGET

- One distribution serves BOTH use cases: CLI desktop and ACP client
- Build output MUST be a single `lana.exe` (no directory bundle, no installer)
- Never use PyInstaller `--onefile` pattern (temp extraction = anti-virus (AV) dropper signature)
- `self update` updates the PYTHON PROJECT via pip, NOT the binary - it requires the package on a package index (PyPI); V1 update path is re-download [VERIFIED: ofek.dev/pyapp/latest/runtime/]
- Ship scripts MUST be self-contained: install missing build tools before building
- NEVER copy `.api-keys.txt` into the bundle - the key file template is code-generated (DD-09)
- `.tools/` (836 MB, Ghostscript is AGPL) is NEVER part of the distribution (FR-09)
- Never ship unsigned binaries once a signing certificate exists
- Windows x64 only in V1; macOS and Linux come later via CI matrix

## Table of Contents

1. [Scenario](#1-scenario)
2. [Context](#2-context)
3. [Domain Objects](#3-domain-objects)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Design Decisions](#6-design-decisions)
7. [Implementation Guarantees](#7-implementation-guarantees)
8. [Key Mechanisms](#8-key-mechanisms)
9. [Action Flow](#9-action-flow)
10. [Logging Requirements](#10-logging-requirements)
11. [Technical Constraints](#11-technical-constraints)
12. [Document History](#12-document-history)

## 1. Scenario

**Problem:** Lana is a Python package (`pip install`), which end users cannot run without a Python 3.12+ environment. Users need a download-and-run binary for two scenarios: 1) local CLI use on Windows x64, 2) ACP client launched by IDEs (Zed, etc.) on Windows x64.

**Solution:**
- Build one self-sufficient `lana.exe` with PyApp (Rust wrapper embedding Python distribution + Lana wheel)
- The wheel carries the default payload as package data: model config files and the default prompt library (`.lana` rules/workflows/skills); zero-setup materializes them on first run (FR-08)
- Same binary serves CLI mode (`lana.exe`) and ACP mode (`lana.exe --acp`)
- One script pair in workspace root produces the shippable artifact: `_build.bat` (launcher) + `_build.ps1` (implementation)
- Distribute via GitHub Release assets; users update by re-downloading `lana.exe` (V1); `lana.exe self update` becomes available once Lana is published to PyPI

**What we don't want:**
- Separate distributions for CLI and ACP (double maintenance, user confusion)
- Directory bundles (`--onedir`) - IDE config would point into a folder, xcopy deploy degrades
- PyInstaller `--onefile` (1.8s startup, AV dropper pattern, temp dir litter)
- Installer-based distribution (MSI, NSIS) in V1 - single binary needs no install step
- Requiring Python, Rust, or any runtime on the END USER machine
- Separate `_build.bat` and `_build.bat` - PyApp build output IS the distributable, so one script suffices (LANADIST-DD-02)
- Shipping `.tools/` binaries (836 MB; Ghostscript AGPL) inside the distribution (FR-09)
- Real API keys anywhere near the build pipeline (DD-09, key-leak guard)

## 2. Context

Lana V1 is a Python CLI agent (`src/lana/`, entry point `lana.cli:main`) with an ACP frontend (`lana --acp`, JSON-RPC over stdio). Zero-setup is already implemented: the binary auto-creates config and data folders on first run.

Distribution research completed 2026-08-30 in session `_2026-08-30_PythonBinaryDistribution` (external workspace, topic `PYDISTBN`, 13 INFO docs, 8 tools evaluated). Decision matrix result: PyApp 75/100, PyInstaller --onedir 68/100, Nuitka 65/100. PyApp selected (LANADIST-DD-01).

**Dependency packaging risk**: LOW. Only `pydantic-core` is a compiled extension (Rust `.pyd`); PyApp installs platform-matched wheels, so no freezer hook issues exist.

## 3. Domain Objects

### Distribution Binary

A **Distribution Binary** is the shippable `lana.exe` produced by the ship pipeline.

**Storage:** `dist/lana-{version}-win-x64.exe` (build output), GitHub Release asset (distribution)

**Key properties:**
- `version` - from `pyproject.toml` `[project] version`
- `platform` - `win-x64` in V1
- `embedded Python` - CPython 3.12 from python-build-standalone, embedded at build time
- `embedded wheel` - Lana wheel built from `src/`, embedded at build time
- `signature` - Authenticode signature (once certificate exists)

### Ship Script Pair

The **Ship Script Pair** is `_build.bat` + `_build.ps1` in the workspace root, following the `/deploy` workflow convention (`.bat` launcher delegates to `.ps1` implementation).

**Key properties:**
- `_build.bat` - double-click/CI entry, calls `pwsh -f _build.ps1`
- `_build.ps1` - toolchain check, wheel build, PyApp build, rename, sign, checksum

### Bundled Payload

The **Bundled Payload** is the default content the wheel carries as package data and zero-setup materializes on the end-user machine.

**Storage:** `src/lana/bundled/` (committed), synced from workspace sources by the ship pipeline

**Key properties:**
- `bundled/config/` - `model-registry.json`, `model-parameter-mapping.json`, `model-pricing.json` (synced from workspace `config/`)
- `bundled/agent/` - default prompt library: rules, workflows, skills (synced from workspace `.lana/`, ~291 files / 2.2 MB)
- `.api-keys.txt` template - NOT stored as a file; generated from a code constant (keyless, commented placeholders)

### PyApp Cache

The **PyApp Cache** is the per-user runtime environment the binary creates on first run.

**Storage:** `%LOCALAPPDATA%\pyapp\data\lana\` [TESTED 2026-08-30]

**Key properties:**
- Created on first run: extraction + venv + dependency install from PyPI (1-5 min, network required)
- Subsequent starts <1 s
- `lana.exe self remove` deletes it; next run recreates it
- Interrupted first run leaves a broken cache - recovery via `self restore` or cache delete (LANADIST-PR-0009)

## 4. Functional Requirements

**LANADIST-FR-01: Single Binary Output**
- Ship pipeline produces exactly one file: `dist/lana-{version}-win-x64.exe`
- Binary is self-sufficient: no Python, Rust, or other runtime required on target machine
- Binary embeds the Python distribution (`PYAPP_DISTRIBUTION_EMBED=1`) - no Python-distribution download; first run still installs dependencies from PyPI (network required, DD-03)

**LANADIST-FR-02: Dual-Mode Operation**
- `lana.exe` starts interactive CLI (existing MVP-1 behavior)
- `lana.exe --acp` starts ACP server on stdio (existing MVP-2 behavior)
- All existing CLI flags work identically in binary form

**LANADIST-FR-03: Ship Script Behavior**
- `_build.bat` runs `_build.ps1` via `pwsh` and pauses on error for double-click use
- `_build.ps1` executes the full pipeline: verify toolchain → build wheel → build PyApp binary → rename → sign (if certificate configured) → checksum → report
- Script is self-contained: installs missing build tools (Rust via rustup, `build` package via pip) after user confirmation
- Script fails fast with a clear message on any step failure; never ships a partial artifact

**LANADIST-FR-04: Update Path**
- V1 update path: user re-downloads `lana.exe` from GitHub Releases and replaces the file (single file, no uninstall needed)
- `lana.exe self update` pip-updates the embedded project in the cached venv - it does NOT replace the binary and requires the package on a package index [VERIFIED: ofek.dev/pyapp/latest/runtime/]
- Once Lana is published to PyPI, `self update` becomes the payload update path (binary stays, Python code updates)
- PyApp management commands `self remove` and `self restore` remain available for cache repair

**LANADIST-FR-05: Versioning**
- Binary version comes from `pyproject.toml` - single source of truth
- Output filename carries version and platform: `lana-0.1.0-win-x64.exe`
- Release asset additionally provides a stable unversioned name `lana.exe` for stable IDE config paths

**LANADIST-FR-06: Code Signing**
- When signing certificate is configured (environment variable or config), `_build.ps1` signs the binary with `signtool` and timestamps the signature
- When no certificate is configured, script prints a NOTICE and produces an unsigned binary (development builds)
- Release builds MUST be signed once a certificate exists (LANADIST-PR-0002)

**LANADIST-FR-07: Checksum Generation**
- `_build.ps1` writes `SHA256SUMS.txt` next to the binary containing the SHA-256 hash
- Checksum file is published as a release asset alongside the binary

**LANADIST-FR-08: Bundled Default Payload**
- The wheel embeds `src/lana/bundled/`: `config/` (three model JSON files) and `agent/` (default prompt library)
- Ship pipeline syncs workspace `config/*.json` and `.lana/` into the bundle BEFORE the wheel build; sync NEVER touches `.api-keys.txt`
- Key-leak guard: pipeline aborts if any bundled file contains an `API_KEY=` assignment with a real-key-shaped value (40+ character token); short documentation placeholders pass
- Zero-setup materialization on the end-user machine (default config path only, extends existing FR-16 behavior):
  - Missing model JSON files -> written from bundle
  - Missing `.api-keys.txt` -> keyless template written from code constant
  - MISSING agent folder -> bundled prompt library copied (replaces today's empty-folder scaffold)
  - EXISTING agent folder (even empty) -> left untouched (user deletions are respected)
- Every materialized artifact is reported via the existing zero-setup `Created '...'` lines

**LANADIST-FR-09: External Tools Not Bundled**
- `.tools/` (7-Zip, GitHub CLI, Ghostscript, ImageMagick, QPDF, youtube-downloader; 836 MB) is NOT part of the distribution
- Skills referencing missing tools degrade gracefully: skill instructions carry install hints for the end user
- Tool provisioning (download-on-demand command or separate release asset) is deferred (DD-10)

## 5. Non-Functional Requirements

**LANADIST-NFR-01: Performance - Startup Time**
- Cached start (run 2+): under 1 second to first prompt/ACP response [TESTED 2026-08-30: 1.3 s for `--version` - minor miss, bound by process spawn + Python startup; accepted]
- First run: 1-5 min (PyApp extraction + venv + dependency install from PyPI, network required) [TESTED 2026-08-30] - documented in README
- Verification: measure `lana.exe --version` wall time on cached run

**LANADIST-NFR-02: Reliability - Reproducible Builds**
- Any team member produces an equivalent binary by running `_build.bat` on a Windows x64 machine
- Pinned inputs: Python version, PyApp version, wheel from current source tree
- Verification: two consecutive builds from the same commit produce binaries with identical embedded content

**LANADIST-NFR-03: Security - AV Compatibility**
- Distribution binary avoids known AV trigger patterns: no UPX, no PyInstaller bootloader, no temp-dir self-extraction to execute
- Release binaries checked on VirusTotal before publishing; target: 0-2/71 flags
- Verification: VirusTotal scan per release

**LANADIST-NFR-04: Usability - Zero Setup**
- User workflow: download `lana.exe` → put in a PATH folder → run. No installer, no admin rights
- IDE (ACP) workflow: point agent config `command` to the `lana.exe` path, `args` to `["--acp"]` (no `--app-dir` needed - exe auto-detects via `PYAPP` env var, DD-11)
- Lana's existing zero-setup creates config and data folders on first run

## 6. Design Decisions

**LANADIST-DD-01:** PyApp is the distribution tool. Rationale: only evaluated tool producing a single binary with built-in project update commands; expected best AV profile (Rust binary, no bootloader extraction) [ASSUMED - VirusTotal test pending, LANADIST-PR-0006]; serves ACP and CLI from one artifact. Scored 75/100 vs PyInstaller 68 and Nuitka 65 in PYDISTBN-IN13 [VERIFIED]. Fallback if PyApp proves unworkable: PyInstaller --onedir with rebuilt bootloader.

**LANADIST-DD-02:** One script pair (`_build.bat` + `_build.ps1`), no separate `_build` scripts. Rationale: PyApp's build output IS the final distributable - there is no separate "create setups" step. A build/ship split would duplicate 90% of the pipeline.

**LANADIST-DD-03:** Embed the Python distribution (`PYAPP_DISTRIBUTION_EMBED=1`). Rationale: removes the Python-distribution download from the first run. LIMIT [TESTED 2026-08-30]: project dependencies (openai, anthropic, ...) still install from PyPI on first run - first run REQUIRES network and takes 1-5 min. Binary size: 22.6 MB [TESTED]. Fully offline first run (embedded wheelhouse) is not supported by PyApp and stays out of V1 scope.

**LANADIST-DD-04:** GitHub Releases as the distribution channel. Rationale: free hosting, versioned assets, direct download URL for updates, standard for CLI tools. No marketplace or package manager in V1.

**LANADIST-DD-05:** Windows x64 only in V1. Rationale: matches user base; no cross-compilation exists for Python payloads, so each platform needs its own CI runner. macOS/Linux follow via GitHub Actions matrix when needed.

**LANADIST-DD-06:** Unsigned development builds allowed, signed release builds required. Rationale: certificate acquisition is pending (LANADIST-PR-0002); blocking all builds on it would stall development. SmartScreen warnings are acceptable for internal testing only.

**LANADIST-DD-07:** V1 updates via binary re-download, not `self update`. Rationale: `self update` requires the package on a package index; Lana is not on PyPI in V1. PyPI publication is a separate decision deferred until the distribution proves itself.

**LANADIST-DD-08:** Bundle is committed to git and synced from workspace sources (`config/*.json`, `.lana/`) by the ship pipeline. Rationale: workspace stays the single source of truth for development; the committed bundle keeps builds reproducible from a fresh clone (NFR-02). Drift is impossible because sync runs on every ship.

**LANADIST-DD-09:** `.api-keys.txt` template is generated from a code constant, never copied from the workspace. Rationale: eliminates every code path where real keys could enter the distribution; the workspace key file never meets the pipeline.

**LANADIST-DD-10:** `.tools/` distribution deferred to a future `lana tools install` command or separate release asset. Rationale: 836 MB dwarfs the ~42 MB binary; Ghostscript's AGPL license imposes redistribution obligations the single-binary channel should not carry. Skills already name their tools and can hint installation.

## 7. Implementation Guarantees

**LANADIST-IG-01:** `_build.ps1` never overwrites a previous `dist/` artifact silently - existing files with the same version are reported before replacement.

**LANADIST-IG-02:** A failed pipeline step aborts the whole run with a non-zero exit code; no partial or unsigned-when-signing-was-requested artifact remains in `dist/`.

**LANADIST-IG-03:** The shipped binary passes a smoke test before the script reports success: `lana.exe --version` (or equivalent) executes and returns the expected version string.

**LANADIST-IG-04:** The ship pipeline never modifies source files outside `src/lana/bundled/` (the designated sync target), config files, or the user's Python environment (build happens in isolated temp/venv locations).

**LANADIST-IG-05:** No file in `dist/` or in the wheel ever contains an API key value - the key-leak guard (FR-08) is a hard gate, not a warning.

## 8. Key Mechanisms

**PyApp build model**: PyApp is a Rust crate configured via environment variables at compile time. `cargo build --release` produces a binary that embeds 1) a python-build-standalone CPython distribution and 2) the Lana wheel. On first run the binary extracts both into `%USERPROFILE%\.pyapp\`, creates a venv, installs the wheel, then delegates every subsequent invocation to the venv's Python with <1 s overhead.

**Configuration set** (environment variables at build time):
- `PYAPP_PROJECT_NAME` = `lana`
- `PYAPP_PROJECT_VERSION` = read from `pyproject.toml`
- `PYAPP_PROJECT_PATH` = path to the built wheel (embeds wheel instead of PyPI download)
- `PYAPP_PYTHON_VERSION` = `3.12`
- `PYAPP_DISTRIBUTION_EMBED` = `1`
- `PYAPP_EXEC_MODULE` = `lana` (runs `python -m lana`; the package `__main__.py` wraps `main()` in `sys.exit()` so exit codes reach the ACP client - `PYAPP_EXEC_SPEC` would discard the return value)
- `PYAPP_PASS_LOCATION` = `1` (injects the outer binary's absolute path as the `PYAPP` env var at runtime; used by `resolve_app_dir()` for portable-app data isolation - DD-11)

**Script pattern** (from `/deploy` workflow): `.bat` file is the human/CI entry point, `.ps1` holds the logic. `.bat` checks for `pwsh`, runs the `.ps1`, pauses on failure so double-click users see the error.

**Update flow (V1)**: user downloads the new `lana.exe` from GitHub Releases and overwrites the old file. IDE configs keep working because the path does not change. Post-PyPI-publication: `lana.exe self update` pip-updates the cached project without touching the binary [VERIFIED: ofek.dev/pyapp/latest/runtime/].

## 9. Action Flow

```
User runs _build.bat
├─> pwsh -f _build.ps1
│   ├─> [ 1 / 7 ] Verify toolchain
│   │   ├─> Python 3.12+ present? (build machine only)
│   │   ├─> Rust/cargo present? If missing → offer rustup install
│   │   └─> signtool + certificate configured? → note signing on/off
│   ├─> [ 2 / 7 ] Sync bundle
│   │   ├─> config/*.json → src/lana/bundled/config/ (NEVER .api-keys.txt)
│   │   ├─> .lana/ → src/lana/bundled/agent/
│   │   └─> key-leak guard: scan bundle for uncommented *_API_KEY= → abort on hit
│   ├─> [ 3 / 7 ] Build wheel
│   │   └─> python -m build → dist/lana-{version}-py3-none-any.whl
│   ├─> [ 4 / 7 ] Build PyApp binary
│   │   ├─> set PYAPP_* environment variables
│   │   └─> cargo build --release → pyapp.exe
│   ├─> [ 5 / 7 ] Rename + smoke test
│   │   ├─> copy → dist/lana-{version}-win-x64.exe
│   │   └─> run binary --version → must match pyproject.toml
│   ├─> [ 6 / 7 ] Sign (if certificate configured)
│   │   └─> signtool sign + timestamp
│   └─> [ 7 / 7 ] Checksum + report
│       ├─> SHA256SUMS.txt
│       └─> print artifact path, size, signed status
```

```
End user (CLI)                      IDE (ACP client)
├─> download lana.exe               ├─> agent config:
├─> place in PATH folder            │     command: C:/path/to/lana.exe
└─> run: lana                       │     args: ["--acp"]
    └─> first run: 5-30s setup      └─> IDE spawns lana.exe --acp
        then interactive CLI            └─> JSON-RPC over stdio
```

## 10. Logging Requirements

**Applicable logging types:**
- [x] Script-Level (SC) - `_build.ps1` build output
- [ ] User-Facing (UF) - covered by existing Lana SPECs, not changed by distribution
- [ ] App-Level (AP) - N/A: no server component

**Script-Level logging:**
- **Audience**: Developer running `_build.bat` locally or reading CI logs
- **Goal**: Know which pipeline step ran, whether it succeeded, and where the artifact is - failures diagnosable from log alone
- **Key operations**: toolchain check, wheel build, cargo build, smoke test, signing, checksum

**Expected output for ship run:**
```
Shipping Lana 0.1.0 (win-x64)...
[ 1 / 7 ] Verifying toolchain...
  Python 3.12.4 OK. Cargo 1.86.0 OK.
  NOTICE: No signing certificate configured - binary will be UNSIGNED.
[ 2 / 7 ] Syncing bundle...
  3 config files, 291 agent files (2.2 MB). Key-leak scan OK.
[ 3 / 7 ] Building wheel...
  dist/lana-0.1.0-py3-none-any.whl (2.4 MB). OK.
[ 4 / 7 ] Building PyApp binary (this takes 1-3 minutes)...
  OK.
[ 5 / 7 ] Smoke test...
  lana.exe --version -> 0.1.0. OK.
[ 6 / 7 ] Signing... SKIPPED (no certificate).
[ 7 / 7 ] Checksum...
  SHA256SUMS.txt written. OK.
DONE: dist/lana-0.1.0-win-x64.exe (42 MB, unsigned)
```

## 11. Technical Constraints

- PyApp requires the Rust toolchain on the BUILD machine only; end users need nothing
- PyApp configuration happens via environment variables at `cargo build` time, not via config files
- `PYAPP_PROJECT_PATH` embedding requires the wheel to be built first - pipeline order is fixed
- No cross-compilation for the Python payload: Windows binaries build on Windows; future macOS/Linux binaries need their own CI runners
- python-build-standalone provides the embedded CPython; version availability constrains `PYAPP_PYTHON_VERSION` choices
- Authenticode signing requires `signtool` (Windows SDK) and an Organization Validation (OV) certificate; timestamping needs network access
- PyApp cache lives in `%LOCALAPPDATA%\pyapp\data\lana\` [TESTED] - disk quotas and cache deletion policies affect first-run repetition
- Bundle access at runtime uses `importlib.resources` (package data survives any install layout); wheel stays pure Python (`py3-none-any`) - data files do not affect purity
- `pyproject.toml` needs a package-data declaration for `lana.bundled` (currently only `packages.find` is configured)
- The bundled prompt library requires a privacy review before first public release - skills may reference personal accounts or services (LANADIST-PR-0007)
- ACP mode must not print to stdout outside JSON-RPC; PyApp first-run extraction output destination is unverified [ASSUMED stderr - test during implementation, LANADIST-PR-0005]. If PyApp writes to stdout on first run, IDE handshake needs a pre-warmed cache or a documented first-run-in-terminal step
- First run takes 1-5 min including PyPI dependency install [TESTED 2026-08-30 - research claim of 5-30 s covered extraction only]; cached runs start in under 1 s [TESTED]
- GitHub Release assets are the distribution and update-download source in V1

## 12. Document History

**[2026-09-01 20:25]**
- Added: `PYAPP_PASS_LOCATION=1` to configuration set (section 8) - enables portable-app auto-detection per LANAAGNT-DD-25
- Changed: NFR-04 ACP workflow note - `--app-dir` no longer needed (auto-detection via `PYAPP` env var)
- Synced from code: `cli.py` `resolve_app_dir()`, `_build.ps1` `PYAPP_PASS_LOCATION`

**[2026-08-30 17:40]**
- Fixed: offline-first-run claim (DD-03, FR-01, NFR-01) - dependencies install from PyPI on first run, 1-5 min, network required [TESTED]
- Fixed: PyApp cache location `%USERPROFILE%\.pyapp\` -> `%LOCALAPPDATA%\pyapp\data\lana\` [TESTED]
- Changed: key-leak guard definition to real-key shape (40+ char token) after placeholder false positive [TESTED]
- Added: broken-cache-on-interrupted-first-run property (LANADIST-PR-0009)

**[2026-08-30 16:35]**
- Added: FR-08 Bundled Default Payload (config trio + agent library as wheel package data, zero-setup materialization, key-leak guard)
- Added: FR-09 External Tools Not Bundled (.tools 836 MB, Ghostscript AGPL)
- Added: DD-08 bundle sync strategy, DD-09 code-generated key template, DD-10 tools deferral
- Added: IG-05 key-leak hard gate; Bundled Payload domain object
- Changed: pipeline 6 -> 7 steps (new step [ 2 / 7 ] Sync bundle); logging example updated
- Context: fixed latent bug - model JSON files were required at startup but never created by zero-setup

**[2026-08-30 16:25]**
- Changed: entry point `PYAPP_EXEC_SPEC=lana.cli:main` → `PYAPP_EXEC_MODULE=lana` (exit code propagation, found during IMPL planning LANADIST-IP01-IS-05)

**[2026-08-30 16:15]**
- Fixed: FR-04 self-update claim corrected against official PyApp docs - `self update` updates the project via pip, not the binary; V1 update path is re-download (DD-07 added)
- Added: verification labels on AV profile, binary size, first-run timing, stdout destination
- Changed: acronyms ACP, AV, OV written out on first use

**[2026-08-30 16:10]**
- Initial specification created: PyApp single-binary distribution, _build.bat + _build.ps1 pipeline, 7 FRs, 4 NFRs, 6 DDs
