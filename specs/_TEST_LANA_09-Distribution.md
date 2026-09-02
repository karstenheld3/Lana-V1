# TEST: Lana Distribution Ship Pipeline - Verification Plan

**Doc ID**: LANADIST-TP01
**Goal**: Verify the distribution pipeline and binary behavior meet all LANADIST-SP01 requirements -- pytest for CLI materialization, manual for pipeline and binary behavior
**Timeline**: Created 2026-09-01

**Target file(s)**:
- `tests/test_distribution.py` (offline pytest - CLI flag + zero-setup materialization)
- Manual verification of `_build.bat` pipeline and binary behavior on Windows x64

**Depends on:**
- `_SPEC_LANA_09-Distribution.md [LANADIST-SP01]` for requirements
- `_IMPL_LANA_09-Distribution.md [LANADIST-IP01]` for implementation structure, edge cases, and TC definitions (TC-01..17)

## MUST-NOT-FORGET

- `--version` must exit BEFORE config load (no zero-setup side effects)
- Key-leak guard is a hard gate - never skip in any test scenario
- Pipeline tests require the full toolchain (Rust, .venv, build package)
- Binary behavior tests require a clean machine or PyApp cache wipe
- IG-05: no `.api-keys.txt` with values in wheel or bundle

## Table of Contents

