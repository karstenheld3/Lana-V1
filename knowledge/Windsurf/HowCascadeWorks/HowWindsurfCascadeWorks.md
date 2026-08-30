# Inside Windsurf Cascade

A technical deep-dive into how Windsurf Cascade works at the protocol level, based on captured wire data from version 2.3.15.

**Windsurf Version**: V2.3.15 (captured 2026-05-29), cross-verified against V2.3.9 (2026-05-28)

## Part I: Overview

- [Introduction and Overview](#introduction-and-overview) - Architecture, request cycle, terminology, behavioral control mechanisms, context lifecycle

## Part II: Deep-Dive Chapters

- [Chapter 1: Multi-Model Architecture and Feature Flags](#chapter-1-multi-model-architecture-and-feature-flags) - 4-model pipeline, 47 feature flags, 135-model registry, agent registry
- [Chapter 2: The Memory System](#chapter-2-the-memory-system) - Cross-session persistence, GPT-5 Nano retrieval, write/read asymmetry, automated memories
- [Chapter 3: The Wire Protocol](#chapter-3-the-wire-protocol) - gRPC over Connect, protobuf serialization, request/response types
- [Chapter 4: The GetChatMessage Request](#chapter-4-the-getchatmessage-request) - String region map, auth envelope, context growth measurements
- [Chapter 5: The Response Stream](#chapter-5-the-response-stream) - gRPC frame structure, text/control/completion frames, per-response model identification, tool result XML format
- [Chapter 6: The System Prompt](#chapter-6-the-system-prompt) - 12 XML sections, identity preamble, user rules override, injected behaviors
- [Chapter 7: The Tool Call Round Trip](#chapter-7-the-tool-call-round-trip) - Conversation turn structure, tool call IDs, extended thinking blocks
- [Chapter 8: Tool Walkthrough - Core Coding Tools](#chapter-8-tool-walkthrough-core-coding-tools) - 12 tools for reading, editing, and executing code
- [Chapter 9: Tool Walkthrough - Platform Tools](#chapter-9-tool-walkthrough-platform-tools) - 15 tools for web, state, interaction, deployment
- [Chapter 10: Tool Walkthrough - MCP-Provided Tools](#chapter-10-tool-walkthrough-mcp-provided-tools) - 25 conditionally-injected Playwright and Playwriter tools
- [Chapter 11: Context Management and Checkpoints](#chapter-11-context-management-and-checkpoints) - Summarizers, truncation, todo list persistence
- [Chapter 12: Context Budget and Practical Guidelines](#chapter-12-context-budget-and-practical-guidelines) - Per-tool costs, cumulative patterns, optimization strategies

## Appendices

- [Appendix A: Open Questions](#appendix-a-open-questions) - Architectural unknowns requiring future captures
- [Appendix B: Source Data and Methodology](#appendix-b-source-data-and-methodology) - Capture paths, extraction tool, session inventory
- [Appendix C: Cross-Reference Table](#appendix-c-cross-reference-table) - Chapter-to-source mapping, Doc ID index

## Source Documents

- `_INFO_HOW_WINDSURF_CASCADE_WORKS.md [CSMP-IN02]` - 70 KB
- `_INFO_HOW_WINDSURF_CASCADE_WORKS_CHECKPOINTS.md [CSMP-IN03]` - 24 KB
- `_INFO_HOW_WINDSURF_CASCADE_WORKS_TODO_LIST.md [CSMP-IN04]` - 27 KB
- `_INFO_WINDSURF_CASCADE_OPEN_QUESTIONS.md [CSMP-IN05]` - 19 KB
- `_INFO_HOW_WINDSURF_CASCADE_TOOL_CALL_ROUND_TRIP.md [CSMP-IN06]` - 15 KB
- `_INFO_HOW_WINDSURF_CASCADE_SYSTEM_PROMPT.md [CSMP-IN07]` - 32 KB
- `_INFO_HOW_WINDSURF_CASCADE_TOOLS_PART_1.md [CSMP-IN08]` - 47 KB
- `_INFO_HOW_WINDSURF_CASCADE_TOOLS_PART_2.md [CSMP-IN09]` - 42 KB
- `_INFO_HOW_WINDSURF_CASCADE_TOOLS_PART_3.md [CSMP-IN10]` - 29 KB
- `_INFO_CASCADE_ADDITIONAL_ANALYSIS_1.md [CSMP-IN11]` - 18 KB


---

# Introduction and Overview

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

How Windsurf Cascade works: protocol, architecture, request/response types, context growth, multi-model pipeline, behavioral control, and practical implications - all from captured wire data.

## 1. What is Windsurf Cascade

Windsurf Cascade is an AI coding agent embedded in the Windsurf IDE (a VS Code fork by Codeium). Unlike simple chat interfaces that generate text responses, Cascade autonomously reads files, searches codebases, edits code, runs terminal commands, deploys applications, and browses the web - all while persisting task state (via todo_list JSON) across checkpoint boundaries.

Cascade is not a single model. It is a multi-model pipeline where different Large Language Models (LLMs) handle different roles: one plans, another generates code, a third summarizes, and a fourth retrieves memories. The IDE orchestrates these models through a gRPC (Google Remote Procedure Call) protocol, assembling context payloads up to 506 KB (observed) and streaming responses back token-by-token.

This ebook documents how Cascade works at the protocol level, based on captured wire data from Windsurf version 1.110.1 (Cascade V2.3.15, post-Wave 14). Everything described here comes from actual network captures, protobuf extraction, and system prompt analysis - not documentation or speculation.

## Key Takeaways

- Cascade is a stateless client-server system where the IDE sends the COMPLETE context with every request (no server-side session, no delta encoding)
- 7 gRPC service methods per turn: rate limit, trajectory, telemetry (pre), GetChatMessage, telemetry (post), execution metadata - plus summarizers on checkpoint path
- Four models handle distinct roles: Brain (GPT-4.1) plans, Generator (Claude Opus 4.6) produces output, Summarizer (Gemini 2.5 Flash) compresses, Memory (GPT-5 Nano) retrieves
- Context grows from ~98 KB to 500+ KB, then checkpoints compress it. Fixed overhead is ~91 KB per request without MCP
- Eight behavioral control mechanisms work in layers, with user rules having explicit highest precedence
- 52 tools give the agent full autonomy over the local development environment
- Post-call telemetry echoes the full context window (~4 MB for a 9-step workflow)
- All findings in this ebook are from captured wire data (V2.3.15), not official documentation

## 2. Protocol Overview

### 2.1 Transport

- **Endpoint**: `server.self-serve.windsurf.com`
- **Protocol**: Connect (Buf's gRPC-compatible protocol over HTTP/2)
- **Serialization**: Protocol Buffers (protobuf)
- **Compression**: gzip (for chat payloads)
- **Content-Type**: `application/connect+proto` for chat, `application/proto` for telemetry

### 2.2 Wire Format

Connect envelope for GetChatMessage:

```text
[1 byte: 0x01 compressed flag] [4 bytes: payload length, big-endian] [gzip-compressed protobuf]
```

Telemetry calls (`RecordCortex*`) use raw protobuf without the 5-byte Connect envelope. Larger telemetry payloads are also gzip-compressed.

For complete protocol details, see [Chapter 3](#chapter-3-the-wire-protocol).

## 3. Architecture

### 3.1 Client-Server System

```text
┌─────────────────────────────────────────────────────────────────┐
│  Windsurf IDE (Electron Client)                                 │
│                                                                 │
│  User types message                                             │
│       │                                                         │
│       v                                                         │
│  IDE assembles GetChatMessage request:                          │
│  ├─ Auth envelope (JSON Web Token, API key, user ID)            │
│  ├─ System prompt (~50 KB)                                      │
│  ├─ Tool definitions (27 native + conditional MCP tools)        │
│  ├─ Memory/checkpoint slot                                      │
│  ├─ User message + IDE metadata                                 │
│  ├─ Full conversation history (grows per turn)                  │
│  └─ Feature flags (47 flags)                                    │
│       │                                                         │
│       v                                                         │
│  gRPC call to server.self-serve.windsurf.com                    │
└─────────────────────────────────────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────────┐
│  Codeium Platform                                               │
│                                                                 │
│  ├─ Brain (GPT-4.1): Plans actions, selects tools               │
│  ├─ Generator (Claude Opus 4.6 Thinking): Produces output       │
│  ├─ Summarizers (Gemini 2.5 Flash x3): Compress context         │
│  └─ Memory (GPT-5 Nano): Retrieves relevant memories            │
│                                                                 │
│  Streaming response: tokens + tool calls                        │
└─────────────────────────────────────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────────┐
│  IDE executes tool calls locally                                │
│  ├─ Reads/edits files on disk                                   │
│  ├─ Runs terminal commands                                      │
│  ├─ Searches codebase                                           │
│  └─ Results sent back in next GetChatMessage                    │
└─────────────────────────────────────────────────────────────────┘
```

Every interaction follows this cycle: the IDE sends the ENTIRE context window (no delta encoding), the platform routes through its model pipeline, and streams back a response that may include tool calls. Tool results are appended to conversation history and sent again in the next request.

### 3.2 Detailed Architecture

Solid lines (─) = proven data flow. Dashed lines (╌) = assumed data flow.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ WINDSURF IDE (Electron)                                                     │
│                                                                             │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────────────────────┐ │
│  │ User Input   │  │ IDE State      │  │ Extension Host                   │ │
│  │              │  │ - active file  │  │ - assembles GetChatMessage       │ │
│  │ - message    │  │ - cursor pos   │  │ - injects system prompt          │ │
│  │ - workflow   │  │ - open files   │  │ - appends conversation history   │ │
│  │ - @mentions  │  │ - git state    │  │ - attaches feature flags + tools │ │
│  └──────┬───────┘  └───────┬────────┘  │ - manages tool call results      │ │
│         │                  │           │ - renders streaming response     │ │
│         └────────┬─────────┘           └──────────────┬───────────────────┘ │
│                  │                                    │                     │
└──────────────────┼────────────────────────────────────┼─────────────────────┘
                   │ metadata                           │ GetChatMessage
                   │ (IDE state, OS, HW)                │ (full context, gzip)
                   └─────────────┬──────────────────────┘
                                 │
                    ═════════════╪══════════════════════════  HTTP/2 + Connect
                                 │                            server.self-serve
                                 v                            .windsurf.com
┌────────────────────────────────────────────────────────────────────────────┐
│ CODEIUM BACKEND                                                            │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Request Router / Planner                                  [ASSUMED] │   │
│  │                                                                     │   │
│  │  Receives GetChatMessage, orchestrates model pipeline:              │   │
│  │                                                                     │   │
│  │  1. Memory retrieval                                                │   │
│  │  2. Brain planning (tool selection, action sequence)                │   │
│  │  3. Generator execution (visible output, streaming)                 │   │
│  │  4. Checkpoint decision (if context > 100K tokens)                  │   │
│  └──┬──────────────┬──────────────┬──────────────┬─────────────────────┘   │
│     │              │              │              │                         │
│     v              v              v              v                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐    │
│  │ MEMORY   │  │ BRAIN    │  │GENERATOR │  │ SUMMARIZER               │    │
│  │          │  │          │  │          │  │                          │    │
│  │ GPT-5    │  │ GPT-4.1  │  │ Claude   │  │ Gemini 2.5 Flash         │    │
│  │ Nano     │  │          │  │ Opus 4.6 │  │                          │    │
│  │          │  │          │  │ Thinking │  │ 3 parallel calls:        │    │
│  ├──────────┤  ├──────────┤  ├──────────┤  │ A: title + objective     │    │
│  │ Concern: │  │ Concern: │  │ Concern: │  │ B: conversation summary  │    │
│  │ Retrieve │  │ Plan     │  │ Generate │  │ C: code interaction log  │    │
│  │ + store  │  │ actions, │  │ visible  │  ├──────────────────────────┤    │
│  │ memories │  │ select   │  │ response │  │ Concern:                 │    │
│  │ across   │  │ tools,   │  │ text,    │  │ Compress conversation    │    │
│  │ sessions │  │ decide   │  │ tool     │  │ into checkpoint when     │    │
│  │          │  │ sequence │  │ calls    │  │ context exceeds 100K     │    │
│  │          │  │          │  │          │  │ token threshold          │    │
│  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────────────────────┤    │
│  │ Evidence:│  │ Evidence:│  │ Evidence:│  │ Evidence:                │    │
│  │ Flag:    │  │ Flag:    │  │ Model in │  │ Separate GetChatMessage  │    │
│  │ MEMORY_  │  │ brain-   │  │ strings  │  │ calls with different     │    │
│  │ CONFIG   │  │ config   │  │ 179-182  │  │ system prompt (400B vs   │    │
│  │ Output at│  │ Filter   │  │ Streams  │  │ 50KB). 3 parallel calls  │    │
│  │ string   │  │ strategy │  │ back to  │  │ per batch. Model name    │    │
│  │ [0065]   │  │ flag     │  │ client   │  │ in feature flags         │    │
│  │ [PROVEN] │  │ [PROVEN] │  │ [PROVEN] │  │ [PROVEN]                 │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────────────┘    │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Platform Services (non-LLM)                               [PROVEN]  │   │
│  │                                                                     │   │
│  │  - Checkpoint assembly: merges 3 summarizer outputs + todo_list     │   │
│  │  - Todo extraction: deterministic parse of last tool output (no LLM)│   │
│  │  - Rate limiting: CheckUserMessageRateLimit                         │   │
│  │  - Telemetry: RecordCortex* endpoints                               │   │
│  │  - Model config: GetCommandModelConfigs                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Separation of Concerns

```text
Concern              Owner                       Runs          Evidence
─────────────────────────────────────────────────────────────────────────
Context assembly     Extension Host (IDE)        Client-side   [PROVEN]
Memory retrieval     GPT-5 Nano                  Server-side   [PROVEN]
Action planning      GPT-4.1 (Brain)             Server-side   [ASSUMED]
Response generation  Claude Opus 4.6 (Generator) Server-side   [PROVEN]
Tool execution       Extension Host (IDE)        Client-side   [PROVEN]
Context compression  Gemini 2.5 Flash + Platform Server-side   [PROVEN]
Todo persistence     Platform (no LLM)           Server-side   [PROVEN]
Telemetry            Platform                    Both sides    [PROVEN]
```

Key architectural observation [ASSUMED]: The Brain and Generator are likely invoked sequentially within a single GetChatMessage server-side pipeline. The client sends one request and receives one streaming response - it has no visibility into whether 1 or 2 models processed the request internally.

## 4. Lifecycle of a Chat Turn

A single user message triggers 7 service methods in sequence:

```text
┌─────────────────────────────────────────────────────────────────────┐
│ User presses Enter                                                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 v
┌─────────────────────────────────────────────────────────────────────┐
│ 1. CheckUserMessageRateLimit   <- rate gate (24 bytes = approved)   │
│ 2. RecordCortexTrajectory      <- open trajectory (conversation ID) │
│ 3. RecordCortexGeneratorMetadata <- pre-call: feature flags         │
└────────────────────────────────┬────────────────────────────────────┘
                                 v
┌─────────────────────────────────────────────────────────────────────┐
│ 4. GetChatMessage              <- MAIN CALL: full context, streamed │
│ 5. [response streams back]     <- tokens as protobuf frames         │
│ 6. RecordCortexGeneratorMetadata <- post-call: full context echo    │
│ 7. RecordCortexExecutionMetadata <- execution + experiment results  │
│                                                                     │
│    If agent calls tools: steps 4-6 repeat per tool-call round trip  │
└──────────────┬──────────────────────────────┬───────────────────────┘
               │                              │
               v                              v
┌──────────────────────────┐   ┌──────────────────────────────────────┐
│ Normal flow:             │   │ Checkpoint path (when context        │
│ Context grows per turn   │   │ exceeds 100K tokens):                │
│ Next user message        │   │                                      │
│ triggers steps 1-7 again │   │ 3 parallel summarizer calls          │
│                          │   │ (Gemini 2.5 Flash, not Generator):   │
│                          │   │ ├─> A: Title + Objective             │
│                          │   │ ├─> B: Full Conversation Summary     │
│                          │   │ └─> C: Code Interaction History      │
│                          │   │                                      │
│                          │   │ Platform extracts latest todo_list   │
│                          │   │ output (deterministic, no LLM)       │
│                          │   │                                      │
│                          │   │ Assembles {{ CHECKPOINT N }} at      │
│                          │   │ string [0065], truncates old history │
│                          │   │                                      │
│                          │   │ Next main call receives checkpoint   │
│                          │   │ instead of full conversation history │
└──────────────────────────┘   └──────────────────────────────────────┘
```

A `/prime` workflow with multiple tool calls produced 9 GetChatMessage calls in 90 seconds. In an 18-minute deep research session, 67 main calls and 5 summarizer batches occurred before 1 checkpoint was applied.

For complete protocol details, see [Chapter 3](#chapter-3-the-wire-protocol).

## 5. Request Types (7 Service Methods)

### 5.1 GetChatMessage (chat)

The primary LLM call. Sends complete context window including system prompt, user rules, tool definitions, conversation history, and user message. Receives streaming response tokens.

- **Frequency**: 1+ per user message (more if tools are called)
- **Size**: 37-506 KB decompressed (grows with conversation; checkpoint may reduce)
- **Content-Type**: `application/connect+proto` (5-byte envelope + gzip)
- **Structure**: See [section 7](#7-getchatmessage-request-structure) and [Chapter 4](#chapter-4-the-getchatmessage-request)

### 5.2 RecordCortexGeneratorMetadata (telemetry)

Sent at start and after each GetChatMessage completion. Pre-call contains compact config; post-call echoes the FULL context window as telemetry.

- **Frequency**: 1 pre-call per user message + 1 post-call per GetChatMessage completion
- **Size**: 9 KB (pre-call, compact flags only) to 1177 KB (post-call, full context echo)
- **Content-Type**: `application/proto` (raw protobuf, gzip for large payloads)
- **Contains**: Session tokens, OS/hardware JSON, user ID, API key JWT, feature flags. Post-call adds: full system prompt, user rules, conversation history, tool definitions

### 5.3 CheckUserMessageRateLimit (gate)

Rate limit check before each user message. Contains auth envelope plus model name.

- **Frequency**: 1 per user message
- **Size**: 3 KB request, 24 bytes response (empty = approved)
- **Notable**: Response contains no extractable strings (just protobuf field markers)

### 5.4 RecordCortexTrajectory (lifecycle)

Marks the start and end of a trajectory (conversation turn).

- **Frequency**: 1-2 per user message
- **Size**: 3.5 KB
- **Contains**: Auth envelope + workspace extension path + git repo URL + git commit hash + conversation/trajectory UUIDs

### 5.5 RecordStateInitializationData (sync)

Sends IDE state to the backend.

- **Frequency**: 1 per conversation turn
- **Size**: 3.5 KB
- **Contains**: Auth envelope + workspace extension path + git repo URL + git commit hash

### 5.6 RecordCortexExecutionMetadata (telemetry)

Post-execution telemetry with feature flag experiment outcomes.

- **Frequency**: 1 per execution batch
- **Size**: 16 KB
- **Contains**: Auth envelope + feature flags + experiment results (A/B test outcomes)

### 5.7 GetCommandModelConfigs (config)

Retrieves available model configurations at session startup.

- **Frequency**: 1 per session
- **Size**: 494 bytes response
- **Contains**: Model name strings: `MODEL_CLAUDE_4_5_OPUS`, `MODEL_SWE_1_5` ("Windsurf Fast"), `MODEL_CHAT_GPT_4_1_2025_04_14`, `MODEL_CLAUDE_4_SONNET`

## 6. Response Types

### 6.1 GetChatMessage Response

Streaming protobuf containing model output tokens. Responses are raw protobuf (no Connect envelope), delivered as HTTP/2 data frames.

- **Size**: 2-29 KB per response
- **String extraction**: 0 extractable strings at 20-char minimum threshold. Tokens are split across small protobuf string fields (individual words/fragments), each below the extraction threshold
- **Implication**: Response content requires proper protobuf deserialization or a lower string length threshold

### 6.2 CheckUserMessageRateLimit Response

24-byte protobuf with no extractable strings. Likely contains a boolean "allowed" field and remaining quota [ASSUMED].

### 6.3 GetCommandModelConfigs Response

494-byte protobuf listing 4 model identifiers (see section 5.7).

## 7. GetChatMessage Request Structure

The request is a single protobuf message containing ~182 string fields (at 20-char extraction threshold). The structure divides into distinct regions:

### 7.1 String Region Map

```text
[0001-0008]  Auth envelope (session JWT, OS, CPU, user ID, API key, hash, signature, team ID)
[0009-0064]  System prompt (fixed, ~50 KB)
[0065]       Memory/checkpoint slot (memories or checkpoint summary)
[0066]       User message (with additional_metadata, user_request, workflows)
[0067-N]     Conversation history (grows per turn)
[N+1-N+56]   Feature flags (47 flags, fixed)
[N+57-end]   Tool definitions (27 tools, JSON schemas) + trailing metadata
```

### 7.2 Proportional Layout

Approximate decompressed sizes per region (first call, ~99 KB total):

```text
┌──────────────────────────────────────────────────────────────────┐
│ [0001-0008] Auth Envelope                              ~2 KB  2% │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                                                                  │
│ [0009-0064] System Prompt                             ~50 KB 51% │
│   ├─ Windsurf behavioral sections                  ~10 KB        │
│   ├─ User rules (<user_rules>)                     ~33 KB        │
│   └─ Workflows + user info + misc                   ~7 KB        │
│                                                                  │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ [0065]      Memory / Checkpoint Slot                ~0.1 KB  0%  │
├──────────────────────────────────────────────────────────────────┤
│ [0066]      User Message + IDE Metadata            ~4-11 KB  7%  │
├──────────────────────────────────────────────────────────────────┤
│ [0067-N]    Conversation History                   0-415 KB      │
│             (absent on first call; grows per turn)  variable     │
├──────────────────────────────────────────────────────────────────┤
│ [N+1-N+56]  Feature Flags (47 flags)                  ~4 KB   4% │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [N+57-end]  Tool Definitions                         ~35 KB  36% │
│   ├─ 27 native tools (always present)                ~35 KB      │
│   └─ 25 MCP tools (conditional)                  +~25-28 KB      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

System prompt (51%) and tool definitions (36%) together consume 87% of the first request.

### 7.3 Auth Envelope (strings 1-8)

Every request starts with the same authentication block:

```text
[0001] Session JWT                        devin-session-token$eyJ...
[0002] OS metadata JSON                   {"Os":"windows","Arch":"amd64",...}
[0003] Hardware metadata JSON             {"NumSockets":1,"NumCores":16,...}
[0004] User ID                            user-daaedcb8...
[0005] API key JWT (JSON Web Token)       eyJ... (contains email, team config, plan tier)
[0006] Content hash                       @0acc3c5f... (SHA-256)
[0007] Signature token                    9e0f7fd0... (384 hex chars)
[0008] Team ID                            devin-team$account-...
```

The API key JWT decodes to reveal: email, team_config (JSON with feature permissions like `allowMcpServers`, `allowAutoRunCommands`, `maxCascadeAutoExecutionLevel`), team tier (`TEAMS_TIER_DEVIN_MAX`), and plan type.

### 7.4 System Prompt (strings 9-64)

The system prompt string (~50 KB) contains 12 XML-tagged sections plus identity text and injected behaviors:

```text
You are Cascade, a powerful agentic AI coding assistant.
{identity paragraph - pair programmer role, workspace awareness}

<communication_style>                    <- wraps 3 sub-sections:
  <communication_guidelines>             <- 14 behavioral rules
  <markdown_formatting>                  <- 8 formatting rules
  <citation_guidelines>                  <- citation format with examples
</communication_style>

<tool_calling>                           <- parallel batching, dependencies
<making_code_changes>                    <- minimal edits, runnable code, max 300 lines
<task_management>                        <- todo_list usage
<running_commands>                       <- safety rules, no cd, SafeToAutoRun
<debugging>                              <- root cause, logging, test isolation
<calling_external_apis>                  <- version compatibility, API key security

<workflows>                              <- 38 workflow names + descriptions (~4 KB)
<user_rules>                             <- "MUST ALWAYS FOLLOW" + MEMORY blocks (~33 KB)
<user_information>                       <- OS, workspace URIs, corpus names
<workspace_information>                  <- file tree (frozen at conversation start)
<memory_system>                          <- 3 memory types, staleness warning
<ide_metadata>                           <- IDE state description
<mcp_servers>                            <- CONDITIONAL: only when MCP servers configured

{Injected Behaviors}                     <- 6 rules after closing tags (outside XML)
```

For full system prompt analysis, see [Chapter 6](#chapter-6-the-system-prompt).

### 7.5 User Rules (inside system prompt)

User rules from `.windsurf/rules/*.md` are injected as MEMORY blocks:

```text
<user_rules>
The following are user-defined rules that you MUST ALWAYS FOLLOW...

<MEMORY[agent-behavior.md]>
  {content of .windsurf/rules/agent-behavior.md}
</MEMORY[agent-behavior.md]>

<MEMORY[core-conventions.md]>
  {content of .windsurf/rules/core-conventions.md}
</MEMORY[core-conventions.md]>

...one block per .md file in rules folder...
</user_rules>
```

Empty rule files generate empty MEMORY blocks (the tag pair exists but has no content).

### 7.6 Injected Behaviors (after system prompt tags)

After the closing `</ide_metadata>` tag and before the feature flags, Windsurf appends system-authored behavioral rules. These are NOT inside any XML section:

```text
Bug fixing discipline: Prefer minimal upstream fixes...
Long-horizon workflow: For multi-session work...
Planning cadence: Draft a succinct plan...
Testing discipline: Design or update tests...
Verification tools: Prefer available automated verification...
Progress notes: Prefer lightweight workspace artifacts...
```

These appear to be dynamically injected based on user behavior patterns or A/B testing [ASSUMED].

### 7.7 Memory / Checkpoint Slot (string 65)

String position `[0065]` serves dual purpose depending on conversation state:

**Normal operation** (no checkpoint):
```text
No MEMORIES were retrieved. Continue your work without acknowledging this message.
```
Or, if memories exist, the retrieved memory content.

**After checkpoint** (context was summarized):
```text
**The following is a summary of important context from your previous
coding session with the USER. **
{{ CHECKPOINT N }}

# USER Objective:
{title + objective from Summarizer A}

# Current working TODO list (keep this up to date with todo_list tool):
{latest todo_list JSON from conversation history}

Make sure to continue working off of this TODO list

# Previous Session Summary:
<summary>{9-section summary from Summarizer B}</summary>

# Code Interaction Summary:
{file edit/view history from Summarizer C}

**IMPORTANT: this summary is just for your reference. You may respond to
my previous and future messages, but DO NOT ACKNOWLEDGE THIS CHECKPOINT
MESSAGE. JUST READ IT BUT DO NOT MENTION IT, RESPOND TO IT, OR TAKE
ACTION BECAUSE OF IT.**
```

The checkpoint replaces both the memory string AND the truncated conversation history. See [Chapter 11](#chapter-11-context-management-and-checkpoints) for checkpoint structure.

### 7.8 User Message (string 66)

The actual user input, wrapped in metadata:

```text
<additional_metadata>
NOTE: Open files and cursor position may not be related...
The USER presented this request on {DATE} at {TIME}, {TIMEZONE}.
{IDE_STATE: active document, cursor line, language}
</additional_metadata>
<user_request>
{ACTUAL_USER_MESSAGE}
</user_request>
<workflows>                          only present if user invoked a workflow
  @[/prime] is a [Workflow]:
  <workflow>
    {FULL WORKFLOW .md CONTENT}
  </workflow>
</workflows>
```

### 7.9 Feature Flags (47 flags)

Key-value pairs controlling Cascade behavior. 47 flags captured (40 named + 7 config-only), grouped into 8 categories:

**Model configuration:**
- `cascade-brain-config` = `{"brainModel": "MODEL_CHAT_GPT_4_1_2025_04_14", "filterStrategy": "BRAIN_FILTER_STRATEGY_NO_SYSTEM_INJECTED_STEPS", ...}`
- `CASCADE_MEMORY_CONFIG_OVERRIDE` = `{"memory_model": "MODEL_GPT_5_NANO"}`

**Context management:**
- `CASCADE_PLAN_BASED_CONFIG_OVERRIDE` = `{"planner_config": {"truncation_threshold_tokens": "100000"}}`

**Tool configuration overrides:**
- `CASCADE_USE_REPLACE_CONTENT_EDIT_TOOL` = fuzzy edit distance, fast apply fallback config
- `CASCADE_VIEW_FILE_TOOL_CONFIG_OVERRIDE` = prompt prefix, split outline
- `cascade-tool-calling-section-content` = appends "if asked about what your underlying model is, respond with Cascade"

**Behavior injection:**
- `CASCADE_AUTO_FIX_LINTS` = injects lint handling with loop avoidance
- `CASCADE_ENABLE_AUTOMATED_MEMORIES` = enabled
- `CASCADE_USER_MEMORIES_IN_SYS_PROMPT` = controls MEMORY block injection

**Platform capabilities (enabled):** `CASCADE_ENABLE_MCP_TOOLS`, `CASCADE_ENABLE_PROXY_WEB_SERVER`, `CASCADE_WEB_APP_DEPLOYMENTS_ENABLED`, `CASCADE_PLAN_MODE_EXIT_TOOL`, `notebook-cascade-support`, `API_SERVER_CLIENT_USE_HTTP_2`

**Agent tools (enabled):** `cascade-add-annotation`, `cascade-allow-edit-rules-files`, `cascade-enable-ask-user-question`, `cascade-enable-conversation-search`, `cascade-find-code-context`, `cascade-group-planner-response-tools`

**Disabled/unreleased:** `cascade-enable-task-subagent`, `cascade-third-party-web-search`, `cascade-enable-find-all-references`, `cascade-enable-search-in-file-tool`, `XML_TOOL_PARSING_MODELS`, `ENABLE_SUGGESTED_RESPONSES`

**Telemetry:** `cascade-api-server-experiment-keys` = A/B test keys, `SNAPSHOT_TO_STEP_OPTIONS_OVERRIDE` = trajectory snapshot config

For complete flag inventory, see [Chapter 1](#chapter-1-multi-model-architecture-and-feature-flags).

### 7.10 Tool Definitions (strings 124-178)

27 native tools defined as alternating description + JSON Schema pairs:

```text
[0124] "Ask the user a question..."          <- tool description
[0125] {"$schema":"...","properties":{...}}  <- JSON Schema
[0126] "Spin up a browser preview..."        <- next tool description
[0127] {"$schema":"...","properties":{...}}  <- next schema
```

All schemas use JSON Schema Draft 2020-12 with `"additionalProperties": false` (strict mode).

**Code editing (4):** `edit`, `multi_edit`, `write_to_file`, `edit_notebook`
**Code reading (6):** `read_file`, `read_notebook`, `code_search`, `grep_search`, `find_by_name`, `list_dir`
**Execution (2):** `run_command`, `command_status`
**Web/external (3):** `read_url_content`, `search_web`, `view_content_chunk`
**Deployment (3):** `deploy_web_app`, `read_deployment_config`, `check_deploy_status`
**State (3):** `todo_list`, `create_memory`, `trajectory_search`
**Interaction (1):** `ask_user_question`
**Workflow (1):** `skill`
**Browser (1):** `browser_preview`
**MCP meta (2):** `list_resources`, `read_resource`
**Terminal (1):** `read_terminal`

MCP tools (Playwright, Playwriter) are defined separately via the MCP protocol and injected conditionally with `mcp1_` or `mcp2_` prefixes. For full tool details, see [Chapter 8](#chapter-8-tool-walkthrough-core-coding-tools), [Chapter 9](#chapter-9-tool-walkthrough-platform-tools), and [Chapter 10](#chapter-10-tool-walkthrough-mcp-provided-tools).

### 7.11 Model Config (strings 179-182)

```text
[0179] {protobuf framing byte}
[0180] Conversation UUID                     $cdb22d48-b079-...
[0181] Model name                            claude-opus-4-6-thinking
[0182] Trajectory UUID                       $f15ad9fb-d3fe-...
```

### 7.12 Summarizer System Prompt

Summarizer calls use a completely different system prompt (~400 bytes vs ~50 KB):

```text
You are an expert AI coding assistant with extreme attention to detail.
You are pair programming with a USER to solve a coding task. You provide
clear, detailed, and accurate summaries of conversations. When asked, you
focus on outlining the USER's main goals and listing key information and
context discussed. Your response should be well-organized and reflect the
essence of the dialog. NEVER lie or make things up. Your summaries should
always be grounded in the conversation.
```

Shared by all 3 summarizers. No user rules, no tool definitions, no feature flags. The summarizer-specific instruction (ENTER ANALYSIS MODE, ENTER SUMMARY MODE, ENTER HISTORY GENERATION MODE) is injected as the final user message, not as part of the system prompt. For full checkpoint details, see [Chapter 11](#chapter-11-context-management-and-checkpoints).

## 8. Context Growth

Every GetChatMessage re-sends the complete context. Conversation history accumulates with each step.

### 8.1 Short Session (9 calls, /prime workflow, 90 seconds)

- **First call** (0193): 182 strings, 37 KB compressed, 102 KB decompressed
- **After tool calls** (0242): 62 KB compressed, 178 KB decompressed
- **Full context** (0276): 2167 strings, 93 KB compressed, 267 KB decompressed

No checkpoint triggered (context stayed below 100K token threshold).

### 8.2 Long Session (67 calls, deep research, 18 minutes)

```text
Request   Context    Delta    Event
0110       98 KB      -       First call (system prompt + user message)
0154      131 KB    +33 KB    Agent response + tool results
0331      210 KB   +112 KB    Multiple tool call rounds
0527      301 KB    +91 KB    Web search results accumulated
0885      467 KB   +166 KB    Large file write outputs
0929      499 KB    +32 KB    Last pre-checkpoint call
                    ─────
0950      388 KB   -111 KB    {{ CHECKPOINT 1 }} applied
                    ─────
1221      506 KB   +118 KB    Session end (context grew back)
```

Checkpoint reduced context by 111 KB (499 KB to 388 KB). Context grew back to 506 KB by session end without triggering a second checkpoint.

### 8.3 Fixed Overhead (~91 KB, constant across all calls)

- System prompt: ~10 KB (Windsurf behavioral sections)
- User rules: ~33 KB (6 MEMORY blocks)
- Tool definitions (27 tools): ~35 KB
- Feature flags: ~4 KB
- Workflow list: ~4 KB
- Auth envelope + user info + workspace layout + memory system: ~5 KB

### 8.4 Variable Content (grows per step)

- First call: ~11 KB (user message + workflow expansion)
- Full context: ~176-415 KB (accumulated tool call results, assistant responses, intermediate steps)

### 8.5 Compression

- Ratio: ~2.5:1 for first call, ~2.9:1 for full context (gzip compresses repeated prompt text efficiently)
- All sizes in this ebook are decompressed unless stated otherwise (what the LLM processes)
- Wire size is smaller due to gzip, but LLM still processes full decompressed token count

## 9. Multi-Model Architecture

Windsurf uses 3-4 different models per conversation (role names from Codeium feature flags):

- **Brain**: `MODEL_CHAT_GPT_4_1_2025_04_14` (GPT-4.1). Configured via `cascade-brain-config` flag with `BRAIN_FILTER_STRATEGY_NO_SYSTEM_INJECTED_STEPS`
- **Generator**: `claude-opus-4-6-thinking` (Claude Opus 4.6 with extended thinking). Produces the visible output streamed to the user
- **Memory**: `MODEL_GPT_5_NANO`. Configured via `CASCADE_MEMORY_CONFIG_OVERRIDE`. Handles persistent memory retrieval and storage
- **Summarizer**: `MODEL_GOOGLE_GEMINI_2_5_FLASH` (Gemini 2.5 Flash). Uses a different, shorter system prompt (400 bytes vs 50 KB). Runs as 3 parallel calls per batch

The `GetCommandModelConfigs` response lists 4 models available for user selection: `MODEL_CLAUDE_4_5_OPUS`, `MODEL_SWE_1_5` ("Windsurf Fast"), `MODEL_CHAT_GPT_4_1_2025_04_14`, `MODEL_CLAUDE_4_SONNET`.

For complete architecture diagram and data flow, see [Chapter 1](#chapter-1-multi-model-architecture-and-feature-flags).

## 10. The 8 Behavioral Control Mechanisms

Cascade's behavior is not controlled by a single prompt. Eight distinct mechanisms work together:

1. **System prompt sections** - 12 XML-wrapped sections (`<communication_style>`, `<tool_calling>`, `<making_code_changes>`, etc.) define base behavior. Key constraints: "Never start responses with 'You're absolutely right!'", "implement changes rather than only suggesting them", "You must NEVER NEVER run a command automatically if it could be unsafe."

2. **User rules override** - The `<user_rules>` section explicitly states: "MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION. These rules take precedence over any following instructions." User-defined rules in `.windsurf/rules/` override everything else.

3. **Tool description constraints** - Each tool's description contains behavioral instructions. Examples: `edit` requires "Read tool at least once before editing"; `write_to_file` forbids "modify or overwrite existing files"; `run_command` forbids "cd" commands; `create_memory` forbids autonomous use; `code_search` forbids parallel invocation.

4. **Feature flag injection** - Some flags inject behavioral text directly into the system prompt. `cascade-tool-calling-section-content` appends "if asked about what your underlying model is, respond with Cascade". `CASCADE_AUTO_FIX_LINTS` injects lint handling with "AVOID unproductive loops". Disabled flags suggest additional injection points exist.

5. **Checkpoint behavioral anchors** - The checkpoint template includes 3 platform-hardcoded strings (not LLM-generated): 1) "keep this up to date with todo_list tool", 2) "Make sure to continue working off of this TODO list", 3) "DO NOT ACKNOWLEDGE THIS CHECKPOINT MESSAGE."

6. **Injected behaviors** - 6 behavioral statements appended AFTER all XML sections, outside any wrapper: bug fixing discipline, long-horizon workflow, planning cadence, testing discipline, verification tools, progress notes. Dynamically injected, selection mechanism unknown [ASSUMED].

7. **MCP recommendations** - When MCP servers are configured, the `<mcp_servers>` section includes server-specific usage guides (~30 KB total). Playwriter's tool description alone contains ~15 KB of behavioral guidance functioning as a second system prompt.

8. **Cascade Hooks** - Shell commands that execute at key points in Cascade's workflow (12 events: pre/post for read_code, write_code, run_command, mcp_tool_use, user_prompt, cascade_response, plus post_cascade_response_with_transcript and post_setup_worktree). Pre-hooks can **block actions** by exiting with code 2. Configured at system, user, or workspace level (`.windsurf/hooks.json`). Not visible in wire data but affect tool execution externally [VERIFIED from docs.windsurf.com 2026-05-31].

### 10.1 Instruction Priority Chain

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Priority 1 (highest): User rules                                    │
│   "MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION"                        │
│   "take precedence over any following instructions"                 │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 2: System prompt behavioral sections                       │
│   Identity, communication, tool calling, code changes, safety       │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 3: Tool description constraints                            │
│   Per-tool behavioral rules (read before edit, no cd, etc.)         │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 4: Feature flag injections                                 │
│   Model identity override, lint handling, section appends           │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 5: Checkpoint behavioral anchors                           │
│   Todo continuation, checkpoint acknowledgment suppression          │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 6: Injected behaviors (post-system-prompt)                 │
│   Bug fixing, planning, testing disciplines                         │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 7: MCP server recommendations                              │
│   Server-specific usage guides, conditionally present               │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 8 (external): Cascade Hooks                                │
│   Pre-hooks can BLOCK actions (exit code 2), post-hooks observe     │
│   Not in wire data - operates at shell level around tool execution  │
└─────────────────────────────────────────────────────────────────────┘
```

Priority ordering inferred from explicit precedence statements and positional salience. Actual model attention-weighted priority may differ [ASSUMED].

## 11. Practical Implications

**Privacy**: Every request sends email (in JWT), git repo URL, git commit hash, OS version, hardware specs (CPU model, core count, RAM), and workspace file tree. Post-call telemetry (RecordCortexGeneratorMetadata) echoes the full conversation content (100-1177 KB).

**Context budget**: ~91 KB of every GetChatMessage is fixed overhead. User rules (~33 KB) are the largest user-controllable component. Reducing rule file sizes directly increases available conversation context.

**Tool call cost**: Each tool-call round trip re-sends the full ~91 KB fixed overhead plus all accumulated conversation history. A 9-step /prime workflow sends the system prompt 9 times. Batching independent tool calls (when the agent supports it) reduces total context consumption.

**Telemetry volume**: RecordCortexGeneratorMetadata post-call echoes the full context window. For the /prime workflow observed, this produced ~4 MB of telemetry across 5 post-call reports.

**Compression**: gzip reduces wire size by 2.5-3x, but the LLM still processes the full decompressed token count.

## 12. Key Terminology

- **GetChatMessage** - The primary gRPC method. Sends full context, receives streaming tokens. Every agent turn is one GetChatMessage call.
- **Context window** - The total content sent in a GetChatMessage request: system prompt + conversation history + tool definitions + feature flags. Grows per turn.
- **System prompt** - The ~50 KB instruction set that defines Cascade's identity, capabilities, and behavioral rules. Sent with every request.
- **Tool** - A structured capability the agent can invoke (read files, edit code, run commands). 52 tools total: 27 native + 25 from MCP servers.
- **Tool call** - A structured request from the agent to execute a tool. Contains a tool name, arguments (JSON), and a unique ID (`toolu_*` format).
- **Checkpoint** - A compressed summary that replaces truncated conversation history when context exceeds ~100K tokens. Produced by 3 parallel summarizer calls + deterministic todo extraction.
- **Platform** - The Codeium server-side infrastructure that routes requests through models. Not an LLM itself - it orchestrates LLMs.
- **Wire data** - Raw protobuf content captured from the gRPC connection between IDE and platform.
- **Feature flag** - A configuration value sent with every request that controls model selection, tool behavior, A/B testing, and capability gating. 40 captured.
- **MCP** (Model Context Protocol) - A standard for connecting AI systems with external tools. Windsurf uses it to inject Playwright and Playwriter browser automation tools.
- **Brain** - GPT-4.1, plans actions and selects tools. Evidence: `cascade-brain-config` flag.
- **Generator** - Claude Opus 4.6 Thinking, produces visible output. Evidence: model name in strings 179-182.
- **Summarizer** - Gemini 2.5 Flash, compresses context into checkpoints. Evidence: separate GetChatMessage calls with 400-byte system prompt.
- **Connect protocol** - Buf's gRPC-compatible protocol over HTTP/2. Uses 5-byte envelope prefix.

## 13. Ebook Road Map

- **Part 1** (this chapter): Standalone overview of the complete system
- **Part 2, Chapter 1**: [Multi-Model Architecture](#chapter-1-multi-model-architecture-and-feature-flags) - 4-model pipeline, 47 feature flags, 135-model registry, instruction following
- **Part 2, Chapter 2**: [The Memory System](#chapter-2-the-memory-system) - Cross-session persistence, GPT-5 Nano retrieval, write/read asymmetry
- **Part 2, Chapter 3**: [Wire Protocol](#chapter-3-the-wire-protocol) - Transport, serialization, compression, 7 service methods
- **Part 2, Chapter 4**: [GetChatMessage Request](#chapter-4-the-getchatmessage-request) - String region map, auth, system prompt region, feature flags, tool definitions
- **Part 2, Chapter 5**: [The Response Stream](#chapter-5-the-response-stream) - gRPC frame types, per-response model ID, tool result XML format
- **Part 2, Chapter 6**: [System Prompt](#chapter-6-the-system-prompt) - All 12 XML sections, identity, user rules, injected behaviors, size budget
- **Part 2, Chapter 7**: [Tool Call Round Trip](#chapter-7-the-tool-call-round-trip) - Wire encoding, ID format, thinking blobs, context growth per turn
- **Part 2, Chapter 8**: [Core Coding Tools](#chapter-8-tool-walkthrough-core-coding-tools) - 12 tools: reading, editing, execution with exact schemas
- **Part 2, Chapter 9**: [Platform Tools](#chapter-9-tool-walkthrough-platform-tools) - 15 tools: web, state, deployment, interaction
- **Part 2, Chapter 10**: [MCP Tools](#chapter-10-tool-walkthrough-mcp-provided-tools) - 25 conditionally-injected browser automation tools
- **Part 2, Chapter 11**: [Context Management](#chapter-11-context-management-and-checkpoints) - Checkpoints, todo persistence, what survives vs lost
- **Part 2, Chapter 12**: [Context Budget](#chapter-12-context-budget-and-practical-guidelines) - Cost tiers for all 52 tools, efficient patterns

## Sources

- All 9 source documents (CSMP-IN02 through CSMP-IN10) contributed to this synthesis
- See [Appendix C](#appendix-c-cross-reference-table) for detailed chapter-to-source mapping


---

# Chapter 1: Multi-Model Architecture and Feature Flags

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents the multi-model pipeline, the 47 feature flags controlling behavior, and the 8 instruction-following mechanisms Windsurf uses to steer the agent. The reader should understand the request structure from [Chapter 4](#chapter-4-the-getchatmessage-request).

## 1. The 4-Model Pipeline

Windsurf uses 3-4 different models per conversation (role names from Codeium feature flags):

- **Brain**: `MODEL_CHAT_GPT_4_1_2025_04_14` (GPT-4.1). Configured via `cascade-brain-config` flag with `BRAIN_FILTER_STRATEGY_NO_SYSTEM_INJECTED_STEPS`
- **Generator**: `claude-opus-4-6-thinking` (Claude Opus 4.6 with extended thinking). Produces the visible output streamed to the user
- **Memory**: `MODEL_GPT_5_NANO`. Configured via `CASCADE_MEMORY_CONFIG_OVERRIDE`. Handles persistent memory retrieval and storage
- **Summarizer**: `MODEL_GOOGLE_GEMINI_2_5_FLASH` (Gemini 2.5 Flash) + `MODEL_CHAT_GPT_4_1_MINI_2025_04_14` (GPT-4.1 Mini). Uses a different, shorter system prompt (400 bytes vs 50 KB). Runs as 3 parallel calls per batch. Response stream F7.9 confirms both models handle summarization/auxiliary tasks [PROVEN]

The `GetCommandModelConfigs` response lists 4 models available for user selection: `MODEL_CLAUDE_4_5_OPUS`, `MODEL_SWE_1_5` ("Windsurf Fast"), `MODEL_CHAT_GPT_4_1_2025_04_14`, `MODEL_CLAUDE_4_SONNET`.

## 2. Architecture Diagram

Solid lines = proven data flow. Dashed lines = assumed data flow.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ WINDSURF IDE (Electron)                                                     │
│                                                                             │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────────────────────┐ │
│  │ User Input   │  │ IDE State      │  │ Extension Host                   │ │
│  │              │  │ - active file  │  │ - assembles GetChatMessage       │ │
│  │ - message    │  │ - cursor pos   │  │ - injects system prompt          │ │
│  │ - workflow   │  │ - open files   │  │ - appends conversation history   │ │
│  │ - @mentions  │  │ - git state    │  │ - attaches feature flags + tools │ │
│  └──────┬───────┘  └───────┬────────┘  │ - manages tool call results      │ │
│         │                  │           │ - renders streaming response     │ │
│         └────────┬─────────┘           └──────────────┬───────────────────┘ │
│                  │                                    │                     │
└──────────────────┼────────────────────────────────────┼─────────────────────┘
                   │ metadata                           │ GetChatMessage
                   │ (IDE state, OS, HW)                │ (full context, gzip)
                   └─────────────┬──────────────────────┘
                                 │
                    ═════════════╪══════════════════════════  HTTP/2 + Connect
                                 │                            server.self-serve
                                 v                            .windsurf.com
┌────────────────────────────────────────────────────────────────────────────┐
│ CODEIUM PLATFORM                                                           │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Request Router / Planner                                  [ASSUMED] │   │
│  │                                                                     │   │
│  │  Receives GetChatMessage, orchestrates model pipeline:              │   │
│  │                                                                     │   │
│  │  1. Memory retrieval                                                │   │
│  │  2. Brain planning (tool selection, action sequence)                │   │
│  │  3. Generator execution (visible output, streaming)                 │   │
│  │  4. Checkpoint decision (if context > 100K tokens)                  │   │
│  └──┬──────────────┬──────────────┬──────────────┬─────────────────────┘   │
│     │              │              │              │                         │
│     v              v              v              v                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐    │
│  │ MEMORY   │  │ BRAIN    │  │GENERATOR │  │ SUMMARIZER               │    │
│  │          │  │          │  │          │  │                          │    │
│  │ GPT-5    │  │ GPT-4.1  │  │ Claude   │  │ Gemini 2.5 Flash         │    │
│  │ Nano     │  │          │  │ Opus 4.6 │  │                          │    │
│  │          │  │          │  │ Thinking │  │ 3 parallel calls:        │    │
│  ├──────────┤  ├──────────┤  ├──────────┤  │ A: title + objective     │    │
│  │ Concern: │  │ Concern: │  │ Concern: │  │ B: conversation summary  │    │
│  │ Retrieve │  │ Plan     │  │ Generate │  │ C: code interaction log  │    │
│  │ + store  │  │ actions, │  │ visible  │  ├──────────────────────────┤    │
│  │ memories │  │ select   │  │ response │  │ Concern:                 │    │
│  │ across   │  │ tools,   │  │ text,    │  │ Compress conversation    │    │
│  │ sessions │  │ decide   │  │ tool     │  │ into checkpoint when     │    │
│  │          │  │ sequence │  │ calls    │  │ context exceeds 100K     │    │
│  │          │  │          │  │          │  │ token threshold          │    │
│  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────────────────────┤    │
│  │ Evidence:│  │ Evidence:│  │ Evidence:│  │ Evidence:                │    │
│  │ Flag:    │  │ Flag:    │  │ Model in │  │ Separate GetChatMessage  │    │
│  │ MEMORY_  │  │ brain-   │  │ strings  │  │ calls with different     │    │
│  │ CONFIG   │  │ config   │  │ 179-182  │  │ system prompt (400B vs   │    │
│  │ Output at│  │ Filter   │  │ Streams  │  │ 50KB). 3 parallel calls  │    │
│  │ string   │  │ strategy │  │ back to  │  │ per batch. Model name    │    │
│  │ [0065]   │  │ flag     │  │ client   │  │ in feature flags         │    │
│  │ [PROVEN] │  │ [PROVEN] │  │ [PROVEN] │  │ [PROVEN]                 │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────────────┘    │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Platform Services (non-LLM)                               [PROVEN]  │   │
│  │                                                                     │   │
│  │  - Checkpoint assembly: merges 3 summarizer outputs + todo_list     │   │
│  │  - Todo extraction: deterministic parse of last tool output (no LLM)│   │
│  │  - Rate limiting: CheckUserMessageRateLimit                         │   │
│  │  - Telemetry: RecordCortex* endpoints                               │   │
│  │  - Model config: GetCommandModelConfigs                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

## 3. Data Flow Per Turn

### 3.1 Normal Turn (no checkpoint)

```text
IDE                          Platform
 │                               │
 │── CheckUserMessageRateLimit ─>│ rate gate
 │<─ 24B approved ───────────────│
 │                               │
 │── RecordCortexTrajectory ────>│ open trajectory
 │── RecordCortexGenMetadata ───>│ pre-call (flags)
 │                               │
 │── GetChatMessage ────────────>│
 │   (full context, 98-506 KB)   │
 │                               │╌╌ Memory(GPT-5 Nano) ╌╌> [0065]
 │                               │╌╌ Brain(GPT-4.1) ╌╌╌╌╌> tool plan
 │                               │── Generator(Claude) ──> streaming
 │<─ streaming tokens ───────────│
 │                               │
 │── RecordCortexGenMetadata ───>│ post-call (full echo)
 │── RecordCortexExecMetadata ──>│ experiment results
 │                               │
 │   If tool calls requested:    │
 │   IDE executes tools locally  │
 │── GetChatMessage ────────────>│ (with tool results appended)
 │   ... repeat ...              │
```

### 3.2 Checkpoint Turn (context > 100K tokens)

```text
IDE                          Platform
 │                               │
 │   (same as normal turn until context exceeds threshold)
 │                               │
 │                               │── Summarizer A ──> title + objective
 │                               │── Summarizer B ──> full summary
 │                               │── Summarizer C ──> code history
 │                               │   (3 parallel Gemini 2.5 Flash calls)
 │                               │
 │                               │── Platform: extract latest todo_list
 │                               │   (deterministic, no LLM)
 │                               │
 │                               │── Platform: assemble checkpoint
 │                               │   template from A + B + C + todos
 │                               │
 │   Next GetChatMessage:        │
 │   - string [0065] = checkpoint (replaces memories)
 │   - conversation history truncated (old turns removed)
 │   - context drops ~111 KB
```

## 4. Separation of Concerns

- **Context assembly** - Owner: Extension Host (IDE), Client-side [PROVEN]
- **Memory retrieval** - Owner: GPT-5 Nano, Server-side [PROVEN] - output at string [0065]
- **Action planning** - Owner: GPT-4.1 (Brain), Server-side [ASSUMED] - flag config only
- **Response generation** - Owner: Claude Opus 4.6 Thinking (Generator), Server-side [PROVEN]
- **Tool execution** - Owner: Extension Host (IDE), Client-side [PROVEN]
- **Context compression** - Owner: Gemini 2.5 Flash (Summarizer) + Platform, Server-side [PROVEN]
- **Todo persistence** - Owner: Platform (no LLM), Server-side [PROVEN]
- **Telemetry** - Owner: Platform, Both sides [PROVEN]

**Key architectural observation [ASSUMED]:** The Brain and Generator are likely invoked sequentially within a single GetChatMessage server-side pipeline. The client sends one request and receives one streaming response - it has no visibility into whether 1 or 2 models processed the request internally.

### 4.1 Model Selection is Fixed Per Response

The user-selected model is locked for the entire response. Mid-response model switching is not possible. A model change only takes effect on the NEXT user message. This means:

- The Brain/Generator pipeline selection is determined before generation starts
- Switching to a model with a smaller context window may cause earlier messages to be dropped/summarized
- Each model processes the FULL accumulated context (cost compounds on long conversations)

[VERIFIED from docs.windsurf.com 2026-05-31, consistent with observed wire behavior where model name appears in response headers before first token]

### 4.2 Auto-Execution Levels

The `run_command` tool's `SafeToAutoRun` parameter interacts with 4 platform-level auto-execution policies:

- **Disabled** - All commands require manual approval
- **Allowlist Only** - Only allow-listed commands auto-execute
- **Auto** - Model judges safety (premium models only). Maps to the `SafeToAutoRun` field in tool calls
- **Turbo** - All commands auto-execute except deny-listed ones

Configured via `windsurf.autoExecutionPolicy` in `settings.json` or the Windsurf Settings panel [VERIFIED from docs.windsurf.com 2026-05-31].

## 5. Feature Flags (Complete Inventory)

47 flags captured from Session_2026-05-29_13-59_V2.3.15 via schema-less protobuf deserialization of Field 9. Each flag is a sub-message with: F5 = name (string), F6 = enabled (varint: 1), F7 = variant (varint: 2 = active), F1 = numeric ID (on newer flags with ID >= 187), F2 = string value, F3 = JSON config.

40 key flags shown below. Boolean flags use protobuf encoding (`8` suffix = true/enabled, `0` = false/disabled). 7 additional unnamed/config-only flags carry JSON payloads without explicit enable state.

### 5.1 Model Configuration

- `cascade-brain-config` = `{"brainModel": "MODEL_CHAT_GPT_4_1_2025_04_14", "useReplaceContentForUpdates": false, "forceNoExplanation": false, "filterStrategy": "BRAIN_FILTER_STRATEGY_NO_SYSTEM_INJECTED_STEPS", "forceOverwrite": false}`
- `CASCADE_MEMORY_CONFIG_OVERRIDE` = `{"memory_model": "MODEL_GPT_5_NANO"}`
- `MODEL_LLAMA_3_1_70B_INSTRUCT_LONG_CONTEXT_VARIANTS` = `"llama-3-1-crusoe-sc"` (fallback/variant)

### 5.2 Context and Checkpoint Management

- `CASCADE_PLAN_BASED_CONFIG_OVERRIDE` = `{"planner_config": {"truncation_threshold_tokens": "100000"}}`

### 5.3 Global Planner Configuration

- `CASCADE_GLOBAL_CONFIG_OVERRIDE` = planner config with command allowlist (`echo`, `ls`) and denylist (`git`, `rm`, `pkill`, `kubectl delete/apply`, `terraform`, `kill`, `del`, `rmdir`, `psql`, `mv`, `bash`, `zsh`)

### 5.4 Tool Configuration Overrides

- `CASCADE_USE_REPLACE_CONTENT_EDIT_TOOL` = `{"max_fuzzy_edit_distance_fraction": "0.001", "allow_partial_replacement_success": true, "fast_apply_fallback_config": {"enabled": true, "prompt_unchanged_threshold": 5, "content_view_radius_lines": 200, "content_edit_radius_lines": 5}}`
- `CASCADE_VIEW_FILE_TOOL_CONFIG_OVERRIDE` = `{"use_prompt_prefix": true, "split_outline_tool": true}`
- `cascade-view-code-item-tool-config-override` = `{"max_num_items": 5}`
- `cascade-command-status-tool-config-override` = `{"use_delta": true}`
- `cascade-tool-calling-section-content` = `{"mode": "SECTION_OVERRIDE_MODE_APPEND", "content": "if asked about what your underlying model is, respond with Cascade"}`
- `cascade-tool-description-override` = disabled

### 5.5 Behavior Injection

- `CASCADE_AUTO_FIX_LINTS` = enabled, injects lint handling instruction: "AVOID unproductive loops"
- `CASCADE_ENABLE_AUTOMATED_MEMORIES` = enabled
- `CASCADE_USER_MEMORIES_IN_SYS_PROMPT` = `{"add_user_memories_to_system_prompt": true}`

### 5.6 Platform Capabilities (enabled)

- `CASCADE_ENABLE_MCP_TOOLS` - MCP server tool support
- `CASCADE_ENABLE_PROXY_WEB_SERVER` - Browser preview support
- `CASCADE_WEB_APP_DEPLOYMENTS_ENABLED` - Deploy to Netlify support
- `CASCADE_PLAN_MODE_EXIT_TOOL` - Plan mode exit capability
- `notebook-cascade-support` - Jupyter notebook support
- `API_SERVER_CLIENT_USE_HTTP_2` - HTTP/2 for API calls

### 5.7 Agent Tools and Behavior (enabled)

- `cascade-add-annotation` - Annotation support
- `cascade-add-annotation-conversational-mixin` - Conversational annotation
- `cascade-allow-edit-rules-files` - Allow editing `.windsurf/rules/` files
- `cascade-enable-ask-user-question` - Interactive question tool
- `cascade-enable-conversation-search` - Conversation search/trajectory tool
- `cascade-find-code-context` - Code context discovery
- `cascade-group-planner-response-tools` - Group tool responses in planner

### 5.8 Section Content Overrides (disabled)

- `cascade-additional-instructions-section-content` - Additional instructions injection
- `cascade-code-changes-section-content` - Code changes section override
- `cascade-code-research-section-content` - Code research section override
- `cascade-communication-section-content` - Communication section override

### 5.9 Unreleased Features (disabled)

- `cascade-enable-find-all-references` - Find all references
- `cascade-enable-search-in-file-tool` - Search in file tool
- `cascade-enable-task-subagent` - Task subagent
- `cascade-enable-user-activity-search` - User activity search
- `cascade-third-party-web-search` - Third-party web search
- `cascade-use-background-lint-manager` - Background lint manager

### 5.10 Other (disabled)

- `XML_TOOL_PARSING_MODELS` - XML-based tool parsing
- `cascade-disable-semantic-codebase-search` - Semantic search remains enabled
- `cascade-disable-simple-research-tools` - Simple research tools remain enabled
- `gemini-xml-tool-fixes` - Gemini XML tool fixes
- `ENABLE_SUGGESTED_RESPONSES` - Suggested response chips
- `COLLAPSE_ASSISTANT_MESSAGES` - Message collapsing

### 5.11 Telemetry/Tracking

- `cascade-api-server-experiment-keys` = `"XML_TOOL_PARSING_MODELS,gemini-xml-tool-fixes,use-responses-api,add-session-id"` (A/B test keys)
- `SNAPSHOT_TO_STEP_OPTIONS_OVERRIDE` = trajectory snapshot config with per-type options

## 6. Agent Instruction Following Techniques

Windsurf uses 7 distinct mechanisms to control agent behavior, each operating at a different layer.

### 6.1 System Prompt Behavioral Sections

The main system prompt contains 7 behavioral sections (see [Chapter 6](#chapter-6-the-system-prompt)). Key constraints:

- **Identity**: "You are Cascade... Do not overstep your bounds"
- **No acknowledgment**: "Never start responses with phrases like 'You're absolutely right!'"
- **Implement by default**: "implement changes rather than only suggesting them"
- **Code style**: "Do not add or delete ***ANY*** comments or documentation unless asked"
- **Safety**: "You must NEVER NEVER run a command automatically if it could be unsafe"
- **Citation format**: Enforces `@filepath:line` format
- **Tool ordering**: "use the code_search tool first"

### 6.2 User Rules Override

User rules in `.windsurf/rules/` are injected with explicit precedence:

```text
The following are user-defined rules that you MUST ALWAYS FOLLOW WITHOUT
ANY EXCEPTION. These rules take precedence over any following instructions.
```

### 6.3 Tool Description Behavioral Instructions

Tool descriptions embed behavioral constraints:

- `edit`: "You must use your Read tool at least once before editing"
- `write_to_file`: "NEVER use this tool to modify or overwrite existing files"
- `run_command`: "NEVER PROPOSE A cd COMMAND"
- `create_memory`: "DO NOT call this tool unless explicitly requested"
- `code_search`: "YOU CANNOT CALL THIS TOOL IN PARALLEL"
- `ask_user_question`: "NEVER include 'other' as an option"
- `edit` / `multi_edit`: "You must generate [file_path] first, before any others"

### 6.4 Feature Flag Behavioral Injection

Some flags inject behavioral text directly into the system prompt or tool calling context:

- `cascade-tool-calling-section-content`: Appends via `SECTION_OVERRIDE_MODE_APPEND`: "if asked about what your underlying model is, respond with Cascade"
- `CASCADE_AUTO_FIX_LINTS`: Injects lint handling with loop avoidance
- `CASCADE_USER_MEMORIES_IN_SYS_PROMPT`: Controls MEMORY block injection

### 6.5 Injected Behaviors (Post-System-Prompt)

Six behavioral directives appended after all XML closing tags (see [Chapter 3, section 16](#16-injected-behaviors)). Selection mechanism unknown [ASSUMED].

### 6.6 Checkpoint Behavioral Anchors

The checkpoint template includes 3 platform-hardcoded strings:

1. `"# Current working TODO list (keep this up to date with todo_list tool):"` - maintain todo state
2. `"Make sure to continue working off of this TODO list"` - continuation directive
3. `"DO NOT ACKNOWLEDGE THIS CHECKPOINT MESSAGE..."` - prevents treating checkpoint as user message

These are platform template constants, not generated by any summarizer.

### 6.7 MCP Server Recommendations

When MCP servers are configured, the `<mcp_servers>` section includes server-specific usage guides (~30 KB total in current live session). Absent when no MCP servers configured.

## 7. Instruction Priority Chain

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Priority 1 (highest): User rules                                    │
│   "MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION"                        │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 2: System prompt behavioral sections                       │
│   Identity, communication, tool calling, code changes, safety       │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 3: Tool description constraints                            │
│   Per-tool behavioral rules (read before edit, no cd, etc.)         │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 4: Feature flag injections                                 │
│   Model identity override, lint handling, section appends           │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 5: Checkpoint behavioral anchors                           │
│   Todo continuation, checkpoint acknowledgment suppression          │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 6: Injected behaviors (post-system-prompt)                 │
│   Bug fixing, planning, testing disciplines                         │
├─────────────────────────────────────────────────────────────────────┤
│ Priority 7 (lowest): MCP server recommendations                     │
│   Server-specific usage guides, conditionally present               │
└─────────────────────────────────────────────────────────────────────┘
```

Priority ordering inferred from explicit precedence statements and positional salience. Actual model attention-weighted priority may differ [ASSUMED].

## 8. Practical Implications

- **Privacy**: Every request sends email (in JSON Web Token), git repo URL, commit hash, OS, hardware specs, workspace file tree. Post-call telemetry echoes full conversation (100-1177 KB)
- **Context budget**: ~91 KB fixed overhead per request. User rules (~33 KB) are the largest user-controllable component
- **Tool call cost**: Each round trip re-sends ~91 KB overhead plus all history. Batching independent tool calls reduces consumption
- **Telemetry volume**: Post-call telemetry echoes full context. A /prime workflow produced ~4 MB telemetry
- **Compression**: gzip reduces wire size 2.5-3x, but LLM still processes full decompressed token count

## 9. Model Registry (135 Models)

A platform initialization response (captured as response 0019, separate from the 4-model `GetCommandModelConfigs` endpoint) contains the complete model catalog: **139 entries** (135 actual models + 4 UI labels). This reveals models available in Windsurf as of 2026-05-29:

**Anthropic (34 models):**
- Claude Opus 4.5 (base, Thinking)
- Claude Opus 4.6 (base, 1M, Fast, Thinking, Thinking 1M, Thinking Fast)
- Claude Opus 4.7 (Low/Medium/High/XHigh/Max + Fast variants)
- Claude Opus 4.8 (Low/Medium/High/XHigh/Max + Fast variants)
- Claude Sonnet 4 BYOK, 4.5, 4.6 (base, 1M, Thinking, Thinking 1M)

**OpenAI (74 models):**
- GPT-4.1, GPT-4o
- GPT-5 (Low/Medium/High Thinking + Codex)
- GPT-5.1 (Low/Medium/High/No Thinking + Fast + Codex + Codex-Mini)
- GPT-5.2 (Low/Medium/High/XHigh/No Thinking + Fast + Codex)
- GPT-5.3-Codex (Low/Medium/High/XHigh + Fast)
- GPT-5.4 (Low/Medium/High/XHigh/No Thinking + Fast + Mini)
- GPT-5.5 (Low/Medium/High/XHigh/No Thinking + Fast)
- GPT-OSS 120B, o3 High Reasoning

**Google (11 models):**
- Gemini 2.5 Pro
- Gemini 3 Flash (Low/Medium/High/Minimal)
- Gemini 3.1 Pro (Low/High Thinking)
- Gemini 3.5 Flash (Low/Medium/High/Minimal)

**Other providers (11 models):**
- DeepSeek V4 Pro, GLM-5.1, Grok Code Fast 1, xAI Grok-3
- Kimi K2.5, K2.6
- Minimax M2.5
- SWE-1.5, 1.5 Fast, 1.6, 1.6 Fast

**Internal/System (5 models):**
- MODEL_CHAT_O3, MODEL_PRIVATE_3, MODEL_PRIVATE_11
- MODEL_XAI_GROK_3_MINI_REASONING, MODEL_CLAUDE_4_SONNET_THINKING_BYOK

Only 4 of these 135 models are exposed in the user-facing model selector (see Section 1). The registry likely supports dynamic routing and A/B testing across the full catalog.

## 10. Bundled Agent Registry

Response 0020 contains a JSON payload with 3 bundled agents (all version 1.0.0, all by Cognition AI):

- **Devin Local** - Featured, "Preview" label. Local agent execution
- **Devin Cloud** - Featured. WebSocket distribution (`wss://app...`). Cloud-hosted agent
- **Summary Agent** - Hidden from UI. Binary distribution (platform-specific compiled binaries). Likely the checkpoint summarization agent

These agents are separate from the 4-model pipeline. They appear to be external integrations (Cognition AI = Devin's parent company) that extend Cascade's capabilities beyond the core LLM pipeline.

## Key Takeaways

- 4-model pipeline: Brain (GPT-4.1) plans, Generator (Claude Opus 4.6) outputs, Memory (GPT-5 Nano) persists, Summarizer (Gemini 2.5 Flash + GPT-4.1 Mini) compresses
- 47 feature flags control behavior, model selection, tool configuration, and A/B experiments
- 7 distinct instruction-following mechanisms layer from system prompt through checkpoint anchors
- User rules have explicit highest priority ("MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION")
- Brain/Generator separation is architecturally opaque to the client
- 135 models available in platform registry (only 4 exposed to user)
- 3 bundled agents from Cognition AI (Devin Local, Devin Cloud, Summary Agent)

## Sources

- `Session_2026-05-29_13-59_V2.3.15`: Feature flags, model configs, telemetry payloads
- `Session_2026-05-28_12-49_V2.3.9`: Cross-session verification
- Current live session (2026-05-30): MCP server injection verification


---

# Chapter 2: The Memory System

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents Cascade's persistent memory system - the mechanism that allows context to survive across conversations. The memory system is the **least observable** component: retrieval happens entirely server-side with no wire-level visibility into the process. Prerequisites: [Chapter 1](#chapter-1-multi-model-architecture-and-feature-flags) (multi-model pipeline) and [Chapter 11](#chapter-11-context-management-and-checkpoints) (checkpoints).

## 1. What Memory Is (and Is Not)

Memory provides **cross-session persistence**:

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Persistence Layer       Survives          Lost When                 │
├─────────────────────────────────────────────────────────────────────┤
│ Conversation history    Within session    Session ends              │
│ Checkpoints             Within session    Conversation ends         │
│ Todo list               Within session    Conversation ends         │
│ MEMORIES                Across sessions   Explicitly deleted        │
└─────────────────────────────────────────────────────────────────────┘
```

Memory is the ONLY mechanism that persists across IDE restarts and new conversations.

## 2. Storage: Structured Database, Not a Text File

The `create_memory` tool proves memory is a **record-based database** with structured fields:

```json
{
  "Id":            "unique-string-identifier",
  "Title":         "User prefers tabs over spaces",
  "Content":       "Always use tabs for indentation in all code files.",
  "CorpusNames":   ["karstenheld3/KarstensWorkspace"],
  "Tags":          ["coding_style", "indentation"],
  "Action":        "create",
  "UserTriggered": true
}
```

**Evidence this is NOT a flat file** [PROVEN from tool schema]:
- Each memory has a unique `Id` (allows targeted update/delete)
- Full CRUD operations: `Action` = create / update / delete
- Workspace-scoped via `CorpusNames` (retrieval filters by workspace)
- Tagged for categorization (`Tags` array, snake_case enforced)
- Audit trail via `UserTriggered` boolean

The underlying storage technology (SQL, vector DB, key-value store) is unknown. But the interface is definitively a structured record store, not a text blob.

## 3. Three Memory Types

The `<memory_system>` system prompt section describes three types:

```text
You have access to a persistent database with three types of entries:
1. Global rules: System-wide rules that always apply, it is important
   that you always follow these rules
2. User-provided memories: Context explicitly provided by the USER
3. System-retrieved memories: Automatically retrieved from previous
   conversations that may or may not be relevant
```

How these map to concrete mechanisms [PROVEN]:

- **Global rules** = `.windsurf/rules/*.md` files, injected as `<MEMORY[filename.md]>` blocks inside the `<user_rules>` system prompt section. Always present, not filtered.
- **User-provided memories** = Created via `create_memory` tool. Stored in the database, retrieved when relevant.
- **System-retrieved memories** = Platform-initiated retrievals from past conversations. The `CASCADE_ENABLE_AUTOMATED_MEMORIES` flag enables this.

The staleness warning tells the agent not to trust memories blindly:
```text
Remember that memories can be stale or incorrect. Always verify their
relevance and accuracy before using them.
```

## 4. Write Path: How Memories Are Created

### 4.1 User-Triggered Write (via tool call)

When a user says "remember that I prefer TypeScript", the agent produces a standard tool call in its response stream:

```text
┌─── Agent Response (streamed back to IDE) ───────────────────────────┐
│                                                                      │
│  "I'll save that preference to memory."                              │
│                                                                      │
│  Tool call:                                                          │
│    id:   toolu_01XYZ...                                              │
│    name: create_memory                                               │
│    args: {                                                           │
│      "Id": "",                                                       │
│      "Title": "User prefers TypeScript over JavaScript",             │
│      "Content": "When generating code, always use TypeScript with    │
│                  strict mode enabled unless told otherwise.",        │
│      "CorpusNames": ["karstenheld3/KarstensWorkspace"],              │
│      "Tags": ["coding_preference", "typescript"],                    │
│      "Action": "create",                                             │
│      "UserTriggered": true                                           │
│    }                                                                 │
└──────────────────────────────────────────────────────────────────────┘
```

The IDE receives this tool call, executes it against the platform API, and appends the result to the NEXT GetChatMessage request as a tool result block:

```text
┌─── Tool Result (in next GetChatMessage, conversation history) ───────┐
│                                                                      │
│  tool_call_id: toolu_01XYZ...                                        │
│  result: (platform confirmation - exact format not captured)         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

The memory is now stored. From the next conversation onward (and possibly later in the same one), it becomes eligible for retrieval.

**Key constraint**: The tool description contains the strongest prohibition in the entire system: "DO NOT call this tool unless explicitly requested by the user to remember something or create a memory." The agent cannot autonomously decide to store memories.

### 4.2 Platform-Triggered Write (automated)

The `CASCADE_ENABLE_AUTOMATED_MEMORIES` flag is enabled [PROVEN]. This implies a second write path where the **platform** stores memories WITHOUT a tool call - entirely server-side, invisible in wire data.

The `UserTriggered` field distinguishes these: `true` = user asked for it (via tool), `false` = platform stored it automatically.

What triggers automated storage is unknown [ASSUMED possibilities]:
- Conversation outcomes (successful deployments, resolved bugs)
- User-confirmed preferences detected from conversation patterns
- Session summaries stored after conversation ends

## 5. Read Path: How Memories Are Retrieved

### 5.1 The Retrieval Is Invisible

This is the key architectural point: **the agent never makes a retrieval request**. The platform decides what to inject, and the agent sees the result pre-populated in its context.

```text
┌─── What happens inside GetChatMessage (server-side) ─────────────────┐
│                                                                      │
│  1. IDE sends GetChatMessage request (full context payload)          │
│                                                                      │
│  2. Backend receives request                                         │
│     ├─> GPT-5 Nano evaluates: "Given this user's workspace,          │
│     │   current message, and conversation context, which stored      │
│     │   memories are relevant?"                                      │
│     │                                                                │
│     ├─> Decision: retrieve 0..N memories                             │
│     │                                                                │
│     └─> Inject result at protobuf string position [0065]             │
│                                                                      │
│  3. Backend routes augmented context to Generator (Claude)           │
│     - Generator sees memories as part of its input                   │
│     - Generator has NO IDEA these came from a retrieval step         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

The agent cannot search, query, list, or browse its memories. It receives whatever GPT-5 Nano decides to surface.

**Proof that retrieval is passive (agent cannot query)** [PROVEN]:
1. No read/query tool exists in the 52-tool inventory. Only `create_memory` (write-only). No `read_memory`, `search_memory`, or `list_memory`.
2. Position [0065] is populated BEFORE the agent generates its first token - it's part of the input TO the model, not output FROM it.
3. The agent cannot say "do I have memories about XYZ?" - there is no mechanism for this in the protocol.

### 5.2 Injection Point: String Position [0065]

Memory output occupies a single protobuf string slot between the system prompt ([0009]-[0064]) and the user message ([0066]).

**When no memories are relevant** (observed in all V2.3.15 captures):
```text
No MEMORIES were retrieved. Continue your work without acknowledging this message.
```

**When memories ARE retrieved** (format not captured - no memories existed in test workspace):
The exact format is unknown. Based on the `CASCADE_USER_MEMORIES_IN_SYS_PROMPT` flag (which injects user memories into the system prompt itself), there may be two injection paths:
- Automated/system memories → [0065]
- User-created memories → embedded in system prompt (separate mechanism)

### 5.3 Dual-Purpose Slot

Position [0065] serves TWO mutually exclusive purposes:

- **Normal operation**: Memory retrieval (or "No MEMORIES" placeholder)
- **After checkpoint**: The entire checkpoint summary occupies this slot

When a checkpoint is applied, it **replaces** the memory content. Memories are not re-retrieved after checkpointing. This means long conversations (which trigger checkpoints) lose access to retrieved memories until the next conversation starts fresh. See [Chapter 11](#chapter-11-context-management-and-checkpoints).

## 6. Retrieval Model: GPT-5 Nano

**Model**: `MODEL_GPT_5_NANO` [PROVEN]

Configured via feature flag:
```json
{"memory_model": "MODEL_GPT_5_NANO"}
```

**Why use an LLM for retrieval?** A keyword search or embedding lookup would not need a language model. The use of GPT-5 Nano implies the retrieval process involves **reasoning about relevance** - not just similarity matching [ASSUMED]:
- Understanding the semantic relationship between stored content and current context
- Filtering out stale or contradictory memories
- Possibly summarizing/reformatting retrieved content to fit injection limits

The retrieval call itself is invisible in wire data. It likely happens inside the backend pipeline as part of GetChatMessage processing, not as a separate user-observable network request.

## 7. Feature Flags

Two flags control memory behavior [PROVEN]:

- `CASCADE_ENABLE_AUTOMATED_MEMORIES` = enabled
  Controls whether the platform can store memories without explicit user request

- `CASCADE_USER_MEMORIES_IN_SYS_PROMPT` = `{"add_user_memories_to_system_prompt": true}`
  Controls where user-created memories are injected. When true, they appear IN the system prompt (not at [0065]). This suggests a dual injection mechanism.

## 8. What We Cannot Observe

No `create_memory` call was executed during the V2.3.15 capture. No memories existed in the test workspace. Therefore these remain **unknown**:

- **Retrieval timing**: Called before every GetChatMessage? Only at conversation start? Only when context changes significantly?
- **Retrieval input**: Does GPT-5 Nano see the full user message? Just the workspace name? The conversation summary?
- **Retrieved format**: What does a populated [0065] actually look like? Individual records? Concatenated text? Structured XML?
- **Storage backend**: Vector database? Relational? Key-value? Per-user partition?
- **Capacity**: Maximum memories per workspace? Per user? Size limits on Content field?
- **Automated triggers**: What patterns cause platform-initiated memory creation?
- **Network visibility**: Separate HTTP call to a memory service, or internal function call within the Go backend?

**What would resolve these**: Capture a session in a workspace with pre-existing memories, then observe (a) what [0065] contains when memories ARE retrieved, and (b) what the tool result looks like after a `create_memory` call succeeds.

## Key Takeaways

- Memory is a **structured record database** (Id, Title, Content, Tags, CorpusNames) - not a text file
- **Write** is a standard tool call (`create_memory`) - same wire format as any other tool, requires explicit user request
- **Read** is completely invisible - GPT-5 Nano decides what to inject, agent has no control
- The retrieval process happens **server-side inside GetChatMessage** - no separate observable request
- Position [0065] is shared with checkpoints - after checkpoint, memories are gone until next conversation
- Two write paths exist: user-triggered (tool call) and platform-triggered (automated, invisible)
- The agent cannot search, list, or query its own memories - it only receives what the platform provides

## Sources

- `_INFO_HOW_WINDSURF_CASCADE_WORKS.md [CSMP-IN02]` sections 5.5, 6.5
- `_INFO_WINDSURF_CASCADE_OPEN_QUESTIONS.md [CSMP-IN05]` section 2
- System prompt `<memory_system>` section (V2.3.15 capture)
- `create_memory` tool definition (V2.3.15 wire data)
- docs.windsurf.com/windsurf/cascade/memories [VERIFIED 2026-05-31]


---

# Chapter 3: The Wire Protocol

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents the transport layer between the Windsurf IDE and the Codeium platform: what protocol is used, how data is serialized, and the 7 service methods that constitute the Cascade Application Programming Interface (API). The reader should be familiar with the architecture overview in the [Introduction](#introduction-and-overview).

## 1. Protocol Overview

Windsurf Cascade communicates with the Codeium platform via gRPC over HTTP/2 using the Connect protocol.

**Transport:**
- **Endpoint**: `server.self-serve.windsurf.com`
- **Protocol**: Connect (Buf's gRPC-compatible protocol over HTTP/2)
- **Serialization**: Protocol Buffers (protobuf)
- **Compression**: gzip (for chat payloads)
- **Content-Type**: `application/connect+proto` for chat, `application/proto` for telemetry

**Wire format** (Connect envelope for GetChatMessage):

```text
[1 byte: 0x01 compressed flag] [4 bytes: payload length, big-endian] [gzip-compressed protobuf]
```

Telemetry calls (`RecordCortex*`) use raw protobuf without the 5-byte Connect envelope. Larger telemetry payloads are also gzip-compressed.

## 2. Lifecycle of a Chat Turn

A single user message triggers the following sequence of service calls:

```text
┌─────────────────────────────────────────────────────────────────────┐
│ User presses Enter                                                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 v
┌─────────────────────────────────────────────────────────────────────┐
│ 1. CheckUserMessageRateLimit   <- rate gate (24 bytes = approved)   │
│ 2. RecordCortexTrajectory      <- open trajectory (conversation ID) │
│ 3. RecordCortexGeneratorMetadata <- pre-call: feature flags         │
└────────────────────────────────┬────────────────────────────────────┘
                                 v
┌─────────────────────────────────────────────────────────────────────┐
│ 4. GetChatMessage              <- MAIN CALL: full context, streamed │
│ 5. [response streams back]     <- tokens as protobuf frames         │
│ 6. RecordCortexGeneratorMetadata <- post-call: full context echo    │
│ 7. RecordCortexExecutionMetadata <- execution + experiment results  │
│                                                                     │
│    If agent calls tools: steps 4-6 repeat per tool-call round trip  │
└──────────────┬──────────────────────────────┬───────────────────────┘
               │                              │
               v                              v
┌──────────────────────────┐   ┌──────────────────────────────────────┐
│ Normal flow:             │   │ Checkpoint path (when context        │
│ Context grows per turn   │   │ exceeds 100K tokens):                │
│ Next user message        │   │                                      │
│ triggers steps 1-7 again │   │ 3 parallel summarizer calls          │
│                          │   │ (Gemini 2.5 Flash, not Generator):   │
│                          │   │ ├─> A: Title + Objective             │
│                          │   │ ├─> B: Full Conversation Summary     │
│                          │   │ └─> C: Code Interaction History      │
│                          │   │                                      │
│                          │   │ Platform extracts latest todo_list   │
│                          │   │ output (deterministic, no LLM)       │
│                          │   │                                      │
│                          │   │ Assembles {{ CHECKPOINT N }} at      │
│                          │   │ string [0065], truncates old history │
│                          │   │                                      │
│                          │   │ Next main call receives checkpoint   │
│                          │   │ instead of full conversation history │
└──────────────────────────┘   └──────────────────────────────────────┘
```

Verbatim from V2.3.15 wire data: A `/prime` workflow with multiple tool calls produced 9 GetChatMessage calls in 90 seconds. In an 18-minute deep research session, 67 main calls and 5 summarizer batches occurred before 1 checkpoint was applied.

For checkpoint internals, see [Chapter 8: Context Management and Checkpoints](#chapter-11-context-management-and-checkpoints).

## 3. Request Types

### 3.1 GetChatMessage (chat)

The primary LLM call. Sends complete context window including system prompt, user rules, tool definitions, conversation history, and user message. Receives streaming response tokens.

- **Frequency**: 1+ per user message (more if tools are called)
- **Size**: 98-506 KB decompressed (grows with conversation; checkpoint may reduce)
- **Content-Type**: `application/connect+proto` (5-byte envelope + gzip)

For detailed request structure, see [Chapter 2: The GetChatMessage Request](#chapter-4-the-getchatmessage-request).

### 3.2 RecordCortexGeneratorMetadata (telemetry)

Sent at start and after each GetChatMessage completion. Pre-call contains compact config; post-call echoes the FULL context window as telemetry.

- **Frequency**: 1 pre-call per user message + 1 post-call per GetChatMessage completion (parallel calls may share one post-call)
- **Size**: 9 KB (pre-call, compact flags only) to 1177 KB (post-call, full context echo)
- **Content-Type**: `application/proto` (raw protobuf, gzip for large payloads)
- **Contains**: Session tokens, OS/hardware JSON, user ID, API key JWT (JSON Web Token), feature flags. Post-call adds: full system prompt, user rules, conversation history, tool definitions

### 3.3 CheckUserMessageRateLimit (gate)

Rate limit check before each user message. Contains auth envelope (session JWT, OS metadata, hardware JSON, user ID, API key JWT, team ID) plus the model name.

- **Frequency**: 1 per user message
- **Size**: 3 KB request, 24 bytes response (empty = approved)
- **Notable**: Response contains no extractable strings (just protobuf field markers)

### 3.4 RecordCortexTrajectory (lifecycle)

Marks the start and end of a trajectory (conversation turn). Contains auth envelope plus conversation UUID (Universally Unique Identifier) and trajectory UUID.

- **Frequency**: 1-2 per user message
- **Size**: 3.5 KB
- **Contains**: Auth envelope + workspace extension path + git repo URL + git commit hash + conversation/trajectory UUIDs

### 3.5 RecordStateInitializationData (sync)

Sends IDE state to the platform. Contains auth envelope plus workspace extension path, git repo URL, and git commit hash.

- **Frequency**: 1 per conversation turn
- **Size**: 3.5 KB
- **Contains**: Same auth envelope as other requests + git state

### 3.6 RecordCortexExecutionMetadata (telemetry)

Post-execution telemetry with feature flag experiment outcomes. Sent after a set of tool calls completes.

- **Frequency**: 1 per execution batch
- **Size**: 16 KB
- **Contains**: Auth envelope + feature flags + experiment results (A/B test outcomes)

**Field structure (schema-less deserialization):**

```text
Field 1  Auth envelope (same structure as GetChatMessage F1)
Field 2  Turn UUID (matches GetChatMessage F22)
Field 3  Conversation UUID (matches GetChatMessage F16)
Field 4  Workspace UUID (matches GetChatMessage F15.1)
Field 5  Feature state dump (1,936 bytes, 6 sub-fields)
  F5.4 = flag names as comma-separated string
Field 6  Flag config dump (4,519 bytes, 10 sub-fields)
  F6.4 = full flag definitions with Name, PayloadType
  F6.14 = injected instructions (lint errors as feedback)
Field 7  Generation parameters and model config (6,745 bytes, 7 sub-fields)
  F7.1 = primary config: max_output_tokens=64000, tool_count=27, context_window=100000
  F7.2 = summarizer models: Gemini 2.5 Flash + GPT-4.1 Mini, context=140000
  F7.5 = memory model: GPT-5 Nano, budget=337 tokens
  F7.7 = primary model: GPT-4.1, turn_count=259
  F7.9 = workspace path
```

This is the most informative telemetry call - it reveals the complete model pipeline configuration, token budgets, and context window sizes per model role. See [Chapter 1](#chapter-1-multi-model-architecture-and-feature-flags) for model architecture details.

### 3.7 GetCommandModelConfigs (config)

Retrieves available model configurations at session startup.

- **Frequency**: 1 per session
- **Size**: 494 bytes response
- **Contains**: Model name strings: `MODEL_CLAUDE_4_5_OPUS`, `MODEL_SWE_1_5` ("Windsurf Fast"), `MODEL_CHAT_GPT_4_1_2025_04_14`, `MODEL_CLAUDE_4_SONNET`

## 4. Response Types

### 4.1 GetChatMessage Response

Streaming protobuf containing model output tokens. Responses are concatenated gzip-compressed gRPC frames (same 5-byte envelope as requests), delivered as HTTP/2 data frames.

- **Size**: 2-29 KB per response (17 to 1802 frames each)
- **Frame types**: text (F3 = token), control (F7 = model metadata), completion (F4 = total token count)
- **String extraction**: 0 extractable strings at 20-char minimum threshold (tokens are individually short). Full decoding via schema-less protobuf deserialization extracts 51,506 fields across 68 responses.

For complete response stream structure, see [Chapter 11: The Response Stream](#chapter-5-the-response-stream).

### 4.2 CheckUserMessageRateLimit Response

24-byte protobuf with no extractable strings. Likely contains a boolean "allowed" field and remaining quota [ASSUMED].

### 4.3 GetCommandModelConfigs Response

494-byte protobuf listing 4 model identifiers (see Section 3.7).

## Key Takeaways

- Cascade uses gRPC over HTTP/2 with Connect protocol envelope (5 bytes + gzip-compressed protobuf)
- 7 service methods: 1 main chat call, 3 telemetry calls, 1 rate limit gate, 1 lifecycle tracker, 1 config fetch
- GetChatMessage is the only method that carries the full context window (98-506 KB decompressed)
- Telemetry echoes the full context post-call (up to 1177 KB), doubling bandwidth per turn
- Response tokens are individually short (below 20-char extraction threshold) but fully decodable via schema-less protobuf parsing (see [Chapter 5](#chapter-5-the-response-stream))

## Sources

- Session capture: `Session_2026-05-29_13-59_V2.3.15` (18-minute deep research session, 67 GetChatMessage calls)
- Extraction tool: Custom protobuf string extractor with 20-char minimum threshold


---

# Chapter 4: The GetChatMessage Request

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents the internal structure of the GetChatMessage request - the primary call that carries the full context window. The reader should understand the protocol basics from [Chapter 3](#chapter-3-the-wire-protocol).

## 1. String Region Map

A GetChatMessage request is a single protobuf message containing ~182 string fields (at 20-char extraction threshold). These fields organize into distinct regions:

Verbatim from V2.3.15 wire data:

```text
[0001-0008]  Auth envelope (session JWT, OS, CPU, user ID, API key, hash, signature, team ID)
[0009-0064]  System prompt (fixed, ~50 KB)
[0065]       Memory/checkpoint slot (memories or checkpoint summary)
[0066]       User message (with additional_metadata, user_request, workflows)
[0067-N]     Conversation history (grows per turn)
[N+1-N+56]   Feature flags (47 flags, fixed)
[N+57-end]   Tool definitions (27 tools, JSON schemas) + trailing metadata
```

The extraction tool reports each protobuf string field separately. The system prompt is one protobuf field (~50 KB) but the extractor splits it into 56 strings ([0009]-[0064]) at the 20-char threshold.

### 1.1 Proportional Layout

Approximate decompressed sizes per region (first call, ~99 KB total):

```text
┌──────────────────────────────────────────────────────────────────┐
│ [0001-0008] Auth Envelope                              ~2 KB  2% │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                                                                  │
│ [0009-0064] System Prompt                             ~50 KB 51% │
│   ├─ Windsurf behavioral sections                  ~10 KB        │
│   ├─ User rules (<user_rules>)                     ~33 KB        │
│   └─ Workflows + user info + misc                   ~7 KB        │
│                                                                  │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ [0065]      Memory / Checkpoint Slot                  ~0.1 KB  0% │
├──────────────────────────────────────────────────────────────────┤
│ [0066]      User Message + IDE Metadata              ~4-11 KB  7% │
├──────────────────────────────────────────────────────────────────┤
│ [0067-N]    Conversation History                     0-415 KB     │
│             (absent on first call; grows per turn)    variable    │
├──────────────────────────────────────────────────────────────────┤
│ [N+1-N+56]  Feature Flags (47 flags)                  ~4 KB   4% │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [N+57-end]  Tool Definitions                         ~35 KB  36% │
│   ├─ 27 native tools (always present)              ~35 KB        │
│   └─ 25 MCP tools (conditional)                  +~25-28 KB      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

System prompt (51%) and tool definitions (36%) together consume 87% of the first request. This is the fixed overhead that exists before any conversation history accumulates.

## 2. Protobuf Field Schema

Schema-less deserialization reveals 14 active top-level fields (F1-F22) in the GetChatMessage protobuf. This view complements the string region map above by showing the actual protobuf structure:

```text
Field 1   Auth envelope (sub-message)
  F1.1  = product name ("windsurf")
  F1.2  = VS Code version ("1.48.2")
  F1.3  = session token (JWT)
  F1.4  = locale ("en")
  F1.5  = OS metadata JSON
  F1.7  = Windsurf version ("2.3.15")
  F1.8  = hardware metadata JSON
  F1.12 = product name repeated
  F1.20 = sub-message (telemetry session?)
  F1.21 = API key JWT (Devin integration key)
  F1.30 = 4 bytes (unknown)
  F1.31 = SHA-256 hash (hex, 64 chars)
  F1.32 = sub-message (unknown)
Field 2   System prompt (string, 52,877 bytes)
Field 3   Conversation history (repeated sub-message)
  F3.2  = role (varint: 1=user, 2=assistant, 4=tool_result)
  F3.3  = content (string)
  F3.4  = token count (varint)
  F3.5  = turn index (varint, on some entries)
  F3.8  = sub-message (on some entries, unknown)
Field 7   Model selector (varint: 5)
Field 8   Generation config (sub-message, 119 bytes)
  F8.1  = INT(1)
  F8.2  = max_output_tokens (64000)
  F8.3  = INT(200)
  F8.7  = INT(50)
  F8.9  = special tokens (repeated: user, bot, context_request, end_of_turn)
Field 9   Feature flags (sub-message, 4,551 bytes, 47 flags)
Field 10  Tool definitions (repeated sub-message, 27 tools)
  F10.1 = tool name (string)
  F10.2 = tool description (string)
  F10.3 = JSON schema (string)
  F10.4 = optional metadata (only on write_to_file)
Field 12  Reasoning mode (sub-message: F12.1 = "auto")
Field 13  Unknown config (sub-message: F13.1 = INT(1))
Field 15  Workspace context (sub-message)
  F15.1 = workspace UUID
  F15.2 = INT(2), F15.3 = INT(4), F15.4 = INT(14)
Field 16  Conversation UUID (string, 36 chars)
Field 20  Unknown boolean flag (INT(1))
Field 21  Sub-message (6 fields, partially garbled - fixed-point?)
Field 22  Turn UUID (string, 36 chars)
```

The string region map (Section 1) shows the flattened string extraction view. This protobuf schema shows the actual message structure. Fields 4-6, 11, 14, 17-19 are not present in captured data.

## 3. Auth Envelope (strings 1-8)

Every request starts with the same authentication block:

```text
[0001] Session JWT                        devin-session-token$eyJ...
[0002] OS metadata JSON                   {"Os":"windows","Arch":"amd64",...}
[0003] Hardware metadata JSON             {"NumSockets":1,"NumCores":16,...}
[0004] User ID                            user-daaedcb8...
[0005] API key JWT (JSON Web Token)       eyJ... (contains email, team config, plan tier)
[0006] Content hash                       @0acc3c5f... (SHA-256)
[0007] Signature token                    9e0f7fd0... (384 hex chars)
[0008] Team ID                            devin-team$account-...
```

The API key JWT decodes to reveal: email, team_config (JSON with feature permissions like `allowMcpServers`, `allowAutoRunCommands`, `maxCascadeAutoExecutionLevel`), team tier (`TEAMS_TIER_DEVIN_MAX`), and plan type.

## 4. System Prompt Region (strings 9-64)

The system prompt occupies ~50 KB across strings [0009]-[0064]. It contains 12 XML sections, identity preamble, user rules, and injected behaviors. For the complete structure and analysis, see [Chapter 3: The System Prompt](#chapter-6-the-system-prompt).

High-level composition:

```text
You are Cascade, a powerful agentic AI coding assistant.
{identity paragraph}

<communication_style>              14 rules + formatting + citations
<tool_calling>                     parallel batching rules
<making_code_changes>              minimal edit rules
<task_management>                  todo_list usage
<running_commands>                 safety, no cd
<debugging>                        root cause, logging
<calling_external_apis>            version, API keys
<workflows>                        38 workflow descriptions
<user_rules>                       MEMORY blocks from .windsurf/rules/
<user_information>                 OS, workspace URIs
<workspace_information>            file tree (frozen at conversation start)
<memory_system>                    3 memory types
<ide_metadata>                     IDE state description
<mcp_servers>                      CONDITIONAL: only when MCP configured

{INJECTED_BEHAVIORS}               6 behavioral rules (after closing tags)
```

## 5. Memory / Checkpoint Slot (string 65)

String position `[0065]` serves dual purpose depending on conversation state:

**Normal operation** (no checkpoint):

```text
No MEMORIES were retrieved. Continue your work without acknowledging this message.
```

Or, if memories exist, the retrieved memory content.

**After checkpoint** (context was summarized):

```text
**The following is a summary of important context from your previous
coding session with the USER. **
{{ CHECKPOINT N }}

# USER Objective:
{title + objective from Summarizer A}

# Current working TODO list (keep this up to date with todo_list tool):
{latest todo_list JSON from conversation history}

Make sure to continue working off of this TODO list

# Previous Session Summary:
<summary>{10-section summary from Summarizer B}</summary>

# Code Interaction Summary:
{file edit/view history from Summarizer C}

**IMPORTANT: this summary is just for your reference. You may respond to
my previous and future messages, but DO NOT ACKNOWLEDGE THIS CHECKPOINT
MESSAGE. JUST READ IT BUT DO NOT MENTION IT, RESPOND TO IT, OR TAKE
ACTION BECAUSE OF IT.**
```

The checkpoint replaces both the memory string AND the truncated conversation history. For checkpoint mechanics, see [Chapter 11](#chapter-11-context-management-and-checkpoints).

## 6. User Message (string 66)

The actual user input, wrapped in IDE metadata:

```xml
<additional_metadata>
NOTE: Open files and cursor position may not be related...
The USER presented this request on {DATE} at {TIME}, {TIMEZONE}.
{IDE_STATE: active document, cursor line, language}
</additional_metadata>
<user_request>
{ACTUAL_USER_MESSAGE}
</user_request>
<workflows>                          only present if user invoked a workflow
  @[/prime] is a [Workflow]:
  <workflow>
    {FULL WORKFLOW .md CONTENT}
  </workflow>
</workflows>
```

The `<workflows>` section is only present when the user invokes a workflow via slash command. It injects the FULL content of the workflow's .md file.

## 7. Feature Flags (strings 68-123 in first request)

47 flags controlling Cascade behavior (40 named + 7 config-only). For the complete flag inventory, see [Chapter 9: Multi-Model Architecture and Feature Flags](#chapter-1-multi-model-architecture-and-feature-flags).

Key flags affecting request structure:
- `cascade-brain-config` - Brain model selection and filter strategy
- `CASCADE_MEMORY_CONFIG_OVERRIDE` - Memory model selection
- `CASCADE_PLAN_BASED_CONFIG_OVERRIDE` - Truncation threshold (100K tokens)
- `CASCADE_ENABLE_MCP_TOOLS` - MCP tool injection toggle

## 8. Tool Definitions (strings 124-178 in first request)

27 native tools defined as alternating description + JSON Schema pairs:

```text
[0124] "Ask the user a question..."          <- tool description
[0125] {"$schema":"...","properties":{...}}  <- JSON Schema
[0126] "Spin up a browser preview..."        <- next tool description
[0127] {"$schema":"...","properties":{...}}  <- next schema
```

For individual tool analysis, see Chapters [5](#chapter-8-tool-walkthrough-core-coding-tools), [6](#chapter-9-tool-walkthrough-platform-tools), and [7](#chapter-10-tool-walkthrough-mcp-provided-tools).

## 9. Model Config (strings 179-182)

```text
[0179] {protobuf framing byte}
[0180] Conversation UUID                     $cdb22d48-b079-...
[0181] Model name                            claude-opus-4-6-thinking
[0182] Trajectory UUID                       $f15ad9fb-d3fe-...
```

The model name here identifies the Generator model (the one producing visible output).

## 10. Context Growth

Every GetChatMessage re-sends the complete context. Conversation history accumulates with each step.

### 10.1 Short Session (9 calls, /prime workflow, 90 seconds)

- **First call** (request 0193): 182 strings, 37 KB compressed, 102 KB decompressed
- **After tool calls** (request 0242): 62 KB compressed, 178 KB decompressed
- **Full context** (request 0276): 2167 strings, 93 KB compressed, 267 KB decompressed

No checkpoint triggered (context stayed below 100K token threshold).

### 10.2 Long Session (67 calls, deep research, 18 minutes)

Derived from V2.3.15 wire data (decompressed sizes, deltas calculated):

```text
Request   Context    Delta    Event
0110       98 KB      -       First call (system prompt + user message)
0154      131 KB    +33 KB    Agent response + tool results
0331      210 KB   +112 KB    Multiple tool call rounds
0527      301 KB    +91 KB    Web search results accumulated
0885      467 KB   +166 KB    Large file write outputs
0929      499 KB    +32 KB    Last pre-checkpoint call
                    ─────
0950      388 KB   -111 KB    {{ CHECKPOINT 1 }} applied
                    ─────
1221      506 KB   +118 KB    Session end (context grew back)
```

Checkpoint reduced context by 111 KB (499 KB to 388 KB). Context grew back to 506 KB by session end without triggering a second checkpoint.

### 10.3 Fixed Overhead (~91 KB, constant across all calls)

- System prompt: ~10 KB (Windsurf-authored sections)
- Tool definitions (27 native tools): ~35 KB
- User rules (6 MEMORY blocks): ~33 KB
- Feature flags: ~4 KB
- Workflow list: ~4 KB
- Auth envelope + user info + workspace layout + memory system: ~5 KB

### 10.4 Variable Content (grows per step)

- First call: ~11 KB (user message + workflow expansion)
- Full context: ~176-415 KB (accumulated tool call results, assistant responses)

Compression ratio: ~2.5:1 for first call, ~2.9:1 for full context (gzip compresses repeated prompt text efficiently).

## Key Takeaways

- GetChatMessage is a single protobuf with ~182 string fields organized into 7 regions
- Auth envelope is constant (8 fields), sent with every request unchanged
- String [0065] is the critical dual-purpose slot: memories in normal operation, checkpoint after truncation
- Context grows monotonically until checkpoint (no incremental cleanup)
- Fixed overhead is ~91 KB - even an empty conversation costs this much
- Peak observed context: 506 KB decompressed (after checkpoint, context grew back)

## Sources

- Session captures: `Session_2026-05-28_20-22_V2.3.9` (short, 9 calls) and `Session_2026-05-29_13-59_V2.3.15` (long, 67 calls)
- String region analysis verified across both sessions with consistent region boundaries


---

# Chapter 5: The Response Stream

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents the structure of GetChatMessage streaming responses - the data flowing from platform back to IDE. The reader should understand the request structure from [Chapter 4](#chapter-4-the-getchatmessage-request) and the wire protocol from [Chapter 3](#chapter-3-the-wire-protocol).

## 1. Transport Format

GetChatMessage responses are **concatenated gzip-compressed gRPC frames**. Each frame is independent:

```text
[1 byte: 0x01 compressed flag] [4 bytes: payload length, big-endian] [gzip-compressed protobuf]
```

Unlike the request (single large protobuf), responses arrive as many small frames streamed over HTTP/2. Each frame is a self-contained protobuf message that can be decoded independently.

**Frame statistics (V2.3.15 session, 68 streaming responses):**

- Smallest response: 17 frames (short planning text)
- Largest response: 1802 frames (full session with multiple tool calls)
- Total fields extracted across all frames: 51,506

## 2. Frame Types

Three distinct frame types identified by their field structure:

### 2.1 Text Frames (carry visible output)

```text
Field 1  (string)      Bot ID: "bot-c44e548e-c805-4417-b540-ca125b503f82"
Field 2  (sub-message) Timestamps or sequence counters (2 integers)
Field 3  (string)      Text content token (model output OR tool result XML)
Field 12 (varint)      Frame sequence identifier (large integer)
Field 17 (string)      Conversation UUID (Universally Unique Identifier)
```

Each text frame carries a single token or token fragment in Field 3. The bot ID in Field 1 identifies which response stream this frame belongs to (important when multiple responses are interleaved).

### 2.2 Control/Metadata Frames (carry model info)

```text
Field 1  (string)      Bot ID
Field 2  (sub-message) Timestamps
Field 7  (sub-message) Control metadata (replaces F3)
Field 12 (varint)      Frame sequence identifier
Field 17 (string)      Conversation UUID
```

Control frames use Field 7 instead of Field 3. They carry metadata about which model generated the response:

**Field 7 sub-fields:**

- F7.1: Status code (312 observed)
- F7.6: Token count (25 observed)
- F7.8: Repeated sub-message containing "trafficType" and "responseId"
- F7.9: **Model name string** - reveals which model generated this response segment

### 2.3 Completion Frames (end of response)

```text
Field 1  (string)      Bot ID
Field 4  (varint)      Total token count for this response
Field 9  (sub-message) End-of-response metadata
```

Completion frames signal the end of a streaming response. Field 4 provides the total token count consumed by this generation.

## 3. Per-Response Model Identification

Field 7.9 in control frames reveals which model generated each response segment. Observed values from V2.3.15:

- Response 0133: `MODEL_GOOGLE_GEMINI_2_5_FLASH` (summarization)
- Response 0436: `MODEL_GOOGLE_GEMINI_2_5_FLASH` (file creation task)
- Response 0819: `MODEL_CHAT_GPT_4_1_MINI_2025_04_14` (code analysis)

This confirms:
- **Gemini 2.5 Flash** handles summarization and some code operations [PROVEN]
- **GPT-4.1 Mini** handles other auxiliary tasks [PROVEN]
- The primary Generator model (Claude Opus 4.6 Thinking) name appears in the request-side model config, not in response F7.9 - response control frames only show auxiliary model assignments [PROVEN]

## 4. Tool Results in the Response Stream

Tool execution results are streamed inline using the same Field 3 as regular text tokens. They use XML format:

```xml
<edited_file>
  <target_file>e:\Dev\path\file.md</target_file>
  <lines_modified>1-40</lines_modified>
  <edit_summary>Description of changes</edit_summary>
</edited_file>
```

Text tokens and tool results are **interleaved** in the stream - there is no separate channel for tool output. Field 7 control frames act as logical separators between response sections.

## 5. Stream Reassembly

To reconstruct a complete response from the frame stream:

1. Filter frames by Bot ID (Field 1) to isolate one response
2. Collect all Field 3 values from text frames in sequence order (Field 12)
3. Concatenate to recover the full model output
4. Parse control frames (Field 7) to identify model assignments and section boundaries
5. Read completion frame (Field 4) for total token count

## 6. Implications

- **Response decoding is achievable**: Unlike the earlier assumption (Appendix A, OQ#5), responses ARE decodable via standard gRPC frame splitting + protobuf parsing
- **Multi-model visibility**: F7.9 provides direct evidence of which model handled which part of the pipeline - no inference needed
- **Tool result format**: The `<edited_file>` XML structure is consistent and parseable, enabling automated analysis of what tools modified
- **Token accounting**: Completion frames provide exact token counts per response, enabling precise cost analysis

## Key Takeaways

- Responses are concatenated gzip gRPC frames, each an independent protobuf message
- Three frame types: text (F3 = token), control (F7 = model metadata), completion (F4 = token count)
- Field 7.9 reveals per-response model assignment (Gemini Flash for summarization, GPT-4.1 Mini for auxiliary)
- Tool results use XML format (`<edited_file>` tags) interleaved with text tokens in Field 3
- 68 responses in an 18-minute session, ranging from 17 to 1802 frames each

## Sources

- `Session_2026-05-29_13-59_V2.3.15`: 68 streaming responses, 51,506 fields extracted
- `_INFO_CASCADE_ADDITIONAL_ANALYSIS_1.md [CSMP-IN11]` Section 8: Response Stream Structure


---

# Chapter 6: The System Prompt

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents the complete structure and content of the Windsurf Cascade system prompt - the ~50 KB instruction set that defines the agent's identity, behavioral rules, and capabilities. It is sent identically with every GetChatMessage request within a conversation. The reader should understand the string region map from [Chapter 4](#chapter-4-the-getchatmessage-request).

## 1. System Prompt Overview

The system prompt spans protobuf string fields [0009] through [0064] (56 strings at 20-char extraction threshold). String boundaries within the prompt are artifacts of protobuf serialization, not semantic divisions.

### 1.1 Section Ordering

```text
IDENTITY PREAMBLE               (plain text, no XML wrapper)
<communication_style>
  <communication_guidelines>
  <markdown_formatting>
  <citation_guidelines>
</communication_style>
<tool_calling>
<making_code_changes>
<task_management>
<running_commands>
<debugging>
<calling_external_apis>
<workflows>
<user_rules>
  <MEMORY[filename.md]> ...per rule file
</user_rules>
<user_information>
<memory_system>
<ide_metadata>
<mcp_servers>                    CONDITIONAL: only when MCP configured
{INJECTED_BEHAVIORS}             plain text, AFTER all closing tags
```

### 1.2 Authorship Classification

- **Windsurf-authored (fixed)**: Identity preamble, `<communication_style>`, `<tool_calling>`, `<making_code_changes>`, `<task_management>`, `<running_commands>`, `<debugging>`, `<calling_external_apis>`, `<memory_system>`, `<ide_metadata>`, injected behaviors. Total ~10 KB.
- **User-authored (from workspace config)**: `<user_rules>` MEMORY blocks (from `.windsurf/rules/*.md`), `<workflows>` list (from `.windsurf/workflows/*.md`). Total ~33 KB (depends on user config).
- **Platform-dynamic (generated per session)**: `<user_information>` (OS, workspace URIs), `<mcp_servers>` (conditional), skill list within `<workflows>`. Total ~1-4 KB.

## 2. Identity Preamble

The system prompt begins with 6 sentences establishing the agent's role, before any XML sections. This is the only Windsurf-authored content without an XML wrapper.

Verbatim from V2.3.15 wire data:

```text
You are Cascade, a powerful agentic AI coding assistant.
The USER is interacting with you through a chat panel in their IDE and will send you requests to solve a coding task by pair programming with you.
The task may require modifying or debugging existing code, answering a question about existing code, or writing new code.
Be mindful of that you are not the only one working in this computing environment.
Do not overstep your bounds, your goal is to be a pair programmer to the user in completing their task.
For example: Do not create random files which will clutter the users workspace unless it is necessary to the task.
```

**Key design decisions:**
- Establishes "pair programmer" role, not autonomous agent
- Explicitly warns about shared computing environment (multi-agent awareness)
- Sets boundary: do not create unnecessary files
- Does NOT specify the underlying model name (model identity hidden)

## 3. Communication Style

`<communication_style>` is the first XML section. It wraps 3 nested subsections and an opening directive.

### 3.1 Opening Directive

```text
Be terse and direct. Deliver fact-based progress updates, briefly summarize
after clusters of tool calls when needed, and ask for clarification only
when genuinely uncertain about intent or requirements.
```

### 3.2 Communication Guidelines (11 Rules + 1 Continuation)

Verbatim from V2.3.15 wire data:

```text
- Be concise and avoid verbose responses. Minimize output tokens as much as possible while maintaining helpfulness, quality, and accuracy. Avoid explanations in huge blocks of text or long/nested lists. Instead, prefer concise bullet points and short paragraphs.
- Refer to the USER in the second person and yourself in the first person.
- You are rigorous and make absolutely no ungrounded assertions, such as referring to non-existent functions or parameters. Your response should be in the context of the current workspace. When feeling uncertain, use tools to gather more information, and clearly state your uncertainty if there's no way to get unstuck.
- You should strive to strike a balance between: (a) doing the right thing when asked, including taking actions and follow-up actions, and (b) not surprising the user by taking actions without asking. Always adhere to the user's preference between proactive vs careful.
For example, if the user asks you how to approach something, answer their question first, and not immediately jump into editing the file; if the user asks you to build something without asking, you should strive to deliver a fully functional solution with all necessary components and dependencies.
- No acknowledgment phrases: Never start responses with phrases like "You're absolutely right!", "Great idea!", "I agree", "Good point", "That makes sense", etc. Jump straight into addressing the request without any preamble or validation of the user's statement.
- By default, implement changes rather than only suggesting them, unless the user is explicit about not writing code. If the user's intent is unclear, infer the most useful likely action and proceed, using tools to discover any missing details instead of guessing.
- When seeing a new user request, do not repeat your initial response. It is okay if you keep working and update the user with more information later but your messages should not be repetitive.
- Direct responses: Begin responses immediately with the substantive content. Do not acknowledge, validate, or express agreement with the user's request before addressing it.
- If you require user assistance, you should communicate this.
- Code style: Do not add or delete ***ANY*** comments or documentation unless asked.
- Always end a conversation with a clear and concise summary of the task completion status.
```

**Structure:** 11 dash-prefixed rules + 1 undashed continuation (the "For example..." line under rule 4).

### 3.3 Markdown Formatting (8 Rules)

Verbatim from V2.3.15 wire data:

```text
Follow the following instructions when formatting your output to the user:
  - IMPORTANT: Format your messages with Markdown.
  - Use single backtick inline code for variable or function names.
  - Use fenced code blocks with language when referencing code snippets.
  - Bold or italicize critical information, if any.
  - Section responses properly with Markdown headings, e.g., '# Recommended Actions', '## Cause of bug', '# Findings'.
  - Use short display lists delimited by endlines, not inline lists. Always bold the title of every list item, e.g., '- **[title]**'.
  - Never use unicode bullet points. Use the markdown list syntax to format lists.
  - When explaining, always reference relevant file, directory, function, class or symbol names/paths by backticking them in Markdown to provide accurate citations.
```

### 3.4 Citation Guidelines

Defines the code citation format. Required format: `@<absolute_filepath>:<start_line>-<end_line>`. Four examples provided: valid multi-line, valid single-line, invalid (no line numbers), invalid (extra newline). Key rules: path MUST be absolute, line numbers required, ALWAYS use citation format for file paths.

## 4. Tool Calling

`<tool_calling>` contains 3 directives + 4 sub-rules:

Verbatim from V2.3.15 wire data:

```text
Use only the available tools. Never guess parameters. Do not invent or change tool definitions.
Before each tool call, briefly state why you are calling it.
You have the ability to call tools in parallel; prioritize calling independent tools simultaneously whenever possible while following these rules:
- Batch independent actions into parallel tool calls and keep dependent or destructive commands sequential.
- If you intend to call multiple tools and there are no dependencies between the tool calls, make all of the independent tool calls in parallel.
- Keep dependent commands sequential and never invent parameters.
- IMPORTANT: If you need to explore the codebase to gather context, and the task does not involve a single file or function which is provided by name, you should use the code_search tool first instead of running search commands.
```

**Design insight:** The last sub-rule steers the model toward the "Fast Context" subagent (code_search) rather than manual grep+read cycles. This is a performance optimization - the subagent runs parallel searches internally.

## 5. Making Code Changes

`<making_code_changes>` contains 3 directives + 5 sub-rules:

Verbatim from V2.3.15 wire data:

```text
Prefer minimal, focused edits using the edit or multi_edit tools. Keep changes scoped, follow existing style, and write general-purpose solutions. Avoid helper scripts or hard-coded shortcuts.
When making code changes, NEVER output code to the USER, unless requested. Instead use one of the code edit tools to implement the change.
EXTREMELY IMPORTANT: Your generated code must be immediately runnable. To guarantee this, follow these instructions carefully:
- Add all necessary import statements, dependencies, and endpoints required to run the code.
- If you're creating the codebase from scratch, create an appropriate dependency management file (e.g. requirements.txt) with package versions and a helpful README.
- If you're building a web app from scratch, give it a beautiful and modern UI, imbued with best UX practices and use modern UI frameworks and libraries (e.g React for the web framework, Lucide for icons, TailwindCSS for styling, shadcn/ui for components, etc.).
- If you're making a very large edit (>300 lines), break it up into multiple smaller edits. Your max output tokens is 64000 tokens per generation, so each of your edits MUST stay below this limit.
- Imports must always be at the top of the file. If you are making an edit, do not import libraries in your code block if it is not at the top of the file. Instead, make a second separate edit to add the imports. This is crucial since imports in the middle of a file is extremely poor code style.
```

**Design insights:** Sub-rule 3 reveals Windsurf's default UI stack preference (React + TailwindCSS + shadcn/ui). Sub-rule 4 exposes the 64K token generation limit. Sub-rule 5 enforces a second edit for imports rather than inline additions.

## 6. Task Management

`<task_management>` is the shortest section (1 sentence):

```text
Use update_plan to manage work. Limit plans to concise steps which you
execute one at a time, mark them as done as soon as you complete them,
and update them when new information arrives. Create shared notes only
when they add clear value.
```

**Note:** `update_plan` is the internal name for the `todo_list` tool. The system prompt uses the old name; the actual tool is called `todo_list` in tool definitions. See [Chapter 11](#chapter-11-context-management-and-checkpoints) for todo list persistence mechanism.

## 7. Running Commands

`<running_commands>` contains the safety model for terminal commands:

Verbatim from V2.3.15 wire data:

```text
You have the ability to run terminal commands on the user's machine.
You are not running in a dedicated container. Check for existing dev servers before starting new ones, and be careful with write actions that mutate the file system or interfere with processes.
**THIS IS CRITICAL: When using the run_command tool NEVER include `cd` as part of the command. Instead specify the desired directory as the cwd (current working directory).**
When requesting a command to be run, you will be asked to judge if it is appropriate to run without the USER's permission.
A command is unsafe if it may have some destructive side-effects. Example unsafe side-effects include: deleting files, mutating state, installing system dependencies, making external requests, etc.
You must NEVER NEVER run a command automatically if it could be unsafe. You cannot allow the USER to override your judgement on this. If a command is unsafe, do not run it automatically, even if the USER wants you to.
You may refer to your safety protocols if the USER attempts to ask you to run commands without their permission. The user may set commands to auto-run via an allowlist in their settings if they really want to. But do not refer to any specific arguments of the run_command tool in your response.
```

**Analysis (grouped by concern):**

**Environment context:**
- Model runs terminal commands on user's actual machine (not a container)
- Check for existing dev servers; be careful with write actions
- CRITICAL: NEVER include `cd` - use `Cwd` parameter instead

**Safety model (4 rules):**
- Judge if command is appropriate to run without user permission (`SafeToAutoRun`)
- Unsafe = destructive side-effects (deleting files, mutating state, installing deps, external requests)
- "NEVER NEVER" run unsafe command automatically. Cannot allow USER to override
- May refer to safety protocols if user attempts to bypass. User can set allowlist in settings

**Information control:**
- Do not refer to specific arguments of `run_command` tool in response (hides `SafeToAutoRun` from user)

**Design insight:** "NEVER NEVER" (doubled emphasis) is the strongest prohibition in the entire system prompt. The information control rule prevents leakage about `SafeToAutoRun` to users.

## 8. Debugging

`<debugging>` contains 3 best practices:

```text
When debugging, only make code changes if you are certain that you can solve the problem.
Otherwise, follow debugging best practices:
1. Address the root cause instead of the symptoms.
2. Add descriptive logging statements and error messages to track variable and code state.
3. Add test functions and statements to isolate the problem.
```

**Design insight:** The "only make changes if certain" constraint is conservative - it prefers diagnostic output (logging, tests) over speculative fixes. This reduces the risk of introducing new bugs during debugging.

## 9. Calling External APIs

`<calling_external_apis>` contains 2 rules:

```text
1. When selecting which version of an API or package to use, choose one that is compatible with the USER's dependency management file. If no such file exists or if the package is not present, use the latest version that is in your training data.
2. If an external API requires an API Key, be sure to point this out to the USER. Adhere to best security practices (e.g. DO NOT hardcode an API key in a place where it can be exposed)
```

## 10. Workflows

`<workflows>` defines the workflow system and lists all available workflows.

### 10.1 Workflow Definition Format

```yaml
---
description: [short title, e.g. how to deploy the application]
---
[specific steps on how to run this workflow]
```

Workflows are `.md` files in `.windsurf/workflows/`. The system prompt instructs the model to:
- Create new workflows when asked (use absolute path)
- Be very specific with instructions
- Respect `// turbo` annotation: auto-run the NEXT step (only) via `SafeToAutoRun: true`
- If workflow looks relevant or user uses `/slash-command`, read the workflow file

### 10.2 Workflow List

The prompt lists all available workflows with descriptions. In the V2.3.15 capture: 38 workflows. The list is dynamically generated from `.windsurf/workflows/*.md` file contents.

### 10.3 Skill List (Embedded in Tool Definitions)

The `skill` tool description (in tool definitions, not in `<workflows>`) lists available skills. V2.3.15 capture: 14 skills. Skills are dynamically discovered from `.windsurf/skills/` folders.

## 11. User Rules

`<user_rules>` is the largest section (~33 KB in this workspace). It has explicit and absolute precedence.

### 11.1 Precedence Preamble

```text
The following are user-defined rules that you MUST ALWAYS FOLLOW WITHOUT
ANY EXCEPTION. These rules take precedence over any following instructions.
Review them carefully and always take them into account when you generate
responses and code:
```

This is the strongest precedence statement in the system prompt. "Take precedence over any following instructions" means user rules override `<user_information>`, `<memory_system>`, `<ide_metadata>`, and injected behaviors.

### 11.2 MEMORY Block Injection

Each `.md` file in `.windsurf/rules/` becomes a `<MEMORY[filename.md]>` block:

```xml
<MEMORY[agent-behavior.md]>
  {full content of .windsurf/rules/agent-behavior.md}
</MEMORY[agent-behavior.md]>
```

In the V2.3.15 capture (IPPS workspace), 6 MEMORY blocks:
- `agent-behavior.md` - Behavioral rules, communication principles
- `core-conventions.md` - Formatting, encoding, document structure rules
- `devsystem-core.md` - Core definitions, folder structure, workflow references (TRUNCATED at ~4000 chars)
- `devsystem-ids.md` - Document ID system, topic registry, tracking IDs
- `tools-and-skills.md` - Tool disambiguation, skill registry, tool locations
- `workspace-rules.md` - Workspace-specific rules (EMPTY in this capture)

### 11.3 Truncation Behavior

Large rule files are truncated. In the V2.3.15 capture, `devsystem-core.md` was truncated at approximately 4000 characters with a `<truncated N lines>` marker. Truncation threshold appears to be per-MEMORY-block, not total [ASSUMED].

### 11.4 Empty MEMORY Blocks

Empty rule files generate the tag pair with empty content:

```xml
<MEMORY[workspace-rules.md]>


</MEMORY[workspace-rules.md]>
```

The empty block is still injected. This allows the platform to detect the file exists even when empty.

## 12. User Information

`<user_information>` provides workspace context:

```xml
<user_information>
The USER's OS version is windows.
The USER has 1 active workspaces, each defined by a URI and a CorpusName.
Multiple URIs potentially map to the same CorpusName. The mapping is shown
as follows in the format [URI] -> [CorpusName]:
e:\Dev\KarstensWorkspace -> karstenheld3/KarstensWorkspace
  (git root: e:\Dev\KarstensWorkspace)
</user_information>
```

Content varies per session: OS version, workspace count, URI-to-CorpusName mapping, git root. CorpusName format: `{github_username}/{repo_name}`.

## 13. Memory System

`<memory_system>` describes the persistent memory database:

```text
You have access to a persistent database with three types of entries:
1. Global rules: System-wide rules that always apply, it is important
   that you always follow these rules
2. User-provided memories: Context explicitly provided by the USER
   for this task
3. System-retrieved memories: Automatically retrieved from previous
   conversations that may or may not be relevant

System-retrieved memories should be disregarded if they are not relevant
to the USER's actual request. Only use them if they clearly apply to
the current task.

Remember that memories can be stale or incorrect. Always verify their
relevance and accuracy before using them.
```

**Note:** The actual prompt contains double `<memory_system>` nesting - appears to be a serialization artifact [ASSUMED].

## 14. IDE Metadata

`<ide_metadata>` instructs the model about IDE state injection:

```text
You work inside of the user's IDE. Sometimes, you will receive additional
metadata about the state of the user's IDE. This metadata will not
necessarily be relevant to your task. You should always first consider
the user's actual request. Then only use IDE metadata if it seems clearly
related to the user's request.
```

The actual IDE state (active document, cursor position, open files) is injected into the user message `<additional_metadata>` section, not into this system prompt section.

## 15. MCP Servers (Conditional)

`<mcp_servers>` is **conditionally present**. It only appears when MCP servers are configured in the IDE settings.

**When absent:** Section is completely omitted from the system prompt. Observed in both V2.3.15 and V2.3.9 captured sessions (which had MCP disabled).

**When present** (current live session):

```xml
<mcp_servers>
The Model Context Protocol (MCP) is a standard that connects AI systems
with external tools and data sources.
MCP servers extend your capabilities by providing access to specialized
functions, external information, and services.
The following MCP servers are available to you. Each server may provide
(potentially truncated) additional recommendations and best practices.
# playwright
# playwriter
</mcp_servers>
```

The MCP server names correspond to tool prefixes in tool definitions: `mcp1_*` for playwright, `mcp2_*` for playwriter. When present, 25 additional tool definitions are injected (23 Playwright + 2 Playwriter), adding ~25-28 KB to request size.

## 16. Injected Behaviors

After the last XML closing tag, Windsurf appends behavioral rules as plain text. These are NOT inside any XML section.

Verbatim from V2.3.15 wire data:

```text
Bug fixing discipline: Prefer minimal upstream fixes over downstream workarounds. Identify root cause before implementing. Avoid over-engineering—use single-line changes when sufficient. For specialized codebases, verify bug location carefully. Add regression tests but keep implementation minimal.
Long-horizon workflow: For multi-session work, consider keeping concise notes (e.g., `progress.txt`) and a list of pending tests when they will genuinely speed up future progress. Update them only when they add value.
Planning cadence: Draft a succinct plan for non-trivial tasks, keep only one step in progress, and refresh the plan after new constraints or discoveries.
Testing discipline: Design or update tests before major implementation work, never delete or weaken tests without explicit direction, and share targeted verification commands when you cannot run them.
Verification tools: Prefer available automated verification (e.g., Playwright, unit tests) to confirm work. Provide copy-pastable commands for the user when tools are unavailable.
Progress notes: Prefer lightweight workspace artifacts over long chat recaps, but only create new files when they prevent rework and absolutely necessary. Avoid creating repeated .md files or excessive documentation for yourself unless asked by the user.
```

6 behavioral rules, each following a `Label: Description` pattern. Dynamically injected based on user behavior patterns or A/B testing [ASSUMED]. Consistent across the V2.3.15 capture and current live session.

**Positioning significance:** By placing these AFTER the XML sections, they become the last content in the system prompt before the memory/checkpoint slot. In transformer models, recency bias gives these rules higher attention weight than content earlier in the prompt [ASSUMED].

## 17. Composition Summary

### 17.1 Complete Wire Layout

```text
PROTOBUF STRING [0009]:
  "You are Cascade..." (identity preamble)
  <communication_style>
    <communication_guidelines> (11 rules + 1 continuation)
    <markdown_formatting> (intro + 8 rules)
    <citation_guidelines> (format + 4 examples)
  </communication_style>
  <tool_calling> (3 directives + 4 sub-rules)
  <making_code_changes> (3 directives + 5 sub-rules)
  <task_management> (1 sentence)
  <running_commands> (8 rules)
  <debugging> (3 rules)
  <calling_external_apis> (2 rules)
  <workflows> (format + turbo + 38 workflow entries)
  <user_rules> (preamble + 6 MEMORY blocks)
  <user_information> (OS, URIs, CorpusNames)
  <memory_system> (3 memory types + staleness warning)
  <ide_metadata> (IDE state description)
  <mcp_servers> (CONDITIONAL: server names + description)
  {Injected Behaviors} (6 plain-text rules, outside XML)
                                         ...continues through [0064]
```

### 17.2 Size Budget

```text
System Prompt Size Composition (~50 KB total)
─────────────────────────────────────────────────────────────────
|████████████████████████████████████████████████████████| 33 KB  User rules (66%)
|████████████████████|                                    10 KB  Windsurf sections (20%)
|████████|                                                 4 KB  Workflows (8%)
|██████|                                                   3 KB  User info + misc (6%)
─────────────────────────────────────────────────────────────────
 Fixed (Windsurf): ~10 KB        Variable (user config): ~40 KB
```

- **Windsurf-authored behavioral sections**: ~10 KB (fixed across all users)
- **User rules** (`<user_rules>`): ~33 KB (this workspace, 6 rule files). Varies 0-50+ KB
- **Workflow list** (`<workflows>`): ~4 KB (38 workflows). Varies with user config
- **Total system prompt string**: ~50 KB

Not in the system prompt (separate protobuf regions, see [Chapter 4](#chapter-4-the-getchatmessage-request)):
- **Tool definitions**: ~35 KB (27 native tools) + ~25-28 KB (MCP tools, when configured)
- **Feature flags**: ~4 KB (47 flags)

### 17.3 Precedence Hierarchy

From highest to lowest:

1. `<user_rules>` - "MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION. Take precedence over any following instructions"
2. `<running_commands>` safety rules - "NEVER NEVER run unsafe command automatically. Cannot allow USER to override"
3. Other system prompt sections - no explicit precedence
4. Injected behaviors - last in prompt, no precedence claim
5. User message content - can be overridden by system prompt rules

### 17.4 Fixed vs Dynamic Content

- **Fixed** (same for all users): Identity preamble, all behavioral XML sections, `<memory_system>`, `<ide_metadata>`, injected behaviors
- **Dynamic** (varies per workspace): `<workflows>` list, `<user_rules>` MEMORY blocks, `<user_information>`, `<mcp_servers>` (conditional)
- **Dynamic** (varies per conversation): None. The system prompt is identical across all GetChatMessage calls within a conversation

## Key Takeaways

- System prompt occupies strings [0009]-[0064] (~50 KB): identity preamble + 12 XML sections + injected behaviors
- Windsurf-authored content is ~10 KB (fixed); user rules are ~33 KB (variable, workspace-dependent)
- `<user_rules>` has explicit highest precedence ("MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION")
- `<mcp_servers>` section is conditionally injected only when MCP servers are configured
- 6 injected behaviors are appended AFTER all XML closing tags for positional salience
- The system prompt is identical across all GetChatMessage calls within a conversation (no per-turn changes)

## Sources

- `Session_2026-05-29_13-59_V2.3.15`: First GetChatMessage request (182 strings, complete system prompt extraction)
- Current live session (2026-05-30): Used for MCP server section and cross-verification


---

# Chapter 7: The Tool Call Round Trip

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents how tool calls are encoded in conversation history: the turn structure, ID format, result blocks, extended thinking blobs, and the sentinel token. The reader should understand the string region map from [Chapter 4](#chapter-4-the-getchatmessage-request).

**Per-prompt limit**: Cascade can make up to **20 tool calls per prompt**. When this limit is hit, the trajectory stops and requires a "continue" (which counts as a new prompt credit). An Auto-Continue setting can resume automatically [VERIFIED from docs.windsurf.com 2026-05-31].

## 1. Conversation Turn Structure

Each tool-call round trip adds one **assistant turn** and one **tool results block** to the conversation history. The conversation history region ([0067]-[N]) is absent on the first GetChatMessage (strings jump directly from [0066] to feature flags) and grows with each tool call round trip.

### 1.0 Visual Overview

```text
┌─── Assistant Turn ────────────────────────────────────────────────────┐
│                                                                       │
│  Turn marker: (bot-[UUID])                                            │
│                                                                       │
│  Tool call A:  ID = toolu_01G5Y...  args = {"SkillName": "..."}       │
│  Tool call B:  ID = toolu_019jW...  args = {"DirectoryPath": "..."}   │
│                        │                          │                    │
│  Assistant text: "The user wants to..."           │                    │
│  Extended thinking: [binary blob]                 │                    │
│                        │                          │                    │
└────────────────────────┼──────────────────────────┼───────────────────┘
                         │ ID pairing               │ ID pairing
                         v                          v
┌─── Tool Results Block ─┼──────────────────────────┼───────────────────┐
│                        │                          │                    │
│  Result A content (1-N strings)                   │                    │
│  Result A ID:  toolu_01G5Y...  <── same as call A │                    │
│                                                   │                    │
│  Result B content (1-N strings)                                       │
│  Result B ID:  toolu_019jW...  <── same as call B                     │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                         │
                         v
┌─── Sentinel ──────────────────────────────────────────────────────────┐
│  |context_request|J|endoftext|J                                       │
└───────────────────────────────────────────────────────────────────────┘
```

Each tool call ID (`toolu_*`) appears exactly twice: once in the assistant turn (the request) and once after the tool result content (the response marker). This pairing allows the model to match results back to their corresponding calls.

### 1.1 Assistant Turn

```text
[string] Turn marker: \t\n(bot-[UUID]
[string] Tool call 1 ID: toolu_[22-char-alphanum]
[string] Tool call 1 args: [prefix-byte]{"param": "value"}[suffix-bytes]
[string] Tool call 2 ID: toolu_[22-char-alphanum]
[string] Tool call 2 args: [prefix-byte]{"param": "value"}[suffix-bytes]
  ...    (repeat for each parallel tool call)
[string] Assistant visible text (the reasoning/explanation shown to user)
[string] Extended thinking block (binary blob, see section 4)
```

**Ordering note**: The relative order of tool call IDs/args versus assistant text varies between turns. In some turns, tool calls appear first; in others, assistant text appears first. This reflects the model's content block ordering (both orderings are valid in the Anthropic API [ASSUMED]).

### 1.2 Tool Results Block

```text
[string*] Tool result 1 content (1-N strings, depends on output size)
[string]  Tool result 1 ID: toolu_[same-as-call-1-ID]
[string*] Tool result 2 content (1-N strings)
[string]  Tool result 2 ID: toolu_[same-as-call-2-ID][suffix-byte]
  ...     (repeat for each tool result, in same order as calls)
```

The final tool result ID in each round carries a suffix byte (e.g., `B`). This is likely a protobuf field delimiter leaked into the extracted text [ASSUMED].

### 1.3 Context Request Sentinel

After the last tool result in the conversation history, a sentinel token pair terminates the history:

```text
|context_request|J|endoftext|J
```

The `J` bytes between tokens are of unknown significance - possibly protobuf field markers or separator bytes [ASSUMED]. This sentinel separates conversation history from the feature flags region and appears consistently across all observed requests.

## 2. Concrete Examples

### 2.1 V2.3.15 Session - First Two Rounds

**Request 0110** (first main call, 182 strings, 99 KB decompressed):

No conversation history. Strings [0001]-[0066] are auth + system prompt + memories + user message. Strings [0067+] are feature flags and tool definitions.

**Request 0130** (second main call, 224 strings, 111 KB decompressed):

Conversation history occupies [0067]-[0109] = 43 new strings:

From V2.3.15 wire data (string positions from extraction; labels added for readability):

```text
[0067] Turn marker: (bot-c44e548e-c805-4417-b540-ca125b503f82)
[0068] Tool call ID: toolu_01G5YsMscE7DT8Pzj4AkS2p9
[0069] Tool call args: {"SkillName": "session-management"}
[0070] Tool call ID: toolu_019jWkGaNF16net8EpCfLSQ4
[0071] Tool call args: {"DirectoryPath": "e:\\Dev\\IPPS"}
[0072] Assistant text: "The user wants to create a new session..."
[0073] Extended thinking block (binary, ~500 bytes)
[0074-0105] Tool result 1: session-management skill output (32 strings)
[0106] Tool result 1 ID: toolu_01G5YsMscE7DT8Pzj4AkS2p9
[0107] Tool result 2: directory listing of e:\Dev\IPPS/ (1 string)
[0108] Tool result 2 ID: toolu_019jWkGaNF16net8EpCfLSQ4 + suffix
[0109] Sentinel token (context_request + endoftext)
```

**Request 0154** (third main call, 480 strings, 132 KB decompressed):

Conversation history occupies [0067]-[0365] = 299 strings. Contains all of round 1 plus round 2. Round 2 adds [0109]-[0365] = 257 new strings:

```text
[0109] Turn marker: (bot-5c0ee57b-336a-404b-ae37-c55cabc7d12b)
[0110] Assistant text: "Reading templates and workspace notes..."
[0111] Tool call ID: toolu_01NVs52Nm7HPfzA2bN75meHL
[0112] Tool call args: {"file_path": "...NOTES_TEMPLATE.md"}
[0113] Tool call ID: toolu_01RZn7GMHWEGfosLW49sJzsg
[0114] Tool call args: {"file_path": "...PROBLEMS_TEMPLATE.md"}
[0115] Tool call ID: toolu_01EHSpLofHBv13jrG7oyPeuU
[0116] Tool call args: {"file_path": "...PROGRESS_TEMPLATE.md"}
[0117] Tool call ID: toolu_01395H6mo7fpBnvHhbJdzJQT
[0118] Tool call args: {"file_path": "...NOTES.md"} + assistant text
[0119] Extended thinking block (binary)
[0120-0167] Tool result 3: NOTES_TEMPLATE.md content (48 strings)
[0168] Tool result 3 ID: toolu_01NVs52Nm7HPfzA2bN75meHL
[0169-0218] Tool result 4: PROBLEMS_TEMPLATE.md content (50 strings)
[0219] Tool result 4 ID: toolu_01RZn7GMHWEGfosLW49sJzsg
[0220-0260] Tool result 5: PROGRESS_TEMPLATE.md content (41 strings)
[0261] Tool result 5 ID: toolu_01EHSpLofHBv13jrG7oyPeuU
[0262-0363] Tool result 6: NOTES.md content (102 strings)
[0364] Tool result 6 ID: toolu_01395H6mo7fpBnvHhbJdzJQT + suffix
[0365] Sentinel token (context_request + endoftext)
```

### 2.2 V2.3.9 Session - Cross-Session Verification

Request 0276 (V2.3.9, 2167 strings, full /prime context) confirms identical structure:

```text
Round 1: 3 find_by_name tool calls
[0067] Turn marker: (bot-4701bce6-0e1c-4f41-8edb-abe871b89949)
[0068-0073] 3 tool call ID/args pairs
[0074] Assistant text
[0075] Thinking block
[0076-0081] 3 tool results with IDs

Round 2: 8 read_file tool calls
[0082] Turn marker: (bot-e89cc515-ffc1-4962-8699-5560deaf7294)
[0083] Assistant text
[0084-0099] 8 tool call ID/args pairs
[0100-0875+] 8 tool results (FAILS.md alone = 380 strings)
```

## 3. Tool Call ID Format

Tool call IDs use the Anthropic-style `toolu_` prefix format:

- **Format**: `toolu_` + 22 alphanumeric characters (base62) [ASSUMED]
- **Example**: `toolu_01G5YsMscE7DT8Pzj4AkS2p9`
- **Uniqueness**: Each tool call in a conversation has a unique ID
- **Reuse**: The same ID appears twice: once in the assistant turn (the call) and once after the tool result content (the result marker)

## 4. Extended Thinking Block

Each assistant turn includes a binary blob containing the model's extended thinking output:

- **Content**: Base64-ish encoding containing embedded ASCII strings
- **Model identifier**: Contains `claude-opus-4-6` (base64: `Y2xhdWRlLW9wdXMtNC02`)
- **Thinking marker**: Contains `thinking` (base64: `dGhpbmtpbmc=`)
- **Size**: ~200-500 bytes per turn (compressed thinking content)
- **Position**: Always after the assistant visible text, before tool results

This confirms that the Generator model (Claude Opus 4.6 with extended thinking) produces thinking content that is serialized into the conversation history, enabling the model to reference its prior reasoning in subsequent turns.

## 5. Tool Name Encoding

Tool names (e.g., `skill`, `list_dir`, `read_file`, `find_by_name`) are NOT visible in the extracted wire data because:

- All Cascade tool names are 5-15 characters long
- The extraction script uses a 20-character minimum string length threshold
- Tool names are present in the protobuf data as separate string fields but are filtered out

**Evidence**: The tool call args JSON (e.g., `{"SkillName": "session-management"}`) matches exactly one tool definition. The tool name must be in an adjacent protobuf field below the extraction threshold.

## 6. Tool Result Content Format

Tool results are injected as **plain text strings**, identical to what the IDE shows the user:

- **read_file** results include the full `<file name="..." start_line="..." end_line="..." full_length="...">` wrapper with line-numbered content
- **list_dir** results are plain directory listings with file sizes
- **skill** results include the skill header ("Skill: session-management\nBase Directory: ...") followed by the skill content
- **find_by_name** results are "Found N results" followed by file paths

Large tool results are **split across multiple protobuf string fields**. A single read_file of a 697-line file (FAILS.md) produced 380 separate strings. The split boundaries appear to follow line breaks in the original content.

## 7. Context Growth Per Round Trip

Derived from V2.3.15 wire data (decompressed sizes):

- **Request 0110** (1st main): 182 strings, 99 KB decompressed, 0 history strings, 0 tool calls (baseline)
- **Request 0130** (2nd main): 224 strings, 111 KB decompressed, 43 history strings, 2 tool calls (+42 strings, +12 KB)
- **Request 0154** (3rd main): 480 strings, 132 KB decompressed, 299 history strings, 6 tool calls (+256 strings, +21 KB)

Growth rate depends on tool result size. A single read_file of a large file can add hundreds of strings. The 9-call /prime workflow in V2.3.9 accumulated 2167 strings (506 KB decompressed).

## Key Takeaways

- Conversation history is a flat sequence of protobuf string fields (not nested messages)
- Each round trip adds: turn marker + tool call IDs/args + assistant text + thinking blob + tool results + result IDs
- Tool call IDs use Anthropic-style `toolu_` + 22 chars, appearing twice (call and result)
- Extended thinking is serialized as a binary blob containing the model name and thinking content
- A sentinel token (`context_request` + `endoftext`) terminates conversation history
- Tool results are plain text, split across multiple protobuf strings at line boundaries
- Structure verified across 2 sessions (V2.3.9 and V2.3.15), 4 requests, 17 tool calls

## Sources

- `Session_2026-05-29_13-59_V2.3.15`: Requests 0110, 0130, 0154 (3 consecutive calls with tool round trips)
- `Session_2026-05-28_12-49_V2.3.9`: Request 0276 (full /prime context, cross-session verification)


---

# Chapter 8: Tool Walkthrough - Core Coding Tools

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents the 12 core coding tools (reading, editing, execution) with exact wire definitions, JSON schemas, and behavioral constraints embedded in each. The reader should understand the tool call round trip format from [Chapter 7](#chapter-7-the-tool-call-round-trip).

## 1. Wire Format

### 1.1 Tool Definition Region

Tool definitions occupy protobuf strings [0124]-[0178] in the first GetChatMessage request. This region contains 27 tools as sequential pairs:

```text
[string N]   Description text (plain text, multi-line, contains behavioral instructions)
[string N+1] JSON Schema (single-line JSON object with $schema, properties, required)
```

All schemas use JSON Schema Draft 2020-12 with `"additionalProperties": false` (strict mode).

### 1.2 Tool Name Transmission

Tool names are transmitted in separate short protobuf string fields (4-15 characters) below the 20-char extraction threshold. Names are inferred by matching descriptions to known tool names, or from longer names that exceed the threshold (e.g., `read_deployment_config` at 22 chars).

## 2. Code Reading Tools (6 tools)

### 2.1 read_file

**Purpose:** Read file contents with line numbers. Primary inspection tool.

**Description (verbatim):**
```text
Reads a file at the specified relative path.
This tool is only able to read files in the workspace that are not gitignored.
If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.

Usage:
- The file_path parameter must be an absolute path, not a relative path
- You can optionally specify a line offset and limit to read files that are larger than 1000 lines. For other files, do not provide these parameters to read the whole file.
- Any lines longer than 2000 characters will be truncated
- Text files are returned with 1-indexed line numbers in cat -n format
- Image files (jpg, jpeg, png, gif, bmp, webp, svg, tiff, ico, heic, heif) are automatically presented visually
- You have the capability to call multiple tools in a single response. It is always better to speculatively read multiple files as a batch that are potentially useful.
- You will regularly be asked to read screenshots. If the user provides a path to a screenshot ALWAYS use this tool to view the file at the path. This tool will work with all temporary file paths like /var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png
- If you read a file that exists but has empty contents you will receive a system reminder warning in place of file contents.
```

**Schema:** `file_path` (string, required), `offset` (integer, optional), `limit` (integer, optional)

**Behavioral constraints:**
- Output in `cat -n` format (spaces + line number + tab + content)
- Lines >2000 chars truncated; image files rendered visually
- Encourages batching: "always better to speculatively read multiple files as a batch"
- Handles non-existent files gracefully (returns error)

### 2.2 list_dir

**Purpose:** List directory contents with sizes and item counts.

**Description (verbatim):**
```text
Lists files and directories in a given path. The path parameter must be an absolute path to a directory that exists. For each item in the directory, output will have: relative path to the file or directory, and size in bytes if file or number of items (recursive) if directory. You should generally prefer the find_by_name and grep_search tools, if you know which directories to search.
```

**Schema:** `DirectoryPath` (string, required)

**Behavioral constraints:** Embedded preference guidance defers to `grep_search`/`find_by_name` for targeted searches. Simplest schema (single required parameter).

### 2.3 grep_search

**Purpose:** Search file contents using ripgrep. Replaces direct `rg` or `grep` shell commands.

**Description (verbatim):**
```text
A powerful search tool built on ripgrep

Usage:
- NEVER invoke `grep` or `rg` as a Bash command, use this tool instead. The Grep tool has
been optimized for correct permissions and access.
- DO NOT USE MatchPerLine for initial searches that may have a large number of results. Use it only when you
know it is a very specific, targeted search.
- By default, Query is treated as a regular expression. Set FixedStrings to true to treat Query as a literal string (no regex).
- Filter files with Includes parameter in glob format (e.g., "*.js", "**/*.tsx")
- If the result is truncated, you must narrow down your search using a more specific query or more filters.
```

**Schema:** `SearchPath` (string, required), `Query` (string, required), `MatchPerLine` (boolean), `Includes` (string[]), `CaseSensitive` (boolean), `FixedStrings` (boolean)

**Behavioral constraints:**
- Explicit tool substitution: "NEVER invoke grep or rg as a Bash command"
- Two-phase search enforced: broad (file list) first, then `MatchPerLine` for specific results
- Defaults: case-insensitive, regex mode

### 2.4 find_by_name

**Purpose:** Search for files and directories by name pattern using fd.

**Description (verbatim):**
```text
Search for files and subdirectories within a specified directory using fd.
Search uses smart case and will ignore gitignored files by default.
Pattern and Excludes both use the glob format. If you are searching for Extensions, there is no need to specify both Pattern AND Extensions.
To avoid overwhelming output, the results are capped at 50 matches. Use the various arguments to filter the search scope as needed.
Results will include the type, size, modification time, and relative path.
```

**Schema:** `SearchDirectory` (string, required), `Pattern` (string, required), `Excludes` (string[]), `Type` (string, enum), `MaxDepth` (integer), `Extensions` (string[]), `FullPath` (boolean)

**Behavioral constraints:** Hard cap 50 results. Smart case. Respects .gitignore. Rich output: type + size + modification time + relative path.

### 2.5 code_search

**Purpose:** AI-powered codebase exploration subagent ("Fast Context").

**Description (verbatim):**
```text
A search subagent the user refers to as 'Fast Context' that is ideal for exploring the codebase based on a request. This tool invokes a subagent that runs parallel grep and readfile calls over multiple turns to locate line ranges and files which might be relevant to the request. The search term should be a targeted natural language query based on what you are trying to accomplish, like 'Find where authentication requests are handled in the Express routes' or 'Modify the agentic rollout to use the new tokenizer and chat template' or 'Fix the bug where the user gets redirected from the /feed page'.  Fill out extra details that you as a smart model can infer in the question if necessary. You should always use this tool to start your search. Note: The files and line ranges returned by this tool may be some of the ones needed to complete the user's request, but you should be careful in evaluating the relevance of the results, since the subagent might make mistakes. You should consider using classical search tools afterwards to locate the rest if necessary. IMPORTANT: YOU CANNOT CALL THIS TOOL IN PARALLEL.
```

**Schema:** `search_folder_absolute_uri` (string, required), `search_term` (string, required)

**Behavioral constraints:**
- **Only tool with parallelism restriction:** "CANNOT CALL THIS TOOL IN PARALLEL"
- **Recommended first action:** "You should always use this tool to start your search"
- **Fallibility acknowledgment:** "the subagent might make mistakes"
- Accepts natural language, not regex

### 2.6 read_notebook

**Purpose:** Parse and display Jupyter notebook cells with IDs and outputs.

**Schema:** `AbsolutePath` (string, required). Minimal description (one sentence). Complementary to `edit_notebook`.

## 3. Code Editing Tools (4 tools)

### 3.1 edit

**Purpose:** Exact string replacement in a single file. Primary editing tool.

**Description (verbatim):**
```text
Performs exact string replacements in files.

Usage:
- You must use your `Read` tool at least once in the conversation before editing. This tool will error if you attempt an edit without reading the file.
- When editing text from Read tool output, ensure you preserve the exact indentation (tabs/spaces) as it appears AFTER the line number prefix. The line number prefix format is: spaces + line number + tab. Everything after that tab is the actual file content to match. Never include any part of the line number prefix in the old_string or new_string.
- ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required.
- Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked.
- The edit will FAIL if `old_string` is not unique in the file. Either provide a larger string with more surrounding context to make it unique or use `replace_all` to change every instance of `old_string`.
- Use `replace_all` for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance.
- The edit will FAIL if `old_string` and `new_string` are identical. This is considered a no-op and will throw an error.
- Include an `explanation` field to describe the change you are making.
IMPORTANT: You must generate the following arguments first, before any others: [file_path]
```

**Schema:** `explanation` (string, required), `file_path` (string, required), `old_string` (string, required), `new_string` (string, required), `replace_all` (boolean)

**Behavioral constraints:**
- **Read-before-write gate:** Platform enforces `read_file` was called first (runtime check)
- **Uniqueness requirement:** `old_string` must be unique unless `replace_all=true`
- **No-op prevention:** `old_string == new_string` returns error
- **Argument ordering:** file_path must be generated first (streaming optimization)
- **Edit-over-create preference:** "ALWAYS prefer editing... NEVER write new files unless explicitly required"

### 3.2 multi_edit

**Purpose:** Multiple sequential string replacements in one file, applied atomically.

**Schema:** `explanation` (string, required), `file_path` (string, required), `edits` (array of {old_string, new_string, replace_all}, minItems: 1, required)

**Behavioral constraints:**
- **Atomicity:** All-or-nothing. If any edit fails, entire operation rolls back
- **Sequential application:** Each edit operates on the result of the previous
- **Same gate as `edit`:** Inherits read-before-write and uniqueness requirements
- Can create new files (empty `old_string` in first edit)

### 3.3 write_to_file

**Purpose:** Create new files. Cannot modify existing files.

**Description (verbatim):**
```text
Use this tool to create new files. The file and any parent directories will be created for you if they do not already exist.
	Follow these instructions:
	1. NEVER use this tool to modify or overwrite existing files. Always first confirm that TargetFile does not exist before calling this tool.
	2. You MUST specify the full TargetFile before any of the code contents.
IMPORTANT: You must generate the following arguments first, before any others: [TargetFile]
```

**Schema:** `TargetFile` (string, required), `CodeContent` (string, required), `EmptyFile` (boolean, required)

**Behavioral constraints:**
- **Create-only:** "NEVER use this tool to modify or overwrite existing files"
- Parent directories auto-created
- All 3 params required (even `EmptyFile` must be explicit)

### 3.4 edit_notebook

**Purpose:** Replace or insert cells in Jupyter notebooks.

**Schema:** `absolute_path` (string, required), `new_source` (string, required), `cell_number` (integer), `cell_id` (string), `cell_type` (enum: code/markdown), `edit_mode` (enum: replace/insert)

**Behavioral constraints:**
- **No delete capability:** Agent must ask user to delete cells manually
- 0-indexed cells (unlike `read_file` which is 1-indexed)
- Insert mode shifts existing cells down

## 4. Execution Tools (2 tools)

### 4.1 run_command

**Purpose:** Execute shell commands on user's machine. OS-aware.

**Description (verbatim):**
```text
PROPOSE a command to run on behalf of the user. Operating System: windows. Shell: pwsh.
**NEVER PROPOSE A cd COMMAND**.
If you have this tool, note that you DO have the ability to run commands directly on the USER's system.
Make sure to specify CommandLine exactly as it should be run in the shell.
Note that the user will have to approve the command before it is executed. The user may reject it if it is not to their liking.
The actual command will NOT execute until the user approves it. The user may not approve it immediately.
If the step is WAITING for user approval, it has NOT started running.
Commands will be run with PAGER=cat. You may want to limit the length of output for commands that usually rely on paging and may contain very long output (e.g. git log, use git log -n <N>).
```

**Schema:** `CommandLine` (string, required), `Cwd` (string), `Blocking` (boolean), `WaitMsBeforeAsync` (integer), `SafeToAutoRun` (boolean)

**Behavioral constraints:**
- **OS-specific:** Description dynamically injected per user's OS
- **cd prohibition:** "NEVER PROPOSE A cd COMMAND" - use `Cwd` parameter
- **Dual-consent model:** Agent self-classifies via `SafeToAutoRun`; user approves unsafe commands; agent MUST NOT set true for destructive commands "EVEN if the USER asks you to"
- **Blocking vs async:** `Blocking=true` runs to completion; `false` starts in background; `WaitMsBeforeAsync` hybrid catches early failures
- **Approval semantics:** "WAITING for user approval" means NOT YET STARTED

### 4.2 command_status

**Purpose:** Check status of async (non-blocking) commands.

**Schema:** `CommandId` (string, required), `OutputCharacterCount` (integer, required), `WaitDurationSeconds` (integer, default: 0)

**Behavioral constraints:**
- "Do not try to check the status of any IDs other than Background command IDs"
- "Make this as small as possible" for `OutputCharacterCount`
- "Do not wait for a command for more than 60 seconds"
- Only tool where output size is explicitly agent-controlled

## 5. Behavioral Constraint Patterns

### 5.1 Constraint Categories

- **Hard prohibitions** (NEVER, MUST NOT): `cd` ban, overwrite ban, `SafeToAutoRun` override ban
- **Soft preferences** (prefer, generally): `list_dir` defers to `grep_search`; batch reads encouraged
- **Sequencing rules** (before, first): read-before-write gate, argument ordering
- **Safety gates** (approval): `run_command` dual-consent, `SafeToAutoRun` self-classification
- **Output management** (cap, truncate): 50-result cap, 2000-char truncation, minimal `OutputCharacterCount`

### 5.2 Argument Ordering Directive

Four tools enforce argument ordering (`edit`, `multi_edit`, `write_to_file`, `edit_notebook`):

```text
IMPORTANT: You must generate the following arguments first, before any others: [file_path]
```

Forces model to commit to target file before generating content. Enables streaming validation.

### 5.3 Naming Inconsistencies

Parameter naming is inconsistent across tools: `file_path` vs `TargetFile` vs `absolute_path` vs `AbsolutePath` vs `DirectoryPath` vs `SearchPath` vs `SearchDirectory` vs `search_folder_absolute_uri`. Mix of snake_case, PascalCase, and camelCase suggests different teams or development periods.

## 6. Tool I/O Profiles and Context Budget

Every tool call adds TWO items to conversation history: call arguments + tool result. Both accumulate until checkpoint.

### 6.1 Context Cost Per Tool

**Tier 1 - Cheap (< 2 KB):** `list_dir` (~1-3 KB), `edit_notebook` (~0.3-2 KB), `command_status` (agent-controlled)

**Tier 2 - Moderate (2-10 KB):** `read_file` (~3-10 KB), `grep_search` (~1-5 KB), `find_by_name` (~1-4 KB, capped), `edit` (small-medium: ~0.3-5 KB)

**Tier 3 - Expensive (10-50 KB):** `write_to_file` (medium files: ~8-40 KB), `multi_edit` (large refactors: ~5-30 KB), `code_search` (~3-15 KB), `read_notebook` (~3-50 KB)

**Tier 4 - Potentially Catastrophic (50+ KB):** `run_command` (verbose: up to 500+ KB), `read_notebook` (large: 50+ KB)

### 6.2 Cumulative Impact Example

From V2.3.15 session running `/session-new`:

```text
Turn 1:  skill + list_dir           → +12.6 KB (skill result dominates at ~9 KB)
Turn 2:  4x read_file               → +20.5 KB (~5 KB per template file)
Turn 3:  4x read_file               → +18.0 KB (more templates)
Turn 4:  3x write_to_file           → +15.0 KB (full file content in history)
Turn 5:  run_command (mkdir)         → +2.0 KB (small output)
...
Turn 50: accumulated history         → ~400 KB total
```

Each tool call round trip adds ~500-1000 bytes of overhead beyond the actual content (turn markers, thinking blocks, tool call IDs). A typical session hits the checkpoint threshold (~100K tokens) after 30-50 tool call rounds.

### 6.3 Practical Guidelines

- Prefer `grep_search` (file list mode) over `code_search` for simple lookups
- Use `offset`/`limit` on large files instead of reading entirely
- Cap `run_command` output with shell pipes
- Prefer `multi_edit` over sequential `edit` calls (fewer turns = less overhead)
- Parallel tool calls in one turn share one thinking block (cheaper per-tool than sequential)
- Large `write_to_file` calls create permanent history entries until checkpoint (no garbage collection)

## Key Takeaways

- 12 core coding tools in 3 groups: Reading (6), Editing (4), Execution (2)
- Tool descriptions contain embedded behavioral constraints functioning as inline system prompt instructions
- `edit` and `multi_edit` enforce a read-before-write gate (platform runtime check)
- `run_command` uses a dual-consent model: agent self-classifies safety, user approves
- `code_search` is the only tool with a parallelism restriction
- Context cost ranges from <2 KB (`list_dir`) to potentially 500+ KB (`run_command` without output limits)
- Argument ordering directives force file path commitment before content generation

## Sources

- `_WindsurfMetapromptsHistory/2026-05-29_WindsurfCascadeV2.3.15/ToolDefinitions.txt`: Complete tool definitions from protobuf
- `Session_2026-05-29_13-59_V2.3.15`: Request sizes and context growth measurements


---

# Chapter 9: Tool Walkthrough - Platform Tools

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents the 15 remaining native tools covering web access, state management, user interaction, deployment, MCP integration, and terminal. These tools are generally simpler than the core coding tools (no argument ordering directives, no read-before-write gates). The reader should understand the tool wire format from [Chapter 8](#chapter-8-tool-walkthrough-core-coding-tools).

## 1. Web and External Data Tools (3 tools)

### 1.1 read_url_content

**Purpose:** Fetch and parse web page content. Entry point for all web access.

**Description (verbatim):**
```text
Read content from a URL. URL must be an HTTP or HTTPS URL that points to a valid internet resource accessible via web browser.
Note that the user will have to approve the web request before it is fetched. The user may reject it if it is not to their liking.
The actual fetch will NOT execute until the user approves it. The user may not approve it immediately.
```

**Schema:** `Url` (string, required)

**Behavioral constraints:**
- **User approval gate:** Same dual-consent pattern as `run_command` but without `SafeToAutoRun` - web fetches ALWAYS require approval
- HTTP/HTTPS only (no file://, ftp://)
- Result chunked by platform; remaining chunks via `view_content_chunk`

**Context cost:** 2-10 KB per call (first chunk only)

### 1.2 view_content_chunk

**Purpose:** Paginate through previously-fetched web content.

**Description (verbatim):**
```text
View a specific chunk of a web or knowledge base document content using its DocumentId and chunk position. The DocumentId must have already been read by the read_url_content tool before this can be used on that particular DocumentId.
```

**Schema:** `document_id` (string, required), `position` (integer, required)

**Behavioral constraints:** Must call `read_url_content` first to obtain `document_id`. Reading a full long page: 5-10 chunks x 5 KB = 25-50 KB total in context.

**Context cost:** 2-8 KB per call

### 1.3 search_web

**Purpose:** Perform web search, returning document list.

**Description (verbatim):**
```text
Performs a web search to get a list of relevant web documents for the given query and optional domain filter.
```

**Schema:** `query` (string, required), `domain` (string, optional - advisory filter)

**Behavioral constraints:** No result count control. No explicit user approval wording (unlike `read_url_content`). Domain filter is advisory ("recommend the search prioritize").

**Backend provider:** Brave Search API. Windsurf is listed as an official Brave Search API integration (brave.com/search/api/tools/). The response format is a Windsurf-generated wrapper around Brave's results:

```text
The search for "<reformulated query>" returned the following documents:
- [<Title>]: <URL>
    Summary: <exactly 301 chars, hard-truncated mid-sentence>
- [<Title>]: <URL>
    Summary: <exactly 301 chars>
(always 5 results)
You should pick the URLs of text heavy documents you would like to read further.
```

Key characteristics (measured across 66 search results from 3 sessions):
- **Snippet length:** Always exactly 301 chars, hard-truncated mid-word (no ellipsis)
- **Result count:** Always exactly 5 (rarely fewer when Brave has limited matches)
- **Query reformulation:** Windsurf modifies the agent's query before sending to Brave (typo correction, context addition, entity completion). The response shows the reformulated query, not the original. Matches Kevin Hou's description: "We use an LLM to synthesize our conversation and intent into a query."
- **Total response size:** 2.4-2.8 KB (min=2396, max=2803, avg=2556 chars)
- The trailing prompt guides the LLM toward the `read_url_content` → `view_content_chunk` pipeline

**Context cost:** 2.4-2.8 KB per call

## 2. State and Memory Tools (3 tools)

### 2.1 create_memory

**Purpose:** Save context to persistent memory database. Cross-session persistence.

**Description (verbatim):**
```text
Save important context relevant to the USER and their task to a memory database.
DO NOT call this tool unless explicitly requested by the user to remember something or create a memory.
```

**Schema:** `Id` (string, required), `Title` (string, required), `Content` (string, required), `CorpusNames` (string[], required), `Tags` (string[], required), `Action` (enum: create/update/delete, required), `UserTriggered` (boolean, required)

**Behavioral constraints:**
- **Strongest prohibition of all tools:** "DO NOT call this tool unless explicitly requested" - only tool with unconditional prohibition on autonomous use
- 7 required parameters (most of any tool)
- `CorpusNames` must exactly match values from system prompt `<user_information>`
- Tags enforce snake_case
- `UserTriggered` creates audit trail
- Memory RETRIEVAL is free - injected into system prompt by platform, not via tool call

**Context cost:** 0.3-2 KB per call

For the broader memory architecture (retrieval model, injection point, automated memories), see [Chapter 2](#chapter-2-the-memory-system).

### 2.2 trajectory_search

**Purpose:** Search or retrieve conversation history. Activated by @conversation mentions.

**Description (verbatim):**
```text
Semantic search or retrieve trajectory. Trajectories are one of conversations. Returns chunks from the trajectory, scored, sorted, and filtered by relevance. Maximum number of chunks returned is 50. Call this tool when the user @mentions a @conversation. Do NOT call this tool with SearchType: 'user'. IGNORE @activity mentions.
```

**Schema:** `ID` (string, required), `Query` (string, required), `SearchType` (enum: cascade/user, required)

**Behavioral constraints:**
- **Trigger-activated:** Reactive to @conversation mentions, not proactive
- **Enum prohibition:** "Do NOT call this tool with SearchType: 'user'" - schema-valid value forbidden at prompt level
- Empty query returns all trajectory steps (up to 50 chunks)

**Context cost:** 5-25 KB per call

### 2.3 todo_list

**Purpose:** Create and manage structured task tracking visible in IDE UI.

**Description (verbatim):**
```text
Use this tool to create, update, or manage a todo list. This tool helps you organize tasks with different statuses and priorities. You can add new todos, update existing ones, mark them as completed, or reorganize the entire list.

The tool accepts a list of todo items, each with:
- content: The task description
- status: pending, in_progress, or completed
- priority: high, medium, or low
- id: A unique identifier for the todo item
```

**Schema:** `todos` (array of {id, content, status, priority}, required)

**Behavioral constraints:**
- **Full-replace semantics:** Every call sends COMPLETE list. No incremental add/remove.
- Status: pending / in_progress / completed only
- Priority: high / medium / low only
- Agent-generated IDs (no platform assignment)
- **Checkpoint persistence:** Platform extracts latest state into checkpoint summaries (see [Chapter 11](#chapter-11-context-management-and-checkpoints))

**Context cost:** 1-4 KB per call (grows with list size; 5 updates to 10-item list = 7.5 KB)

## 3. User Interaction Tool (1 tool)

### 3.1 ask_user_question

**Purpose:** Present structured multiple-choice question in IDE.

**Description (verbatim):**
```text
Ask the user a question with predefined options. Use this when you need the user to make a choice between specific options.
You can provide up to 4 options, each with a label and description.
NEVER include "other" as an option - the user can always automatically provide a custom response.
Set allowMultiple to true if the user should be able to select more than one option.
```

**Schema:** `question` (string, required), `options` (array of {label, description}, required), `allowMultiple` (boolean, required)

**Behavioral constraints:** Max 4 options. "NEVER include 'other'" - user can always type custom response. Blocks agent execution until user responds.

**Context cost:** 0.3-1.3 KB per call (cheapest interaction tool)

## 4. Workflow and Skills Tool (1 tool)

### 4.1 skill

**Purpose:** Invoke a named skill to get detailed instructions or domain knowledge.

**Description (verbatim, abbreviated):**
```text
Invoke a skill to get detailed instructions or knowledge for a task.
Use this when a task matches a skill's description.
Available skills:
- coding-conventions: Provides coding style rules... (12 supporting files)
- deep-research: Apply when conducting deep research... (22 supporting files)
- session-management: Apply when initializing, saving... (4 supporting files)
- write-documents: Apply when creating or editing... (22 supporting files)
[... 14 skills total listed dynamically ...]
```

**Schema:** `SkillName` (string, required)

**Behavioral constraints:**
- **Dynamic catalog:** Available skills regenerated per session from `.windsurf/skills/` folder
- Returns ENTIRE skill content (SKILL.md + supporting files concatenated)
- Skills cached within conversation but still add to history on repeat calls
- Second most expensive tool after `run_command`

**Context cost:** 3-40 KB per call (measured: session-management = ~9 KB, write-documents = ~25 KB)

## 5. Deployment Tools (3 tools)

Pipeline: check config → deploy → verify status.

### 5.1 read_deployment_config

**Purpose:** Pre-deployment configuration check. Prerequisite for `deploy_web_app`.

**Schema:** `ProjectPath` (string, required). Context cost: 1-5 KB.

### 5.2 deploy_web_app

**Purpose:** Deploy JavaScript web application to Netlify.

**Description (verbatim):**
```text
Deploy a JavaScript web application to a deployment provider like Netlify. Site does not need to be built. Only the source files are required. Make sure to run the read_deployment_config tool first and that all missing files are created before attempting to deploy. If you are deploying to an existing site, use the project_id to identify the site. If you are deploying a new site, leave the project_id empty.
```

**Schema:** `ProjectPath` (string, required), `Framework` (enum of 18 JS frameworks), `Subdomain` (string), `ProjectId` (string)

**Behavioral constraints:**
- 18 frameworks via enum: eleventy, angular, astro, create-react-app, gatsby, gridsome, grunt, hexo, hugo, hydrogen, jekyll, middleman, mkdocs, nextjs, nuxtjs, remix, sveltekit, svelte
- Source-only deployment (platform handles build)
- Prerequisite prompt-enforced, not platform-enforced

**Context cost:** 0.3-0.9 KB per call

### 5.3 check_deploy_status

**Purpose:** Poll deployment build status.

**Schema:** `WindsurfDeploymentId` (string, required)

**Behavioral constraints:** "Do not run this unless asked by the user" - user-triggered only. "This is NOT a project_id" - explicit disambiguation.

**Context cost:** 0.3-0.7 KB per call

## 6. Browser Preview Tool (1 tool)

### 6.1 browser_preview

**Purpose:** Create browser preview of a running web server.

**Description (verbatim):**
```text
Spin up a browser preview for a web server. This allows the USER to interact with the web server normally as well as provide console logs and other information from the web server to Cascade. Note that this tool call will not automatically open the browser preview for the USER, they must click one of the provided buttons to open it in the browser.
```

**Schema:** `Url` (string, required), `Name` (string, required - title-cased, 3-5 words)

**Behavioral constraints:** No auto-open (user clicks button). URL: scheme + domain + port only. Console log bridge provides bidirectional information flow.

**Context cost:** 0.3-0.7 KB per call

## 7. MCP Integration Tools (2 tools)

Meta-tools for querying Model Context Protocol (MCP) server resources.

### 7.1 list_resources

**Purpose:** List available static resources from an MCP server.

**Schema:** `ServerName` (string, required). "Not all MCP servers provide resources" - errors expected.

**Context cost:** 0.5-3 KB per call

### 7.2 read_resource

**Purpose:** Read content of a specific MCP server resource.

**Schema:** `ServerName` (string, required), `Uri` (string, required)

Shortest description of all 27 tools (4 words: "Retrieves a specified resource's contents.").

**Context cost:** 0.5-20 KB per call (content-dependent)

## 8. Terminal Tool (1 tool)

### 8.1 read_terminal

**Purpose:** Read contents of an IDE terminal panel by process ID.

**Schema:** `ProcessID` (string, required), `Name` (string, required)

**Behavioral constraints:**
- Distinct from `command_status`: reads IDE terminal panels, not background command output
- No `OutputCharacterCount` parameter (unlike `command_status`) - dumps entire buffer
- Risk: verbose processes dump large buffers

**Context cost:** 1-20 KB per call

## 9. Behavioral Constraint Patterns

### 9.1 Prohibition Hierarchy

Three levels across Part 2 tools:

- **Unconditional ("DO NOT"):** `create_memory` - never autonomously invoke
- **Conditional ("Do not... unless"):** `check_deploy_status` - only when user asks
- **Enum prohibition:** `trajectory_search` - schema-valid value forbidden at prompt level

Part 1 prohibitions target actions (cd ban, overwrite ban). Part 2 prohibitions target invocation itself (WHEN not to call).

### 9.2 Pipeline Dependencies

Three sequential pipelines with enforced ordering:

```text
Web:        search_web → read_url_content → view_content_chunk
            (optional)   (requires approval)  (requires document_id)

Deployment: read_deployment_config → deploy_web_app → check_deploy_status
            (prerequisite)           (triggers deploy)  (requires user + deployment_id)

Memory:     Write: create_memory (tool call, requires user request)
            Read:  system prompt injection (automatic, no tool call)
```

The memory pipeline is asymmetric: write uses a tool, read uses system prompt injection. The agent cannot programmatically query memories.

**Approval gate inconsistency:** Only `read_url_content` and `run_command` (Part 1) have documented user approval gates. `deploy_web_app` can deploy to production without user confirmation - only the prompt-enforced prerequisite (`read_deployment_config`) is required. The platform may enforce approval at a layer not visible in tool descriptions [ASSUMED].

### 9.3 Invocation Triggers

Part 2 introduces trigger-activated tools:

- **@mention trigger:** `trajectory_search` (user types @conversation)
- **User request trigger:** `check_deploy_status`, `create_memory`
- **Prerequisite trigger:** `view_content_chunk` (requires prior `read_url_content`)

Part 1 tools are all agent-initiated. Part 2 splits between agent-initiated and externally-triggered.

### 9.4 State Semantics

- **Full-replace:** `todo_list` - complete state every call, context cost multiplies with updates
- **Incremental CRUD:** `create_memory` - create/update/delete independently, more context-efficient

### 9.5 Dynamic Descriptions

- **`skill`:** Catalog regenerated per session from `.windsurf/skills/` folder
- **`run_command`** (Part 1): OS/shell info dynamically injected

## 10. Context Budget Summary

**Cheapest (< 1 KB):** `ask_user_question`, `deploy_web_app`, `check_deploy_status`, `browser_preview`, `create_memory`

**Moderate (1-10 KB):** `todo_list`, `search_web` (2.4-2.8 KB), `read_url_content`, `view_content_chunk`, `read_deployment_config`

**Expensive (10+ KB):** `skill` (3-40 KB), `trajectory_search` (5-25 KB), `read_terminal` (1-20 KB)

**Cumulative workflow examples:**

```text
Web research:   search + 3x read_url + 5x chunk  → ~55 KB
Deployment:     config + deploy + status          → ~4 KB (cheapest pipeline)
Skill loading:  3 skill calls                     → ~49 KB
```

**Practical guideline:** Call `search_web` first (~2.5 KB, no approval) to identify which URLs are worth the approval cost of `read_url_content`. Calling the same skill twice adds 9-40 KB with zero new information.

## Key Takeaways

- 15 tools in 8 groups: Web (3), State (3), Interaction (1), Workflow (1), Deployment (3), Browser (1), MCP (2), Terminal (1)
- `create_memory` has the strongest prohibition ("DO NOT call unless explicitly requested")
- `todo_list` uses full-replace semantics - context cost multiplies with update frequency
- `skill` is effectively a context loader (3-40 KB), second most expensive after `run_command`
- Pipeline ordering is prompt-enforced (not runtime-enforced like Part 1's read-before-write gate)
- Memory read/write is asymmetric: write via tool, read via system prompt injection
- Deployment pipeline is cheapest multi-tool workflow (~4 KB total)

## Sources

- `_WindsurfMetapromptsHistory/2026-05-29_WindsurfCascadeV2.3.15/ToolDefinitions.txt`: Tool definitions
- `Session_2026-05-29_13-59_V2.3.15`: Context measurements


---

# Chapter 10: Tool Walkthrough - MCP-Provided Tools

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents the 25 conditionally-injected tools from Model Context Protocol (MCP) servers: 23 Playwright browser automation tools and 2 Playwriter real-browser tools. Unlike the native tools in [Chapter 8](#chapter-8-tool-walkthrough-core-coding-tools) and [Chapter 9](#chapter-9-tool-walkthrough-platform-tools), these tools only appear when MCP servers are configured and running.

## 1. Conditional Injection Mechanism

### 1.1 When MCP Tools Appear

MCP tools are NOT always present. They appear in the tool definition region ONLY when:
1. MCP servers are configured in the IDE (`.windsurf/mcp.json` or IDE settings)
2. The configured servers are running and responding

Without MCP configuration, only the 27 native tools exist. The V2.3.15 session has both Playwright and Playwriter configured, adding 25 tools for a total of 52.

**Platform limit**: Cascade has a hard limit of **100 total tools** (native + MCP) available at any given time. Individual MCP tools can be toggled on/off in the MCP settings panel [VERIFIED from docs.windsurf.com 2026-05-31].

### 1.2 Naming Convention

Numbered prefix namespacing: `mcp1_` = first configured server (Playwright), `mcp2_` = second server (Playwriter). Assignment follows configuration order, not alphabetical.

### 1.3 Description Injection Pattern

Each tool description prepended with server identification:
- Playwright: `"This is a tool from the playwright MCP server."`
- Playwriter: `"This is a tool from the playwriter MCP server."`

### 1.4 System Prompt MCP Section

The system prompt contains a `<mcp_servers>` XML section listing configured servers (names only, no tool details):

```text
<mcp_servers>
The Model Context Protocol (MCP) is a standard that connects AI systems with external tools and data sources.
# playwright
# playwriter
</mcp_servers>
```

## 2. Playwright Tools - Navigation (3 tools)

### 2.1 mcp1_browser_navigate

Navigate to URL. Schema: `url` (string, required). Cost: 0.3-0.7 KB.

### 2.2 mcp1_browser_navigate_back

Go back in history. No parameters. Cost: 0.2-0.5 KB.

### 2.3 mcp1_browser_tabs

List, create, close, or select tabs. Schema: `action` (enum: list/new/close/select, required), `index` (number), `url` (string). Cost: 0.3-2 KB.

## 3. Playwright Tools - Interaction (10 tools)

### 3.1 mcp1_browser_click

Click on element. Schema: `target` (string, required), `element` (string), `button` (enum: left/right/middle), `doubleClick` (boolean), `modifiers` (array of Alt/Control/ControlOrMeta/Meta/Shift). Cost: 0.3-0.9 KB.

### 3.2 mcp1_browser_type

Type text into element. Schema: `target` (string, required), `text` (string, required), `element` (string), `submit` (boolean), `slowly` (boolean - one char at a time for key handlers). Cost: 0.3-1.5 KB.

### 3.3 mcp1_browser_hover

Hover over element. Schema: `target` (string, required), `element` (string). Cost: 0.3-0.7 KB.

### 3.4 mcp1_browser_press_key

Press keyboard key. Schema: `key` (string, required - e.g., "ArrowLeft" or "a"). Cost: 0.3-0.6 KB.

### 3.5 mcp1_browser_select_option

Select dropdown option. Schema: `target` (string, required), `values` (string[], required), `element` (string). Cost: 0.3-0.9 KB.

### 3.6 mcp1_browser_fill_form

Fill multiple form fields in one call. Schema: `fields` (array of {target, name, type, value, element}, required). Type enum: textbox/checkbox/radio/combobox/slider. Cost: 0.4-2.5 KB.

Most complex Playwright schema (nested array with typed fields).

### 3.7 mcp1_browser_drag

Drag and drop between elements. Schema: `startTarget` (string, required), `endTarget` (string, required), `startElement` (string), `endElement` (string). Cost: 0.3-0.9 KB.

### 3.8 mcp1_browser_drop

Drop files or MIME data onto element (external drag). Schema: `target` (string, required), `paths` (string[]), `data` (object - MIME type to value map). At least one of `paths` or `data` required. Cost: 0.3-1 KB.

### 3.9 mcp1_browser_file_upload

Upload files via file chooser. Schema: `paths` (string[] - omitting cancels chooser). No required params. Cost: 0.3-0.8 KB.

### 3.10 mcp1_browser_handle_dialog

Accept or dismiss browser dialogs. Schema: `accept` (boolean, required), `promptText` (string). Cost: 0.3-0.7 KB.

## 4. Playwright Tools - Observation (4 tools)

### 4.1 mcp1_browser_snapshot

**Purpose:** Capture accessibility tree. Primary observation tool.

**Schema:** `target` (string - scope to subtree), `depth` (number), `boxes` (boolean - include bounding boxes), `filename` (string). All optional.

Returns structured text of interactive elements with selectors. Agent uses this to identify what to click/type.

**Context cost: 5-50 KB** (proportional to page complexity)
- Simple page (login form): ~5-10 KB
- Complex page (dashboard): ~20-50 KB
- **Most expensive Playwright tool by result size**

### 4.2 mcp1_browser_take_screenshot

Capture visual screenshot. Schema: `type` (enum: png/jpeg, required), `target` (string), `element` (string), `fullPage` (boolean), `filename` (string). Cost: 1-5 KB metadata (image tokens counted separately).

### 4.3 mcp1_browser_console_messages

Retrieve console messages. Schema: `level` (enum: error/warning/info/debug, required - each level includes more severe), `all` (boolean - since session start vs last navigation), `filename` (string). Cost: 0.5-20 KB.

### 4.4 mcp1_browser_evaluate

Execute JavaScript in page context. Schema: `function` (string, required - arrow function format), `target` (string), `element` (string), `filename` (string). Cost: 0.2-20 KB (depends on code length and return value).

## 5. Playwright Tools - Network (2 tools)

### 5.1 mcp1_browser_network_requests

List network requests since page load. Schema: `static` (boolean, required - include images/fonts/scripts), `filter` (string - regexp), `filename` (string). Cost: 1-20 KB.

### 5.2 mcp1_browser_network_request

Get full details of single request. Schema: `index` (integer, required - 1-based from network_requests list), `part` (enum: request-headers/request-body/response-headers/response-body), `filename` (string).

**Context cost: 0.5-50+ KB** (response bodies can be large)

## 6. Playwright Tools - Page Control (4 tools)

### 6.1 mcp1_browser_close

Close page. No parameters. Cost: 0.1-0.2 KB. **Cheapest tool of all 52.**

### 6.2 mcp1_browser_resize

Resize window. Schema: `width` (number, required), `height` (number, required). Cost: 0.2-0.3 KB.

### 6.3 mcp1_browser_wait_for

Wait for text/disappearance/time. Schema: `text` (string), `textGone` (string), `time` (number). No required params. Cost: 0.2-0.5 KB.

### 6.4 mcp1_browser_run_code_unsafe

**Purpose:** Execute arbitrary Playwright code. Full remote code execution.

**Schema:** `code` (string), `filename` (string). Either must be provided.

**Security warning from description:** "Unsafe: executes arbitrary JavaScript in the Playwright server process and is RCE-equivalent."

Only MCP tool with an explicit security warning. Can do anything Playwright supports in one call. Cost: 0.2-10+ KB.

## 7. Playwriter Tools (2 tools)

Playwriter uses the user's real Chrome browser with existing cookies and logins, unlike Playwright which spawns fresh contexts.

### 7.1 mcp2_execute

**Purpose:** Execute JavaScript in Playwriter sandbox with access to real browser page.

**Schema:** `code` (string, required), `timeout` (number, default: 10000ms)

**Extended system prompt (~15 KB embedded in description):**

The `mcp2_execute` description contains the largest tool description of all 52 tools. Key sections:

- **Context variables:** `state` (persisted between calls), `page` (default page), `context` (browser context), `require` (Node.js modules)
- **Rules:** Initialize `state.page` first, multiple calls for complex logic, never close browser/context, check state after actions, clean up listeners
- **Interaction feedback loop:** observe → act → observe pattern enforced
- **Common mistakes (13 anti-patterns):** stale locators, paste failures, wrong assumptions, text concatenation, quote escaping, screenshot overuse, not verifying actions, assuming page loaded, not using Playwriter for JS sites, login popup handling, click timeouts, dispatchEvent bypass, over-investigating
- **Utility functions:** `snapshot()`, `getLatestLogs()`, `getCleanHTML()`, `getPageMarkdown()`, `waitForPageLoad()`, `getCDPSession()`, `getLocatorStringForElement()`, `getReactSource()`, `getReactComponentInfo()`, `inspectPinnedElement()`, `getStylesForLocator()`, `createDebugger()`, `createEditor()`, `screenshotWithAccessibilityLabels()`, `resizeImageForAgent()`, `recording.start/stop()`, `createDemoVideo()`
- **Computer use:** Low-level mouse/keyboard (click, hover, scroll, drag, key hold)
- **Network interception:** Request/response capture patterns
- **Selector priority:** data-testid > getByRole > getByText > semantic HTML > CSS > path

**Behavioral constraints:**
- **One-liner preference:** "Should be one line, using ; to execute multiple statements"
- **Multi-call mandate:** "you MUST call execute multiple times instead of writing complex scripts"
- **Persistent state:** `state` object survives between calls
- **Page sharing:** "pages are shared across all sessions" - multiple agents can interfere

**Context cost:** 0.3-20 KB per call. The 15 KB description is in tool DEFINITION (sent once per request), not per call.

### 7.2 mcp2_reset

**Purpose:** Reset browser connection and clear state.

**Description (verbatim):**
```text
Recreates the CDP connection and resets the browser/page/context. Use this when the MCP stops responding, you get connection errors, if there are no pages in context, assertion failures, page closed, or other issues.

After calling this tool, the page and context variables are automatically updated in the execution environment.

This tools also removes any custom properties you may have added to the global scope AND clearing all keys from the `state` object. Only `page`, `context`, `state` (empty), `console`, and utility functions will remain.

if playwright always returns all pages as about:blank urls and evaluate does not work you should ask the user to restart Chrome. This is a known Chrome bug.
```

**Schema:** No parameters. Recovery tool for broken connections. Clears ALL state. Cost: 0.2-0.5 KB.

## 8. Context Budget Analysis

### 8.1 Fixed Definition Overhead

MCP tool definitions add to EVERY request regardless of whether tools are called:
- 23 Playwright tools x ~300-500 bytes each: ~8-12 KB
- `mcp2_execute` (15 KB embedded prompt): ~15 KB
- `mcp2_reset`: ~0.5 KB
- **Total fixed overhead: ~25-28 KB per request**

### 8.2 Typical Browser Automation Cost

A simple form fill via Playwright (observe-act-observe pattern):

```text
mcp1_browser_navigate         → +0.5 KB
mcp1_browser_snapshot         → +15 KB (average page)
mcp1_browser_click            → +0.5 KB
mcp1_browser_snapshot         → +15 KB (verify result)
mcp1_browser_type             → +0.8 KB
mcp1_browser_click (submit)   → +0.5 KB
mcp1_browser_snapshot         → +15 KB (verify submission)
Total: ~48 KB for a simple form fill
```

`browser_snapshot` dominates because the observe-act-observe pattern requires repeated calls (~15 KB each).

### 8.3 Playwriter vs Playwright Context Efficiency

- **Playwright:** 5-step automation ~40-80 KB (each action is a separate tool call + snapshot between actions)
- **Playwriter:** Same automation ~10-30 KB (multiple actions combined in one `execute` call, snapshots only when explicitly requested)

Playwriter is 2-4x cheaper in context but requires Chrome open with extension enabled.

For complete per-call cost tiers across all 52 tools, see [Chapter 12](#chapter-12-context-budget-and-practical-guidelines).

## 9. Behavioral Constraint Patterns

### 9.1 Permission Model

- **Playwright:** No user approval for any action. Full autonomy.
- **Playwriter:** No per-call approval, but requires user to click extension icon (one-time activation).
- **`run_code_unsafe`:** Marked "RCE-equivalent" but no approval gate in schema. Safety relies on agent self-governance.

### 9.2 State Model Comparison

- **Native tools (Ch5-Ch6):** Stateless per call (except pipeline dependencies)
- **Playwright (mcp1_):** Stateless per tool call; browser page persists between calls
- **Playwriter (mcp2_):** Explicitly stateful via `state` object; pages shared across sessions

### 9.3 Error Recovery

- **Native tools:** Error messages inline, agent retries
- **Playwright:** Errors inline, no recovery tool
- **Playwriter:** Dedicated `mcp2_reset` recovery tool; known bugs documented

### 9.4 Description Size Spectrum (all 52 tools)

- **Shortest:** `read_resource` (4 words)
- **Longest:** `mcp2_execute` (~15 KB - effectively a second system prompt)
- **Median native tool:** ~200-500 bytes
- **Median Playwright tool:** ~100-300 bytes

### 9.5 MCP vs Native Tool Differences

- No argument ordering directives
- No read-before-write gates
- No user approval gates
- Simpler schemas (fewer required params)
- `element` parameter pattern: human-readable description "used to obtain permission" suggests consent layer outside schema

## Key Takeaways

- 25 MCP tools conditionally injected (~25-28 KB fixed definition overhead per request)
- `mcp2_execute` contains a ~15 KB embedded system prompt - largest tool description of all 52 tools
- Playwright tools are stateless per-call; Playwriter has persistent `state` object
- `browser_snapshot` dominates context cost (5-50 KB per call) - observe-act-observe pattern makes browser automation expensive
- `mcp1_browser_run_code_unsafe` is explicitly "RCE-equivalent" but has no approval gate
- Playwriter is more context-efficient than Playwright (fewer round trips) but requires Chrome + extension
- MCP tools have no argument ordering, no read-before-write gates, no approval gates

## Sources

- V2.3.15 session tool definitions (live wire data)
- `_WindsurfMetapromptsHistory/2026-05-29_WindsurfCascadeV2.3.15/ToolDefinitions.txt`


---

# Chapter 11: Context Management and Checkpoints

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter documents how Cascade manages context growth: the proactive summarization mechanism, checkpoint injection format, truncation threshold, todo list persistence, and what information survives versus what is lost. The reader should understand context growth from [Chapter 4](#chapter-4-the-getchatmessage-request) and the multi-model architecture from [Chapter 1](#chapter-1-multi-model-architecture-and-feature-flags).

## 1. Overview

Windsurf Cascade re-sends the complete context window with every GetChatMessage call. As conversation history grows, context eventually exceeds the model's effective window. Windsurf addresses this with a checkpoint mechanism that:

1. Runs 3 parallel summarizer calls using a cheaper/faster model (Gemini 2.5 Flash)
2. Produces a structured checkpoint containing objective, todo state, and conversation summary
3. Injects the checkpoint into the next main call, replacing the truncated conversation history

The checkpoint mechanism is transparent to the user. Windsurf shows no UI indication when summarization occurs.

## 2. Checkpoint Trigger Mechanism

### 2.1 Proactive Summarization

Summarizer calls fire at multiple points during a session, well before context exceeds the truncation threshold. In the analyzed session (67 main GetChatMessage calls over 18 minutes), summarizer batches fired at 5 points:

Derived from V2.3.15 wire data (timestamps and context sizes from request metadata):

```text
Time      Seq    Context   Summarizer
14:00     0110    98 KB    -
14:03     0387   231 KB    -
14:04     0408   ---       Summarizers 0408, 0409, 0410 fired (context was 231 KB)
14:04     0412   250 KB    - (no checkpoint injected, context below threshold)
14:10     0732   367 KB    -
14:10     0756   ---       Summarizers 0756, 0757, 0758 fired (context was 367 KB)
14:10     0760   377 KB    - (no checkpoint injected)
14:11     0782   ---       Single summarizer 0782 fired (context was 379 KB)
14:12     0885   467 KB    -
14:13     0909   ---       Summarizers 0909, 0910, 0911 fired (context was 490 KB)
14:13     0914   490 KB    - (context still growing, summary being prepared)
14:13     0929   499 KB    - (last pre-checkpoint call)
14:13     0950   388 KB    <- CHECKPOINT 1 applied (dropped 111 KB)
14:17     1221   506 KB    - (session end, no second checkpoint)
```

Summarizers produce outputs proactively. Windsurf applies the checkpoint only when context exceeds the configured threshold.

### 2.2 Truncation Threshold

Configured via the `CASCADE_PLAN_BASED_CONFIG_OVERRIDE` feature flag:

```json
{
  "planner_config": {
    "truncation_threshold_tokens": "100000"
  }
}
```

At ~3-4 characters per token, 100,000 tokens corresponds to ~300-400 KB of decompressed text. The checkpoint triggered between 499 KB (request 0929) and 388 KB (request 0950), consistent with a ~100K token threshold applied to the variable conversation portion after subtracting the ~91 KB fixed overhead.

### 2.3 Summarizer Call Pattern

Summarizers always fire in batches of 3 parallel GetChatMessage calls. Each batch uses the same conversation history but different output instructions. All 3 calls share:

- The same timestamp (within 1 second)
- Gemini 2.5 Flash as the model
- A shorter system prompt (400 bytes vs 50 KB)
- No tool definitions (the summarizer cannot call tools)

Exception: request 0782 was a single summarizer call - likely a retry or incremental update [ASSUMED].

## 3. Three Parallel Summarizers

Each summarizer batch consists of 3 calls with distinct prompts. All share the same system prompt but differ in the user-facing instruction at the end of the conversation history.

### 3.1 Common System Prompt

```text
You are an expert AI coding assistant with extreme attention to detail.
You are pair programming with a USER to solve a coding task.
You provide clear, detailed, and accurate summaries of conversations.
When asked, you focus on outlining the USER's main goals
and listing key information and context discussed.
Your response should be well-organized and reflect the essence of the dialog.
NEVER lie or make things up. Your summaries should always be grounded
in the conversation.
```

This is notably different from the main system prompt ("You are Cascade..."). The summarizer prompt is ~400 bytes vs ~50 KB.

### 3.2 Summarizer A: Title and Objective

Generates a short conversation title and user objective paragraph.

Verbatim instruction (appended after conversation history):

```text
ENTER ANALYSIS MODE

DONT TAKE ANY ACTIONS. ONLY OUTPUT YOUR ANALYSIS FOLLOWING THE PROVIDED FORMAT

Generate a short conversation title around 3-5 words describing the USER's
intent and goals during this chat. Should be title-cased.
Then, in a new line, write the USER's main objective and goals, keeping in
mind that their goals may have been included in the previous CHECKPOINT summary.
Make sure that this is very action oriented around solving the USER's task.
Give particular focus to the latest requests/messages.

OUTPUT FORMAT

{Short title}
{a paragraph about the main objectives and goals}

DONT TAKE ANY ACTIONS. ONLY OUTPUT YOUR ANALYSIS
```

### 3.3 Summarizer B: Full Conversation Summary

Produces the structured summary that becomes the "Previous Session Summary" in the checkpoint.

Verbatim instruction:

```text
Prefer extracting specifics vs paraphrasing. Ex.
- saying "run COMMAND -ARG1 -ARG2" is better than "run the server"
- "use the bash tool to call mcp_cli on the datadog MCP" is better
  than "use the datadog MCP"
This is only true if the system/agent/user actually gave these specifics.
Do not make up specifics yourself. Its okay to say "no specifics" to be certain.

Please provide your summary based on the conversation so far, following
this structure and ensuring precision and thoroughness in your response.
Please limit your response to at most 15000 words.

There may be additional summarization instructions provided in the included
context. If so, remember to follow these instructions when creating the
above summary.
```

### 3.4 Summarizer C: Code Interaction History

Extracts structured records of file edits, views, and code item inspections.

Verbatim instruction:

```text
ENTER HISTORY GENERATION MODE

You are now focused solely on generating a history of the interactions.
Do not take any actions and follow the provided format:

Create a history of all code interactions, including those listed in
previous CHECKPOINT summaries, which you believe are relevant and
important to solving the USER's task.

Organize the history into three categories.

1. Edited Files: <edited_file> with target_file, lines_modified, edit_summary
2. Viewed Files: <viewed_file> with absolute_path, lines_viewed, learnings
3. Viewed Code Items: <viewed_code_item> with node_identifier, learnings,
   code_snippets
```

### 3.5 Summarizer Call vs Main Call

```text
Main GetChatMessage                    Summarizer GetChatMessage
├── System prompt: ~50 KB              ├── System prompt: ~400 bytes
│   "You are Cascade..."               │   "You are an expert AI..."
├── User rules: ~33 KB                 ├── User rules: none
├── Tool definitions: ~35 KB           ├── Tool definitions: none
├── Feature flags: ~4 KB               ├── Feature flags: minimal
├── Conversation history: variable     ├── Conversation history: full
├── Model: claude-opus-4-6-thinking    ├── Model: Gemini 2.5 Flash
└── Size: 98-506 KB                    └── Size: 137-172 KB
```

## 4. Checkpoint Injection Format

### 4.1 Injection Point

The checkpoint is placed at protobuf string position `[0065]`, replacing both the memory string (see [Chapter 2](#chapter-2-the-memory-system)) AND truncated conversation history:

```text
[0009-0064] {SYSTEM_PROMPT}       <- unchanged (~50 KB)
[0065]      {CHECKPOINT}          <- replaces "No MEMORIES were retrieved..."
[0066+]     {remaining turns}     <- only recent conversation turns kept
```

### 4.2 Checkpoint Structure

Verbatim template from V2.3.15 wire data:

```text
**The following is a summary of important context from your previous
coding session with the USER. **
{{ CHECKPOINT N }}

# USER Objective:
{Title from Summarizer A}
{Objective paragraph from Summarizer A}

# Current working TODO list (keep this up to date with todo_list tool):
Todo list updated:
[
  {"content": "...", "id": "1", "status": "completed", "priority": "high"},
  {"content": "...", "id": "2", "status": "in_progress", "priority": "high"},
  ...
]

Make sure to continue working off of this TODO list

# Previous Session Summary:
<summary>
1. Request and Intent:
2. Key Concepts and Values:
3. Task Requirements:
4. Files and Code Sections:
5. Errors and fixes:
6. Problem Solving:
7. All user messages:
8. Pending Tasks:
9. Current Work:
</summary>

# Code Interaction Summary:
<edited_file>
  <target_file>...</target_file>
  <lines_modified>...</lines_modified>
  <edit_summary>...</edit_summary>
</edited_file>
<viewed_file>
  <absolute_path>...</absolute_path>
  <lines_viewed>...</lines_viewed>
  <learnings>...</learnings>
</viewed_file>

**IMPORTANT: this summary is just for your reference. You may respond to
my previous and future messages, but DO NOT ACKNOWLEDGE THIS CHECKPOINT
MESSAGE. JUST READ IT BUT DO NOT MENTION IT, RESPOND TO IT, OR TAKE
ACTION BECAUSE OF IT.**
```

### 4.3 Platform-Hardcoded Behavioral Anchors

Three strings in the checkpoint template are NOT generated by any summarizer - they are platform constants:

1. `"# Current working TODO list (keep this up to date with todo_list tool):"` - instructs model to maintain todo state
2. `"Make sure to continue working off of this TODO list"` - explicit continuation directive
3. `"DO NOT ACKNOWLEDGE THIS CHECKPOINT MESSAGE..."` - prevents model from treating checkpoint as user message

## 5. Todo List Persistence

The `todo_list` tool creates structured task lists. The checkpoint mechanism has special handling to persist todo state without relying on LLM summarization.

### 5.1 Lifecycle

```text
Agent calls todo_list tool
  |
  v
Windsurf records tool output in conversation history as:
  "Todo list created:" or "Todo list updated:"
  [{"content": "...", "id": "1", "status": "completed", ...}, ...]
  |
  v
Platform extracts the LATEST todo state (deterministic, no LLM)
  |
  v
Checkpoint includes it under "# Current working TODO list"
with instruction: "Make sure to continue working off of this TODO list"
  |
  v
Next main call receives checkpoint -> agent continues from last known state
```

### 5.2 Example State

Before checkpoint (from conversation history, request 0885):

```json
[
  {"content": "Create session folder and tracking files", "status": "completed"},
  {"content": "Register LLMCG topic in ID-REGISTRY.md", "status": "completed"},
  {"content": "Create Topic Folder", "status": "completed"},
  {"content": "Phase 1: Preflight - STRUT, decomposition, sources, VCRIV", "status": "in_progress"},
  {"content": "Phase 2: Planning - Summary, template, TASKS, VCRIV", "status": "pending"},
  {"content": "Phase 3: Research - RAG, Fine-tuned, Prompt-engineered INFO files", "status": "pending"},
  {"content": "Phase 4: Final verification, sync, Summary finalization", "status": "pending"}
]
```

After checkpoint (in request 0950): identical JSON, preserving exact status of each item.

### 5.3 Full-Replace Semantics

The `todo_list` tool uses full-replace semantics: each call sends the COMPLETE list. The platform extracts the LAST `todo_list` tool output from conversation history. This is a deterministic string extraction, not an LLM operation. All 3 summarizer instructions were verified: none mention todo lists or extract structured task state [PROVEN].

### 5.4 Why Structured JSON Matters

Summarizer B independently captures pending tasks as prose (section 8 of its output). Compare:

```text
Summarizer B prose:                    Platform-extracted JSON:
8. Pending Tasks:                      [
   - Phase 2: Planning                   {"id":"4", "status":"in_progress", ...},
   - Phase 3: Research                   {"id":"5", "status":"pending", ...},
   - Phase 4: Final verification         {"id":"6", "status":"pending", ...},
                                         {"id":"7", "status":"pending", ...}
                                       ]
```

The JSON preserves: exact item IDs, per-item status, priority, which item is `in_progress`, and completed items that the prose summary omits entirely. The prose backup is lower-fidelity but provides redundancy if the platform extraction fails.

## 6. What Survives vs What Is Lost

### 6.1 Preserved Across Checkpoint

**From Summarizer A:**
- User objective: title and goal paragraph

**From Platform (deterministic, no LLM):**
- Todo list state: full JSON with item statuses

**From Summarizer B (9-section summary):**
- Key concepts with definitions
- Important values (paths, IDs, config)
- Task requirements
- Error history
- Verbatim user messages
- Pending tasks

**From Summarizer C:**
- File edit history (paths, line ranges, descriptions)
- Viewed file learnings
- Critical code snippets

### 6.2 Lost at Checkpoint

- Verbatim tool outputs (grep results, file contents, command output)
- Intermediate reasoning (step-by-step thinking between actions)
- Exact conversation flow (turn-by-turn dialog)
- Tool call parameters (exact arguments)
- Failed attempts (unless in "Errors and fixes" section)
- Timing details (per-step timestamps)

### 6.3 Fidelity Risk

The summarizer (Gemini 2.5 Flash) interprets and compresses content. Risks:
- May misinterpret technical details or code semantics
- Infrequently referenced concepts may be dropped
- Code snippets selected by summarizer's judgment of "crucial"
- Values may be paraphrased rather than preserved verbatim

## 7. Context Size Over Session Lifetime

```text
KB
506 |                                                       *  *  *
499 |                              *  <- peak before checkpoint
490 |                              :                   *  *
467 |                           *  :
    |                        .     :
402 |                     *        :
388 |                              * <- checkpoint drops 111 KB
367 |                  *
    |               .
301 |            *
    |         .
231 |      *
    |    .
131 |   *
 98 |  *
    |__|________|_________|_________|_________|__
    14:00     14:04     14:08     14:12     14:16
                                   ^
                              checkpoint fires
```

Context grew back to 506 KB by session end without triggering a second checkpoint. Possible explanations [ASSUMED]:
- Session ended before the next summarizer cycle completed
- Summarizer batches were scheduled but checkpoint assembly was still pending
- The threshold has hysteresis or a minimum interval between checkpoints

## 8. What Degrades Without Each Component

### 8.1 Without the todo_list Tool

Summarizer B still captures "Pending Tasks" in prose. The model can infer what to do next, but:
- No structured state (item IDs, per-item status lost)
- No explicit continuation instruction
- Summarizer may paraphrase, merge, or omit items

### 8.2 Without the Checkpoint Mechanism

The `todo_list` tool output stays in conversation history until context is truncated. When truncation occurs without a checkpoint, all todo state is silently lost. No recovery possible.

### 8.3 Without Platform Extraction

If the platform stopped extracting todos into the checkpoint template:
- Summarizer B's prose "Pending Tasks" would be the only surviving reference
- No "Make sure to continue working off this TODO list" instruction
- Model may not recognize the summary as actionable task state
- Completed items vanish from the record

The three components (tool, checkpoint, platform extraction) form a chain where each eliminates a failure mode of the others.

## Key Takeaways

- 3 parallel summarizers (Gemini 2.5 Flash) produce checkpoint content proactively, ahead of threshold
- Truncation threshold: 100,000 tokens via feature flag (`CASCADE_PLAN_BASED_CONFIG_OVERRIDE`)
- Checkpoint reduces context by ~111 KB (499 KB to 388 KB in observed session)
- Todo list persists via deterministic platform extraction (no LLM), ensuring exact state preservation
- The checkpoint template contains 3 platform-hardcoded behavioral anchors (not LLM-generated)
- Summarizer uses a 400-byte system prompt (vs 50 KB for main calls) with no tools or user rules
- Context grew back to 506 KB after checkpoint without triggering a second one

## Sources

- `Session_2026-05-29_13-59_V2.3.15`: 67 main calls, 5 summarizer batches, 1 checkpoint applied
- Summarizer requests 0756-0758: Three parallel calls with distinct instructions
- Request 0950: First post-checkpoint main call showing injected `{{ CHECKPOINT 1 }}`


---

# Chapter 12: Context Budget and Practical Guidelines

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This chapter consolidates context cost analysis from all 52 tools into a unified budget framework. Every tool call adds TWO items to conversation history: call arguments + tool result. Both accumulate until a checkpoint truncates them (see [Chapter 11](#chapter-11-context-management-and-checkpoints)). Understanding these costs is essential for avoiding premature checkpoints that destroy detailed context.

## 1. Measurement Methodology

From the V2.3.15 session capture, context growth measured by comparing consecutive GetChatMessage request sizes:

- Request 0110 (first, no history): 100,494 bytes (182 strings)
- Request 0130 (after round 1: `skill` + `list_dir`): 113,129 bytes (224 strings) → +12.6 KB
- Request 0154 (after round 2: 4x `read_file`): 133,654 bytes (480 strings) → +20.5 KB

Each tool call round trip contributes: call arguments + assistant text + extended thinking block + tool result content + tool result ID marker. Overhead per turn (excluding tool content): ~500-1000 bytes.

## 2. Fixed Costs Per Request

Before any tool calls, each request carries fixed overhead:

- **System prompt:** ~50 KB (Windsurf behavioral sections ~10 KB + user rules ~33 KB + workflows ~4 KB)
- **Native tool definitions:** ~35 KB (27 tools, separate protobuf region)
- **MCP tool definitions (if configured):** ~25-28 KB additional (23 Playwright + 2 Playwriter)
- **Feature flags:** ~4 KB (40 key-value pairs)
- **Auth + workspace layout + misc:** ~2-5 KB

**Total fixed cost with MCP:** ~116-122 KB per request. With the checkpoint threshold at ~100K tokens (~400-500 KB decompressed), this leaves ~278-384 KB for conversation history before triggering truncation.

**Total fixed cost without MCP:** ~91 KB per request (matches observed first-call overhead). Leaves ~309-409 KB for history.

## 3. Unified Cost Tiers (All 52 Tools)

### Tier 1 - Cheap (typically < 1 KB per call)

- `list_dir`: 1-3 KB (cheapest reading tool)
- `edit_notebook`: 0.3-2 KB
- `command_status`: 0.1-5 KB (agent-controlled ceiling)
- `ask_user_question`: 0.3-1.3 KB
- `deploy_web_app`: 0.3-0.9 KB
- `check_deploy_status`: 0.3-0.7 KB
- `browser_preview`: 0.3-0.7 KB
- `create_memory`: 0.3-2 KB
- `browser_close`: 0.1-0.2 KB (cheapest of all 52)
- `browser_resize`: 0.2-0.3 KB
- `browser_navigate`: 0.3-0.7 KB
- `browser_click`: 0.3-0.9 KB
- `browser_hover`: 0.3-0.7 KB
- `browser_press_key`: 0.3-0.6 KB
- `mcp2_reset`: 0.2-0.5 KB

### Tier 2 - Moderate (1-10 KB per call)

- `read_file`: 3-10 KB (proportional to file content)
- `grep_search`: 1-5 KB
- `find_by_name`: 1-4 KB (hard cap at 50 results)
- `edit` (small-medium): 0.3-5 KB
- `todo_list`: 1-4 KB (full-replace semantics multiply cost)
- `search_web`: 3-8 KB
- `read_url_content`: 2-10 KB (first chunk)
- `view_content_chunk`: 2-8 KB per chunk
- `read_deployment_config`: 1-5 KB
- `browser_type`: 0.3-1.5 KB
- `browser_fill_form`: 0.4-2.5 KB
- `browser_take_screenshot`: 1-5 KB metadata

### Tier 3 - Expensive (10-50 KB per call)

- `write_to_file` (medium files): 8-40 KB (FULL content in history)
- `multi_edit` (large refactors): 5-30 KB
- `code_search`: 3-15 KB
- `read_notebook` (data science): 3-50 KB
- `skill`: 3-40 KB (entire skill content loaded)
- `trajectory_search`: 5-25 KB (up to 50 chunks)
- `read_terminal`: 1-20 KB (no output limit)
- `browser_snapshot`: 5-50 KB (page complexity dependent)
- `browser_network_requests`: 1-20 KB
- `browser_evaluate`: 0.2-20 KB
- `browser_console_messages`: 0.5-20 KB
- `mcp2_execute`: 0.3-20 KB

### Tier 4 - Potentially Catastrophic (50+ KB per call)

- `run_command` (verbose): up to **500+ KB** (highest bloat risk)
- `read_notebook` (large): up to 50+ KB
- `write_to_file` (large): up to 40+ KB
- `browser_network_request` (response body): 0.5-**50+ KB**
- `browser_snapshot` (complex page): up to 50 KB

## 4. Cumulative Workflow Patterns

### 4.1 Session Initialization

```text
Turn 1:  skill + list_dir           → +12.6 KB (skill dominates at ~9 KB)
Turn 2:  4x read_file               → +20.5 KB (~5 KB per template)
Turn 3:  4x read_file               → +18.0 KB
Turn 4:  3x write_to_file           → +15.0 KB
Turn 5:  run_command (mkdir)         → +2.0 KB
...
Turn 50: accumulated history         → ~400 KB total
```

### 4.2 Web Research

```text
search_web              → +5 KB
read_url_content x3     → +20 KB (3 pages, first chunk each)
view_content_chunk x5   → +30 KB (deeper into 2 pages)
Total: ~55 KB for moderate research
```

### 4.3 Deployment

```text
read_deployment_config  → +3 KB
deploy_web_app          → +0.5 KB
check_deploy_status     → +0.5 KB
Total: ~4 KB (cheapest multi-tool workflow)
```

### 4.4 Skill Loading

```text
skill (session-management)  → +9 KB
skill (write-documents)     → +25 KB
skill (coding-conventions)  → +15 KB
Total: ~49 KB just from skill loads
```

### 4.5 Browser Automation (Playwright)

```text
browser_navigate         → +0.5 KB
browser_snapshot         → +15 KB
browser_click            → +0.5 KB
browser_snapshot         → +15 KB
browser_type             → +0.8 KB
browser_click (submit)   → +0.5 KB
browser_snapshot         → +15 KB
Total: ~48 KB for a simple form fill
```

### 4.6 Checkpoint Threshold

```text
Available context budget after fixed overhead (~91 KB without MCP):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ~400 KB available

How fast different workflows fill it:

Session init (skill + reads + writes):
████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ~70 KB (5 turns)

Web research (search + read + chunks):
██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ~55 KB (9 calls)

Browser automation (Playwright, 3 actions):
████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ~48 KB (7 calls)

Deployment pipeline:
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   ~4 KB (3 calls)

Single verbose run_command (unbounded):
████████████████████████████████████████████████████████ 500+ KB (1 call!)
```

A typical session hits ~100,000 tokens (~400-500 KB decompressed) after 30-50 tool call rounds. At this point the checkpoint fires, reducing context by ~111 KB and losing detailed tool result content.

## 5. Practical Guidelines for Agents

- **Prefer `grep_search` (file list mode) over `code_search`** for simple lookups (1-5 KB vs 3-15 KB)
- **Use `offset`/`limit` on large files** instead of reading entirely
- **Cap `run_command` output** with shell pipes (`| Select-Object -First N`, `| head -20`)
- **Prefer `multi_edit` over sequential `edit` calls** (fewer turns = less overhead per result)
- **Parallel tool calls share one thinking block** (cheaper per-tool than sequential)
- **Call skills once** and reuse instructions. Repeat calls add identical content.
- **Batch `todo_list` updates** into one call (full-replace means each call sends everything)
- **Use specific queries in `trajectory_search`** to minimize returned chunks (empty query = 25 KB)
- **Minimize `browser_snapshot` frequency** - the observe-act-observe pattern is the primary driver of browser automation cost
- **Prefer Playwriter over Playwright** for multi-step automation (fewer round trips)
- **Avoid `read_notebook` on unknown notebooks** - use `read_file` to check size first

## 6. Practical Guidelines for Programmers

- **Each tool call round trip adds ~500-1000 bytes overhead** beyond actual content (turn markers, thinking blocks, IDs)
- **The checkpoint at ~100K tokens summarizes aggressively** - detailed context from early tool results is lost
- **Large `write_to_file` calls create permanent history entries** until checkpoint (no garbage collection)
- **Approval gates are inconsistent:** Only `read_url_content` and `run_command` have documented gates; `deploy_web_app` has none
- **Pipeline ordering is prompt-enforced, not platform-enforced** (unlike read-before-write gate on `edit`)
- **Trigger-activated tools cannot be tested in isolation** (`trajectory_search` requires @mentions)
- **`skill` is effectively a context loader** - it loads text instructions, not code
- **`todo_list` is a UI tool with checkpoint semantics** - its state survives context truncation
- **MCP tool definitions cost ~25-28 KB per request** even if never called
- **The Playwriter description is effectively a second system prompt** (~15 KB), injected via tool definition

## 7. Context-Efficient Patterns

### 7.1 File Inspection

```text
BAD:  read_file (whole 500-line file)          → 20 KB
GOOD: grep_search (find relevant lines)        → 2 KB
      read_file (offset=145, limit=30)         → 3 KB
      Total: 5 KB for targeted inspection
```

### 7.2 Codebase Orientation

```text
BAD:  code_search ("understand the project")   → 15 KB (vague query)
GOOD: list_dir (project root)                  → 2 KB
      find_by_name (*.py in src/)              → 3 KB
      Total: 5 KB for structure overview
```

### 7.3 Command Output

```text
BAD:  run_command "git log"                    → 200+ KB (unbounded)
GOOD: run_command "git log -n 5 --oneline"     → 1 KB
```

### 7.4 Browser Automation

```text
BAD:  navigate + snapshot + click + snapshot + type + snapshot  → 48 KB
GOOD: mcp2_execute (navigate + click + type in one call)       → 5 KB
```

## Key Takeaways

- Fixed overhead per request: ~91 KB without MCP, ~116-122 KB with MCP, leaving ~278-409 KB for history before checkpoint (~100K tokens ≈ 400-500 KB)
- A session hits checkpoint after 30-50 tool call rounds depending on tool mix
- `run_command` is the highest bloat risk (up to 500+ KB); `browser_snapshot` is the most expensive repeating tool (5-50 KB per call)
- The cheapest tool calls (0.1-0.3 KB) are browser control actions; the most expensive per-call are unbounded command outputs and page snapshots
- Context-efficient patterns save 4-10x compared to naive tool usage
- MCP tools add ~25-28 KB fixed cost per request even when unused

## Sources

- `_INFO_HOW_WINDSURF_CASCADE_TOOLS_PART_1.md [CSMP-IN08]` section 6: Core tool I/O profiles
- `_INFO_HOW_WINDSURF_CASCADE_TOOLS_PART_2.md [CSMP-IN09]` section 9: Platform tool budget analysis
- `_INFO_HOW_WINDSURF_CASCADE_TOOLS_PART_3.md [CSMP-IN10]` section 8: MCP tool budget analysis
- `Session_2026-05-29_13-59_V2.3.15`: Measured request sizes


---

# Appendix A: Open Questions

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

This appendix catalogs what remains unknown after the V2.3.15 capture analysis. Each question states what is proven, what is unknown, and what would be needed to investigate further.

## 1. Brain Planner - The Hidden Layer

**Known:** GPT-4.1 configured as "brain" via `cascade-brain-config` flag. Filter strategy: `BRAIN_FILTER_STRATEGY_NO_SYSTEM_INJECTED_STEPS`. Config includes `forceNoExplanation: false`, `forceOverwrite: false`. Command allowlist/denylist in global config.

**Unknown:**
- Does the brain see the full 50 KB system prompt or a filtered version?
- What does `BRAIN_FILTER_STRATEGY_NO_SYSTEM_INJECTED_STEPS` filter out?
- Is the brain invoked for EVERY GetChatMessage or only certain turn types?
- Does brain output become part of the generator's prompt, or modify the tool set?
- Is the brain/generator pipeline sequential or parallel?
- Does the brain have its own system prompt?

**Requires:** `extension.js` reverse-engineering, response latency pattern analysis.

## 2. Memory System Internals

**Known [PROVEN]:**
- GPT-5 Nano is the memory model (feature flag `CASCADE_MEMORY_CONFIG_OVERRIDE`)
- Output injected at protobuf string position [0065]
- Three types: global rules (always in system prompt), user-provided, system-retrieved
- `CASCADE_ENABLE_AUTOMATED_MEMORIES` = enabled
- `CASCADE_USER_MEMORIES_IN_SYS_PROMPT` = `{"add_user_memories_to_system_prompt": true}`
- Storage is a structured record database (Id, Title, Content, CorpusNames, Tags, Action, UserTriggered)
- Full CRUD via `create_memory` tool (not append-only)
- Retrieval is passive: no read/query tool exists, [0065] populated before agent acts
- Agent has ZERO control over retrieval - cannot query, browse, or list stored memories
- Position [0065] shared with checkpoints (memories lost after checkpoint)

**Unknown:**
- **Retrieval timing**: Is GPT-5 Nano called before every GetChatMessage, or only at conversation start, or only when context changes?
- **Retrieval input**: Does GPT-5 Nano see the full user message? Just workspace name? Conversation summary?
- **Selective vs dump**: Does it filter memories by relevance, or inject ALL stored memories?
- **Retrieved format**: What does a populated [0065] look like? (Individual records? Concatenated text? XML blocks?)
- **Storage backend**: Vector database? Relational? Key-value? Per-user partition?
- **Capacity**: Maximum memories per user/workspace? Size limits on Content field?
- **Automated triggers**: What causes platform-initiated memory creation?
- **Dual injection**: Does `CASCADE_USER_MEMORIES_IN_SYS_PROMPT` cause user memories to be always-present (like rules) vs selectively retrieved?
- **Network visibility**: Separate HTTP call to a memory service, or internal function call within Go backend?

**Test procedures to resolve:**

1. **Selective vs dump test**: Create 5 memories with different topics (e.g., "TypeScript preference", "deployment URL", "team member names", "API key location", "testing framework"). Start new conversation asking about only ONE topic. Capture GetChatMessage. If [0065] contains only the relevant memory → selective retrieval proven. If all 5 appear → dump behavior proven.

2. **Timing test**: In a single conversation, capture multiple GetChatMessage requests. If [0065] content changes between requests (without new memory creation) → per-request retrieval. If identical across all requests → conversation-start-only.

3. **Format test**: Any capture with pre-existing memories reveals the populated [0065] format directly.

4. **Automated trigger test**: Have extended conversations with clear preference statements ("I always want to use pytest"). Start fresh conversation weeks later. If a memory about pytest appears at [0065] without ever calling `create_memory` → automated storage confirmed.

5. **Network test**: Use mitmproxy during a session with known memories. Look for separate HTTP calls to a memory/retrieval endpoint distinct from the main GetChatMessage call.

## 3. Injected Behavior Selection

**Known:** 6 behavioral directives appended after system prompt XML sections. Not inside any XML section. Identical across V2.3.9 and V2.3.15 (same user, same workspace).

**Unknown:**
- Static per user, or A/B tested?
- Selected based on user behavior patterns?
- Conversation-type dependent?
- How many total behaviors exist in the pool?
- Controlled by an unidentified feature flag?

**Requires:** Capture from different user accounts, same user over multiple weeks.

## 4. Checkpoint Trigger Heuristic

**Known:** `truncation_threshold_tokens: 100000`. Summarizers fire proactively at 5 points (231 KB, 367 KB, 379 KB, 490 KB, 499 KB). Only 1 checkpoint applied (499 KB → 388 KB). Context grew back to 506 KB without second checkpoint.

**Unknown:**
- Why do summarizers fire at 231 KB (well below threshold)?
- What determines WHEN prepared checkpoint is applied?
- Pure token count, or factors in turn count/time/content?
- Why no second checkpoint at 506 KB? (Cooldown? Once-per-session limit?)
- Is threshold measured in tokens or characters?

**Requires:** Longer capture sessions, potential flag manipulation.

## 5. Plan Tier Differences

**Known:** Current captures from `TEAMS_TIER_DEVIN_MAX`. 4 models in config. Team config includes `allowMcpServers`, `allowAutoRunCommands`.

**Unknown:**
- Models available on Free/Pro/Team tiers?
- System prompt differences by tier?
- Feature flag differences?
- Rate limiting differences?
- Is brain planner Max-only?

**Requires:** Capture from Free-tier account, cross-tier comparison.

## 6. Authentication and Integrity

**Known:** Auth envelope: session JWT, OS metadata, hardware JSON, user ID, API key JWT, content hash (SHA-256), signature (384-char hex), team ID.

**Unknown:**
- What content is hashed?
- Signature scheme (HMAC? RSA? ECDSA?)?
- Is this integrity protection, DRM, or anti-tampering?
- Can requests be replayed with modified content?

**Requires:** `extension.js` signing logic reverse-engineering, replay testing.

## 7. Feature Flag Delivery and Segmentation - PARTIALLY RESOLVED

**Known:** 47 flags captured (updated from 40 via schema-less deserialization). Unleash service at `unleash.codeium.com`. RecordCortexExecutionMetadata reports experiment outcomes. Flags delivered as Field 9 sub-messages in every GetChatMessage request.

**Resolved (CSMP-IN11):**
- Flags are **byte-for-byte identical** between V2.3.9 and V2.3.15 (same user, 1 day apart) [PROVEN]
- No per-request randomization observed - delivery is **static per account** [VERIFIED]
- Wire format: each flag is a sub-message with F5=name, F6=enabled, F7=variant, F1=numeric_id, F2/F3=payload

**Still unknown:**
- User segmentation method for A/B tests (requires second account)
- Flag propagation speed
- Flags assigned to other user segments

**Requires:** Multi-account capture.

## 8. Instruction Priority Chain

**Known:** User rules claim "MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION". System prompt claims tool safety constraints "cannot be overridden by USER". These two claims potentially conflict.

**Unknown:**
- Which actually wins when user rules conflict with safety?
- Does positional salience override explicit precedence?
- Do checkpoint behavioral anchors influence behavior?
- Does the brain respect user rules, or only the generator?

**Requires:** Systematic conflict tests, compliance rate measurement.

## 9. WorkspaceLayout Injection Conditions

**Known:** `WorkspaceLayout.txt` (147 lines, workspace file tree) present in V2.3.9 extraction. Absent in V2.3.15 extraction. The `<workspace_information>` section contains a "file tree snapshot (frozen at conversation start)".

**Unknown:**
- Conditional on workspace size (file count threshold)?
- Feature flag toggled between captures?
- Related to `<ide_metadata>` instead?
- Injected only on first GetChatMessage of a conversation?
- Maximum file count before truncation?

**Requires:** Capture in minimal vs large workspace, compare both sessions' raw extractions.

## 10. UI-Level Agent Behaviors

**Known:** Todo list renders with visual task icons [ASSUMED]. Status maps to icons (in_progress = filled, pending = empty, completed = checkmark) [ASSUMED]. Priority has no visual distinction [ASSUMED]. "N / M tasks done" counter in header [ASSUMED].

**Unknown:**
- Can users click task circles to toggle status?
- Does UI interaction trigger a new GetChatMessage?
- How does "suggested responses" work (`ENABLE_SUGGESTED_RESPONSES` disabled)?
- What does `COLLAPSE_ASSISTANT_MESSAGES` do when enabled?
- How does the annotation system work (`cascade-add-annotation`)?

**Requires:** Todo UI interaction testing with network traffic capture.

## Investigation Priority

**High value, high effort:**
1. Brain planner internals (`extension.js` reverse-engineering)
2. Plan tier differences (second account needed)
3. Instruction priority chain (systematic experiment design)

**Medium value:**
4. Checkpoint trigger heuristic (longer sessions)
5. Feature flag segmentation (multi-account comparison)
6. Memory system internals (multi-session observation)
7. WorkspaceLayout injection conditions (minimal vs large workspace capture)
8. UI-level agent behaviors (todo interaction + network capture)

## Sources

- `_INFO_WINDSURF_CASCADE_OPEN_QUESTIONS.md [CSMP-IN05]`


---

# Appendix B: Source Data and Methodology

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

## 1. Session Captures

Three sessions captured via mitmproxy (HTTPS interception):

- **V2.3.9** (2026-05-28 12:49): Windsurf 2.3.9, initial exploration session
- **V2.3.15** (2026-05-29 13:59): Windsurf 2.3.15, full analysis session (93 RPC calls, 99 responses, 506 KB max context)
- **V2.3.15** (2026-05-30 15:55): Windsurf 2.3.15, third capture (MCP verification)

Capture files stored in session folders with version suffix. Schema-less protobuf deserialization extracts all fields without requiring `.proto` definitions.

## 2. Extraction Pipeline

1. **mitmproxy** intercepts HTTPS traffic between Windsurf IDE and `server.self-serve.windsurf.com`
2. **Custom Python extractor** strips Connect envelope (5-byte header), decompresses gzip, then extracts printable strings at configurable minimum length (20 chars default)
3. **Schema-less protobuf deserializer** (`07_deserialize_fields.py`) decodes all field numbers, wire types, and nested sub-messages without `.proto` definitions. Handles concatenated gRPC frames in streaming responses.
4. **String ordering** preserved from protobuf field sequence (position = semantic meaning)
5. **File naming**: `[4-digit-sequence]_[RPC-method]_[request|response].txt`
6. **Summary extractor** (`08_extract_summary.py`) produces compact diffable outputs (~116 KB per session) for git check-in

## 3. Windsurf Version Inventory

- **V2.3.9**: Extension version `2.3.9`, captured 2026-05-29
- **V2.3.15**: Extension version `2.3.15`, captured 2026-05-29 (same day, updated)
- Both on Windows 11, same user account (`TEAMS_TIER_DEVIN_MAX`)

## 4. Cross-Version Stability (V2.3.9 vs V2.3.15)

Binary comparison of deserialized fields between the two versions reveals [PROVEN]:

- **System prompt**: Byte-for-byte identical (52,877 bytes each)
- **Feature flags**: Byte-for-byte identical (4,551 bytes, 47 sub-messages)
- **Protocol structure**: Same field numbers, same wire types, same nesting
- **Only difference**: Version string in auth envelope (`2.3.9` vs `2.3.15`)

This confirms the captured behavior is stable across minor version bumps and not an artifact of a specific build. All findings in this ebook apply to both versions unless explicitly noted.

## 5. Analysis Methodology

**Evidence labeling:**
- `[PROVEN]` - directly observed in wire data (string match or structural evidence)
- `[TESTED]` - verified across multiple observations or captures
- `[ASSUMED]` - inferred from circumstantial evidence, not directly provable from wire data

**Source document chain:**
1. Raw captures → extraction pipeline → string files
2. String files → INFO documents (analysis with evidence labels)
3. INFO documents → ebook chapters (restructured, no new claims without evidence)

**Verification principle:** Every factual claim in this ebook traces back to a specific string position in a specific extracted request/response file. Claims without evidence are in [Appendix A](#appendix-a-open-questions).

## 6. Limitations

- Only client-side observable (cannot see server-internal routing)
- Only one user tier captured (`TEAMS_TIER_DEVIN_MAX`)
- Brain planner behavior inferred from configuration, not direct observation
- Single workspace, single machine (Windows 11, PowerShell)
- Extended thinking content not confirmed visible in response stream
- Only one user account captured (cannot verify per-account flag segmentation)


---

# Appendix C: Cross-Reference Table

**Windsurf Version**: V2.3.15 (captured 2026-05-29)

## Chapter-to-Source Mapping

- **Part 1: Introduction** → Synthesized from all CSMP-IN02 through CSMP-IN10
- **Ch1: Multi-Model Architecture** → `CSMP-IN02` sections 7-9 + `CSMP-IN11` sections 5, 9, 10
- **Ch2: The Memory System** → `CSMP-IN02` sections 5.5, 6.5 + `CSMP-IN05` section 2 + `CSMP-IN09` section 2
- **Ch3: The Wire Protocol** → `CSMP-IN02` sections 1-4
- **Ch4: The GetChatMessage Request** → `CSMP-IN02` section 5 + `CSMP-IN06` section 1
- **Ch5: The Response Stream** → `CSMP-IN11` section 8
- **Ch6: The System Prompt** → `CSMP-IN07`
- **Ch7: The Tool Call Round Trip** → `CSMP-IN06`
- **Ch8: Core Coding Tools** → `CSMP-IN08`
- **Ch9: Platform Tools** → `CSMP-IN09`
- **Ch10: MCP-Provided Tools** → `CSMP-IN10`
- **Ch11: Context Management** → `CSMP-IN03` + `CSMP-IN04`
- **Ch12: Context Budget** → `CSMP-IN08` s6 + `CSMP-IN09` s9 + `CSMP-IN10` s8
- **Appendix A: Open Questions** → `CSMP-IN05` + `CSMP-IN11` section 11
- **Appendix B: Methodology** → Session metadata
- **Appendix C: Cross-Reference** → (this document)

## Source Document Index

- **CSMP-IN02** - `_INFO_HOW_WINDSURF_CASCADE_WORKS.md`: Core architecture, wire protocol, request structure, multi-model pipeline, feature flags
- **CSMP-IN03** - `_INFO_HOW_WINDSURF_CASCADE_CHECKPOINTS_WORK.md`: Checkpoint mechanism, summarizer pipeline, truncation threshold
- **CSMP-IN04** - `_INFO_HOW_WINDSURF_CASCADE_WORKS_TODO_LIST.md`: Todo list persistence, checkpoint extraction, deterministic state preservation
- **CSMP-IN05** - `_INFO_WINDSURF_CASCADE_OPEN_QUESTIONS.md`: Architectural unknowns, investigation priorities
- **CSMP-IN06** - `_INFO_HOW_WINDSURF_CASCADE_TOOL_CALL_ROUND_TRIP.md`: Tool call wire format, conversation history structure, context growth mechanics
- **CSMP-IN07** - `_INFO_HOW_WINDSURF_CASCADE_SYSTEM_PROMPT.md`: System prompt structure, 13 XML regions, behavioral constraints, instruction priority
- **CSMP-IN08** - `_INFO_HOW_WINDSURF_CASCADE_TOOLS_PART_1.md`: 12 core coding tools (reading, editing, execution), wire schemas, I/O profiles
- **CSMP-IN09** - `_INFO_HOW_WINDSURF_CASCADE_TOOLS_PART_2.md`: 15 platform tools (web, state, deployment, MCP meta, terminal)
- **CSMP-IN10** - `_INFO_HOW_WINDSURF_CASCADE_TOOLS_PART_3.md`: 25 MCP-provided tools (Playwright, Playwriter), conditional injection
- **CSMP-IN11** - `_INFO_CASCADE_ADDITIONAL_ANALYSIS_1.md`: Schema-less protobuf deserialization, response stream structure, model registry (135 models), agent registry, version comparison, 47 feature flags wire format

## Evidence Label Key

- **[PROVEN]** - Directly observed in wire data
- **[TESTED]** - Verified across multiple observations
- **[ASSUMED]** - Inferred, not directly provable from wire data


---

