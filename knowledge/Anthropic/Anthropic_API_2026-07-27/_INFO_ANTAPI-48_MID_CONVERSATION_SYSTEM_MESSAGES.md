# Mid-Conversation System Messages

**Doc ID**: ANTAPI-IN48
**Goal**: Document mid-conversation system messages for dynamic instruction injection during long-running sessions
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` for Messages API request schema

## Summary

Mid-conversation system messages allow sending `role: "system"` messages within the `messages` array (not just at the top-level `system` parameter). This enables changing instructions mid-conversation while preserving prompt cache hits, particularly useful for long-running agentic sessions. Available on Claude Opus 5, Opus 4.8, Fable 5, Mythos 5, and Sonnet 5. No beta header is required.

## Key Facts

- **Message Role**: `"system"` in `messages` array
- **Placement**: After a `user` turn (not after `assistant` turns)
- **Cache Benefit**: Preserves prompt cache hits when instructions change
- **Beta Header**: None required (GA)
- **Supported Models**: Opus 5, Opus 4.8, Fable 5, Mythos 5, Sonnet 5
- **Not Supported**: Opus 4.7 (rejects with 400 error), Opus 4.6, Sonnet 4.6, Haiku 4.5
- **Status**: GA

## Supported Models

- **claude-opus-5** - Full support
- **claude-opus-4-8** - Full support (first model to support this feature)
- **claude-fable-5** - Full support
- **claude-mythos-5** - Full support
- **claude-sonnet-5** - Full support (confirmed Jul 15)
- **claude-opus-4-7** - **Not supported**: Returns 400 error if `role: "system"` appears in messages

## Basic Usage

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    system="You are a helpful coding assistant.",
    messages=[
        {"role": "user", "content": "Write a Python function to sort a list."},
        {"role": "assistant", "content": "Here's a sorting function:\n\n```python\ndef sort_list(items):\n    return sorted(items)\n```"},
        {"role": "user", "content": "Now add type hints."},
        # Mid-conversation system message: change instructions without breaking cache
        {"role": "system", "content": "From now on, also include docstrings in all code."},
        {"role": "user", "content": "Rewrite the function with both type hints and docstrings."},
    ],
)
```

## Placement Rules

System messages in the `messages` array must follow placement rules:

- Must appear **after a user turn** (after `role: "user"`)
- Cannot appear after an `assistant` turn
- Cannot appear as the first message in the array
- Multiple system messages can be interspersed throughout the conversation
- The top-level `system` parameter still works as the initial system prompt

## Cache Preservation

The primary benefit is maintaining prompt cache hits during long-running sessions:

```python
# Without mid-conversation system messages:
# Changing the top-level system prompt invalidates the entire cache prefix

# With mid-conversation system messages:
# The original system prompt and conversation history remain cached
# Only the new system message is uncached
messages = [
    {"role": "user", "content": "First question..."},
    {"role": "assistant", "content": "First answer..."},
    {"role": "user", "content": "Second question..."},
    {"role": "assistant", "content": "Second answer..."},
    # This preserves cache for everything above
    {"role": "system", "content": "Switch to formal academic tone."},
    {"role": "user", "content": "Third question in new style..."},
]
```

## Gotchas and Quirks

- Claude Opus 4.7 returns 400 if `role: "system"` appears in messages (breaking change from 4.8)
- System messages in the array are additive to the top-level `system` parameter, not replacements
- Placement after assistant turns is not allowed; must be after user turns
- Available on Claude API, Amazon Bedrock, and Google Cloud Vertex AI
- Not available on Microsoft Foundry (as of Jul 2026)

## Related Endpoints

- `_INFO_ANTAPI-08_MESSAGES.md [ANTAPI-IN08]` - Messages API request schema
- `_INFO_ANTAPI-20_PROMPT_CACHING.md [ANTAPI-IN20]` - Prompt caching integration

## Sources

- ANTAPI-SC-ANTH-MIDSYS - https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages - Mid-conversation system messages guide
- ANTAPI-SC-ANTH-MIGR - https://platform.claude.com/docs/en/about-claude/models/migration-guide - Migration guide (model compatibility)

## SDK Verification

Examples written for `anthropic` SDK 0.120.0. Pending re-verification in Prompt 3.

## Document History

**[2026-07-26]**
- Initial documentation created (new topic)
- Covers: placement rules, cache preservation, model compatibility, breaking change on Opus 4.7
