# TEST: Lana Agent Core - Verification Plan

**Doc ID**: LANACORE-TP01
**Goal**: Define black-box CLI scenarios proving the agent turn loop, session persistence, checkpoint compaction, and command safety satisfy LANACORE-SP01
**Timeline**: Created 2026-08-29, Extracted from _TEST_LANA_MVP-1.md 2026-09-01

**Target file(s)**:
- `tests/test_agent.py` (loop + safety integration)
- `tests/test_session.py` (persistence + resume)
- `tests/test_compaction.py` (projection + checkpoint)
- `tests/test_full_recall.py` (FR-08 end-to-end)

**Depends on:**
- `_SPEC_LANA_02-AgentCore.md [LANACORE-SP01]` for FR-04, FR-05, FR-07, FR-08, FR-12, IG-02..04, IG-06..07
- `_IMPL_LANA_02-AgentCore.md [LANACORE-IP01]` for IS-09, IS-13, IS-14, IS-17, IS-24 and edge cases
- `_TEST_LANA_01-ProductOverview.md [LANAAGNT-TP01]` for test strategy, harness, and fixtures

**Does not depend on:**
- `_TEST_LANA_05-Tools.md [LANATOOL-TP01]` (tool-specific tests are separate; AgentCore tests use tools only as loop drivers)

## MUST-NOT-FORGET

- Every black-box scenario runs the REAL `lana` executable via `tests/harness.py` - no in-process shortcuts
- Scripted adapter = determinism; live-key tests are a separate, skippable phase
- Test workspaces are temp folders with their own `--config`
- All scenario fixtures use generic content (Privacy Gate)

## Table of Contents

1. [Test Cases](#1-test-cases)
2. [Verification Checklist](#2-verification-checklist)
3. [Document History](#3-document-history)

## 1. Test Cases

Black-box scenarios (Layer 3) proving AgentCore requirements. Unit/integration inventory in `_IMPL_LANA_02-AgentCore.md [LANACORE-IP01]` section 3.

### Category 1: Conversation Scenarios (3 tests)

- **LANAAGNT-TP01-TC-01**: Workflow round trip - `lana -p "/tooluse"` with a script calling `read_file` + `write_to_file` -> events show expansion, 2 tool calls, created file exists with expected content; exit 0 (FR-04, FR-05, IG-02)
- **LANAAGNT-TP01-TC-02**: Multi-turn piped session - 3 prompts via stdin pipe -> 3 `turn_finished` events, session file replays to identical state via `--resume` + `/cost` (FR-08, IG-06)
- **LANAAGNT-TP01-TC-03**: Todo lifecycle - script calls `todo_list` twice then compaction fires (tiny threshold config) -> checkpoint event carries second todo state byte-identical (FR-07, IG-04)

### Category 2: Safety Scenarios (3 tests)

- **LANAAGNT-TP01-TC-04**: Destructive command blocked end-to-end - script requests `Remove-Item x` under `--policy auto` headless -> denied result event, no file deleted, agent continues, exit 0 (FR-12, FR-14, IG-03)
- **LANAAGNT-TP01-TC-05**: Out-of-workspace write blocked - script requests `write_to_file` outside temp workspace headless -> denied, target absent (FR-12)
- **LANAAGNT-TP01-TC-12**: Approve-all (`a`) skips subsequent prompts - in-process integration (approval prompts are terminal-only per FR-14; no piped-stdin path) with scripted 3 consecutive `run_command` calls under `--policy manual`; callback returns `"all"` on first call -> first `approval_required` event shows `approved: true`, remaining 2 `approval_required` events also show `approved: true` with callback not called again; next `run_prompt` call does NOT reset the flag (session-scoped) (FR-12)

### Category 3: Robustness Scenarios (2 tests)

- **LANAAGNT-TP01-TC-06**: Kill and resume - harness kills the process mid-script (after 2nd `tool_call_finished` observed via tail), then `--resume` -> prior events intact, skipped-line count 0 or 1, continuation works (NFR-02, EC-21)
- **LANAAGNT-TP01-TC-07**: Oversized tool output - script triggers `run_command` echoing 200K chars (approved via `--policy turbo` with benign command) -> result event capped at 50K with marker, next turn succeeds (FR-04, RF-03 regression)

### Category 6: Full-Recall Resume Scenario (1 test)

- **LANAAGNT-TP01-TC-11**: Environment survives resume end-to-end - run a scripted session, then 1) DELETE a rule file from the fake prompt system, 2) change the generator `model_id` in the config, 3) `--resume` -> stderr shows the fingerprint mismatch warning and the model-change report; the session JSONL `session_started` line still carries the original system prompt; a follow-up prompt succeeds with the RECORDED environment (captured request byte-identical to pre-restart) (FR-08, IG-06, IG-07, DD-22)

## 2. Verification Checklist

- [x] **LANACORE-TP01-VC-01**: All 9 TP01 scenarios covering AgentCore pass (TC-01..07, TC-11, TC-12)
- [x] **LANACORE-TP01-VC-02**: Coverage contract - FR-04, FR-05, FR-07, FR-08, FR-12, IG-02..04, IG-06..07 each cited by at least one passing TC
- [x] **LANACORE-TP01-VC-03**: `assert_no_secret_leak` wired into every black-box scenario (NFR-01)

## 3. Document History

**[2026-09-01 21:45]**
- Extracted from `_TEST_LANA_MVP-1.md [LANAAGNT-TP01]`: Categories 1 (Conversation), 2 (Safety), 3 (Robustness), 6 (Full-Recall Resume)
- Content is verbatim from source with section renumbering and header block update only
