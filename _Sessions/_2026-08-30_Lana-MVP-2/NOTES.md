# Session Notes

**Doc ID**: LANAACPB-MVP2-NOTES

## Session Info

- **Started**: 2026-08-30
- **Goal**: Design, implement, and test Lana MVP-2 ACP frontend + robustness hardening
- **Operation Mode**: IMPL-CODEBASE
- **Output Location**: `src/lana/acp/`, `tests/`, existing `src/lana/` modules
- **Origin**: Split from `_2026-08-29_LanaV1DesignQuestions/` on 2026-08-30

## Authoritative ACP Documentation

**`docs/AI-Standards/ACP-AgentClientProtocol_2026-08-30/` is the authoritative ACP documentation** (replaces `ACP-AgentClientProtocol_2026-06-12/`). All MVP-2 ACP SPEC/IMPL/TEST work MUST cite the 2026-08-30 folder.

## Key Documents

- `specs/_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` - 11 FRs, 4 NFRs, 9 DDs, 5 IGs
- `specs/_IMPL_LANA_MVP-2_ACP.md [LANAACPB-IP01]` - 6 phases, 21 ECs, 13 ISs, 41 TCs
- `specs/_TEST_LANA_MVP-2_ACP.md [LANAACPB-TP01]` - 4 layers, 10 automated scenarios + 1 manual
- `_INFO_LANAACPB-IN01_AcpV1WireShapeVerification.md [LANAACPB-IN01]` - wire shape authority
- `_INFO_ROBUSTNESS_HAZARDS.md [LANAAGNT-IN03]` - hazard analysis (4 CR, 7 BL, 6 UX)
- `specs/_IMPL_LANA_HARDENING.md [LANAAGNT-IP02]` - hardening implementation plan (Tier 1 + Tier 2 + zero-setup), IMPLEMENTED

## Key Decisions

- Option A: native in-process ACP module, hand-rolled JSON-RPC over stdio
- Awaitable callback seam in agent.py (CLI sync callbacks unchanged)
- $/cancel_request params read tolerantly (requestId falling back to id)
- EC-10 denial-vs-cancellation race accepted as benign
- **Zero-setup philosophy**: Lana MUST auto-create everything it needs on first run (data dirs, default config, prompt library) and tell the user what it did. No `init` command, no manual setup steps. The user runs `lana` and works. Distribution of the bundled prompt library is a separate concern (deferred).

## ACP Implementation Result

- `acp/jsonrpc.py`, `acp/server.py`, `acp/translator.py`, `acp/bridge.py`
- 48 ACP tests + 179 MVP-1 regression = 227 offline green
- OPEN: VC-11/TP01-TC-11 manual smoke against Zed needs user environment

## Hardening Status (Approach B)

- **Tier 1 + Tier 2 + zero-setup: DONE 2026-08-30** - `_IMPL_LANA_HARDENING.md [LANAAGNT-IP02]`, 240 tests green (17 new in `tests/test_hardening.py`)
- SPEC homes: LANAAGNT-SP01 FR-16 (zero-setup + resilience + responsiveness), DD-23/DD-24; LANAACPB-SP01 FR-01/03/10 (BL-01/02/04/06)
- Mitigations conform to `LOGGING-RULES-USER-FACING.md` (LG-UF-03/04/05) and `LOGGING-RULES-APP-LEVEL.md` (LG-AP-02)

## Topic Registry

**Global topics** (registered in ID-REGISTRY.md):
- `LANAAGNT` - Lana-V1 Agent
- `LANAACPB` - Lana ACP Backend
