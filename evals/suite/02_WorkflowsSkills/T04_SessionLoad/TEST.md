# TEST: 02-T04 SessionLoad

**Goal**: Prove the agent executes `/session-load` efficiently: reads the workflow from the correct agent folder, primes the correct workspace, reads session documents without unnecessary subfolder exploration, and produces a session summary.
**Bucket**: 02_WorkflowsSkills (IPPS content via `scaffold.json`)
**Expected outcome**: Session summary output. Agent reads session NOTES.md, PROGRESS.md, PROBLEMS.md and workspace !NOTES.md.

## Runner Config

```yaml
tiers: [1, 2]
step_timeout_seconds: 600
policy: turbo
```

## Pass Criteria

- Tier 1 >= 0.9: workspace !NOTES.md not deleted, session docs intact
- Tier 2 >= 0.7: workflow read from correct agent folder (CRITICAL), no .devin/ reads (CRITICAL), zero tool errors (HIGH), session docs read (HIGH), efficient tool usage (HIGH)

## Findings Coverage

This test covers findings from LANALOGS-BRNDSSNL-IN01:

- **PR-0001**: no read_file targeting `.devin/` (forbidden_tool_args check)
- **PR-0002**: zero tool_call_finished errors (tool_call_errors check)
- **PR-0003**: total tool calls bounded (tool_call_count check)
- **PR-0005**: FAILS.md not read in full or read with offset (tool_called max check)
- **PR-0006**: session completes within tool limit (tool_call_count check)
- **PR-0007**: no unnecessary subfolder reads (checked via tool_call_count bounds)

## Golden Production (Cascade + IPPS)

1. Copy `workspace/` to a scratch folder, run the runner's scaffold step manually (copy `workflows/session-load.md`, `workflows/prime.md`, `skills/session-management` from `.lana/` into the scratch `.lana/`), open in Windsurf
2. Paste the fenced prompt from `PROMPTS.md`
3. Capture the session summary output as golden reference
