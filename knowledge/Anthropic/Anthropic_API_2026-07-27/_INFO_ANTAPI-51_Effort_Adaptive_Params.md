# Effort-Based and Adaptive Reasoning Parameters

**Doc ID**: ANTAPI-IN51
**Goal**: Comprehensive reference for effort and adaptive thinking API parameters across all model generations, in both Python and TypeScript
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-15_EXTENDED_THINKING.md [ANTAPI-IN15]` for thinking configuration details
- `_INFO_ANTAPI-50_SDK_Model_Methods.md [ANTAPI-IN50]` for live API test results

## Summary

Claude models use different API parameter patterns to control reasoning depth, depending on model generation. There are four distinct methods: `temperature` (no reasoning control), `thinking` (manual budget), `effort` (output_config only), and `adaptive_thinking` (model-controlled with effort). Sending the wrong parameter type for a model returns HTTP 400 immediately. This document provides copy-paste-ready code for every method in both Python and TypeScript, verified against live API calls.

## Model Method Routing

```
Model                  Method             API Parameters
-----                  ------             --------------
Sonnet 4.5, Haiku 4.5  thinking           thinking: {type: "enabled", budget_tokens: N}
Opus 4.5               effort             output_config: {effort: "low"|"medium"|"high"}
Opus 4.6+              adaptive_thinking   thinking: {type: "adaptive"} + output_config: {effort: ...}
Fable 5, Mythos 5      adaptive_thinking   thinking: {type: "adaptive"} + output_config: {effort: ...}
Sonnet 5, Opus 5       adaptive_thinking   thinking: {type: "adaptive"} + output_config: {effort: ...}
Claude 3.5, 3          temperature         temperature: N (no reasoning control)
```

**Error matrix** (what NOT to do):

```
Parameter sent                       4.5-gen models         4.6+ models
--------------                       --------------         -----------
thinking: {type: "adaptive"}         400 (not supported)    OK
thinking: {type: "enabled"}          OK                     400 (not supported)*
output_config: {effort} alone        OK (Opus 4.5 only)     OK (but add thinking: adaptive)
```

*Exception: Opus 4.7 may still accept `thinking: enabled` but it is deprecated.

## Method 1: thinking (Manual Budget) - 4.5 Generation

For Sonnet 4.5, Haiku 4.5, and Opus 4.5. The caller sets an explicit token budget for thinking. The model always thinks when enabled.

**Constraints:**
- `budget_tokens` must be less than `max_tokens`
- Minimum budget: 1,024 tokens
- If `max_tokens <= budget_tokens`, the API returns 400

### Python

```python
import anthropic

client = anthropic.Anthropic()

# Sonnet 4.5 with thinking
message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "Analyze this code for bugs..."}],
)

for block in message.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking[:200]}...")
    elif block.type == "text":
        print(f"Answer: {block.text}")

# Token breakdown
print(f"Thinking tokens: {message.usage.output_tokens_details.thinking_tokens}")
print(f"Total output: {message.usage.output_tokens}")
```

### TypeScript

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const message = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 16000,
  thinking: { type: "enabled", budget_tokens: 10000 },
  messages: [{ role: "user", content: "Analyze this code for bugs..." }],
});

for (const block of message.content) {
  if (block.type === "thinking") {
    console.log("Thinking:", block.thinking.slice(0, 200));
  } else if (block.type === "text") {
    console.log("Answer:", block.text);
  }
}

console.log("Thinking tokens:", message.usage.output_tokens_details?.thinking_tokens);
```

### Streaming

Thinking blocks stream via `thinking_delta` events, followed by `signature_delta`:

```python
# Python streaming
with client.messages.stream(
    model="claude-sonnet-4-5-20250929",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "Solve this step by step..."}],
) as stream:
    for event in stream:
        if hasattr(event, "type"):
            if event.type == "content_block_start":
                if event.content_block.type == "thinking":
                    print("[THINKING]", end="")
                elif event.content_block.type == "text":
                    print("\n[ANSWER]", end="")
            elif event.type == "content_block_delta":
                if event.delta.type == "thinking_delta":
                    print(event.delta.thinking, end="")
                elif event.delta.type == "text_delta":
                    print(event.delta.text, end="")
```

