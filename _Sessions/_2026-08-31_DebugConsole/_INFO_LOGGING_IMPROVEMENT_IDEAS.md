# INFO: Debug Console Logging - Performance Analysis and Improvement Ideas

**Doc ID**: LANADEBG-IN01
**Goal**: Assess the performance of the current debug console write path and develop ideas for offloading work asynchronously to the viewer process.
**Timeline**: Created 2026-08-31, Updated 0 times
**Target file(s)**:
- `src/lana/debuglog.py`
- `src/lana/debug_viewer.py`

**Depends on:**
- `_SPEC_LANADEBG.md [LANADEBG-SP01]` for the current design (DD-01 pipe transport, NFR-01 write cost)

## Summary

- Current synchronous `dlog()` costs **13.6 us per line** on the main thread - negligible CPU at Lana's volumes (hundreds of lines per turn = ~1-3 ms) [TESTED]
- **Blocking hazard is the real problem, not CPU**: the Windows pipe buffer holds only ~4 KB (~23 debug lines); a viewer that stops draining stdin blocks `dlog()` and **freezes Lana entirely** [TESTED]
- A likely stall trigger exists in normal use: clicking into the viewer window puts the console into select mode, which suspends the viewer's output and therefore its stdin reading [ASSUMED]
- Bounded queue + writer thread (Idea 3.1, the existing `StdoutWriter` pattern from `jsonrpc.py`) cuts main-thread cost to **1.1 us** and makes a stalled viewer harmless (drop + count instead of block) [TESTED]
- Raw epoch timestamp (`time.time()` = 0.04 us) instead of strftime (3.5 us) moves timestamp formatting to the viewer - 80x cheaper capture [TESTED]
- JSON serialization (3.0 us) can also move to the writer thread - the main thread hands over a plain dict [TESTED]
- Viewer-side analytics (session totals, per-tool latency stats, cache-expiry detection) add analysis power at **zero** main-process cost - the viewer already receives all facts [VERIFIED]
- Not recommended: raw start/end markers with viewer-derived durations (breaks per-line self-containment for ~0.05 us), UDP transport (adds loss without need), shared-memory ring (over-engineering) [VERIFIED]

## Table of Contents

