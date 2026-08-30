# Multi-Agent Orchestration

**Doc ID**: OAIAPI-IN95
**Goal**: Document Multi-Agent beta feature in the Responses API for parallel subagent coordination
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API context
- `_INFO_OAIAPI-IN93_GPT56_LATEST_MODEL.md [OAIAPI-IN93]` for GPT-5.6 context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Overview

Multi-Agent is a beta feature in the Responses API, released with GPT-5.6 (2026-07-09). It lets a GPT-5.6 instance coordinate multiple subagents in parallel and synthesize their results. Similar to ultra mode in ChatGPT/Codex, this reduces wall-clock time and improves performance for tasks that divide cleanly into independent workstreams.

Multi-Agent is the API-level building block for ultra-like experiences. In ChatGPT, ultra runs 4 agents in parallel by default; via the API, developers control agent count and configuration.

## Status

**Beta** - Available in the Responses API. Breaking changes possible. Iterate on developer feedback.

## How It Works

1. A request specifies multi-agent configuration with subagent definitions
2. GPT-5.6 fans work out to subagents that execute in parallel
3. Each subagent processes its workstream independently
4. Results are synthesized into a single coherent response
5. Higher token use traded for stronger results and faster time-to-result

## REST API

### Enable Multi-Agent

**Endpoint**: `POST /v1/responses`

```json
{
  "model": "gpt-5.6-sol",
  "input": "Research and compare cloud storage providers: AWS S3, Azure Blob, and GCP Cloud Storage.",
  "reasoning": {
    "effort": "high",
    "multi_agent": {
      "enabled": true,
      "agent_count": 3
    }
  }
}
```

## SDK Examples

### Python

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Research and compare cloud storage providers: AWS S3, Azure Blob, and GCP Cloud Storage.",
    reasoning={
        "effort": "high",
        "multi_agent": {
            "enabled": True,
            "agent_count": 3,
        },
    },
)
print(response.output_text)
```

## Performance Characteristics

Based on OpenAI benchmarks (4-agent vs 1-agent baseline):

- **BrowseComp**: Score improvement with reduced latency
- **SEC-Bench Pro**: Higher accuracy with parallel research
- **Terminal-Bench 2.1**: 88.8% (1-agent) -> 91.9% (4-agent)
- 16-agent configurations show further improvements on BrowseComp and SEC-Bench Pro

## When to Use Multi-Agent

**Good fit:**
- Tasks that split into independent parallel workstreams
- Research across multiple sources/topics
- Complex analysis requiring diverse perspectives
- Tasks where wall-clock time matters more than token cost

**Not suitable:**
- Sequential tasks where each step depends on the previous
- Simple single-focus queries
- Cost-sensitive workloads (multi-agent increases token usage)

## Gotchas and Quirks

- **Beta**: API surface may change without notice
- Token usage scales with agent count - 4 agents use roughly 4x tokens
- Best results on tasks that genuinely parallelize - forcing parallelism on sequential work wastes tokens
- Available only in Responses API, not Chat Completions

## TypeScript Examples

### Basic Response

```typescript
import OpenAI from "openai";

const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Explain this concept briefly.",
});

console.log(response.output_text);
```

### With Instructions

```typescript
const response = await client.responses.create({
  model: "gpt-4o-mini",
  instructions: "You are a helpful assistant.",
  input: "What is 2+2?",
});

console.log(response.output_text);
```

## Sources

- https://developers.openai.com/api/docs/guides/responses-multi-agent
- https://openai.com/index/gpt-5-6/ (Launch announcement)
- OAIAPI-SC-OAI-GLATEST (Model guidance page)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Initial documentation for Multi-Agent beta
