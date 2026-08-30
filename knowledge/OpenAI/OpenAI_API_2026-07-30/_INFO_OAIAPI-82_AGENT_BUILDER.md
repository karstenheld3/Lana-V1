# Agent Builder [DEPRECATED]

**Doc ID**: OAIAPI-IN82
**Goal**: Document Agent Builder visual tool, node reference, safety considerations
**Version scope**: API v1, Documentation date 2026-07-30
**Status**: **DEPRECATED** (announced 2026-06-03). ChatKit remains available. Migrate to Agents SDK or ChatGPT Workspace Agents. See https://developers.openai.com/api/docs/guides/agent-builder/migrate-from-agent-builder

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

**DEPRECATED**: Agent Builder was deprecated on 2026-06-03. Migrate to the Agents SDK (Python/TypeScript) or ChatGPT Workspace Agents. ChatKit remains available as an alternative for UI-based agent creation.

Agent Builder was a visual tool for creating and configuring AI agents without code. Provided a node-based interface for defining agent workflows, tool connections, guardrails, and orchestration patterns. Three main guides: Overview (concepts, getting started), Node Reference (available nodes and configuration), and Safety in Building Agents (guardrails, approval flows, risk mitigation). [VERIFIED] (OAIAPI-SC-OAI-GAGTBL)

## Key Facts

- **Type**: Visual no-code tool for agent design [VERIFIED]
- **Models**: GPT-5.5, GPT-5.4 [VERIFIED]
- **Export**: Agents exportable to Agents SDK code for production [VERIFIED]
- **Relationship**: Prototyping tool; production = Agents SDK [VERIFIED]

## Key Capabilities

- **Visual workflow editor**: Drag-and-drop agent design
- **Node types**: Input, Output, Agent, Tool, Guardrail, Router, Handoff
- **Tool integration**: Connect to MCP servers, built-in tools, custom functions
- **Safety controls**: Approval flows, content filtering, scope limitations
- **Testing**: Built-in test harness for agent behavior validation
- **Multi-agent**: Orchestrate handoffs between specialized agents

## Node Types

### Core Nodes

- **Input**: Entry point, receives user messages
- **Output**: Final response delivery
- **Agent**: LLM processing node with instructions and model config
- **Router**: Conditional branching based on input classification

### Tool Nodes

- **Function**: Custom function call definitions
- **MCP Server**: Connect to remote MCP servers
- **Web Search**: Built-in web search tool
- **File Search**: Vector store search
- **Code Interpreter**: Python code execution
- **Computer Use**: Browser/desktop automation

### Control Nodes

- **Guardrail**: Content filtering and safety checks
- **Handoff**: Transfer between agents
- **Approval**: Human-in-the-loop confirmation

## Workflow: Prototype to Production

1. **Design** in Agent Builder (visual, iterative)
2. **Test** with built-in test harness
3. **Export** to Agents SDK code
4. **Deploy** SDK code in production environment
5. **Monitor** via API usage dashboards

## Guides

- **Overview**: https://developers.openai.com/api/docs/guides/agent-builder
- **Node Reference**: https://developers.openai.com/api/docs/guides/node-reference
- **Safety in Building Agents**: https://developers.openai.com/api/docs/guides/agent-builder-safety

## Limitations

- **Visual only**: Not a replacement for Agents SDK - use SDK for production deployments
- **Model support**: Works with GPT-5.5 and GPT-5.4 models
- **Export**: Agents can be exported to SDK code for production use
- **No version control**: Visual editor does not integrate with git

## Gotchas and Quirks

- **Not an API**: Agent Builder is a UI tool, not accessible via API [VERIFIED]
- **Export required**: Must export to SDK code before production deployment [VERIFIED]
- **Safety guide separate**: Agent safety considerations documented in dedicated sub-guide [VERIFIED]

## Sources

- OAIAPI-SC-OAI-GAGTBL - Agent Builder guide (https://developers.openai.com/api/docs/guides/agent-builder)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Changed: Marked as DEPRECATED (announced 2026-06-03)
- Added: Migration guidance to Agents SDK / ChatGPT Workspace Agents
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 22:00]**
- Enriched: Node types, workflow, key facts, gotchas

**[2026-05-22 13:00]**
- Initial documentation (gap found during /improve review)