1. [Current Implementation Costs](#1-current-implementation-costs)
2. [The Pipe-Block Hazard](#2-the-pipe-block-hazard)
3. [Improvement Ideas](#3-improvement-ideas)
4. [Rejected Ideas](#4-rejected-ideas)
5. [Recommended Combination](#5-recommended-combination)

Unnumbered: [Sources](#sources) | [Next Steps](#next-steps) | [Document History](#document-history)

## 1. Current Implementation Costs

Measured on this machine (Python 3.12, 20000 iterations, typical `llm response` record of ~170 bytes):

- **strftime timestamp**: 3.48 us - `datetime.now().strftime(...)` per line
- **json.dumps**: 3.04 us - serialization of the record dict
- **text pipe write + flush**: ~7 us - TextIOWrapper encode + two calls (write, flush)
- **Total current `dlog()`**: **13.64 us** per line, all on the caller's thread

**Volume context:** a busy turn produces low hundreds of lines. 200 lines x 13.6 us = **2.7 ms per turn** - invisible next to multi-second LLM calls. Pure CPU cost is NOT a problem today.

**Comparison variants measured:**
- Binary unbuffered pipe (`bufsize=0`, pre-encoded bytes, raw float ts): 7.46 us - halves the cost, still synchronous
- `queue.put_nowait` hand-off (writer thread does json + write + flush): **1.07 us** main-thread cost - 12x cheaper, and decouples the caller from the pipe

## 2. The Pipe-Block Hazard

The measurement that matters most:

```
Child process that never reads stdin:
  lines until write BLOCKED: 23 (172 bytes each, ~3 KB pipe buffer)
```

`dlog()` writes synchronously to the viewer's stdin. The Windows anonymous pipe buffers only ~4 KB. If the viewer stops reading, the 24th line **blocks the main thread indefinitely** - in ACP mode that freezes the agent mid-turn with no error and no timeout.

**When does a viewer stop reading?**
- Console select mode: user clicks/drags in the viewer window - Windows suspends console output; the viewer blocks in `console.print` and stops reading stdin [ASSUMED - select-mode suspension is documented Windows console behavior; the block-on-full-pipe chain itself is TESTED above]
- Viewer busy rendering a burst while the window is being resized/moved
- Viewer process suspended by the OS or a debugger

The current design survives viewer **death** (EC-01: write fails, logging disables). It does NOT survive viewer **stall** - the write never fails, it just never returns. This is the exact hazard `StdoutWriter` in `jsonrpc.py` was built to remove for ACP stdout ("a client that stops draining stdout cannot freeze the event loop").

## 3. Improvement Ideas

### 3.1 Bounded queue + writer thread (StdoutWriter pattern)

Main thread: `queue.put_nowait(record_dict)` - 1.07 us, never blocks. Dedicated writer thread: dequeue, serialize, write + flush per line. On queue full: drop the line, count drops, emit one meta line when draining resumes.

- **Fixes**: the pipe-block hazard (stalled viewer costs dropped lines, never a frozen agent)
- **Preserves**: immediate flush per line (on the writer thread; visibility delay is microseconds), strict ordering (single queue)
- **Trade**: on hard crash of the main process, up to queue-depth lines are lost before write; mitigate with small depth (~1000) and an atexit drain with timeout
- **Precedent**: `StdoutWriter` (`jsonrpc.py`) - same pattern, proven in this codebase
- **Note**: this revisits rejected Option C - the rejection predated the discovery of the 23-line block hazard; the writer thread now earns its complexity

### 3.2 Raw epoch timestamp, viewer formats

Send `t: time.time()` (0.04 us) instead of a strftime string (3.48 us). The viewer formats `HH:MM:SS.mmm` for display; the full date stays derivable for correlation (LOG-AP-01 intent preserved - epoch is even easier to parse for machines).

- **Saves**: 3.4 us per line on the capture side, 80x cheaper
- **Offloads**: all timestamp formatting to the viewer process (separate core)

### 3.3 Serialize in the writer thread

With Idea 3.1 in place, `json.dumps` (3.0 us) moves off the main thread for free - the queue carries dict references. Caller cost becomes: dict literal + put_nowait = ~1 us total.

- **Caution**: the dict must not be mutated after enqueue - all current call sites build fresh literals, so this holds by construction

### 3.4 Binary unbuffered pipe in the writer thread

Spawn the viewer with `bufsize=0` (binary), writer thread writes pre-encoded UTF-8 bytes - one syscall per line, no TextIOWrapper, no separate flush call (7.46 us measured synchronously; irrelevant on the writer thread but reduces writer-thread lag under bursts).

### 3.5 Viewer-side analytics (pass facts, let the viewer analyze)

The viewer already receives every fact. It can maintain derived state at zero main-process cost:

- **Session totals**: running cost, tokens, turn count - rendered in the window title or a footer line
- **Cache-expiry detection**: `cache_read` dropping to ~0 after a prior high value → print a highlighted `cache expired (idle > TTL?)` line - directly answers the session goal "when do caches expire"
- **Per-tool latency stats**: count, mean, max per tool name - dumped on demand (keypress) or at EOF
- **TTFT trend**: flag first_token outliers (e.g. > 2x running median) in yellow
- **Turn digest**: after each `acp turn` / `llm response` without tool calls, one summary line: turn duration, tool time vs model time split

This is the direct answer to "pass pure data objects and let the subprocess do all the analysis": the data already flows; analysis belongs in the viewer, and adding it later never touches the instrumented hot path.

## 4. Rejected Ideas

### 4.1 Raw start/end markers, viewer derives durations

Send only monotonic timestamps at operation boundaries; the viewer pairs them and computes `dur_ms`. Rejected: the subtraction being moved costs ~0.05 us (nothing), while each wire line stops being self-contained - grep-ability and the single-source-of-truth goal suffer, and pairing state in the viewer adds failure modes. Pre-computed `dur_ms` stays (SPEC IG-03, NFR-01 pre-computation contract).

### 4.2 UDP datagrams to localhost

Never blocks by nature, but introduces silent loss under burst, socket/port lifecycle, and no benefit over Idea 3.1 (which makes loss explicit via a drop counter). Rejected.

### 4.3 multiprocessing.Connection (pickle) transport

Passing Python objects directly saves nothing measurable (pickle ~ json at these sizes), couples viewer to pickle versioning/security, and kills the text-protocol debuggability (EC-06 raw rendering, manual `--debug-viewer` piping). Rejected.

### 4.4 Shared-memory ring buffer

~0.1 us writes, maximal complexity (synchronization protocol, corruption handling, platform specifics). At hundreds of lines per turn the queue hand-off is already 1 us. Over-engineering (SOCAS-11). Rejected.

## 5. Recommended Combination

Ideas 3.1 + 3.2 + 3.3 + 3.4 as one change to `debuglog.py` (viewer adjusts ts handling):

```
Main thread                     Writer thread                   Viewer process
dlog(dom, op, **fields)
  dict literal (~0.3 us)
  t = time.time() (0.04 us)
  put_nowait (~0.7 us)   ──>    get()
  return (total ~1 us)          json.dumps (3 us)
                                bytes + write (4 us)     ──>    parse, format ts,
                                queue full? drop + count        format durations,
                                                                render, analytics (ID-05)
```

- Main-thread cost: 13.6 us → ~1 us per line (NFR-01 strengthened)
- Stalled viewer: frozen agent → dropped lines with a visible drop count (NFR-02 strengthened)
- Immediate flush: preserved per line on the writer thread
- Idea 3.5 analytics: independent follow-up, viewer-only change, zero hot-path impact

**Effort**: Ideas 3.1-3.4 = one focused change in `debuglog.py` + ts handling in `debug_viewer.py` + spec sync (DD/NFR updates) + tests (queue drop, ordering, crash-drain). Idea 3.5 = viewer-only, incremental per analytic.

## Sources

- `LANADEBG-IN01-SC-BENCH-DLOG`: local micro-benchmark (Python 3.12, this machine, 20000 iterations per variant; method: `timeit` over component calls and full write paths against a draining child process; block test against a non-reading child) - all numbers in sections 1-2 [TESTED]
- `LANADEBG-IN01-SC-CODE-JSONRPC`: `src/lana/acp/jsonrpc.py` `StdoutWriter` - proven bounded-queue writer-thread precedent with drop-on-overflow [VERIFIED]
- `LANADEBG-IN01-SC-CODE-DEBUGLOG`: `src/lana/debuglog.py` - current synchronous write path under analysis [VERIFIED]

## Next Steps

1. Decide: adopt Ideas 3.1-3.4 (queue + writer thread + raw ts + binary pipe) - requires SPEC update (DD-01 amendment, NFR-01/02, new EC for drop-on-overflow)
2. If adopted: implement in `debuglog.py`/`debug_viewer.py`, extend `tests/test_debuglog.py` (ordering, overflow drop + counter, atexit drain)
3. Idea 3.5 analytics: pick the first analytic (recommendation: cache-expiry detection - a direct session goal) and add it viewer-side
4. Re-run the NFR-01 timing comparison after the change to confirm no regression

## Document History

**[2026-08-31 14:25]**
- Initial research document created: benchmark results, pipe-block hazard proof, 9 ideas (5 proposed, 4 rejected), recommended combination
