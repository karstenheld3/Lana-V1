# INFO: Gemini API Context Engineering

**Doc ID**: GEMAPI-IN38
**Goal**: Document prompt design, context window optimization, and Gemini 3 context engineering patterns
**Version scope**: API v1beta, Documentation date 2026-03-20

**Depends on:**
- `__GEMAPI_TOC.md [GEMAPI-TOC]` for topic index
- `__GEMAPI_SOURCES.md [GEMAPI-SOURCES]` for source references

## Summary

Context engineering for Gemini encompasses prompt design, context window management, and Gemini 3's specific patterns for optimal performance. Key practices include: using system instructions for persistent behavior rules, placing reference material before questions, leveraging thought signatures for multi-turn reasoning continuity, combining multiple tools with context circulation (Gemini 3), and managing the context budget across system instructions, cached content, conversation history, tools, and user input. Gemini 3 introduces "context_engineering_is_the_way_to_go" as a thought signature bypass, signaling the model's emphasis on context engineering over prompt engineering. Strategies include: context caching for repeated large contexts, File API for media, structured output for reliable parsing, and thinking budget tuning for cost-quality tradeoffs.

## Key Facts

- [VERIFIED] System instruction + contents + tools = full context (GEMAPI-SC-GOOG-GENCNT)
- [VERIFIED] Thought signatures for reasoning continuity across turns (GEMAPI-SC-GOOG-THINKG)
- [VERIFIED] Gemini 3: context circulation between tools (GEMAPI-SC-GOOG-GEM3DV)
- [VERIFIED] Context caching for cost optimization (GEMAPI-SC-GOOG-CACHNG)
- [VERIFIED] countTokens for budget management (GEMAPI-SC-GOOG-TOKENS)

## Context Budget Allocation

A typical context budget for a Gemini request:

```
Total Context Window (e.g., 1M tokens)
├─> System Instruction: ~500-2000 tokens
├─> Cached Content: variable (documents, files)
├─> Tools (function declarations): ~200-1000 tokens per tool
├─> Conversation History: grows per turn
├─> User Input (current turn): variable
├─> Reserved for Output: maxOutputTokens
└─> Reserved for Thinking: thinkingBudget
```

**Formula**: Available input = context_window - maxOutputTokens - thinkingBudget

## Context Engineering Patterns

### Pattern 1: Layered Context

```python
# Layer 1: Persistent rules (system instruction)
# Layer 2: Domain knowledge (cached content / files)
# Layer 3: Session context (conversation history)
# Layer 4: Current query (user input)

from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="Layer 1: You are a Python expert. Always use type hints.",
        temperature=0.3,
    ),
    contents=[
        # Layer 3: Previous context
        types.Content(role="user", parts=[types.Part(text="I'm building a REST API")]),
        types.Content(role="model", parts=[types.Part(text="Great! I can help with that.")]),
        # Layer 4: Current query
        types.Content(role="user", parts=[types.Part(text="Add authentication middleware")]),
    ]
)
print(response.text)
```

### Pattern 2: Tool Context Circulation (Gemini 3)

```python
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Gemini 3: Multiple tools share context automatically
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(code_execution=types.ToolCodeExecution()),
        ],
    ),
    contents="Find the latest Python release version, then write code to check if my version is up to date."
)
# Model: searches web -> gets version -> writes code using that data
print(response.text)
```

### Pattern 3: Cost-Optimized Repeated Queries

```python
from google import genai
from google.genai import types
import time
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Upload large reference material once
uploaded = client.files.upload(file="api_docs.pdf")
while uploaded.state == "PROCESSING":
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

# Cache for repeated use
cache = client.caches.create(
    model="gemini-2.5-flash",
    config=types.CreateCachedContentConfig(
        system_instruction="Answer questions about this API documentation.",
        contents=[types.Content(role="user", parts=[
            types.Part(file_data=types.FileData(
                mime_type="application/pdf", file_uri=uploaded.uri
            ))
        ])],
        ttl="3600s",
    )
)

# Multiple queries at reduced cost
questions = [
    "What endpoints are available?",
    "How does authentication work?",
    "What are the rate limits?",
]

for q in questions:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        cached_content=cache.name,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disable thinking for simple extraction
        ),
        contents=q
    )
    print(f"Q: {q}\nA: {response.text[:200]}...\n")
```

## Comparison with Other APIs

### vs OpenAI

- **Context window**: Gemini: 1M tokens | OpenAI: 128-200K tokens
- **System instruction**: Gemini: separate field | OpenAI: system message in array
- **Context caching**: Gemini: explicit API | OpenAI: automatic
- **Tool circulation**: Gemini 3: built-in | OpenAI: manual orchestration

### vs Anthropic

- **Context window**: Gemini: 1M tokens | Anthropic: 200K tokens
- **Context caching**: Gemini: explicit | Anthropic: cache_control blocks (auto-extend)
- **Thought signatures**: Gemini: explicit preservation | Anthropic: thinking block signatures

## Limitations and Known Issues

- Context quality may degrade at extreme token counts (>500K) for some tasks
- Thinking budget compounds with large contexts for billing

## Gotchas and Quirks

- Reference material BEFORE the question performs better ("given this context, answer...")
- Disable thinking for simple extraction tasks to save cost
- Context caching TTL starts from creation, not last access
- Gemini 3 thought signature bypass: "context_engineering_is_the_way_to_go"
- Tool declarations consume context tokens - minimize unused tool definitions
- Conversation history grows linearly - prune old turns for long sessions

## Sources

- GEMAPI-SC-GOOG-GENCNT: https://ai.google.dev/api/generate-content [VERIFIED]
- GEMAPI-SC-GOOG-GEM3DV: https://ai.google.dev/gemini-api/docs/gemini-3 [VERIFIED]
- GEMAPI-SC-GOOG-THINKG: https://ai.google.dev/gemini-api/docs/thinking [VERIFIED]
- GEMAPI-SC-GOOG-LNGCTX: https://ai.google.dev/gemini-api/docs/long-context [VERIFIED]

## Document History

**[2026-03-20 07:35]**
- Fixed: types.CodeExecution() does not exist in SDK. Corrected to types.ToolCodeExecution()
- Source: google-genai v1.68.0, google/genai/types.py

**[2026-03-20 05:50]**
- Initial document created
