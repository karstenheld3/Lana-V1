# Extended Thinking

**Doc ID**: ANTAPI-IN15
**Goal**: Document extended thinking configuration, thinking blocks, adaptive thinking, and effort control
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` for Messages API request/response schema

## Summary

Extended thinking enables Claude to show its internal reasoning process before generating a final response. When enabled via the `thinking` parameter, responses include `thinking` content blocks with Claude's step-by-step analysis, followed by `text` blocks with the final answer. Two modes exist: manual (`type: "enabled"` with `budget_tokens`) and adaptive (`type: "adaptive"` with effort levels). On Opus 5, effort is the primary control (supports low/medium/high/xhigh/max); disabling thinking at xhigh or max returns 400. On Fable 5/Mythos 5 and Sonnet 5, adaptive thinking is always on: `thinking: {"type": "disabled"}` and manual `budget_tokens` both return 400. The `usage.output_tokens_details.thinking_tokens` field (since May 27) reports how many output tokens were thinking.

## Key Facts

- **Parameter**: `thinking` object in request body
- **Manual Mode**: `{"type": "enabled", "budget_tokens": N}` (deprecated on Opus 4.6; removed on Sonnet 5/Fable 5/Mythos 5)
- **Adaptive Mode**: `{"type": "adaptive"}` with effort parameter
- **Effort Levels**: low, medium, high (default on Opus 5), xhigh, max
- **Response Blocks**: `thinking` (reasoning) + `text` (final answer)
- **Thinking Signature**: Each thinking block includes a `signature` for integrity verification
- **Max Output**: Opus 5, 4.8, 4.7, 4.6, Sonnet 5, Fable 5, Mythos 5 support 128K output tokens; earlier models 64K
- **Display Modes**: `"summarized"` or `"omitted"` (default on Opus 5, 4.8, 4.7, Fable 5, Mythos 5)
- **Thinking Token Breakdown**: `usage.output_tokens_details.thinking_tokens` in response
- **Budget Constraint**: `budget_tokens` must be less than `max_tokens`
- **Status**: GA

## Supported Models

- **claude-opus-5** - Manual and adaptive thinking; effort primary control (low/medium/high/xhigh/max); disabling thinking at xhigh/max returns 400; display defaults to "omitted"
- **claude-opus-4-8** - Adaptive only; `thinking.type: "enabled"` returns 400 ("not supported for this model"); effort defaults to high; display defaults to "omitted"
- **claude-opus-4-7** - Manual and adaptive; display defaults to "omitted"
- **claude-fable-5** - Adaptive only; `disabled` and manual `budget_tokens` return 400; display defaults to "omitted"
- **claude-mythos-5** - Adaptive only; same restrictions as Fable 5; display defaults to "omitted"
- **claude-sonnet-5** - Adaptive only; manual extended thinking removed (400); display defaults to "omitted"
- **claude-opus-4-6** - Adaptive thinking only; manual mode deprecated; display defaults to "summarized"
- **claude-sonnet-4-6** - Both manual and adaptive thinking, plus interleaved mode
- **claude-opus-4-5-20251101** - Manual thinking (`type: "enabled"` with `budget_tokens`) and effort control (`output_config.effort` without thinking); `thinking.type: "adaptive"` returns 400. The `effort-2025-11-24` beta header is no longer required (effort works without it as of 2026)
- **claude-haiku-4-5-20251001** - Manual thinking only; `thinking.type: "adaptive"` returns 400

## Configuration

### Manual Mode (type: "enabled")

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000,
    },
    messages=[
        {"role": "user", "content": "Prove there are infinitely many primes p where p mod 4 = 3"}
    ],
)

for block in message.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking[:200]}...")
    elif block.type == "text":
        print(f"Answer: {block.text}")
```

### Adaptive Mode (type: "adaptive")

```python
import anthropic

client = anthropic.Anthropic()

# Adaptive thinking with effort control
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    messages=[
        {"role": "user", "content": "What is 2 + 2?"}
    ],
)
```

### Controlling Effort Level

```python
# Low effort for simple tasks
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    output_config={"effort": "low"},
    messages=[{"role": "user", "content": "Classify this sentiment: Great product!"}],
)

# Max effort for capability-critical work (Opus 5)
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=32000,
    thinking={"type": "adaptive"},
    output_config={"effort": "max"},
    messages=[{"role": "user", "content": "Design an optimal database schema for..."}],
)

# Opus 5: thinking cannot be disabled at xhigh or max effort
# This will return a 400 error:
# client.messages.create(
#     model="claude-opus-5",
#     thinking={"type": "disabled"},
#     output_config={"effort": "xhigh"},  # ERROR
#     ...
# )
```

