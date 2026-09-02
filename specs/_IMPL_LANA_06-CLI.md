# IMPL: Lana CLI Frontend

**Doc ID**: LANACLI-IP01
**Goal**: Implement the CLI frontend, headless mode, prompt queue, cost tracking, zero-setup, and runtime resilience per LANACLI-SP01
**Timeline**: Created 2026-08-29, Extracted from _IMPL_LANA_MVP-1.md and _IMPL_LANA_HARDENING.md 2026-09-01

**Target file(s)**:
- `src/lana/cli.py` (REPL, headless, startup, zero-setup, --prompt-file)
- `src/lana/render.py` (terminal rendering, severity-prefix notices, status spinner)
- `src/lana/cost.py` (per-turn and per-role cost engine)
- `src/lana/prompt_queue.py` (PromptQueueFile parsing)

**Depends on:**
- `_SPEC_LANA_06-CLI.md [LANACLI-SP01]` for FR-09, FR-14, FR-16, LANAACPB-FR-12, DD-20, DD-24
- `_IMPL_LANA_02-AgentCore.md [LANACORE-IP01]` for IS-13 (turn loop), IS-14 (session), IS-22 (scripted adapter/harness)
- `_IMPL_LANA_03-PromptAndConfig.md [LANAPRCF-IP01]` for IS-03 (config), IS-04 (loader), IS-05 (prompt assembly)

**Does not depend on:**
- `_IMPL_LANA_11-Selftest.md [LANASTST-IP01]` (selftest is a separate component)

## MUST-NOT-FORGET

- AgentEvent enum is 12 types (11 core + headless-only `prompt_step`, DD-24); notices ride on ErrorEvent with severity prefixes
- stdout purity in headless jsonl mode: startup banner, warnings, and error notices route to stderr
- No test deleted or weakened; existing tests stay green
- Small cycles: implement -> test -> green -> commit per phase; never proceed on red

## Table of Contents