1. [Test Strategy](#1-test-strategy)
2. [Test Fixtures](#2-test-fixtures)
3. [Test Cases](#3-test-cases)
4. [Test Phases](#4-test-phases)
5. [Verification Checklist](#5-verification-checklist)
6. [Document History](#6-document-history)

## 1. Test Strategy

Three layers matching IP01 categories:

- **Layer 1 (pytest)**: CLI flag + zero-setup materialization - `--version`, bundled config materialization, agent folder behavior, tools materialization. 7 tests.
- **Layer 2 (manual)**: Ship pipeline - full `_build.bat` run, same-version replacement, signing skip, checksum, wheel listing, key-leak guard. 6 tests.
- **Layer 3 (manual)**: Distribution binary behavior - fresh machine startup, ACP stdout purity, VirusTotal. 5 tests.

## 2. Test Fixtures

**Setup:**
```python
# Category 1: tmp_path workspace with minimal config; monkeypatch LANA_CONFIG to isolate
# Harness utilities from conftest.py for scripted adapter and config writing
```

**Teardown:**
- pytest `tmp_path` auto-cleanup

## 3. Test Cases

IP01 test cases TC-01..17 are the authoritative definitions. This plan maps them to verification layers and adds the black-box contract.

### Category 1: CLI flag + zero-setup materialization (6 tests, pytest)

- **LANADIST-TP01-TC-01**: `lana --version` exits 0, prints `lana {version}` matching `importlib.metadata.version('lana')` (IP01-TC-01)
- **LANADIST-TP01-TC-02**: `--version` does NOT create config/data folders - no `.lana-data/` in cwd after run (IP01-TC-02)
- **LANADIST-TP01-TC-03**: Empty workspace startup -> all 3 model JSONs + `.api-keys.txt` template + agent library materialized (IP01-TC-12, FR-08)
- **LANADIST-TP01-TC-04**: Partial config (pricing JSON deleted) -> only pricing JSON recreated, others untouched (IP01-TC-13, EC-15)
- **LANADIST-TP01-TC-05**: Existing empty agent folder -> NOT repopulated (IP01-TC-14, EC-14, FR-08)
- **LANADIST-TP01-TC-06**: Materialized `.api-keys.txt` contains `OPENAI_API_KEY`/`ANTHROPIC_API_KEY` lines commented, no values (IP01-TC-15, DD-09)
- **LANADIST-TP01-TC-18**: Tools materialization: missing `.lana-tools/` -> bundled `rg.bin` materializes as `rg.exe`; existing `rg.exe` -> untouched (IP01-TC-18, DD-12, FR-08)

### Category 2: Ship pipeline (6 manual tests, Windows x64 build machine)

- **LANADIST-TP01-TC-07**: `_build.bat` full run -> `dist\lana-{version}-win-x64.exe` + `SHA256SUMS.txt` exist, DONE line printed (IP01-TC-03, FR-01..05)
- **LANADIST-TP01-TC-08**: Second run same version -> old artifact reported before replacement (IP01-TC-04, IG-01)
- **LANADIST-TP01-TC-09**: No `LANA_SIGN_THUMBPRINT` -> NOTICE printed, exit 0, unsigned exe (IP01-TC-05, FR-06)
- **LANADIST-TP01-TC-10**: `Get-FileHash` of exe matches `SHA256SUMS.txt` entry (IP01-TC-06, FR-07)
- **LANADIST-TP01-TC-11**: Wheel listing contains `lana/bundled/agent/` tree and NO `.api-keys.txt` (IP01-TC-16, IG-05)
- **LANADIST-TP01-TC-12**: Planted fake key in a bundled file -> pipeline aborts at step 2 with CRITICAL (IP01-TC-17, EC-12)

### Category 3: Distribution binary behavior (5 manual tests)

- **LANADIST-TP01-TC-13**: Fresh machine/cache: first run takes 5-30 s, second run <1 s (IP01-TC-07, NFR-01)
- **LANADIST-TP01-TC-14**: Binary CLI mode on FRESH machine: starts without pre-existing config, prompt system loads with bundled rules/workflows/skills counts > 0 (IP01-TC-08, FR-08)
- **LANADIST-TP01-TC-15**: Binary ACP mode: `lana.exe --acp` + `initialize` over stdin -> valid JSON-RPC response, stdout ONLY JSON-RPC (IP01-TC-09, FR-02)
- **LANADIST-TP01-TC-16**: PR-0005 probe: delete PyApp cache, pipe `initialize` into `lana.exe --acp`, capture stdout/stderr separately -> stdout has NO extraction noise (IP01-TC-10)
- **LANADIST-TP01-TC-17**: Upload exe to VirusTotal -> record flag count (IP01-TC-11, target 0-2/71)

## 4. Test Phases

1. **Phase 1: Offline unit** - TC-01..06, TC-18 -- pytest, no toolchain required, fast
2. **Phase 2: Pipeline** - TC-07..12 -- requires Rust + .venv + build package, Windows x64
   - Gate: Phase 1 green
3. **Phase 3: Binary behavior** - TC-13..17 -- requires completed binary from Phase 2
   - Gate: Phase 2 green, `dist/` artifact exists
4. **Phase 4: External** - TC-17 VirusTotal -- requires manual upload, async result
   - Gate: Phase 3 green

## 5. Verification Checklist

### Offline (pytest)
- [x] **LANADIST-TP01-VC-01**: TC-01..06 implemented in `tests/test_distribution.py`
- [x] **LANADIST-TP01-VC-02**: `pytest tests/test_distribution.py -q` green without build toolchain

### Pipeline (manual)
- [x] **LANADIST-TP01-VC-03**: TC-07..12 verified on build machine
- [x] **LANADIST-TP01-VC-04**: Key-leak guard tested with planted key (TC-12)

### Binary (manual)
- [x] **LANADIST-TP01-VC-05**: TC-13..16 verified
- [ ] **LANADIST-TP01-VC-06**: TC-17 VirusTotal result recorded (LANADIST-PR-0006)

### Coverage cross-check
- [x] **LANADIST-TP01-VC-07**: Every SP01 FR has at least one TC (FR-01..09 covered; FR-08 tools path via TC-18)
- [x] **LANADIST-TP01-VC-08**: Every SP01 IG has at least one TC (IG-01..05 covered)
- [x] **LANADIST-TP01-VC-09**: DD-12 agent tools vs skill tools distinction covered by TC-18

## 6. Document History

**[2026-09-02 00:00]**
- Added: TC-18 tools materialization (DD-12, FR-08 tools path)
- Added: VC-09 DD-12 coverage check
- Changed: Layer 1 test count 6 -> 7; Phase 1 scope includes TC-18

**[2026-09-01 21:55]**
- Initial test plan created (spec restructure step 9)
