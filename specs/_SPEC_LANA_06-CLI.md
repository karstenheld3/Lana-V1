# SPEC: Lana CLI Frontend

**Doc ID**: LANACLI-SP01
**Goal**: Specify the CLI frontend, headless mode, prompt queue execution, cost tracking, zero-setup startup, and runtime resilience for the Lana CLI agent
**Timeline**: Created 2026-08-29, Extracted from _SPEC_LANA_MVP-1.md and _SPEC_LANA_MVP-2_ACP.md 2026-09-01

**Target file(s)**:
- `src/lana/cli.py` (REPL, headless mode, startup, zero-setup)
- `src/lana/render.py` (terminal rendering, severity-prefix notices)
- `src/lana/cost.py` (per-turn and per-role cost engine)
- `src/lana/prompt_queue.py` (PromptQueueFile parsing, --prompt-file mode)

**Depends on:**
- `_SPEC_LANA_02-AgentCore.md [LANACORE-SP01]` for AgentEvent stream (DD-06), turn loop (FR-04), session (FR-08)
- `_SPEC_LANA_03-PromptAndConfig.md [LANAPRCF-SP01]` for config loading (FR-01), prompt system (FR-02)

**Does not depend on:**
- `_SPEC_LANA_11-Selftest.md [LANASTST-SP01]` (selftest is a separate component)

## Table of Contents

