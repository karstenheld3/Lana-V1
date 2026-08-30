# Session Notes

**Doc ID**: ACPDOCUP-NOTES

## Task

UPDATE of existing ACP (Agent Client Protocol) documentation from 2026-06-12 to 2026-08-30.
Follows `HOW_TO_UPDATE_API_DOCS.md` and `HOW_TO_CREATE_API_DOCS.md` from KarstensWorkspace.

## Placeholder Values

- `[PRODUCT]` = ACP (Agent Client Protocol)
- `[COMPANY]` = AI-Standards
- `[TOPIC]` = ACP
- `[OLD_FOLDER]` = `ACP-AgentClientProtocol_2026-06-12`
- `[NEW_FOLDER]` = `ACP-AgentClientProtocol_2026-08-30`
- `[REF_COMPANY]` = Anthropic
- `[REFERENCE_FOLDER]` = `Anthropic_API_2026-07-27`
- `[PY_SDK_VERSION]` = TBD (ACP is a protocol spec; SDK verification may differ from API docs)
- `[JS_SDK_VERSION]` = TBD

## Paths

- Old: `E:\Dev\Delphios-Lana-V1\docs\AI-Standards\ACP-AgentClientProtocol_2026-06-12`
- New: `E:\Dev\Delphios-Lana-V1\docs\AI-Standards\ACP-AgentClientProtocol_2026-08-30`
- Reference: `E:\Dev\Delphios-Lana-V1\docs\Anthropic\Anthropic_API_2026-07-27`

## Notes

- ACP is a protocol specification, not a traditional API with SDKs. Prompts 4-5 (SDK verification) may need adaptation or skipping.
- Old folder has 14 INFO files (ACP-01 through ACP-14), no scaffolding files (__SOURCES, __TEMPLATE).
- Topic Number Retention Rules apply: existing INxx numbers kept, new topics start at IN15+.

## Prompt Templates

### Prompt 2: Inventory Existing Docs

```
Read the TOC and all _INFO_*.md files in
E:\Dev\Delphios-Lana-V1\docs\AI-Standards\ACP-AgentClientProtocol_2026-06-12

Also read python/README.md and javascript/README.md from
E:\Dev\Delphios-Lana-V1\docs\Anthropic\Anthropic_API_2026-07-27
to understand the target dual-language test structure.

Summarize: topic count, categories, highest INxx number,
SDK versions used (Python + JS), beta features,
language coverage gaps (topics with Python-only or JS-only examples).
Record findings in session NOTES.md under "Important Findings".
```

### Prompt 3: Research and Per-Topic Update

```
Copy __ACP_SOURCES.md and __TEMPLATE_*.md from ACP-AgentClientProtocol_2026-06-12 to ACP-AgentClientProtocol_2026-08-30.
Update __TEMPLATE to include both Python AND TypeScript SDK Examples sections.

This is an UPDATE of existing ACP API documentation.
Old version: ACP-AgentClientProtocol_2026-06-12. Files will be copied one at a time during per-topic update.

Use __ACP_SOURCES.md from ACP-AgentClientProtocol_2026-06-12 as starting source list.
Focus on: what changed since 2026-06-12, new endpoints, deprecations,
new SDK versions, renamed/removed features.

DUAL-LANGUAGE REQUIREMENT (see "INFO File Example Structure" in HOW_TO_CREATE):
Every INFO file with code examples MUST have BOTH:
- Python examples INLINE within each feature section (contextual)
- A consolidated `## TypeScript Examples` section (H2) near end of file
TypeScript need not duplicate every Python example - cover key patterns and API differences.
Use the latest stable SDK version for each language.
REST/JSON schema sections remain language-neutral.

/deep-research

with modified Phase 2 and 3:
- Phase 2: Identify which existing INxx topics need updating vs which are NEW.
- Phase 3: For existing topics, copy _INFO_*INxx*.md from ACP-AgentClientProtocol_2026-06-12 to
  ACP-AgentClientProtocol_2026-08-30 and update against findings. Add Document History:
  "[2026-08-30] Updated from ACP-AgentClientProtocol_2026-06-12".
  For new topics, create from scratch per standard deep-research.
  For ALL topics: add TypeScript examples where only Python exists.

/go
```

### Prompt 4: Review and Python SDK Verification

```
Review the updated TOC for completeness. Check for:
- Beta or preview features we missed
- Recently deprecated endpoints not yet marked
- Changelog entries since 2026-06-12 that we didn't cover
- INFO files missing Python OR TypeScript examples

Then run Python SDK verification:

1. Install TBD to e:\Dev\.tools\llm-venv
2. Follow SDK Code Verification (AST Methodology) from HOW_TO_CREATE_API_DOCS.md
   targeting ACP-AgentClientProtocol_2026-08-30
