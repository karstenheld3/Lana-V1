# Computer Use Tools

**Doc ID**: ANTAPI-IN26
**Goal**: Document computer use, bash, and text editor Anthropic-defined client tools
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` for tool use architecture

## Summary

Computer use tools are Anthropic-defined client tools that enable Claude to interact with computer environments. Three tools exist: computer use (screen interaction via screenshots and mouse/keyboard), bash (shell command execution), and text editor (file viewing/editing). Unlike server tools, these require client-side implementation - you provide the execution environment and return results to Claude. Tools use versioned type strings (e.g., `bash_20250124`, `text_editor_20250124`).

## Key Facts

- **Computer Use**: Screen interaction via screenshots, mouse clicks, keyboard input
- **Bash**: `bash_20250124` - Shell command execution
- **Text Editor**: `text_editor_20250124` - File viewing, creation, string replacement
- **Execution**: Client-side (you implement the execution environment)
- **Pattern**: Claude sends commands -> you execute -> return screenshots/output
- **Status**: GA (beta for some features)

## Bash Tool

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[{"type": "bash_20250124", "name": "bash"}],
    messages=[{"role": "user", "content": "List all Python files in the current directory"}],
)

# Claude will return tool_use blocks with bash commands
for block in message.content:
    if block.type == "tool_use" and block.name == "bash":
        command = block.input.get("command", "")
        print(f"Execute: {command}")
        # Execute command in your environment, return result as tool_result
```

## Text Editor Tool

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[{"type": "text_editor_20250124", "name": "text_editor"}],
    messages=[{"role": "user", "content": "View the contents of config.py"}],
)

# Claude will return tool_use blocks with editor commands
# Commands: view, create, str_replace
for block in message.content:
    if block.type == "tool_use" and block.name == "text_editor":
        command = block.input.get("command")
        path = block.input.get("path")
        print(f"Editor command: {command} on {path}")
```

### Text Editor Commands

- **view** - View file contents (with optional line range)
- **create** - Create a new file with specified content
- **str_replace** - Replace a string in a file (old_str -> new_str)

## Computer Use Tool

The computer use tool enables Claude to interact with a graphical desktop environment:

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[
        {
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": 1920,
            "display_height_px": 1080,
        }
    ],
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/png", "data": "..."},
                },
                {"type": "text", "text": "Click the Submit button"},
            ],
        }
    ],
)

# Claude returns actions like mouse_move, click, type, screenshot
for block in message.content:
    if block.type == "tool_use" and block.name == "computer":
        action = block.input.get("action")
        print(f"Action: {action}")
```

### Computer Use Actions

- **screenshot** - Request a screenshot of the current screen
- **mouse_move** - Move cursor to coordinates
- **left_click** / **right_click** / **double_click** / **middle_click** - Mouse clicks
- **type** - Type text
- **key** - Press key combination (e.g., "ctrl+c")
- **scroll** - Scroll in a direction
- **drag** - Drag from one point to another

## Implementation Pattern

```python
import anthropic
import subprocess

client = anthropic.Anthropic()

def execute_bash(command):
    """Execute bash command and return output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout + result.stderr

tools = [
    {"type": "bash_20250124", "name": "bash"},
    {"type": "text_editor_20250124", "name": "text_editor"},
]

messages = [{"role": "user", "content": "Create a Python script that prints Hello World"}]

while True:
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=4096,
        tools=tools,
        messages=messages,
    )

    if response.stop_reason == "end_turn":
        for block in response.content:
            if hasattr(block, "text"):
                print(block.text)
        break

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                if block.name == "bash":
                    output = execute_bash(block.input["command"])
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                    })
                elif block.name == "text_editor":
                    # Implement text editor operations
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "File operation completed",
                    })
        messages.append({"role": "user", "content": results})
```

## Beta Status and Safety

- Computer use is **beta**; capabilities and API may change
- **Safety warning**: Computer use carries unique risks; Claude may make mistakes interacting with desktops
- Recommended: Run in sandboxed environments (VMs, containers) with limited permissions
- Avoid giving Claude access to sensitive data or systems without human oversight
- Not designed for fully autonomous operation; use human-in-the-loop patterns

## Platform Availability

- Claude API (Anthropic) - supported
- Amazon Bedrock - supported (computer use only)
- Google Vertex AI - supported (computer use only)
- Microsoft Azure AI Foundry - check current availability

## Gotchas and Quirks

- Computer use tools are **client-side**; you must implement the execution environment
- **Beta**: Capabilities and API surface may change
- Tool versions are tied to specific capabilities; use the documented version strings
- Computer use requires providing screenshots for Claude to understand screen state
- **Screenshot resolution**: Recommended max 1280x800 for best performance; higher resolutions increase token cost and may reduce accuracy
- Bash commands should be executed with appropriate sandboxing and security controls
- Text editor's `str_replace` requires exact string matching (unique in file)
- Code execution server tool is different from bash/text_editor client tools
- Computer use is token-intensive due to repeated screenshot processing

## Related Endpoints

- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` - Tool use architecture
- `_INFO_ANTAPI-25_CODE_EXECUTION.md [ANTAPI-IN25]` - Server-side code execution (different from bash tool)

## Sources

- ANTAPI-SC-ANTH-COMPUSE - https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool - Computer use
- ANTAPI-SC-ANTH-TXTEDIT - https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool - Text editor
- ANTAPI-SC-ANTH-BASHTL - https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool - Bash tool

## SDK Verification

All 4 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `types/tool_bash_20250124_param.py`: `ToolBash20250124Param(type="bash_20250124", name="bash")`
- `types/tool_text_editor_20250124_param.py`: `ToolTextEditor20250124Param(type="text_editor_20250124", name="text_editor")`
- `types/tool_union_param.py`: Both bash and text_editor types included in `ToolUnionParam` union

**Notes**:
- SDK also includes newer text editor versions: `tool_text_editor_20250429` and `tool_text_editor_20250728`
- Computer use tool type (`computer_20250124`) is available via beta resources, not in base `ToolUnionParam`

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:40]**
- Added: SDK verification section (anthropic 0.120.0, all 4 examples valid)

**[2026-03-20 05:00]**
- Added: Beta status and safety warnings
- Added: Platform availability, screenshot resolution guidance
- Added: Token-intensive nature note

**[2026-03-20 03:52]**
- Initial documentation created from computer use, bash, and text editor tool guides
