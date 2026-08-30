# INFO: Provisioned Throughput

**Doc ID**: GROKAPI-IN40
**Goal**: Guaranteed capacity, pricing, unit calculation, optional headers, FAQs
**Version scope**: API v1, Documentation date 2026-03-20

**Depends on:**
- `__GROKAPI_SOURCES.md [GROKAPI-SOURCES]` for source references

## Summary

Provisioned Throughput is an enterprise feature providing guaranteed API capacity with predictable performance. Instead of shared rate limits, teams purchase dedicated throughput units for specific models. Key benefits: guaranteed capacity regardless of system load, predictable latency, custom rate limits. Pricing is based on throughput units calculated from expected token volume. Uses optional headers to route requests through provisioned capacity. Includes FAQ on exceeding capacity (requests queue or fallback to shared), adjusting allocation (contact support), and minimum commitment. [VERIFIED] (GROKAPI-SC-XAI-PROVTHRU | https://docs.x.ai/developers/provisioned-throughput)

## Key Facts

- [VERIFIED] Guaranteed capacity regardless of system load (GROKAPI-SC-XAI-PROVTHRU)
- [VERIFIED] Throughput units calculated from expected token volume (GROKAPI-SC-XAI-PROVTHRU)
- [VERIFIED] Optional headers for routing to provisioned capacity (GROKAPI-SC-XAI-PROVTHRU)
- [VERIFIED] Enterprise feature with minimum commitment (GROKAPI-SC-XAI-PROVTHRU)

## Quick Reference

- **Type**: Enterprise feature
- **Pricing**: Per throughput unit (contact sales)
- **Benefit**: Guaranteed capacity, predictable latency
- **Routing**: Optional headers on API requests

## Differences from Other APIs

### vs OpenAI
- **Similar**: OpenAI has Reserved Capacity / Provisioned Throughput
- **Same concept**: Dedicated capacity for enterprise customers

### vs Anthropic
- **Similar**: Anthropic offers custom rate limits for enterprise
- **Less formalized**: No dedicated "Provisioned Throughput" product

### vs Gemini
- **Similar**: Google Cloud offers reserved capacity for Vertex AI

## Sources

- GROKAPI-SC-XAI-PROVTHRU | https://docs.x.ai/developers/provisioned-throughput | Accessed: 2026-03-20

## Document History

**[2026-03-20 05:55]**
- Initial document created with Provisioned Throughput reference
