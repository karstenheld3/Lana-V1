# Local Shell Tool

**Doc ID**: OAIAPI-IN88
**Goal**: Document local shell tool for agent command execution
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Local shell tool enables agents to execute commands on the local machine (distinct from hosted shell which runs in cloud containers). Requires explicit user consent and security configuration. Available as a tool type in the Agents SDK. Higher security risk than hosted shell - must implement sandboxing and command filtering. [VERIFIED] (OAIAPI-SC-OAI-GLSHLL (https://developers.openai.com/api/docs/guides/tools-local-shell))

## Key Facts

- **Type**: Built-in tool for Agents SDK [VERIFIED]
- **Execution**: Commands run on local machine (user's system) [VERIFIED]
- **Security**: Requires explicit consent and sandboxing [VERIFIED]
- **Distinction**: Local shell = user machine; Hosted shell = cloud container

## Comparison: Local vs Hosted Shell

- **Local shell**: Runs on user's machine, access to local files/tools, higher risk
- **Hosted shell**: Runs in sandboxed cloud container, isolated, safer default
- **Use case for local**: IDE integrations, local dev workflows, file system access
- **Use case for hosted**: Code execution, package installs, untrusted operations

## Security Requirements

### Mandatory Controls

- **User consent**: Explicit opt-in before enabling local shell
- **Command allowlist**: Restrict to specific commands/paths
- **Working directory**: Limit to specific directories
- **Timeout**: Maximum execution time per command
- **Output limits**: Cap stdout/stderr capture size

### Recommended Controls

- **Audit logging**: Log all executed commands
- **Confirmation prompts**: Ask user before destructive operations
- **Network restrictions**: Block network access if not needed
- **Privilege restriction**: Run with minimum necessary permissions

## SDK Examples (Python)

### Basic Local Shell Configuration (Agents SDK)

```python
from openai.agents import Agent, LocalShellTool

# Configure local shell with restrictions
shell_tool = LocalShellTool(
    working_directory="/home/user/project",
    allowed_commands=["ls", "cat", "grep", "find", "python"],
    timeout_seconds=30,
    require_confirmation=True,
)

agent = Agent(
    model="gpt-5.6-sol",
    instructions="You are a coding assistant. Use the shell to explore and modify code.",
    tools=[shell_tool],
)
```

### With Approval Flow

```python
from openai.agents import Agent, LocalShellTool

def approval_callback(command: str) -> bool:
    """Ask user before executing potentially dangerous commands."""
    response = input(f"Execute: {command}? [y/N] ")
    return response.lower() == "y"

shell_tool = LocalShellTool(
    working_directory="/home/user/project",
    approval_callback=approval_callback,
    timeout_seconds=60,
)
```

## Gotchas and Quirks

- **Not in Responses API**: Local shell is Agents SDK only, not available in raw Responses API [VERIFIED]
- **No containerization**: Commands execute directly on host OS [VERIFIED]
- **Path traversal risk**: Agent may attempt to access files outside working directory [VERIFIED]
- **Persistent state**: Commands share shell state (env vars, CWD) within session [VERIFIED]

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

- OAIAPI-SC-OAI-GLSHLL - Local shell tool guide (https://developers.openai.com/api/docs/guides/tools-local-shell)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Security requirements, comparison with hosted shell, SDK examples, gotchas

**[2026-05-22 13:05]**
- Initial documentation (gap found during /improve review)
