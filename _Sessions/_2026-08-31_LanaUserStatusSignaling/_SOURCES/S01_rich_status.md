# S01: rich/status.py (Rich 15.0.0)

**Path**: `C:\Users\User\AppData\Local\Programs\Python\Python312\Lib\site-packages\rich\status.py`
**Accessed**: 2026-08-31

## Key Findings

- `Status` wraps `Live` (line 37): `self._live = Live(self.renderable, console=console, refresh_per_second=refresh_per_second, transient=True)`
- Default spinner is `"dots"` (line 17, 28)
- `update()` method (line 53): accepts `status`, `spinner`, `spinner_style`, `speed`. Does NOT acquire any lock.
- `start()` delegates to `self._live.start()` (line 87)
- `stop()` delegates to `self._live.stop()` (line 91)
