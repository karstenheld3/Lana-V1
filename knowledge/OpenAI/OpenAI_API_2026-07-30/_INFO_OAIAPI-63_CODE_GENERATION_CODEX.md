# Codex

**Doc ID**: OAIAPI-IN63
**Goal**: Document Codex - OpenAI's cloud software engineering agent for code tasks, automations, and repository management
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Codex is OpenAI's cloud-based software engineering agent that operates in sandboxed environments to complete coding tasks. Available via web app (codex.openai.com) and CLI (`codex-cli`). Connects to Git repositories, reads code, writes files, runs commands, executes tests, and creates pull requests. Tasks run in isolated sandbox environments with configurable access levels. Supports background automations, subagents for parallelization, web search, screenshot/design spec input, and code review. Current model: `gpt-5.3-codex`. Legacy models `gpt-5-codex`, `gpt-5.1-codex`, `gpt-5.2-codex` are deprecated. OpenAI Developers plugin for Codex released 2026-05. Shell tool available for sandboxed code execution. [VERIFIED] (OAIAPI-SC-OAI-CODEX, OAIAPI-SC-OAI-GCODGN, OAIAPI-SC-OAI-GSHELL)

## Key Facts

- **Interfaces**: Web app (codex.openai.com) and CLI (codex-cli) [VERIFIED] (OAIAPI-SC-OAI-CODEX)
- **Current model**: gpt-5.3-codex [VERIFIED] (OAIAPI-SC-OAI-GCODGN)
- **Sandbox modes**: Read-only, workspace write, full access [VERIFIED] (OAIAPI-SC-OAI-CODEX)
- **Repository integration**: Git repos, PRs, code review [VERIFIED] (OAIAPI-SC-OAI-CODEX)
- **Automations**: Background tasks, scheduled/triggered [VERIFIED] (OAIAPI-SC-OAI-CODEX)
- **Subagents**: Parallel task execution [VERIFIED] (OAIAPI-SC-OAI-CODEX)
- **Shell tool**: Sandboxed code execution [VERIFIED] (OAIAPI-SC-OAI-GSHELL)

## Use Cases

- **Feature implementation**: Describe a feature, Codex writes the code
- **Bug fixing**: Point Codex at an issue, it investigates and fixes
- **Code review**: Automated review before commit/push
- **Refactoring**: Large-scale code changes across files
- **Test writing**: Generate tests for existing code
- **Documentation**: Auto-generate docs from code
- **Dependency updates**: Update packages and fix breaking changes

## Architecture

```
User (Web/CLI)
  |
  v
Codex Task
  |
  v
Sandboxed Environment
  |-> Git Repository (clone/read/write)
  |-> File System (read/write per sandbox mode)
  |-> Command Execution (per sandbox mode)
  |-> Web Search (cached or live)
  └-> Network (per sandbox mode)
  |
  v
Output (PR, files, logs)
```

## Sandbox Modes

- **Read-only**: Can read files and run read-only commands. Cannot modify files
- **Workspace write**: Can modify files within workspace. Cannot run arbitrary commands
- **Full access**: Full file system, command execution, and network access. Highest risk

## CLI Usage

```bash
# Install
npm install -g codex-cli

# Start task
codex "Add input validation to the user registration form"

# With screenshot input
codex "Match this design" --image design-spec.png

# Code review
codex review --before-push

# Subagents for parallel work
codex "Refactor auth module" --parallel
```

## SDK Examples (Python)

> **SDK note**: `client.codex.*` methods are not available in openai Python SDK v2.38.0.
> Codex is primarily used via web app or CLI. Use `httpx` or `requests` for direct REST API calls.

### Create Codex Task via API

```python
from openai import OpenAI

client = OpenAI()

task = client.codex.tasks.create(
    description="Add rate limiting middleware to the Express API server",
    repository="https://github.com/myorg/api-server",
    sandbox_mode="workspace_write",
    rules=[
        "Do not modify existing tests",
        "Use express-rate-limit package",
        "Add rate limit of 100 requests per 15 minutes"
    ]
)

print(f"Task ID: {task.id}")
print(f"Status: {task.status}")
```

### Monitor Task Progress

```python
from openai import OpenAI
import time

client = OpenAI()

def wait_for_task(task_id: str, timeout: int = 600):
    """Wait for Codex task completion"""
    start = time.time()
    
    while True:
        task = client.codex.tasks.retrieve(task_id)
        elapsed = time.time() - start
        
        print(f"[{elapsed:.0f}s] Status: {task.status}")
        
        if task.status in ("completed", "failed", "cancelled"):
            return task
        
        if elapsed > timeout:
            raise TimeoutError(f"Task timed out after {timeout}s")
        
        time.sleep(10)

try:
    task = wait_for_task("task_abc123")
    if task.status == "completed":
        print(f"PR: {task.pull_request_url}")
    else:
        print(f"Failed: {task.error}")
except Exception as e:
    print(f"Error: {e}")
```

## Error Responses

- **400 Bad Request** - Invalid task parameters
- **401 Unauthorized** - Invalid API key
- **403 Forbidden** - Repository access denied
- **429 Too Many Requests** - Concurrent task limit exceeded

## Differences from Other APIs

- **vs Anthropic Claude Code**: Similar concept - AI coding agent. Claude Code runs locally via CLI
- **vs Gemini**: No equivalent cloud coding agent
- **vs GitHub Copilot Workspace**: Similar cloud-based coding environment with AI agent

## Limitations and Known Issues

- **Sandbox constraints**: Some operations require full access mode [VERIFIED] (OAIAPI-SC-OAI-CODEX)
- **Repository size**: Very large repos may have longer setup times [ASSUMED]
- **Language coverage**: Best for popular languages; less effective for niche ones [ASSUMED]
- **Background automation risk**: Full access + background = potential for unintended changes [VERIFIED] (OAIAPI-SC-OAI-CODEX)

## TypeScript Examples

### Client Setup and Basic Usage

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  organization: process.env.OPENAI_ORG_ID,
});

const response = await client.responses.create({
  model: "gpt-4o-mini",
  input: "Hello!",
});
console.log(response.output_text);
```

## Sources

- OAIAPI-SC-OAI-CODEX - Codex Documentation
- OAIAPI-SC-OAI-GCODGN - Code Generation Guide
- OAIAPI-SC-OAI-GSHELL - Shell Tool Guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 17:50]**
- Enriched from 2026-03-20 IN63 (19 -> 175 lines)
- Added gpt-5.3-codex model, legacy model deprecation, shell tool

**[2026-05-22 11:50]**
- Stub created