1. [Implementation Steps](#1-implementation-steps)
2. [Test Cases](#2-test-cases)
3. [Verification Checklist](#3-verification-checklist)
4. [Document History](#4-document-history)

## 1. Implementation Steps

### Phase E: CLI Frontend

### LANAAGNT-IP01-IS-15: CLI frontend and renderer

**Location**: `cli.py`, `render.py`

**Action**: `cli.py`: args (`--resume`, `--debug`, `--policy`, `--app-dir`, `--prompt-file`), startup sequence (config -> prompt system -> banner + auto/turbo risk notice per NFR-05), REPL via prompt_toolkit, built-ins `/help` `/cost` `/exit`. `--app-dir` (or env `LANA_APP_DIR`) sets the base directory for config, agent_folder, and data_dir (DD-25); defaults to CWD when unset. `render.py`: subscribes to events; streams text; tool lines + approval y/n/a prompts (FR-12: `a` sets an approve-all flag for the rest of the session) + numbered `ask_user_question` prompts per SPEC section 12 format; per-turn cost line via `cost.py`

**Note**: `--debug` writes redacted request/response JSON to `.lana-data/logs/` (NFR-04). Renderer constraint (BG-0004, synced 2026-08-30): event payload text (model output, tool results, provider messages) is UNTRUSTED and never enters rich markup parsing - markup=False on all payload prints, styling via style= parameters only. Executor registration is feature-flag-aware: `_EXECUTORS_BASE` (shared tools) + `_EXECUTORS_UNIFIED_SEARCH` or `_EXECUTORS_LEGACY_SEARCH` selected by `app.lana.unified_file_search_tool` (DD-28); the flag is also passed to the `ToolRegistry` constructor so definitions match executors

### Phase F: Cost Tracking

### LANAAGNT-IP01-IS-16: Cost engine (LANAAGNT-FR-09)

**Location**: `cost.py`

**Action**: Per-turn cost from usage x pricing (input/output/cache-read/cache-write rates); accumulate per role; `/cost` summary; unknown model -> `?` (EC-24). Usage normalization contract: adapters report input_tokens INCLUDING cache reads (Anthropic normalized up, OpenAI native) (synced 2026-08-30)

### Phase E addendum

### LANAAGNT-IP01-IS-21: Headless mode and exit codes (LANAAGNT-FR-14)

**Location**: `cli.py`, `agent.py`

**Action**: Add `-p/--prompt`, `--output-format text|jsonl`, `--config`/`LANA_CONFIG` override; exit codes 0/2/3/4 per FR-14; non-terminal stdin detection (`sys.stdin.isatty()`) switches to plain line input and auto-denies `approval_required`/`ask_user_question` with the FR-14 messages; built-ins (/help /cost /exit) dispatched before slash expansion in headless mode too (synced 2026-08-30)

**Note**: The jsonl output stream writes the same serialized AgentEvents as the session file - one serializer, two sinks. jsonl purity contract (`/improve` run 3, 2026-08-30): stdout carries ONLY event lines - startup banner, warnings, and error notices route to stderr so strict consumers (jq, log shippers, the MVP-2 ACP frontend) parse stdout directly

### LANAAGNT-IP01-IS-22: Scripted adapter and CLI test harness (LANAAGNT-DD-20)

**Location**: `providers/scripted_adapter.py` (adapter), `tests/scripted_adapter.py` (re-export + helpers), `tests/harness.py`, `providers/__init__.py` (env hook)

**Action**: Script format = JSONL, one line per Generator turn: `{"text": str, "thinking": str?, "tool_calls": [{"name": str, "args": {}}]?, "usage": {"input": int, "output": int}?}` or `{"error": str}` (adapter raises a simulated provider failure - deterministic exit-code-3 testing, TP01-TC-10) - the adapter replays lines in order, errors if the script is exhausted. Harness `LanaProc`: spawn `lana` via subprocess with temp workspace + `--config` + `LANA_SCRIPTED_ADAPTER`, inject prompts (`-p` or stdin pipe), collect stdout JSONL events, `tail_session(predicate, timeout)` polling the flushed session file, assert exit codes

**Note**: Resolves deferred candidate D-02 (LANAAGNT-DF01). The env hook in `providers/__init__.py` is 5 lines: if `LANA_SCRIPTED_ADAPTER` set, return the scripted adapter for every role

### Phase 1-5: Zero-Setup and Hardening (absorbed from `_IMPL_LANA_HARDENING.md [LANAAGNT-IP02]`)

### LANAAGNT-IP02-IS-01 through IS-14: Hardening implementation

Phases 1-5 of `_IMPL_LANA_HARDENING.md [LANAAGNT-IP02]` implement LANAAGNT-FR-16 in full:

- **Phase 1** (IS-01..03): Zero-setup config auto-create, data/agent dir scaffolding, startup/REPL resilience
- **Phase 2** (IS-04..06): Tool hardening - command_status clamp, web fetch deadline, process cleanup
- **Phase 3** (IS-07..09): Renderer responsiveness - status spinner, severity-prefix rendering, compaction notice
- **Phase 4** (IS-10..12): Provider timeouts + visible retries
- **Phase 5** (IS-13..14): ACP hardening (writer thread, executor runtime)

See `_IMPL_LANA_HARDENING.md [LANAAGNT-IP02]` for full step details, edge cases (EC-01..11), and test cases (TC-01..16).

## 2. Test Cases

### Category 8: End-to-End (2 tests)

- **LANAAGNT-IP01-TC-46**: Offline e2e: fake-adapter /prime flow -> transcript matches SPEC section 12 log format
- **LANAAGNT-IP01-TC-47**: Live manual acceptance (IS-20 script) -> all steps pass, recorded in PROGRESS.md

### Category 9: Cost (2 tests)

- **LANAAGNT-IP01-TC-48**: Per-turn cost math: input/output/cache-read rates from `model-pricing.json` -> cost matches hand-computed value to 4 decimals
- **LANAAGNT-IP01-TC-49**: Per-role accumulation across 3 turns + 1 compaction -> `/cost` output shows generator, summarizer, websearch totals and session sum

### Category 10: Automated CLI Harness (6 tests, real executable, scripted adapter)

- **LANAAGNT-IP01-TC-50**: `lana -p "hello"` with 1-turn script -> final text on stdout, exit 0
- **LANAAGNT-IP01-TC-51**: Missing config -> stderr names file and fix, exit 2
- **LANAAGNT-IP01-TC-52**: Script requests denylisted `run_command` headless -> "approval denied (non-interactive session)" in tool result event, loop continues, exit 0
- **LANAAGNT-IP01-TC-53**: Same script run twice -> byte-identical event sequences modulo timestamps/ids (determinism)
- **LANAAGNT-IP01-TC-54**: `tail_session` observes each `tool_call_finished` within 1 s of stdout appearance (FR-08 flush contract)
- **LANAAGNT-IP01-TC-55**: Piped stdin session (`echo /help | lana`) -> workflow list printed, clean exit (non-terminal fallback)

### Hardening TCs (from `_IMPL_LANA_HARDENING.md [LANAAGNT-IP02]`)

LANAAGNT-IP02-TC-01 through TC-16 verify FR-16 zero-setup and hardening. See `_IMPL_LANA_HARDENING.md [LANAAGNT-IP02]` section "Test Cases" for full list.

## 3. Verification Checklist

- [x] **LANACLI-IP01-VC-01**: LANACLI-SP01 re-read; 3 LANAAGNT FRs + LANAACPB-FR-12 + 2 DDs accounted for
- [x] **LANACLI-IP01-VC-02**: Phase E green (TC-50..55, IS-21/IS-22)
- [x] **LANACLI-IP01-VC-03**: Phase F green (TC-48..49)
- [x] **LANACLI-IP01-VC-04**: Hardening green (IP02 TC-01..16)
- [x] **LANACLI-IP01-VC-05**: E2E green (TC-46..47)

## 4. Document History

**[2026-09-02 00:50]**
- Changed: IS-15 note updated for feature-flag-aware executor registration (`_EXECUTORS_BASE` + unified/legacy split, DD-28)
- Source: Code -> Docs sync after unified search tool implementation

**[2026-09-01 23:17]**
- Fixed: MNF "11 types + 1" -> "12 types (11 core + prompt_step)" (synced from `events.py` AgentEvent union)
- Fixed: IS-22 location added `providers/scripted_adapter.py` as primary (adapter lives there; `tests/scripted_adapter.py` is a re-export helper)
- Source: `/fact-check` + `/sync` against source code

**[2026-09-01 21:45]**
- Extracted from `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]`: IS-15 (CLI frontend), IS-16 (cost engine), IS-21 (headless mode), IS-22 (scripted adapter/harness)
- Absorbed from `_IMPL_LANA_HARDENING.md [LANAAGNT-IP02]`: Phases 1-5 (IS-01..14) implementing FR-16, referenced by pointer
- Test cases: Categories 8 (E2E), 9 (Cost), 10 (Automated CLI Harness), plus Hardening TC-01..16 by reference
- Content is verbatim from sources with section renumbering and header block update only
