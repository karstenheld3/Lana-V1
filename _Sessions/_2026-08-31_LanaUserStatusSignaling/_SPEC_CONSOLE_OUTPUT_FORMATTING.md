# SPEC: Console Output Formatting

**Doc ID**: LANAUSRX-SP01
**Feature**: CONSOLE_FORMAT
**Goal**: Specify the visual layout, styling, and behavior of Lana's Command-Line Interface (CLI) console output during agent prompt execution
**Timeline**: Created 2026-08-31

**Target file(s):**
- `src/lana/render.py`

**Depends on:**
- `_INFO_LANAUSRX_INTERACTION_CHAIN.md [LANAUSRX-IN01]` for 12 AgentEvent types, 7 dead-air phases, 6 interaction categories
- `_INFO_LANAUSRX_CONSOLE_UX_ELEMENTS.md [LANAUSRX-IN02]` for element inventory, compatibility, anti-patterns
- `_INFO_LANA_CONSOLE_DESIGN_APPROACHES.md [LANAUSRX-IN03]` for design approach analysis (C selected with D/B elements)

**Does not depend on:**
- `_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` (ACP frontend has its own formatting)

## MUST-NOT-FORGET

- `markup=False` on every `console.print()` call (BG-0004). Styling via `style=` parameter only
- Any gap >300ms gets a spinner or status indicator (DLPHS-IN10 Section 16.2)
- Yellow = WARNING, red = ERROR. Never borrowed for other purposes
- Activity box uses American National Standards Institute (ANSI) cursor control, not Rich Live (zero Rich dependency)
- Hide cursor (`\033[?25l`) during activity box updates, show cursor (`\033[?25h`) on stop
- Word-wrap text to terminal width minus bracket prefix (2 chars)

## Table of Contents

