# TEST: 03-T02 DeepResearch

**Goal**: Prove the agent executes `/deep-research` with real web research: searches, fetches sources, and produces an INFO document with an auditable citation trail.
**Bucket**: 03_AdvancedCapabilities (IPPS content via `scaffold.json`, LIVE WEB REQUIRED)
**Expected outcome**: `_INFO_BERLINWALL.md` answering the unambiguous headline question (the Berlin Wall fell on 1989-11-09) with a Sources section, https URLs, and verification labels.

Question design: unambiguous headline answer chosen deliberately - headline conclusions converge across runs (CSRCMP-IN10 CC-1=1.00) while sources vary, so the manifest checks the answer and the citation STRUCTURE, never specific sources.

## Runner Config

```yaml
tiers: [1, 2, 3]
step_timeout_seconds: 1200
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: INFO file with correct date, Summary and Sources sections, https URLs, verification labels
- Tier 2 >= 0.7: web searches actually executed (CRITICAL), source URLs actually fetched (HIGH)
- Tier 3 >= 0.7: judge rubric - answer correctness, citation auditability, source diversity, no invention

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, copy `workflows/deep-research.md` + `skills/deep-research` from `.lana/` into the scratch `.lana/`, open in Windsurf
2. Paste the fenced prompt from `PROMPTS.md` (requires live web access)
3. Copy the resulting `_INFO_BERLINWALL.md` (and `_SOURCES/` if produced) into `golden/`

Golden status: PENDING - requires a live Cascade deep-research run.
