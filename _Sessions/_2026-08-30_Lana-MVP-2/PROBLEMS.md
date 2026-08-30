# Session Problems

**Doc ID**: LANAACPB-MVP2-PROBLEMS

Track problems using ID format: `LANAACPB-PR-[NNNN]`

## Open

**LANAACPB-PR-0002: grep_search returns zero matches on ACP INFO doc files with known content**
- **History**: Added 2026-08-30 14:05
- **Assessment**: searches for `capabilit`/`agentCapabilities`/`embeddedContext` in both `ACP-AgentClientProtocol_*` folders return nothing although the files contain the terms (verified by direct read; files are plain UTF-8, `# AC` first bytes, no BOM). Some folder-wide queries match (e.g., `resource`), others silently miss. Workaround: `read_file` for ground truth on these folders; do not trust negative grep results there.
- **Decision needed**: none for the session - recorded so future searches do not draw false negatives

## Resolved

**LANAACPB-PR-0001: 2026-08-30 ACP INFO refresh contained hallucinated wire shapes**
- **History**: Added 2026-08-30 14:05 | Resolved 2026-08-30 14:25
- **Solution**: 8 files corrected in-place against live official docs with per-file Document History entries; every correction backed by LANAACPB-IN01 verified findings
