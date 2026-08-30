# STRUT: Gemini API Python Code Example Verification

**Doc ID**: GEMAPI-STRUT01
**Goal**: Verify all 105 Python code examples against google-genai SDK v1.68.0 and improve with SDK-verified corrections
**SDK path**: `E:\Dev\.tools\llm-venv\Lib\site-packages\google\genai` (v1.68.0)

## MUST-NOT-FORGET

- KEEP original examples from API docs, ADD corrected version below with SDK source citation
- Note source of each correction: python file path + SDK version
- Check imports, class names, method signatures, enum values, parameter names
- ThinkingLevel enum: LOW, MEDIUM, HIGH, MINIMAL (NOT "off"/"default")
- Env var: SDK accepts both GOOGLE_API_KEY and GEMINI_API_KEY (prefers GOOGLE_API_KEY)
- AutomaticFunctionCallingConfig.disable (bool), not enable
- SafetySetting uses HarmCategory enum + HarmBlockThreshold enum
- GenerateContentConfig uses `response_json_schema` (not `response_schema` for JSON)
- Tool fields: google_search, code_execution, url_context, google_maps, computer_use, mcp_servers

## Known SDK Discrepancies Found During Exploration

- `ThinkingLevel` enum: LOW, MEDIUM, HIGH, MINIMAL (no "off", no "default")
- `ThinkingConfig` fields: `thinking_budget` (int), `thinking_level` (ThinkingLevel), `include_thoughts` (bool)
- `GenerateContentConfig` uses `thinking_config` (not `thinkingConfig`)
- `LiveConnectConfig` has `enable_affective_dialog`, `proactivity`, `session_resumption`, `input_audio_transcription`, `output_audio_transcription`
- `Tool` has `google_search` (GoogleSearch), `code_execution` (ToolCodeExecution), `url_context` (UrlContext), `google_maps` (GoogleMaps)
- `ImageConfig` has `aspect_ratio`, `image_size`, `person_generation`, `output_mime_type`
- `EmbedContentConfig` has `task_type`, `title`, `output_dimensionality`, `mime_type`, `auto_truncate`

## Code Examples Catalog (105 total across 40 files)

### Group A: Core API (IN01-IN06) - 19 examples

- IN01 (4): Basic Text Gen, System Instruction, Multi-Turn, Multimodal
- IN02 (4): Env Var Auth, Explicit Key, Ephemeral Token, Locked Token
- IN03 (3): Error format, Retry Backoff, Comprehensive Error Handling
- IN04 (2): Rate Limit Retry, Batch Rate Awareness
- IN05 (2): List Models, Get Model Info
- IN06 (4): OpenAI compat snippets (4 blocks)

### Group B: Content Generation (IN07-IN11) - 18 examples

- IN07 (5): Basic Gen, Full Config, Multi-Turn Roles, Streaming, JSON Output
- IN08 (3): Basic Streaming, Full Response Assembly, Error Handling
- IN09 (3): Pydantic Model, Enum Constrained, Streaming Structured
- IN10 (4): Default Thinking, Disable Thinking, High Budget, G3 Level
- IN11 (3): Custom Safety, Check Ratings, Permissive Settings

### Group C: Multimodal (IN12-IN15) - 9 examples

- IN12 (3): Inline Image, Multiple Images, File API Image
- IN13 (2): Audio Transcription, Audio Summarization
- IN14 (2): Video Understanding, Timestamp Query
- IN15 (2): PDF Analysis, Inline PDF

### Group D: Tools & Functions (IN16-IN22) - 16 examples

- IN16 (4): Basic FC, Auto FC, ANY mode, MCP
- IN17 (3): Google Search, Code Execution, Multi-Tool
- IN18 (2): Basic Grounding, Citation Extraction
- IN19 (2): Basic Code Exec, Data Analysis
- IN20 (2): Analyze Web Page, Compare URLs
- IN21 (2): Find Places, Combined Search+Maps
- IN22 (1): Computer Use

### Group E: Files/Cache/Embed/Batch (IN23-IN28) - 14 examples

- IN23 (3): Upload+Use, List+Cleanup, Upload Display Name
- IN24 (2): Cache Document, Cache Management
- IN25 (2): Count Tokens, Count Multimodal
- IN26 (3): Single Embed, Batch Embed, Multimodal Embed
- IN27 (2): Submit Batch, Monitor Results
- IN28 (2): Build+Query KB, Inline Passages

### Group F: Media Generation (IN29-IN31) - 8 examples

- IN29 (4): Text-to-Image, Image Editing, Text+Image, Imagen 4
- IN30 (2): Text-to-Video, Veo 3.1 Audio
- IN31 (2): TTS, Multi-Speaker TTS

### Group G: Live API (IN32-IN34) - 6 examples

- IN32 (3): Basic Live, Voice Conversation, Session Resumption
- IN33 (1): Affective Voice
- IN34 (2): Screen Sharing, Camera+Voice

### Group H: Advanced & Platform (IN35-IN41) - 15 examples

- IN35 (3): Basic System Instr, Multi-Part, Cached System
- IN36 (2): Multi-Doc Analysis, Context Budget
- IN37 (2): Basic Deep Research, Streaming Deep Research
- IN38 (3): Context engineering blocks
- IN39 (13): SDK usage patterns (snippets + 3 full examples)
- IN40 (2): Vertex AI Client, Switch Backends
- IN41 (4): Gemini 3 feature blocks

## Plan

