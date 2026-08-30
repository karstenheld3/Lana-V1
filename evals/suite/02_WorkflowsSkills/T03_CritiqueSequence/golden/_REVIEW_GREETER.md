# REVIEW: _SPEC_GREETER.md

**Doc ID**: GREETER-SP01-RV01
**Goal**: Devil's advocate review of the Greeter CLI specification.

## Findings

**GREETER-SP01-RV01-RF-01: Unverifiable error handling requirement**
- GREETER-FR-02 states "The tool handles errors appropriately" - no concrete behavior, not testable
- Decision: ACCEPTED - replace with concrete error cases (unknown language, missing name) and exit codes

**GREETER-SP01-RV01-RF-02: Language count contradiction**
- Scenario says "exactly two languages: English and German"; GREETER-FR-01 says "The three supported languages"
- Decision: ACCEPTED - align GREETER-FR-01 to the two languages defined in the Scenario

## Document History

**[2026-08-30 20:00]**
- Initial review created; reconcile decisions recorded (golden reference, produced by Cascade + IPPS)
