# TEST: Lana MVP-2 - Automated Verification of the ACP Frontend

**Doc ID**: LANAACPB-TP01
**Feature**: acp-frontend
**Goal**: Define the automated test system proving the ACP frontend satisfies LANAACPB-SP01, with a fake ACP client driving the real `lana --acp` executable as the primary black-box layer
**Timeline**: Created 2026-08-30, Updated 0 times
**Target file(s)**:
- `tests/acp_harness.py`, `tests/test_acp_*.py` (per LANAACPB-IP01 File Structure)

**Depends on:**
- `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` rev 2026-08-30 14:00 for requirements
- `_IMPL_LANA_MVP-2_ACP.md [LANAACPB-IP01]` rev 2026-08-30 14:05 for the unit/integration test cases (TC-01..43) and phases
- `_INFO_LANAACPB-IN01_AcpV1WireShapeVerification.md [LANAACPB-IN01]` for wire fixtures (authority over the local doc snapshots)
- `_TEST_LANA_MVP-1.md [LANAAGNT-TP01]` for the existing harness contract and layer definitions

## MUST-NOT-FORGET

- IP01 owns unit/integration cases (LANAACPB-IP01-TC-01..44); this plan owns black-box scenarios (LANAACPB-TP01-TC-*) and the coverage contract - never duplicate case definitions across the two documents
- Every black-box scenario runs the REAL `lana --acp` executable over actual stdio pipes - no in-process shortcuts
- Wire fixtures transcribe LANAACPB-IN01 verified shapes - NOT the 2026-08-30 doc snapshot (4+ hallucinated shapes, PR-0001)
- Scripted adapter = determinism; no provider calls in T1-T3
- All fixtures use generic content (Privacy Gate) - no real names, keys, or personal data
- Cross-frontend equivalence (IG-02) needs scenarios in BOTH directions: ACP session → CLI resume AND CLI session → ACP load

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

