# TASKS: LANAAGNT Tasks Plan - Lana MVP-1 Implementation

**Doc ID**: LANAAGNT-TK01
**Feature**: lana-mvp-1
**Goal**: Partitioned tasks for the Lana MVP-1 implementation, dependency-ordered, max 0.5 human hours of work (HHW) each
**Timeline**: Created 2026-08-29, Updated 0 times
**Target file(s)**:
- `pyproject.toml`, `README.md`, `config/lana-config.json`, `src/lana/` (22 modules), `tests/` (per LANAAGNT-IP01 File Structure)
**Source**: `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` rev 22:30, `_TEST_LANA_MVP-1.md [LANAAGNT-TP01]` rev 22:30, `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` rev 22:20
**Strategy**: PARTITION-DEPENDENCY

## Task Overview

- Total tasks: 36 (34 work tasks + Task 0 baseline + final verification)
- Estimated total: ~16 HHW [ASSUMED - derived from IP01 module line estimates]
- Parallelizable: 15 tasks marked [P]
- Commit cadence: after every green task (IP01 MNF "small cycles"); phase completion = IP01 VC gate

## Task 0 - Baseline (MANDATORY)

Run before starting any implementation:
- [x] Record environment baseline: Python version (3.12+ required), `pip --version`, empty `src/` confirmed, no pre-existing tests (greenfield - baseline is the clean state)
- [x] Confirm read access to `e:\Dev\IPPS\DevSystemV4.2` and the 4 `config/*.json` inputs
- [x] Note: API keys NOT required until TK-016/TK-017 (Phase D live smokes); all of A-C and the scripted-adapter path through E-G run key-free

## Task Execution Protocol

Applies to every task. Purpose: a ~16-HHW implementation spans sessions and context compactions - each task must be executable from its documented sources, never from conversation memory (lesson: session FAILS.md `LANAAGNT-FL-0002`, `LANAAGNT-FL-0003`).

**Before starting a task:**
1. Re-read the IP01 implementation step(s) cited in the task's phase heading and the FR/IG items cited in `Done when`/`Guardrails`
2. TK-008/TK-009 only: open `_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02]` - transcribe from it, never from memory
3. Re-read session `FAILS.md` Active Issues (30 seconds; skip if read this session)

**During a task:**
4. Small cycles: implement -> run the task's `Verify` command -> fix -> green; never start the next task on red
5. Deviation from IP01/SP01 discovered? Record in PROBLEMS.md immediately; do not silently improvise

**After a task:**
6. Commit: `feat(lana): TK-NNN <task description>` (one task = one commit; `/commit` conventions apply)
7. Tick the task checkbox here and update the PROGRESS.md phase line
8. Phase complete? Check the corresponding IP01 VC gate before entering the next phase

## Tasks

### Phase A: Foundation (IP01 IS-01..03)

- [x] **LANAAGNT-TK-001** - Package skeleton: pyproject.toml, README.md, entry point, module stubs
  - Files: `pyproject.toml`, `README.md`, `src/lana/__init__.py`, `__main__.py`, empty modules
  - Done when: `pip install -e .` clean and `lana --help` prints (IS-01 gate)
  - Verify: `pip install -e . ; lana --help`
  - Depends: none
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-002** - Canonical conversation model
  - Files: `src/lana/models.py`
  - Done when: Message/ToolCall/ThinkingBlock/Usage types validate and round-trip (IS-02)
  - Verify: `pytest tests/test_models.py`
  - Depends: TK-001
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-003** - AgentEvent types and JSONL serialization
  - Files: `src/lana/events.py`
  - Done when: all 10 event types serialize/deserialize; `checkpoint_created` carries payload (IS-02)
  - Verify: `pytest tests/test_events.py`
  - Depends: TK-002
  - Parallel: [P] (with TK-004)
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-004** - Configuration loading and validation
  - Files: `src/lana/config.py`, `config/lana-config.json`
  - Done when: IP01 TC-01..06 green (registry validation, key precedence, effort translation, pricing tolerance) (IS-03)
  - Verify: `pytest tests/test_config.py`
  - Guardrails: existing `config/*.json` opened read-only; never log key material
  - Depends: TK-001
  - Parallel: [P]
  - Est: 0.5 HHW

