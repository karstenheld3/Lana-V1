# Session Problems

**Doc ID**: LANAAGNT-PROBLEMS

Track problems using ID format: `LANAAGNT-PR-[NNNN]`

## Open

- (none)

## Resolved

**LANAAGNT-PR-0005: Renderer parses untrusted text as rich markup**
- **History**: Added 2026-08-30 03:50 | Resolved 2026-08-30 03:58 | → Now tracked as LANAAGNT-BG-0004
- **Solution**: markup=False on all payload-carrying prints; style= parameters for coloring (see `_BugFixes/LANAAGNT-BG-0004_RendererMarkupInjection/`)
- **Verification**: 5/5 repro cases verbatim after fix (3 LOST + 1 CRASH before); regression tests green; also verified non-bug: Anthropic auto-combines consecutive same-role messages (ANTAPI-IN08), so cancellation-note/checkpoint user-message sequences are safe

**LANAAGNT-PR-0004: Anthropic web_search built with invalid allowed_domains parameter**
- **History**: Added 2026-08-30 02:40 | Resolved 2026-08-30 02:45 | → Now tracked as LANAAGNT-BG-0003
- **Solution**: Parameter removed (web_fetch-only per ANTAPI-IN24); domain folded into the search prompt; live smoke added for the branch (see `_BugFixes/LANAAGNT-BG-0003_AnthropicWebSearchBadParam/`)
- **Verification**: `test_anthropic_web_search_branch` live green; found by `/drift-correct` retroactive doc verification (drift item 21)

**LANAAGNT-PR-0003: /cost empty after --resume**
- **History**: Added 2026-08-30 01:48 | Resolved 2026-08-30 01:55 | → Now tracked as LANAAGNT-BG-0002
- **Solution**: `CostTracker.seed()` restores usage/cost/turn totals from the resumed log; wired in `cli.build_runtime` (see `_BugFixes/LANAAGNT-BG-0002_ResumeCostNotSeeded/`)
- **Verification**: TP01-TC-02 green against the real executable

**LANAAGNT-PR-0002: approval_required event persisted but never yielded to frontends**
- **History**: Added 2026-08-30 01:35 | Resolved 2026-08-30 01:40 | → Now tracked as LANAAGNT-BG-0001
- **Solution**: Approval resolution split from dispatch and yielded through the run_prompt generator (see `_BugFixes/LANAAGNT-BG-0001_ApprovalEventNotYielded/`)
- **Verification**: `test_denylisted_command_denied_without_callback` + TP01-TC-04/05 green

**LANAAGNT-PR-0001: Open design questions block architecture SPEC**
- **History**: Added 2026-08-29 20:46 | Resolved 2026-08-29 21:08
- **Solution**: User delegated decisions ("make optimal decisions, simple but effective"); all 20 P1 questions resolved in `_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` DD-01 to DD-18; deferred scope (ACP, MCP, memory) recorded in DD-18
- **Verification**: Every DD cites its OQ-NN; 2 documented deviations from INFO leanings (DD-04 Chat Completions, DD-05 sequential tools)

## Deferred

- (none yet)

## Problems Changes

**[2026-08-30 02:15]**
- Resolved: LANAAGNT-PR-0002/0003 (implementation bugs BG-0001/BG-0002, both fixed and regression-tested)

**[2026-08-29 21:08]**
- Resolved: LANAAGNT-PR-0001 (all P1 questions decided in LANAAGNT-SP01)

**[2026-08-29 20:46]**
- Added: LANAAGNT-PR-0001 (design questions block SPEC)