## Response Format

```json
{
  "content": [
    {
      "type": "thinking",
      "thinking": "Let me analyze this step by step...",
      "signature": "WaUjzkypQ2mUEVM36O2TxuC06KN8xyfbJwyem2dw3URve..."
    },
    {
      "type": "text",
      "text": "Based on my analysis..."
    }
  ]
}
```

### Response Content Blocks

- **thinking** - Claude's internal reasoning (may be summarized in Claude 4+ models)
  - `thinking` (`string`) - Reasoning text
  - `signature` (`string`) - Integrity verification signature
- **redacted_thinking** - Thinking that was redacted for safety reasons
  - `data` (`string`) - Encrypted data
- **text** - Final response text

## Controlling Thinking Display

The `display` field on the thinking configuration controls how thinking content is returned:

- **`"summarized"`** - Thinking blocks contain summarized thinking text. Default on Opus 4.6, Sonnet 4.6, and earlier Claude 4 models
- **`"omitted"`** - Thinking blocks returned with empty `thinking` field; `signature` preserved for multi-turn continuity. Default on Opus 5, 4.8, 4.7, Fable 5, Mythos 5, and Sonnet 5. Reduces time-to-first-text-token when streaming

Key considerations for `display: "omitted"`:
- Still charged for full thinking tokens (reduces latency, not cost)
- Pass thinking blocks back unchanged in multi-turn; server decrypts signature
- Invalid with `thinking.type: "disabled"`
- With `thinking.type: "adaptive"`, no thinking block produced if model skips thinking
- Switching display values between turns is supported

## Extended Thinking with Tool Use

When using tools with extended thinking, Claude can think before each tool call and after receiving results. In interleaved thinking mode (Sonnet 4.6), thinking blocks appear between tool use and tool result blocks.

### Preserving Thinking Blocks

In multi-turn conversations with thinking enabled, pass thinking and redacted_thinking blocks back in assistant messages to maintain context:

```python
# First turn
response1 = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "Analyze this data..."}],
)

# Second turn - include thinking blocks from first response
messages = [
    {"role": "user", "content": "Analyze this data..."},
    {"role": "assistant", "content": response1.content},  # includes thinking blocks
    {"role": "user", "content": "Now compare with this..."},
]

response2 = client.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=messages,
)
```

## Streaming with Thinking

Thinking content streams via `thinking_delta` events, followed by `signature_delta` before `content_block_stop`:

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-opus-5",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "Solve this complex problem..."}],
) as stream:
    for event in stream:
        if hasattr(event, "type"):
            if event.type == "content_block_start":
                if event.content_block.type == "thinking":
                    print("[THINKING]")
                elif event.content_block.type == "text":
                    print("\n[ANSWER]")
            elif event.type == "content_block_delta":
                if event.delta.type == "thinking_delta":
                    print(event.delta.thinking, end="")
                elif event.delta.type == "text_delta":
                    print(event.delta.text, end="")
```

## TypeScript Examples

### Manual Thinking (Sonnet 4.5, Haiku 4.5, Opus 4.5)

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const message = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 16000,
  thinking: { type: "enabled", budget_tokens: 10000 },
  messages: [
    { role: "user", content: "Prove there are infinitely many primes p where p mod 4 = 3" },
  ],
});

for (const block of message.content) {
  if (block.type === "thinking") console.log("Thinking:", block.thinking.slice(0, 200));
  else if (block.type === "text") console.log("Answer:", block.text);
}
// usage.output_tokens_details.thinking_tokens reports thinking token count
```

### Adaptive Thinking with Effort (Opus 4.8, Fable 5, Opus 5)

```typescript
// Low effort - fast, minimal thinking
const low = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  output_config: { effort: "low" },
  messages: [{ role: "user", content: "Classify this sentiment: Great product!" }],
});
// Simple task: thinking_tokens may be 0, no thinking block

// High effort - deeper analysis, thinking blocks likely
const high = await client.messages.create({
  model: "claude-fable-5",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  output_config: { effort: "high" },
  messages: [{ role: "user", content: "Design an optimal database schema for..." }],
});
// Complex task: content includes [{ type: "thinking", ... }, { type: "text", ... }]
```

### Effort-Only (Opus 4.5)

Opus 4.5 uses `output_config.effort` without `thinking: adaptive`. No beta header required.

