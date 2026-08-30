# Lana MVP-1

CLI agent that runs a prompt system (rules, workflows, skills) with an agentic tool loop on OpenAI/Anthropic backends.

## Install

```powershell
pip install -e .[dev]
```

## Configure

Zero-setup: on first run Lana creates everything it needs - `config/lana-config.json` (default roles), the model config files, a keyless `config/.api-keys.txt` template, `.lana-data/sessions/`, and the `.lana/` prompt system (full default library bundled with the package) - and reports each created artifact. No init command. An existing `.lana/` folder is never modified.
Runtime configuration lives in `config/lana-config.json` (roles, agent folder, safety policy).
API keys resolve from environment variables (`OPENAI_API_KEY` / `ANTHROPIC_API_KEY`) first, then `config/.api-keys.txt`.

## Run

```powershell
lana                        # interactive session, workspace = current directory
lana --resume <session>     # resume a session JSONL file
lana --policy auto          # execution policy: manual | auto | turbo
lana --debug                # write redacted API traffic to .lana-data/logs/
lana --show-thinking        # stream model thinking dim-styled
lana -p "your prompt"       # headless single prompt (exit codes 0/2/3/4)
lana -p "..." --output-format jsonl   # stream AgentEvents as JSON Lines
```

## Chat

- Free text sends a user message
- `/name` invokes a loaded workflow (e.g. `/prime`)
- Built-ins: `/help`, `/cost`, `/exit`
- Ctrl+C cancels the current turn

## Tests

```powershell
pytest                      # offline suite (scripted adapter, no API keys)
pytest -m live              # live smoke tests (requires API keys)
```

## Distribution (Windows x64 binary)

Build the standalone `lana.exe` (no Python required on the target machine):

```powershell
_InstallAndCompileDependencies.bat   # once: creates .venv
_ship.bat                            # builds dist\lana-{version}-win-x64.exe + SHA256SUMS.txt
```

- Build machine needs the Rust toolchain (the script offers to install it) and network access
- The binary serves both modes: `lana.exe` (CLI) and `lana.exe --acp` (ACP client for IDEs)
- First run: 1-5 minutes (extracts embedded Python, installs dependencies from PyPI - network required); later starts are fast
- If the first run is interrupted, the local cache is broken - fix with `lana.exe self restore` or delete `%LOCALAPPDATA%\pyapp\data\lana\`
- Updates: download the new `lana.exe` and replace the file
- Signing: set `LANA_SIGN_THUMBPRINT` to an installed certificate thumbprint before running `_ship.bat`

## Specification

See `_2026-08-29_LanaV1DesignQuestions/_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` and `_Sessions/_2026-08-30_LanaDistribution/_SPEC_LANADIST.md [LANADIST-SP01]`.
