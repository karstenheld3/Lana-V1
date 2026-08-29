# PROBLEMS: LANAAGNT-BG-0002 ResumeCostNotSeeded

**Doc ID**: LANAAGNT-BG-0002
**Goal**: Track and fix /cost showing no usage after --resume

### LANAAGNT-BG-0002 /cost empty after --resume despite prior turns in the session log

**Status**: Resolved
**Reported**: 2026-08-30 01:48
**Resolved**: 2026-08-30 01:55

**Verbatim failure**:
````
tests\test_scenarios_conversation.py:50 (TP01-TC-02)
assert 'generator: 3 turns' in "...Resumed session...6 messages.\n> No usage recorded in this session.\n> "
````

**Initial assessment**: `session.resume()` computes `usage_by_role`/`cost_by_role` from `turn_finished` events, but `cli.build_runtime()` creates a fresh empty `CostTracker` and never seeds it. Violates IG-06 (state after resume equals state before exit) and FR-09 (/cost session totals per role).

**Root cause**: TK-021 (resume projection) and TK-026 (cost tracker) were implemented as independent units; the wiring between them in `build_runtime` was never specified as its own step, so the integration fell through until the black-box scenario exercised the combination.

**Impact assessment**:
- `cli.build_runtime` resume branch (fix location)
- `CostTracker` (gains a seed method), `session.ResumedState` (gains turns_by_role count)
- `/cost` built-in output; per-turn "session $" totals in the renderer after resume
- Detecting test: TP01-TC-02 (`test_tp01_tc02_multi_turn_piped_and_resume`)

**Solution**: `ResumedState` counts `turns_by_role`; `CostTracker.seed(resumed)` restores usage, cost, and turn counts; `build_runtime` calls it in the resume branch.

**Changed files**:
- `src/lana/session.py` - turns_by_role counting in resume()
- `src/lana/cost.py` - CostTracker.seed()
- `src/lana/cli.py` - seed call in resume branch
