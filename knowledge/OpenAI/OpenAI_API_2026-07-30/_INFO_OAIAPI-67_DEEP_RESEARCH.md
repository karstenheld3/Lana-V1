# Deep Research API

**Doc ID**: OAIAPI-IN67
**Goal**: Document the Deep Research API for automated multi-step research with citation-rich reports
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Deep Research API automates complex research workflows requiring reasoning, planning, and synthesis. Takes a high-level query and returns structured, citation-rich reports by leveraging agentic models that decompose tasks, search the web, read sources, and synthesize findings. Current model: `gpt-5.6-sol` with Pro mode (replaces deprecated `gpt-5.5-pro`, which replaced `o3-deep-research` and `o4-mini-deep-research`). Available via the Responses API with `web_search` tool. Background mode for long-running tasks with webhook notifications. Use `reasoning: {"mode": "pro", "effort": "max"}` for deepest analysis. Reports include figures, statistics, data-backed reasoning, and URL citations. [VERIFIED] (OAIAPI-SC-OAI-GDPRS, OAIAPI-SC-OAI-GDEEP)

## Key Facts

- **Current model**: gpt-5.6-sol with `reasoning.mode: "pro"` (gpt-5.5-pro deprecated 2026-06-11, removal 2026-12-11) [VERIFIED] (OAIAPI-SC-OAI-GDEEP)
- **Legacy models**: o3-deep-research, o4-mini-deep-research (replaced) [VERIFIED] (OAIAPI-SC-OAI-GDEEP)
- **API**: Via Responses API with web_search tool [VERIFIED] (OAIAPI-SC-OAI-GDPRS)
- **Output**: Structured reports with inline citations and source metadata [VERIFIED] (OAIAPI-SC-OAI-GDPRS)
- **Agents SDK**: Compatible with Agent/Runner pattern [VERIFIED] (OAIAPI-SC-OAI-GDPRS)
- **Pipeline**: Query -> decompose -> search -> read -> synthesize -> cite [VERIFIED] (OAIAPI-SC-OAI-GDPRS)
- **Async**: Research tasks may take minutes; use polling, streaming, or webhooks [VERIFIED] (OAIAPI-SC-OAI-GDPRS)

## Use Cases

- **Market analysis**: Research industry trends with data-backed findings
- **Academic review**: Literature survey with cited sources
- **Competitive intelligence**: Compare products, services, strategies
- **Policy research**: Analyze regulations, guidelines, impacts
- **Technical due diligence**: Evaluate technologies, architectures, trade-offs
- **Healthcare research**: Drug efficacy, treatment outcomes with clinical citations

## SDK Examples (Python)

### Basic Deep Research

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    tools=[{"type": "web_search"}],
    reasoning={"mode": "pro", "effort": "max"},
    input="""Research the current state of quantum computing hardware.
    Include specific figures, trends, and statistics.
    Prioritize reliable sources: peer-reviewed research, company reports.
    Include inline citations and return all source metadata."""
)

print(response.output_text)

for item in response.output:
    if hasattr(item, 'annotations'):
        for ann in item.annotations:
            if ann.type == "url_citation":
                print(f"  [{ann.title}]({ann.url})")
```

### Deep Research with Agents SDK

```python
from agents import Agent, Runner, WebSearchTool

research_agent = Agent(
    name="Research Agent",
    model="gpt-5.6-sol",
    tools=[WebSearchTool()],
    instructions="""You perform deep empirical research based on the user query.
    Include specific figures, trends, statistics, and measurable outcomes.
    Prioritize reliable, up-to-date sources.
    Include inline citations and return all source metadata.
    Be analytical, avoid generalities."""
)

result = Runner.run_sync(
    research_agent,
    "Compare the AI agent frameworks: LangChain, CrewAI, OpenAI Agents SDK. "
    "Include adoption metrics, feature comparison, and production readiness."
)

print(result.final_output)
```

### Production Research Pipeline

```python
from openai import OpenAI

