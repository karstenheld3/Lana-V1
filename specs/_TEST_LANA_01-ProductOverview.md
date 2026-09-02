# TEST: Lana Product Overview - Verification Plan

**Doc ID**: LANAAGNT-TP01
**Goal**: Define the test strategy, NFR verification approaches, and cross-cutting test infrastructure for the Lana CLI agent
**Timeline**: Created 2026-08-29, Extracted from _TEST_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `tests/conftest.py` (shared fixtures)
- `tests/harness.py` (CLI harness)
- `tests/scripted_adapter.py` (deterministic replay)

**Depends on:**
- `_SPEC_LANA_01-ProductOverview.md [LANAAGNT-SP01]` for NFRs and domain objects
- `_IMPL_LANA_01-ProductOverview.md [LANAAGNT-IP01]` for IS-01 (skeleton), IS-02 (models/events)

**Does not depend on:**
- Component-specific test plans (02-AgentCore through 11-Selftest) -- this defines the cross-cutting strategy they all use

## MUST-NOT-FORGET

- Every black-box scenario runs the REAL `lana` executable via `tests/harness.py` - no in-process shortcuts
- Scripted adapter = determinism; live-key tests are a separate, skippable phase
- Test workspaces are temp folders with their own `--config` - the real `config/lana-config.json` and IPPS are never written
- All scenario fixtures use generic content (Privacy Gate) - no real names, keys, or personal data in scripts or fake prompt systems

## Table of Contents

