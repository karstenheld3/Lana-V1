# TEST: 01-T04 ShellExecution

**Goal**: Prove the agent uses shell execution to gather facts from the workspace and records a deterministic result.
**Bucket**: 01_Basics (raw tool usage, empty `.lana/`)
**Expected outcome**: `count.txt` containing the number of `.log` files in `data/` (exactly 4).

## Runner Config

```yaml
tiers: [1, 2]
step_timeout_seconds: 300
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: `count.txt` exists and contains 4
- Tier 2 >= 0.7: a shell command was executed (CRITICAL)

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, open it in Windsurf
2. Paste the fenced prompt from `PROMPTS.md`
3. Copy the resulting `count.txt` into `golden/`
