# INFO: SDK Reference and Compatibility

**Doc ID**: GROKAPI-IN45
**Goal**: Supported SDKs, compatibility matrix, installation, configuration
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

The Grok API supports multiple SDKs: the native xAI SDK (Python, gRPC), OpenAI SDK (Python/JS/etc., REST), and Vercel AI SDK (TypeScript). The OpenAI SDK is the primary integration path for most developers - simply change `base_url` and `api_key`. The xAI SDK provides additional features (video generation, gRPC streaming, `chat.parse()`) but has tool name limitations (`code_interpreter`/`file_search` not supported). The Vercel AI SDK uses `@ai-sdk/xai` package with native xAI provider support. All Responses API-compatible SDKs work with xAI. [VERIFIED] (GROKAPI-SC-XAI-SDK | https://docs.x.ai/developers/xai-sdk)

## SDK Matrix

### xAI SDK (Native)
- **Language**: Python
- **Protocol**: gRPC
- **Install**: `pip install xai-sdk`
- **Client**: `from xai_sdk import Client`
- **Unique features**: `chat.parse()`, `client.video.generate()`, `AsyncClient`, tool helpers
- **Limitations**: No `code_interpreter` or `file_search` tool names
- **Details**: See `_INFO_GROKAPI-IN39_XAI_SDK.md [GROKAPI-IN39]`

### OpenAI SDK (Recommended for most)
- **Languages**: Python, JavaScript, Go, etc.
- **Protocol**: REST (HTTP/JSON)
- **Install**: `pip install openai` / `npm install openai`
- **Config**: `OpenAI(api_key=XAI_KEY, base_url="https://api.x.ai/v1")`
- **Compatibility**: Full Chat Completions + Responses API + Files + Batches + Images + Audio
- **Advantage**: Drop-in replacement, extensive community resources

### Vercel AI SDK
- **Language**: TypeScript
- **Protocol**: REST
- **Install**: `npm install @ai-sdk/xai ai`
- **Config**: `xai.responses('model-name')`
- **Features**: `generateText()`, `streamText()`, `generateObject()`, `generateVideo()`
- **Tool helpers**: `xai.tools.xSearch()`, `xai.tools.webSearch()`, `xai.tools.codeExecution()`

## Configuration Examples

### OpenAI SDK (Python)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)
```

### OpenAI SDK (JavaScript)

```javascript
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});
```

### xAI SDK (Python)

```python
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))
```

### Vercel AI SDK (TypeScript)

```typescript
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text } = await generateText({
    model: xai.responses('grok-4.20-beta-latest-non-reasoning'),
    prompt: 'Hello!',
});
```

## Tool Name Compatibility

| Tool | OpenAI SDK (REST) | xAI SDK (gRPC) | Vercel AI SDK |
|------|-------------------|----------------|---------------|
| web_search | web_search | web_search() | xai.tools.webSearch() |
| x_search | x_search | x_search() | xai.tools.xSearch() |
| code_execution | code_execution | code_execution() | xai.tools.codeExecution() |
| code_interpreter | code_interpreter | NOT SUPPORTED | - |
| collections_search | collections_search | collections_search() | - |
| file_search | file_search | NOT SUPPORTED | - |
| function | function | tool() | tool() from ai |

## Differences from Other APIs

### vs OpenAI
- **Drop-in**: Change base_url and api_key only
- **Additional SDK**: Native xAI SDK with gRPC and video generation

### vs Anthropic
- **Not compatible**: Cannot use Anthropic SDK with xAI
- **Use OpenAI SDK**: Or xAI SDK for xAI-specific features

### vs Gemini
- **Not compatible**: Cannot use Gemini SDK with xAI

## Sources

- GROKAPI-SC-XAI-SDK | https://docs.x.ai/developers/xai-sdk | Accessed: 2026-03-20
- GROKAPI-SC-XAI-QUICKSTART | https://docs.x.ai/developers/quickstart | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:50]**
- Initial document created with SDK compatibility matrix
