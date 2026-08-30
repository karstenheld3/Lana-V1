# Agents Framework

**Doc ID**: OAIAPI-IN64
**Goal**: Document Agents overview, building agents, Agents SDK (Python/TypeScript), sandbox agents, harness, memory control
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

OpenAI provides an Agents framework for building AI agents that can reason, use tools, execute code, and maintain state. The Agents SDK is available in Python and TypeScript. Key capabilities: function calling, built-in tools (web search, file search, code interpreter, computer use, hosted shell, apply patch, Skills, MCP), sandbox agents for isolated execution, an inspectable open-source harness for testing and debugging, and memory control. **NEW (2026-07)**: GPT-5.6 adds Programmatic Tool Calling (model writes JS to orchestrate tools, see IN94) and Multi-Agent beta (parallel subagents, see IN95) in the Responses API, enabling ultra-like experiences programmatically. **DEPRECATED (2026-06)**: Agent Builder visual tool deprecated - migrate to Agents SDK or ChatGPT Workspace Agents (see IN82). Agents can leverage GPT-5.6's full tool suite including tool_search, compaction, and programmatic_tool_calling. [VERIFIED] (OAIAPI-SC-OAI-GAGENT, OAIAPI-SC-OAI-GCHLOG)

## Key Capabilities

- **Function calling**: Define custom tools via JSON schema
- **Built-in tools**: web_search, file_search, code_interpreter, computer_use, hosted_shell, apply_patch, skills, mcp, tool_search
- **Sandbox agents**: Run agents in controlled sandboxes (containers)
- **Inspectable harness**: Open-source framework for testing agent behavior
- **Memory control**: Configure when memories are created and where they are stored
- **Compaction**: Manage context growth in multi-turn agent loops
- **Tool search**: Defer large tool surfaces until runtime to reduce tokens

## Agents SDK

### Python SDK

```python
from openai.agents import Agent, Runner

agent = Agent(
    name="research_assistant",
    model="gpt-5.6-sol",
    instructions="You are a research assistant that finds and summarizes information.",
    tools=[
        {"type": "web_search"},
        {"type": "code_interpreter"},
        {
            "type": "function",
            "function": {
                "name": "save_note",
                "description": "Save a research note",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["title", "content"]
                }
            }
        }
    ],
)

runner = Runner()
result = runner.run(agent, "Research the latest developments in quantum computing.")
print(result.output)
```

### TypeScript SDK (NEW - 2026-05)

```typescript
import { Agent, Runner } from 'openai/agents';

const agent = new Agent({
  name: 'code_reviewer',
  model: 'gpt-5.5',
  instructions: 'Review code for bugs and security issues.',
  tools: [
    { type: 'code_interpreter' },
    { type: 'web_search' },
  ],
});

const runner = new Runner();
const result = await runner.run(agent, 'Review the auth module for vulnerabilities.');
console.log(result.output);
```

### Sandbox Agents (NEW - 2026-04)

Run agents in isolated container environments:

```python
from openai.agents import Agent, Runner

agent = Agent(
    name="sandbox_coder",
    model="gpt-5.6-sol",
    instructions="Write and test code in a sandboxed environment.",
    tools=[{"type": "code_interpreter"}, {"type": "hosted_shell"}],
    sandbox=True,  # Run in isolated container
)

runner = Runner()
result = runner.run(agent, "Write a web scraper and test it against example.com")
print(result.output)
```

### Memory Control (NEW - 2026-04)

Configure memory creation and storage:

```python
from openai.agents import Agent, Runner

agent = Agent(
    name="memory_agent",
    model="gpt-5.6-sol",
    instructions="Help users with their questions. Remember important context.",
    memory={
        "enabled": True,
        "auto_create": False,  # Don't auto-create memories
        "storage": "project",  # Store in project scope
    },
)
```

## Multi-Agent Patterns

### Handoff Pattern

```python
from openai.agents import Agent, Runner

researcher = Agent(
    name="researcher",
    model="gpt-5.6-sol",
    instructions="Research topics using web search.",
    tools=[{"type": "web_search"}],
)

writer = Agent(
    name="writer",
    model="gpt-5.6-sol",
    instructions="Write polished articles from research notes.",
)

# Chain agents
runner = Runner()
research = runner.run(researcher, "Find latest AI safety research papers from 2026.")
article = runner.run(writer, f"Write a summary article based on: {research.output}")
print(article.output)
```

## Error Responses

- **400 Bad Request** - Invalid agent configuration, unsupported tool
- **429 Too Many Requests** - Rate limit exceeded during agent execution
- **500 Internal Server Error** - Agent execution failure

## SDK Sub-Guides

- **Overview**: https://developers.openai.com/api/docs/guides/agents
- **Quickstart**: https://developers.openai.com/api/docs/guides/agents/quickstart
- **Agent definitions**: https://developers.openai.com/api/docs/guides/agents/define-agents
- **Models and providers**: https://developers.openai.com/api/docs/guides/agents/models
- **Running agents**: https://developers.openai.com/api/docs/guides/agents/running-agents
- **Sandbox agents**: https://developers.openai.com/api/docs/guides/agents/sandboxes
- **Orchestration**: https://developers.openai.com/api/docs/guides/agents/orchestration
- **Guardrails and approvals**: https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
- **Results and state**: https://developers.openai.com/api/docs/guides/agents/results
- **Integrations and observability**: https://developers.openai.com/api/docs/guides/agents/integrations-observability
- **Evaluate agent workflows**: https://developers.openai.com/api/docs/guides/agent-evals

## Gotchas and Quirks

- **TypeScript SDK**: New as of 2026-05, includes sandbox and harness support [VERIFIED]
- **Sandbox costs**: Sandbox agents incur additional container costs [ASSUMED]
- **Memory scope**: Memory storage scoped to project level by default [ASSUMED]
- **Tool search**: Reduces token usage for agents with many tools by deferring tool definitions [VERIFIED]
- **Guardrails required**: Production agents should use guardrails and approval flows for safety [VERIFIED]
- **Agent evals**: Separate evaluation framework for testing agent workflows end-to-end [VERIFIED]

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

- OAIAPI-SC-OAI-GAGENT - Agents Overview guide
- OAIAPI-SC-GH-AGNTPY - openai-agents-python repository
- OAIAPI-SC-OAI-GCHLOG - Changelog (April/2026-05)
- OAIAPI-SC-OAI-GAGEVAL - Agent Evals guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Added: GPT-5.6 Programmatic Tool Calling and Multi-Agent beta references
- Added: Agent Builder deprecation notice (2026-06-03)
- Changed: Model references from GPT-5.5 to GPT-5.6
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 10:35]**
- Major update from 2026-03-20 version
- Added: TypeScript SDK documentation (2026-05)
- Added: Sandbox agents examples (2026-04)
- Added: Memory control configuration
- Added: Multi-agent handoff pattern
- Changed: Updated model references to GPT-5.5
