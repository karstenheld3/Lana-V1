# STRUT: Grok API Code Example Verification

**Doc ID**: GROKAPI-STRUT01
**Goal**: Verify and improve all 86 Python code examples across 35 INFO documents against xai-sdk v1.9.1 source

**Depends on:**
- xai-sdk v1.9.1 installed at `e:\Dev\.tools\llm-venv\Lib\site-packages\xai_sdk\`

## MUST-NOT-FORGET

- Verify imports exist in actual SDK (e.g., `from xai_sdk.chat import user, system`)
- Check method signatures match SDK source (parameter names, types, defaults)
- xAI SDK uses gRPC, NOT REST - code using `from xai_sdk import Client` uses gRPC client
- OpenAI SDK examples use REST via `base_url="https://api.x.ai/v1"` - different from xAI SDK
- `xai_sdk.tools` exports: `web_search`, `x_search`, `code_execution`, `collections_search`, `mcp`
- `xai_sdk.chat` exports: `user`, `system`, `assistant`, `developer`, `tool_result`, `tool`, `required_tool`, `text`, `image`, `file`
- `xai_sdk.video.VideoGenerationError` exists at that path
- Video API: `client.video.generate()` (sync polling), `client.video.start()` + `client.video.get()`
- Image API: `client.image.sample()`, not `client.image.generate()`
- SearchParameters imported from `xai_sdk.search`, NOT `xai_sdk.chat`
- No `xai_sdk.chat.SearchParameters` - it is `from xai_sdk.search import SearchParameters`
- Follow /improve workflow: find issues, fix immediately, update Document History
- APAPALAN: precision first, brevity second

## Plan

[x] P1 [VERIFY]: Core Setup and SDK Reference (5 files, ~10 examples)
├─ Objectives:
│   └─ [x] All core setup examples match SDK v1.9.1 API ← P1-D1
├─ Strategy: Read each file, compare code examples against SDK source, fix in-place
├─ [x] P1-S1 [VERIFY](IN01_INTRODUCTION - 3 examples) - all correct
├─ [x] P1-S2 [VERIFY](IN02_AUTHENTICATION - 1 example) - correct
├─ [x] P1-S3 [VERIFY](IN39_XAI_SDK - 3 examples) - all correct
├─ [x] P1-S4 [VERIFY](IN44_REST_REFERENCE - 1 example) - correct
├─ [x] P1-S5 [VERIFY](IN45_SDK_REFERENCE - 2 examples) - all correct
├─ Deliverables:
│   └─ [x] P1-D1: Core setup examples verified - 0 fixes needed
└─> Transitions:
    - P1-D1 checked → P2 [VERIFY]

[x] P2 [VERIFY]: Chat, Responses, and Streaming (7 files, ~21 examples)
├─ Objectives:
│   └─ [x] All chat/response examples match SDK v1.9.1 API ← P2-D1
├─ Strategy: Focus on OpenAI SDK vs xAI SDK usage patterns, method signatures
├─ [x] P2-S1 [VERIFY](IN06_RESPONSES_API - 7 examples) - all correct
├─ [x] P2-S2 [VERIFY](IN07_CHAT_COMPLETIONS - 3 examples) - all correct
├─ [x] P2-S3 [VERIFY](IN08_STREAMING - 4 examples) - all correct
├─ [x] P2-S4 [VERIFY](IN09_REASONING - 2 examples) - all correct
├─ [x] P2-S5 [VERIFY](IN10_STRUCTURED_OUTPUTS - 2 examples) - all correct
├─ [x] P2-S6 [VERIFY](IN11_MULTI_AGENT - 3 examples) - all correct
├─ [x] P2-S7 [VERIFY](IN36_PROMPT_ENGINEERING - 2 examples) - all correct
├─ Deliverables:
│   └─ [x] P2-D1: Chat/response examples verified - 0 fixes needed
└─> Transitions:
    - P2-D1 checked → P3 [VERIFY]

[x] P3 [VERIFY]: Tools and Search (9 files, ~27 examples)
├─ Objectives:
│   └─ [x] All tool/search examples match SDK v1.9.1 API ← P3-D1
├─ Strategy: Verify tool function signatures, search parameter classes, handle filtering
├─ [x] P3-S1 [VERIFY](IN13_TOOLS_OVERVIEW - 3 examples) - all correct
├─ [x] P3-S2 [VERIFY](IN14_FUNCTION_CALLING - 3 examples) - 1 fix: added tool_call_id to tool_result()
├─ [x] P3-S3 [VERIFY](IN15_WEB_SEARCH - 3 examples) - all correct
├─ [x] P3-S4 [VERIFY](IN16_X_SEARCH - 6 examples) - all correct
├─ [x] P3-S5 [VERIFY](IN17_CODE_EXECUTION - 2 examples) - all correct
├─ [x] P3-S6 [VERIFY](IN18_COLLECTIONS_SEARCH - 3 examples) - all correct
├─ [x] P3-S7 [VERIFY](IN19_REMOTE_MCP - 2 examples) - all correct
├─ [x] P3-S8 [VERIFY](IN20_TOOL_ADVANCED - 3 examples) - all correct
├─ [x] P3-S9 [VERIFY](IN21_TOOL_DETAILS - 1 example) - correct
├─ Deliverables:
│   └─ [x] P3-D1: Tool/search examples verified - 1 fix applied (IN14)
└─> Transitions:
    - P3-D1 checked → P4 [VERIFY]

[x] P4 [VERIFY]: Media and Files (8 files, ~13 examples)
├─ Objectives:
│   └─ [x] All media/file examples match SDK v1.9.1 API ← P4-D1
├─ Strategy: Verify image, video, voice, TTS, files, collections APIs
├─ [x] P4-S1 [VERIFY](IN22_IMAGE_UNDERSTANDING - 3 examples) - all correct
├─ [x] P4-S2 [VERIFY](IN23_IMAGE_GENERATION - 1 example) - correct
├─ [x] P4-S3 [VERIFY](IN24_VIDEO_GENERATION - 2 examples) - all correct
├─ [x] P4-S4 [VERIFY](IN26_VOICE_AGENT - 1 example) - correct
├─ [x] P4-S5 [VERIFY](IN27_TEXT_TO_SPEECH - 1 example) - correct
├─ [x] P4-S6 [VERIFY](IN28_FILES_API - 2 examples) - all correct
├─ [x] P4-S7 [VERIFY](IN29_CHAT_WITH_FILES - 1 example) - correct
├─ [x] P4-S8 [VERIFY](IN30_COLLECTIONS_API - 2 examples) - all correct
├─ Deliverables:
│   └─ [x] P4-D1: Media/file examples verified - 0 fixes needed
└─> Transitions:
    - P4-D1 checked → P5 [VERIFY]

[x] P5 [VERIFY]: Advanced and Operational (6 files, ~15 examples)
├─ Objectives:
│   └─ [x] All advanced/operational examples match SDK v1.9.1 API ← P5-D1
├─ Strategy: Verify models, errors, rate limits, migration, caching, batch
├─ [x] P5-S1 [VERIFY](IN03_MODELS - 2 examples) - all correct
├─ [x] P5-S2 [VERIFY](IN04_ERRORS - 2 examples) - all correct
├─ [x] P5-S3 [VERIFY](IN05_RATE_LIMITS - 3 examples) - all correct
├─ [x] P5-S4 [VERIFY](IN12_MIGRATION - 3 examples) - all correct
├─ [x] P5-S5 [VERIFY](IN33_PROMPT_CACHING - 2 examples) - all correct
├─ [x] P5-S6 [VERIFY](IN34_BATCH_API - 1 example) - correct
├─ Deliverables:
│   └─ [x] P5-D1: Advanced/operational examples verified - 0 fixes needed
└─> Transitions:
    - P5-D1 checked → [END]

## Document History

**[2026-03-20 12:30]**
- All 5 phases completed: 86 examples verified, 1 fix applied (IN14 tool_call_id)

**[2026-03-20 12:00]**
- Initial STRUT plan created with 5 phases, 35 files, 86 code examples
