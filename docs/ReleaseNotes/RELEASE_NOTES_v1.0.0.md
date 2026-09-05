# Release Notes: v1.0.0

## Summary

Initial release of Lana, an ACP-compatible AI agent that runs as a CLI and supports rules, workflows, and skills on OpenAI and Anthropic backends. Includes a full agentic tool loop with 16 tools, session persistence with full recall, checkpoint compaction, cost tracking, an evaluation suite, ACP integration for Devin Desktop, and a PyApp single-binary distribution pipeline.

## Changes

### Features
- **Agent core**: multi-turn tool loop with 16 Cascade-compatible tools (read, edit, grep, shell, web research, trajectory search, etc.)
- **Dual-backend support**: OpenAI (Responses API) and Anthropic (Messages API with automatic caching)
- **Session persistence**: append-only JSONL with full-recall resume (system prompt, tool definitions, config snapshot recorded)
- **Checkpoint compaction**: usage-anchored token projection, deterministic todo state survival
- **Cost tracking**: per-turn and per-session cost with model pricing lookup
- **Command safety**: 3-tier execution policy (manual/auto/turbo), denylist, session-scoped approve-all (`a`)
- **Prompt queue**: headless multi-prompt execution from fenced markdown files
- **ACP frontend**: JSON-RPC 2.0 over stdio for Devin Desktop integration (session/new, session/load, session/prompt, event translation, permission/elicitation bridges)
- **Evaluation suite**: 9 tests across 3 buckets, 3-tier evaluators, golden benchmark comparison, aggregatable run structure
- **Selftest**: `/selftest` workflow with 6 categories (environment, configuration, prompt system, model sweep, effort matrix, tool calls)
- **Distribution**: PyApp single-binary pipeline with signing, checksums, smoke test, and locked-file handling
- **Zero-setup startup**: auto-creates data dirs, default config, and prompt library on first run

### Fixes
- Session-scoped approve-all (was incorrectly turn-scoped)
- ACP handshake leniency for Devin Desktop (auto-promote on missing `initialized` notification)
- Build script pre-flight lock check with `_old.exe` restore on failure
- Selftest `__pycache__` false positive in SKILL.md check
- Resume with missing file: self-contained error instead of traceback
- Renderer markup injection from untrusted event text
- Anthropic `web_search` `allowed_domains` removal
- `cp1252` JSONL crash fix

## Sessions

### _2026-08-29_LanaV1DesignQuestions

**Goal**: Collect and resolve open design questions for Lana-V1
**Outcome**: 43 design questions analyzed, decisions documented in LANAAGNT-IN01
**Artifacts**: `_INFO_OPEN_DESIGN_QUESTIONS.md`, `_INFO_CASCADE_TOOL_DEFINITIONS.md`

---

### _2026-08-29_Lana-MVP-1

**Goal**: Implement Lana MVP-1 per SPEC LANAAGNT-SP01
**Outcome**: Complete -- all 16 tools, agent loop, session persistence, cost tracking, CLI frontend
**Artifacts**: `_SPEC_LANA_MVP-1.md`, `_IMPL_LANA_MVP-1.md`, `_TEST_LANA_MVP-1.md`

---

### _2026-08-30_Lana-MVP-2

**Goal**: ACP frontend for Devin Desktop integration
**Outcome**: Complete -- JSON-RPC handshake, session management, event translation, permission bridges
**Artifacts**: `_SPEC_LANA_MVP-2_ACP.md`, `_IMPL_LANA_MVP-2_ACP.md`, `_TEST_LANA_MVP-2_ACP.md`

---

### _2026-08-30_ACPDocsUpdate

**Goal**: Verify and correct ACP protocol documentation against live sources
**Outcome**: 6 hallucinated wire shapes fixed across 9 files

---

### _2026-08-30_LanaDistribution

**Goal**: Single-binary distribution pipeline via PyApp
**Outcome**: Complete -- `build.ps1` producing signed/unsigned Windows x64 binary
**Artifacts**: `_SPEC_LANADIST.md`

---

### _2026-08-30_LanaEvalSuite

**Goal**: Evaluation framework for measuring agent quality
**Outcome**: 9 tests, golden benchmarks, 3-tier evaluators, runner infrastructure

---

### _2026-08-30_ModelTestSuite

**Goal**: Selftest framework for runtime health checks
**Outcome**: 6-category selftest with offline and live model tests

## Test Results

- **Offline tests**: 285 passed, 1 skipped
- **Selftest category 03** (Prompt System): 5 passed

## Binary

- `dist/lana-1.0.0-win-x64.exe` (23 MB, unsigned)
- SHA256: `28fe9b43255be4efdea9dacef0efe28645740157b0e9e841b9a1f7eac3fa203b`

## Document History

**[2026-08-31 01:40]**
- Initial release notes created
