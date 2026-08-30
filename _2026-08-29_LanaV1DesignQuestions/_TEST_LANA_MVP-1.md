# TEST: Lana MVP-1 - Automated Verification of the CLI Agent

**Doc ID**: LANAAGNT-TP01
**Feature**: lana-mvp-1
**Goal**: Define the automated test system proving Lana MVP-1 satisfies LANAAGNT-SP01, with black-box command-line interface (CLI) testing (prompt injection, log access, activity monitoring) as the primary layer
**Timeline**: Created 2026-08-29, Updated 0 times
**Target file(s)**:
- `tests/` (all modules per LANAAGNT-IP01 File Structure)

**Depends on:**
- `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` rev 22:20 for requirements (FR-14/DD-20 added for this plan)
- `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` rev 06:20 for the 63 unit/integration test cases (TC-01..63 incl. Categories 11-12) and phases
- `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` for tool contract assertions

## MUST-NOT-FORGET

- IP01 owns unit/integration cases (LANAAGNT-IP01-TC-01..63); this plan owns black-box scenarios (LANAAGNT-TP01-TC-*) and the coverage contract - never duplicate case definitions across the two documents
- Every black-box scenario runs the REAL `lana` executable via `tests/harness.py` - no in-process shortcuts
- Scripted adapter = determinism; live-key tests are a separate, skippable phase
- Test workspaces are temp folders with their own `--config` - the real `config/lana-config.json` and DevSystemV4.2 are never written
- All scenario fixtures use generic content (Privacy Gate) - no real names, keys, or personal data in scripts or fake prompt systems

## Table of Contents

