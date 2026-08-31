# S04: rich/style.py (Rich 15.0.0)

**Path**: `C:\Users\User\AppData\Local\Programs\Python\Python312\Lib\site-packages\rich\style.py`
**Accessed**: 2026-08-31

## Key Findings

- `Style.STYLE_ATTRIBUTES` dict (verified output):
  - `bold` (shorthand `b`)
  - `dim` (shorthand `d`)
  - `italic` (shorthand `i`)
  - `underline` (shorthand `u`)
  - `blink`
  - `blink2`
  - `reverse` (shorthand `r`)
  - `conceal` (shorthand `c`)
  - `strike` (shorthand `s`) - NOT `strikethrough`
  - `underline2` (shorthand `uu`)
  - `frame`
  - `encircle`
  - `overline` (shorthand `o`)

- `Style.parse("strikethrough")` raises `StyleSyntaxError: unable to parse 'strikethrough' as color; 'strikethrough' is not a valid color`
- Compound styles work: `Style.parse("bold dim")`, `Style.parse("reverse green")`, `Style.parse("white on blue")` all valid
