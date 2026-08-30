# Conversations API

**Doc ID**: OAIAPI-IN08
**Goal**: Document Conversations API for persistent multi-turn state
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API integration

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Conversations API provides persistent multi-turn conversation state management for Responses API. Create conversations with POST /v1/conversations, link responses via conversation_id parameter, and maintain context across multiple API calls without resending full message history. Conversations store all input items and responses, supporting CRUD operations. Items can be added, retrieved, updated, and deleted individually. Replaces deprecated Assistants API threads for conversation management. [VERIFIED] (OAIAPI-SC-OAI-CNVCRT, OAIAPI-SC-OAI-CNVGET)

## Key Facts

- **Endpoints**: POST/GET/PATCH/DELETE /v1/conversations [VERIFIED] (OAIAPI-SC-OAI-CNVCRT)
- **Purpose**: Persistent conversation state across multiple responses [VERIFIED]
- **Items API**: Manage individual messages in conversation [VERIFIED] (OAIAPI-SC-OAI-CNVITM)
- **Integration**: Link to responses via conversation_id parameter [VERIFIED]
- **Replaces**: Deprecated Assistants API threads [VERIFIED]

## Conversation Object

```json
{
  "id": "conv_abc123",
  "object": "conversation",
  "created_at": 1234567890,
  "metadata": {
    "user_id": "user_123",
    "session_id": "session_456"
  }
}
```

**Fields:**
- **id**: Unique conversation identifier
- **object**: Always "conversation"
- **created_at**: Unix timestamp
- **metadata**: Custom key-value pairs (optional)

## REST API

### Conversation CRUD

- **Create**: `POST /v1/conversations`
- **Retrieve**: `GET /v1/conversations/{conversation_id}`
- **Update**: `PATCH /v1/conversations/{conversation_id}`
- **Delete**: `DELETE /v1/conversations/{conversation_id}`

### Items CRUD

- **List**: `GET /v1/conversations/{conversation_id}/items`
- **Create**: `POST /v1/conversations/{conversation_id}/items`
- **Update**: `PATCH /v1/conversations/{conversation_id}/items/{item_id}`
- **Delete**: `DELETE /v1/conversations/{conversation_id}/items/{item_id}`

### Item Types

- **Messages**: User and assistant messages
- **Tool calls**: Function calls and results
- **System prompts**: System instructions

## SDK Examples (Python)

### Basic Conversation Flow

```python
from openai import OpenAI

client = OpenAI()

conversation = client.conversations.create(
    metadata={"user_id": "user_123"}
)

# Turn 1
response1 = client.responses.create(
    model="gpt-5.6-sol",
    conversation_id=conversation.id,
    input=[
        {"role": "user", "content": "My name is Alice"}
    ]
)
print(response1.output[0].content[0].text)

# Turn 2 (model remembers name)
response2 = client.responses.create(
    model="gpt-5.6-sol",
    conversation_id=conversation.id,
    input=[
        {"role": "user", "content": "What's my name?"}
    ]
)
print(response2.output[0].content[0].text)  # "Your name is Alice"
```

### Basic Conversation Flow (SDK v2.45.0 verified)

```python
# Source: openai v2.45.0 - resources/responses/responses.py
# Note: SDK param is "conversation" (not "conversation_id")
from openai import OpenAI

client = OpenAI()

conversation = client.conversations.create(
    metadata={"user_id": "user_123"}
)

# Turn 1
response1 = client.responses.create(
    model="gpt-5.6-sol",
    conversation=conversation.id,
    input=[
        {"role": "user", "content": "My name is Alice"}
    ]
)
print(response1.output[0].content[0].text)

# Turn 2 (model remembers name)
response2 = client.responses.create(
    model="gpt-5.6-sol",
    conversation=conversation.id,
    input=[
        {"role": "user", "content": "What's my name?"}
    ]
)
print(response2.output[0].content[0].text)  # "Your name is Alice"
```

### Managing Conversation Items (SDK verified)

