# TEST: 01-T01 CreateFile

**Goal**: Prove the agent creates a new file with exact required structure from a single prompt using its edit tools.
**Bucket**: 01_Basics (raw tool usage, empty `.lana/`)
**Expected outcome**: `hello.py` exists with a `greet(name)` function and a main guard.

## Runner Config

```yaml
tiers: [1, 2]
step_timeout_seconds: 300
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: `hello.py` present, `greet(name)` defined, main guard present
- Tier 2 >= 0.7: file created via edit tool (CRITICAL), no edit without prior read (CRITICAL)

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, open it in Windsurf
2. Paste the fenced prompt from `PROMPTS.md`
3. Copy the resulting `hello.py` into `golden/`