1. [Scenario](#1-scenario)
2. [Context](#2-context)
3. [Domain Objects](#3-domain-objects)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Design Decisions](#6-design-decisions)
7. [Implementation Guarantees](#7-implementation-guarantees)
8. [Key Mechanisms](#8-key-mechanisms)
9. [Action Flow](#9-action-flow)
10. [UX Design](#10-ux-design)
    - 10.1-10.4: Component diagrams (OutputScope, ActivityBox, ApprovalBox, Error Messages)
    - 10.5-10.14: Interaction cases (11 scenarios)
    - 10.15: Color Reference
11. [Logging Requirements](#11-logging-requirements)
12. [Technical Constraints](#12-technical-constraints)
13. [Document History](#13-document-history)

## 1. Scenario

**Problem:** Lana's CLI output is a flat stream of unstyled text. Users cannot distinguish model text from metadata, have no real-time progress during tool operations, and lack visual hierarchy to separate prompts.

**Solution:**
- Bracket-scoped output per prompt with header (model, context, timestamp) and footer (turns, tool calls, cost, duration)
- Activity box that grows line-by-line during tool operations and collapses to a single summary line when done
- Three visual tiers: content (full brightness), metadata (dim), emphasis (color)
- Approval prompts in styled approval boxes with explicit option labels

**What we don't want:**
- Rich library dependency for the footer/activity box (ANSI escape codes suffice)
- Category prefixes on every line (`[tool]`, `[sys]`, `[think]`)
- Tool activity polluting permanent scrollback (tracked in ephemeral activity box, collapsed to summary)
- Emojis or ambiguous-width Unicode characters
- Responsive terminal reflow (standard scrollback mode; text wraps correctly at print time, past output stays fixed)

## 2. Context

This spec synthesizes Approach C (Live Footer) from `LANAUSRX-IN03` with elements from Approach D (parenthetical asides) and Approach B (quiet infrastructure). The prototype `proto_c_live_footer.py` validated the design through 5 demo scenarios covering all interaction types.

The current renderer (`render.py`) uses Rich Console with a status spinner. This spec replaces the rendering logic with ANSI-native output that uses only `sys.stdout.write()` for the activity box and cursor control, while retaining Rich Console for basic styled text output in the scrollback.

**Events not rendered by this spec:**
- `session_started` - Not rendered in CLI (session-file-only event)
- `thinking_delta` with `show_thinking=True` - Printed inline as dim text within bracket scope (existing behavior preserved, not changed by this spec)

## 3. Domain Objects

### OutputScope

An **OutputScope** is the visual bracket wrapping all output for a single prompt. One scope per `run_one_prompt()` invocation.

**Key properties:**
- `header` - Opening line: `┌─[ model | context% (of NM context) | timestamp ]`
- `body` - All output between header and footer, prefixed with `│ `
- `footer` - Closing line: `└─[ N turns | N tool calls | $X.XXX | N secs ]`

### ActivityBox

An **ActivityBox** is an ephemeral box-drawing bordered region that shows chronological activity during a turn. Grows line-by-line as activities happen. Collapses to a single summary line when the turn ends or model text begins.

**Key properties:**
- `log` - Completed activities with elapsed times (list of strings)
- `active_line` - Current activity with spinner and live elapsed counter
- `box_width` - Max of longest entry + 8 or 60 chars

**States:**
- GROWING: Box visible, new activities append as rows
- COLLAPSED: Box erased, single summary line emitted to scrollback

### ApprovalBox

An **ApprovalBox** is a permanent bold cyan box in scrollback for approval prompts.

**Key properties:**
- `header` - `┌─[ Approval ]───...───┐`
- `content` - Tool action and arguments
- `prompt` - `Approve? [ y = yes, n = no, a = all ]`
- `separator` - `├───...───┤`
- `answer_line` - `│ Answer: y = yes   │` (filled after user input)
- `bottom` - `└───...───┘`

## 4. Functional Requirements

**LANAUSRX-FR-01: Output Scope Brackets**
- Every prompt response wrapped in an OutputScope
- Header printed after the `> prompt` line
- Footer printed after all turns complete
- All lines between header and footer prefixed with `│ ` (bracket prefix, dim style)
- Empty line after header and before footer for breathing room

**LANAUSRX-FR-02: Header Content**
- Format: `┌─[ {model} | {context_pct}% (of {context_total} context) | {timestamp} ]`
- Model name from active provider config
- Context percentage = current token usage / max context window
- Timestamp in `YYYY-MM-DD HH:MM:SS` format
- Styled dim

**LANAUSRX-FR-03: Footer Content**
- Format: `└─[ {N} turn(s) | {N} tool call(s) | ${cost} | {duration} ]`
- Pluralization: "1 turn" vs "2 turns", "1 tool call" vs "2 tool calls"
- Duration in `format_duration()` format: "1 sec", "N secs"
- Styled dim

**LANAUSRX-FR-04: Activity Box Growth**
- On `turn_started`: create new activity box with "thinking..." as active line
- On `tool_call_requested`: freeze current activity to log, set new active line "running {name}..."
- On `tool_call_finished`: freeze current activity to log, set active line to "working..."
- Each log entry includes elapsed time: "thinking... 3 secs", "running read_file... 1 sec"
- Box redraws in-place via ANSI cursor-up. Box grows vertically as log entries accumulate
- Spinner (braille dots) animates on the active line only

**LANAUSRX-FR-05: Activity Box Collapse**
- On `text_delta` or `turn_finished`: erase the activity box from screen
- Emit a single dim summary line to scrollback: `  thinking... 3 secs -> running read_file... 1 sec -> running edit... 0 secs`
- Arrow separator ` -> ` between entries
- Clear log for next turn

**LANAUSRX-FR-06: Model Text Output**
- Printed at full brightness (no style) after bracket prefix
- Word-wrapped to terminal width minus bracket prefix length (2 chars)
- Continuation lines get bracket prefix
- Empty line between consecutive text blocks from different turns

**LANAUSRX-FR-07: Error Messages**
- WARNING: `│ WARNING: {message}` styled yellow. Empty line above
- ERROR: `│ ERROR: {message}` styled red. Empty line above
- NOTICE: Shown in activity box as temporary activity text, not in scrollback

**LANAUSRX-FR-08: Approval Box**
- Approval prompts rendered as ApprovalBox in scrollback (permanent)
- Styled bold cyan
- Empty line before and after the box
- Box opens, shows content and prompt, then separator, then waits for input on "Answer:" line
- After input, answer displayed, right border aligned, box closed

**LANAUSRX-FR-09: Checkpoint/Compaction**
- Shown in activity box: "compacted: {before} -> {after}"
- Not emitted to scrollback (ephemeral status only)

**LANAUSRX-FR-10: Cursor Visibility**
- Hide cursor (`\033[?25l`) whenever the activity box draws or updates
- Show cursor (`\033[?25h`) whenever the activity box stops or erases

## 5. Non-Functional Requirements

**LANAUSRX-NFR-01: Performance - Terminal Responsiveness**
- Activity box update must complete in <16ms (60fps equivalent) per frame
- No perceptible lag between event receipt and visual update

**LANAUSRX-NFR-02: Usability - Terminal Width Adaptation**
- Text wraps to current terminal width at print time (queried per text block)
- Activity box min width 60 chars. If terminal narrower than 64 chars, drop box borders and show inline
- Footer box adapts similarly

**LANAUSRX-NFR-03: Reliability - Non-Terminal Fallback**
- When `sys.stdout.isatty()` is False, skip all ANSI escape codes
- Activity box degrades to sequential print lines (no cursor control)
- Bracket prefix and header/footer still emitted as plain text

**LANAUSRX-NFR-04: Reliability - Cursor Restoration**
- If the process crashes or receives SIGINT (signal interrupt) during active activity box, cursor must be restored
- Register `atexit` handler and SIGINT handler to emit `\033[?25h`

## 6. Design Decisions

**LANAUSRX-DD-01:** ANSI escape codes instead of Rich Live for the activity box. Rationale: Proto C validated that 6 ANSI codes (`dim`, `bold`, `yellow`, `red`, `bold cyan`, `reset`) plus 3 cursor codes (`cursor up`, `clear line`, `hide/show cursor`) replace all Rich functionality needed. Eliminates render conflicts between Live and print.

**LANAUSRX-DD-02:** Bracket scope (OutputScope) wraps every prompt. Rationale: Visual grouping separates sequential prompts in scrollback. The `│ ` prefix creates a consistent left margin for all content. `┌─` and `└─` provide clear start/end boundaries.

**LANAUSRX-DD-03:** Activity box collapses to summary instead of persisting. Rationale: Tool operation details are ephemeral infrastructure. The collapsed summary provides enough forensic context ("thinking -> read_file -> edit") without polluting scrollback with full tool lines. Full detail available in JSON Lines (JSONL) log.

**LANAUSRX-DD-04:** Approval prompts use bold cyan ApprovalBox. Rationale: Cyan is the accent/primary color in the design system, distinct from severity colors (yellow, red) and metadata (dim). Bold cyan makes approvals visually prominent as the single "10% emphasis" element.

**LANAUSRX-DD-05:** 70/20/10 color distribution. Rationale: DLPHS-IN10 Section 3.7. 70% dim (activity box, header, footer, collapsed summaries), 20% default (model text), 10% emphasis (bold cyan approvals, yellow warnings, red errors).

**LANAUSRX-DD-06:** Terminal width queried per text block, not cached. Rationale: Users resize terminals during long operations. Each new text block wraps to the current width. Already-printed lines do not reflow (standard terminal behavior).

**LANAUSRX-DD-07:** Explicit option labels in approval prompts. Rationale: `[ y = yes, n = no, a = all ]` and `Answer: y = yes` are self-documenting. No ambiguity about what each key does.

## 7. Implementation Guarantees

**LANAUSRX-IG-01:** Every `sys.stdout.write()` call that includes ANSI style codes must end with `\033[0m` (reset) before the line terminator.

**LANAUSRX-IG-02:** Every `_draw_footer` / `_update_footer` call emits `\033[?25l` before writing lines and the corresponding `_erase_footer` / `_stop_footer` emits `\033[?25h`.

**LANAUSRX-IG-03:** Activity box cursor-up count always matches the actual number of lines previously written. The renderer tracks the rendered line count and uses `\033[{N}F` to move up exactly N lines.

**LANAUSRX-IG-04:** Bracket prefix `│ ` is prepended to every line emitted within an OutputScope, including activity box lines, text lines, error lines, and approval box lines.

**LANAUSRX-IG-05:** `markup=False` on every Rich `console.print()` call. No exceptions.

## 8. Key Mechanisms

### Activity Box ANSI Protocol

The activity box uses a 3-step cursor protocol:

1. **Draw**: Write N lines (top border, log entries, active line, bottom border). Record N as the rendered line count
2. **Update**: Emit `\033[{N}F` (cursor up N lines), then draw new lines (possibly N+1 if box grew). Clear orphan lines if count decreased
3. **Erase**: Emit `\033[{N}F`, write `\033[K\n` (clear line) N times, then `\033[{N}F` again to position cursor at the top of the cleared area

### Text Word-Wrapping

Text content is wrapped using `textwrap.wrap()` with `width = terminal_columns - len(prefix) - 1`. Each wrapped line gets the bracket prefix. Terminal width queried via `shutil.get_terminal_size()`.

### Activity Collapse

When collapsing, the renderer joins all log entries with ` -> ` and emits as a single dim line prefixed with `│   ` (bracket + 2-space indent). The summary reads left-to-right as a chronological chain.

## 9. Action Flow

```
User types prompt
├─> print("> {prompt}")
├─> print("┌─[ model | context | timestamp ]")   [dim]
├─> print("│")                                     [dim, empty line]
│
├─> turn_started
│   └─> ActivityBox starts: "thinking..."
│       ┌──────────────────────────────────────┐
│       │ ⠹ thinking...                        │
│       └──────────────────────────────────────┘
│
├─> tool_call_requested
│   └─> ActivityBox grows:
│       ┌──────────────────────────────────────┐
│       │ thinking... 3 secs                   │
│       │ ⠹ running read_file...               │
│       └──────────────────────────────────────┘
│
├─> text_delta
│   └─> ActivityBox collapses:
│       print("│   thinking... 3s -> read_file... 1s")  [dim]
│       print("│ {model text}")                          [no style]
│
├─> error (WARNING)
│   └─> pause ActivityBox, print warning, resume
│       print("│")                                       [dim, empty]
│       print("│ WARNING: {msg}")                        [yellow]
│
├─> approval_required
│   └─> ApprovalBox in scrollback:
│       print("│ ┌─[ Approval ]─────────┐")             [bold cyan]
│       print("│ │ run_command ...       │")             [bold cyan]
│       print("│ │ Approve? [y/n/a]     │")             [bold cyan]
│       print("│ ├──────────────────────┤")             [bold cyan]
│       input("│ │ Answer: ")                            [bold cyan]
│       print("│ └──────────────────────┘")             [bold cyan]
│
├─> All turns done
│   └─> print("│")                                       [dim, empty]
│       print("└─[ 3 turns | 5 tool calls | $0.009 | 23 secs ]")  [dim]
│       print()
```

## 10. UX Design

### 10.1 Component: OutputScope

The bracket scope wraps all output for one prompt. Header opens, footer closes.

**Header anatomy:**

```
> {user prompt}
┌─[ {model} | {context_pct}% (of {context_total} context) | {timestamp} ]   [dim]
│                                                                           [dim]
```

**Footer anatomy:**

```
│                                                                           [dim]
└─[ {N} turn(s) | {N} tool call(s) | ${cost} | {duration} ]                      [dim]
```

**Pluralization examples:**

```
└─[ 1 turn | 0 tool calls | $0.001 | 4 secs ]
└─[ 1 turn | 1 tool call | $0.003 | 8 secs ]
└─[ 3 turns | 5 tool calls | $0.009 | 23 secs ]
└─[ 2 turns | 12 tool calls | $0.041 | 1 min 12 secs ]
```

### 10.2 Component: ActivityBox

**Stage 1 - Initial (turn just started):**

```
│ ┌──────────────────────────────────────────────────────┐   [dim]
│ │ ⠹ thinking...                                        │   [dim, spinner]
│ └──────────────────────────────────────────────────────┘   [dim]
```

**Stage 2 - Growing (first tool requested):**

```
│ ┌──────────────────────────────────────────────────────┐   [dim]
│ │ thinking... 3 secs                                   │   [dim]
│ │ ⠹ running read_file...                               │   [dim, spinner]
│ └──────────────────────────────────────────────────────┘   [dim]
```

**Stage 3 - Growing (multiple tools):**

```
│ ┌──────────────────────────────────────────────────────┐   [dim]
│ │ thinking... 3 secs                                   │   [dim]
│ │ running read_file... 1 sec                           │   [dim]
│ │ running edit... 0 secs                               │   [dim]
│ │ ⠹ working...                                         │   [dim, spinner]
│ └──────────────────────────────────────────────────────┘   [dim]
```

**Stage 4 - Long-running tool (elapsed ticking):**

```
│ ┌──────────────────────────────────────────────────────┐   [dim]
│ │ thinking... 2 secs                                   │   [dim]
│ │ ⠹ running run_command... 12 secs                     │   [dim, spinner]
│ └──────────────────────────────────────────────────────┘   [dim]
```

**Collapsed summary (after box erased):**

```
│   thinking... 3 secs -> read_file... 1 sec -> edit... 0 secs              [dim]
```

**Collapsed summary (thinking only, no tools):**

```
│   thinking... 2 secs                                                       [dim]
```

**Collapsed summary (many tools, wraps to terminal width):**

```
│   thinking... 2 secs -> read_file... 1 sec -> grep_search... 1 sec ->     [dim]
│   edit... 0 secs -> run_command... 8 secs                                  [dim]
```

### 10.3 Component: ApprovalBox

**Anatomy (before user input):**

```
│                                                                             [dim]
│ ┌─[ Approval ]────────────────────────────────────────────────┐      [bold cyan]
│ │ run_command rm -rf build/ && make clean                      │      [bold cyan]
│ │ Approve? [ y = yes, n = no, a = all ]                       │      [bold cyan]
│ ├─────────────────────────────────────────────────────────────┤      [bold cyan]
│ │ Answer: _                                                   │      [bold cyan]
│                                                                 (cursor waiting)
```

**After approval (y = yes):**

```
│ ┌─[ Approval ]────────────────────────────────────────────────┐      [bold cyan]
│ │ run_command rm -rf build/ && make clean                      │      [bold cyan]
│ │ Approve? [ y = yes, n = no, a = all ]                       │      [bold cyan]
│ ├─────────────────────────────────────────────────────────────┤      [bold cyan]
│ │ Answer: y = yes                                             │      [bold cyan]
│ └─────────────────────────────────────────────────────────────┘      [bold cyan]
│                                                                             [dim]
```

**After denial (n = no):**

```
│ ┌─[ Approval ]────────────────────────────────────────────────┐      [bold cyan]
│ │ run_command rm -rf /important/data                           │      [bold cyan]
│ │ Approve? [ y = yes, n = no, a = all ]                       │      [bold cyan]
│ ├─────────────────────────────────────────────────────────────┤      [bold cyan]
│ │ Answer: n = no                                              │      [bold cyan]
│ └─────────────────────────────────────────────────────────────┘      [bold cyan]
│                                                                             [dim]
```

**After approve-all (a = all):**

```
│ ├─────────────────────────────────────────────────────────────┤      [bold cyan]
│ │ Answer: a = all                                             │      [bold cyan]
│ └─────────────────────────────────────────────────────────────┘      [bold cyan]
```

### 10.4 Component: Error Messages

**WARNING (yellow, empty line above):**

```
│
│ WARNING: Rate limit exceeded, retrying in 8 secs                       [yellow]
```

**ERROR (red, empty line above):**

```
│
│ ERROR: Edit failed: file is read-only (src/db.py)                         [red]
```

**NOTICE (activity box only, not in scrollback):**

```
│ ┌──────────────────────────────────────────────────────┐   [dim]
│ │ thinking... 5 secs                                   │   [dim]
│ │ ⠹ compacting context...                              │   [dim, spinner]
│ └──────────────────────────────────────────────────────┘   [dim]
```

### 10.5 Case: Pure Text Q&A (No Tools)

Single turn, thinking only, no tool calls.

```
> what does the config module do?
┌─[ claude-4-sonnet | 80% (of 0.2M context) | 2026-08-31 20:51:00 ]
│
│   thinking... 2 secs
│
│ The config module loads settings from lana-config.json at startup.
│ It validates required fields (model, provider, temperature) and
│ falls back to defaults for optional ones.
│
└─[ 1 turn | 0 tool calls | $0.001 | 4 secs ]
```

### 10.6 Case: Single Turn with Fast Tools

Tools complete quickly, collapsed summary shows chain.

```
> read the README and fix the typo on line 5
┌─[ claude-4-sonnet | 15% (of 0.2M context) | 2026-08-31 20:53:00 ]
│
│   thinking... 3 secs -> read_file... 0 secs -> edit... 0 secs
│
│ Fixed the typo on line 5: changed "recieve" to "receive".
│
└─[ 1 turn | 2 tool calls | $0.002 | 5 secs ]
```

### 10.7 Case: Multi-Turn with Tools, Approval, and Compaction

Full interaction: multiple turns, tool calls, approval gate, warning, compaction.

```
> fix the import error in parser.py
┌─[ claude-4-sonnet | 12% (of 0.2M context) | 2026-08-31 20:50:00 ]
│
│   thinking... 3 secs -> read_file... 1 sec -> edit... 0 secs
│
│ I'll read parser.py to find the import error.
│
│ WARNING: Token budget exceeded, compacted context
│
│ ┌─[ Approval ]────────────────────────────────────────────────┐
│ │ run_command rm -rf build/ && make clean                      │
│ │ Approve? [ y = yes, n = no, a = all ]                       │
│ ├─────────────────────────────────────────────────────────────┤
│ │ Answer: y = yes                                             │
│ └─────────────────────────────────────────────────────────────┘
│
│   thinking... 2 secs -> running pytest... 12 secs
│
│ Fixed. Changed `json_parser` to `parser_core` on line 3.
│ All 12 tests pass.
│
└─[ 3 turns | 5 tool calls | $0.009 | 23 secs ]
```

### 10.8 Case: Tool Failure, ERROR, Retry, Recovery

Tool fails, error printed, agent retries with different approach.

```
> refactor the database connection pooling
┌─[ claude-4-sonnet | 45% (of 0.2M context) | 2026-08-31 20:52:00 ]
│
│   thinking... 2 secs -> read_file... 1 sec -> read_file... 1 sec -> edit... FAIL
│
│ ERROR: Edit failed: file is read-only (src/db.py)
│
│   thinking... 1 sec -> run_command... 0 secs -> edit... 0 secs
│
│ Made the file writable and applied the refactoring. Connection
│ pooling now uses a shared pool with configurable max connections.
│
└─[ 2 turns | 6 tool calls | $0.007 | 11 secs ]
```

### 10.9 Case: Approval Denied

User denies a dangerous command. Agent proceeds without it.

```
> clean up all temporary files
┌─[ claude-4-sonnet | 30% (of 0.2M context) | 2026-08-31 20:54:00 ]
│
│   thinking... 2 secs
│
│ ┌─[ Approval ]────────────────────────────────────────────────┐
│ │ run_command rm -rf /tmp/project_* && rm -rf ~/.cache/lana   │
│ │ Approve? [ y = yes, n = no, a = all ]                       │
│ ├─────────────────────────────────────────────────────────────┤
│ │ Answer: n = no                                              │
│ └─────────────────────────────────────────────────────────────┘
│
│   thinking... 1 sec -> run_command... 0 secs
│
│ Understood. I cleaned only the project build artifacts instead.
│
└─[ 2 turns | 2 tool calls | $0.004 | 9 secs ]
```

### 10.10 Case: Long-Running Tool

A single tool dominates elapsed time. Activity box shows ticking counter.

```
> run the full test suite
┌─[ claude-4-sonnet | 55% (of 0.2M context) | 2026-08-31 20:55:00 ]
│
│   thinking... 1 sec -> running run_command... 45 secs
│
│ All 847 tests passed. No failures, 3 skipped.
│
└─[ 1 turn | 1 tool call | $0.003 | 48 secs ]
```

### 10.11 Case: Heavy Compaction with Many Tools

Large context triggers compaction mid-conversation.

```
> analyze all source files and create a dependency graph
┌─[ claude-4-sonnet | 92% (of 0.2M context) | 2026-08-31 20:56:00 ]
│
│   thinking... 3 secs -> read_file... 1 sec -> read_file... 0 secs ->
│   read_file... 1 sec -> read_file... 0 secs -> read_file... 1 sec ->
│   grep_search... 1 sec -> grep_search... 0 secs
│
│ I've analyzed the source tree. Here are the key dependencies:
│
│   thinking... 2 secs -> read_file... 0 secs -> read_file... 0 secs ->
│   read_file... 1 sec -> read_file... 0 secs
│
│ WARNING: Context 95% full, compacting to preserve conversation
│
│   thinking... 3 secs -> read_file... 1 sec -> read_file... 0 secs
│
│ The complete dependency graph shows 4 clusters with 2 circular
│ dependencies between agent.py and tools/__init__.py.
│
└─[ 3 turns | 17 tool calls | $0.041 | 38 secs ]
```

### 10.12 Case: Provider Retry with WARNING

Provider returns a retryable error. WARNING printed, then agent resumes.

```
> explain the caching strategy
┌─[ claude-4-sonnet | 40% (of 0.2M context) | 2026-08-31 20:57:00 ]
│
│   thinking... 2 secs
│
│ WARNING: Rate limit exceeded (429), retrying in 8 secs
│
│   thinking... 10 secs
│
│ The caching strategy uses prompt caching for the system prompt
│ and tool definitions, reducing input tokens by 60-80%.
│
└─[ 1 turn | 0 tool calls | $0.002 | 22 secs ]
```

### 10.13 Case: Consecutive Prompts in Session

Two prompts in sequence. Each gets its own OutputScope.

```
> what does the config module do?
┌─[ claude-4-sonnet | 10% (of 0.2M context) | 2026-08-31 20:58:00 ]
│
│   thinking... 2 secs
│
│ The config module loads settings from lana-config.json at startup.
│
└─[ 1 turn | 0 tool calls | $0.001 | 4 secs ]

> now add a validation for the "temperature" field
┌─[ claude-4-sonnet | 15% (of 0.2M context) | 2026-08-31 20:58:10 ]
│
│   thinking... 3 secs -> read_file... 1 sec -> edit... 0 secs
│
│ Added validation: temperature must be between 0.0 and 2.0.
│ Values outside this range now raise a ConfigError at startup.
│
└─[ 1 turn | 2 tool calls | $0.003 | 6 secs ]
```

### 10.14 Case: Non-Terminal Fallback

When `sys.stdout.isatty()` is False (piped output, CI). No ANSI codes, no activity box animation, no cursor control. Bracket prefix and structure preserved as plain text.

```
> fix the import error in parser.py
┌─[ claude-4-sonnet | 12% (of 0.2M context) | 2026-08-31 20:50:00 ]
│
│   thinking... 3 secs -> read_file... 1 sec -> edit... 0 secs
│
│ I'll read parser.py to find the import error.
│
│   thinking... 2 secs -> running pytest... 12 secs
│
│ Fixed. Changed `json_parser` to `parser_core` on line 3.
│ All 12 tests pass.
│
└─[ 3 turns | 5 tool calls | $0.009 | 23 secs ]
```

Note: Identical to terminal output after collapse. The activity box GROWING state is never shown; only collapsed summaries appear.

### 10.15 Color Reference

- **Dim** (`\033[2m`): Header, footer, bracket prefix, activity box, collapsed summaries
- **No style**: Model text content
- **Yellow** (`\033[33m`): WARNING messages
- **Red** (`\033[31m`): ERROR messages
- **Bold cyan** (`\033[1;36m`): Action box borders and content
- **Bold** (`\033[1m`): Title line only

## 11. Logging Requirements

**User-Facing (UF) applies.**

- **Audience**: Developer monitoring agent execution in terminal
- **Goal**: Know what the agent is doing, how long it takes, and what it costs
- **Key operations**: prompt execution, tool calls, approval gates, context compaction

## 12. Technical Constraints

- ANSI escape codes require a terminal (`sys.stdout.isatty()`). Non-terminal mode must fall back to plain text
- Activity box cursor-up assumes no other process writes to stdout between draw and update. Interleaved output corrupts positioning
- `shutil.get_terminal_size()` returns a default (80, 24) when terminal size cannot be determined
- Braille spinner characters (braille pattern dots in the U+2800 block, e.g. U+280B, U+2839) are safe in all modern terminal emulators. Not monospace-safe on legacy terminals; degrade to single character width
- Windows Terminal, PowerShell 7, and Windows ConHost all support the required ANSI sequences. Legacy cmd.exe requires `os.system('')` or `colorama.init()` to enable ANSI processing

## 13. Document History

**[2026-08-31 20:58]**
- Added: Section 10 expanded from 4 to 15 subsections
- Added: Component diagrams for OutputScope (header/footer anatomy, pluralization), ActivityBox (4 growth stages, 3 collapse variants), ApprovalBox (before input, 3 answer states), Error Messages (WARNING, ERROR, NOTICE)
- Added: 10 interaction case diagrams: fast tools, approval denied, long-running tool, heavy compaction, provider retry, consecutive prompts, non-terminal fallback

**[2026-08-31 20:56]**
- Fixed: Expanded acronyms on first use (ANSI, JSONL, SIGINT)
- Fixed: Terminology consistency - "footer box" replaced with "activity box" in MNF section
- Fixed: Removed implementation variable name `_footer_line_count` from Key Mechanisms and IG-03
- Fixed: Braille character range claim (was "U+280B through U+280F", now correct block reference)
- Fixed: Replaced ambiguous-width `↕` character with `---` in UX diagram
- Added: Events not rendered (session_started, thinking_delta with show_thinking)
- Added: JSONL acronym expansion

**[2026-08-31 20:52]**
- Initial specification created from prototype validation and LANAUSRX-IN03 design analysis