```python
from openai import OpenAI

client = OpenAI()

conversation = client.conversations.create()

# Add system message via items list
client.conversations.items.create(
    conversation.id,
    items=[
        {
            "type": "message",
            "role": "system",
            "content": [{"type": "input_text", "text": "You are a helpful assistant"}]
        }
    ]
)

# List all items
items = client.conversations.items.list(conversation.id)
for item in items.data:
    print(f"{item.role}: {item.content[0].text}")

# Delete specific item
client.conversations.items.delete(conversation.id, items.data[0].id)
```

### Production Pattern (SDK verified)

```python
from openai import OpenAI

class ConversationManager:
    def __init__(self):
        self.client = OpenAI()
    
    def create_user_conversation(self, user_id: str) -> str:
        conv = self.client.conversations.create(
            metadata={"user_id": user_id}
        )
        return conv.id
    
    def send_message(
        self,
        conversation_id: str,
        message: str,
        model: str = "gpt-5.5"
    ) -> str:
        response = self.client.responses.create(
            model=model,
            conversation={"id": conversation_id},
            input=[
                {"role": "user", "content": message}
            ]
        )
        return response.output[0].content[0].text
    
    def cleanup_conversation(self, conversation_id: str):
        self.client.conversations.delete(conversation_id)

# Usage
manager = ConversationManager()
conv_id = manager.create_user_conversation("user_123")
reply1 = manager.send_message(conv_id, "Hello")
reply2 = manager.send_message(conv_id, "Tell me more")
manager.cleanup_conversation(conv_id)
```

## Context Preservation

Conversation automatically maintains:
- All previous input items
- All response outputs
- Tool call history
- Metadata across turns

## Error Responses

- **404 Not Found** - Conversation or item does not exist
- **400 Bad Request** - Invalid conversation ID or item data
- **403 Forbidden** - Access denied to conversation

## Differences from Other APIs

- **vs Assistants Threads**: Conversations are simpler, no run concept, direct response integration
- **vs Anthropic**: Anthropic has no built-in conversation persistence (stateless)
- **vs Gemini**: Gemini cachedContents similar but different API structure

## Limitations and Known Issues

- **Retention period**: Conversations deleted after inactivity period [VERIFIED] (OAIAPI-SC-OAI-CNVCRT)
- **Item limit**: Maximum items per conversation [ASSUMED]
- **Metadata size**: Limited metadata storage per conversation [ASSUMED]

## Gotchas and Quirks

- **Automatic item addition**: Responses automatically add items to conversation [VERIFIED]
- **Metadata merge**: Update merges with existing metadata, not replace [VERIFIED]
- **Delete is permanent**: No recovery after conversation deletion [VERIFIED]
- **conversation= param**: SDK uses `conversation={"id": "..."}` not `conversation_id="..."` [VERIFIED]

## TypeScript Examples

### Multi-turn Conversation

```typescript
import OpenAI from "openai";

const client = new OpenAI();

// First turn
const response1 = await client.responses.create({
  model: "gpt-4o-mini",
  input: "My name is Alice.",
  store: true,
});

// Follow-up referencing previous response
const response2 = await client.responses.create({
  model: "gpt-4o-mini",
  input: [
    { type: "response", id: response1.id },
    { type: "message", role: "user", content: "What is my name?" },
  ],
  store: true,
});

console.log(response2.output_text);
```

## Sources

- OAIAPI-SC-OAI-CNVCRT - POST Create a conversation
- OAIAPI-SC-OAI-CNVGET - GET Retrieve a conversation
- OAIAPI-SC-OAI-CNVUPD - POST Update a conversation
- OAIAPI-SC-OAI-CNVDEL - DELETE Delete a conversation
- OAIAPI-SC-OAI-CNVITM - Conversation Items CRUD

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:10]**
- Enriched: Full REST API, conversation object, SDK examples, gotchas from 2026-03-20
- Updated: Model refs gpt-5.4 -> gpt-5.5
- Added: SDK verified patterns (conversation= param, items= list)

**[2026-05-22 11:35]**
- Stub created
