# Lana MVP-1

CLI agent that runs a prompt system (rules, workflows, skills) with an agentic tool loop on OpenAI/Anthropic backends.

## Install

```powershell
pip install -e .[dev]
```

## Configure

Zero-setup: on first run Lana creates everything it needs - `config/lana-config.json` (default roles), `.lana-data/sessions/`, and the `.lana/` prompt system scaffold - and reports each created artifact. No init command.
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

## Specification

See `_2026-08-29_LanaV1DesignQuestions/_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]`.
