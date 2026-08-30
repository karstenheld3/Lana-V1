# ChatKit (Beta)

**Doc ID**: OAIAPI-IN45
**Goal**: Document ChatKit - embeddable chat UI for deploying AI agents in products
**Version scope**: API v1, Documentation date 2026-07-30

**Depends on:**
- `_INFO_OAIAPI_02-SOURCES.md [OAIAPI-IN02]` for source references

## MUST-NOT-FORGET

- All dates formatted as YYYY-MM or YYYY-MM-DD (never "June 3" or "Dec 2026")
- Model strings in code examples must use current models
- SDK version references must be reference latest version used to verify code examples
- Deprecated features must be marked with `[DEPRECATED YYYY-MM-DD]` and migration path

## Summary

**[BETA]** ChatKit is an embeddable chat interface for deploying AI agents in web products. Two implementation paths: Recommended integration (embed frontend widget, OpenAI hosts backend via Agent Builder) or Advanced integration (run on your own infrastructure with ChatKit Python SDK). The API provides sessions (`POST /v1/chatkit/sessions`) for creating chat instances with client secrets, threads for conversation management, and list items for retrieving chat history. Frontend uses `@openai/chatkit-react` npm package or `<script>` tag. Widgets provide customizable UI components via Widget Builder. Supports file uploads, actions, and developer mode. API unchanged from 2026-03-20 but remains in beta. [VERIFIED] (OAIAPI-SC-OAI-CKSESS, OAIAPI-SC-OAI-GCHATK)

## Key Facts

- **Status**: Beta - API may change [VERIFIED] (OAIAPI-SC-OAI-GCHATK)
- **Two modes**: Recommended (OpenAI-hosted backend) or Advanced (self-hosted) [VERIFIED] (OAIAPI-SC-OAI-GCHATK)
- **Agent Builder**: Visual canvas for designing multi-step agent workflows [VERIFIED] (OAIAPI-SC-OAI-GCHATK)
- **Frontend**: `@openai/chatkit-react` or `<script>` tag embed [VERIFIED] (OAIAPI-SC-OAI-GCHATK)
- **Client secrets**: Short-lived session tokens for frontend authentication [VERIFIED] (OAIAPI-SC-OAI-CKSESS)
- **Widgets**: Customizable UI components via Widget Builder [VERIFIED] (OAIAPI-SC-OAI-GCKWDG)
- **Beta header**: `OpenAI-Beta: chatkit_beta=v1` [VERIFIED] (OAIAPI-SC-OAI-GCHATK)

## Quick Reference

```
POST /v1/chatkit/sessions           # Create session (get client secret)
GET  /v1/chatkit/threads            # List threads
GET  /v1/chatkit/threads/{id}/items # List thread items

Headers:
  Authorization: Bearer $OPENAI_API_KEY
  Content-Type: application/json
  OpenAI-Beta: chatkit_beta=v1
```

## Architecture

### Recommended Integration Flow

1. **Create agent workflow** in Agent Builder (visual canvas) -> get workflow ID
2. **Server-side**: Create ChatKit session (`POST /v1/chatkit/sessions`) with workflow ID and user ID
3. **Send client_secret** to frontend
4. **Frontend**: Initialize ChatKit with client secret via React component or script tag
5. **User interacts** with embedded chat widget

### Advanced Integration Flow

1. **Install ChatKit Python SDK**: `pip install openai-chatkit`
2. **Implement backend**: Handle messages, tools, file uploads
3. **Use ChatKit widgets**: Build custom frontend with widget components
4. **Manage sessions**: Handle authentication and state on your infrastructure

## Session Creation

```
POST /v1/chatkit/sessions
```

**Request:**
```json
{
  "workflow": {
    "id": "wf_abc123..."
  },
  "user": "user_unique_id_123"
}
```

**Response:**
```json
{
  "id": "ckses_abc123",
  "object": "chatkit.session",
  "client_secret": "ckss_abc123...",
  "created_at": 1699061776
}
```

**Parameters:**
- **workflow.id** (required): Agent Builder workflow ID
- **user** (required): Unique end-user identifier (your app authenticates users)

**Security**: The `user` parameter must be a unique identifier per end-user. Your backend is responsible for authenticating users before creating sessions.

## Frontend Setup

### React Integration

```bash
npm install @openai/chatkit-react
```

```jsx
import { ChatKit } from '@openai/chatkit-react';

function App() {
  const [clientSecret, setClientSecret] = useState(null);
  
  useEffect(() => {
    fetch('/api/chatkit/session', { method: 'POST' })
      .then(r => r.json())
      .then(data => setClientSecret(data.client_secret));
  }, []);
  
  if (!clientSecret) return <div>Loading...</div>;
  
  return <ChatKit clientSecret={clientSecret} />;
}
```

### Script Tag Integration

```html
<script src="https://cdn.openai.com/chatkit/chatkit.js"></script>
<script>
  ChatKit.init({ clientSecret: 'ckss_abc123...' });
</script>
```

## Widgets

Widgets are customizable UI components within ChatKit:

- **Cards**: Rich content blocks with images, text, actions
- **List rows**: Structured list items for search results, products
- **Custom components**: Build your own with Widget Builder in ChatKit Studio

