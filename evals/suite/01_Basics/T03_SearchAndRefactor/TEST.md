# TEST: 01-T03 SearchAndRefactor

**Goal**: Prove the agent finds all usages of a function across multiple files (search) and renames it consistently (multi-file edit).
**Bucket**: 01_Basics (raw tool usage, empty `.lana/`)
**Expected outcome**: `calc_total` renamed to `compute_invoice_total` in all 3 source files, no old name left, behavior untouched.

## Runner Config

```yaml
tiers: [1, 2]
step_timeout_seconds: 300
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: new name present in all 3 files, old name absent everywhere
- Tier 2 >= 0.7: search performed before editing (HIGH), edits only after reads (CRITICAL)

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, open it in Windsurf
2. Paste the fenced prompt from `PROMPTS.md`
3. Copy the three resulting `.py` files into `golden/`
