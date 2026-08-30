# Standard Operating Procedures (SOPs)

**Doc ID**: GLOB-SOPS
**Goal**: Repeatable procedures for versioning, building, releasing, and maintaining the Lana-V1 project.

**Acronyms**: SOP = Standard Operating Procedure. MNF = MUST-NOT-FORGET.

## Placeholders

- `[WORKSPACE]` - `E:\Dev\Lana-V1`
- `[AGENT_FOLDER]` - `[WORKSPACE]\.lana` (prompt system: rules, workflows, skills)
- `[BUNDLED]` - `[WORKSPACE]\src\lana\bundled` (build-time copy of config + agent library)

## MUST-NOT-FORGET

- Version 1.x only in this repo. No major version bump. Lana 2.x = separate repo (ACP 2.x)
- `pyproject.toml` is the single source of truth for the version string
- `_ship.bat` bumps version, `_build.bat` builds binary. Pipeline order: ship before build
- `.api-keys.txt` NEVER enters the bundle or wheel (DD-09, IG-05)
- `.tools/` (836 MB, AGPL) NEVER part of the distribution (FR-09)
- Existing user agent folder is never overwritten by materialization (FR-08)
- Every SOP ends with a verification step before you can consider the change complete

## Table of Contents

- [SOP 1: Version Bump](#sop-1-version-bump)
- [SOP 2: Build Distribution Binary](#sop-2-build-distribution-binary)
- [SOP 3: Prompt Library Changed](#sop-3-prompt-library-changed)
- [SOP 4: Model Config Files Updated](#sop-4-model-config-files-updated)
- [SOP 5: Dependencies Changed](#sop-5-dependencies-changed)
- [SOP 6: Post-Release Tag](#sop-6-post-release-tag)
- [Common Verification Commands](#common-verification-commands)

## SOP 1: Version Bump

**Scenario**: Preparing a new release version.

### Rules

- **Starting version**: 1.1.0
- **Allowed bumps**: minor and patch only (1.1.x, 1.2.0, ...). No major version bump in this repo.
- **Rationale**: Lana 1.x supports ACP 1.x. Lana 2.x will live in a separate repo and support ACP 2.x.

### Steps

1. **Run `_ship.bat`**: bumps version in `pyproject.toml` based on commit types (patch for fixes, minor for features)
2. **Commit**: `git add pyproject.toml && git commit -m "chore: bump version to X.Y.Z"`

### Verification

```powershell
# Version in pyproject.toml matches intent
Select-String -Path "[WORKSPACE]\pyproject.toml" -Pattern '^version\s*='
# No major version (first digit must be 1)
# lana --version output matches pyproject.toml after install
```

## SOP 2: Build Distribution Binary

**Scenario**: Producing `dist\lana-{version}-win-x64.exe` from current source.

### Prerequisites

- `.venv` exists (run `_InstallAndCompileDependencies.bat` once)
- Rust toolchain installed (`rustup` + MSVC Build Tools)
- Version already bumped (SOP 1) if this is a release build

### Steps

1. **Run `_build.bat`** (or `pwsh -f _build.ps1` directly)
   - Pipeline: toolchain check -> bundle sync -> wheel -> PyApp -> smoke test -> sign -> checksum -> cleanup
2. **Artifact**: `dist\lana-{version}-win-x64.exe` + `SHA256SUMS.txt`

### Verification

```powershell
# Artifact exists and checksum matches
Test-Path "[WORKSPACE]\dist\lana-*-win-x64.exe"
$hash = (Get-FileHash "[WORKSPACE]\dist\lana-*-win-x64.exe" -Algorithm SHA256).Hash.ToLower()
Get-Content "[WORKSPACE]\dist\SHA256SUMS.txt"
# Bundled dirs are empty after build (cleanup step)
(Get-ChildItem "[BUNDLED]\agent" -Recurse -File -ErrorAction SilentlyContinue).Count -eq 0
(Get-ChildItem "[BUNDLED]\config" -Recurse -File -ErrorAction SilentlyContinue).Count -eq 0
```

## SOP 3: Prompt Library Changed

**Scenario**: Rules, workflows, or skills edited in `[AGENT_FOLDER]`.

### Steps

1. **Edit source** in `[AGENT_FOLDER]` (`.lana/rules/`, `.lana/workflows/`, `.lana/skills/`)
2. **No manual sync needed**: `_build.bat` step 2 copies `.lana/` -> `[BUNDLED]/agent/` automatically
3. **If skill/workflow added or removed**: update `README.md` counts and lists

### Verification

```powershell
# After next build: wheel contains updated agent tree
# .lana/ is the source of truth - bundled/ is transient (emptied after build)
```

## SOP 4: Model Config Files Updated

**Scenario**: Adding a model, changing pricing, or updating parameter mappings.

### Source of truth

`[WORKSPACE]/config/` contains the canonical copies:
- `model-registry.json`
- `model-pricing.json`
- `model-parameter-mapping.json`

### Steps

1. **Edit source** in `[WORKSPACE]/config/`
2. **No manual sync needed**: `_build.bat` step 2 copies `config/*.json` -> `[BUNDLED]/config/` automatically
3. **Never edit `.api-keys.txt` for distribution** - key template is code-generated (DD-09)

### Verification

```powershell
# JSON is valid
foreach ($f in 'model-registry.json','model-pricing.json','model-parameter-mapping.json') {
  Get-Content "[WORKSPACE]\config\$f" | ConvertFrom-Json | Out-Null
  Write-Host "$f OK"
}
```

## SOP 5: Dependencies Changed

**Scenario**: Adding, removing, or updating a Python dependency in `pyproject.toml`.

### Steps

1. **Edit** `pyproject.toml` `[project] dependencies`
2. **Reinstall**: `pip install -e .[dev]` in `.venv`
3. **Run tests**: `pytest`
4. **Rebuild binary** (SOP 2) - PyApp first-run will install new deps from PyPI

### Verification

```powershell
# All tests pass
& "[WORKSPACE]\.venv\Scripts\python.exe" -m pytest
# Dependency resolves
& "[WORKSPACE]\.venv\Scripts\python.exe" -m pip check
```

## SOP 6: Post-Release Tag

**Scenario**: A release was tagged. Working version must be incremented so ongoing development is distinguishable.

### When to apply

Immediately after `git tag` and `git push --tags`. Last step of the release process.

### Steps

1. **Determine next version**: increment patch (e.g., `1.1.0` -> `1.1.1`) or minor (e.g., `1.1.x` -> `1.2.0`)
2. **Edit** `pyproject.toml` version
3. **Commit**: `git commit -am "chore: bump working version to X.Y.Z"`

### Verification

```powershell
# pyproject.toml version is higher than the just-released tag
Select-String -Path "[WORKSPACE]\pyproject.toml" -Pattern '^version\s*='
git tag --sort=-v:refname | Select-Object -First 1
```

## Common Verification Commands

### Check bundled dir is clean (after build)

```powershell
Get-ChildItem "[BUNDLED]\agent","[BUNDLED]\config" -Recurse -File -ErrorAction SilentlyContinue
# Expected: no output (dirs exist but are empty)
```

### Check for key leaks in source

```powershell
Select-String -Path (Get-ChildItem "[WORKSPACE]\src" -Recurse -File) -Pattern 'API_KEY\s*=\s*["'']?[A-Za-z0-9_-]{40,}'
# Expected: no output
```

### Check __pycache__ pollution

```powershell
Get-ChildItem -Path "[WORKSPACE]\src","[WORKSPACE]\tests" -Recurse -Directory -Filter "__pycache__"
# Cleanup: pipe to Remove-Item -Recurse -Force
```