1. [Functional Requirements](#1-functional-requirements)
2. [Design Decisions](#2-design-decisions)
3. [Domain Objects](#3-domain-objects)
4. [User Actions](#4-user-actions)
5. [Logging Requirements](#5-logging-requirements)
6. [Document History](#6-document-history)

## 1. Functional Requirements

**LANAAGNT-FR-09: Cost Tracking**
- Per-turn: input/output/cache-read/cache-write tokens and cost from `model-pricing.json`, rendered after each turn (OQ-42)
- `/cost`: session totals per role (generator, summarizer, websearch)
- Unknown model in pricing file: show token counts with cost marked `?`

**LANAAGNT-FR-14: Headless Mode and Test Interfaces**
- `lana -p "<prompt>"`: non-interactive single-prompt run - executes the full turn loop, prints the final assistant text (default) or streams every AgentEvent as JSON Lines to stdout (`--output-format jsonl`), then exits
- Exit codes: 0 = turn completed, 2 = configuration error, 3 = provider/API failure after retries, 4 = stopped without completion (cancelled or tool-call limit without continue)
- Non-interactive approvals: in headless mode or when stdin is not a terminal, `approval_required` is DENIED automatically - the tool result reads "approval denied (non-interactive session)" and the loop continues; `ask_user_question` returns "no answer (non-interactive session)"
- `--config <path>` (or env `LANA_CONFIG`) overrides the default `config/lana-config.json` location - test isolation without touching the real config
- When stdin is not a terminal, the interactive loop reads plain lines from stdin (no terminal-dependent input features) - pipe-driven sessions work
- Scripted adapter (test infrastructure, NOT a third LLM backend): env `LANA_SCRIPTED_ADAPTER=<script.jsonl>` replaces both provider adapters with a deterministic replay adapter; never active without the env var; the startup banner marks the session SCRIPTED; no API keys required in this mode
- Built-ins (`/help`, `/cost`, `/exit`) are dispatched in headless `-p` mode exactly like in the REPL - they never reach the Generator (synced from implementation 2026-08-30)

**LANAAGNT-FR-16: Zero-Setup Startup and Runtime Resilience** (hardening per `_INFO_ROBUSTNESS_HAZARDS.md [LANAAGNT-IN03]`)
- Zero-setup: at startup Lana auto-creates every missing artifact it can create safely - the runtime data directory (`data_dir` with `sessions/`), the agent folder scaffold (`agent_folder` with `rules/`, `workflows/`, `skills/`), and a default `config/lana-config.json` (DD-02 default roles) - all relative to the app directory - and prints one line per created artifact; no init command, no manual setup steps (DD-23)
- Auto-created config applies only to the DEFAULT config path; an explicit `--config`/`LANA_CONFIG` override that does not exist stays a ConfigError (an explicit path is a user statement, not a gap)
- Model data files (`model-registry.json`, `model-parameter-mapping.json`, `model-pricing.json`) are shipped data: when missing, startup fails with the existing self-contained ConfigError (bundled-default distribution deferred)
- Empty prompt system (0 rules, 0 workflows, 0 skills): print a one-line notice that Lana runs without prompt system content
- Startup resilience (IN03 CR-01): `OSError` during startup is handled like `ConfigError` - self-contained message naming path and corrective action, exit code 2, never a raw traceback
- REPL/headless resilience (IN03 CR-02/CR-03): any unexpected exception in a prompt turn prints a self-contained error; the REPL stays alive (headless: exit code 4); the session JSONL survives for `--resume`
- Compaction fail-safe widened (IN03 CR-04): the entire compaction body runs under EC-17 warn-and-continue semantics, not only the Summarizer call
- `command_status` wait clamp (IN03 BL-03): `WaitDurationSeconds` is clamped to 60 s server-side (the bound the tool description already promises); a triggered clamp is noted in the result
- Fetch wall-clock deadline (IN03 BL-07): `read_url_content` reads in chunks under a 120 s wall-clock deadline - a trickling server cannot extend a fetch beyond it
- Provider timeouts and visible retries (IN03 BL-05/UX-03): SDK clients are constructed with explicit timeouts (connect 10 s, read 120 s) and SDK-internal retries disabled; Lana owns up to 2 retries on retryable failures (connection errors, HTTP 408/429/5xx) occurring before the first streamed delta, each announced as a user-visible WARNING notice with backoff delay
- Responsiveness (IN03 UX-01/02/04/05): a status line renders between turn start and the first visible output, ticking elapsed seconds while thinking stays hidden; `--show-thinking` streams thinking dim-styled; a notice line announces compaction BEFORE the Summarizer call; resume prints the session file name BEFORE parsing
- Process cleanup (IN03 BL-02/BL-06): live tool child processes (foreground and background `pwsh`) are terminated on turn cancellation and at process exit; survivors are named in one line

**LANAACPB-FR-12: Prompt Queue Headless Execution** (absorbed from `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]`)
- `lana --prompt-file <path>` parses the file as a PromptQueueFile and runs each prompt as one turn of ONE new session, in fence order
- Fence lengths 3 through 9 backticks are accepted, chosen per prompt (PromptQueueFile format rules)
- Extends the AgentEvent set (LANAAGNT-SP01 DD-06) by `prompt_step` with queue index (1-based), queue total, and a prompt digest; emitted before each turn, persisted in the session JSONL, printed under `--output-format jsonl`
- Same output-format options as `-p` (LANAAGNT-FR-14)
- Malformed file (not starting with a fence, unclosed fence, missing `---` between prompts, opening fence longer than 9 backticks, zero prompts) -> self-contained error on stderr naming the violated rule, exit code 2
- Turn failure (provider error, cancellation) -> remaining queue entries are abandoned, non-zero exit; completed turns stay persisted and the session remains resumable
- Mutually exclusive with `-p`, `--acp`, and `--resume` (MVP scope: queue always starts a fresh session)

## 2. Design Decisions

**LANAAGNT-DD-20:** Black-box CLI testing via three observable interfaces (FR-14): headless prompt injection, per-line-flushed session JSONL as the activity monitor, and the scripted replay adapter for deterministic turns. Rationale: tests exercise the real `lana` executable end-to-end without API cost, nondeterminism, or pseudo-terminal emulation (fragile on Windows); the AgentEvent stream (DD-06) stays the single observability surface for humans, tests, and the future ACP frontend alike.

**LANAAGNT-DD-24:** Severity-prefixed notices over the existing `error` event: messages starting `WARNING:` render yellow, `NOTICE:` render dim (prefix stripped), all others red with `ERROR:` prefix; the AgentEvent enum stays at 11 types. Rationale: retry notices (FR-16) and the pre-compaction line need non-error rendering; a 12th event type would touch the JSONL schema, resume projection, and the ACP translator for a pure presentation concern - the EC-17 `WARNING:` prefix convention already exists, this formalizes it.

## 3. Domain Objects

### PromptQueueFile

A **PromptQueueFile** (`PROMPTS*.md`) is a markdown file carrying an ordered queue of prompts for headless execution (LANAACPB-FR-12). Format authority: `docs/PROMPT_FILE_FORMAT.md`.

**Format rules:**
- The first non-empty line MUST be an opening fence
- Each prompt is one fenced block: opening fence of N backticks (3 <= N <= 9, optional info string), closed by a line of >= N backticks (CommonMark fence semantics)
- Each prompt chooses its own N independently; a prompt containing M-backtick fences as content needs a fence of N > M
- Consecutive prompts are separated by one `---` line (between closing fence and next opening fence)
- Commentary (step labels, notes) may appear between the `---` and the next opening fence; it is never sent to the agent
- Queue order = fence order in the file

### prompt_step Event

```json
{"type": "prompt_step", "index": 1, "total": 2, "digest": "a1b2c3d4e5f6"}
```

Headless-only AgentEvent: persisted in the session JSONL, never emitted on the ACP wire.

## 4. User Actions

- **Start**: `lana` (workspace = cwd) | `lana --app-dir [path]` (infrastructure base, DD-25) | `lana --resume [session-file]` | `lana --debug` | `lana --policy manual|auto|turbo` | `lana --config [path]`
- **Headless**: `lana -p "<prompt>"` | `--output-format text|jsonl` - single prompt, exit code signals outcome (LANAAGNT-FR-14)
- **Prompt queue**: `lana --prompt-file <path>` - multi-prompt headless from PromptQueueFile (LANAACPB-FR-12)
- **Chat**: free text sends a user message; `/name` invokes a workflow
- **Built-ins**: `/help` (workflows + built-ins), `/cost` (session usage), `/exit`
- **Approve command**: y/n/a prompt showing command line + working directory when the safety gate requires it; `a` approves all remaining approval-gated calls in the session
- **Answer question**: numbered choice prompt when the Generator calls `ask_user_question`
- **Cancel**: Ctrl+C aborts the current turn, returns to input

## 5. Logging Requirements

**Applicable logging types:**
- [x] User-Facing (UF) - `LOGGING-RULES-USER-FACING.md`
- [x] App-Level (AP) - `LOGGING-RULES-APP-LEVEL.md` (only with `--debug`)
- [ ] Script-Level (SC) - N/A in MVP-1 (no selftest scripts specified here; TEST plan will add them)

**User-Facing (UF):**
- Audience: the person chatting with Lana in the terminal
- Goal: always know what Lana is doing - which tool runs, what it costs, when compaction happens
- Key operations: startup load, tool execution, approval gates, turn completion, compaction

**Expected user-facing output for startup and one turn:**
```text
Lana MVP-1 | generator: claude-sonnet-4-5 (medium) | summarizer: gpt-4.1-mini (low)
Keys: Anthropic (Environment variable: ANTHROPIC_API_KEY), OpenAI (Environment variable: OPENAI_API_KEY)
Loading prompt system '.lana'...
  8 rules (7 injected, 1 skipped: empty), 46 workflows, 21 skills.
  OK. Loaded in 0.4 secs.

> /prime
Running workflow 'prime'...
  [tool] read_file '!NOTES.md'...
    OK. 34 lines.
  [tool] run_command 'git log -n 5 --oneline' (policy: manual)
    Approve? [y/n/a] y
    OK. Exit code 0.
  Turn: in=21050 (cache 18200) out=412 | $0.0164 | session $0.0164
```

**App-Level (AP, `--debug` only):**
- Audience: developer debugging provider requests
- Goal: reproduce any API call from the log alone (keys redacted)
- Key operations: request/response JSON per API call, cache token accounting, compaction decisions

## 6. Document History

**[2026-09-01 21:45]**
- Extracted from `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]`: FR-09, FR-14, FR-16, DD-20, DD-24, Section 11 (User Actions), Section 12 (Logging Requirements)
- Absorbed from `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]`: LANAACPB-FR-12 (Prompt Queue Headless Execution), PromptQueueFile domain object and format rules, prompt_step event
- Content is verbatim from sources with section renumbering and header block update only