[x] P1 [VERIFY]: Core API examples (IN01-IN06, 19 examples)
├─ Objectives:
│   └─ [x] All core API examples verified and corrected ← P1-D1
├─ Strategy: Read each file, compare each Python block against SDK source, add corrections
├─ [x] P1-S1 [VERIFY](IN01 - 4 examples) OK
├─ [x] P1-S2 [VERIFY](IN02 - 4 examples) OK
├─ [x] P1-S3 [VERIFY](IN03 - 3 examples) FIXED: google.api_core.exceptions -> google.genai.errors
├─ [x] P1-S4 [VERIFY](IN04 - 2 examples) FIXED: google.api_core.exceptions -> google.genai.errors
├─ [x] P1-S5 [VERIFY](IN05 - 2 examples) OK
├─ [x] P1-S6 [VERIFY](IN06 - 4 examples) OK (uses OpenAI SDK, not google-genai)
├─ Deliverables:
│   └─ [x] P1-D1: IN01-IN06 examples verified, corrections added where needed
└─> Transitions:
    - P1-D1 checked → [P2]

[x] P2 [VERIFY]: Content Generation examples (IN07-IN11, 18 examples)
├─ Objectives:
│   └─ [x] All content gen examples verified and corrected ← P2-D1
├─ Strategy: Focus on GenerateContentConfig, ThinkingConfig, SafetySetting types
├─ [x] P2-S1 [VERIFY](IN07 - 5 examples) OK
├─ [x] P2-S2 [VERIFY](IN08 - 3 examples) FIXED: google.api_core.exceptions -> google.genai.errors
├─ [x] P2-S3 [VERIFY](IN09 - 3 examples) OK
├─ [x] P2-S4 [VERIFY](IN10 - 4 examples) OK (ThinkingConfig accepts string "high" -> auto-converts to enum)
├─ [x] P2-S5 [VERIFY](IN11 - 3 examples) OK
├─ Deliverables:
│   └─ [x] P2-D1: IN07-IN11 examples verified, corrections added where needed
└─> Transitions:
    - P2-D1 checked → [P3]

[x] P3 [VERIFY]: Multimodal + Tools examples (IN12-IN22, 25 examples)
├─ Objectives:
│   └─ [x] All multimodal and tools examples verified ← P3-D1
├─ Strategy: Check Part, Blob, FileData, Tool, FunctionDeclaration types
├─ [x] P3-S1 [VERIFY](IN12-IN15 - 9 examples) OK
├─ [x] P3-S2 [VERIFY](IN16-IN19 - 11 examples) FIXED: IN17+IN19 types.CodeExecution -> types.ToolCodeExecution
├─ [x] P3-S3 [VERIFY](IN20-IN22 - 5 examples) OK
├─ Deliverables:
│   └─ [x] P3-D1: IN12-IN22 examples verified, corrections added where needed
└─> Transitions:
    - P3-D1 checked → [P4]

[x] P4 [VERIFY]: Files/Cache/Embed/Batch + Media Gen examples (IN23-IN31, 22 examples)
├─ Objectives:
│   └─ [x] All file, cache, embed, batch, media gen examples verified ← P4-D1
├─ Strategy: Check Files, Caches, Tokens, Batches, embed_content, ImageConfig
├─ [x] P4-S1 [VERIFY](IN23-IN25 - 7 examples) OK
├─ [x] P4-S2 [VERIFY](IN26-IN28 - 7 examples) FIXED: IN27 BatchGenerateContentRequest->InlinedRequest, IN28 old SDK types (RetrievalSource, Chunk, etc.)
├─ [x] P4-S3 [VERIFY](IN29-IN31 - 8 examples) OK
├─ Deliverables:
│   └─ [x] P4-D1: IN23-IN31 examples verified, corrections added where needed
└─> Transitions:
    - P4-D1 checked → [P5]

[x] P5 [VERIFY]: Live API + Advanced + Platform (IN32-IN41, 21 examples)
├─ Objectives:
│   └─ [x] All Live API, advanced, and platform examples verified ← P5-D1
├─ Strategy: Check LiveConnectConfig, Live session patterns, SDK patterns
├─ [x] P5-S1 [VERIFY](IN32-IN34 - 6 examples) OK
├─ [x] P5-S2 [VERIFY](IN35-IN38 - 10 examples) FIXED: IN38 types.CodeExecution -> types.ToolCodeExecution
├─ [x] P5-S3 [VERIFY](IN39-IN41 - 19 examples) FIXED: IN39 google.api_core + error docs, IN41 CodeExecution
├─ Deliverables:
│   └─ [x] P5-D1: IN32-IN41 examples verified, corrections added where needed
└─> Transitions:
    - P5-D1 checked → [END]

## Document History

**[2026-03-20 07:50]**
- Completed: All 5 phases verified, 10 files fixed
- Systematic issues found and corrected:
  - google.api_core.exceptions (4 files: IN03, IN04, IN08, IN39) - not a dependency of google-genai
  - types.CodeExecution (4 files: IN17, IN19, IN38, IN41) - correct type is types.ToolCodeExecution
  - types.BatchGenerateContentRequest/GenerateContentRequest (IN27) - correct type is types.InlinedRequest
  - Old SDK types: RetrievalSource, GroundingPassage, Chunk, ChunkData, client.corpora (IN28) - use FileSearch + file_search_stores
- SDK verification method: introspected google-genai v1.68.0 types, enums, and method signatures
- Confirmed: FinishReason enum supports string comparison (== "SAFETY" works)
- Confirmed: ThinkingConfig accepts lowercase string values (auto-converts to enum)

**[2026-03-20 07:00]**
- Initial STRUT plan created with 105 examples across 40 files, 5 phases
