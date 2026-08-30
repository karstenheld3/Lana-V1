# Session Problems

**Doc ID**: LANAAGNT-MVP1-PROBLEMS

Track problems using ID format: `LANAAGNT-PR-[NNNN]`

## Open

**LANAAGNT-PR-0007: Registry prefix `claude-sonnet-4.5` (dot) never matches dash-form model ids**
- **History**: Added 2026-08-30 05:45 (observation from /bugfix discovery sweep)
- **Assessment**: `model-registry.json` `model_id_startswith` has `claude-sonnet-4.5` / `claude-opus-4.5` (dot notation) but all model ids use dashes (`claude-sonnet-4-5-20250929`) - first-match falls through to the `claude-sonnet-4` row, so the 4.5 generator gets max_output 8192 instead of the 16384 the 4.5 row intends. NOT a Lana code bug: the registry is a read-only input (DD-16) and SPEC section 13 forbids hardcoded per-model logic. Functional impact: lower max_tokens ceiling, otherwise correct behavior.
- **Decision needed**: user owns the registry - either change the prefix rows to dash notation or accept the fallback row

## Resolved

**LANAAGNT-PR-0006: --resume with missing file crashes with raw traceback**
- **History**: Added 2026-08-30 05:40 | Resolved 2026-08-30 05:50 | -> Now tracked as LANAAGNT-BG-0005
- **Solution**: resume path validated at startup -> ConfigError with named file + fix, exit 2

**LANAAGNT-PR-0005: Renderer parses untrusted text as rich markup**
- **History**: Added 2026-08-30 03:50 | Resolved 2026-08-30 03:58 | -> Now tracked as LANAAGNT-BG-0004
- **Solution**: markup=False on all payload-carrying prints; style= parameters for coloring

**LANAAGNT-PR-0004: Anthropic web_search built with invalid allowed_domains parameter**
- **History**: Added 2026-08-30 02:40 | Resolved 2026-08-30 02:45 | -> Now tracked as LANAAGNT-BG-0003
- **Solution**: Parameter removed (web_fetch-only per ANTAPI-IN24); domain folded into the search prompt

**LANAAGNT-PR-0003: /cost empty after --resume**
- **History**: Added 2026-08-30 01:48 | Resolved 2026-08-30 01:55 | -> Now tracked as LANAAGNT-BG-0002
- **Solution**: `CostTracker.seed()` restores usage/cost/turn totals from the resumed log

**LANAAGNT-PR-0002: approval_required event persisted but never yielded to frontends**
- **History**: Added 2026-08-30 01:35 | Resolved 2026-08-30 01:40 | -> Now tracked as LANAAGNT-BG-0001
- **Solution**: Approval resolution split from dispatch and yielded through the run_prompt generator
