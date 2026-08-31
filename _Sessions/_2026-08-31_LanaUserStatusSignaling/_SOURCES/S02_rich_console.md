# S02: rich/console.py (Rich 15.0.0)

**Path**: `C:\Users\User\AppData\Local\Programs\Python\Python312\Lib\site-packages\rich\console.py`
**Accessed**: 2026-08-31

## Key Findings

- `Console.print()` parameters: `markup=False` skips `render_markup()`, creates plain `Text()`. `style=` applies via `Segment.apply_style()`.
- `Console.width` property: returns `self.size.width` (int, columns)
- `Console.log()`: wraps content in `_log_render()` with `log_time=self.get_datetime()` - adds timestamps
- `Console.status()`: factory method, creates and returns `Status(status, console=self, ...)`
- `Console.set_live(live)`: appends to `_live_stack`, returns `len(self._live_stack) == 1`. Supports NESTING, not mutual exclusion.
- `Console.clear_live()`: pops from `_live_stack`
- `is_terminal` property: checks `isatty()`, `FORCE_COLOR`, `TTY_COMPATIBLE` env vars
- `JustifyMethod = Literal["default", "left", "center", "right", "full"]`
- `render_str()` with `markup=False`: `rich_text = Text(text, justify=justify, overflow=overflow, style=style)` - no markup parsing
