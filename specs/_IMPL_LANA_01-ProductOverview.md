# IMPL: Lana Product Overview

**Doc ID**: LANAAGNT-IP01
**Goal**: Implement the project skeleton, canonical domain types, and NFR verification infrastructure per LANAAGNT-SP01
**Timeline**: Created 2026-08-29, Extracted from _IMPL_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `pyproject.toml` (package metadata, deps, entry point)
- `README.md` (install + quickstart)
- `src/lana/__init__.py` (version constant)
- `src/lana/__main__.py` (python -m lana)
- `src/lana/models.py` (canonical types)
- `src/lana/events.py` (AgentEvent union)

**Depends on:**
- `_SPEC_LANA_01-ProductOverview.md [LANAAGNT-SP01]` for domain objects, NFRs, DDs, IG-05

**Does not depend on:**
- Component-specific IMPLs (02-AgentCore through 11-Selftest) -- this is the foundation phase

## MUST-NOT-FORGET

- IMPL-CODEBASE mode: output goes to `src/`, `tests/`, `config/`, workspace root (`pyproject.toml`, `README.md`)
- Small cycles: implement -> test -> green -> commit per phase; never proceed on red

## Impact Analysis

- **Greenfield**: `src/` is empty; no existing code paths, callers, or tests are affected
- **Shared file surface**: `config/` gains one NEW file (`lana-config.json`); the 4 existing config files are opened read-only - zero modification risk
- **Workspace root**: gains `pyproject.toml`, `README.md`, `tests/`; no collision with existing files (verified: none exist)
- **External surface**: IPPS folder is read-only input at runtime; never written

## Table of Contents

1. [File Structure](#1-file-structure)
2. [Implementation Steps](#2-implementation-steps)
3. [Test Cases](#3-test-cases)
4. [Verification Checklist](#4-verification-checklist)
5. [Document History](#5-document-history)

## 1. File Structure

```
e:\Dev\Lana-V1\
├── pyproject.toml                    # Package metadata, deps, entry point 'lana' (~40 lines) [NEW]
├── README.md                         # Install + quickstart (~60 lines) [NEW]
├── src/lana/
│   ├── __init__.py                   # Version constant (~5 lines) [NEW]
│   ├── __main__.py                   # python -m lana -> cli.main() (~5 lines) [NEW]
│   ├── models.py                     # Canonical types: Message, ToolCall, ToolResult, ThinkingBlock, Usage (pydantic) (~120 lines) [NEW]
│   └── events.py                     # AgentEvent union (11 types per SPEC incl. session_started), serialization (~130 lines) [NEW]
└── tests/
    └── conftest.py                   # Fixtures: tmp workspace, fake prompt system, scripted adapter wiring (~120 lines) [NEW]
```

Estimated total: ~480 lines source + ~120 lines test fixtures [ASSUMED].

## 2. Implementation Steps

### Phase A: Package Skeleton and Domain Types

### LANAAGNT-IP01-IS-01: Create package skeleton

**Location**: workspace root, `src/lana/`

**Action**: Add `pyproject.toml` (name `lana`, Python >=3.12, deps: `openai`, `anthropic`, `pydantic>=2`, `rich`, `prompt_toolkit`, `pyyaml`; entry point `lana = lana.cli:main`; `pytest` dev dep), `README.md`, `src/lana/__init__.py`, `__main__.py`, empty module files

**Note**: `pip install -e .` must succeed and `lana --help` must print before any feature work

### LANAAGNT-IP01-IS-02: Canonical models and events

**Location**: `models.py`, `events.py`

**Action**: Add pydantic types:
```python
# models.py - provider-neutral conversation model
class ToolCall: id, name, args_json, status          # status: pending|ok|error|cancelled
class ThinkingBlock: provider, payload               # opaque, resent per provider rules
class Message: role, content, tool_calls, thinking, usage
# events.py - the 11 AgentEvent types from SPEC Domain Objects, each with ts + to_jsonl()/from_jsonl()
```

**Note**: `checkpoint_created` carries full checkpoint text (resume replay); `user_message` carries `expanded_workflow` name when applicable; `session_started` carries the full-recall environment (FR-08, see `_IMPL_LANA_02-AgentCore.md [LANACORE-IP01]`)

## 3. Test Cases

### Category 1: Package Skeleton (1 test)

- **LANAAGNT-IP01-TC-SKEL-01**: `pip install -e .` succeeds; `lana --help` prints usage; `python -m lana --help` prints same output

### NFR Verification Approaches

NFRs are defined in `_SPEC_LANA_01-ProductOverview.md [LANAAGNT-SP01]`. Their verification is distributed across component test plans:

- **NFR-01 (No Telemetry)**: Verified by code review + `assert_no_secret_leak` in every black-box scenario (`_TEST_LANA_06-CLI.md [LANACLI-TP01]`)
- **NFR-02 (Crash-Safe Sessions)**: Kill/resume scenario (`_TEST_LANA_02-AgentCore.md [LANACORE-TP01]`)
- **NFR-03 (Prompt Cache)**: Startup timing + Anthropic cache-read verification (`_TEST_LANA_04-Providers.md [LANAPRVD-TP01]`)
- **NFR-04 (Debuggable API Traffic)**: `--debug` log file assertions (`_TEST_LANA_06-CLI.md [LANACLI-TP01]`)
- **NFR-05 (Prompt Injection Threat Model)**: Risk notice assertion (`_TEST_LANA_02-AgentCore.md [LANACORE-TP01]`)

## 4. Verification Checklist

- [x] **LANAAGNT-IP01-VC-01**: LANAAGNT-SP01 re-read; domain objects match Section 3
- [x] **LANAAGNT-IP01-VC-02**: Python 3.12+ available; `pip install -e .` clean
- [x] **LANAAGNT-IP01-VC-04**: Phase A green -- skeleton + models + events compile and pass basic tests

## 5. Document History

**[2026-09-01 21:45]**
- Extracted from `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]`: Impact Analysis, File Structure (skeleton portion), IS-01 (package skeleton), IS-02 (canonical models and events), Phase A VCs
- NFR verification cross-references added pointing to component test plans
- Content is verbatim from source with section renumbering and header block update only
