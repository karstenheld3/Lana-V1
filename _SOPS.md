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
- Release MUST include a build from the release version (binary filename must match pyproject.toml version)

## Table of Contents

- [SOP 1: Version Bump](#sop-1-version-bump)
- [SOP 2: Build Distribution Binary](#sop-2-build-distribution-binary)
- [SOP 3: Prompt Library Changed](#sop-3-prompt-library-changed)
- [SOP 4: Model Config Files Updated](#sop-4-model-config-files-updated)
- [SOP 5: Dependencies Changed](#sop-5-dependencies-changed)
- [SOP 6: Full Release](#sop-6-full-release)
- [SOP 7: Register Lana as ACP Agent](#sop-7-register-lana-as-acp-agent)
- [Common Verification Commands](#common-verification-commands)
- [Domain-Specific SOPs](#domain-specific-sops)

## SOP 1: Version Bump

**Scenario**: Preparing a new release version.

### Rules

- **Starting version**: 1.0.0
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

## SOP 6: Full Release

**Scenario**: Creating a tagged release with GitHub release and binary asset.

### Prerequisites

- All work committed and pushed
- GitHub CLI (`gh`) installed and authenticated

### Steps

1. **Version bump** (SOP 1): run `_ship.bat` or manually edit `pyproject.toml`, commit
2. **Build** (SOP 2): run `_build.bat` -- binary filename MUST match `pyproject.toml` version
3. **Verify binary version**: `dist/lana-{version}-win-x64.exe` exists and `lana --version` output matches
4. **Run `/project-release`** workflow: generates release notes, tags, creates GitHub release with binary
5. **Post-release bump**: increment patch version in `pyproject.toml`, commit (`chore: bump working version to X.Y.Z`)

### Gate: Version Consistency Check

Before creating the GitHub release, ALL of these must match:
- `pyproject.toml` version
- Binary filename version (`dist/lana-X.Y.Z-win-x64.exe`)
- `lana --version` output from the binary
- Git tag (`vX.Y.Z`)

If any mismatch: STOP and rebuild. Never release a binary built from a different version.

### Verification

```powershell
$v = (Select-String -Path pyproject.toml -Pattern '^version\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
Test-Path "dist\lana-$v-win-x64.exe"  # must be True
git tag --sort=-v:refname | Select-Object -First 1  # must be v$v
gh release view "v$v" --json tagName,assets  # must show binary asset
# pyproject.toml version is higher than the just-released tag (post-release bump done)
```

## SOP 7: Register Lana as ACP Agent

**Scenario**: Hooking up Lana as a local ACP agent in Devin Desktop (stable) or Devin Next.

### Prerequisites

- Built binary exists (`dist\lana-{version}-win-x64.exe`) or `lana-debug.bat` wrapper (SOP 2)
- Devin Desktop or Devin Next installed
- Pro, Max, or Teams subscription (ACP requires paid plan)

### Registry Path

**Windows** (both Devin Desktop and Devin Next share one file):

```
%APPDATA%\Code\User\acp\registry.json
```

**macOS/Linux** (separate per channel):
- **Devin Desktop**: `~/.windsurf/acp/registry.json`
- **Devin Next**: `~/.windsurf-next/acp/registry.json`

**Safest approach**: Use `Ctrl+Shift+P` > **Open Local ACP Registry Config** from within the target IDE.

### Steps (same for Devin Desktop and Devin Next)

1. **Open** the target IDE (Devin Desktop or Devin Next)

2. **Open registry**: `Ctrl+Shift+P` > **Open Local ACP Registry Config**

3. **Add agent entry**. Two options (can register both side by side with different `id` values):

   **Option A -- standard** (no debug console):
   ```json
   {
     "id": "lana",
     "name": "Lana",
     "version": "1.1.0",
     "description": "CLI agent running IPPS prompt system on OpenAI/Anthropic backends",
     "authors": ["Karsten Held"],
     "license": "proprietary",
     "distribution": {
       "binary": {
         "windows-x86_64": {
           "archive": "",
           "cmd": "E:/Dev/Lana-V1/dist/lana-1.1.0-win-x64.exe",
           "args": ["--acp"]
         }
       }
     }
   }
   ```

   **Option B -- with debug console** (opens a second window with real-time LLM/tool/ACP timing):
   ```json
   {
     "id": "lana-debug",
     "name": "Lana (Debug Console)",
     "version": "1.1.0",
     "description": "Lana with real-time debug/timing output in a second console window",
     "authors": ["Karsten Held"],
     "license": "proprietary",
     "distribution": {
       "binary": {
         "windows-x86_64": {
           "archive": "",
           "cmd": "E:/Dev/Lana-V1/dist/lana-1.1.0-win-x64.exe",
           "args": ["--debug-console", "--acp"]
         }
       }
     }
   }
   ```

   **IMPORTANT**: `cmd` must point directly to the `.exe`. Do NOT use `.bat` wrappers -- Devin Desktop spawns binaries via Node.js `child_process.spawn`, which cannot execute `.bat` files without `shell: true`. The bat silently fails to launch.

4. **Reload**: `Ctrl+Shift+P` > **Reload ACP Connections** (no restart needed), OR restart the IDE

5. **Enable**: `Ctrl+Shift+P` > **Devin User Settings** > **Agents** tab > toggle **Lana** on

6. **API keys**: Configure via the `...` button next to Lana in the Agents tab, or place keys in `config/.api-keys.txt` relative to the workspace

7. **Test**: Start a new conversation, select **Lana** from the agent selector (bottom-right)

### Troubleshooting

- **Agent not listed in Settings > Agents**: Registry JSON is malformed or `cmd` path does not exist. Validate JSON and verify the path
- **Agent listed but fails to start**: Check that the binary runs standalone (`lana.exe --acp` from terminal). Look for missing API keys or config errors
- **Changed registry but nothing happened**: Run `Reload ACP Connections` from Command Palette. If still no change, restart the IDE
- **Agent visible in Devin but not Next (or vice versa)**: On Windows both channels share one registry. On macOS/Linux each channel has its own file (see Registry Path above)
- **`.bat` wrapper silently fails**: Devin Desktop cannot spawn `.bat` files as ACP agents. Always use a direct `.exe` path in `cmd`. Pass `--debug-console` in the `args` array instead
- **Version drift after rebuild**: After `_build.bat`, the exe filename changes (e.g., `lana-1.0.0-win-x64.exe` -> `lana-1.0.1-win-x64.exe`). Update the `cmd` path in the registry to match the new filename, then run `Reload ACP Connections`

### Verification

```powershell
# Registry file exists and contains Lana entry
$reg = "$env:APPDATA\Code\User\acp\registry.json"
Test-Path $reg
(Get-Content $reg | ConvertFrom-Json).agents | Where-Object id -eq 'lana'
# cmd path resolves
$cmd = ((Get-Content $reg | ConvertFrom-Json).agents | Where-Object id -eq 'lana').distribution.binary.'windows-x86_64'.cmd
Test-Path $cmd
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

## Domain-Specific SOPs

Procedures for specific domains live in `specs/SOPS/`. These are separate from workspace SOPs above because they address cross-session processes rather than build/release mechanics.

- **`_INFO_HOW_TO_IMPROVE_LANA.md`** `[LANALOGS-IN01]` - Evidence-Driven Improvement Pipeline: batched OBSERVE-EXTEND-MEASURE-CHANGE-VERIFY-GATE-COMMIT cycle with check-level attribution and tiered verification
- **`_PROMPTS_IMPROVE_LANA_FROM_LANALOGS_TEMPLATE.md`** - Prompt sequence template enforcing the pipeline above. One copy per batch of findings (1-5), produces atomic commits with per-finding attribution