```typescript
const message = await client.messages.create({
  model: "claude-opus-4-5-20251101",
  max_tokens: 1024,
  output_config: { effort: "high" },
  messages: [{ role: "user", content: "Summarize this article..." }],
});
// Response: [{ type: "text", text: "..." }] - no thinking block
// Opus 4.5 also supports thinking: { type: "enabled", budget_tokens: N } for explicit thinking
```

### Streaming with Thinking

```typescript
const stream = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 16000,
  thinking: { type: "enabled", budget_tokens: 10000 },
  messages: [{ role: "user", content: "Solve this complex problem..." }],
  stream: true,
});

for await (const event of stream) {
  if (event.type === "content_block_start") {
    if (event.content_block.type === "thinking") console.log("[THINKING]");
    else if (event.content_block.type === "text") console.log("\n[ANSWER]");
  } else if (event.type === "content_block_delta") {
    if (event.delta.type === "thinking_delta") process.stdout.write(event.delta.thinking);
    else if (event.delta.type === "text_delta") process.stdout.write(event.delta.text);
  }
}
```

### Multi-turn with Thinking Blocks

```typescript
// First turn
const response1 = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 16000,
  thinking: { type: "enabled", budget_tokens: 10000 },
  messages: [{ role: "user", content: "Analyze this data..." }],
});

// Second turn - include thinking blocks from first response to maintain context
const response2 = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 16000,
  thinking: { type: "enabled", budget_tokens: 10000 },
  messages: [
    { role: "user", content: "Analyze this data..." },
    { role: "assistant", content: response1.content },  // includes thinking blocks
    { role: "user", content: "Now compare with this..." },
  ],
});
```

## Token Management

- `budget_tokens` sets the max thinking tokens (must be < `max_tokens`)
- `max_tokens` covers both thinking and response tokens
- Claude may not use the entire budget, especially above 32K
- With interleaved thinking + tools, the token limit becomes the entire context window
- Thinking tokens are billed as output tokens

## Pricing

Thinking tokens are billed at the same rate as output tokens for the model used. The `usage.output_tokens_details.thinking_tokens` field (since May 27, 2026) reports the thinking portion of billed output tokens. When streaming, this appears only on the final `message_delta` event.

## Feature Compatibility Restrictions

- **Not compatible with**: `temperature` modifications (400 on Opus 4.7+/Sonnet 5/Fable 5), `top_k` modifications, forced tool use (`tool_choice: {type: "tool", name: "..."}`))
- **top_p**: Limited to values between 0.95 and 1.0 when thinking is enabled
- **No pre-fill**: Cannot use assistant pre-fill when thinking is enabled
- **Caching**: Changes to thinking budget invalidate cached prompt prefixes that include messages (cached system prompts and tool definitions still work)

## Performance Constraints

- **Minimum budget**: 1,024 tokens
- **Streaming required**: SDKs require streaming when `max_tokens` > 21,333 to avoid HTTP timeouts (client-side validation, not API restriction). Use `.stream()` with `.get_final_message()` for non-incremental processing
- **Large budgets (>32K)**: Use batch processing to avoid networking issues; long-running requests can hit system timeouts and open connection limits
- **max_tokens strictly enforced**: On Claude 3.7+ and 4 models, `prompt_tokens + max_tokens` must not exceed context window (returns validation error, no longer silently adjusted)
- **Latency**: Set `display: "omitted"` on thinking config to reduce time-to-first-text-token when your app does not display thinking content

## Gotchas and Quirks

- On Opus 4.6, `type: "enabled"` with `budget_tokens` is deprecated; on Sonnet 5/Fable 5/Mythos 5 it returns 400
- On Opus 5, `thinking: {"type": "disabled"}` at effort xhigh or max returns 400
- On Fable 5/Mythos 5, `thinking: {"type": "disabled"}` is not supported (400 error)
- Fable 5 produces thinking blocks by default even without any `thinking` parameter; code consuming Fable 5 responses must always handle `thinking` content blocks
- On Opus 4.8, adaptive thinking triggers reasoning only when needed, reducing wasted tokens vs 4.7
- Thinking blocks include a `signature` field for integrity verification; do not modify thinking content
- `redacted_thinking` blocks appear when safety classifiers flag reasoning content
- In Claude 4+ models, `budget_tokens` applies to full thinking, not summarized output
- Summarized thinking: Claude 4+ models internally produce full reasoning but may return a summarized version
- Cannot disable thinking mid-conversation if it was enabled in earlier turns (Opus 4.5+)
- Thinking blocks from earlier turns should be passed back in multi-turn conversations
- Previous thinking blocks are automatically ignored and not counted toward context usage
- Thinking budget is a target, not a strict limit; actual usage may vary

