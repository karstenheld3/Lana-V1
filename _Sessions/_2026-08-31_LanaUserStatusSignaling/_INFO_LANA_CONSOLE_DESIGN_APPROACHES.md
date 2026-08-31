# INFO: Console Design Approaches for Lana CLI

**Doc ID**: LANAUSRX-IN03
**Goal**: Propose 5 alternative design approaches for Lana's Command-Line Interface (CLI) console output, grounded in Delphios design system principles, with ASCII previews of each
**Timeline**: Created 2026-08-31, Updated 2 times (2026-08-31 - 2026-08-31)

**Depends on:**
- `_INFO_LANAUSRX_INTERACTION_CHAIN.md [LANAUSRX-IN01]` for dead-air phases DA-01 through DA-07 and interaction categories
- `_INFO_LANAUSRX_CONSOLE_UX_ELEMENTS.md [LANAUSRX-IN02]` for element inventory, compatibility assessment, and anti-patterns
- `_INFO_DELPHIOS_DESIGN_SYSTEM.md [DLPHS-IN10]` for CLEN-CARE-FROM (CLear ENgineered, CAlm RElaxed, FResh MOdern) principle, 70/20/10 rule, interaction philosophy

## Summary

- 5 design approaches proposed, each emphasizing a different facet of the Delphios design system [ASSUMED]
- All approaches share 3 non-negotiable constraints: `markup=False`, monospace-safe characters, >300ms spinner coverage [VERIFIED]
- Approaches range from minimal change (B) to architectural shift (C, E) [ASSUMED]
- Each preview uses the same 3-turn scenario for direct comparison [ASSUMED]
- All approaches inherit a shared CLI Color Map (Section 1.1) mapping 6 interaction categories to Rich styles: dim for metadata (70%), no style for content (20%), yellow/red/bold for emphasis (10%) [VERIFIED]
- Each approach specifies a complete event-to-output map showing exact Rich style, format, and state transitions per AgentEvent type [VERIFIED]
- Recommended shortlist: B and D for pragmatic implementation; C for aspirational target [ASSUMED]

## Table of Contents

