# TEST: 02-T02 VerifyFix

**Goal**: Prove the agent executes `/verify` on a document with known IPPS rule violations, FIXES them (verify has fix authority), and reports the fixes in a second step.
**Bucket**: 02_WorkflowsSkills (IPPS content via `scaffold.json`)
**Expected outcome**: `STATUS.md` violations fixed (table → list, emojis → text, locale date → ISO, `---` separator removed, content preserved); `FIXLOG.md` lists the applied fixes.

## Runner Config

```yaml
tiers: [1, 2]
step_timeout_seconds: 600
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: no emojis, no table syntax, no locale date; ISO date present; original facts preserved; FIXLOG.md exists with list items
- Tier 2 >= 0.7: STATUS.md read before editing (CRITICAL), edits applied via edit tools (CRITICAL)

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, copy `workflows/verify.md`, `rules/core-conventions.md`, `skills/write-documents` from `.lana/` into the scratch `.lana/`, open in Windsurf
2. Paste the two fenced prompts from `PROMPTS.md` in order
3. Copy the resulting `STATUS.md` and `FIXLOG.md` into `golden/`
