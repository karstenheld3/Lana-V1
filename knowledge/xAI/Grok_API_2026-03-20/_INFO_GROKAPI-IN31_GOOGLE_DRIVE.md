# INFO: Google Drive Integration

**Doc ID**: GROKAPI-IN31
**Goal**: Google Drive file access, OAuth, supported formats
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Google Drive integration enables Grok to access files stored in Google Drive for analysis. This is a **UNIQUE Grok feature** - no other major API provider offers native Google Drive integration. Files from Drive can be used with chat and tool features without manual download/upload. Requires OAuth authorization for Drive access. [VERIFIED] (GROKAPI-SC-XAI-GDRIVE | https://docs.x.ai/developers/google-drive)

## Key Facts

- [VERIFIED] Native Google Drive integration (GROKAPI-SC-XAI-GDRIVE)
- [VERIFIED] Requires OAuth for Drive access (GROKAPI-SC-XAI-GDRIVE)
- [VERIFIED] UNIQUE: No equivalent in OpenAI, Anthropic, or Gemini APIs (GROKAPI-SC-XAI-GDRIVE)

## Differences from Other APIs

- **vs OpenAI**: No native Google Drive integration
- **vs Anthropic**: No native Google Drive integration
- **vs Gemini**: Gemini integrates with Google Workspace but through different mechanism

## Sources

- GROKAPI-SC-XAI-GDRIVE | https://docs.x.ai/developers/google-drive | Accessed: 2026-03-20

## Document History

**[2026-03-20 06:00]**
- Initial document created