```typescript
// TypeScript streaming
const stream = await client.messages.create({
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 16000,
  thinking: { type: "enabled", budget_tokens: 10000 },
  messages: [{ role: "user", content: "Solve this step by step..." }],
  stream: true,
});

for await (const event of stream) {
  if (event.type === "content_block_start") {
    if (event.content_block.type === "thinking") process.stdout.write("[THINKING] ");
    else if (event.content_block.type === "text") process.stdout.write("\n[ANSWER] ");
  } else if (event.type === "content_block_delta") {
    if (event.delta.type === "thinking_delta") process.stdout.write(event.delta.thinking);
    else if (event.delta.type === "text_delta") process.stdout.write(event.delta.text);
  }
}
```

## Method 2: effort (Output Config Only) - Opus 4.5

Opus 4.5 supports `output_config: {effort}` without `thinking: adaptive`. The model adjusts internal processing but does NOT produce thinking blocks. No beta header required (the `effort-2025-11-24` header is obsolete).

Opus 4.5 ALSO accepts `thinking: {type: "enabled", budget_tokens: N}` (see Method 1). Choose based on need: effort for speed control without visible thinking, thinking for visible reasoning.

### Python

```python
import anthropic

client = anthropic.Anthropic()

# Effort-only: no thinking blocks in response
message = client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=8192,
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "Summarize this document..."}],
)

# Response contains only text blocks, no thinking
for block in message.content:
    if block.type == "text":
        print(block.text)
```

**Alternative using `extra_body`** (works with older SDK versions that lack native `output_config` support):

```python
# Older SDK workaround via extra_body
message = client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=8192,
    extra_body={"output_config": {"effort": "high"}},
    messages=[{"role": "user", "content": "Summarize this document..."}],
)
```

### TypeScript

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const message = await client.messages.create({
  model: "claude-opus-4-5-20251101",
  max_tokens: 8192,
  output_config: { effort: "high" },
  messages: [{ role: "user", content: "Summarize this document..." }],
});

// Response contains only text blocks
for (const block of message.content) {
  if (block.type === "text") console.log(block.text);
}
```

## Method 3: adaptive_thinking - 4.6+ Generation

For Opus 4.6+, Fable 5, Mythos 5, Sonnet 5, Opus 5. The model decides whether to think based on task complexity. Use `output_config.effort` to influence thinking depth.

**Key behaviors:**
- Simple tasks: `thinking_tokens: 0`, no thinking block in response
- Complex tasks: thinking block appears automatically
- Higher effort = more likely to think, deeper analysis
- Fable 5 and Mythos 5 think by default even WITHOUT the thinking parameter

### Python

```python
import anthropic

client = anthropic.Anthropic()

# Adaptive thinking - model decides whether to think
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "Design a database schema for a social network."}],
)

# Must handle both cases: with and without thinking blocks
for block in message.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking[:200]}...")
    elif block.type == "text":
        print(f"Answer: {block.text}")

thinking_tokens = getattr(
    message.usage, "output_tokens_details", None
)
if thinking_tokens:
    print(f"Thinking tokens: {thinking_tokens.thinking_tokens}")
```

**Alternative using `extra_body`** (for SDKs without native `output_config`):

```python
# Streaming with extra_body (from tested call-llm.py implementation)
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    extra_body={"output_config": {"effort": "high"}},
    messages=[{"role": "user", "content": "Explain quantum entanglement."}],
) as stream:
    response = stream.get_final_message()

for block in response.content:
    if hasattr(block, "text"):
        print(block.text)
        break
```

### TypeScript

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

// Adaptive thinking with effort control
const message = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  output_config: { effort: "high" },
  messages: [{ role: "user", content: "Design a database schema for a social network." }],
});

// Must handle both cases: with and without thinking blocks
for (const block of message.content) {
  if (block.type === "thinking") {
    console.log("Thinking:", block.thinking.slice(0, 200));
  } else if (block.type === "text") {
    console.log("Answer:", block.text);
  }
}

console.log("Thinking tokens:", message.usage.output_tokens_details?.thinking_tokens ?? 0);
```

