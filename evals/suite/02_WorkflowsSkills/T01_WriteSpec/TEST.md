# TEST: 02-T01 WriteSpec

**Goal**: Prove the agent executes the IPPS `/write-spec` workflow: reads the skill material and produces a SPEC document following the template structure and ID system.
**Bucket**: 02_WorkflowsSkills (IPPS content via `scaffold.json`)
**Expected outcome**: `_SPEC_WORDCOUNT.md` with header block, MUST-NOT-FORGET, TOC, FR/DD IDs, Document History.

## Runner Config

```yaml
tiers: [1, 2]
step_timeout_seconds: 600
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: spec file exists with Doc ID `WRDCOUNT-SP01`, MUST-NOT-FORGET section, `WRDCOUNT-FR-*` and `WRDCOUNT-DD-*` items, Document History
- Tier 2 >= 0.7: SPEC template actually read (HIGH), spec written via edit tool (CRITICAL)

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, run the runner's scaffold step manually (copy `workflows/write-spec.md`, `workflows/verify.md`, `skills/write-documents` from `.lana/` into the scratch `.lana/`), open in Windsurf
2. Paste the fenced prompt from `PROMPTS.md`
3. Copy the resulting `_SPEC_WORDCOUNT.md` into `golden/`