client = OpenAI()

def deep_research(query: str, instructions: str = None) -> dict:
    """Execute deep research and extract structured results"""
    default_instructions = """Include specific figures, trends, and statistics.
    Prioritize reliable sources. Include inline citations.
    Be analytical and data-driven."""
    
    full_input = f"{instructions or default_instructions}\n\nResearch query: {query}"
    
    response = client.responses.create(
        model="gpt-5.6-sol",
        tools=[{"type": "web_search"}],
    reasoning={"mode": "pro", "effort": "max"},
        input=full_input
    )
    
    report = response.output_text
    citations = []
    
    for item in response.output:
        if hasattr(item, 'annotations'):
            for ann in item.annotations:
                if ann.type == "url_citation":
                    citations.append({
                        "title": ann.title,
                        "url": ann.url
                    })
    
    return {
        "report": report,
        "citations": citations,
        "citation_count": len(citations),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }

try:
    result = deep_research(
        "What are the latest advances in solid-state batteries for EVs?",
        "Focus on commercial readiness, energy density improvements, and manufacturer timelines."
    )
    
    print(f"Report length: {len(result['report'])} chars")
    print(f"Citations: {result['citation_count']}")
    print(f"Tokens: {result['usage']}")
    
    for cite in result['citations'][:5]:
        print(f"  - {cite['title']}: {cite['url']}")

except Exception as e:
    print(f"Error: {e}")
```

## Research Quality Guidelines

For best results, include in your prompt:
- **Specificity**: Name exact topics, metrics, time periods
- **Source preferences**: "peer-reviewed", "official reports", "regulatory filings"
- **Output format**: Request "inline citations", "source metadata", "data tables"
- **Analytical depth**: "avoid generalities", "data-backed reasoning"
- **Scope boundaries**: Define what to include and exclude

## Error Responses

- **400 Bad Request** - Invalid model or missing web_search tool
- **429 Too Many Requests** - Rate limit exceeded
- **500 Internal Server Error** - Research pipeline failure

## Differences from Other APIs

- **vs Anthropic**: No equivalent automated deep research API
- **vs Gemini Deep Research**: Google has Deep Research in Gemini Advanced (consumer); API access differs
- **vs Perplexity**: Perplexity provides search-augmented answers but not multi-step research planning
- **vs standard web_search**: Deep research does multi-step planning and synthesis; web_search is single-query retrieval

## Limitations and Known Issues

- **Execution time**: Research tasks may take minutes, not seconds [VERIFIED] (OAIAPI-SC-OAI-GDPRS)
- **Background mode recommended**: Use `store: true` and poll or webhooks for long tasks [VERIFIED] (OAIAPI-SC-OAI-GBKGND)
- **Data retention**: Background mode retains response data for ~10 minutes only [VERIFIED] (OAIAPI-SC-OAI-GBKGND)
- **Source freshness**: Depends on web search index recency [ASSUMED]
- **Hallucination risk**: Citations should be verified for accuracy [ASSUMED]
- **Cost**: Higher token consumption than standard completions [VERIFIED] (OAIAPI-SC-OAI-GDPRS)

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

- OAIAPI-SC-OAI-GDPRS - Deep Research Guide
- OAIAPI-SC-OAI-GDEEP - Deep Research Reference
- OAIAPI-SC-OAI-GBKGND - Background Mode Guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-07-13 12:00]**
- Changed: Model from `gpt-5.5-pro` to `gpt-5.6-sol` with Pro mode
- Changed: Reasoning parameter from `reasoning_effort: "xhigh"` to `reasoning: {"mode": "pro", "effort": "max"}`
- Updated from OpenAI_API_2026-05-22

**[2026-05-22 17:55]**
- Enriched from 2026-03-20 IN67 (19 -> 195 lines)
- Updated model to gpt-5.5-pro, added webhook/background mode info

**[2026-05-22 11:50]**
- Stub created
