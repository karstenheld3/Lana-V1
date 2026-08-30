# TEST: 03-T01 TranscribeLocal

**Goal**: Prove the agent executes the `/transcribe` workflow on a local HTML fixture with full content preservation.
**Bucket**: 03_AdvancedCapabilities (IPPS content via `scaffold.json`, local fixture - no network)
**Expected outcome**: `output/pricing_page.md` reproducing all fixture content (headings, list, table incl. all prices) in markdown.

## Runner Config

```yaml
tiers: [1, 2, 3]
step_timeout_seconds: 600
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: output file exists, product name and all price values present
- Tier 2 >= 0.7: fixture actually read (CRITICAL), output written via edit tool (CRITICAL)
- Tier 3 >= 0.7: judge rubric - completeness, structure fidelity, no invention

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, copy `workflows/transcribe.md` from `.lana/` into the scratch `.lana/workflows/`, open in Windsurf
2. Paste the fenced prompt from `PROMPTS.md`
3. Copy the resulting `output/pricing_page.md` into `golden/`
