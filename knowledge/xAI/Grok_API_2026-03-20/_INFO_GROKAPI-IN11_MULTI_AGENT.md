# INFO: Multi-Agent Research

**Doc ID**: GROKAPI-IN11
**Goal**: Multi-agent orchestration, configuration, pricing, prompting guide, limitations
**Version scope**: API v1 (beta), Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references
- `_INFO_GROKAPI-IN06_RESPONSES_API.md [GROKAPI-IN06]` for Responses API base

## Summary

Realtime Multi-agent Research is a **UNIQUE Grok feature** (no equivalent in OpenAI, Anthropic, or Gemini APIs) that orchestrates multiple AI agents working in parallel on deep research tasks. Using the `grok-4.20-multi-agent` model, a leader agent coordinates 4 or 16 sub-agents that simultaneously search the web, analyze data, and synthesize findings with citations. Agent count is configured via `agent_count` (xAI SDK) or `reasoning.effort` (OpenAI SDK/REST: "low"/"medium" = 4 agents, "high"/"xhigh" = 16 agents). Only the leader agent's output is returned; sub-agent state is encrypted and optionally included for multi-turn continuation. The feature uses the Responses API exclusively (Chat Completions not supported). Built-in server-side tools (web_search, x_search, code_execution, collections_search) are supported but client-side function calling is NOT. All tokens from all agents are billed, making multi-agent requests significantly more expensive than single-agent. Currently in beta with possible breaking changes. [VERIFIED] (GROKAPI-SC-XAI-MULTIAGENT | https://docs.x.ai/developers/model-capabilities/text/multi-agent)

## Key Facts

- [VERIFIED] Model: `grok-4.20-multi-agent` (only supported model) (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Agent counts: 4 agents or 16 agents (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Configuration mapping: xAI SDK `agent_count=4|16`, OpenAI SDK `reasoning.effort="low"|"medium"` (4) or `"high"|"xhigh"` (16) (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Only leader agent output exposed; sub-agent state encrypted (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Encrypted state included when `use_encrypted_content=True` (xAI SDK) (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Built-in tools supported: web_search, x_search, code_execution, collections_search (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Client-side tools (function calling) NOT supported (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Chat Completions API NOT supported - Responses API only (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] `max_tokens` parameter NOT supported (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] All tokens from all agents billed (leader + sub-agents) (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Beta feature - interface may include breaking changes (GROKAPI-SC-XAI-MULTIAGENT)

## Quick Reference

- **Model**: `grok-4.20-multi-agent`
- **API**: Responses API only (`POST /v1/responses`)
- **4 agents**: `agent_count=4` (xAI SDK) or `reasoning.effort="low"` (OpenAI SDK)
- **16 agents**: `agent_count=16` (xAI SDK) or `reasoning.effort="high"` (OpenAI SDK)
- **Best for 4 agents**: Quick research, focused queries
- **Best for 16 agents**: Deep research, complex multi-faceted topics

## Examples

### Basic Multi-Agent Research (xAI SDK)

```python
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4.20-multi-agent",
    tools=[web_search(), x_search()],
    include=["verbose_streaming"],
)

chat.append(user("Research the latest breakthroughs in quantum computing and summarize the key findings."))

is_thinking = True
for response, chunk in chat.stream():
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\n\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print(f"\n\nUsage: {response.usage}")
```

### Basic Multi-Agent Research (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4.20-multi-agent",
    reasoning={"effort": "high"},  # 16 agents for deep research
    input=[
        {
            "role": "user",
            "content": "Compare the top 3 EV manufacturers by battery technology, range, charging infrastructure, and 2025 sales projections.",
        },
    ],
    tools=[
        {"type": "web_search"},
        {"type": "x_search"},
    ],
)

print(response.output_text)
```

### 4-Agent Quick Research (cURL)

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4.20-multi-agent",
    "reasoning": {"effort": "low"},
    "input": [
      {"role": "user", "content": "What are the key differences between TCP and UDP?"}
    ],
    "tools": [
      {"type": "web_search"}
    ]
  }'
```

### Multi-Turn Deep Research

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Turn 1: Broad overview
r1 = client.responses.create(
    model="grok-4.20-multi-agent",
    reasoning={"effort": "medium"},
    input=[{"role": "user", "content": "What are the leading approaches to carbon capture technology?"}],
    tools=[{"type": "web_search"}, {"type": "x_search"}],
)
print(f"Turn 1: {r1.output_text[:200]}...")

# Turn 2: Narrow down
r2 = client.responses.create(
    model="grok-4.20-multi-agent",
    previous_response_id=r1.id,
    reasoning={"effort": "high"},
    input=[{"role": "user", "content": "Which of those has the best cost-per-ton economics today?"}],
    tools=[{"type": "web_search"}, {"type": "code_execution"}],
)
print(f"Turn 2: {r2.output_text[:200]}...")
```

## Prompting Guide

**Set scope and depth explicitly**:
```
BAD:  "Tell me about electric vehicles."
GOOD: "Compare the top 3 EV manufacturers by battery technology, range, charging infrastructure, and 2025 sales projections."
```

**Request structured output**:
```
GOOD: "Research pros and cons of microservices vs monolithic architecture. Present as comparison table with categories: scalability, complexity, deployment, team size."
```

**Specify sources or perspectives**:
```
GOOD: "Analyze environmental impact of LLM training, citing recent academic papers and industry reports from 2024-2025."
```

**Break complex research into conversation turns** rather than one massive prompt.

**Provide context when relevant**:
```
GOOD: "I'm building a fintech app for Southeast Asian markets. Research regulatory requirements for digital payments in Singapore, Indonesia, and Philippines."
```

## Differences from Other APIs

### vs OpenAI

- **UNIQUE**: No equivalent multi-agent orchestration in OpenAI API
- **Closest OpenAI feature**: OpenAI Assistants with tools, but single-agent only
- **Reasoning effort mapping**: xAI repurposes `reasoning.effort` for agent count (OpenAI uses it for thinking depth)

### vs Anthropic

- **UNIQUE**: No equivalent in Anthropic API
- **Closest Anthropic feature**: Extended thinking with tool use, but single-agent

### vs Gemini

- **UNIQUE**: No equivalent in Gemini API
- **Closest Gemini feature**: Grounding with Google Search, but single-agent

## Limitations and Known Issues

- [VERIFIED] Beta feature - API may have breaking changes (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] No client-side function calling support (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Chat Completions API not supported - must use Responses API (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] `max_tokens` parameter not supported (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Only leader agent output visible; sub-agent reasoning hidden (GROKAPI-SC-XAI-MULTIAGENT)
- [VERIFIED] Significantly higher token/tool usage than single-agent requests (GROKAPI-SC-XAI-MULTIAGENT)

## Sources

- GROKAPI-SC-XAI-MULTIAGENT | https://docs.x.ai/developers/model-capabilities/text/multi-agent | Accessed: 2026-03-20

## Document History

**[2026-03-20 03:35]**
- Initial document created with full multi-agent reference, examples, and prompting guide