### Phase B: Prompt System (IP01 IS-04..05)

- [x] **LANAAGNT-TK-005** - PromptSystem loader
  - Files: `src/lana/loader.py`
  - Done when: IP01 TC-07..12 green (frontmatter tolerance, empty/oversized rules, precedence, real DevSystemV4.2 8/46/21 in < 2 s) (IS-04)
  - Verify: `pytest tests/test_loader.py`
  - Depends: TK-001
  - Parallel: [P]
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-006** - System prompt section constants
  - Files: `src/lana/prompt.py`
  - Done when: adapted Cascade behavioral sections + `<capability_notice>` stored as constants; zero dropped-tool references (IS-05)
  - Verify: `pytest tests/test_prompt.py -k tc14`
  - Guardrails: no datetime/cwd in any constant (IG-01)
  - Depends: TK-001
  - Parallel: [P]
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-007** - System prompt assembly
  - Files: `src/lana/prompt.py`
  - Done when: IP01 TC-13..15 green (byte identity, section order per FR-03) (IS-05)
  - Verify: `pytest tests/test_prompt.py`
  - Depends: TK-005, TK-006
  - Est: 0.25 HHW

### Phase C: Tools (IP01 IS-06..10)

- [x] **LANAAGNT-TK-008** - Tool definitions transcription 1/2: file reading + editing (8 tools)
  - Files: `src/lana/tools/definitions.py`
  - Done when: read_file, list_dir, grep_search, find_by_name, edit, multi_edit, write_to_file, run_command match `LANAAGNT-IN02` with zero diff outside substitution points (IS-06)
  - Verify: diff-check script vs IN02 blocks
  - Guardrails: transcription only - never paraphrase (IN02 [LITERAL])
  - Depends: TK-001
  - Parallel: [P]
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-009** - Tool definitions transcription 2/2: remaining 7 + registry
  - Files: `src/lana/tools/definitions.py`, `src/lana/tools/__init__.py`
  - Done when: command_status, todo_list, skill, ask_user_question, search_web, read_url_content, view_content_chunk transcribed; registry dispatches by name; deterministic schema serialization (IS-06)
  - Verify: diff-check + `pytest tests/test_tools_registry.py`
  - Depends: TK-008
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-010** - File reading tool executors
  - Files: `src/lana/tools/file_tools.py`
  - Done when: IP01 TC-16..18, TC-23 green (cat-n format, caps, shared `cap_result()`) (IS-07)
  - Verify: `pytest tests/test_file_tools.py`
  - Depends: TK-009
  - Parallel: [P]
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-011** - Edit tool executors with ReadLedger
  - Files: `src/lana/tools/edit_tools.py`
  - Done when: IP01 TC-19..22 green (read gate, mtime staleness, atomicity, create-only) (IS-08)
  - Verify: `pytest tests/test_edit_tools.py`
  - Depends: TK-009
  - Parallel: [P]
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-012** - Safety classifier
  - Files: `src/lana/safety.py`
  - Done when: IP01 TC-26..30 green (first-token + alias + wrapper + policy matrix) (IS-09)
  - Verify: `pytest tests/test_safety.py`
  - Guardrails: IG-03 - denylist match must be un-bypassable by policy or SafeToAutoRun
  - Depends: TK-004
  - Parallel: [P]
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-013** - Shell tool executors
  - Files: `src/lana/tools/shell_tools.py`
  - Done when: run_command (pwsh, Blocking/WaitMsBeforeAsync) + command_status (background table) work; TC-31 green (IS-09)
  - Verify: `pytest tests/test_shell_tools.py`
  - Depends: TK-009, TK-012
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-014** - State, skill, interaction tool executors
  - Files: `src/lana/tools/state_tools.py`, `skill_tool.py`, `interact_tools.py`
  - Done when: IP01 TC-24 (byte-stable todo rendering), TC-25 green (IS-10)
  - Verify: `pytest tests/test_state_tools.py tests/test_skill_tool.py`
  - Depends: TK-009, TK-005
  - Parallel: [P]
  - Est: 0.5 HHW

