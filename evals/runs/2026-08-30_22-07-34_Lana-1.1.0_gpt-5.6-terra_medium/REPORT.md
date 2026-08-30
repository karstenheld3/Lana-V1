# Eval Run Report: All

**Run**: `2026-08-30_22-07-34_Lana-1.1.0_gpt-5.6-terra_medium`
**Agent**: Lana-1.1.0
**Executed**: 2026-08-30 22:14

**Result**: 7 passed, 2 failed, 0 invalid, 0 error

## Tests

- **01-T01_CreateFile**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **01-T02_EditSequence**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **01-T03_SearchAndRefactor**: PASS (Tier 1: 0.90 | Tier 2: 1.00)
  - FAILED: `test_billing.py:forbid:calc_total`
- **01-T04_ShellExecution**: FAIL (Tier 1: 1.00 | Tier 2: 0.50)
  - FAILED: `result_written_via_edit_tool`
- **02-T01_WriteSpec**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **02-T02_VerifyFix**: PASS (Tier 1: 0.92 | Tier 2: 1.00)
  - FAILED: `STATUS.md:pattern:next_step_kept`
- **02-T03_CritiqueSequence**: PASS (Tier 1: 1.00 | Tier 2: 1.00)
- **03-T01_TranscribeLocal**: PASS (Tier 1: 1.00 | Tier 2: 1.00 | Tier 3: 1.00)
- **03-T02_DeepResearch**: FAIL (Tier 1: 0.00 | Tier 2: 0.50 | Tier 3: 0.25)
  - FAILED: `required:_INFO_BERLINWALL.md`
  - FAILED: `file_rules:_INFO_BERLINWALL.md`
  - FAILED: `info_written_via_edit_tool`
  - NOTE: golden reference pending (DC-03 warning)
  - NOTE: lana exit code 4 (EC-01/EC-02)

## Cost Summary

**Lana (agent under test)**: $0.9495
**Judge (Tier 3 eval)**: $0.0011
**Total**: $0.9505

- **01-T01_CreateFile**: Lana $0.0154 (14069in/312out) | Judge $0.0000 (n/a)
- **01-T02_EditSequence**: Lana $0.0226 (29571in/583out) | Judge $0.0000 (n/a)
- **01-T03_SearchAndRefactor**: Lana $0.0371 (28914in/1513out) | Judge $0.0000 (n/a)
- **01-T04_ShellExecution**: Lana $0.0141 (9302in/298out) | Judge $0.0000 (n/a)
- **02-T01_WriteSpec**: Lana $0.1785 (216415in/5844out) | Judge $0.0000 (n/a)
- **02-T02_VerifyFix**: Lana $0.2211 (445527in/3681out) | Judge $0.0000 (n/a)
- **02-T03_CritiqueSequence**: Lana $0.3340 (688735in/8867out) | Judge $0.0000 (n/a)
- **03-T01_TranscribeLocal**: Lana $0.0464 (57682in/1034out) | Judge $0.0005 (1149in/194out)
- **03-T02_DeepResearch**: Lana $0.0802 (94483in/2271out) | Judge $0.0006 (936in/347out)

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
- **02-T01_WriteSpec**: 0/1 files match golden, avg similarity 0.13
  - `_SPEC_WORDCOUNT.md`: DIFFERS (similarity 0.13)
- **02-T02_VerifyFix**: 0/2 files match golden, avg similarity 0.20
  - `FIXLOG.md`: DIFFERS (similarity 0.09)
  - `STATUS.md`: DIFFERS (similarity 0.31)
- **02-T03_CritiqueSequence**: 0/2 files match golden, avg similarity 0.25
  - `_REVIEW_GREETER.md`: DIFFERS (similarity 0.02)
  - `_SPEC_GREETER.md`: DIFFERS (similarity 0.47)
- **03-T01_TranscribeLocal**: 0/1 files match golden, avg similarity 0.00
  - `pricing_page.md`: MISSING
- **03-T02_DeepResearch**: no golden reference (pending)