### Effort Levels

```
Level    Behavior
-----    --------
low      Minimal thinking, fastest response, may skip thinking entirely
medium   Balanced (default on most models)
high     Deeper analysis, thinking blocks more likely
xhigh    Extended analysis (Opus 5 only at this level requires thinking enabled)
max      Maximum effort (Opus 5, Fable 5, Mythos 5)
```

### Streaming Adaptive Thinking

```python
# Python - streaming required for adaptive thinking in practice
# (non-streaming works but SDK may timeout on complex tasks)
with client.messages.stream(
    model="claude-fable-5",
    max_tokens=4096,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "Complex analysis task..."}],
) as stream:
    response = stream.get_final_message()
    for block in response.content:
        if hasattr(block, "text"):
            print(block.text)
```

```typescript
// TypeScript - streaming with event handling
const stream = await client.messages.create({
  model: "claude-fable-5",
  max_tokens: 4096,
  thinking: { type: "adaptive" },
  output_config: { effort: "high" },
  messages: [{ role: "user", content: "Complex analysis task..." }],
  stream: true,
});

for await (const event of stream) {
  if (event.type === "content_block_start") {
    if (event.content_block.type === "thinking") process.stdout.write("[THINKING] ");
    else if (event.content_block.type === "text") process.stdout.write("\n[ANSWER] ");
  } else if (event.type === "content_block_delta") {
    if (event.delta.type === "thinking_delta") process.stdout.write(event.delta.thinking);
    else if (event.delta.type === "text_delta") process.stdout.write(event.delta.text);
  }
}
```

## Effort-Level Mapping (Config-Driven Approach)

Both the deep-research-agent TypeScript implementation and the call-llm.py Python implementation use a configuration-driven approach to map abstract effort levels to model-specific parameters. This avoids hardcoding effort values per model.

### Configuration Structure

```json
{
  "effort_mapping": {
    "none":    { "temperature_factor": 0.0,  "anthropic_thinking_factor": 0.0,  "anthropic_adaptive_effort": "low",    "output_length_factor": 0.25 },
    "minimal": { "temperature_factor": 0.1,  "anthropic_thinking_factor": 0.01, "anthropic_adaptive_effort": "low",    "output_length_factor": 0.5 },
    "low":     { "temperature_factor": 0.2,  "anthropic_thinking_factor": 0.04, "anthropic_adaptive_effort": "low",    "output_length_factor": 0.5 },
    "medium":  { "temperature_factor": 0.35, "anthropic_thinking_factor": 0.1,  "anthropic_adaptive_effort": "medium", "output_length_factor": 0.75 },
    "high":    { "temperature_factor": 0.5,  "anthropic_thinking_factor": 0.32, "anthropic_adaptive_effort": "high",   "output_length_factor": 1.0 },
    "xhigh":   { "temperature_factor": 0.5,  "anthropic_thinking_factor": 1.0,  "anthropic_adaptive_effort": "xhigh",  "output_length_factor": 1.0 },
    "max":     { "temperature_factor": 0.5,  "anthropic_thinking_factor": 1.0,  "anthropic_adaptive_effort": "max",    "output_length_factor": 1.0 }
  }
}
```

### Routing Logic

```python
# Python routing (from call-llm.py)
def build_api_params(model, method, effort_level, effort_map, model_config):
    params = {}

    if method == "temperature":
        factor = effort_map[effort_level]["temperature_factor"]
        params["temperature"] = factor * model_config.get("temp_max", 2.0)

    elif method == "thinking":
        factor = effort_map[effort_level]["anthropic_thinking_factor"]
        budget = int(factor * model_config.get("thinking_max", 100000))
        if budget > 0:
            params["thinking"] = {"type": "enabled", "budget_tokens": budget}

    elif method == "effort":
        params["output_config"] = {"effort": effort_map[effort_level]["anthropic_adaptive_effort"]}

    elif method == "adaptive_thinking":
        params["thinking"] = {"type": "adaptive"}
        params["output_config"] = {"effort": effort_map[effort_level]["anthropic_adaptive_effort"]}

    # max_tokens from output_length
    output_factor = effort_map[effort_level]["output_length_factor"]
    params["max_tokens"] = int(output_factor * model_config.get("max_output", 16384))

    # Anthropic constraint: max_tokens must exceed budget_tokens
    if "thinking" in params and params["thinking"].get("budget_tokens", 0) > 0:
        if params["max_tokens"] <= params["thinking"]["budget_tokens"]:
            params["max_tokens"] = params["thinking"]["budget_tokens"] + 1024

    return params
```