1. [Overview](#1-overview)
2. [Test Strategy](#2-test-strategy)
3. [Test Priority Matrix](#3-test-priority-matrix)
4. [Test Data](#4-test-data)
5. [Test Phases](#5-test-phases)
6. [Helper Functions](#6-helper-functions)
7. [Cleanup](#7-cleanup)
8. [NFR Verification Contract](#8-nfr-verification-contract)
9. [Verification Checklist](#9-verification-checklist)
10. [Document History](#10-document-history)

## 1. Overview

Four test layers verify Lana MVP-1: unit (pure functions), integration (agent loop with in-process scripted adapter), **automated CLI black-box** (real executable driven by the harness - the layer this plan specifies in scenarios), and live smoke (real APIs, skippable). The black-box layer is possible because SPEC FR-14/DD-20 define three observable interfaces: headless prompt injection, per-line-flushed session JSONL, and the scripted replay adapter.

## 2. Test Strategy

**Approach**: unit + integration + black-box CLI (scripted) + live smoke, mapped to IP01 phases:

- **Layer 1 Unit** (IP01 TC groups per component): pure functions, in-process, no subprocess - config, loader, prompt assembly, tools, safety, projection, cost
- **Layer 2 Integration** (IP01 TC groups per component): agent loop as async generator with in-process scripted adapter - event sequences, cancellation, resume
- **Layer 3 Black-box CLI** (IP01 TC groups + TP01-TC per component): real `lana` subprocess, temp workspace, scripted adapter env - the automated equivalent of a human driving the CLI
- **Layer 4 Live smoke** (IP01 TC groups per component): real provider APIs; auto-skipped when keys absent; budget cap: under $1 per full run [ASSUMED]

**Verification style**: event-sequence assertions (ordered subsequence matching on typed events with ids/timestamps masked), exit-code assertions, and file-state assertions (workspace files after edit-tool scenarios).

## 3. Test Priority Matrix

### MUST TEST (critical logic, automated)

- **Safety gate** (`safety.py` + FR-12) - Testability: EASY, Effort: Low - denylist/alias/wrapper/policy matrix; the one component where a bug destroys user data
- **Turn loop event contract** (`agent.py` + DD-06) - Testability: EASY (scripted), Effort: Medium - ordering, limits, cancellation, headless denial
- **Session persistence + resume** (`session.py` + IG-02/IG-06) - Testability: EASY, Effort: Medium - crash-safety is a headline NFR
- **Compaction** (`compaction.py` + IG-04) - Testability: EASY, Effort: Medium - deterministic todo survival, fail-safe
- **Edit gates** (`edit_tools.py` + FR-11) - Testability: EASY, Effort: Low - read-ledger, uniqueness, atomicity
- **System prompt assembly** (`prompt.py` + IG-01) - Testability: EASY, Effort: Low - byte identity, no dropped-tool names

### SHOULD TEST (important, automated where cheap)

- **Provider adapters** - Testability: MEDIUM (live keys), Effort: Medium - round trips, cache hits, Responses reasoning regression
- **Prompt system loader against real IPPS** - Testability: EASY (skip-if-absent), Effort: Low
- **Cost math** - Testability: EASY, Effort: Low
- **Web tools** - Testability: MEDIUM (network), Effort: Medium - fetch/chunk against a local HTTP fixture server where possible, live search in smoke only

### DROP (not worth automating)

- **rich rendering pixel/layout output** - Reason: formatting-only; events carry the tested substance
- **prompt_toolkit interactive keybindings** - Reason: terminal-dependent; non-terminal path is tested, interactive path covered by manual acceptance (IP01 TC-47)
- **Provider SDK internals (retries, HTTP)** - Reason: external dependency, SDK-tested upstream

## 4. Test Data

**Required Fixtures:**
- `fake_system/` - minimal prompt system: 3 rules (one empty, one oversized, one normal with `trigger: always_on`), 3 workflows (`hello.md`, `tooluse.md`, `prime-like.md`), 2 skills (one with supporting files)
- `scripts/*.jsonl` - scripted adapter turn scripts per scenario (IS-22 format); naming: `script_[scenario].jsonl`
- `config_test.json` - LanaConfig pointing at `fake_system/`, tiny thresholds for compaction scenarios (e.g., `compaction_threshold_max_tokens: 500`)
- Local HTTP fixture server (pytest fixture) serving one HTML page and one binary blob for `read_url_content` tests
- Live-key markers: pytest marker `live` auto-skipped unless both provider keys resolve

**Setup:** per-test temp workspace (`tmp_path`), copy `fake_system/` + write `config_test.json`, set `LANA_SCRIPTED_ADAPTER` + `LANA_CONFIG` env for the subprocess.

**Teardown:** terminate any surviving `lana` subprocess (kill after 5 s grace); temp folders removed by pytest; no global state.

## 5. Test Phases

1. **Phase T1: Offline foundation** (Layers 1-2), run on every change, no keys, no network
2. **Phase T2: Black-box CLI** (Layer 3), scripted adapter, no keys; requires `pip install -e .`
3. **Phase T3: Live smoke** (Layer 4), keys present, marker `live`, budget-capped
4. **Phase T4: Acceptance** - offline e2e + live manual run; results recorded in PROGRESS.md

Dependency: T2 requires T1 green; T3/T4 require T2 green. T1+T2 are the continuous integration (CI) gate.

## 6. Helper Functions

```python
# tests/harness.py - the automated CLI driver (IP01 IS-22)
class LanaProc:
    def __init__(workspace, config_path, script_path, policy): ...  # configure; not yet started
    def run_headless(prompt, output_format="jsonl", timeout=60): ...  # lana -p "<prompt>" (FR-14)
    def run_piped(stdin_text, timeout=60): ...                       # piped stdin REPL fallback
    def start_piped(extra_args=None) -> Popen: ...                   # non-blocking spawn (kill/resume)
    def send(line) -> None: ...                                      # stdin injection (piped mode)
    def events(result=None) -> list[AgentEvent]: ...                 # parsed stdout JSONL
    def tail_session(predicate, timeout=10.0) -> AgentEvent: ...     # poll flushed session file (FR-08)
    def wait_exit(timeout=30) -> int: ...                            # exit code (FR-14 semantics)
# assertions
def assert_event_order(events, expected_types): ...                  # ordered subsequence match on type strings
def assert_no_secret_leak(outputs, key_values): ...                  # NFR-01: key material absent everywhere
```

## 7. Cleanup

- Surviving `lana` subprocesses (harness teardown kills after grace period)
- Temp workspaces and session files (pytest `tmp_path` auto-removal)
- `.lana-data/logs/` debug output inside temp workspaces only - never in the real workspace
- Live smoke sessions: no cleanup needed (temp workspaces); spend reported in test summary

## 8. NFR Verification Contract

Every NFR from `_SPEC_LANA_01-ProductOverview.md [LANAAGNT-SP01]` must be cited by at least one passing TC across component test plans:

- **LANAAGNT-NFR-01 (No Telemetry)**: `assert_no_secret_leak` wired into every black-box scenario; code review confirms only `api.openai.com` / `api.anthropic.com` contacted
- **LANAAGNT-NFR-02 (Crash-Safe Sessions)**: Kill/resume scenario in `_TEST_LANA_02-AgentCore.md [LANACORE-TP01]`
- **LANAAGNT-NFR-03 (Prompt Cache)**: Startup < 2 s; Anthropic cache-read tokens verified in live smoke in `_TEST_LANA_04-Providers.md [LANAPRVD-TP01]`
- **LANAAGNT-NFR-04 (Debuggable API Traffic)**: `--debug` log assertions in `_TEST_LANA_06-CLI.md [LANACLI-TP01]`
- **LANAAGNT-NFR-05 (Prompt Injection Threat Model)**: Risk notice on auto/turbo startup in `_TEST_LANA_02-AgentCore.md [LANACORE-TP01]`

## 9. Verification Checklist

- [x] **LANAAGNT-TP01-VC-01**: Phases T1+T2 green locally with zero keys configured (proves offline completeness)
- [x] **LANAAGNT-TP01-VC-03**: Coverage contract - every SPEC NFR-01..05 is cited by at least one passing TC across component test plans
- [x] **LANAAGNT-TP01-VC-04**: `assert_no_secret_leak` wired into every black-box scenario (NFR-01)
- [x] **LANAAGNT-TP01-VC-05**: T3 live smoke green with keys; spend under budget cap
- [x] **LANAAGNT-TP01-VC-06**: T4 acceptance executed; deviations synced back to SPEC/IMPL via `/sync`

## 10. Document History

**[2026-09-01 21:58]**
- Fixed: `LanaProc` API sketch synced from `tests/harness.py` (`__init__` not `start`, `run_headless`/`run_piped`/`start_piped` methods, `assert_event_order` not `assert_event_sequence`)
- Source: `/fact-check` + `/sync` against source code

**[2026-09-01 21:45]**
- Extracted from `_TEST_LANA_MVP-1.md [LANAAGNT-TP01]`: Overview, Test Strategy, Test Priority Matrix, Test Data, Test Phases, Helper Functions, Cleanup, Verification Checklist
- Added: NFR Verification Contract section (cross-references to component test plans)
- Specific TCs (conversation, safety, robustness, diagnostics, full-recall) moved to their respective component test plans
- Content is verbatim from source with section renumbering and header block update only