### Phase D: Provider Adapters (IP01 IS-11..12) - first tasks needing API keys

- [x] **LANAAGNT-TK-015** - Adapter protocol and selection
  - Files: `src/lana/providers/base.py`, `providers/__init__.py`
  - Done when: `stream_turn` protocol defined; selection by registry provider field; `LANA_SCRIPTED_ADAPTER` env hook present (IS-11, IS-22)
  - Verify: `pytest tests/test_providers_base.py`
  - Depends: TK-002, TK-004
  - Est: 0.25 HHW

- [x] **LANAAGNT-TK-016** - OpenAI Responses adapter
  - Files: `src/lana/providers/openai_adapter.py`
  - Done when: typed output parsing, reasoning items resent, effort/temperature per registry method (IS-11)
  - Verify: `pytest tests/test_adapters.py -m live -k openai` (TC-40, TC-42)
  - Depends: TK-015
  - Parallel: [P] (with TK-017)
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-017** - Anthropic Messages adapter with caching
  - Files: `src/lana/providers/anthropic_adapter.py`
  - Done when: thinking resend, cache_control breakpoints + automatic caching, usage capture (IS-12)
  - Verify: `pytest tests/test_adapters.py -m live -k anthropic` (TC-41: cache_read > 0 on call 2)
  - Depends: TK-015
  - Parallel: [P]
  - Est: 0.5 HHW

### Phase E: Loop, Session, CLI (IP01 IS-13..15, IS-21..22)

- [x] **LANAAGNT-TK-018** - Scripted adapter and turn scripts
  - Files: `tests/scripted_adapter.py`, `tests/scripts/*.jsonl`, `tests/conftest.py`
  - Done when: replay of text/thinking/tool_calls/usage/error lines per IS-22 format; conftest fixtures (temp workspace, fake_system, config_test)
  - Verify: `pytest tests/test_scripted_adapter.py`
  - Depends: TK-015
  - Parallel: [P] (with TK-016/017 - no keys needed)
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-019** - Agent turn loop core
  - Files: `src/lana/agent.py`
  - Done when: scripted 3-tool-call turn produces correct event sequence (IP01 TC-32); sequential dispatch through registry + safety (IS-13)
  - Verify: `pytest tests/test_agent.py -k tc32`
  - Depends: TK-003, TK-010, TK-011, TK-013, TK-014, TK-018
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-020** - Loop limits, caps, cancellation
  - Files: `src/lana/agent.py`
  - Done when: IP01 TC-33 (limit + auto_continue), TC-34 (cancellation keeps results + synthetic note), tool result cap wired (IS-13)
  - Verify: `pytest tests/test_agent.py`
  - Depends: TK-019
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-021** - Session store and resume
  - Files: `src/lana/session.py`
  - Done when: per-line flush, resume projection incl. checkpoint replay + corrupt-line skip (IP01 TC-35) (IS-14)
  - Verify: `pytest tests/test_session.py`
  - Depends: TK-003
  - Parallel: [P] (with TK-019)
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-022** - Slash command expansion and built-ins
  - Files: `src/lana/agent.py`, `src/lana/cli.py`
  - Done when: `/name` expands per Cascade format; unknown names suggest matches; `/help` `/cost` `/exit` work (FR-05)
  - Verify: `pytest tests/test_slash.py`
  - Depends: TK-005, TK-019
  - Est: 0.25 HHW

