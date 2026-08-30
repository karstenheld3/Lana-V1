# Failure Log

Lessons learned from past mistakes. Never delete entries unconfirmed; only append or mark as resolved.
ID format: `LANADIST-FL-[NNNN]`

## Failures

**LANADIST-FL-0001: PyApp cache reuse silently serves stale bundled content on same-version rebuild**
- **Severity**: [HIGH]
- **When**: 2026-08-30 22:54
- **Where**: `_build.ps1` step 5 (smoke test), PyApp cache at `%LOCALAPPDATA%\pyapp\data\lana`
- **What**: Rebuilding the binary with the same version (1.1.0) after adding new workflows/skills produces a wheel with the new content, but the smoke test and all subsequent runs use the stale PyApp cache. The binary reports the correct version but serves outdated bundled agent files. New selftest workflow and skill were in the wheel but absent from the running binary.
- **Evidence**: Wheel contains `lana/bundled/agent/workflows/selftest.md` (verified via zipfile listing). PyApp cache at `%LOCALAPPDATA%\pyapp\data\lana` has 46 workflows (no selftest). Binary reports "46 workflows, 23 skills" and "Unknown workflow '/selftest'".
- **Root cause**: PyApp caches the extracted Python + installed wheel by project name + version. Same version = cache hit = skip reinstall. `_build.ps1` smoke test runs `--version` which triggers PyApp extraction, but if cache exists from a prior build with the same version, the new wheel embedded in the rebuilt binary is never installed. The smoke test passes (version string matches) without validating the actual bundled content.
- **Workflow re-read findings**: `_build.ps1` line 111 checks the wheel for `lana/bundled/agent/` (present = OK), but never validates the running binary's actual prompt system count against the source `.lana/`. The smoke test (line 141) only checks `--version` output. No guard against PyApp cache staleness.
- **Suggested fix**: Add `& $Script:Artifact self restore` before the smoke test in `_build.ps1` to clear the PyApp cache, forcing a fresh extraction from the new wheel. Alternatively, validate the prompt system count from the smoke test output.

**LANADIST-FL-0002: Agent misdiagnosed root cause as stale materialization instead of stale PyApp cache**
- **Severity**: [MEDIUM]
- **When**: 2026-08-30 22:52
- **Where**: Agent diagnostic response
- **What**: When asked why `/selftest` was missing from the binary, agent incorrectly diagnosed the root cause as stale `dist/.lana` materialization (created at 17:04, before selftest was added). The actual root cause was the PyApp cache at `%LOCALAPPDATA%\pyapp\data\lana` serving the old wheel despite the binary being rebuilt.
- **Evidence**: After rebuilding the binary and deleting `dist/.lana`, running `--version` did not re-materialize (expected - `--version` exits before config load). The agent claimed the fix was "delete `dist/.lana`" but never verified the hypothesis end-to-end.
- **Root cause**: Agent assumed the binary's bundled content was fresh (based on build timestamp) and focused on the downstream materialization. Did not consider the PyApp runtime cache layer between "wheel in binary" and "installed package on disk". Did not verify the hypothesis by checking the actual PyApp cache or running the binary fully.
- **Workflow re-read findings**: N/A (diagnostic task, no workflow)
- **Suggested fix**: When diagnosing runtime packaging issues, always trace the full chain: source -> wheel -> binary -> cache -> installed -> materialized. Verify each layer empirically.