## Task Budgets (Beta)

Task budgets let you tell Claude how many tokens it has for a full agentic loop (thinking + tool calls + tool results + output). The model sees a running countdown and finishes gracefully as the budget is consumed. Requires the `task-budgets-2026-03-13` beta header.

```python
with client.beta.messages.stream(
    model="claude-opus-5",
    max_tokens=128000,
    output_config={
        "effort": "high",
        "task_budget": {"type": "tokens", "total": 64000},
    },
    messages=[{"role": "user", "content": "Review the codebase and propose a refactor plan."}],
    betas=["task-budgets-2026-03-13"],
) as stream:
    response = stream.get_final_message()
```

Supported on Opus 5, Fable 5, Mythos 5, Opus 4.8, and Opus 4.7. Set `task_budget` inside `output_config` alongside `effort`.

## Related Endpoints

- `_INFO_ANTAPI-51_Effort_Adaptive_Params.md [ANTAPI-IN51]` - **Comprehensive effort and adaptive reasoning reference** with Python + TypeScript examples, routing logic, and config-driven approach

- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Messages API (thinking parameter)
- `_INFO_ANTAPI-09_STREAMING.md [ANTAPI-IN09]` - Streaming thinking deltas
- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` - Thinking with tool use

## Sources

- ANTAPI-SC-ANTH-THINK - https://platform.claude.com/docs/en/build-with-claude/extended-thinking - Full thinking guide
- ANTAPI-SC-ANTH-ADAPT - https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking - Adaptive thinking
- ANTAPI-SC-ANTH-EFFORT - https://platform.claude.com/docs/en/build-with-claude/effort - Effort control

## SDK Verification

All 5 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `types/thinking_config_enabled_param.py`: `ThinkingConfigEnabledParam(type="enabled", budget_tokens=int, display?="summarized"|"omitted")`
- `types/thinking_config_adaptive_param.py`: `ThinkingConfigAdaptiveParam(type="adaptive", display?="summarized"|"omitted")`
- `types/output_config_param.py`: `OutputConfigParam(effort?="low"|"medium"|"high"|"xhigh"|"max", format?=JSONOutputFormatParam)`
- `resources/messages/messages.py` (line 119): `thinking: ThinkingConfigParam` param confirmed

**Notes**:
- `output_config={"effort": "low"}` verified - SDK supports `Literal["low", "medium", "high", "max"]`
- SDK supports full effort ladder: low, medium, high, xhigh, max
- `display` option in thinking config confirmed: `"summarized"` (default) or `"omitted"`

## Document History

**[2026-07-27]**
- Fixed: Opus 4.8 changed from "Manual and adaptive" to "Adaptive only" (live API test confirms `thinking.type: "enabled"` returns 400)
- Added: Opus 4.5 to Supported Models (manual thinking + effort control, no adaptive)
- Added: Haiku 4.5 corrected to "Manual only" (adaptive returns 400)
- Added: Note that `effort-2025-11-24` beta header is no longer required for Opus 4.5
- Added: Note that Fable 5 produces thinking blocks by default without thinking parameter
- Added: TypeScript Examples section (manual thinking, adaptive + effort, effort-only Opus 4.5, streaming with thinking, multi-turn)
- Source: `_INFO_ANTAPI-50_SDK_Model_Methods.md` (22 live API tests)

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: Opus 5 with effort as primary control (xhigh level added)
- Added: Opus 4.8 with adaptive thinking improvements
- Added: Fable 5/Mythos 5 (adaptive only, no disable/manual)
- Added: Sonnet 5 (adaptive only, manual removed)
- Added: usage.output_tokens_details.thinking_tokens field
- Added: Opus 5 restriction: cannot disable thinking at xhigh/max effort
- Changed: Display defaults updated for new models

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references to claude-opus-5
- Added: Opus 4.7 and Mythos Preview with display "omitted" default
- Changed: Expanded display field documentation (summarized vs omitted, per-model defaults)

**[2026-03-20 06:30]**
- Added: SDK verification section (anthropic 0.120.0, all 5 examples valid)
- Added: Note about "max" effort level available in SDK

**[2026-03-20 05:00]**
- Added: Feature compatibility restrictions (no temperature, top_k, forced tool use, pre-fill)
- Added: Performance constraints (min 1,024 budget, streaming >21,333, batch >32K, strict max_tokens)
- Added: display "omitted" option, caching invalidation behavior

**[2026-03-20 03:10]**
- Initial documentation created from extended thinking guide
