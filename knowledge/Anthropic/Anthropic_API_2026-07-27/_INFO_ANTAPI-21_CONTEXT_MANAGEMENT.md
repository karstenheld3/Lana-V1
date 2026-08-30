# Context Window Management

**Doc ID**: ANTAPI-IN21
**Goal**: Document context window sizes, compaction strategies, and token budget management
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` for Messages API request schema
- `_INFO_ANTAPI-13_MODELS.md [ANTAPI-IN13]` for model context window sizes

## Summary

Claude models have fixed context windows (input + output tokens). Context management involves strategies for fitting content within these windows: token counting before sending, conversation summarization, sliding window approaches, and the newer context management capabilities (compaction, editing) available on some models. The Models API reports `max_input_tokens` and `max_output_tokens` for each model. Extended thinking tokens share the output budget with response tokens.

## Key Facts

- **Context Window**: Input tokens + output tokens combined
- **Opus 4.7**: 1M input (GA), 128K output
- **Opus 4.6**: 1M input (GA), 128K output
- **Sonnet 4.6**: 1M input (GA), 64K output
- **Haiku 4.5**: 200K input, 64K output
- **1M Context Beta**: Retired for Sonnet 4.5 and Sonnet 4 (April 30, 2026)
- **Token Counting**: `POST /v1/messages/count_tokens` for pre-check
- **Context Management**: Model capability (compaction, editing strategies)
- **Status**: GA (context management strategies: varies by model)

## Context Window Sizes

Model context windows can be queried via the Models API:

```python
import anthropic

client = anthropic.Anthropic()

model = client.models.retrieve("claude-opus-5")
print(f"Max input: {model.max_input_tokens}")
print(f"Max output: {model.max_output_tokens}")
```

## Management Strategies

### Pre-Request Token Counting

```python
import anthropic

client = anthropic.Anthropic()

messages = [
    {"role": "user", "content": "Very long conversation history..."},
]

count = client.messages.count_tokens(
    model="claude-opus-5",
    messages=messages,
)

model_info = client.models.retrieve("claude-opus-5")
remaining = model_info.max_input_tokens - count.input_tokens
print(f"Tokens used: {count.input_tokens}")
print(f"Remaining capacity: {remaining}")
```

### Sliding Window (Drop Oldest Messages)

```python
def trim_conversation(messages, max_tokens, client, model):
    """Remove oldest messages until within token budget."""
    while len(messages) > 1:
        count = client.messages.count_tokens(
            model=model,
            messages=messages,
        )
        if count.input_tokens <= max_tokens:
            return messages
        # Remove oldest user/assistant pair (keep at least last message)
        messages = messages[2:]
    return messages
```

### Summarization Strategy

```python
import anthropic

client = anthropic.Anthropic()

def summarize_history(messages, model="claude-haiku-3-5-20241022"):
    """Summarize old messages to compress context."""
    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in messages
    )
    summary = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"Summarize this conversation concisely:\n{history_text}",
            }
        ],
    )
    return summary.content[0].text

# Use summary as system context for new conversation
old_messages = [...]  # Long conversation history
summary = summarize_history(old_messages)

new_message = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    system=f"Previous conversation summary: {summary}",
    messages=[{"role": "user", "content": "Continue our discussion..."}],
)
```

## Extended Thinking Token Budget

When using extended thinking, `max_tokens` covers both thinking and response tokens:

- `budget_tokens` (thinking) must be < `max_tokens`
- Remaining tokens after thinking are available for the response
- With interleaved thinking + tools, the limit becomes the full context window

## Gotchas and Quirks

- Context window is shared between input and output; large inputs reduce available output space
- Tool definitions consume input tokens (can be significant with many tools)
- System prompts are part of the input token count
- Images and PDFs are converted to tokens based on their content/dimensions
- Prompt caching helps with repeated prefixes but does not reduce context window usage
- `model_context_window_exceeded` stop reason indicates the model hit its context limit

## Related Endpoints

- `_INFO_ANTAPI-10_TOKEN_COUNTING.md [ANTAPI-IN10]` - Token counting endpoint
- `_INFO_ANTAPI-13_MODELS.md [ANTAPI-IN13]` - Model context window sizes
- `_INFO_ANTAPI-15_EXTENDED_THINKING.md [ANTAPI-IN15]` - Thinking token budgets
- `_INFO_ANTAPI-20_PROMPT_CACHING.md [ANTAPI-IN20]` - Reduce latency for repeated prefixes

## Sources

- ANTAPI-SC-ANTH-CTXMGMT - https://platform.claude.com/docs/en/build-with-claude/context-windows - Context window guide
- ANTAPI-SC-ANTH-MODOVW - https://platform.claude.com/docs/en/about-claude/models/overview - Model specs

## SDK Verification

All 4 Python examples verified against `anthropic` SDK 0.120.0. No corrections needed.

**SDK source files checked**:
- `resources/models.py`: `Models.retrieve(model_id: str)` returns model with `.max_input_tokens`, `.max_output_tokens`
- `resources/messages/messages.py`: `count_tokens(messages, model, ...)` returns `MessageTokensCount` with `.input_tokens`

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Updated from Anthropic_API_2026-03-20
- Changed: Context windows updated (1M GA on Opus 4.7/4.6/Sonnet 4.6)
- Changed: 1M beta retired for Sonnet 4.5/4 (April 30, 2026)
- Added: Opus 4.7 to key facts

**[2026-03-20 06:35]**
- Added: SDK verification section (anthropic 0.120.0, all 4 examples valid)

**[2026-03-20 03:32]**
- Initial documentation created from context window and model documentation
