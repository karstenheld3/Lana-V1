# PROBLEMS: LANAAGNT-BG-0001 ApprovalEventNotYielded

**Doc ID**: LANAAGNT-BG-0001
**Goal**: Track and fix the approval_required event never reaching frontends

### LANAAGNT-BG-0001 approval_required persisted but not yielded to the event stream

**Status**: Resolved
**Reported**: 2026-08-30 01:35
**Resolved**: 2026-08-30 01:40

**Verbatim failure**:
````
tests\test_agent.py:113: assert any(event.type == "approval_required" and event.approved is False for event in events)
E     assert False
````

**Initial assessment**: `Agent.execute_tool_call()` calls `self.emit(ApprovalRequired(...))` which appends to the session JSONL but cannot yield - it is a plain method, not the generator. Frontends (renderer, headless jsonl output, TC-52 harness assertions) never see the event, violating DD-06 (the AgentEvent stream is the single frontend contract) and FR-12 (approval visibility).

**Root cause**: Event emission placed inside a non-generator helper during IS-13 implementation; only the session sink received the event.

**Impact assessment**:
- `Agent.run_prompt` tool-call loop (only caller of `execute_tool_call`)
- Renderer approval line, headless `--output-format jsonl` stream, TP01 TC-52 harness assertion
- Session JSONL unaffected (event was already persisted correctly)

**Solution**: Split `execute_tool_call` into `resolve_approval()` (returns the ApprovalRequired event + applies denial to the call) and `dispatch_call()` (pure execution). `run_prompt` now yields the approval event through the generator before dispatch. Regression test: `test_denylisted_command_denied_without_callback` asserts the event appears on the stream.

**Changed files**:
- `src/lana/agent.py` - approval resolution moved into the generator path
- `tests/test_agent.py` - regression assertion (was the detecting test)
