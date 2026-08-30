# Python SDK Test Scripts

Verify ALL Python code examples from the Anthropic API INFO documentation against live API.

**SDK version**: `anthropic` 0.120.0
**Last run**: 2026-07-27
**Result**: 63 passed, 0 failed, 9 skipped (72 total across 14 files, ~164s)

## File Structure

```
_lib.py                        # Shared: client init, test harness, API key loading
01_client_errors_test.py       # IN06, IN07: Client setup, errors, auth
02_messages_test.py            # IN08: Messages API (basic, system, multi-turn)
03_streaming_test.py           # IN09: Streaming (text_stream, events, thinking)
04_token_counting_test.py      # IN10, IN14: count_tokens, cost estimation
05_stop_reasons_test.py        # IN11: All stop reasons + match/case pattern
06_thinking_test.py            # IN15, IN51: Extended thinking, adaptive, effort
07_structured_outputs_test.py  # IN16: JSON schema, Pydantic parse, strict tools
08_prompt_caching_test.py      # IN20, IN42: Auto/explicit cache, TTL, diagnostics
09_tool_use_test.py            # IN23, IN29: Tools, agentic loop, streaming tools
10_web_tools_test.py           # IN24: Server-side web search
11_context_features_test.py    # IN21, IN48: Context management, mid-conversation
12_platform_compat_test.py     # IN38: Bedrock/Vertex class existence
13_admin_apis_test.py          # IN32-35: Admin endpoints (requires ANTHROPIC_ADMIN_KEY)
14_beta_features_test.py       # IN12,IN25,IN26,IN30,IN31,IN40,IN47,IN49: Beta stubs
run_all.py                     # Execute all 01-14, aggregate summary
sdk_test.py                    # Standalone: 22 model param combination tests
sdk_methods.py                 # SDK introspection (no API calls)
```

Each `NN_*_test.py` produces a matching `NN_*_results.json`.

## Reproducing Results

Prerequisites: Python 3.10+, `anthropic` and `httpx` packages.

```bash
pip install anthropic httpx pydantic

# API keys (project-local takes precedence over .tools):
#   E:\Dev\deep-research-agent\.api-keys.txt -> ANTHROPIC_API_KEY
#   E:\Dev\.tools\.api-keys.txt             -> ANTHROPIC_ADMIN_KEY

# Run ALL tests (~3min, ~$0.30)
python docs/Anthropic/Anthropic_API_2026-07-27/python/run_all.py

# Run a single topic
python docs/Anthropic/Anthropic_API_2026-07-27/python/07_structured_outputs_test.py

# Run SDK introspection (no API calls, instant)
python docs/Anthropic/Anthropic_API_2026-07-27/python/sdk_methods.py
```

## Backwards Compatibility Testing

When a new SDK version ships:

```bash
pip install anthropic==0.121.0
python run_all.py
# Compare: diff 06_thinking_results.json 06_thinking_results_v0.120.0.json
```

Each results JSON captures per-test: status, latency, response details. Diffs reveal behavioral changes.

## Skipped Tests (9)

Require beta access or special environments (file 14):
- IN12 (Batches), IN25 (Code Execution), IN26 (Computer Use)
- IN30 (Files API), IN31 (Skills API), IN40 (Managed Agents)
- IN47 (Refusals), IN49 (Memory Stores)

## Documentation Bugs Found

### IN16: Structured Outputs - 3 issues

1. **`output_config.format` schema nesting wrong**: Docs show `{"type": "json_schema", "json_schema": {"name": "...", "schema": {...}}}` but API expects `{"type": "json_schema", "schema": {<JSON schema directly>}}`.
2. **`additionalProperties: false` required**: Docs omit this but API requires it for strict/json_schema modes.
3. **`client.messages.parse()` attribute**: Docs say `.parsed` but SDK 0.120.0 uses `.parsed_output`.

### IN32-33: Admin API endpoint paths

- Docs show `/v1/users` but actual path is `/v1/organizations/users`
- Docs show `/v1/api_keys` but actual path is `/v1/organizations/api_keys`

## Related Documents

- `_INFO_ANTAPI-50_SDK_Model_Methods.md` - Findings from `sdk_test.py`
- `_INFO_ANTAPI-51_Effort_Adaptive_Params.md` - Effort/adaptive parameter analysis
