# Eval Run Report: All

**Run**: `2026-08-30_21-59-17_Lana-1.1.0_claude-sonnet-4-6_medium`
**Agent**: Lana-1.1.0
**Executed**: 2026-08-30 21:59

**Result**: 0 passed, 9 failed, 0 invalid, 0 error

## Tests

- **01-T01_CreateFile**: FAIL (Tier 1: 0.00 | Tier 2: 0.50)
  - FAILED: `required:hello.py`
  - FAILED: `file_rules:hello.py`
  - FAILED: `file_created_via_edit_tool`
  - NOTE: lana exit code 2 (EC-01/EC-02)
- **01-T02_EditSequence**: FAIL (Tier 1: 0.00 | Tier 2: 0.50)
  - FAILED: `required:notes.md`
  - FAILED: `file_rules:notes.md`
  - FAILED: `file_created_via_edit_tool`
  - NOTE: lana exit code 2 (EC-01/EC-02)
- **01-T03_SearchAndRefactor**: FAIL (Tier 1: 0.40 | Tier 2: 0.33)
  - FAILED: `billing.py:pattern:new_name_defined`
  - FAILED: `billing.py:forbid:calc_total`
  - FAILED: `invoice.py:pattern:new_name_imported`
  - FAILED: `invoice.py:forbid:calc_total`
  - FAILED: `test_billing.py:pattern:new_name_used`
  - FAILED: `test_billing.py:forbid:calc_total`
  - FAILED: `search_performed`
  - FAILED: `edits_performed`
  - NOTE: lana exit code 2 (EC-01/EC-02)
- **01-T04_ShellExecution**: FAIL (Tier 1: 0.00 | Tier 2: 0.00)
  - FAILED: `required:count.txt`
  - FAILED: `file_rules:count.txt`
  - FAILED: `shell_command_executed`
  - FAILED: `result_written_via_edit_tool`
  - NOTE: lana exit code 2 (EC-01/EC-02)
- **02-T01_WriteSpec**: FAIL (Tier 1: 0.00 | Tier 2: 0.33)
  - FAILED: `required:_SPEC_WORDCOUNT.md`
  - FAILED: `file_rules:_SPEC_WORDCOUNT.md`
  - FAILED: `spec_template_read`
  - FAILED: `spec_written_via_edit_tool`
  - NOTE: lana exit code 2 (EC-01/EC-02)
- **02-T02_VerifyFix**: FAIL (Tier 1: 0.33 | Tier 2: 0.25)
  - FAILED: `required:FIXLOG.md`
  - FAILED: `STATUS.md:pattern:iso_date`
  - FAILED: `STATUS.md:forbid:✅`
  - FAILED: `STATUS.md:forbid:❌`
  - FAILED: `STATUS.md:forbid:|--`
  - FAILED: `STATUS.md:forbid:03/15/2026`
  - FAILED: `STATUS.md:forbid:---`
  - FAILED: `file_rules:FIXLOG.md`
  - FAILED: `status_read_first`
  - FAILED: `fixes_via_edit_tools`
  - FAILED: `fixlog_written`
  - NOTE: lana exit code 2 (EC-01/EC-02)
- **02-T03_CritiqueSequence**: FAIL (Tier 1: 0.33 | Tier 2: 0.25)
  - FAILED: `required:_REVIEW_GREETER.md`
  - FAILED: `file_rules:_REVIEW_GREETER.md`
  - FAILED: `_SPEC_GREETER.md:forbid:handles errors appropriately`
  - FAILED: `_SPEC_GREETER.md:forbid:The three supported languages`
  - FAILED: `spec_read_before_critique`
  - FAILED: `review_written`
  - FAILED: `spec_fixed_via_edit`
  - NOTE: lana exit code 2 (EC-01/EC-02)
- **03-T01_TranscribeLocal**: FAIL (Tier 1: 0.00 | Tier 2: 0.00 | Tier 3: 0.33)
  - FAILED: `required:output/pricing_page.md`
  - FAILED: `file_rules:output/pricing_page.md`
  - FAILED: `fixture_read`
  - FAILED: `output_written_via_edit_tool`
  - NOTE: lana exit code 2 (EC-01/EC-02)
- **03-T02_DeepResearch**: FAIL (Tier 1: 0.00 | Tier 2: 0.00 | Tier 3: 0.25)
  - FAILED: `required:_INFO_BERLINWALL.md`
  - FAILED: `file_rules:_INFO_BERLINWALL.md`
  - FAILED: `web_searches_executed`
  - FAILED: `sources_fetched`
  - FAILED: `info_written_via_edit_tool`
  - NOTE: golden reference pending (DC-03 warning)
  - NOTE: lana exit code 2 (EC-01/EC-02)

## Cost Summary

**Lana (agent under test)**: $0.0000
**Judge (Tier 3 eval)**: $0.0010
**Total**: $0.0010

- **01-T01_CreateFile**: Lana $0.0000 (n/a) | Judge $0.0000 (n/a)
- **01-T02_EditSequence**: Lana $0.0000 (n/a) | Judge $0.0000 (n/a)
- **01-T03_SearchAndRefactor**: Lana $0.0000 (n/a) | Judge $0.0000 (n/a)
- **01-T04_ShellExecution**: Lana $0.0000 (n/a) | Judge $0.0000 (n/a)
- **02-T01_WriteSpec**: Lana $0.0000 (n/a) | Judge $0.0000 (n/a)
- **02-T02_VerifyFix**: Lana $0.0000 (n/a) | Judge $0.0000 (n/a)
- **02-T03_CritiqueSequence**: Lana $0.0000 (n/a) | Judge $0.0000 (n/a)
- **03-T01_TranscribeLocal**: Lana $0.0000 (n/a) | Judge $0.0005 (994in/270out)
- **03-T02_DeepResearch**: Lana $0.0000 (n/a) | Judge $0.0005 (936in/248out)

## Golden Benchmark Comparison

Golden files are Cascade + IPPS reference anchors - similarity is informational, not a pass/fail gate.

- **01-T01_CreateFile**: 0/1 files match golden, avg similarity 0.00
  - `hello.py`: MISSING
- **01-T02_EditSequence**: 0/1 files match golden, avg similarity 0.00
  - `notes.md`: MISSING
- **01-T03_SearchAndRefactor**: 0/3 files match golden, avg similarity 0.87
  - `billing.py`: DIFFERS (similarity 0.96)
  - `invoice.py`: DIFFERS (similarity 0.78)
  - `test_billing.py`: DIFFERS (similarity 0.86)
- **01-T04_ShellExecution**: 0/1 files match golden, avg similarity 0.00
  - `count.txt`: MISSING
- **02-T01_WriteSpec**: 0/1 files match golden, avg similarity 0.00
  - `_SPEC_WORDCOUNT.md`: MISSING
- **02-T02_VerifyFix**: 0/2 files match golden, avg similarity 0.34
  - `FIXLOG.md`: MISSING
  - `STATUS.md`: DIFFERS (similarity 0.68)
- **02-T03_CritiqueSequence**: 0/2 files match golden, avg similarity 0.40
  - `_REVIEW_GREETER.md`: MISSING
  - `_SPEC_GREETER.md`: DIFFERS (similarity 0.80)
- **03-T01_TranscribeLocal**: 0/1 files match golden, avg similarity 0.00
  - `pricing_page.md`: MISSING
- **03-T02_DeepResearch**: no golden reference (pending)
