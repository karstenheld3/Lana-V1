# PROBLEMS: LANAAGNT-BG-0004 RendererMarkupInjection

**Doc ID**: LANAAGNT-BG-0004
**Goal**: Track and fix untrusted text being parsed as rich markup in the renderer

### LANAAGNT-BG-0004 Renderer parses model/tool text as rich markup - silent corruption and MarkupError crash

**Status**: Resolved
**Reported**: 2026-08-30 03:50 (found by /bugfix discovery-mode adversarial review)
**Resolved**: 2026-08-30 03:58
**Solution**: markup=False on every console.print carrying event payload text; inline [dim]/[red] tags replaced with style= parameters. BEFORE: 3 LOST + 1 CRASH of 5 repro cases; AFTER: 5/5 verbatim. Regression tests `test_bg0004_*` added; backup in `backup/render.py`

**Verbatim reproduction** (`.tmp_repro_markup.py`):
````
LOST  text_delta markdown link: output='See (https://example.com) for details'      <- "[the docs]" swallowed
LOST  text_delta bold-like: output='this is from the model literally'               <- "[bold]" tags swallowed
CRASH text_delta closing tag mismatch: MarkupError: closing tag '[/end]' at position 13 doesn't match any open tag
LOST  tool error with brackets: output="ERROR: Invalid arguments for 'x': unknown parameter ''"
````

**Initial assessment**: `Renderer.handle` passes untrusted text (assistant text deltas, thinking deltas, tool error results) to `rich.Console.print` with markup parsing enabled. Any bracketed content - Markdown links `[text](url)`, array indexing `x[/end]`-like sequences, PowerShell output - is either silently deleted or raises `MarkupError`, killing the render loop mid-turn. BG-0001's fix pattern (markup=False) was applied only to the two lines that failed tests then; the untrusted-text lines were missed.

**Root cause**: rich markup is enabled by default on `Console.print`; only trusted static format strings may use it. Untrusted event payloads (model output, tool results, provider error messages) must always render with `markup=False`.

**Impact assessment**:
- `src/lana/render.py` - only file constructing rich output (fix location, all `handle` branches)
- Consumers: interactive REPL + headless text mode (`run_one_prompt` -> renderer); jsonl mode unaffected (no rich)
- Tests touching rendered text: `tests/test_render.py` (asserts plain strings - unaffected by markup=False), `tests/test_e2e_offline.py` TC-46 transcript assertions (plain strings - unaffected)
- SPEC section 12 log format: unchanged (visual output identical for bracket-free text)

**Reproduce-before-fix**: CONFIRMED on current code (output above, exit 0 with CRASH line)

**Fix plan** (small, single-cycle):
1. Backup `render.py` to `backup/`
2. Set `markup=False` on every `console.print` carrying event payload text; replace inline `[dim]`/`[red]` tags with `style=` parameters
3. Regression test: bracketed link + `[/end]` crash case + bracketed tool error render verbatim
4. Full suite green -> commit `fix(LANAAGNT-BG-0004): ...`