Three automated layers verify the ACP frontend: unit (jsonrpc framing/correlation, no subprocess), integration (server components against the harness), and **black-box ACP client** (a fake client speaking real JSON-RPC over the spawned executable's stdio - the layer this plan specifies in scenarios). A manual acceptance phase against a real ACP client (Zed) closes the loop. The MVP-1 layers (LANAAGNT-TP01) keep running unchanged - TC-40 in IP01 gates the `agent.py` callback seam against them.

## 2. Scenario

**Problem:** An ACP agent is normally tested by clicking through an editor - handshake mistakes, wrong wire shapes, and deadlocks in bidirectional request flows (permission round-trips blocking the turn while cancellation arrives) only surface interactively. Worse, our protocol reference docs contained hallucinated shapes (PR-0001) - tests asserting against wrong fixtures would pass while every real client fails.

**Solution:**
- A fake ACP client (`acp_harness.py`) that spawns `lana --acp`, exchanges newline-delimited JSON-RPC, auto-responds to agent-bound requests per scenario policy, and records the full wire transcript
- Wire fixtures transcribed from LANAACPB-IN01 live-verified shapes; byte-structural comparison (field names, nesting, discriminators - ids and timestamps masked)
- Deterministic turns via the scripted adapter; observation via the wire transcript, the session JSONL, and stderr

**What we don't want:**
- Fixtures copied from the 2026-08-30 doc snapshot (hallucination risk - LANAACPB-IN01 is the authority)
- A real editor in CI - Zed stays in the manual acceptance phase
- In-process AcpServer tests as a REPLACEMENT for subprocess scenarios (stdio framing, flushing, and encoding bugs only show on real pipes)
- Sleep-based waits - the harness reads until expected message or timeout

## 3. Test Strategy

**Approach**: unit + integration + black-box ACP client (scripted) + manual acceptance, mapped to IP01 phases:

- **Layer 1 Unit** (IP01 TC-01..06, TC-44): jsonrpc parse/serialize/correlation, translator exhaustiveness - in-process, no subprocess
- **Layer 2 Integration** (IP01 TC-07..43 minus Layer 1): handshake, sessions, turns, brokers, cancellation - harness-driven subprocess per category
- **Layer 3 Black-box scenarios** (TP01-TC-01..10 below): multi-step end-to-end flows across the real executable - the automated equivalent of an editor driving Lana
- **Layer 4 Manual acceptance** (TP01-TC-11): real ACP client (Zed) against a live-configured Lana

**Verification style**: wire-transcript assertions (ordered subsequence, byte-structural fixture match with ids/timestamps masked), session-JSONL assertions (event types + payloads), stderr assertions (warnings present, stdout purity), exit-code assertions.

## 4. Test Priority Matrix

### MUST TEST (critical logic, automated)

- **stdout purity** (IG-01) - Testability: EASY, Effort: Low - one non-JSON byte breaks every client; sweep every scenario's stdout
- **Wire shape conformance** (NFR-01) - Testability: EASY (fixtures), Effort: Medium - the PR-0001 lesson: wrong shapes pass self-tests and fail every client
- **Permission bridge** (FR-08, IG-04) - Testability: EASY (harness auto-responder), Effort: Medium - the security control point in ACP mode
- **Cancellation under blocked round-trips** (FR-10, IG-05) - Testability: MEDIUM (timing), Effort: High - deadlock-prone bidirectional flow; the hardest bug class
- **Cross-frontend session equivalence** (IG-02) - Testability: EASY, Effort: Medium - one JSONL, two frontends, both directions
- **Baseline content acceptance** (FR-05) - Testability: EASY, Effort: Low - rejecting `resource_link` breaks file mentions in every editor

### SHOULD TEST (important, automated where cheap)

- **Handshake state machine** (FR-02) - Testability: EASY, Effort: Low
- **Elicitation round-trip** (FR-09) - Testability: EASY, Effort: Low
- **Wire error handling** (FR-11) - Testability: EASY, Effort: Low - hostile-client battery
- **Crash-safe parity** (NFR-03) - Testability: MEDIUM (kill timing), Effort: Medium

### DROP (not worth automating)

- **Streaming latency** (NFR-04) - Reason: no-buffering is a code-review property (write+flush per event); latency assertions flake in CI
- **Real editor UI rendering** - Reason: client-side concern; the wire contract is the boundary
- **`$/cancel_request` cross-direction cascades to client-owned requests** - Reason: MVP-2 issues no client-bound requests outside permission/elicitation, both covered

## 5. Test Data

**Required Fixtures:**
- `fake_system/` - reused from MVP-1 (rules/workflows/skills)
- `scripts/script_acp_*.jsonl` - scripted adapter turns per scenario (text-only, tool call, todo_list, ask_user_question, denylisted command, slow tool, provider error)
- `fixtures/acp_wire/*.json` - expected wire shapes transcribed from LANAACPB-IN01: initialize response, tool_call/tool_call_update, request_permission, usage_update, elicitation/create, prompt response
- Client capability profiles: `full` (elicitation.form present), `bare` (no optional capabilities)
- Fake key values in env for the secret-leak sweep

**Setup:** per-test temp workspace, `fake_system/` + `config_test.json` copied, `LANA_SCRIPTED_ADAPTER` + `LANA_CONFIG` env, harness spawns `lana --acp` and completes the handshake (except handshake-order scenarios).

**Teardown:** close stdin (clean EOF exit expected), kill after 5 s grace; pytest `tmp_path` auto-removal.

## 6. Test Cases

Black-box scenarios (Layer 3). Each drives the real executable end-to-end and cites the requirements it proves. Unit/integration inventory stays in `LANAACPB-IP01` section 5 (TC-01..44).

### Category 1: Protocol Conformance (2 tests)

- **LANAACPB-TP01-TC-01**: Full happy path - initialize → initialized → session/new → prompt (scripted: text + read_file call + todo_list) → wire transcript contains handshake response, available_commands_update, agent_message_chunk stream (stable messageId), tool_call/tool_call_update pairs, plan update, usage_update, `{stopReason: "end_turn"}`; EVERY stdout line parses as JSON-RPC; EOF → exit 0 (FR-01..03, FR-05..07, IG-01, DD-08)
- **LANAACPB-TP01-TC-02**: Fixture conformance - each recorded wire message byte-structurally matches its `fixtures/acp_wire/` counterpart (ids/timestamps/dynamic text masked) (NFR-01)

### Category 2: Cross-Frontend Equivalence (2 tests)

- **LANAACPB-TP01-TC-03**: ACP → CLI - session created and driven via ACP, then `lana --resume <file> -p "/cost"` → resume succeeds, message count and cost totals match the ACP-driven turns (IG-02, LANAAGNT-FR-08)
- **LANAACPB-TP01-TC-04**: CLI → ACP - session created via `lana -p` (scripted tool turn), then `session/load` over ACP → replay stream carries user_message_chunk + agent chunks + tool pairs in original order, then a follow-up ACP prompt succeeds with the RECORDED environment (LANA_SCRIPTED_CAPTURE oracle) (FR-04, IG-02, LANAAGNT-IG-07)

### Category 3: Permission and Elicitation Round-Trips (3 tests)

- **LANAACPB-TP01-TC-05**: Denylisted command end-to-end - scripted `Remove-Item x` under `--policy turbo`; fake client answers `reject_once` → denial in tool result and session JSONL, file untouched, turn completes `end_turn` (FR-08, IG-04, EC-21)
- **LANAACPB-TP01-TC-06**: Elicitation answer reaches the model - scripted `ask_user_question` with `full` capability profile; client answers `accept` with a value → next generator request (capture oracle) carries the selected value in the tool result; `bare` profile variant → fallback string, zero elicitation requests (FR-09, EC-20)
- **LANAACPB-TP01-TC-07**: allow_always memory across turns - two prompts, same command; client answers `allow_always` on the first → second turn executes without a second permission request; new process (fresh session) asks again (FR-08 in-memory scope)

### Category 4: Cancellation and Robustness (3 tests)

- **LANAACPB-TP01-TC-08**: Cancel while blocked on permission - scripted command turn; harness delays the permission response, sends `session/cancel`, then responds → pending request resolved as cancelled, `{stopReason: "cancelled"}`, session JSONL replayable via CLI `--resume` afterwards (FR-10, IG-05, EC-10)
- **LANAACPB-TP01-TC-09**: Kill mid-turn - harness kills the process after the first `tool_call_update` → session JSONL intact (0-1 skipped lines), fresh `lana --acp` process loads the session and completes a new turn (NFR-03)
- **LANAACPB-TP01-TC-10**: Hostile client battery in one connection - garbage line (`-32700`), unknown method (`-32601`), `session/prompt` before handshake (error), image content block (`-32602`), then a VALID full turn → all errors correct, connection alive, turn green; secret-leak sweep over stdout+stderr+session file with fake key values (FR-11, NFR-02)

### Category 5: Real Client Acceptance (1 test, manual)

- **LANAACPB-TP01-TC-11**: Zed drives Lana - register `lana --acp` in Zed `agent_servers` (with env for keys), run a live prompt with a file mention (resource_link), approve one command, cancel one turn → interactions render correctly, no client errors; results and any deviations recorded in PROGRESS.md (VC-11 of IP01; skippable when no Zed available - scripted replay documented instead)

## 7. Test Phases

1. **Phase T1: Unit** - IP01 TC-01..06 + TC-44 (Layer 1), on every change, no subprocess
2. **Phase T2: Integration** - IP01 TC-07..43 (Layer 2), harness-driven, scripted adapter, no keys
3. **Phase T3: Black-box scenarios** - TP01-TC-01..10 (Layer 3), requires `pip install -e .`
4. **Phase T4: Regression + acceptance** - full MVP-1 suite (179 offline, IP01 TC-40 gate) + TP01-TC-11 manual

Dependency: T2 requires T1 green; T3 requires T2 green; T4 requires T3 green. T1-T3 + the MVP-1 offline suite are the CI gate.

## 8. Helper Functions

```python
# tests/acp_harness.py - the fake ACP client (IP01 File Structure)
class AcpClient:
    def start(workspace, config, script, capabilities="full") -> AcpClient: ...  # spawn `lana --acp`, wire env
    def handshake() -> dict: ...                      # initialize -> initialized; returns agent capabilities
    def request(method, params, timeout_s=10) -> dict: ...   # send request, read until response (collecting notifications)
    def notify(method, params) -> None: ...
    def send_raw(line) -> None: ...                   # hostile-client injection
    def on_agent_request(policy) -> None: ...         # auto-responder: permission/elicitation answers per scenario
    def transcript() -> list[dict]: ...               # full ordered wire log, both directions
    def stderr_text() -> str: ...
    def wait_exit(timeout_s=30) -> int: ...
# assertions
def assert_wire_match(message, fixture_name): ...     # byte-structural, ids/timestamps/dynamic text masked
def assert_stdout_pure(transcript_raw): ...           # IG-01: every stdout line parses as JSON-RPC
def assert_no_secret_leak(outputs, key_values): ...   # reused from MVP-1 harness
```

## 9. Cleanup

- Surviving `lana --acp` subprocesses (stdin close → EOF exit; kill after grace period)
- Temp workspaces and session files (pytest `tmp_path` auto-removal)
- No global state; the real `config/lana-config.json` and IPPS never touched

## 10. Verification Checklist

- [x] **LANAACPB-TP01-VC-01**: Phases T1-T3 green locally with zero keys configured (227 offline, harness pops key env)
- [x] **LANAACPB-TP01-VC-02**: All 10 automated TP01 scenarios pass - mapping: TC-01/07/09/10 in test_acp_scenarios.py; TC-02 via structural equality asserts (TC-07/16/24/27 exact shapes); TC-03/04 in test_acp_load.py (tc35/tc36); TC-05 = turn TC-29; TC-06 = turn TC-27/28; TC-08 = turn TC-31
- [x] **LANAACPB-TP01-VC-03**: Coverage contract - every SP01 FR-01..11, IG-01..05, NFR-01..03 cited by at least one passing case (NFR-04 dropped with reason, section 4)
- [x] **LANAACPB-TP01-VC-04**: `assert_stdout_pure` in purity-relevant scenarios + `assert_no_secret_leak` in the hostile battery (TC-10); every stdout line of every harness run parses via the AcpClient pump
- [x] **LANAACPB-TP01-VC-05**: MVP-1 regression - full 179-test offline suite green after all ACP changes (IP01 TC-40 gate)
- [ ] **LANAACPB-TP01-VC-06**: TC-11 acceptance executed (or scripted-replay fallback documented); deviations synced back to SPEC/IMPL via `/sync`

## 11. Document History

**[2026-08-30 15:10]**
- Changed: VC-01..05 checked - 48 ACP tests green (8 unit + 9 handshake + 21 turn + 6 load + 4 scenarios), full suite 227 offline; TC-11 (real Zed client) remains the only open item

**[2026-08-30 14:35]**
- Initial test plan created: 4-layer strategy on top of IP01 TC-01..44, 10 automated black-box scenarios + 1 manual acceptance, AcpClient harness contract, wire fixtures anchored to LANAACPB-IN01 (not the doc snapshot - PR-0001 lesson), coverage contract incl. both-direction IG-02 equivalence