1. [Overview](#1-overview)
2. [Scenario](#2-scenario)
3. [Test Strategy](#3-test-strategy)
4. [Test Priority Matrix](#4-test-priority-matrix)
5. [Test Data](#5-test-data)
6. [Test Cases](#6-test-cases)
7. [Test Phases](#7-test-phases)
8. [Helper Functions](#8-helper-functions)
9. [Cleanup](#9-cleanup)
10. [Verification Checklist](#10-verification-checklist)
11. [Document History](#11-document-history)

## 1. Overview

Four test layers verify Lana MVP-1: unit (pure functions), integration (agent loop with in-process scripted adapter), **automated CLI black-box** (real executable driven by the harness - the layer this plan specifies in scenarios), and live smoke (real APIs, skippable). The black-box layer is possible because SPEC FR-14/DD-20 define three observable interfaces: headless prompt injection, per-line-flushed session JSONL, and the scripted replay adapter.

## 2. Scenario

**Problem:** An interactive LLM agent CLI is traditionally tested by hand - nondeterministic model output, blocking approval prompts, and terminal-dependent input make automation fail. Regressions in the turn loop, safety gates, or session persistence would only surface in manual runs.

**Solution:**
- Deterministic turns via the scripted adapter (`LANA_SCRIPTED_ADAPTER`) - a test states exactly which tool calls the "model" makes
- Prompt injection via `lana -p` and piped stdin; observation via stdout JSON Lines (JSONL) events, the tailed session file, and `--debug` logs
- Assertions on the AgentEvent stream - the same contract the renderer and future ACP frontend consume

**What we don't want:**
- Tests asserting on rich-rendered terminal text (brittle formatting coupling) - assert on events, not paint
- Pseudo-terminal emulation (pywinpty/pexpect) - FR-14's non-terminal fallback exists precisely to avoid it
- Live-API calls in the default test run - cost and flakiness; live smoke is opt-in via keys present
- Sleep-based waits - the harness polls the flushed session file with timeouts

## 3. Test Strategy

**Approach**: unit + integration + black-box CLI (scripted) + live smoke, mapped to IP01 phases:

- **Layer 1 Unit** (IP01 TC-01..31, TC-36..39, TC-48..49): pure functions, in-process, no subprocess - config, loader, prompt assembly, tools, safety, projection, cost
- **Layer 2 Integration** (IP01 TC-32..35): agent loop as async generator with in-process scripted adapter - event sequences, cancellation, resume
- **Layer 3 Black-box CLI** (IP01 TC-50..55 + TP01-TC-01..10 below): real `lana` subprocess, temp workspace, scripted adapter env - the automated equivalent of a human driving the CLI
- **Layer 4 Live smoke** (IP01 TC-40..45, TC-47): real provider APIs; auto-skipped when keys absent; budget cap: under $1 per full run [ASSUMED]

**Verification style**: event-sequence assertions (ordered subsequence matching on typed events with ids/timestamps masked), exit-code assertions, and file-state assertions (workspace files after edit-tool scenarios).

## 4. Test Priority Matrix

### MUST TEST (critical logic, automated)

- **Safety gate** (`safety.py` + FR-12) - Testability: EASY, Effort: Low - denylist/alias/wrapper/policy matrix; the one component where a bug destroys user data
- **Turn loop event contract** (`agent.py` + DD-06) - Testability: EASY (scripted), Effort: Medium - ordering, limits, cancellation, headless denial
- **Session persistence + resume** (`session.py` + IG-02/IG-06) - Testability: EASY, Effort: Medium - crash-safety is a headline NFR
- **Compaction** (`compaction.py` + IG-04) - Testability: EASY, Effort: Medium - deterministic todo survival, fail-safe
- **Edit gates** (`edit_tools.py` + FR-11) - Testability: EASY, Effort: Low - read-ledger, uniqueness, atomicity
- **System prompt assembly** (`prompt.py` + IG-01) - Testability: EASY, Effort: Low - byte identity, no dropped-tool names

### SHOULD TEST (important, automated where cheap)

- **Provider adapters** - Testability: MEDIUM (live keys), Effort: Medium - round trips, cache hits, Responses reasoning regression
- **Prompt system loader against real DevSystemV4.2** - Testability: EASY (skip-if-absent), Effort: Low
- **Cost math** - Testability: EASY, Effort: Low
- **Web tools** - Testability: MEDIUM (network), Effort: Medium - fetch/chunk against a local HTTP fixture server where possible, live search in smoke only

### DROP (not worth automating)

- **rich rendering pixel/layout output** - Reason: formatting-only; events carry the tested substance
- **prompt_toolkit interactive keybindings** - Reason: terminal-dependent; non-terminal path is tested, interactive path covered by manual acceptance (IP01 TC-47)
- **Provider SDK internals (retries, HTTP)** - Reason: external dependency, SDK-tested upstream

## 5. Test Data

**Required Fixtures:**
- `fake_system/` - minimal prompt system: 3 rules (one empty, one oversized, one normal with `trigger: always_on`), 3 workflows (`hello.md`, `tooluse.md`, `prime-like.md`), 2 skills (one with supporting files)
- `scripts/*.jsonl` - scripted adapter turn scripts per scenario (IS-22 format); naming: `script_[scenario].jsonl`
- `config_test.json` - LanaConfig pointing at `fake_system/`, tiny thresholds for compaction scenarios (e.g., `compaction_threshold_max_tokens: 500`)
- Local HTTP fixture server (pytest fixture) serving one HTML page and one binary blob for `read_url_content` tests
- Live-key markers: pytest marker `live` auto-skipped unless both provider keys resolve

**Setup:** per-test temp workspace (`tmp_path`), copy `fake_system/` + write `config_test.json`, set `LANA_SCRIPTED_ADAPTER` + `LANA_CONFIG` env for the subprocess.

**Teardown:** terminate any surviving `lana` subprocess (kill after 5 s grace); temp folders removed by pytest; no global state.

## 6. Test Cases

Black-box scenarios (Layer 3). Each drives the real CLI and cites the requirements it proves. Unit/integration inventory stays in `LANAAGNT-IP01` section 5 (TC-01..63).

### Category 1: Conversation Scenarios (3 tests)

- **LANAAGNT-TP01-TC-01**: Workflow round trip - `lana -p "/tooluse"` with a script calling `read_file` + `write_to_file` -> events show expansion, 2 tool calls, created file exists with expected content; exit 0 (FR-04, FR-05, IG-02)
- **LANAAGNT-TP01-TC-02**: Multi-turn piped session - 3 prompts via stdin pipe -> 3 `turn_finished` events, session file replays to identical state via `--resume` + `/cost` (FR-08, IG-06)
- **LANAAGNT-TP01-TC-03**: Todo lifecycle - script calls `todo_list` twice then compaction fires (tiny threshold config) -> checkpoint event carries second todo state byte-identical (FR-07, IG-04)

### Category 2: Safety Scenarios (2 tests)

- **LANAAGNT-TP01-TC-04**: Destructive command blocked end-to-end - script requests `Remove-Item x` under `--policy auto` headless -> denied result event, no file deleted, agent continues, exit 0 (FR-12, FR-14, IG-03)
- **LANAAGNT-TP01-TC-05**: Out-of-workspace write blocked - script requests `write_to_file` outside temp workspace headless -> denied, target absent (FR-12)

### Category 3: Robustness Scenarios (2 tests)

- **LANAAGNT-TP01-TC-06**: Kill and resume - harness kills the process mid-script (after 2nd `tool_call_finished` observed via tail), then `--resume` -> prior events intact, skipped-line count 0 or 1, continuation works (NFR-02, EC-21)
- **LANAAGNT-TP01-TC-07**: Oversized tool output - script triggers `run_command` echoing 200K chars (approved via `--policy turbo` with benign command) -> result event capped at 50K with marker, next turn succeeds (FR-04, RF-03 regression)

### Category 4: Real Prompt System Scenario (1 test)

- **LANAAGNT-TP01-TC-08**: DevSystemV4.2 startup + `/help` via pipe (skip if folder absent) -> banner reports filesystem-derived counts (8/46/21 at analysis; the folder evolves - counts computed at test time), workflow list contains `prime` and `verify`, startup under 2 s (FR-02, NFR-03)

### Category 5: Diagnostics and Exit Codes (2 tests)

- **LANAAGNT-TP01-TC-09**: `--debug` run with fake key values in env -> request/response JSON files exist under the temp workspace `.lana/logs/`, `assert_no_secret_leak` passes over log contents, events carry timestamps (NFR-01, NFR-04)
- **LANAAGNT-TP01-TC-10**: Exit code semantics - script with `{"error": ...}` line -> exit 3 with provider-style message; script exceeding `max_tool_calls_per_prompt` headless with `auto_continue: false` -> exit 4 (FR-14)

## 7. Test Phases

1. **Phase T1: Offline foundation** - IP01 TC-01..39, TC-48..49, TC-56..57, TC-59..63 (Layers 1-2), run on every change, no keys, no network
2. **Phase T2: Black-box CLI** - IP01 TC-50..55, TC-58 + TP01-TC-01..10 (Layer 3), scripted adapter, no keys; requires `pip install -e .`
3. **Phase T3: Live smoke** - IP01 TC-40..45 (Layer 4), keys present, marker `live`, budget-capped
4. **Phase T4: Acceptance** - IP01 TC-46 offline end-to-end + TC-47 manual live run against DevSystemV4.2; results recorded in PROGRESS.md

Dependency: T2 requires T1 green; T3/T4 require T2 green. T1+T2 are the continuous integration (CI) gate (VC below).

## 8. Helper Functions

```python
# tests/harness.py - the automated CLI driver (IP01 IS-22)
class LanaProc:
    def start(workspace, config, script, args) -> LanaProc: ...   # spawn real executable, env wired
    def send(line) -> None: ...                                   # stdin prompt injection (piped mode)
    def events() -> list[AgentEvent]: ...                         # parsed stdout JSONL (--output-format jsonl)
    def tail_session(predicate, timeout_s=5) -> AgentEvent: ...   # poll flushed session file (FR-08 contract)
    def wait_exit(timeout_s=30) -> int: ...                       # exit code (FR-14 semantics)
# assertions
def assert_event_sequence(events, expected_subsequence): ...      # ordered match, ids/timestamps masked
def assert_no_secret_leak(all_outputs, key_values): ...           # NFR-01: key material absent everywhere
```

## 9. Cleanup

- Surviving `lana` subprocesses (harness teardown kills after grace period)
- Temp workspaces and session files (pytest `tmp_path` auto-removal)
- `.lana/logs/` debug output inside temp workspaces only - never in the real workspace
- Live smoke sessions: no cleanup needed (temp workspaces); spend reported in test summary

## 10. Verification Checklist

- [x] **LANAAGNT-TP01-VC-01**: Phases T1+T2 green locally with zero keys configured (proves offline completeness)
- [x] **LANAAGNT-TP01-VC-02**: All 10 TP01 scenarios pass against the installed executable (not in-process imports)
- [x] **LANAAGNT-TP01-VC-03**: Coverage contract - every SPEC FR-01..14 and IG-01..06 is cited by at least one passing IP01 TC or TP01 TC (traceability sweep over both documents)
- [x] **LANAAGNT-TP01-VC-04**: `assert_no_secret_leak` wired into every black-box scenario (NFR-01)
- [x] **LANAAGNT-TP01-VC-05**: T3 live smoke green with keys; spend under budget cap
- [x] **LANAAGNT-TP01-VC-06**: T4 acceptance executed; deviations synced back to SPEC/IMPL via `/sync`

## 11. Document History

**[2026-08-30 06:20]**
- Changed: IP01 case count 60 → 63 (Category 12 trajectory search TC-61..63 for the 16th tool, SP01 FR-15); T1 range extended

**[2026-08-30 04:15]**
- Changed (`/sync` Code→TEST): IP01 case count 55 → 60 (Category 11 synced regressions TC-56..60), TC-08 asserts filesystem-derived counts instead of the 8/46/21 snapshot (DevSystemV4.2 evolved to 23 skills - the hardcoded assertion broke and was de-hardcoded during `/improve` run 1)

**[2026-08-30 02:10]**
- Changed: all 6 VC items checked - T1 (120 unit/integration), T2 (41 black-box incl. all 10 TP01 scenarios), T3 (4 live smokes, spend well under $1), T4 (offline e2e + live acceptance automated portion) green
- Changed: TP01-TC-09 scope note - with the scripted adapter no provider request JSON is produced, so the redaction assertion covers logs-dir creation + secret-leak sweep over stdout/session/logs; full request-JSON redaction is exercised only in live runs with `--debug`
- Changed: manual-only residue of TC-47 documented in PROGRESS.md - interactive approval y/n and Ctrl+C cancellation are terminal-only by FR-14 design (piped stdin auto-denies)

**[2026-08-29 22:30]**
- Added: Category 5 Diagnostics and Exit Codes (TC-09 --debug redaction for NFR-04, TC-10 exit codes 3/4 for FR-14) - coverage gaps against the VC-03 contract found by `/verify`
- Changed: scenario count 8 -> 10 in Strategy/Phases/VC-02; expanded CI and end-to-end acronyms

**[2026-08-29 22:25]**
- Initial test plan created: 4-layer strategy, 8 black-box scenarios (TP01-TC-01..08), harness contract, coverage checklist; companion gap closure in LANAAGNT-SP01 (FR-14, FR-08 flush, DD-20) and LANAAGNT-IP01 (IS-21/IS-22, TC-50..55)
