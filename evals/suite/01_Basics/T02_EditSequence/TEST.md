# TEST: 01-T02 EditSequence

**Goal**: Prove the agent handles a 2-prompt queue where step 2 builds on step 1's output (read, then extend).
**Bucket**: 01_Basics (raw tool usage, empty `.lana/`)
**Expected outcome**: `notes.md` with sections Alpha, Beta (step 1) and Gamma referencing Alpha's fact (step 2).

## Runner Config

```yaml
tiers: [1, 2]
step_timeout_seconds: 300
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: all 3 sections present; Gamma references the launch year 2031 from Alpha
- Tier 2 >= 0.7: file created via edit tool (CRITICAL), no edit without prior read (CRITICAL)

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, open it in Windsurf
2. Paste the two fenced prompts from `PROMPTS.md` in order (separate messages)
3. Copy the resulting `notes.md` into `golden/`
