# INFO: Prompt Engineering

**Doc ID**: GROKAPI-IN36
**Goal**: Best practices for Grok prompting, system messages, temperature, top_p, persona
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Grok's default persona is witty and slightly irreverent (inspired by "Hitchhiker's Guide to the Galaxy"). System messages can override this persona for professional use cases. Standard prompt engineering techniques apply: clear instructions, few-shot examples, step-by-step reasoning prompts. Temperature (0.0-2.0, default ~0.7) and top_p control randomness. For tool-using requests, prompting affects which tools the model chooses and how many invocations it makes. For structured outputs, system prompts should focus on the task since the schema handles format. Reasoning models benefit from high-level goal prompts rather than step-by-step instructions. [VERIFIED] (GROKAPI-SC-XAI-PROMPTENG | https://docs.x.ai/developers/prompting)

## Key Facts

- [VERIFIED] Default persona: witty, slightly irreverent (GROKAPI-SC-XAI-PROMPTENG)
- [VERIFIED] System message overrides default persona (GROKAPI-SC-XAI-PROMPTENG)
- [VERIFIED] Temperature range: 0.0-2.0 (GROKAPI-SC-XAI-RESTREF)
- [VERIFIED] top_p: nucleus sampling parameter (GROKAPI-SC-XAI-RESTREF)

## Quick Reference

- **Override persona**: Use system message with professional tone instructions
- **Temperature**: 0.0 = deterministic, 1.0 = balanced, 2.0 = very creative
- **Tools**: Prompt affects tool selection and invocation count
- **Reasoning**: Use high-level goals, not step-by-step instructions

## Examples

### Professional System Message

```python
response = client.responses.create(
    model="grok-4.20-beta-latest-non-reasoning",
    input=[
        {"role": "system", "content": "You are a professional financial analyst. Provide concise, data-driven responses."},
        {"role": "user", "content": "Analyze the current market trends."},
    ],
)
```

### Low Temperature for Consistency

```python
response = client.chat.completions.create(
    model="grok-4.20-beta-latest-non-reasoning",
    messages=[{"role": "user", "content": "Classify this text as positive or negative: 'Great product!'"}],
    temperature=0.0,
)
```

## Grok-Specific Tips

- Grok's default personality is more conversational than competitors - override with system message for formal use
- For reasoning models (grok-3-mini), set `reasoning.effort` instead of detailed step-by-step prompts
- For tool-using requests, be specific about what data you need to minimize unnecessary tool calls
- Multi-agent requests benefit from focused, specific queries rather than broad ones

## Differences from Other APIs

### vs OpenAI
- **Persona**: Grok has a built-in personality; GPT is neutral by default
- **Same techniques**: Few-shot, chain-of-thought, system messages all work

### vs Anthropic
- **Persona**: Claude has a careful, cautious default; Grok is witty
- **System message**: Same concept, different placement (Anthropic separates system from messages)

## Sources

- GROKAPI-SC-XAI-PROMPTENG | https://docs.x.ai/developers/prompting | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:15]**
- Initial document created with prompt engineering guidance