- [x] **LANAAGNT-TK-023** - CLI startup and renderer
  - Files: `src/lana/cli.py`, `src/lana/render.py`
  - Done when: startup banner + counts + policy notice (NFR-05); event-subscribed rendering; approval and question prompts (IS-15)
  - Verify: `pytest tests/test_render.py` + manual spot run
  - Depends: TK-019, TK-021
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-024** - Headless mode and exit codes
  - Files: `src/lana/cli.py`, `src/lana/agent.py`
  - Done when: `-p`, `--output-format jsonl`, `--config`/`LANA_CONFIG`, exit codes 0/2/3/4, non-terminal stdin fallback + auto-deny (IS-21, FR-14)
  - Verify: `pytest tests/test_headless.py` (IP01 TC-50..52, TC-55)
  - Depends: TK-023
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-025** - LanaProc test harness
  - Files: `tests/harness.py`
  - Done when: start/send/events/tail_session/wait_exit + assert helpers per TP01 section 8 (IS-22)
  - Verify: `pytest tests/test_harness_selftest.py` (IP01 TC-53, TC-54)
  - Depends: TK-024, TK-018
  - Est: 0.5 HHW

### Phases F-G: Cost and Compaction (IP01 IS-16..17)

- [x] **LANAAGNT-TK-026** - Cost engine
  - Files: `src/lana/cost.py`
  - Done when: IP01 TC-48..49 green (per-turn math, per-role accumulation incl. websearch) (IS-16)
  - Verify: `pytest tests/test_cost.py`
  - Depends: TK-004, TK-003
  - Parallel: [P]
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-027** - Compaction: projection, todo extraction, checkpoint
  - Files: `src/lana/compaction.py`, `src/lana/agent.py` (trigger)
  - Done when: IP01 TC-36..39 green (usage-anchored fire, 3 anchors, byte-identical todo, fail-safe, no-todo) (IS-17)
  - Verify: `pytest tests/test_compaction.py`
  - Guardrails: IG-04 - Summarizer never touches todo state
  - Depends: TK-019, TK-021
  - Est: 0.5 HHW

### Phase H: Web Tools (IP01 IS-18)

- [x] **LANAAGNT-TK-028** - read_url_content and view_content_chunk
  - Files: `src/lana/tools/web_tools.py`
  - Done when: fetch + HTML-to-text + chunking against local fixture server; approval gate; size/binary refusal (IP01 TC-44 offline parts, TC-45)
  - Verify: `pytest tests/test_web_tools.py`
  - Depends: TK-009, TK-019
  - Parallel: [P]
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-029** - search_web via websearch role
  - Files: `src/lana/tools/web_tools.py`
  - Done when: provider-native web search side-call renders Cascade's 5-result format (IP01 TC-43 live)
  - Verify: `pytest tests/test_web_tools.py -m live`
  - Depends: TK-016, TK-017, TK-028
  - Est: 0.5 HHW

### Black-Box Scenarios and Hardening (IP01 IS-19, TP01)

- [x] **LANAAGNT-TK-030** - TP01 scenarios 1-5 (conversation + safety)
  - Files: `tests/test_scenarios_conversation.py`, `tests/test_scenarios_safety.py`
  - Done when: TP01-TC-01..05 green against installed executable
  - Verify: `pytest tests/test_scenarios_*.py`
  - Depends: TK-025, TK-022
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-031** - TP01 scenarios 6-10 (robustness + real system + diagnostics)
  - Files: `tests/test_scenarios_robustness.py`, `tests/test_scenarios_diagnostics.py`
  - Done when: TP01-TC-06..10 green (kill/resume, output cap, DevSystemV4.2 startup, --debug redaction, exit codes 3/4)
  - Verify: `pytest tests/test_scenarios_*.py`
  - Depends: TK-030, TK-027
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-032** - NFR fixtures and offline end-to-end
  - Files: `tests/test_nfr.py`, `tests/test_e2e_offline.py`
  - Done when: IP01 IS-19 fixtures + TC-46 green; TP01-VC-04 secret-leak assertion wired into every scenario
  - Verify: `pytest tests/`
  - Depends: TK-031
  - Est: 0.5 HHW

