# Response Input Items

**Doc ID**: OAIAPI-IN10
**Goal**: Document API for listing input items associated with a response
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI-IN06_RESPONSES_API.md [OAIAPI-IN06]` for Responses API context

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

The Response Input Items API (GET /v1/responses/{response_id}/input_items) retrieves the input items provided to generate a specific response. Returns paginated list of input messages, system prompts, and other input content. Useful for auditing, debugging, and understanding what context was provided to model. Each item includes role, content, and metadata. Items returned in chronological order. Works with both direct responses and conversation-linked responses. API unchanged from 2026-03-20. [VERIFIED] (OAIAPI-SC-OAI-RESINP)

## Key Facts

- **Endpoint**: GET /v1/responses/{response_id}/input_items [VERIFIED] (OAIAPI-SC-OAI-RESINP)
- **Purpose**: Retrieve input items for audit and debugging [VERIFIED]
- **Pagination**: Supports limit and cursor parameters [VERIFIED]
- **Order**: Items returned chronologically [VERIFIED]
- **Content**: Includes full input content and metadata [VERIFIED]

## Request Parameters

### Path Parameters

- **response_id**: Response ID to retrieve input items for

### Query Parameters

- **limit**: Number of items to return (default: 20, max: 100)
- **after**: Cursor for pagination (item ID)
- **before**: Cursor for reverse pagination (item ID)

## Response Schema

```json
{
  "object": "list",
  "data": [
    {
      "id": "item_abc123",
      "object": "conversation.item",
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What is quantum computing?"
        }
      ],
      "created_at": 1234567890
    }
  ],
  "first_id": "item_abc123",
  "last_id": "item_def456",
  "has_more": false
}
```

### Item Object Fields

- **id**: Unique item identifier
- **object**: Object type ("conversation.item")
- **type**: Item type (message, function_call, etc.)
- **role**: Role (user, assistant, system, tool)
- **content**: Array of content objects
- **created_at**: Unix timestamp

## Pagination

### Forward Pagination

```
GET /v1/responses/{response_id}/input_items?limit=20
GET /v1/responses/{response_id}/input_items?limit=20&after={last_id}
```

### Reverse Pagination

```
GET /v1/responses/{response_id}/input_items?limit=20&before={first_id}
```

## SDK Examples (Python)

### List All Input Items

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-sol",
    input=[
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hello"}
    ]
)

items = client.responses.input_items.list(response.id)

for item in items.data:
    print(f"{item.role}: {item.content[0].text}")
```

### Paginated Retrieval

```python
from openai import OpenAI

client = OpenAI()

response_id = "resp_abc123"
all_items = []
after = None

while True:
    items = client.responses.input_items.list(
        response_id,
        limit=100,
        after=after
    )
    
    all_items.extend(items.data)
    
    if not items.has_more:
        break
    
    after = items.last_id

print(f"Total input items: {len(all_items)}")
```

### Audit Logger

```python
from openai import OpenAI
import json
from datetime import datetime

class ResponseAuditor:
    def __init__(self):
        self.client = OpenAI()
    
    def audit_response(self, response_id: str, output_file: str):
        items = self.client.responses.input_items.list(response_id)
        
        audit_data = {
            "response_id": response_id,
            "audited_at": datetime.utcnow().isoformat(),
            "input_items": []
        }
        
        for item in items.data:
            audit_data["input_items"].append({
                "id": item.id,
                "role": item.role,
                "type": item.type,
                "content": [c.text if c.type == "text" else c.type 
                           for c in item.content],
                "created_at": item.created_at
            })
        
        with open(output_file, 'w') as f:
            json.dump(audit_data, f, indent=2)
        
        return audit_data

# Usage
auditor = ResponseAuditor()
audit = auditor.audit_response("resp_abc123", "audit_log.json")
print(f"Audited {len(audit['input_items'])} input items")
```

### Conversation History Reconstruction

```python
from openai import OpenAI

def reconstruct_conversation(response_id: str):
    client = OpenAI()
    
    items = client.responses.input_items.list(response_id, limit=100)
    
    conversation = []
    for item in items.data:
        if item.type == "message":
            conversation.append({
                "role": item.role,
                "content": item.content[0].text if item.content else ""
            })
    
    return conversation

# Usage
history = reconstruct_conversation("resp_abc123")
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

## Error Responses

- **404 Not Found** - Response ID does not exist
- **400 Bad Request** - Invalid pagination parameters
- **403 Forbidden** - Access denied to response

## Differences from Other APIs

- **vs Chat Completions**: No equivalent input listing in Chat Completions API
- **vs Anthropic**: Anthropic doesn't provide input retrieval endpoint
- **vs Conversations Items**: This lists inputs for specific response, not full conversation

## Limitations and Known Issues

- **Tool outputs not included**: Only input items, not tool execution results [VERIFIED] (OAIAPI-SC-OAI-RESINP)
- **Max page size**: Limited to 100 items per request [VERIFIED]
- **No filtering**: Cannot filter by role or type [ASSUMED]

## Gotchas and Quirks

- **Conversation context**: For conversation-linked responses, only shows input array, not full conversation history [VERIFIED]
- **Order**: Items in chronological order, oldest first [VERIFIED]
- **Cursor-based pagination**: Uses item IDs as cursors, not offset-based [VERIFIED]

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

- OAIAPI-SC-OAI-RESINP - GET List input items
- OAIAPI-SC-OAI-RESCRT - POST Create a response

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 14:20]**
- Enriched: Full request/response schema, pagination, SDK examples, gotchas from 2026-03-20
- Updated: Model refs to gpt-5.5

**[2026-05-22 11:40]**
- Stub created