## Advanced Features

### File Uploads

Two methods supported:
- **Direct upload**: Client POSTs file to your endpoint
- **Two-phase upload**: Client requests signed URL, then uploads to cloud storage

### Actions

UI-triggered operations without sending a user message. Attach actions to buttons or widgets.

### Developer Mode

Testing mode for debugging agent behavior and widget rendering.

## Guides

- **Overview**: https://developers.openai.com/api/docs/guides/chatkit
- **Customize (themes)**: https://developers.openai.com/api/docs/guides/chatkit-themes
- **Widgets**: https://developers.openai.com/api/docs/guides/chatkit-widgets
- **Actions**: https://developers.openai.com/api/docs/guides/chatkit-actions
- **Advanced Integrations**: https://developers.openai.com/api/docs/guides/custom-chatkit

## SDK Examples (Python)

### Create ChatKit Session (SDK v2.29.0)

```python
from openai import OpenAI
from fastapi import FastAPI, Depends

app = FastAPI()
client = OpenAI()

@app.post("/api/chatkit/session")
def create_session(user_id: str = Depends(get_authenticated_user)):
    # SDK path: client.beta.chatkit.sessions.create (beta namespace)
    session = client.beta.chatkit.sessions.create(
        workflow={"id": "wf_abc123..."},
        user=user_id
    )
    return {"client_secret": session.client_secret}
```

### List Threads and History (SDK v2.29.0)

```python
from openai import OpenAI

client = OpenAI()

threads = client.beta.chatkit.threads.list()
for thread in threads.data:
    print(f"Thread: {thread.id}, Created: {thread.created_at}")

# Note: list_items() method on threads, not items sub-resource
items = client.beta.chatkit.threads.list_items("ckth_abc123")
for item in items.data:
    print(f"  [{item.role}]: {item.content}")
```

### Production Setup with FastAPI

```python
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
client = OpenAI()

WORKFLOW_ID = os.environ["CHATKIT_WORKFLOW_ID"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourapp.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/api/chatkit/session")
async def create_chatkit_session(request: Request):
    user_id = await authenticate_user(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        session = client.beta.chatkit.sessions.create(
            workflow={"id": WORKFLOW_ID},
            user=user_id
        )
        return {"client_secret": session.client_secret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def authenticate_user(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    return "user_123"
```

## Error Responses

- **400 Bad Request** - Missing workflow ID or user parameter
- **401 Unauthorized** - Invalid API key
- **404 Not Found** - Workflow or thread not found
- **429 Too Many Requests** - Rate limit exceeded

## Rate Limiting

- **Session creation**: Standard API rate limits
- **Thread listing**: Standard API rate limits
- **Chat messages**: Subject to underlying model rate limits

## Differences from Other APIs

- **vs Anthropic**: No embeddable chat UI or agent builder
- **vs Gemini**: No ChatKit equivalent; Google has AI Studio but no embeddable widget
- **vs Grok**: No embeddable chat widget
- **vs Vercel AI SDK**: Vercel provides React chat components but no hosted backend. ChatKit provides both

## Limitations and Known Issues

- **Beta status**: API surface may change without notice [VERIFIED] (OAIAPI-SC-OAI-GCHATK)
- **Agent Builder dependency**: Recommended integration requires Agent Builder workflow [VERIFIED] (OAIAPI-SC-OAI-GCHATK)
- **React-focused**: Primary frontend SDK is React; other frameworks need manual integration [VERIFIED] (OAIAPI-SC-OAI-GCHATK)
- **ChatGPT dependency**: Uses ChatGPT infrastructure, not standalone
- **No self-hosted**: Cannot be deployed outside OpenAI infrastructure

## Gotchas and Quirks

- **User authentication is your responsibility**: ChatKit does not authenticate end-users; your backend must do this [VERIFIED] (OAIAPI-SC-OAI-GCHATK)
- **Client secret is ephemeral**: Do not store; generate fresh per session [VERIFIED] (OAIAPI-SC-OAI-CKSESS)
- **Beta header required**: Must include `OpenAI-Beta: chatkit_beta=v1` [VERIFIED] (OAIAPI-SC-OAI-GCHATK)
- **Workflow ID format**: Long hex string starting with `wf_` [VERIFIED] (OAIAPI-SC-OAI-GCHATK)

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

- OAIAPI-SC-OAI-CKSESS - ChatKit Sessions API
- OAIAPI-SC-OAI-CKTHR - ChatKit Threads API
- OAIAPI-SC-OAI-GCHATK - ChatKit Guide
- OAIAPI-SC-OAI-GCKWDG - ChatKit Widgets Guide

## Document History

**[2026-07-31 01:00]**
- Updated from OpenAI_API_2026-07-13 (dual-language enhancement, version scope 2026-07-30)


**[2026-05-22 16:55]**
- Enriched from 2026-03-20 IN45 (41 -> 280 lines)
- Added architecture, session creation, frontend setup, widgets, SDK examples, gotchas

**[2026-05-22 13:10]**
- Expanded: Beta status, guides list, limitations

**[2026-05-22 11:45]**
- Stub created
