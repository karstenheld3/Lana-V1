# Agent Memory Stores

**Doc ID**: ANTAPI-IN49
**Goal**: Document memory store CRUD endpoints for Managed Agents persistent memory
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-40_MANAGED_AGENTS.md [ANTAPI-IN40]` for Managed Agents overview

## Summary

Memory Stores enable Claude Managed Agents to retain information across sessions. Agents can create, read, update, and delete memories organized in a hierarchical path structure. The `agent-memory-2026-07-22` beta header is required for memory store endpoints and replaces the older `managed-agents-2026-04-01` header for these calls. The SDKs (Python 0.116.0+) send this header automatically on memory store calls.

## Key Facts

- **Beta Header**: `agent-memory-2026-07-22` (replaces `managed-agents-2026-04-01` on memory endpoints)
- **Base Path**: `/v1/memory_stores` and `/v1/memory_stores/{memory_store_id}/memories`
- **SDK Versions**: Python 0.116.0+, TypeScript 0.110.0+, Go 1.56.0+
- **Path Structure**: Hierarchical (e.g., `/project/settings/theme`)
- **Listing Order**: Stable, server-defined (order_by/order params ignored with new header)
- **Depth Filter**: `depth` accepts only 0, 1, or omitted (other values return 400)
- **Path Prefix**: `path_prefix` must end with `/` and matches whole path segments
- **Status**: Beta

## Endpoints

### Create Memory Store

```python
import anthropic

client = anthropic.Anthropic()

# Create a new memory store
store = client.beta.memory_stores.create(
    name="project-context",
    description="Stores project preferences and learnings",
)
print(f"Store ID: {store.id}")
```

### List Memory Stores

```python
stores = client.beta.memory_stores.list()
for store in stores:
    print(f"{store.id}: {store.name}")
```

### Create Memory

```python
# Add a memory to a store
memory = client.beta.memory_stores.memories.create(
    memory_store_id="store_abc123",
    path="/project/preferences",
    content="User prefers Python code examples with type hints",
)
```

### List Memories

```python
# List memories with path prefix filter
memories = client.beta.memory_stores.memories.list(
    memory_store_id="store_abc123",
    path_prefix="/project/",  # Must end with /
    depth=1,  # Only 0 or 1 accepted
)
for memory in memories:
    print(f"{memory.path}: {memory.content}")
```

### Update Memory

```python
client.beta.memory_stores.memories.update(
    memory_store_id="store_abc123",
    memory_id="mem_xyz789",
    content="User prefers Python 3.12+ with type hints and dataclasses",
)
```

### Delete Memory

```python
client.beta.memory_stores.memories.delete(
    memory_store_id="store_abc123",
    memory_id="mem_xyz789",
)
```

## Beta Header Migration

- **New header**: `agent-memory-2026-07-22` - Required for memory store endpoints
- **Old header**: `managed-agents-2026-04-01` - Still works on non-memory endpoints; adopted same list behavior on Jul 22
- **Conflict**: Sending both headers on memory store calls returns 400
- **Page cursors**: Cursors issued without the new header are invalid with it; restart from first page when adopting
- **SDK auto-migration**: Python 0.116.0+ automatically sends `agent-memory-2026-07-22` on memory calls

## Webhook Events

Memory store lifecycle events are available via webhooks (since Jul 22):
- `memory_store.created`
- `memory_store.updated`
- `memory_store.deleted`

## Gotchas and Quirks

- `path_prefix` must end with `/` and matches whole segments (not substrings)
- `depth` only accepts 0, 1, or omission; other values return 400
- `order_by` and `order` parameters are ignored under the new header
- Page cursors from old header are incompatible with new header
- Sending both `managed-agents-2026-04-01` and `agent-memory-2026-07-22` returns 400
- Memory content is text-only (no binary/structured data)
- Memory stores are scoped to the organization/workspace

## Related Endpoints

- `_INFO_ANTAPI-40_MANAGED_AGENTS.md [ANTAPI-IN40]` - Managed Agents overview
- `_INFO_ANTAPI-05_VERSIONING.md [ANTAPI-IN05]` - Beta headers

## Sources

- ANTAPI-SC-ANTH-AGMEM - https://platform.claude.com/docs/en/managed-agents/memory - Memory stores documentation
- ANTAPI-SC-ANTH-BETAHDR - https://platform.claude.com/docs/en/api/beta-headers - Beta headers reference

## SDK Verification

Examples written for `anthropic` SDK 0.120.0. Pending re-verification in Prompt 3.

## Document History

**[2026-07-26]**
- Initial documentation created (new topic)
- Covers: memory store CRUD, memory CRUD, beta header migration, webhook events
