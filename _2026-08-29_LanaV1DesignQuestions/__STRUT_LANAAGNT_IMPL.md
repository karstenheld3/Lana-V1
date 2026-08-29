# STRUT: Lana MVP-1 Implementation Execution

**Goal**: Fully working `lana` CLI agent per `TASKS_LANA_MVP-1.md [LANAAGNT-TK01]` - all automated tests green, live acceptance passed
**Source plans**: LANAAGNT-SP01 (rev 22:20), LANAAGNT-IP01 (rev 22:30), LANAAGNT-TP01 (rev 22:30), LANAAGNT-TK01 (rev 22:46)
**Mode**: `/go` autonomous - [ACTOR] = agent; decisions logged to PROGRESS.md
**Rule**: Task Execution Protocol (TK01) applies to every step; `/bugfix` files each bug found by tests

[ ] P1 [SETUP]: Task 0 baseline + repository
├─ Objectives:
│   └─ [ ] Clean environment, git history started ← P1-D1
├─ Strategy: Greenfield baseline; git init enables per-task commits
├─ [ ] P1-S1 [EXECUTE](Task 0: python/pip versions, src empty, DevSystemV4.2 + config access)
├─ [ ] P1-S2 [EXECUTE](git init + .gitignore + initial commit of planning docs)
├─ Deliverables:
│   └─ [ ] P1-D1: Baseline recorded in PROGRESS.md, repo initialized
└─> Transitions: P1-D1 checked → [FOUNDATION]

[ ] P2 [FOUNDATION]: Phase A - TK-001..004
├─ Objectives:
│   └─ [ ] Editable install + config/models/events tests green ← P2-D1
├─ [ ] P2-S1 [IMPLEMENT](TK-001 skeleton: pyproject, README, package stubs)
├─ [ ] P2-S2 [IMPLEMENT](TK-002/003 models.py + events.py)
├─ [ ] P2-S3 [IMPLEMENT](TK-004 config.py + config/lana-config.json)
├─ [ ] P2-S4 [TEST](TC-01..06) + [COMMIT]
├─ Deliverables:
│   └─ [ ] P2-D1: TC-01..06 green
└─> Transitions: P2-D1 → [PROMPTSYS]; red → /bugfix then P2-S4

[ ] P3 [PROMPTSYS]: Phase B - TK-005..007
├─ Objectives:
│   └─ [ ] DevSystemV4.2 loads and assembles into system prompt ← P3-D1
├─ [ ] P3-S1 [IMPLEMENT](TK-005 loader.py)
├─ [ ] P3-S2 [IMPLEMENT](TK-006/007 prompt.py: adapted sections, capability notice, assembly)
├─ [ ] P3-S3 [TEST](TC-07..15 incl. real DevSystemV4.2 load < 2 s) + [COMMIT]
├─ Deliverables:
│   └─ [ ] P3-D1: TC-07..15 green
└─> Transitions: P3-D1 → [TOOLS]

[ ] P4 [TOOLS]: Phase C - TK-008..014
├─ Objectives:
│   └─ [ ] 15 tool definitions + executors + safety policy working ← P4-D1
├─ [ ] P4-S1 [READ](_INFO_CASCADE_TOOL_DEFINITIONS.md [LANAAGNT-IN02] - transcription source, MANDATORY before S2)
├─ [ ] P4-S2 [IMPLEMENT](TK-008/009 definitions.py + registry, verbatim from IN02)
├─ [ ] P4-S3 [IMPLEMENT](TK-010 file_tools, TK-011 edit_tools + ReadLedger)
├─ [ ] P4-S4 [IMPLEMENT](TK-012 safety.py, TK-013 shell_tools, TK-014 state/skill/interact tools)
├─ [ ] P4-S5 [TEST](TC-16..31) + [COMMIT]
├─ Deliverables:
│   └─ [ ] P4-D1: TC-16..31 green, definitions diff-clean vs IN02
└─> Transitions: P4-D1 → [CORELOOP]