- [x] **LANAAGNT-TK-033** - Live smoke suite complete
  - Files: `tests/test_adapters.py`, `tests/test_web_tools.py` (markers)
  - Done when: IP01 TC-40..45 green with keys; spend under TP01 budget cap
  - Verify: `pytest -m live`
  - Depends: TK-016, TK-017, TK-029
  - Est: 0.25 HHW

- [x] **LANAAGNT-TK-034** - Live acceptance run (IP01 TC-47)
  - Files: none (manual per IS-20 script)
  - Done when: /prime + edit round trip + approval + /cost + Ctrl+C + --resume all pass against DevSystemV4.2; results in PROGRESS.md
  - Verify: manual checklist from IS-20
  - Depends: TK-032, TK-033
  - Est: 0.5 HHW

## Task N - Final Verification (MANDATORY)

Run after all tasks complete:
- [x] Full suite vs Task 0 baseline (greenfield: all 65 automated cases green, 0 regressions possible by definition - any red = defect)
- [x] IP01 VC-01..15 and TP01 VC-01..06 checked off
- [x] Run `/verify` workflow on the implementation against LANAAGNT-IP01
- [x] `/sync` LANAAGNT-SP01/IP01 if implementation deviated
- [x] Update PROGRESS.md - mark complete; `/commit`

## Dependency Graph

```
TK-001 ─> TK-002 ─> TK-003 ──────────────────────┬─> TK-019 (loop core)
   │  └─> TK-004 ─> TK-012 ─> TK-013 ────────────┤      │
   │  └─> TK-005 ─┬> TK-007          TK-021 ─────┤      v
   │  └─> TK-006 ─┘   │                          ├─> TK-020 ─> TK-023 ─> TK-024 ─> TK-025
   │  └─> TK-008 ─> TK-009 ─> TK-010/011/014 ────┘                                   │
   │                   └────> TK-028 ─> TK-029                                       v
   └─> TK-015 ─┬> TK-016/017 ─> TK-033           TK-026/027 ────> TK-030 ─> TK-031 ─> TK-032 ─> TK-034
               └> TK-018 ─────────────────────────────────────────────┘
```

Critical path (longest chain): TK-001 -> TK-008 -> TK-009 -> TK-013 -> TK-019 -> TK-020 -> TK-023 -> TK-024 -> TK-025 -> TK-030 -> TK-031 -> TK-032 -> TK-034 = 13 tasks, ~6.5 HHW (TK-013 also needs TK-012, reachable in parallel via TK-004).

## Document History

**[2026-08-30 02:10]**
- Changed: all 36 tasks + Task 0 + Final Verification checked complete - implementation executed via `/go` (2026-08-30 session); 161 offline + 4 live tests green; 2 bugs filed and fixed (`LANAAGNT-BG-0001`, `LANAAGNT-BG-0002`); note: TK-018 scripted adapter core moved into `src/lana/providers/` (IP01 Document History 02:10)

**[2026-08-29 22:46]**
- Added: Task Execution Protocol section (`/improve` run 3 - context-reset-safe execution: per-task source re-reads, red-stop rule, commit convention, VC phase gates; motivated by FL-0002/FL-0003 memory-drift lessons)

**[2026-08-29 22:42]**
- Fixed (`/verify`): Task 0 keys note pointed at TK-020 instead of TK-016/017; critical path restated as the actual longest chain via TK-008/009/013 (~6.5 HHW); parallel count corrected to 15 at creation

**[2026-08-29 22:38]**
- Initial tasks plan created from LANAAGNT-IP01/TP01: 36 tasks (34 work + 2 mandatory), PARTITION-DEPENDENCY, 15 parallel-marked, critical path ~6.5 HHW
