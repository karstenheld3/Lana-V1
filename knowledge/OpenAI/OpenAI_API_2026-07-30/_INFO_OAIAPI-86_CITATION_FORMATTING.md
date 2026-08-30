# Citation Formatting

**Doc ID**: OAIAPI-IN86
**Goal**: Document citation formatting for web search and file search results
**Version scope**: API v1, Documentation date 2026-07-30

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

Guide for formatting citations in model responses. When using web search or file search tools, the model returns source citations. This guide covers citation format configuration, display patterns, and integration with UI components. Useful for research and content generation applications requiring source attribution. [VERIFIED] (OAIAPI-SC-OAI-GCITN (https://developers.openai.com/api/docs/guides/citation-formatting))

## Key Facts

- **Tools that produce citations**: Web search, file search (vector store) [VERIFIED]
- **Citation format**: Inline annotations in response output [VERIFIED]
- **Configuration**: Automatic when tools are enabled, no extra setup required
- **Use case**: Research apps, content generation with source attribution

## How Citations Work

1. Model uses web_search or file_search tool during generation
2. Response includes citation annotations linked to source URLs or file chunks
3. Client extracts annotations and renders as footnotes, links, or inline references

## Citation Types

### Web Search Citations

Generated when `web_search` tool is active:
- Source URL
- Page title
- Relevant snippet from source

### File Search Citations

Generated when `file_search` tool is active:
- File name and ID
- Chunk/passage reference
- Score/relevance indicator

## SDK Examples (Python)

### Extracting Web Search Citations

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="What are the latest developments in quantum computing?",
    tools=[{"type": "web_search"}],
)

# Access response text
print(response.output_text)

# Extract citations from output items
for item in response.output:
    if hasattr(item, "annotations"):
        for annotation in item.annotations:
            print(f"  Source: {annotation.url}")
            print(f"  Title: {annotation.title}")
```

### Extracting File Search Citations

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input="Summarize the key findings from the research paper.",
    tools=[{
        "type": "file_search",
        "vector_store_ids": ["vs_abc123"],
    }],
)

# Citations reference file chunks
for item in response.output:
    if hasattr(item, "annotations"):
        for annotation in item.annotations:
            print(f"  File: {annotation.filename}")
            print(f"  Quote: {annotation.text}")
```

## Display Patterns

- **Footnotes**: Number citations [1], [2] and list sources at bottom
- **Inline links**: Render as clickable hyperlinks in text
- **Hover cards**: Show source preview on hover
- **Collapsible sources**: Expandable section showing all references

## Gotchas and Quirks

- **Citations are automatic**: No parameter to force/disable individual citations [VERIFIED]
- **Not all responses cite**: Model only cites when using search tools [VERIFIED]
- **Annotation format varies**: Structure differs between web_search and file_search [VERIFIED]

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

- OAIAPI-SC-OAI-GCITN - Citation formatting guide (https://developers.openai.com/api/docs/guides/citation-formatting)

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 22:00]**
- Enriched: Citation types, extraction examples, display patterns, gotchas

**[2026-05-22 13:05]**
- Initial documentation (gap found during /improve review)