[ ] P5 [CORELOOP]: Phase E first (key-free corridor, DF01 D-03) - TK-015, TK-018..025
├─ Objectives:
│   └─ [ ] Full agent loop + CLI + session persistence, scripted adapter only ← P5-D1
├─ Strategy: Scripted adapter before live adapters - whole loop testable without keys
├─ [ ] P5-S1 [IMPLEMENT](TK-015 providers/base.py + selection + scripted env hook)
├─ [ ] P5-S2 [IMPLEMENT](TK-018 tests/scripted_adapter.py + conftest fixtures)
├─ [ ] P5-S3 [IMPLEMENT](TK-019/020 agent.py loop, limits, caps, cancellation)
├─ [ ] P5-S4 [IMPLEMENT](TK-021/022 session.py JSONL persistence + resume)
├─ [ ] P5-S5 [IMPLEMENT](TK-023/024 cli.py REPL + render.py + slash commands)
├─ [ ] P5-S6 [IMPLEMENT](TK-025 headless mode + exit codes + harness helpers)
├─ [ ] P5-S7 [TEST](TC-32..49 + TC-50..55) + [COMMIT]
├─ Deliverables:
│   └─ [ ] P5-D1: Loop/CLI/session/headless tests green
└─> Transitions: P5-D1 → [COSTCOMPACT]

[ ] P6 [COSTCOMPACT]: Phases F+G - TK-026..027
├─ Objectives:
│   └─ [ ] Cost tracking + checkpoint compaction working ← P6-D1
├─ [ ] P6-S1 [IMPLEMENT](TK-026 cost.py: pricing, usage-anchored projection)
├─ [ ] P6-S2 [IMPLEMENT](TK-027 compaction.py: checkpoint summary + reassembly)
├─ [ ] P6-S3 [TEST](phase F/G test cases) + [COMMIT]
├─ Deliverables:
│   └─ [ ] P6-D1: Cost + compaction tests green
└─> Transitions: P6-D1 → [ADAPTERS]

[ ] P7 [ADAPTERS]: Phase D - TK-016..017 (live smokes deferred to P10)
├─ Objectives:
│   └─ [ ] OpenAI + Anthropic adapters implemented per provider docs ← P7-D1
├─ [ ] P7-S1 [READ](docs/OpenAI/OpenAI_API_2026-07-30: IN 06 RESPONSES_API, 07 RESPONSES_STREAMING, 16 REASONING)
├─ [ ] P7-S2 [READ](docs/Anthropic/Anthropic_API_2026-07-27: IN 09 STREAMING, 15 EXTENDED_THINKING, 20 PROMPT_CACHING, 23 TOOL_USE)
├─ [ ] P7-S3 [IMPLEMENT](TK-016 openai_adapter.py, TK-017 anthropic_adapter.py)
├─ [ ] P7-S4 [TEST](offline adapter unit tests; live smokes skip without keys) + [COMMIT]
├─ Deliverables:
│   └─ [ ] P7-D1: Adapter unit tests green
└─> Transitions: P7-D1 → [WEBTOOLS]

[ ] P8 [WEBTOOLS]: Phase H - TK-028..029
├─ Objectives:
│   └─ [ ] read_url_content + view_content_chunk + search_web wired ← P8-D1
├─ [ ] P8-S1 [READ](docs/OpenAI IN 14 WEB_SEARCH + docs/Anthropic IN 24 WEB_TOOLS)
├─ [ ] P8-S2 [IMPLEMENT](TK-028/029 web_tools.py + chunk store)
├─ [ ] P8-S3 [TEST](fixture-based web tool tests) + [COMMIT]
├─ Deliverables:
│   └─ [ ] P8-D1: Web tool tests green
└─> Transitions: P8-D1 → [SCENARIOS]

[ ] P9 [SCENARIOS]: TK-030..032 black-box scenarios
├─ Objectives:
│   └─ [ ] TP01 scenario suite green via CLI harness + scripted adapter ← P9-D1
├─ [ ] P9-S1 [IMPLEMENT](TK-030 scenario fixtures + scripts)
├─ [ ] P9-S2 [TEST](TK-031/032 run scenario suite, /bugfix each failure) + [COMMIT]
├─ Deliverables:
│   └─ [ ] P9-D1: Scenario suite green
└─> Transitions: P9-D1 → [ACCEPT]

[ ] P10 [ACCEPT]: Final verification - TK-033..034
├─ Objectives:
│   └─ [ ] All-layer completion + live smoke if keys available ← P10-D1
├─ [ ] P10-S1 [TEST](full pytest run, all TCs)
├─ [ ] P10-S2 [EXECUTE](TK-033 live smoke if API keys resolve; else document skip)
├─ [ ] P10-S3 [VERIFY](TK-034 final verification vs IP01 VC gates + TK01 checkboxes)
├─ [ ] P10-S4 [EXECUTE](update PROGRESS.md, tick TK01 checkboxes, final commit)
├─ Deliverables:
│   └─ [ ] P10-D1: Multi-layer completion check passes
└─> Transitions: P10-D1 → [END]

## Document History

**[2026-08-30 01:05]**
- Initial STRUT created for /go execution of LANAAGNT-TK01
