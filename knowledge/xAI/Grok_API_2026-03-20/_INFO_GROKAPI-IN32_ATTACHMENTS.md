# INFO: File Attachments and Formats

**Doc ID**: GROKAPI-IN32
**Goal**: Supported file formats, size limits, attachment patterns
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

File attachments support various document formats for use with chat, collections, and batch processing. Supported formats include PDF, plain text, CSV, JSON, Markdown, and common document types. Files can be attached to messages for one-off analysis (via `attachment_search`) or uploaded to collections for persistent RAG. The Files API handles upload and management. Size limits apply per file and per request. [VERIFIED] (GROKAPI-SC-XAI-FILES | https://docs.x.ai/developers/files)

## Key Facts

- [VERIFIED] Multiple file format support: PDF, TXT, CSV, JSON, MD, and more (GROKAPI-SC-XAI-FILES)
- [VERIFIED] Two attachment patterns: per-message (attachment_search) and persistent (collections) (GROKAPI-SC-XAI-FILES)
- [VERIFIED] Files managed via `/v1/files` endpoint (GROKAPI-SC-XAI-RESTREF)

## Attachment Patterns

- **Per-message**: Upload file, attach to message with `attachment_search` tool ($10/1K invocations)
- **Collections**: Upload to collection, query with `collections_search` tool ($2.50/1K invocations)
- **Batch**: Upload JSONL for batch processing

## Sources

- GROKAPI-SC-XAI-FILES | https://docs.x.ai/developers/files | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:05]**
- Initial document created