3. Create ACP-AgentClientProtocol_2026-08-30/python/ subfolder with:
   - _lib.py (shared client init, API key loading from e:\Dev\.api-keys.txt)
   - Per-topic test files (NN_topic_test.py) that execute Python examples from INFO files
   - run_all.py to aggregate results
   - sdk_methods.py + sdk_methods.json (SDK introspection)
   - README.md documenting: SDK version, test count, pass/fail/skip, repro commands
4. Run all tests, record results in NN_*_results.json and run_all_summary.json
5. Fix any WRONG_PARAM or METHOD_NOT_FOUND issues in INFO files

Model for python/ structure:
E:\Dev\Delphios-Lana-V1\docs\Anthropic\Anthropic_API_2026-07-27\python\README.md

/go
```

### Prompt 5: JavaScript SDK Verification

```
Run JavaScript/TypeScript SDK verification:

1. Install TBD (npm install in a temp location or project root)
2. Build JS SDK method map by introspecting the installed package:
   - Parse index.d.ts or resources/*.d.ts for exported methods and parameters
   - Output to ACP-AgentClientProtocol_2026-08-30/javascript/sdk_methods.json
3. Extract all typescript blocks from _INFO_*.md files in ACP-AgentClientProtocol_2026-08-30
4. Create ACP-AgentClientProtocol_2026-08-30/javascript/ subfolder with:
   - sdk_examples_test.cjs - tests that verify TS examples compile/run against live API
   - sdk_test.cjs - model parameter combination tests
   - sdk_methods.json - JS SDK method introspection
   - README.md documenting: SDK version, test count, pass/fail, repro commands
5. Run all tests, record results in *_results.json
6. Fix any incorrect method names or parameters in INFO file TypeScript sections

Model for javascript/ structure:
E:\Dev\Delphios-Lana-V1\docs\Anthropic\Anthropic_API_2026-07-27\javascript\README.md

/go
```

### Prompt 6: Version Comparison

```
Compare the updated files in
E:\Dev\Delphios-Lana-V1\docs\AI-Standards\ACP-AgentClientProtocol_2026-08-30
against the originals in
E:\Dev\Delphios-Lana-V1\docs\AI-Standards\ACP-AgentClientProtocol_2026-06-12
using topic numbers for direct INxx-to-INxx mapping. Create in
E:\Dev\Delphios-Lana-V1\docs\AI-Standards\ACP-AgentClientProtocol_2026-08-30
a version comparison document: __ACP_CHANGES.md

Structure:

1. Executive Summary (topic count old vs new, headline changes)
2. Complete Topic Mapping (old INxx -> new INxx, per section)
3. New Topics (completely new API capabilities)
4. Removed/Consolidated Topics (merged, deprecated, or dropped)
5. Changed Topics (major expansions, parameter changes, SDK changes)
6. Deprecations (sunset dates, migration paths)
7. Recommended Actions (immediate, short-term, evaluate)

Keep it short but instructive. Focus on what a developer using the old version
needs to know to update their integration.
```

### Prompt 7: Size Reasonability and Language Coverage Analysis

```
Compare file sizes between
E:\Dev\Delphios-Lana-V1\docs\AI-Standards\ACP-AgentClientProtocol_2026-06-12
and
E:\Dev\Delphios-Lana-V1\docs\AI-Standards\ACP-AgentClientProtocol_2026-08-30

For each _INFO_*.md file that exists in BOTH folders (using INxx topic mapping):
1. Count lines in old and new version
2. Flag any new file that is < 70% of its old counterpart

For flagged files:
- Read the old version section headings (## and ###)
- Read the new version section headings
- Identify missing sections (present in old, absent in new)
- Check if missing content was intentionally consolidated elsewhere or accidentally dropped

Fix: Restore any accidentally dropped content (parameters, response objects,
SDK examples, error responses, gotchas). Do NOT restore verbose production
pipeline classes or "Differences from Other APIs" sections unless they contain
unique API knowledge.

Dual-language coverage check:
- Grep ALL _INFO_*.md files for python blocks AND `## TypeScript Examples` sections
- Flag any file with Python examples but NO TypeScript section (or vice versa)
- Fix: Add missing language examples for flagged files
- Exception: Files with NO code examples at all (pure REST/schema docs) are OK

Also verify:
- ALL _INFO_*.md files in ACP-AgentClientProtocol_2026-08-30 are > 50 lines. Expand stubs.
- python/README.md exists with test results summary
- javascript/README.md exists with test results summary

Report final metrics: total KB and file count for both folders,
Python test pass rate, JavaScript test pass rate.
```

## Important Findings

### Inventory (Prompt 2, 2026-08-30)

**Old folder**: 14 INFO files, no scaffolding (__SOURCES, __TEMPLATE, __TOC), no python/ or javascript/ subfolders.

**Topic count and categories** (5 categories, 12 content topics + 1 summary + 1 sources):
- **Overview and Architecture** (2): IN03 ProblemAndSolution, IN04 Architecture
- **Protocol Specification** (6): IN05 Initialization, IN06 SessionLifecycle, IN07 PromptTurnAndStreaming, IN08 ToolCallsAndPermissions, IN09 AuthenticationAndSecurity, IN10 TransportsAndExtensibility
- **Ecosystem** (2): IN11 AgentsAndClients, IN12 SDKsAndLibraries
- **Evolution and Roadmap** (1): IN13 VersionHistoryAndRoadmap
- **Best Practices and Limitations** (1): IN14 GotchasAndBestPractices
- **Meta** (2): IN01 Summary, IN02 Sources

**Highest INxx number**: IN14 (= ACP-14)

**SDK versions used**: None tracked (ACP is a protocol spec). ACP SDK packages mentioned:
- Python: `agent-client-protocol` (pip), Python 3.10+
- TypeScript: `@agentclientprotocol/sdk` (npm)
- Also: Kotlin (acp-kotlin), Java (java-sdk), Rust (agent-client-protocol crate)

**Beta features**: v2 proposal is draft (not beta). No beta-gated features in v1.

**Language coverage gaps**:
- IN05 Initialization: Has both Python and TypeScript SDK examples (inline, not dual-language format)
- IN12 SDKsAndLibraries: Has both Python and TypeScript examples (inline)
- IN03-IN04, IN06-IN11, IN13-IN14: JSON-only protocol examples, no SDK code examples
- **No file uses the dual-language format** (inline Python + consolidated `## TypeScript Examples` H2 section)

**Source count**: 21 sources (15 T1 / 3 T2 / 3 T3), all accessed 2026-06-12

**Key observations**:
1. No __SOURCES or __TOC scaffolding files exist in old folder; will need to create for new folder
2. ACP is a protocol spec, not a traditional API. Most files contain JSON-RPC wire format examples, not SDK code. Dual-language requirement applies mainly to IN05, IN12, and any new topics with SDK usage examples.
3. Prompts 4-5 (SDK verification) need significant adaptation: no traditional REST API to test. Could verify ACP SDK package installation and basic agent creation patterns instead.
4. v2 proposal was in draft as of 2026-06-12; research must check current v2 status (stabilized? new RFDs?)
5. Ecosystem lists (35+ agents, 20+ clients) are fast-moving; need fresh counts

### Reference dual-language structure (Anthropic_API_2026-07-27)

**Python test structure**: 14 test files + _lib.py + run_all.py + sdk_methods.py/json + sdk_test.py. 72 tests (63 pass, 9 skip). SDK: anthropic 0.120.0.

**JavaScript test structure**: sdk_examples_test.cjs (14 tests) + sdk_test.cjs (22 tests) + sdk_methods.json. SDK: @anthropic-ai/sdk 0.115.0.

**Pattern**: Per-topic test files (NN_topic_test.py), each producing NN_topic_results.json. run_all.py aggregates. README.md documents repro commands and known bugs found.

### Prompt 3 Research Findings (2026-08-30)

**New v1 stabilizations since 2026-06-12** (8 features):
1. Elicitation (elicitation/create, elicitation/complete) - July 24, 2026
2. Boolean Config Options (session.configOptions.boolean)
3. Request Cancellation ($/cancel_request) - June 29, 2026
4. Model Config Category (model_config)
5. Message IDs (messageId on message chunks)
6. Session Usage Updates (usage_update notifications)
7. Session Delete (session/delete)
8. Rust + TypeScript SDKs 1.0 - June 25, 2026

**ACP v2 Draft** published July 20, 2026. Key breaking changes:
- Prompt lifecycle: response = acknowledgment only, state_update replaces stopReason
- Tool calls: unified upsert, streaming content chunks
- Diff: structured changes array + optional git_patch
- Capabilities: single field, object markers
- Removals: client fs/terminal, session/load, session modes, SSE MCP transport
- Auth: authenticate -> auth/login, logout -> auth/logout

**Ecosystem growth**:
- Agents: 40+ (up from 35+), new: Kimi CLI, fast-agent, crow-cli, OpenCode, Devin CLI
- Clients: 50+ across 8 categories (up from 20+ / 7 categories), new category: Connectors
- Notable new clients: Gold Band, Jockey, Kepler (GitKraken), ACP Inspector, Newio, VACP (voice)

**SDK versions (current)**:
- Python: `agent-client-protocol` v0.12.1 (Aug 16, 2026). Added HTTP/WS transport, schema v1.19.0
- TypeScript: `@agentclientprotocol/sdk` v1.4.0. Experimental v2 import available
- Rust: `agent-client-protocol` v1.0.0+

**New topics created**: IN15 (Elicitation), IN16 (v2 Migration Overview)
**Dual-language examples added to**: IN05 (Initialization), IN12 (SDKs)

**Adaptation for Prompts 4-5**: ACP is a protocol, not a REST API. SDK verification should focus on:
- Python: Install `agent-client-protocol`, verify import of `acp.schema`, `acp.helpers`, create minimal echo agent
- TypeScript: Install `@agentclientprotocol/sdk`, verify import, create minimal agent, test experimental v2 import
