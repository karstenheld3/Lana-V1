# Claude Managed Agents

**Doc ID**: ANTAPI-IN40
**Goal**: Document Claude Managed Agents - autonomous agent harness with managed infrastructure
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL, auth headers
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` for beta header usage

## Summary

Claude Managed Agents is a fully managed autonomous agent platform (beta). Instead of building your own agent loop, tool execution, and runtime, you get a managed environment where Claude can read files, run commands, browse the web, and execute code securely. The system is built around four concepts: agents (configuration), environments (container runtime), sessions (stateful execution), and events (communication). All endpoints require the `managed-agents-2026-04-01` beta header (SDK sets this automatically). Since May 2026, major additions include: scheduled deployments, session event deltas (streaming), backward pagination, session agent overrides, initial_events on session creation, effort on agents, memory stores (`agent-memory-2026-07-22` header), Dreams (research preview), and expanded webhook events.

## Key Facts

- **Beta Header**: `managed-agents-2026-04-01`
- **SDK Namespace**: `client.beta.sessions`, `client.beta.agents`, `client.beta.environments`
- **Agent Tools**: `agent_toolset_20260401` enables bash, file ops, web search, MCP servers
- **Session Model**: Stateful, long-running, persistent event history
- **Environments**: Cloud containers or self-hosted sandboxes
- **Streaming**: SSE-based event streaming
- **Status**: Beta

## Core Concepts

- **Agent** - Reusable configuration: model, system prompt, tools, MCP servers, skills. Created once, referenced by ID across sessions
- **Environment** - Where the agent runs: cloud container or self-hosted sandbox. Configures networking and container settings
- **Session** - Stateful execution context. References an agent and environment. Persistent filesystem and conversation history
- **Events** - Communication mechanism. User sends `user.message` events; agent streams back `agent.message`, `agent.tool_use`, and `session.status_idle` events

## Quick Reference

```python
import anthropic

client = anthropic.Anthropic()

# 1. Create agent
agent = client.beta.agents.create(
    name="Coding Assistant",
    model={"id": "claude-opus-5"},
    system="You are a helpful coding assistant.",
    tools=[{"type": "agent_toolset_20260401"}],
)

# 2. Create environment
environment = client.beta.environments.create(
    name="quickstart-env",
    config={"type": "cloud", "networking": {"type": "unrestricted"}},
)

# 3. Start session
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Quickstart session",
)

# 4. Send message and stream response
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [
                    {
                        "type": "text",
                        "text": "Create a script that generates Fibonacci numbers",
                    },
                ],
            },
        ],
    )

    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="")
            case "agent.tool_use":
                print(f"\n[Using tool: {event.name}]")
            case "session.status_idle":
                print("\n\nAgent finished.")
                break
