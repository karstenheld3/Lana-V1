# Eval Run Report: All

**Run**: `2026-08-30_22-15-53_Lana-1.1.0_claude-sonnet-4-6_medium`
**Agent**: Lana-1.1.0
**Executed**: 2026-08-30 22:26

**Result**: 9 passed, 0 failed, 0 invalid, 0 error

## Tests

- **01-T01_CreateFile**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **01-T02_EditSequence**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **01-T03_SearchAndRefactor**: PASS (Tier 1: 0.90 | Tier 2: 1.00)
  - FAILED: `test_billing.py:forbid:calc_total`
- **01-T04_ShellExecution**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **02-T01_WriteSpec**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **02-T02_VerifyFix**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **02-T03_CritiqueSequence**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **03-T01_TranscribeLocal**: PASS (Tier 1: 1.00 | Tier 2: 1.00 | Tier 3: 1.00)
- **03-T02_DeepResearch**: PASS (Tier 1: 1.00 | Tier 2: 1.00 | Tier 3: 0.89)
  - NOTE: golden reference pending (DC-03 warning)

## Cost Summary

**Lana (agent under test)**: $1.1263
**Judge (Tier 3 eval)**: $0.0022
**Total**: $1.1285

- **01-T01_CreateFile**: Lana $0.0264 (13712in/225out) | Judge $0.0000 (n/a)
- **01-T02_EditSequence**: Lana $0.0235 (28263in/482out) | Judge $0.0000 (n/a)
- **01-T03_SearchAndRefactor**: Lana $0.0460 (48141in/1306out) | Judge $0.0000 (n/a)
- **01-T04_ShellExecution**: Lana $0.0200 (20863in/440out) | Judge $0.0000 (n/a)
- **02-T01_WriteSpec**: Lana $0.2999 (182991in/5611out) | Judge $0.0000 (n/a)
- **02-T02_VerifyFix**: Lana $0.0773 (93809in/1144out) | Judge $0.0000 (n/a)
- **02-T03_CritiqueSequence**: Lana $0.3598 (391969in/9642out) | Judge $0.0000 (n/a)
- **03-T01_TranscribeLocal**: Lana $0.0732 (56873in/1046out) | Judge $0.0005 (1149in/194out)
- **03-T02_DeepResearch**: Lana $0.2002 (191238in/5394out) | Judge $0.0017 (3819in/781out)

## Golden Benchmark Comparison

Golden files are Cascade + IPPS reference anchors - similarity is informational, not a pass/fail gate.

- **01-T01_CreateFile**: 0/1 files match golden, avg similarity 0.98
  - `hello.py`: DIFFERS (similarity 0.98)
- **01-T02_EditSequence**: 0/1 files match golden, avg similarity 0.84
  - `notes.md`: DIFFERS (similarity 0.84)
- **01-T03_SearchAndRefactor**: 2/3 files match golden, avg similarity 0.99
  - `billing.py`: MATCH
  - `invoice.py`: MATCH
  - `test_billing.py`: DIFFERS (similarity 0.96)
- **01-T04_ShellExecution**: 0/1 files match golden, avg similarity 0.67
  - `count.txt`: DIFFERS (similarity 0.67)
- **02-T01_WriteSpec**: 0/1 files match golden, avg similarity 0.07
  - `_SPEC_WORDCOUNT.md`: DIFFERS (similarity 0.07)
- **02-T02_VerifyFix**: 0/2 files match golden, avg similarity 0.67
  - `FIXLOG.md`: DIFFERS (similarity 0.38)
  - `STATUS.md`: DIFFERS (similarity 0.96)
- **02-T03_CritiqueSequence**: 0/2 files match golden, avg similarity 0.26
  - `_REVIEW_GREETER.md`: DIFFERS (similarity 0.02)
  - `_SPEC_GREETER.md`: DIFFERS (similarity 0.51)
- **03-T01_TranscribeLocal**: 0/1 files match golden, avg similarity 0.00
  - `pricing_page.md`: MISSING
- **03-T02_DeepResearch**: no golden reference (pending)
