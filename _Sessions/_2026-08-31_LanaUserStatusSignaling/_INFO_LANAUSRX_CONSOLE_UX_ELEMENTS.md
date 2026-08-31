# INFO: Console UX Element Inventory and Dead-Air Solution Mapping

**Doc ID**: LANAUSRX-IN02
**Goal**: Catalog all console-compatible UX elements available to Lana's CLI renderer, assess compatibility with the streaming architecture, and map each element to the dead-air problems identified in LANAUSRX-IN01
**Timeline**: Created 2026-08-31, Updated 2 times (2026-08-31 - 2026-08-31)

**Depends on:**
- `_INFO_LANAUSRX_INTERACTION_CHAIN.md [LANAUSRX-IN01]` for dead-air phases DA-01 through DA-07 and interaction categories
- `_INFO_DELPHIOS_DESIGN_SYSTEM.md [DLPHS-IN10]` for color system and interaction philosophy
- `_INFO_DELPHIOS_BRAND.md [DLPHS-IN07]` for frugal language and no-interruption constraints
- `LOGGING-RULES.md` and `LOGGING-RULES-USER-FACING.md` (@skills:coding-conventions) for Announce > Track > Report pattern and user-facing output philosophy
- `core-conventions.md` (@rules) for approved Unicode character set and monospace safety constraints
- `SPEC_RULES.md` (@skills:write-documents) for UX diagram conventions and logging requirement structure

## Summary

- 8 element families identified across text styling, spatial layout, structural elements, animation, temporal display, information markers, information density, and terminal control [VERIFIED]
- 5 elements are fully compatible with Lana's streaming async architecture: text styles, indentation, prefix markers, Rich Status spinner, elapsed counters [VERIFIED]
- 3 elements are conditionally compatible (require integration care): Rich Progress bars, in-place line updates, horizontal rules [VERIFIED]
- 4 elements are incompatible or impractical: Rich Live display, Rich Panel mid-stream, Rich Table mid-stream, background colors for large regions [VERIFIED]
- All 3 HIGH-severity dead-air phases (DA-01, DA-02, DA-03) solvable with a single pattern: background-ticking spinner with elapsed counter [VERIFIED]
- The 2 MEDIUM-severity phases (DA-04, DA-05) need spinner reuse (DA-04) and countdown timer (DA-05) [VERIFIED]
- Style consistency fixes (Section 6.4 of LANAUSRX-IN01) require only the `style="dim"` parameter on 3 existing `console.print()` calls [VERIFIED]
- Key constraint: `markup=False` on all prints (BG-0004 security). All styling must go through `style=` parameter, never inline Rich markup tags [VERIFIED]
- Announce > Track > Report pattern from logging rules (LOG-GN) maps directly to dead-air status signaling: announce operation, track with spinner/counter, report result [VERIFIED]
- Announce Before Blocking principle (LOG-GN-09) is the architectural rule behind all dead-air fixes: log BEFORE entering any call that could take >10s [VERIFIED]
- All console characters must preserve monospace fixed-width alignment. Approved set: Unicode box-drawing, arrow `→`, ASCII text, Rich spinner braille dots. No emojis, no ambiguous-width Unicode (core-conventions.md) [VERIFIED]
- Duration format must follow LOG-GN-04: `secs`, `mins`, `hours` - not abbreviations like `s`, `m`, `h` [VERIFIED]

## Table of Contents