1. [Shared Constraints](#1-shared-constraints)
2. [Reference Scenario](#2-reference-scenario)
3. [Approach A: Structured Log](#3-approach-a-structured-log)
4. [Approach B: Quiet Infrastructure](#4-approach-b-quiet-infrastructure)
5. [Approach C: Live Footer](#5-approach-c-live-footer)
6. [Approach D: Conversational Asides](#6-approach-d-conversational-asides)
7. [Approach E: Progressive Disclosure](#7-approach-e-progressive-disclosure)
8. [Comparison](#8-comparison)
9. [Next Steps](#9-next-steps)
10. [Sources](#10-sources)
11. [Document History](#11-document-history)

## 1. Shared Constraints

Every approach must satisfy these non-negotiable constraints from LANAUSRX-IN01, LANAUSRX-IN02, and the design system:

- **BG-0004**: `markup=False` on every `console.print()`. Styling via `style=` parameter only.
- **>300ms rule** (DLPHS-IN10 Section 16.2): Any gap >300ms gets a spinner or status indicator.
- **Monospace safety** (core-conventions.md): ASCII + box-drawing + arrow `->` + Rich braille spinner. No emojis, no ambiguous-width Unicode.
- **Duration format** (LOG-GN-04): `secs`, `mins`, `hours` with singular/plural. Never `s`, `m`, `h`.
- **Announce Before Blocking** (LOG-GN-09): Log before entering any call that could take >10 secs.
- **Severity colors reserved**: yellow = WARNING, red = ERROR. Never borrowed for other purposes.
- **Non-terminal fallback**: All approaches degrade to plain text when `console.is_terminal` is False.

### 1.1 CLI Color Map

All approaches inherit this category-to-style mapping from LANAUSRX-IN01 Section 6.3. Approaches may suppress or rearrange output lines but never change the style assigned to a category.

**70/20/10 distribution in CLI** (DLPHS-IN10 Section 3.7):
- **70% neutral** (`style="dim"`): Thinking status, tool announce/result, turn stats, compaction notices. Reduced brightness signals "infrastructure"
- **20% content** (no style): Model text output. Full terminal brightness = primary reading content
- **10% emphasis**: Errors and approvals. `style="yellow"` (WARNING), `style="red"` (ERROR), `style="bold"` or default (approval prompt)

**Category-to-Rich-style reference:**
- CAT-THINK: `style="dim"` + Rich Status spinner (animated braille dots). Text: `thinking... Ns` or `retrying... Ns`
- CAT-STREAM (text): no style. Printed inline via `console.print(text, end="", markup=False)`
- CAT-STREAM (thinking shown): `style="dim"`. Reasoning printed inline, reduced brightness distinguishes from final output
- CAT-TOOL (announce): `style="dim"`. Tool name + argument summary
- CAT-TOOL (running >300ms): `style="dim"` + spinner. Elapsed counter ticks
- CAT-TOOL (result): `style="dim"`. `OK. N chars.` or `ERROR: message`
- CAT-APPROVE: `style="bold"` or default. Single element requiring user action (DLPHS-IN10 10% emphasis rule)
- CAT-SYSTEM: `style="dim"`. Turn stats, compaction notices, session metadata
- CAT-ERROR (WARNING): `style="yellow"`. Transient issues, retry announcements
- CAT-ERROR (ERROR): `style="red"`. Failures requiring attention
- CAT-ERROR (NOTICE): `style="dim"`. Informational, treated as CAT-SYSTEM

**Color zone isolation** (DLPHS-IN10 Section 3.10): Severity colors (yellow, red) reserved exclusively for errors and warnings. Never borrowed for progress, status, or category differentiation. All non-severity metadata uses `dim` regardless of category.

**Shared state transitions** (event order is fixed; approaches differ in which lines they emit and how they format them):

```
turn_started          → start spinner (dim, animated)
thinking_delta        → tick spinner elapsed (or print dim text if shown)
text_delta            → stop spinner, print text (no style, inline)
tool_call_requested   → stop spinner, emit tool announce (dim)
  [tool running]      → start tool spinner (dim, animated) if >300ms
tool_call_finished    → stop spinner, emit result (dim)
turn_finished         → emit turn stats (dim)
error (WARNING:)      → emit message (yellow)
error (ERROR:)        → emit message (red)
error (NOTICE:)       → emit message (dim)
checkpoint_created    → emit compaction summary (dim)
approval_required     → emit approval prompt (bold)
```

## 2. Reference Scenario

All 5 previews render the same agent interaction for direct comparison.

**User prompt**: "fix the import error in parser.py"

**Agent sequence**:
- Turn 1: Thinks 5 secs, types "I'll read parser.py to find the import error.", reads file (1 sec), edits file (<1 sec)
- Turn 2: Thinks 3 secs, types "Running tests to verify.", runs pytest (12 secs)
- Turn 3: Types "Fixed. Changed `json_parser` to `parser_core` on line 3. All 12 tests pass."

**Styling legend for previews**:
- `[dim]` = rendered with `style="dim"` (reduced brightness, secondary content)
- `[default]` = no style (full brightness, primary content)
- `[yellow]` / `[red]` = severity colors
- `[spinner]` = Rich Status spinner (animated braille dots + text, ephemeral)
- Lines without annotation = default style

## 3. Approach A: Structured Log

**Philosophy**: Every line is typed, classified, and indented by hierarchy. The console reads like a well-formatted structured log. Maps to CLEN-CARE-FROM "Clear, Engineered" - order and structure as top priority.

**Design system principles applied**:
- "Precision: clear, engineered - order, structure and clarity are top priorities" (DLPHS-IN10 Section 1)
- 70/20/10: Category prefixes and dim styling make the 70% neutral visible as structure
- "Evidence presented as a system rather than decoration" (DLPHS-IN10 Section 1)

**Key decisions**:
- Every non-content line gets a category prefix: `[think]`, `[tool]`, `[sys]`
- 2-space indent for category lines, 4-space for sub-items (tool results)
- Content (model text) has zero prefix, zero indent - stands out by absence of structure
- Background-ticking spinner covers all dead-air phases
- Turn stats prefixed with `[sys]`, not naked

### 3.1 Preview: Final Scrollback

```
> fix the import error in parser.py
                                                          .
  [think] thinking... 5 secs                          [dim, spinner]
I'll read parser.py to find the import error.
  [tool] read_file 'src/parser.py'...                     [dim]
    running... 1 sec                                  [dim, spinner]
    OK. 234 chars.                                        [dim]
  [tool] edit 'src/parser.py'...                          [dim]
    OK. 1 char.                                           [dim]
  [sys] in=4521 out=187 $0.003                            [dim]
                                                          .
  [think] preparing... 2 secs                         [dim, spinner]
  [think] thinking... 3 secs                          [dim, spinner]
Running tests to verify.
  [tool] run_command 'pytest tests/test_parser.py'... [dim]
    running... 12 secs                                [dim, spinner]
    OK. 892 chars.                                        [dim]
  [sys] in=5200 out=94 $0.004                             [dim]
                                                          .
  [think] thinking... 1 sec                           [dim, spinner]
Fixed. Changed `json_parser` to `parser_core` on
line 3. All 12 tests pass.
  [sys] in=5800 out=42 $0.002                             [dim]
```

### 3.2 Color and State Behavior

Inherits all styles from Section 1.1. Approach A adds category prefix markers as an additional classification signal on every non-content line.

**Event-to-output map:**
- turn_started → `  [think] thinking...` `[dim, spinner]` - 2-space indent, prefix marker
- thinking_delta → tick spinner elapsed: `  [think] thinking... 5 secs` `[dim, spinner]`
- text_delta → stop spinner, blank separator line, print text at column 0 `[no style]`
- tool_call_requested → `  [tool] name 'args'...` `[dim]` - 2-space indent
- tool running >300ms → `    running... Ns` `[dim, spinner]` - 4-space indent (sub-item)
- tool_call_finished (OK) → `    OK. N chars.` `[dim]`
- tool_call_finished (fail) → `    ERROR: message` `[dim]`
- turn_finished → `  [sys] in=N out=N $X.XXX` `[dim]`
- error (WARNING:) → `WARNING: message` `[yellow]` - no prefix, full width
- error (ERROR:) → `ERROR: message` `[red]` - no prefix, full width
- error (NOTICE:) → `  [sys] message` `[dim]` - reclassified as system
- checkpoint_created → `  [sys] Compacted: N messages → M` `[dim]`
- approval_required → `  [action] details` `[bold]`, then `Approve? [y/n/a]` prompt

**Approach-specific decisions:**
- Prefix markers (`[think]`, `[tool]`, `[sys]`, `[action]`) are 4-7 chars, always inside brackets. Brackets visually separate them from content
- Content lines have NO prefix, NO indent. Model text stands out by ABSENCE of structure
- Blank separator line between turns: emitted after turn stats, before next spinner. Creates visual turn boundary
- `[think] preparing...` appears for post-turn gap (DA-02): the time between turn_finished and next provider response
- Sub-items (tool results) use 4-space indent under 2-space parent. Two-level hierarchy only

**Trade-offs**:
- PRO: Every line is instantly classifiable by prefix. Machine-parseable. Grep-friendly.
- PRO: Clear visual hierarchy - model text jumps out because it lacks the `[prefix]` pattern.
- PRO: Full traceability - nothing hidden, every phase visible.
- CON: Verbose. 21 lines for a 3-turn interaction. The `[think]` and `[sys]` lines add vertical space with low information value.
- CON: Prefix markers `[think]`, `[tool]`, `[sys]` are agent jargon, not user language. Violates "self-explanatory" principle (DLPHS-IN10 Section 11.5).
- CON: The repeated `[think] preparing...` / `[think] thinking...` pairs are noisy for multi-turn tool loops.

**Implementation complexity**: LOW. Extends current renderer with prefix markers and dim styling. No new Rich patterns.

## 4. Approach B: Quiet Infrastructure

**Philosophy**: Model text IS the product. Everything else is invisible infrastructure that the user notices only when needed. Maps to CLEN-CARE-FROM "Calm, Relaxed" - non-distracting, frictionless.

**Design system principles applied**:
- "Calm, relaxed - no distractions, no dissonances, no noise" (DLPHS-IN10 Section 1)
- "Whitespace as active design element" (DLPHS-IN10 Section 1)
- 70/20/10: Dim metadata is the 70% neutral, model text is the 20%, approval/error is the 10%
- "Explorative over instructive" (DLPHS-IN10 Section 11.5): Status is visible when the user looks for it, ignorable otherwise

**Key decisions**:
- Merge tool announce + result into ONE dim line when result is fast (<2 secs)
- Spinner for any gap >2 secs (thinking, long tools, compaction, retry)
- Turn stats compressed to minimal format, dim
- No category prefixes - tools identified by name only
- Empty line between turns creates breathing room (whitespace as design element)
- Content (model text) at full width, default style, zero decoration

### 4.1 Preview: Final Scrollback

```
> fix the import error in parser.py

  thinking... 5 secs                                  [dim, spinner]
I'll read parser.py to find the import error.
  read_file 'src/parser.py'  234 chars.                   [dim]
  edit 'src/parser.py'  OK.                               [dim]
  4521 in  187 out  $0.003                                [dim]

  thinking... 3 secs                                  [dim, spinner]
Running tests to verify.
  run_command 'pytest tests/test_parser.py'...        [dim, spinner]
    12 secs  892 chars.                                   [dim]
  5200 in  94 out  $0.004                                 [dim]

Fixed. Changed `json_parser` to `parser_core` on
line 3. All 12 tests pass.
  5800 in  42 out  $0.002                                 [dim]
```

### 4.2 Color and State Behavior

Inherits all styles from Section 1.1. Approach B maximizes the 70/20/10 ratio by merging and compressing metadata lines.

**Event-to-output map:**
- turn_started → `  thinking...` `[dim, spinner]` - no prefix, 2-space indent
- thinking_delta → tick spinner elapsed: `  thinking... 5 secs` `[dim, spinner]`
- text_delta → stop spinner, print text at column 0 `[no style]`
- tool_call_requested (fast tool, <2 secs) → buffer; do NOT emit yet
- tool_call_finished (fast) → merge with buffered announce: `  name 'args'  result` `[dim]` - single line
- tool_call_requested (slow tool, >2 secs) → `  name 'args'...` `[dim, spinner]`
- tool_call_finished (slow) → `    Ns  N chars.` `[dim]` - indent under parent
- turn_finished → `  Nin  Nout  $X.XXX` `[dim]` - no labels, positional format
- error (WARNING:) → `WARNING: message` `[yellow]`
- error (ERROR:) → `ERROR: message` `[red]`
- error (NOTICE:) → `  message` `[dim]`
- checkpoint_created → `  Compacted: N messages → M` `[dim]`
- approval_required → `[action] details` `[bold]`, prompt

**Approach-specific decisions:**
- **Merged tool lines**: When `tool_call_finished` arrives within 2 secs of `tool_call_requested`, both are emitted as a single dim line. This collapses the "Announce > Track > Report" pattern into "Announce+Report" for fast operations. Trade-off: loses the real-time "waiting" signal for sub-2-second tools
- **No labels on turn stats**: `4521 in  187 out  $0.003` uses positional convention (input count, output count, cost). Learned after first exposure. Violates AP-PR-11 (labels decodable at point of use) but gains compactness
- **Empty line between turns**: Emitted after turn stats, before next spinner. The whitespace IS the turn boundary (no separator line or prefix needed)
- **Spinner threshold 2 secs** (not 300ms): The >300ms rule is satisfied by the dim tool announce line itself (it appears immediately). The spinner adds elapsed tracking only for operations long enough to create user anxiety (>2 secs)
- **Tool names as identifiers**: `read_file`, `edit`, `run_command` are self-explanatory. But `command_status`, `trajectory_search` are not - this is a known weakness

**Trade-offs**:
- PRO: Maximum content-to-noise ratio. 16 lines for the same scenario (vs 21 in A).
- PRO: Merged tool lines for fast operations reduce visual clutter. The user sees "it read and edited a file" in 2 lines, not 6.
- PRO: Whitespace between turns creates natural rhythm. The eye finds model text instantly.
- PRO: Closest to current implementation - evolutionary, not revolutionary.
- CON: Merged tool lines lose the "Announce > Track > Report" three-phase pattern. The user cannot distinguish "announced and waiting" from "completed" during fast tools.
- CON: No category prefixes means tool names must be recognizable on their own. `edit` is clear; `command_status` is not.
- CON: Turn stats are cryptic without labels. `4521 in  187 out` requires learned interpretation.

**Implementation complexity**: LOW. Primarily adding `style="dim"` and merging tool announce/result logic. Minor reformatting.

## 5. Approach C: Live Footer

**Philosophy**: Separate ephemeral metadata from permanent content. A persistent status strip at the terminal bottom shows real-time state. Scrollback contains only what matters long-term. Maps to CLEN-CARE-FROM "Fresh, Modern" - innovative use of terminal capabilities.

**Design system principles applied**:
- "Fresh, modern - innovation from clarity and reduction" (DLPHS-IN10 Section 1)
- "One dominant message per view" (DLPHS-IN10 Section 1): Scrollback is purely content; footer is purely status
- "Zero friction" (DLPHS-IN10 Section 11.5): No mental effort to separate content from metadata

**Key decisions**:
- Rich Status/Live used as persistent bottom region with state, elapsed time, tool count, cost
- Scrollback receives ONLY: model text, errors, approval prompts
- Tool operations announced and tracked in footer only (not printed to scrollback)
- On turn_finished, footer updates cumulatively. On prompt completion, footer emits a one-line summary to scrollback and clears.
- Approval prompts break through to scrollback (they need permanent record + user input)

### 5.1 Preview: Final Scrollback

```
> fix the import error in parser.py

I'll read parser.py to find the import error.

Running tests to verify.

Fixed. Changed `json_parser` to `parser_core` on
line 3. All 12 tests pass.
  3 turns  5 tools  $0.009                                [dim]
```

### 5.2 Preview: Live Footer Strip

```
┌───────────────────────────────────────────────────────┐
│  running run_command... 12 secs | 3/5 tools | $0.007  │
└───────────────────────────────────────────────────────┘
```

### 5.3 Color and State Behavior

Approach C uses TWO rendering surfaces with distinct style rules. The scrollback receives only 20%+10% content (model text, errors, approvals). The footer handles 70% neutral metadata in real-time.

**Scrollback output (permanent record):**
- text_delta → print text at column 0 `[no style]` - the ONLY dim-free content in scrollback
- error (WARNING:) → `WARNING: message` `[yellow]`
- error (ERROR:) → `ERROR: message` `[red]`
- approval_required → `[action] details` `[bold]`, prompt - breaks through to scrollback
- prompt complete → `  N turns  N tools  $X.XXX  Ns` `[dim]` - single cumulative summary

**Footer strip (ephemeral, Rich Status or Live):**
- turn_started → footer appears: `thinking...` + elapsed `[dim, spinner]`
- thinking_delta → footer ticks elapsed counter
- text_delta → footer clears (content flowing = no status needed)
- tool_call_requested → footer shows: `running name... Ns | N/M tools | $X.XXX` `[dim, spinner]`
- tool_call_finished → footer updates tool count, cost. No scrollback output
- turn_finished → footer updates cumulative turn count, stats. No scrollback output
- error (NOTICE:) → footer shows message briefly, then reverts to status `[dim]`
- checkpoint_created → footer shows `compacting...` then `compacted` `[dim]`
- prompt complete → footer emits summary to scrollback, then clears entirely

**Footer appearance** (Rich Status with box-drawing border):
```
┌───────────────────────────────────────────────────────┐
│  running run_command... 12 secs | 3/5 tools | $0.007  │
└───────────────────────────────────────────────────────┘
```
- Box-drawing borders (`┌─┐│└─┘`) mark the footer as structurally separate from scrollback
- Single line of content inside: current activity + elapsed + cumulative stats
- Spinner animates on the left. Stats update in real-time on the right

**Approach-specific decisions:**
- **Two surfaces = two rendering modes**: Scrollback uses `console.print()`. Footer uses `console.status()` or `Live()` with refresh. The boundary is clear: `console.print()` = permanent, `status/Live` = ephemeral
- **No tool lines in scrollback**: Tools are purely operational. The user does not need a permanent record of `read_file 'src/parser.py'`. If they want forensics, JSONL log captures everything
- **Approval breaks through**: Approval prompts need user input AND a permanent record. They appear in both scrollback (permanent) and interrupt the footer
- **Summary on prompt complete**: When the final turn finishes and no more tool calls remain, the footer emits a single dim line to scrollback: `  3 turns  5 tools  $0.009  23 secs`. Then the footer clears. This is the ONLY metadata that persists
- **Footer width**: Footer box adapts to terminal width. On narrow terminals (<60 cols), drops border and shows stats inline

**Trade-offs**:
- PRO: Cleanest scrollback of all approaches. 9 lines for 3 turns. Pure content.
- PRO: Real-time status always visible without polluting history. The user sees "12 secs" ticking live.
- PRO: Tool operations are tracked but do not interrupt the reading flow of model text.
- PRO: Cumulative cost visible at all times (footer persists across turns).
- CON: Rich Live/Status footer conflicts with interleaved `console.print()` for model text. Requires careful coordination to avoid cursor corruption. LANAUSRX-IN02 Section 3.3 warns about this.
- CON: Tool names and results are invisible in scrollback. If the user scrolls up to understand what happened, they see content but not the agent's actions. Loses forensic value.
- CON: Highest implementation complexity. Requires refactoring render.py to manage a persistent Live region alongside streaming text output.
- CON: Non-terminal fallback must handle the "no footer" case entirely differently.

**Implementation complexity**: HIGH. Requires Rich Live region management, careful cursor coordination, and dual rendering paths (terminal vs non-terminal).

## 6. Approach D: Conversational Asides

**Philosophy**: The console reads like a transcript with quiet stage directions. Metadata appears as parenthetical asides - present but subordinate to the narrative flow. Maps to CLEN-CARE-FROM "Calm" combined with the brand voice principle of "authoritative and functional" language.

**Design system principles applied**:
- "Self-explanatory: no proactive help by default" (DLPHS-IN10 Section 11.5): Asides are natural language, not codes
- "Headlines are conclusions" (DLPHS-IN10 Section 12.1): Status text states what happened, not the category
- "Reduce cognitive burden" (DLPHS-IN10 Section 11.5): Parentheses signal "this is secondary" universally

**Key decisions**:
- Metadata in parentheses: `(thinking... 5 secs)`, `(read src/parser.py, 234 chars)`
- Fast sequential tools grouped on one line: `(read src/parser.py, 234 chars) (edit src/parser.py, OK)`
- Parentheses naturally signal "aside" to readers without needing dim style (though dim is still applied)
- Turn stats as natural language: `(turn 1: 4.5K tokens, $0.003)`
- Spinner text also parenthetical: `(running pytest... 12 secs)`
- No prefix markers, no brackets, no engineering notation

### 6.1 Preview: Final Scrollback

```
> fix the import error in parser.py

(thinking... 5 secs)                                  [dim, spinner]
I'll read parser.py to find the import error.
(read 'src/parser.py', 234 chars)                         [dim]
(edit 'src/parser.py', OK)                                [dim]
(4.5K tokens, $0.003)                                     [dim]

(thinking... 3 secs)                                  [dim, spinner]
Running tests to verify.
(run_command 'pytest tests/test_parser.py'...         [dim, spinner]
  12 secs, 892 chars)                                     [dim]
(5.2K tokens, $0.004)                                     [dim]

Fixed. Changed `json_parser` to `parser_core` on
line 3. All 12 tests pass.
(5.8K tokens, $0.002)                                     [dim]
```

### 6.2 Color and State Behavior

Inherits all styles from Section 1.1. Approach D wraps ALL metadata in parentheses. The parentheses are the structural signal; `style="dim"` is the secondary signal. Double encoding (parentheses + dim) ensures metadata is recognizable even without color support.

**Event-to-output map:**
- turn_started → `(thinking...)` `[dim, spinner]` - parenthetical, spinner inside parens
- thinking_delta → tick spinner: `(thinking... 5 secs)` `[dim, spinner]`
- text_delta → stop spinner, print text at column 0 `[no style]` - NO parentheses
- tool_call_requested (fast, <2 secs) → buffer; do NOT emit yet
- tool_call_finished (fast) → merge: `(name 'args', result)` `[dim]`
- tool_call_requested (slow, >2 secs) → `(running name 'args'...` `[dim, spinner]` - open paren
- tool_call_finished (slow) → `  Ns, N chars.)` `[dim]` - close paren on next line
- turn_finished → `(N.NK tokens, $X.XXX)` `[dim]` - natural language, parenthetical
- error (WARNING:) → `WARNING: message` `[yellow]` - NO parentheses, full width
- error (ERROR:) → `ERROR: message` `[red]` - NO parentheses, full width
- error (NOTICE:) → `(message)` `[dim]` - parenthetical
- checkpoint_created → `(compacted: N messages → M)` `[dim]`
- approval_required → `[action] details` `[bold]` - NO parentheses, prompt

**Grouping rules for fast sequential tools:**
When multiple tools complete in <2 secs each within the same turn, each tool gets its own parenthetical on a separate line:
```
(read 'src/parser.py', 234 chars)                        [dim]
(edit 'src/parser.py', OK)                               [dim]
```
Not merged into one set of parentheses - each tool is its own aside. This preserves the one-aside-per-tool invariant while keeping vertical compactness.

**Approach-specific decisions:**
- **Parentheses = metadata boundary**: Anything in `(...)` is secondary information. Anything WITHOUT parentheses is primary (model text, errors, approvals). This is a universal reading convention - readers naturally de-emphasize parenthetical content
- **Errors and approvals escape parentheses**: Warnings, errors, and approval prompts are NOT asides - they demand attention. Breaking the parenthetical pattern signals importance: `(tool result)` vs `WARNING: retry in 8 secs`
- **Natural language stats**: `(4.5K tokens, $0.003)` reads as prose, not data. Compare A's `[sys] in=4521 out=187 $0.003`. Less precise (4.5K vs 4521) but more scannable
- **Dim + parentheses = double encoding**: On monochrome terminals or in copy-pasted text, parentheses alone carry the structural signal. On color terminals, dim + parentheses reinforce each other
- **No category prefixes needed**: The parentheses themselves ARE the category signal. Everything inside `(...)` is metadata. The specific category (think/tool/system) is identifiable from content, not prefix

**Trade-offs**:
- PRO: Natural reading flow. The parentheses create a universal "secondary information" signal that works across cultures and contexts.
- PRO: Grouping fast tools on one line reduces vertical space without losing information.
- PRO: No jargon prefixes to learn. `(read 'src/parser.py', 234 chars)` is self-explanatory.
- PRO: Compact turn stats. `(4.5K tokens, $0.003)` is human-readable, not machine-formatted.
- CON: Parentheses use 2 characters per line that carry no information. Minor but real in a monospace terminal.
- CON: Multi-line asides (long tool names, long results) break the parenthetical pattern. The opening `(` on one line and closing `)` on the next is visually awkward.
- CON: Grouping fast tools requires buffering decisions - how long to wait before deciding tools are "done" and can be grouped? Adds state complexity.

**Implementation complexity**: MEDIUM. Requires reformatting all metadata output, adding tool-grouping logic, and handling multi-line parenthetical edge cases.

## 7. Approach E: Progressive Disclosure

**Philosophy**: Show only what the user asked for. Default view is pure content. Verbosity levels reveal layers of detail. Maps to CLEN-CARE-FROM combined with "Explorative over instructive" - the user chooses their depth.

**Design system principles applied**:
- "Explorative over instructive: users are free to explore on their own" (DLPHS-IN10 Section 11.5)
- "Offer simple, safe defaults while allowing depth for those who seek it" (DLPHS-IN10 Section 11.5)
- "One dominant message per view" (DLPHS-IN10 Section 1): Default view = pure content = one message

**Key decisions**:
- Three verbosity levels via CLI flag: default (content only), `--verbose` (content + tools), `--debug` (everything)
- Default: model text + errors + approval prompts. Spinner visible but ephemeral. No tool lines, no turn stats.
- Verbose: adds tool announce/result lines (dim) and turn stats (dim). Like approach B.
- Debug: adds thinking deltas, token details, timing breakdowns. Diagnostic-grade output.
- Spinner always present in default mode (>300ms rule) but text is minimal: just `thinking...` or `running...`

### 7.1 Preview: Default Mode

```
> fix the import error in parser.py

I'll read parser.py to find the import error.

Running tests to verify.

Fixed. Changed `json_parser` to `parser_core` on
line 3. All 12 tests pass.
```

### 7.2 Preview: Verbose Mode

```
> fix the import error in parser.py

  thinking... 5 secs                                  [dim, spinner]
I'll read parser.py to find the import error.
  read_file 'src/parser.py'  234 chars.                   [dim]
  edit 'src/parser.py'  OK.                               [dim]

  thinking... 3 secs                                  [dim, spinner]
Running tests to verify.
  run_command 'pytest tests/test_parser.py'...        [dim, spinner]
    12 secs  892 chars.                                   [dim]

Fixed. Changed `json_parser` to `parser_core` on
line 3. All 12 tests pass.
```

### 7.3 Preview: Debug Mode

```
> fix the import error in parser.py

  thinking... 5 secs                                  [dim, spinner]
  <reasoning about the import chain...>                   [dim]
I'll read parser.py to find the import error.
  [tool] read_file 'src/parser.py'...                     [dim]
    OK. 234 chars. (0.8 secs)                             [dim]
  [tool] edit 'src/parser.py'...                          [dim]
    OK. 1 char. (0.2 secs)                                [dim]
  Turn 1: in=4521 (cache 3800) out=187 | $0.003          [dim]

  thinking... 3 secs                                  [dim, spinner]
Running tests to verify.
  [tool] run_command 'pytest tests/test_parser.py'... [dim]
    running... 12 secs                                [dim, spinner]
    OK. 892 chars. (12.3 secs)                            [dim]
  Turn 2: in=5200 (cache 4800) out=94 | $0.004           [dim]

Fixed. Changed `json_parser` to `parser_core` on
line 3. All 12 tests pass.
  Turn 3: in=5800 (cache 5400) out=42 | $0.002           [dim]
```

### 7.4 Color and State Behavior

Approach E applies the same styles from Section 1.1 but gates visibility by verbosity level. Each level is a strict superset of the previous.

**Default mode** (content + spinner only):
- turn_started → `thinking...` `[dim, spinner]` - generic, no tool name
- thinking_delta → tick spinner elapsed
- text_delta → stop spinner, print text at column 0 `[no style]`
- tool_call_requested → `running...` `[dim, spinner]` - generic spinner, NO tool name
- tool_call_finished → stop spinner. No output
- turn_finished → No output
- error (WARNING:) → `WARNING: message` `[yellow]` - always visible
- error (ERROR:) → `ERROR: message` `[red]` - always visible
- error (NOTICE:) → No output (suppressed in default)
- checkpoint_created → No output
- approval_required → `[action] details` `[bold]`, prompt - always visible

**Verbose mode** (`--verbose`, adds to default):
- tool_call_requested → `  name 'args'...` `[dim]` - tool name now visible
- tool running >300ms → `  name 'args'...` `[dim, spinner]` - elapsed counter
- tool_call_finished → merge with announce if fast: `  name 'args'  result` `[dim]`
- error (NOTICE:) → `  message` `[dim]` - now visible
- checkpoint_created → `  Compacted: N messages → M` `[dim]`
- turn_finished → still suppressed (verbose = B-equivalent, B has no turn labels)

**Debug mode** (`--debug`, adds to verbose):
- thinking_delta → print dim text inline: `  <reasoning...>` `[dim]`
- tool_call_requested → `  [tool] name 'args'...` `[dim]` - prefix marker added
- tool_call_finished → `    OK. N chars. (Ns)` `[dim]` - with timing
- turn_finished → `  Turn N: in=N (cache N) out=N | $X.XXX` `[dim]` - full diagnostics

**Approach-specific decisions:**
- **Default spinner is GENERIC**: `thinking...` and `running...` without specifying what tool. The user sees activity but not detail. This is the cleanest possible output but violates LOG-GN-09 (Announce Before Blocking) because the user cannot tell WHAT is running during a 5-minute `run_command`
- **Verbose = Approach B equivalent**: When `--verbose` is active, the output matches Approach B's format. Merged tool lines, dim metadata, no turn stats. This makes B and E-verbose interchangeable
- **Debug = Approach A with timing**: When `--debug` is active, the output adds prefix markers (`[tool]`), timing breakdowns, and thinking deltas. More verbose than A because it includes per-operation elapsed time
- **Flag plumbing**: `--verbose` and `--debug` are CLI-level flags passed to `Renderer.__init__()`. The renderer's `handle()` method checks `self.verbosity` before emitting each line type. No per-event branching at the agent level
- **JSONL overlap**: Debug mode partially duplicates JSONL structured output. Justification: JSONL is for machine consumption (log analysis, replay). Debug mode is for human real-time monitoring in the terminal. Different audiences, same data

**Trade-offs**:
- PRO: Default mode is the cleanest possible output. 8 lines for 3 turns. Content only.
- PRO: Power users get full diagnostic detail with `--debug`. No information is permanently hidden.
- PRO: Maps directly to design system "safe defaults + depth for seekers" principle.
- PRO: Each level is independently useful: default for daily use, verbose for monitoring, debug for troubleshooting.
- CON: Default mode hides ALL tool activity. If a tool hangs for 5 minutes, the user sees only a spinner with no context about WHAT is running. Violates Announce Before Blocking (LOG-GN-09).
- CON: Three code paths in the renderer increase testing surface and bug potential.
- CON: Users must discover the `--verbose` flag. New users may think Lana is doing nothing during tool-heavy turns. Violates "always just works" principle.
- CON: The JSON Lines (JSONL) output mode already serves the "full detail" need. Adding `--debug` to the renderer partially duplicates that function.

**Implementation complexity**: MEDIUM. Verbosity flag plumbing through CLI, conditional rendering logic in handle(). No new Rich patterns.

## 8. Comparison

**Dimension: content prominence** (higher = model text stands out more)
- E default > C > B > D > A > E debug

**Dimension: forensic completeness** (higher = more context preserved in scrollback)
- A = E debug > B = D > E verbose > C > E default

**Dimension: implementation effort** (higher = more work)
- C >> D > E > A = B

**Dimension: design system alignment**
- A emphasizes "Clear, Engineered" (structure, order)
- B emphasizes "Calm, Relaxed" (non-distracting, quiet)
- C emphasizes "Fresh, Modern" (innovative terminal use)
- D emphasizes "Self-explanatory" + "Headlines are conclusions"
- E emphasizes "Explorative over instructive" + "Zero friction"

**Hybrid potential**: Approaches are not mutually exclusive. B's dim styling + D's parenthetical format + E's verbosity levels could combine. For example:
- Default mode with D-style parenthetical asides (compact, calm)
- Verbose mode adds B-style tool detail lines
- The "Live Footer" concept from C could be a future enhancement layered on top

## 9. Next Steps

1. **Choose 1-2 approaches** for SPEC: evaluate which best serves Lana's primary user (developer monitoring an agent)
2. **Write SPEC**: Define the chosen approach as functional requirements, design decisions, implementation guarantees
3. **Prototype**: Implement the chosen approach in render.py, verify with existing test suite
4. **Defer C (Live Footer)**: Worth exploring as a v2 enhancement after the basic styling is solid

## 10. Sources

- `LANAUSRX-IN03-SC-IN01`: `_INFO_LANAUSRX_INTERACTION_CHAIN.md [LANAUSRX-IN01]` - Dead-air phases, interaction categories, color scheme [VERIFIED]
- `LANAUSRX-IN03-SC-IN02`: `_INFO_LANAUSRX_CONSOLE_UX_ELEMENTS.md [LANAUSRX-IN02]` - Element inventory, compatibility, anti-patterns, Universal Spinner Pattern [VERIFIED]
- `LANAUSRX-IN03-SC-DLPH`: `specs/UXDesign/_INFO_DELPHIOS_DESIGN_SYSTEM.md [DLPHS-IN10]` - CLEN-CARE-FROM, 70/20/10, interaction philosophy, anti-patterns [VERIFIED]
- `LANAUSRX-IN03-SC-RNDR`: `src/lana/render.py` - Current renderer implementation baseline [VERIFIED]

## 11. Document History

**[2026-08-31 18:10]**
- Added: Section 1.1 CLI Color Map - shared category-to-Rich-style reference, 70/20/10 distribution, state transition diagram
- Added: Section 3.2 (Approach A) - event-to-output map with prefix markers, indent hierarchy, turn boundary behavior
- Added: Section 4.2 (Approach B) - merged tool line logic, spinner threshold rationale, positional stats format
- Added: Section 5.3 (Approach C) - dual-surface rendering model (scrollback vs footer), footer appearance spec, approval break-through rule
- Added: Section 6.2 (Approach D) - parenthetical formatting rules, double encoding rationale, error escape pattern, tool grouping invariant
- Added: Section 7.4 (Approach E) - three verbosity levels mapped to events, default/verbose/debug output specifications, flag plumbing design

**[2026-08-31 17:55]**
- Fixed: Timeline format (INFO-HD-03), expanded CLI/CLEN-CARE-FROM/JSONL acronyms (AP-PR-06)
- Fixed: Subsection headings to decimal notation (INFO-SN-02), standardized preview heading format (AP-PR-09)
- Fixed: Document History action prefix (INFO-FT-02)

**[2026-08-31 17:40]**
- Added: Initial document with 5 design approaches, ASCII previews, and comparison
