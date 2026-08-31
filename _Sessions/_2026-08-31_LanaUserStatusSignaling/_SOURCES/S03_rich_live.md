# S03: rich/live.py (Rich 15.0.0)

**Path**: `C:\Users\User\AppData\Local\Programs\Python\Python312\Lib\site-packages\rich\live.py`
**Accessed**: 2026-08-31

## Key Findings

- `_RefreshThread`: daemon thread calling `live.refresh()` at `refresh_per_second` rate, uses `self.live._lock` (RLock)
- `Live.start()`: calls `console.set_live(self)`. If returns False (not first in stack), sets `_nested = True` and returns early without cursor management or refresh thread
- `Live.stop()`: calls `console.clear_live()`. Nested instances just print their renderable, no cursor restore
- `Live.renderable` property: if `self is live_stack[0]`, renders `Group(*[live.get_renderable() for live in live_stack])` - ALL stacked Live instances are composed
- `Live.process_renderables()`: inserts cursor position control + live render. Only active for `is_interactive` consoles
- `Live._lock`: RLock used in `refresh()`, `start()`, `stop()`, `update()` for terminal output thread safety