```typescript
// TypeScript routing (from model-config.ts)
function buildApiParams(modelId: string, effortLevel: string): Record<string, unknown> {
  const rule = findPrefixRule(modelId);  // from model-registry.json
  const effort = effortMapping[effortLevel];
  const params: Record<string, unknown> = {};

  if (rule.method === "temperature") {
    params.temperature = effort.temperature_factor * (rule.temp_max ?? 2.0);
  } else if (rule.method === "thinking") {
    const budget = Math.floor(effort.anthropic_thinking_factor * (rule.thinking_max ?? 100000));
    if (budget > 0) params.thinking = { type: "enabled", budget_tokens: budget };
  } else if (rule.method === "effort") {
    params.output_config = { effort: effort.anthropic_adaptive_effort };
  } else if (rule.method === "adaptive_thinking") {
    params.thinking = { type: "adaptive" };
    params.output_config = { effort: effort.anthropic_adaptive_effort };
  }

  params.max_tokens = Math.floor(effort.output_length_factor * rule.max_output);

  // Anthropic constraint
  const thinking = params.thinking as { budget_tokens?: number } | undefined;
  if (thinking?.budget_tokens && (params.max_tokens as number) <= thinking.budget_tokens) {
    params.max_tokens = thinking.budget_tokens + 1024;
  }

  return params;
}
```

## Common Pitfalls

1. **Sending `thinking: {type: "adaptive"}` to 4.5-generation models** returns 400 immediately. Sonnet 4.5, Haiku 4.5, and Opus 4.5 only accept `thinking: {type: "enabled", budget_tokens: N}`.

2. **Sending `thinking: {type: "enabled"}` to 4.6+ models** returns 400 with "thinking.type.enabled is not supported for this model". Use `thinking: {type: "adaptive"}` instead.

3. **TypeScript SDK `betas` body parameter** does not exist in SDK v0.115.0. Passing `betas: [...]` in the request body causes `"betas: Extra inputs are not permitted"`. Use `headers` in RequestOptions instead:
   ```typescript
   await client.messages.create(body, { headers: { "anthropic-beta": "feature-name" } });
   ```

4. **Fable 5 always thinks** even without any `thinking` parameter. Code consuming Fable 5 responses must always handle `thinking` content blocks.

5. **`max_tokens` must exceed `budget_tokens`** for manual thinking. If violated, the API returns 400.

6. **Python `extra_body` vs direct `output_config`**: Modern SDK versions (0.120.0+) support `output_config` as a direct parameter. Older versions require `extra_body={"output_config": {...}}`. Both work.

7. **Opus 4.5 beta header obsolete**: The `effort-2025-11-24` beta header is no longer required. `output_config: {effort}` works directly.

## SDK Verification

All Python and TypeScript examples verified against:
- `anthropic` Python SDK 0.120.0
- `@anthropic-ai/sdk` TypeScript SDK 0.115.0
- Live API tests: `_INFO_ANTAPI-50_SDK_Model_Methods.md` (22 tests, 14 pass, 8 fail)
- Reference implementation: `call-llm.py` (tested with `test-call-llm.py`)

## Sources

- ANTAPI-SC-ANTH-THINK - https://platform.claude.com/docs/en/build-with-claude/extended-thinking
- ANTAPI-SC-ANTH-ADAPT - https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking
- ANTAPI-SC-ANTH-EFFORT - https://platform.claude.com/docs/en/build-with-claude/effort
- Reference implementation: `call-llm.py` and `test-call-llm.py` from `@skills:llm-evaluation`

## Document History

**[2026-07-27 13:00]**
- Initial document created from live API tests (ANTAPI-IN50), reference implementation (call-llm.py), and existing IN15 documentation