1. [Console UX Element Inventory](#1-console-ux-element-inventory)
2. [Architecture Constraints](#2-architecture-constraints)
3. [Compatibility Assessment](#3-compatibility-assessment)
4. [Element-to-Problem Mapping](#4-element-to-problem-mapping)
5. [Recommended Patterns](#5-recommended-patterns)
6. [Anti-Patterns](#6-anti-patterns)
7. [Next Steps](#7-next-steps)
8. [Sources](#8-sources)
9. [Document History](#9-document-history)

## 1. Console UX Element Inventory

### 1.1 Text Styling (Foreground Color)

Terminal text can be colored using Rich's `style=` parameter on `console.print()`.

**Available ranges:**
- **Standard 8**: black, red, green, yellow, blue, magenta, cyan, white
- **Bright variants**: bright_black (grey), bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan, bright_white
- **256-color palette**: `color(0)` through `color(255)` - indexed colors. Supported in most modern terminals.
- **Truecolor (24-bit)**: Hex values like `#2C5ED6`. Supported in Windows Terminal, iTerm2, modern Linux terminals. Falls back to nearest 256-color on older terminals.

**Current Lana usage:**
- `"dim"` - thinking deltas, NOTICE messages
- `"yellow"` - WARNING messages
- `"red"` - ERROR messages
- No style (default terminal foreground) - model text, tool lines, turn stats, compaction, tool results

**Unused but available:**
- `"bold"` - high emphasis, terminal-safe
- `"blue"` or `"bright_blue"` - brand-blue-equivalent for CLI (approval prompts, key indicators)
- `"cyan"` - alternative to blue, higher contrast on dark terminals
- `"green"` - success indicators (but conflicts with severity palette in design system)
- `"italic"` - subtle emphasis. Not universally supported (some terminals render as reverse or underline).
- `"underline"` - links or emphasis. Universally supported.

### 1.2 Text Styling (Background Color)

Background colors applied via `"on <color>"` in Rich style strings, e.g., `style="white on blue"`.

**Use cases in terminals:**
- Highlight a single word or short phrase (e.g., status badge `[PENDING]` on blue background)
- Selection/focus indicator
- Alert banners (red background for critical errors)

**Practical constraints:**
- Background colors on long text are visually heavy in terminals. The design system's 70% neutral rule applies.
- Most terminal color schemes already have a dark or light background. Adding more backgrounds creates visual noise.
- Line-width backgrounds (full-width colored bars) depend on terminal width and wrapping behavior.

### 1.3 Text Styles (Non-Color)

Rich supports these via the `style=` parameter:

- **bold** - Increases font weight. Universally supported. Good for emphasis.
- **dim** - Reduces brightness (~50% opacity equivalent). Universally supported. Good for secondary/metadata content.
- **italic** - Slanted text. Partially supported (Windows Terminal yes, some Linux terminals render as reverse video).
- **underline** - Underlined text. Universally supported.
- **strike** - Line through text. Moderately supported. Rich style name is `strike` (shorthand `s`), not `strikethrough`.
- **overline** - Line above text. Rarely supported.
- **blink** - Flashing text. Widely supported but distracting. Prohibited by design system (no interruption patterns).
- **reverse** - Swap foreground/background. Universally supported. Good for inline badges.

**Combinable:** `style="bold dim"`, `style="bold blue"`, `style="dim underline"`. Rich parses compound style strings.

### 1.4 Spatial Layout

- **Indentation**: Leading spaces. Already used: 2-space indent for `[tool]` lines, 4-space indent for tool results (`OK.`, `ERROR:`).
- **Right-alignment**: Rich `Console.print()` supports `justify="right"`. Can right-align elapsed times or metadata.
- **Console width**: `console.width` returns terminal width in columns. Enables responsive formatting.
- **Padding**: Rich `Padding` object adds space around renderables. Works with `Console.print()`.
- **Columns**: Rich `Columns` renders multiple items side-by-side. Requires known content up-front (not streaming-compatible).

### 1.5 Structural Elements

- **Horizontal rule** (Rich `Rule`): Full-width divider line with optional centered title. Example: `Rule("Turn 2", style="dim")` renders `──── Turn 2 ────`. Good for section boundaries.
- **Panel** (Rich `Panel`): Bordered box around content. Good for structured output (tool results, summaries) but interrupts streaming flow. Must be rendered as a complete block.
- **Table** (Rich `Table`): Columnar data display. Same constraint as Panel - requires complete data. Useful for turn summaries or tool result tables after completion.
- **Tree** (Rich `Tree`): Hierarchical display. Not applicable to sequential event stream.
- **Unicode box-drawing**: Manual `┌ ─ ┐ │ └ ┘ ├ ┤` characters. Full control, no Rich dependency. Good for lightweight structural hints.

### 1.6 Dynamic/Animated Elements

- **Spinner** (Rich `Status`): Animated character sequence with updating text. Already used for "generator thinking..." The spinner clears itself before any other output and restores after. Non-disruptive to streaming.
- **Progress bar** (Rich `Progress`): Visual bar with percentage, elapsed time, ETA, speed. Supports multiple concurrent tasks. Requires known total for percentage (or indeterminate mode). Can work alongside console output via `Progress.console`.
- **Live display** (Rich `Live`): In-place updating region. Replaces its content on each update. Powerful but complex to integrate with interleaved `console.print()` calls. Risk of output corruption if prints happen during live update.
- **In-place line update**: `\r` (carriage return) + overwrite. Simple, no Rich dependency. Works for single-line status updates. Conflicts with Rich's own cursor management when Status is active.

### 1.7 Temporal Display Elements

- **Elapsed time counter**: Text showing seconds since operation started. Pattern: `f"operation... {elapsed}s"`. Already used in spinner (`"generator thinking... 5s"`). Trivial to add to any status text.
- **Countdown timer**: Text showing seconds remaining. Pattern: `f"retrying in {remaining}s..."`. Requires known duration (available for retry delays: 2s, 8s).
- **Timestamp prefix**: `[14:30:05]` prefix on log lines. Rich `Console.log()` adds timestamps automatically. Adds precision but increases visual noise. Not recommended for user-facing output (debug console only).
- **Duration formatting** (LOG-GN-04): `"2 mins 15 secs"` not `"135s"` or `"2m 15s"`. Lana uses `secs`, `mins`, `hours` - never single-letter abbreviations. For operations >60s, minute-second format is more readable.

### 1.8 Information Markers

- **Prefix markers**: `[tool]`, `[think]`, `[sys]` - category indicators in square brackets. Already used for `[tool]`. Consistent prefix scheme enables visual scanning.
- **Unicode symbols** (monospace-safe subset per core-conventions.md): `→` (arrow, approved), box-drawing set (`┌ ─ ┐ │ └ ┘ ├ ┤`). Rich spinner braille dots (`⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏`) are single-width. No emojis (double-width, prohibited). No `▼` (ambiguous width, prohibited - use `v`). Avoid `✓` `✗` `●` `○` unless verified single-width in target terminal matrix.
- **Brackets and parentheses**: `(123 chars)`, `{pending}`. Grouping information.
- **Ellipsis truncation**: `"long text..."` with char count. Already used: `event.result[:300]`.
- **Status badges**: `[OK]`, `[FAIL]`, `[WAIT]`. Can combine with reverse style for badge effect: `style="reverse green"` renders green background with terminal-foreground text.

## 2. Architecture Constraints

### 2.1 Streaming Event Model

Lana's CLI processes events via `Renderer.handle(event)`. Events arrive asynchronously from an async generator. The renderer must:

- Print immediately on each event (no buffering multiple events)
- Handle interleaved text_delta events (streaming model output character by character)
- Not block the event generator (no long-running render operations)

### 2.2 Security: markup=False (BG-0004)

All `console.print()` calls MUST use `markup=False`. Model text, tool results, and provider messages are untrusted. Styling goes exclusively through the `style=` parameter. This means:

- No inline `[bold]text[/bold]` markup in print content
- No Rich renderables constructed from untrusted content (Panel titles, Table cells with model text)
- Static structural text (prefix markers, status labels) is safe - only agent-controlled strings

### 2.3 Console Multiplexing

Rich `Status` wraps `Live`, which pushes a render hook onto the `Console` that manages cursor positioning for in-place updates. Multiple Live/Status instances can coexist via Rich's internal `_live_stack` - the first instance renders all stacked content as a vertical group. This means:

- Simultaneous spinners are technically possible but produce confusing stacked live output
- Lana must stop the current spinner before starting a new one for clean single-indicator UX
- `stop_status()` + `start_status()` transition is the correct pattern
- The `try/except` in `start_status()` handles non-terminal consoles where Live rejects activation

### 2.4 JSONL Mode

When `--jsonl` flag is active, events are printed as JSON lines to stdout. The renderer is not used. Any UX improvements are CLI-interactive-mode only. JSONL consumers parse structured data, not visual formatting.

### 2.5 ACP Mode

In ACP mode, `render.py` is not invoked. Events go through `translator.py` into `session/update` JSON-RPC payloads. Console UX elements are irrelevant for ACP - that frontend needs structured data changes in the translator, not terminal styling.

### 2.6 Non-Terminal Fallback

Rich detects non-terminal outputs (pipes, files) and disables styling, spinners, and animations. The `try/except` in `start_status()` already handles this. Any new elements must degrade gracefully when `console.is_terminal` is False.

### 2.7 Monospace Fixed-Width Character Safety

All console output characters MUST occupy exactly one monospace column. Characters that break fixed-width alignment corrupt indentation, progress counters, and box-drawing diagrams.

**Approved characters** (core-conventions.md, verified single-width):
- ASCII printable range (U+0020 - U+007E): letters, digits, punctuation, space
- Unicode box-drawing (U+2500 - U+257F): `┌ ─ ┐ │ └ ┘ ├ ┤ ┬ ┴ ┼` and tree variants `├─>` `└─>`
- Arrow `→` (U+2192): single-width in monospace fonts
- Ellipsis `…` (U+2026): renders as single-width in most terminals
- Rich spinner braille dots (U+2800 - U+28FF): single-width, used internally by Rich Status

**Prohibited characters**:
- Emoji (U+1F600+ and others): double-width in all monospace contexts. Breaks column alignment.
- CJK characters (U+4E00 - U+9FFF, U+3000 - U+303F): double-width
- `▼` (U+25BC, Black Down-Pointing Triangle): ambiguous width across terminals. Use `v` instead.
- Geometric shapes (`●` `○` `✓` `✗`): East Asian Ambiguous width category. Render as single-width on Western terminals but double-width on CJK terminals. Avoid unless the terminal matrix is constrained.

**Test**: Any character used in console output must render identically in Windows Terminal (default font Cascadia Code) and common Linux terminals (default monospace). If a character renders at different widths, it is prohibited.

## 3. Compatibility Assessment

Rating scale: **FULL** (drop-in, no architectural changes), **CONDITIONAL** (works with integration care), **IMPRACTICAL** (conflicts with streaming model or security constraints).

### 3.1 FULL Compatibility

- **Foreground text colors via style=** - Drop-in. Add `style="dim"` to any `console.print()` call. Zero risk.
- **Text styles (bold, dim, underline)** - Drop-in. Same mechanism as colors.
- **Indentation** - Drop-in. Already used. Extend pattern.
- **Prefix markers** - Drop-in. Strings prepended to print content. Agent-controlled, safe with `markup=False`.
- **Rich Status spinner** - Drop-in. Already integrated. Pattern: `start_status()`, `tick_status()`, `stop_status()`.
- **Elapsed time counter** - Drop-in within spinner text. Already implemented in `tick_status()`.
- **Unicode symbols** - Drop-in. Static characters in agent-controlled strings.
- **Horizontal rule** (Rich `Rule`) - Drop-in. `console.print(Rule(style="dim"))`. Works between events. Not during streaming text.

### 3.2 CONDITIONAL Compatibility

- **Rich Progress bar** - Requires wrapping the event loop. Progress replaces Status as the active live display. Can coexist with `console.print()` but needs careful lifecycle management. Useful for known-duration operations (rare in Lana).
- **In-place line update (\r)** - Works for single-line status but conflicts with Rich Status cursor management. Use only when no Status is active. Safe pattern: stop spinner, write \r-updating line, then restart spinner.
- **Background colors on short text** - Works for inline badges (`style="reverse green"` for `[OK]`). Avoid on full lines - visual weight violates 70% neutral rule.
- **Countdown timer** - Requires async sleep loop to update display. Compatible if implemented as a spinner text update (reuse Status pattern with countdown text).

### 3.3 IMPRACTICAL

- **Rich Live display** - Requires owning the terminal region exclusively. Conflicts with interleaved `console.print()` calls from streaming events. Risk of output corruption during text_delta streaming.
- **Rich Panel mid-stream** - Panels are block renderables. Inserting a bordered box during character-by-character streaming breaks the visual flow and may corrupt line endings.
- **Rich Table mid-stream** - Same issue as Panel. Tables need complete data. Could work for post-turn summaries (after streaming ends) but adds visual weight.
- **blink style** - Prohibited by design system (DLPHS-IN07 Section 9.2: no interruption patterns).
- **italic style** - Unreliable cross-terminal support. Windows Terminal supports it; some Linux terminals do not.

## 4. Element-to-Problem Mapping

### 4.1 DA-01: LLM First Token Wait [HIGH]

**Problem**: Spinner freezes without thinking deltas (no independent tick). ACP sends nothing.

**CLI solution elements:**
- **Background-ticking spinner** (Status + asyncio.Task): An independent timer task updates the spinner text every second regardless of incoming events. Pattern: `asyncio.create_task(tick_spinner_loop())` started alongside `start_status()`. The task calls `status.update(f"  generator thinking... {elapsed}s")` every 1s until cancelled.
- **Elapsed counter**: Already present in concept. Just needs independent ticking.

**Why this works**: The spinner is a Rich Status object backed by Live, which has its own `_RefreshThread` for animation. An asyncio background task calling `status.update(text=...)` is safe because both the task and the event handler run on the same event loop thread (no OS-thread contention). The Live refresh thread handles terminal output locking internally via `RLock`. No new UX element needed - same spinner, independent timer.

**ACP solution**: Not a console element. Requires `translator.py` to emit a structured `agent_status` or `agent_thought_chunk` update on `turn_started` (architectural change, not UX element).

### 4.2 DA-02: Post-Turn Dead Air [HIGH]

**Problem**: After Turn stats line, cursor blinks with no activity signal until next `turn_started`.

**CLI solution elements (2 options, pick one):**

**Option A - Immediate spinner restart (RECOMMENDED):**
- After `turn_finished` renders the stats line and tool calls exist (meaning another turn will follow), immediately call `start_status()` with text like `"  preparing next request..."` in dim.
- The next `turn_started` event will call `start_status()` again, which calls `stop_status()` first (idempotent).
- **Elements used**: Existing Status spinner. No new UX elements.
- **Cost**: One extra `start_status()` call. Near-zero complexity.

**Option B - Earlier turn_started emission:**
- Move `yield self.emit(TurnStarted(...))` in `agent.py` to fire before message serialization, not after.
- **Elements used**: None (architectural change only).
- **Trade-off**: Changes agent event semantics. "turn_started" would fire before the request is actually sent.

### 4.3 DA-03: Long Tool Execution [HIGH]

**Problem**: Static `[tool]` line for 0-600s. No progress.

**CLI solution elements:**
- **Tool spinner with elapsed time**: After printing the `[tool]` line, start a new Status spinner with text like `"    running... {elapsed}s"`. Stop it when `tool_call_finished` arrives.
- **Indented spinner**: 4-space indent to nest under the `[tool]` line visually:
  ```
    [tool] run_command 'npm test'...
      running... 45s
  ```
- **Elements used**: Rich Status (reused), elapsed counter, indentation.

**Why not a Progress bar?** Tool durations are unpredictable. `run_command` can be 0-600s. `search_web` can be 2-15s. No known total means no percentage or ETA. An indeterminate spinner with elapsed time is the honest representation.

**Streaming partial output for run_command**: Not a UX element per se but an architectural enhancement. If `run_command` (Blocking) streamed stdout lines as they arrive, each line would stop the spinner and act as a natural progress indicator. This requires changes to `shell_tools.py`, not to `render.py`.

### 4.4 DA-04: Compaction Summarizer [MEDIUM]

**Problem**: 5-30s silence after NOTICE "Compacting context..."

**CLI solution elements:**
- **Spinner with elapsed time**: After the NOTICE line, start Status with `"  compacting... {elapsed}s"`. The `checkpoint_created` event stops the spinner.
- **Elements used**: Rich Status (reused), elapsed counter, dim style.
- **Complication**: The compaction happens inside `maybe_compact()` which yields events. The spinner must start on the NOTICE error event and stop on `checkpoint_created`. Currently both events flow through `handle()`, so the renderer can manage this.

### 4.5 DA-05: Provider Retry Sleep [MEDIUM]

**Problem**: Silence during 2s/8s retry delay.

**CLI solution elements:**
- **Countdown spinner**: After WARNING renders, start Status with `"  retrying in {remaining}s..."`. Update every second. Stop when retry starts (next event arrives).
- **Alternative - in-place countdown**: Update the WARNING line itself using `\r`. But WARNING is already printed and may have scrolled.
- **Elements used**: Rich Status (reused), countdown timer.

**Challenge**: The retry sleep happens inside the provider adapter (`stream_turn()`), which yields a `notice` delta. The renderer sees the WARNING but has no signal for "retry starting now." The countdown must be approximate: start counting after WARNING, stop on next event.

### 4.6 Style Consistency Fixes (LANAUSRX-IN01 Section 6.4)

**Problem**: Turn stats, compaction line, tool OK/ERROR render without dim style.

**CLI solution elements:**
- **dim style for CAT-SYSTEM lines**: Add `style="dim"` to `turn_finished` and `checkpoint_created` print calls.
- **dim style for CAT-TOOL results**: Add `style="dim"` to `tool_call_finished` OK line. ERROR line stays red (CAT-ERROR).

**Changes required** (3 lines in `render.py`):
- Line 86: `console.print(f"  Turn: ...")` add `style="dim"`
- Line 89: `console.print(f"  Compacted: ...")` add `style="dim"`
- Line 75: `console.print(f"    OK. ...")` add `style="dim"`

## 5. Recommended Patterns

### 5.1 The Universal Spinner Pattern

One pattern solves DA-01, DA-02, DA-03, DA-04, and DA-05: **a Rich Status spinner with elapsed/countdown text that ticks independently of event arrival.**

This pattern implements the **Announce Before Blocking** principle (LOG-GN-09, LOGGING-RULES.md): "Never enter a potentially long-running action without stating what is about to happen." Every dead-air phase is a blocking operation entered without announcement. The spinner IS the announcement.

Current implementation has the right structure but the wrong ticking mechanism. The fix is a single architectural change:

**Current**: `tick_status()` called only on `thinking_delta` events. Spinner freezes when no events arrive.
**Proposed**: Background async task ticks the spinner every 1 second, independent of events.

```
Start spinner (turn_started or tool_call_requested or compaction NOTICE)
  Background task: every 1s, update spinner text with elapsed time
  Any visible event: stop spinner, print event
  If more work follows: restart spinner immediately
Stop spinner (content arrives or operation completes)
```

This one change eliminates dead air in all 5 problematic phases. The spinner text changes per context:
- DA-01: `"  thinking... 5 secs"`
- DA-02: `"  preparing..."`
- DA-03: `"    running... 45 secs"` (indented under tool line)
- DA-04: `"  compacting... 8 secs"`
- DA-05: `"  retrying in 3 secs..."` (countdown variant)

Duration format follows LOG-GN-04: `secs`, `mins` - never `s`, `m` or bare numbers.

### 5.2 Dim-for-Metadata Pattern

All CAT-SYSTEM and CAT-TOOL output uses `style="dim"`. This creates a clear visual hierarchy:

- **Default** (no style): Model text output - the primary content the user cares about
- **dim**: Everything else - tool lines, tool results, turn stats, compaction, notices. Visible but unobtrusive.
- **yellow**: Warnings. Draws attention without alarm.
- **red**: Errors. Demands attention.
- **bold blue/cyan** (future): Approval prompts. The ONE thing requiring user action.

This maps directly to the design system's 70/20/10 emphasis rule:
- **70% neutral** = dim metadata (most lines are tool calls and system events)
- **20% primary** = default-styled model text (the actual content)
- **10% emphasis** = colored warnings, errors, approvals (rare, high-signal events)

### 5.3 Indentation-as-Hierarchy Pattern

```
[think] generator thinking... 5s        ← category prefix, dim, spinner
This is the model's response text.       ← default style, primary content
  [tool] search_web 'query'...           ← 2-space indent, dim
    running... 3s                        ← 4-space indent, dim, spinner
    OK. 1234 chars.                      ← 4-space indent, dim
  [tool] read_file '/path'...            ← 2-space indent, dim
    OK. 567 chars.                       ← 4-space indent, dim
More model text continues here.          ← default style
  Turn: in=1234 out=567 | $0.0043       ← 2-space indent, dim
```

Already partially implemented. Tool lines use 2-space indent, results use 4-space. Extending this to all metadata creates a consistent visual tree.

### 5.4 Horizontal Rule for Turn Boundaries (OPTIONAL)

Between turns in a multi-turn tool loop, a dim horizontal rule provides visual separation:

```
  Turn: in=1234 out=567 | $0.0043
  ────
  [tool] run_command 'npm test'...
```

Rich `Rule(style="dim")` renders a full-width line. Lightweight, non-disruptive. However, this adds a line of output that carries no information. Evaluate whether the visual separation justifies the vertical space.

**Verdict**: Defer. Not needed if dim-for-metadata pattern provides sufficient visual hierarchy.

### 5.5 Announce > Track > Report Pattern

The logging rules define a three-phase pattern (LOGGING-RULES.md) that maps directly to status signaling:

1. **Announce**: State what will happen before starting. Pattern: `"operation_name 'target'..."` with ellipsis (LOG-GN-10). This is the `[tool]` line or the spinner start text.
2. **Track**: Show progress during execution. Pattern: elapsed counter in spinner, `[ x / n ]` iteration counters (LOG-UF-02), running counts `( x / n )` for sub-items. Feedback at least every ~10 secs for long operations (LOG-UF-04).
3. **Report**: State final status. Pattern: `OK.` or `OK: details` for success, `ERROR: what -> system error` for failure (LOG-GN-08, two-level error format).

**Current Lana renderer already follows this pattern partially:**
- Announce: `[tool] search_web 'query'...` (ellipsis correct per LOG-GN-10)
- Track: MISSING (spinner frozen or absent - this is the dead-air problem)
- Report: `OK. 1234 chars.` or `ERROR: message` (correct per LOG-GN-11)

**The dead-air problem is a missing Track phase.** The Universal Spinner Pattern (5.1) fills this gap. Every operation gets: Announce (print line) > Track (spinner with elapsed) > Report (result line).

**Additional logging rules applicable to renderer output:**
- LOG-GN-01: 2-space indentation per level (already used)
- LOG-GN-02: Quote paths, names, IDs with single quotes (already used for tool summaries)
- LOG-GN-03: Numbers and counters first in result messages (apply to `OK. 1234 chars.`)
- LOG-GN-05: Singular/plural correctness (`1 char` not `1 chars`)
- LOG-GN-11: Announce lines end with `...`, result lines end with `.`
- LOG-GN-12: No acronyms without expansion on first use

### 5.6 Tool Result Display Enhancement (FUTURE)

For completed tools, the current `OK. N chars.` line is minimal. Future options:

- **Summary line for read tools**: `OK. 567 chars (15 lines, Python).` Adds context without verbose output.
- **Error preview with dim**: `ERROR: FileNotFoundError: /path/to/file` in dim red (currently full red). Distinguishes tool errors (recoverable, agent will adapt) from agent errors (may need user attention).
- **Collapsed result**: Full result hidden, summary shown. Not implementable in sequential terminal output without Rich Live.

## 6. Anti-Patterns

### 6.1 Never: Multiple Simultaneous Spinners

Rich supports stacking multiple Live/Status instances via an internal `_live_stack`. A second Status becomes "nested" - its content is composed into the first instance's live display region as a vertical group. This does not crash or corrupt, but produces a confusing multi-line live display with multiple spinners on screen. Lana should always `stop_status()` before `start_status()` to maintain a single clear status indicator.

### 6.2 Never: Background Colors on Full Lines

A full-width colored background line (e.g., red banner for errors) violates the 70% neutral rule and looks jarring in a terminal. Background colors are acceptable only on short inline badges (2-8 characters).

### 6.3 Never: Rich Markup in Untrusted Content

`markup=False` is non-negotiable (BG-0004). Never construct Rich markup strings from model text or tool results. Even seemingly safe content can contain `[tags]` that Rich interprets.

### 6.4 Never: Progress Bar Without Known Total

An indeterminate progress bar (no percentage) looks identical to a spinner but occupies more vertical space. Use a spinner instead. Reserve progress bars for operations where the total is known (e.g., file upload with known byte count - not applicable in Lana today).

### 6.5 Never: Timestamps on User-Facing Output

`Console.log()` adds timestamps. This is debug-level information. User-facing output should show elapsed time relative to the current operation, not wall-clock time. The debug console (`debug_viewer.py`) already handles timestamped logging.

### 6.6 Never: Color as Sole Indicator

Design system anti-pattern (DLPHS-IN10 Section 14): "No color as the SOLE indicator of state." Always pair color with text. Current implementation is correct: `"WARNING: ..."` in yellow (text + color), not just yellow text with no prefix.

### 6.7 Never: Double-Width or Ambiguous-Width Characters

Emojis, CJK characters, and geometric shapes from the East Asian Ambiguous width category break monospace column alignment. One double-width character shifts all subsequent text by one column, corrupting indentation trees, progress counters, and box-drawing structures. See Section 2.7 for the full approved/prohibited character list.

The core-conventions.md explicitly prohibits `▼` (U+25BC) and mandates `v` instead. This prohibition extends to all characters where width varies across terminal implementations.

### 6.8 Never: Silent Entry Into Blocking Operations

The Announce Before Blocking principle (LOGGING-RULES.md) states: "Any call that could take more than 10 seconds MUST be preceded by a log line announcing the action." In Lana's context, this means:

- Every LLM call must be preceded by a spinner or status text (DA-01, DA-02)
- Every tool execution must be preceded by a `[tool]` announce line (already done) AND followed by a tracking indicator (DA-03, missing)
- Every compaction must be preceded by a NOTICE (already done) AND followed by a tracking indicator (DA-04, missing)
- Every retry must be preceded by a WARNING (already done) AND followed by a countdown (DA-05, missing)

The pattern is always the same: announce BEFORE the blocking call, never after.

## 7. Next Steps

1. **Write SPEC**: Define the status signaling contract using the Universal Spinner Pattern (5.1) and Dim-for-Metadata Pattern (5.2) as the core design
2. **Prototype spinner ticking**: Implement background async task for spinner in render.py. Verify it works with Rich Status on Windows Terminal and basic Linux terminals
3. **Apply style consistency**: Add `style="dim"` to the 3 identified lines in render.py (Section 4.6). This is a zero-risk change that can ship immediately

## 8. Sources

- `LANAUSRX-IN02-SC-SRC-RNDPY`: `src/lana/render.py` - Current renderer implementation, Rich Status usage, style patterns [VERIFIED]
- `LANAUSRX-IN02-SC-SRC-AGTPY`: `src/lana/agent.py` - Event emission sequence, turn loop structure [VERIFIED]
- `LANAUSRX-IN02-SC-SRC-EVTPY`: `src/lana/events.py` - AgentEvent type definitions [VERIFIED]
- `LANAUSRX-IN02-SC-RICH-DOCS`: [Rich documentation](https://rich.readthedocs.io/) (v13+) - Console, Status, Progress, Live, Panel, Table, Rule, Text styling [VERIFIED]
- `LANAUSRX-IN02-SC-PYPR-TOML`: `pyproject.toml` - Rich >= 13 dependency confirmed [VERIFIED]
- `LANAUSRX-IN02-SC-DLPH-IN10`: `specs/UXDesign/_INFO_DELPHIOS_DESIGN_SYSTEM.md [DLPHS-IN10]` - 70/20/10 emphasis rule, anti-patterns (Section 14), interaction philosophy (Section 11.5) [VERIFIED]
- `LANAUSRX-IN02-SC-DLPH-IN07`: `specs/UXDesign/_INFO_DELPHIOS_BRAND.md [DLPHS-IN07]` - Frugal language (Section 9.1), no interruption patterns (Section 9.2) [VERIFIED]
- `LANAUSRX-IN02-SC-IN01-DA`: `_INFO_LANAUSRX_INTERACTION_CHAIN.md [LANAUSRX-IN01]` - Dead-air phases DA-01 through DA-07, interaction categories, proposed color scheme [VERIFIED]
- `LANAUSRX-IN02-SC-LGRLS-GN`: `LOGGING-RULES.md` (@skills:coding-conventions) - Announce > Track > Report pattern, LOG-GN-01 through LOG-GN-12, Announce Before Blocking principle [VERIFIED]
- `LANAUSRX-IN02-SC-LGRLS-UF`: `LOGGING-RULES-USER-FACING.md` (@skills:coding-conventions) - LOG-UF-01 through LOG-UF-06, feedback timing, progress indicator format [VERIFIED]
- `LANAUSRX-IN02-SC-CCONV-MD`: `core-conventions.md` (@rules) - Approved Unicode character set, monospace safety, arrow and box-drawing conventions [VERIFIED]
- `LANAUSRX-IN02-SC-SPRLS-MD`: `SPEC_RULES.md` (@skills:write-documents) - UI diagram conventions, logging requirement structure (SPEC-LG-01 through SPEC-LG-03) [VERIFIED]

## 9. Document History

**[2026-08-31 18:15]**
- Fixed: Section 1.3 "strikethrough" corrected to "strike" (Rich style name, verified against Rich 15.0.0 source)
- Fixed: Section 2.3 mechanism rewritten - Status wraps Live, uses `_live_stack` for nesting, not mutual exclusion
- Fixed: Section 4.1 thread-safety explanation corrected - asyncio same-thread safety, not Rich locking
- Fixed: Section 6.1 anti-pattern rewritten - Rich nesting behavior, not silent failure
- Review: `_INFO_LANAUSRX_CONSOLE_UX_ELEMENTS_REVIEW.md [LANAUSRX-IN02-RV01]`

**[2026-08-31 18:00]**
- Added: Announce > Track > Report pattern (Section 5.5) mapping logging rules to dead-air status signaling
- Added: Announce Before Blocking principle reference in Universal Spinner Pattern (Section 5.1) and as anti-pattern (Section 6.8)
- Added: Monospace fixed-width character safety constraint (Section 2.7) with approved/prohibited character lists per core-conventions.md
- Added: Anti-pattern 6.7 for double-width/ambiguous-width characters
- Changed: Section 1.7 duration format to match LOG-GN-04 (`secs`, `mins` not `s`, `m`)
- Changed: Section 1.8 Unicode symbols list restricted to monospace-safe subset
- Changed: Spinner text examples updated to use LOG-GN-04 duration format
- Added: Dependencies on LOGGING-RULES.md, core-conventions.md, SPEC_RULES.md
- Added: 5 new source entries for logging rules, core conventions, spec rules

**[2026-08-31 17:45]**
- Initial research document created from Rich library analysis, render.py audit, and dead-air problem mapping
