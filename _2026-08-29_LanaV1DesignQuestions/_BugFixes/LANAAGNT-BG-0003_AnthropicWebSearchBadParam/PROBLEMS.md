# PROBLEMS: LANAAGNT-BG-0003 AnthropicWebSearchBadParam

**Doc ID**: LANAAGNT-BG-0003
**Goal**: Track and fix the invalid allowed_domains parameter on the Anthropic web_search tool

### LANAAGNT-BG-0003 allowed_domains passed to web_search_20250305 (web_fetch-only parameter)

**Status**: Resolved
**Reported**: 2026-08-30 02:40 (found by /drift-correct doc verification, gap 21/29)
**Resolved**: 2026-08-30 02:45

**Verbatim evidence**:
````
ANTAPI-IN24 Web Search Parameters: type, name, max_uses, cache_control, hidden, citations_config
ANTAPI-IN24 Web Fetch Parameters: ... allowed_domains (array[string], optional) ...
anthropic_adapter.py: if domain: tool["allowed_domains"] = [domain]   # <- web_search tool dict
````

**Initial assessment**: `AnthropicAdapter.run_web_search` was written from training memory without reading IN24 (drift item 21, FL-0002 recurrence). `allowed_domains` belongs to the web_fetch tool family only; on web_search the request would be rejected or the parameter silently ignored. The branch has zero test coverage (drift item 27), so nothing caught it.

**Root cause**: STRUT step P8-S1 (read IN14/IN24 before implementing) skipped during `/go` execution.

**Impact assessment**:
- `AnthropicAdapter.run_web_search` only (OpenAI path verified correct against IN14; TC-43 live-passed)
- `search_web` tool executor unaffected (adapter-internal)
- No callers rely on the domain parameter reaching the API - it is optional in the tool schema

**Solution**: Drop `allowed_domains`; fold the domain restriction into the search prompt text (mirrors the OpenAI path). Live smoke added for the Anthropic websearch branch (drift item 27).

**Changed files**:
- `src/lana/providers/anthropic_adapter.py` - parameter removed, domain folded into prompt
- `tests/test_adapters.py` - live Anthropic websearch smoke added
