# JavaScript SDK Test Scripts

Verified TypeScript/Node.js SDK examples and results from live API testing on 2026-07-27.

**SDK version**: `@anthropic-ai/sdk` 0.115.0

## Files

- `sdk_examples_test.cjs` - 14 tests covering IN05/IN06/IN07/IN13/IN21 documentation examples
- `sdk_examples_results.json` - Results from the examples test run
- `sdk_test.cjs` - 22 tests covering model parameter combinations (thinking/effort/adaptive)
- `sdk_test_results.json` - Results from the model parameter test run
- `sdk_methods.json` - SDK method introspection (all client methods with their parameters)

## Reproducing Results

Prerequisites: Node.js 18+, `@anthropic-ai/sdk` installed in project root.

```bash
# From project root (E:\Dev\deep-research-agent)
npm install @anthropic-ai/sdk

# Ensure .api-keys.txt contains ANTHROPIC_API_KEY=sk-ant-...

# Run examples test (14 tests, ~30s, costs ~$0.05)
node docs/Anthropic/Anthropic_API_2026-07-27/javascript/sdk_examples_test.cjs

# Run model parameter test (22 tests, ~60s, costs ~$0.15)
node docs/Anthropic/Anthropic_API_2026-07-27/javascript/sdk_test.cjs
```

Results are written to JSON files in the same directory as the test script.

## Related Documents

- `_INFO_ANTAPI-50_SDK_Model_Methods.md` - Findings from `sdk_test.cjs`
- `_INFO_ANTAPI-51_Effort_Adaptive_Params.md` - Effort/adaptive parameter analysis
