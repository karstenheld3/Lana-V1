# Memory Tool

**Doc ID**: ANTAPI-IN27
**Goal**: Document the memory tool for persistent cross-conversation context via local file storage
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` for tool use architecture

## Summary

The memory tool (`memory_20250818`) is a **client-side** tool that enables Claude to maintain persistent context across conversations by reading and writing files in a `/memories` directory. Claude makes tool calls (view, create, str_replace, insert, delete, rename) and your application executes those operations locally. This gives you complete control over where and how memory is stored (filesystem, database, cloud, encrypted). Claude automatically checks its memory directory before starting tasks. There are no Anthropic-imposed size limits; storage constraints are your implementation's responsibility.

## Key Facts

- **Type**: `memory_20250818`
- **Execution**: Client-side (your application handles file operations)
- **Storage**: File-based in `/memories` directory (you implement the backend)
- **Commands**: view, create, str_replace, insert, delete, rename
- **Size Limits**: None from Anthropic; implement your own (recommended)
- **SDK Helpers**: `BetaAbstractMemoryTool` (Python), `betaMemoryTool` (TypeScript)
- **Status**: GA

## Supported Models

- claude-opus-4-6, claude-opus-4-5-20251101, claude-opus-4-1-20250805, claude-opus-4-20250514
- claude-sonnet-4-6, claude-sonnet-4-5-20250929, claude-opus-5
- claude-haiku-4-5-20251001

## Basic Usage

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=2048,
    tools=[{"type": "memory_20250818", "name": "memory"}],
    messages=[
        {"role": "user", "content": "I'm working on a Python web scraper. Help me debug it."}
    ],
)

# Claude will return tool_use blocks with memory commands
# Your application must execute them and return tool_result blocks
for block in message.content:
    if block.type == "tool_use" and block.name == "memory":
        command = block.input["command"]
        path = block.input["path"]
        print(f"Memory command: {command} on {path}")
        # Execute command, return result as tool_result
```

## Tool Commands

Claude issues these commands as tool_use blocks; your client executes them:

- **view** - Show directory listing or file contents (with optional `view_range` for line ranges)
- **create** - Create a new file at a path with `file_text` content
- **str_replace** - Replace `old_str` with `new_str` in a file (must be unique match)
- **insert** - Insert text at a specific line number in a file
- **delete** - Delete a file
- **rename** - Rename/move a file from `old_path` to `new_path`

### Command Examples

```json
{"command": "view", "path": "/memories"}
{"command": "view", "path": "/memories/notes.txt", "view_range": [1, 10]}
{"command": "create", "path": "/memories/preferences.txt", "file_text": "Language: Python\nFramework: FastAPI"}
{"command": "str_replace", "path": "/memories/preferences.txt", "old_str": "Framework: FastAPI", "new_str": "Framework: Django"}
{"command": "insert", "path": "/memories/notes.txt", "insert_line": 3, "new_str": "New line here"}
{"command": "delete", "path": "/memories/old_notes.txt"}
{"command": "rename", "path": "/memories/old.txt", "new_path": "/memories/new.txt"}
```

## SDK Helpers

SDKs provide abstract classes to implement your own memory backend:

```python
from anthropic.beta import BetaAbstractMemoryTool  # API docs import

# Subclass to implement file-based, database, cloud, or encrypted storage
class MyMemoryTool(BetaAbstractMemoryTool):
    # Implement view, create, str_replace, insert, delete, rename
    ...
```

**SDK-Verified Import** (anthropic 0.120.0, `tools/memory.py`):

```python
# Correct import path in SDK 0.120.0:
from anthropic.tools.memory import BetaAbstractMemoryTool

# Also available: BetaLocalFilesystemMemoryTool (ready-made filesystem implementation)
from anthropic.tools.memory import BetaLocalFilesystemMemoryTool
```

Working examples:
- Python: `examples/memory/basic.py` in anthropic-sdk-python
- TypeScript: `examples/tools-helpers-memory.ts` in anthropic-sdk-typescript

## Storage Size and Limits

Anthropic imposes **no hard limits** on memory storage size. Since memory is client-side, your implementation controls all constraints. Recommended safeguards:

- **Track file sizes** - Prevent individual memory files from growing too large
- **Max read size** - Add a maximum character count for the view command return value; let Claude paginate through large files
- **Total storage cap** - Monitor aggregate memory directory size
- **Memory expiration** - Clear files not accessed for an extended period
- **File count limit** - Cap the number of files in the memories directory

## Security Considerations

- **Path traversal protection** (MUST implement): Validate all paths start with `/memories`, resolve to canonical form, reject `../`, `..\\`, URL-encoded sequences (`%2e%2e%2f`)
- **Sensitive information**: Claude usually refuses to store sensitive data, but implement stricter validation to strip potentially sensitive information
- Use language path security utilities (e.g., Python `pathlib.Path.resolve()` and `relative_to()`)

## Integration with Other Features

- **Context Editing**: Memory tool works alongside context editing for long conversations
- **Compaction**: Memory persists even when conversation context is compacted
- **Multi-session pattern**: Store project context in memory, enabling Claude to pick up where it left off across sessions

## Gotchas and Quirks

- Memory tool is **client-side**, not server-side; you must implement the file operation handlers
- Tool type is `memory_20250818` (not `memory_tool_20250818`)
- Claude automatically checks `/memories` at conversation start when the tool is enabled
- No Anthropic-imposed storage limits; all size management is your responsibility
- `str_replace` requires the old_str to be unique in the file (same as text_editor tool)
- Directory view only shows 2 levels deep, excludes hidden items and `node_modules`
- Files with >999,999 lines return an error on view

## Related Endpoints

- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` - Tool use architecture
- `_INFO_ANTAPI-26_COMPUTER_USE.md [ANTAPI-IN26]` - Text editor tool (similar command pattern)

## Sources

- ANTAPI-SC-ANTH-TOOLMEM - https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool - Full memory tool guide
- ANTAPI-SC-GH-SDKAPI - https://github.com/anthropics/anthropic-sdk-python/blob/main/api.md - MemoryTool20250818 type

## SDK Verification

2 Python examples verified against `anthropic` SDK 0.120.0. 1 correction added.

**SDK source files checked**:
- `types/memory_tool_20250818_param.py`: `MemoryTool20250818Param(type="memory_20250818", name="memory")`
- `types/tool_union_param.py`: `MemoryTool20250818Param` included in `ToolUnionParam` union
- `tools/memory.py`: `BetaAbstractMemoryTool`, `BetaLocalFilesystemMemoryTool` exports

**Finding: Import path differs from API docs**

API docs show `from anthropic.beta import BetaAbstractMemoryTool`. SDK 0.120.0 actual path: `from anthropic.tools.memory import BetaAbstractMemoryTool`. SDK-verified import added inline above.

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 07:00]**
- Added: SDK verification section (anthropic 0.120.0)
- Fixed: BetaAbstractMemoryTool import path (`anthropic.tools.memory`, not `anthropic.beta`)

**[2026-03-20 04:45]**
- Fixed: Memory tool is client-side (not server-side); corrected type string to `memory_20250818`
- Added: Tool commands (view, create, str_replace, insert, delete, rename) with examples
- Added: Storage size guidance (no Anthropic limits, implement your own)
- Added: Security considerations (path traversal, sensitive data)
- Added: SDK helpers (BetaAbstractMemoryTool), supported models, integration features

**[2026-03-20 03:55]**
- Initial documentation created from SDK API types
