# Session Notes

**Doc ID**: LANADIST-NOTES

## Initial Request

````text
@/session-new

and @/write-spec that describes the intended distribution mechanism

in the [WORKSPACE_FOLDER] we want

_build.md -> creates binaries
_ship.md -> creates all setups

of if both would do same, then just _build.bat

see deploy.md workflow
````

## Session Info

- **Started**: 2026-08-30
- **Goal**: Specify Lana distribution mechanism (PyApp-based) and create `_build.bat` + `_ship.ps1` build/package scripts
- **Operation Mode**: IMPL-CODEBASE
- **Output Location**: `[WORKSPACE_FOLDER]/_build.bat`, `[WORKSPACE_FOLDER]/_ship.ps1`

## Agent Instructions

- Distribution tool: PyApp (Rust wrapper producing single binary; V1 updates via re-download, `self update` needs PyPI publication)
- One distribution serves both ACP client mode and CLI mode
- Target platform: Windows x64 first (others later)
- Follow `/deploy` workflow pattern: `.bat` launcher + `.ps1` implementation
- Research basis: `E:\Dev\KarstensWorkspace\_Sessions\_2026-08-30_PythonBinaryDistribution\` (13 INFO docs, PYDISTBN topic)

## Key Decisions

- **LANADIST-DD-01**: PyApp chosen over PyInstaller/Nuitka. Rationale: single binary, best expected AV profile [ASSUMED], serves both ACP and CLI from one distribution. See PYDISTBN-IN13 decision matrix (75/100 score).
- **LANADIST-DD-07**: V1 updates via binary re-download. PyApp `self update` pip-updates the PROJECT (not the binary) and requires PyPI publication [VERIFIED: ofek.dev/pyapp/latest/runtime/]. Research doc PYDISTBN-IN07 mislabeled this as binary self-update.
- **LANADIST-DD-02**: Single `_build.bat` instead of separate `_build.bat` + `_build.bat`. Rationale: PyApp build output IS the distributable - no separate installer wrapping needed. Build + sign + package in one script.

## Important Findings

- PyApp `self update` updates the Python project via pip, NOT the binary - research claim "downloads new binary" is wrong [VERIFIED: ofek.dev/pyapp/latest/runtime/]
- PyApp first-run penalty: 5-30s extraction on first use (mitigated by PYAPP_DISTRIBUTION_EMBED=1) [VERIFIED]
- Code signing mandatory for Windows distribution (~100-200 EUR/year) [VERIFIED]
- No cross-compilation: CI matrix builds per platform [VERIFIED]
- Lana deps are packaging-friendly: only pydantic-core is compiled (Rust .pyd) [VERIFIED]

## Topic Registry

**Global topics** (registered in ID-REGISTRY.md):
- `LANADIST` - Lana Distribution and Shipping

**Subtopics** (session-local):
- (none)

## Topic Folders

(none)

## Step Folders

(none)

## Bug List

(none)

## Significant Prompts Log

(none)

## Current Phase

**Phase**: DESIGN
**Workflow**: /write-spec
**Assessment**: Research complete (PYDISTBN session), writing spec for chosen approach
