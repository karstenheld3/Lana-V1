# Code Execution Tool

**Doc ID**: ANTAPI-IN25
**Goal**: Document the sandboxed code execution server tool
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` for tool use architecture

## Summary

The code execution tool (`code_execution_tool_20250522` and later versions) enables Claude to write and run code in a sandboxed environment on Anthropic's servers. This is a server-side tool that executes automatically. Claude can create, run, and iterate on code to solve computational problems, perform data analysis, and generate outputs. Containers can be reused across requests via `container_id`. File uploads to the container are supported via `container_upload` content blocks.

## Key Facts

- **Type**: `code_execution_tool_20250522` / `code_execution_tool_20250825` / `code_execution_tool_20260120` / `code_execution_tool_20260521`
- **Latest**: `code_execution_tool_20260120` adds REPL persistence; `code_execution_tool_20260521` increases timeout to 90s
- **Execution**: Server-side (sandboxed container)
- **Container Reuse**: Via `container_id` parameter on the request
- **File Upload**: `container_upload` content blocks in messages
- **Response**: `code_execution_tool_result` blocks with stdout, results
- **Status**: GA

## Basic Usage

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[{"type": "code_execution_tool_20250522", "name": "code_execution"}],
    messages=[
        {"role": "user", "content": "Calculate the first 20 Fibonacci numbers and plot them"}
    ],
)

for block in message.content:
    if hasattr(block, "text"):
        print(block.text)
    elif block.type == "code_execution_tool_result":
        print(f"Code output: {block}")
```

## Container Reuse

Containers persist across requests when referenced by ID:

```python
# First request creates a container
response1 = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[{"type": "code_execution_tool_20250522", "name": "code_execution"}],
    messages=[{"role": "user", "content": "Create a data.csv file with sample data"}],
)

# Get container ID from response
container_id = response1.container.id if response1.container else None

# Second request reuses the container
if container_id:
    response2 = client.messages.create(
        model="claude-opus-5",
        max_tokens=4096,
        container_id=container_id,
        tools=[{"type": "code_execution_tool_20250522", "name": "code_execution"}],
        messages=[{"role": "user", "content": "Read data.csv and compute statistics"}],
    )
```

## File Upload to Container

```python
message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[{"type": "code_execution_tool_20250522", "name": "code_execution"}],
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "container_upload",
                    "file_data": "base64_encoded_data_here",
                    "filename": "input.csv",
                },
                {"type": "text", "text": "Analyze the uploaded CSV file"},
            ],
        }
    ],
)
```

## Response Content Blocks

- **CodeExecutionToolResultBlock** - Result of code execution
- **CodeExecutionResultBlock** - Individual execution result (stdout, files)
- **CodeExecutionOutputBlock** - Output data
- **BashCodeExecutionToolResultBlock** - Bash execution results
- **TextEditorCodeExecutionToolResultBlock** - Text editor operation results

## Response Container Info

```json
{
  "container": {
    "id": "container_01abc...",
    "expires_at": "2026-03-20T04:00:00Z"
  }
}
```

## Resource Limits

- **Memory**: 5 GiB RAM
- **Disk**: 5 GiB workspace storage
- **CPU**: 1 CPU
- **Runtime**: Python 3.11.12, Linux x86_64
- **Internet**: Completely disabled (no outbound network requests)
- **File access**: Limited to workspace directory only
- **Container expiration**: 30 days after creation
- **Container scoping**: Scoped to workspace of the API key (like Files API)

## Platform Availability

- Claude API (Anthropic) - supported
- Microsoft Azure AI Foundry - supported
- Amazon Bedrock - **NOT available**
- Google Vertex AI - **NOT available**

## Tool Versions

- **`code_execution_20250825`** (current) - Bash commands + file operations (multi-language)
- **`code_execution_20250522`** (legacy) - Python-only execution
- Older tool versions are not guaranteed backward-compatible with newer models

## Pricing

- **Free with web tools**: No additional charges when `web_search_20260209` or `web_fetch_20260209` is also in the request (beyond standard token costs)
- **Standalone pricing**: Billed by execution time
  - Minimum: 5 minutes per execution
  - Free tier: 1,550 hours/month per organization
  - Beyond free tier: $0.05/hour per container
  - If files are included in request, execution time is billed even if tool is not invoked (files preloaded onto container)

## Pre-installed Libraries

- **Data Science**: pandas, numpy, scipy, scikit-learn, statsmodels
- **Visualization**: matplotlib, seaborn
- **File Processing**: pyarrow, openpyxl, xlsxwriter, xlrd, pillow, python-pptx, python-docx, pypdf, pdfplumber, pypdfium2, pdf2image, pdfkit, tabula-py, reportlab, img2pdf
- **Math**: sympy, mpmath
- **Utilities**: tqdm, python-dateutil, pytz, joblib, unzip, unrar, 7zip, bc, ripgrep, fd, sqlite

## Gotchas and Quirks

- **No internet access** - completely disabled for security; cannot pip install or fetch URLs
- Containers have an expiration time (30 days); check `container.expires_at`
- Two tool versions exist: `code_execution_20250825` (Bash+files) and legacy `code_execution_20250522` (Python-only)
- Files created in one container persist until expiration; reuse via container ID
- `container_upload` blocks upload files to the container's input directory
- Encrypted execution results may appear for certain content types
- **Not available on Bedrock or Vertex AI**
- Execution time billed even without tool invocation if files are in the request

## Related Endpoints

- `_INFO_ANTAPI-23_TOOL_USE.md [ANTAPI-IN23]` - Tool use architecture
- `_INFO_ANTAPI-26_COMPUTER_USE.md [ANTAPI-IN26]` - Bash and text editor tools

## Sources

- ANTAPI-SC-ANTH-CODEEXE - https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool - Code execution guide
- ANTAPI-SC-GH-SDKAPI - https://github.com/anthropics/anthropic-sdk-python/blob/main/api.md - SDK types

## SDK Verification

All 3 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `types/code_execution_tool_20250522_param.py`: `CodeExecutionTool20250522Param(type="code_execution_tool_20250522", name="code_execution")`
- `types/tool_union_param.py`: Code execution tool types in `ToolUnionParam` union
- `resources/messages/messages.py`: `container_id` parameter confirmed (SDK 0.120.0)
- `types/message.py`: `Message.container` field confirmed

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Added: code_execution_tool_20260521 (90s timeout)
- Added: code_execution_tool_20260120 note (REPL persistence)
- Changed: Model references to claude-opus-5

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Model references updated to claude-opus-5

**[2026-03-20 06:55]**
- Added: SDK verification section (anthropic 0.120.0, all 3 examples valid)

**[2026-03-20 05:00]**
- Added: Resource limits (5 GiB RAM/disk, 1 CPU, no internet, 30-day expiration)
- Added: Platform availability (API + Azure only, NOT Bedrock/Vertex)
- Added: Pricing (free with web tools, $0.05/hr standalone, 1,550 free hours/month)
- Added: Pre-installed libraries, tool versioning (20250825 vs 20250522)

**[2026-03-20 03:48]**
- Initial documentation created from code execution tool guide and SDK types