```

## How It Works

1. **Provision container** - Environment configuration determines the runtime
2. **Run agent loop** - Claude decides which tools to use based on user message
3. **Execute tools** - File writes, bash commands, tool calls run inside the container
4. **Stream events** - Real-time updates as the agent works
5. **Go idle** - Agent emits `session.status_idle` when finished

## Supported Tools

- **Bash** - Run shell commands in the container
- **File operations** - Read, write, edit, glob, grep files
- **Web search and fetch** - Search the web and retrieve URL content
- **MCP servers** - Connect to external tool providers
- **Skills** - Reusable, filesystem-based expertise (Anthropic pre-built or custom)

## Additional Features (May 2026)

- **Agent memory** (public beta, Apr 23) - Persistent memory across sessions. See `Using agent memory` guide
- **Multiagent sessions** (public beta, May 6) - Multiple agents collaborating in a single session
- **Outcomes** (public beta, May 6) - Define expected outcomes for agent sessions
- **Webhooks** (May 6) - Subscribe to session and vault lifecycle events
- **Vaults** (May 6) - Secure credential storage with `mcp_oauth` background refresh
- **Self-hosted sandboxes** (May 19) - Run tool execution on your own infrastructure instead of Anthropic's cloud
- **Large output spill** (May 19) - Tool outputs exceeding 100K tokens auto-spill to a file; model receives truncated preview with file path

## Use Cases

- Long-running tasks (minutes to hours, multiple tool calls)
- Cloud infrastructure with secure containers
- Self-hosted execution for compliance/data residency
- Stateful sessions with persistent filesystems
- Minimal infrastructure (no custom agent loop needed)

## Limitations

- Not eligible for Zero Data Retention (ZDR) or HIPAA BAA coverage
- Sessions store conversation history, container state, and outputs server-side
- Rate-limited per organization (separate from Messages API limits)
- MCP tunnels and dreaming features require separate research preview access
- Large tool outputs (>100K tokens) are automatically spilled to file in sandbox

## New Features (since May 2026)

- **Scheduled deployments** (Jun 9) - Run sessions on a cron schedule without managing your own scheduler
- **Session event deltas** (Jun 30) - Preview agent text as generated via `event_deltas[]` query param on event stream
- **Backward pagination** (Jun 30) - `prev_page` cursor on `GET /v1/sessions`
- **Session agent overrides** (Jun 30) - Override model, system prompt, tools, MCP servers per session via `type: "agent_with_overrides"`
- **Vault injection_location** (Jun 9) - Control whether credentials inject into request headers, body, or both
- **Initial events on session creation** (Jul 22) - Pass `initial_events` on `POST /v1/sessions` with up to 50 events
- **Effort on agents** (Jul 22) - Pass `effort` inside the model object when creating an agent
- **Version field optional** (Jul 22) - Omit `version` on agent update for unconditional update
- **Thread event streams** (Jul 22) - `event_deltas[]` on thread-level stream endpoint
- **Webhook expansion** - Agent, deployment, deployment run, environment, memory store lifecycle events
- **Memory stores** (Jul 2/22) - See `_INFO_ANTAPI-49_AGENT_MEMORY_STORES.md [ANTAPI-IN49]`
- **Dreams** (Jul 10) - Research preview supporting Fable 5 and Sonnet 5

## Gotchas and Quirks

- The `agent_toolset_20260401` type enables ALL pre-built tools at once; use per-tool configuration for selective enablement
- Sessions are long-lived; delete them via API when no longer needed
- Self-hosted sandboxes run on your infrastructure but require specific setup
- Memory store endpoints use `agent-memory-2026-07-22` header, NOT `managed-agents-2026-04-01`
- Large outputs from agent_toolset/MCP tools exceeding 100K chars are spilled to sandbox file
- Branding guidelines: Your product must maintain its own branding, not appear as Claude Code or Claude Cowork
- Available on Claude Platform on AWS (webhooks, multiagent, self-hosted sandboxes since May 29)

## Related Endpoints

- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` - Beta header configuration
- `_INFO_ANTAPI-31_SKILLS_API.md [ANTAPI-IN31]` - Skills (attachable to agents)
- `_INFO_ANTAPI-44_CLAUDE_PLATFORM_ON_AWS.md [ANTAPI-IN44]` - Managed Agents on AWS
- `_INFO_ANTAPI-45_MCP_TUNNELS.md [ANTAPI-IN45]` - MCP tunnels for private servers
- `_INFO_ANTAPI-49_AGENT_MEMORY_STORES.md [ANTAPI-IN49]` - Agent memory stores

## Sources

- ANTAPI-SC-ANTH-MAOVW - https://platform.claude.com/docs/en/managed-agents/overview - Managed Agents overview
- ANTAPI-SC-ANTH-MAQS - https://platform.claude.com/docs/en/managed-agents/quickstart - Quickstart guide
- ANTAPI-SC-ANTH-MATOOL - https://platform.claude.com/docs/en/managed-agents/tools - Tools reference
- ANTAPI-SC-ANTH-MASESS - https://platform.claude.com/docs/en/managed-agents/sessions - Sessions API reference

## SDK Verification

8 client calls verified against `anthropic` SDK 0.120.0:
- `client.beta.agents.create` - OK (params: name, model, system, tools)
- `client.beta.environments.create` - OK (params: name, config)
- `client.beta.sessions.create` - OK (params: agent, environment_id, title)
- `client.beta.sessions.events.stream` - OK (context manager)
- `client.beta.sessions.events.send` - OK (params: session_id, events)

All Managed Agents methods are in the `beta` namespace and require the `managed-agents-2026-04-01` beta header. The SDK sets this automatically.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: New features section (scheduled deployments, event deltas, backward pagination, overrides, initial_events, effort, Dreams)
- Added: Webhook expansion (agent/deployment/environment/memory_store lifecycle)
- Added: Memory stores reference (IN47)
- Changed: Gotchas updated for memory header conflict, AWS availability

**[2026-05-22]**
- Initial documentation created from Managed Agents overview and quickstart
- Added: Agent memory, multiagent sessions, outcomes, webhooks, vaults (from Apr-May release notes)
- Added: Self-hosted sandboxes, large output spill (May 19 release notes)
- Added: SDK verification section (all 8 calls verified against 0.104.0)
