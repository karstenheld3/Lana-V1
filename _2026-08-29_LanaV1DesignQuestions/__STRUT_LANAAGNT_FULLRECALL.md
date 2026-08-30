# STRUT: Full-Recall Session Log Implementation

**Doc ID**: LANAAGNT-FULLRECALL-STRUT
**Goal**: Implement IS-24 full-recall session log (SP01 FR-08/IG-07/DD-22) - working and testable
**Source plans**: `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` IS-24/EC-28/EC-29/TC-64..67, `_TEST_LANA_MVP-1.md [LANAAGNT-TP01]` TC-11

## MUST-NOT-FORGET

- `session_started` = FIRST line of every new session file, before any user event
- Thinking payloads on `turn_finished.thinking_payloads` - NO 12th event type
- Resume: recorded system prompt + tool definitions WIN over disk; current config wins for model selection
- Cross-provider thinking payloads dropped from resend (EC-29); legacy files fall back to disk assembly (EC-28)
- Fingerprint: sorted (path, content) sha256, mtime-independent
- LANA_SCRIPTED_CAPTURE dumps (system, tools) per call - the byte-identity test oracle
- Never proceed on red; commit after green

## Plan

```
[x] P1 [IMPLEMENT]: Events + recording (write side)
├─ Objectives:
│   └─ [x] Every new session self-contained ← P1-D1, P1-D2
├─ Strategy: events.py first (contract), then write path in cli.py/agent.py; offline tests only
├─ [x] P1-S1 [ANALYZE](events.py, session.py, cli.py, agent.py, loader.py, prompt.py, scripted_adapter.py current state)
├─ [x] P1-S2 [IMPLEMENT](SessionStarted event + TurnFinished.thinking_payloads in events.py)
├─ [x] P1-S3 [IMPLEMENT](fingerprint computation over prompt system files)
├─ [x] P1-S4 [IMPLEMENT](cli.py writes session_started as first line; agent.py emits thinking payloads on turn_finished)
├─ Deliverables:
│   ├─ [x] P1-D1: session_started first line with 4 payloads
│   └─ [x] P1-D2: thinking payloads persisted per turn
└─> Transitions:
    - P1-D1, P1-D2 checked → P2
    - Otherwise → fix and retry current step

[x] P2 [IMPLEMENT]: Resume authority (read side)
├─ Objectives:
│   └─ [x] Resume needs only the JSONL ← P2-D1, P2-D2, P2-D3
├─ Strategy: session.py projection + cli.py resume wiring; EC-28/EC-29 handled
├─ [x] P2-S1 [IMPLEMENT](resume reads session_started -> recorded prompt/tools; fingerprint warning; legacy fallback EC-28)
├─ [x] P2-S2 [IMPLEMENT](thinking payload reprojection into Message.thinking; cross-provider drop EC-29)
├─ [x] P2-S3 [IMPLEMENT](model-change report on resume; LANA_SCRIPTED_CAPTURE in scripted_adapter.py)
├─ Deliverables:
│   ├─ [x] P2-D1: Recorded environment wins on resume
│   ├─ [x] P2-D2: EC-28 legacy + EC-29 provider-drop handled
│   └─ [x] P2-D3: Capture oracle available for tests
└─> Transitions:
    - P2-D1 - P2-D3 checked → P3
    - Otherwise → fix and retry current step

[x] P3 [TEST]: Verify and close
├─ Objectives:
│   └─ [x] Full suite green incl. new cases ← P3-D1, P3-D2
├─ Strategy: TC-64..67 unit/integration + TP01-TC-11 black-box; then full offline suite; commit
├─ [x] P3-S1 [TEST](TC-64: session_started first line, byte-identical prompt, snapshot, fingerprint)
├─ [x] P3-S2 [TEST](TC-65: resume authority under disk mutation + warnings; TP01-TC-11 black-box)
├─ [x] P3-S3 [TEST](TC-66: thinking payload round trip + provider drop; TC-67: legacy fallback)
├─ [x] P3-S4 [TEST](full offline suite - 179 passed, 2 assertions extended for the leading session_started line)
├─ [x] P3-S5 [COMMIT]("feat(lana): full-recall session log")
├─ [x] P3-S6 [VERIFY](VC-12, TP01-VC-02/03 checked; plans synced)
├─ Deliverables:
│   ├─ [x] P3-D1: TC-64..67 + TP01-TC-11 green
│   └─ [x] P3-D2: Full suite green, committed, plans synced
└─> Transitions:
    - P3-D1, P3-D2 checked → [END]
    - Tests fail after 3 attempts → [CONSULT]
```

## Decision Log

- [DECISION] EC-29 cross-provider drop needs no new resume-time filter - both provider adapters already filter thinking blocks by provider at request build time (anthropic_adapter build_messages, openai_adapter reasoning resend); TC-66 asserts the behavior - rules consulted: SP01 FR-08, DD-03 (thin adapters own provider specifics)
- [DECISION] TC-65 and TP01-TC-11 combined into one test (same fixture, same assertions end-to-end) - rules consulted: TP01 MNF (never duplicate case definitions), test-plan Layer 3 definition
- [DECISION] TC-46b + TP01-TC-01 session-log equality assertions extended by the leading session_started line instead of filtering it out - the new contract IS the session file containing one extra environment record (FR-08); not a test weakening
- [DECISION] Fingerprint computed from loaded PromptSystem content (not re-reading files) - identical input basis as the system prompt, zero extra I/O - rules consulted: IS-24 [ASSUMED] note, NFR-03 startup budget
