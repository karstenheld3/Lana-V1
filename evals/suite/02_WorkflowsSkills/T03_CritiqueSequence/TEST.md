# TEST: 02-T03 CritiqueSequence

**Goal**: Prove the agent executes the critique chain across 3 prompts: `/critique` finds the planted flaws, `/reconcile` decides, `/implement` fixes the spec. Goal achievable only via the sequence.
**Bucket**: 02_WorkflowsSkills (IPPS content via `scaffold.json`)
**Expected outcome**: `_REVIEW_GREETER.md` with findings (planted flaws: vague requirement, language-count contradiction); `_SPEC_GREETER.md` fixed (vague phrase replaced, contradiction resolved).

## Runner Config

```yaml
tiers: [1, 2]
step_timeout_seconds: 600
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: review file exists with finding IDs; spec no longer contains the vague phrase; language count consistent
- Tier 2 >= 0.7: spec read before critique (CRITICAL), review written (CRITICAL), spec edited in step 3 (CRITICAL)

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, copy `workflows/critique.md`, `workflows/reconcile.md`, `workflows/implement.md`, `skills/write-documents` from `.lana/` into the scratch `.lana/`, open in Windsurf
2. Paste the three fenced prompts from `PROMPTS.md` in order
3. Copy the resulting `_REVIEW_*.md` and `_SPEC_GREETER.md` into `golden/`
