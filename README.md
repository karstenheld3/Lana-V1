# Lana

Lana is an AI coding assistant that runs in your terminal. You type requests, Lana reads your files, writes code, runs commands, and manages work sessions -- powered by OpenAI or Anthropic models.

Lana loads a **prompt system** called IPPS (rules, workflows, skills) that defines how it behaves: coding conventions to follow, workflows like `/prime` (load project context) or `/commit` (create git commits), and skills for specialized tasks. The prompt system ships with this project in the `.lana/` folder.

## Prerequisites

- **Python 3.12+** (`python --version` to check)
- **An API key** for at least one provider: [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com/settings/keys)

## Quick Start

```powershell
# 1. Install (editable mode, includes test dependencies)
pip install -e .[dev]

# 2. Set your API key (pick one or both)
$env:OPENAI_API_KEY = "sk-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# 3. Run
lana
```

On first run, Lana creates any missing configuration (`config/lana-config.json`, `config/.api-keys.txt` template, `.lana-data/` for sessions and logs) and reports what it created. No setup commands needed.

## What Lana Can Do

Once running, you interact by typing at the `>` prompt:

- **Free text** -- ask Lana to read code, fix bugs, write features, explain files
- **`/workflow`** -- invoke a workflow (e.g. `/prime` to load project context, `/commit` to create git commits, `/verify` to check work against specs)
- **`/help`** -- list all loaded workflows
- **`/cost`** -- show API spend for the current session
- **`/exit`** or **Ctrl+C** -- stop

Lana has 16 built-in tools: read/write/edit files, run shell commands, search code, manage todos, do web research, and more. Every destructive action (file writes, command execution) requires your approval in `manual` mode.

## Configuration

**`config/lana-config.json`** controls which AI models Lana uses and how it behaves:

- **`roles`** -- which model handles each task (generation, summarization, web search)
- **`agent_folder`** -- path to the prompt system (default: `.lana/`)
- **`execution_policy`** -- safety level for tool execution:
  - `manual` (default) -- every file write and command needs your approval
  - `auto` -- safe operations run automatically, destructive ones still ask
  - `turbo` -- everything runs automatically (use only in trusted workspaces)
- **`command_denylist`** -- commands that are always blocked (e.g. `rm`, `del`, `format`)

**API keys** resolve in order: environment variables (`OPENAI_API_KEY` / `ANTHROPIC_API_KEY`) first, then `config/.api-keys.txt`.

## Project Structure

```
.lana/              # prompt system (rules, workflows, skills) -- shipped with project
.lana-data/         # runtime data (sessions, debug logs) -- gitignored
config/             # model configuration, API keys, runtime settings
src/lana/           # source code
tests/              # test suite
specs/              # specifications and implementation plans
```

## CLI Reference

```powershell
lana                                    # interactive session (workspace = current directory)
lana --resume .lana-data/sessions/X.jsonl  # resume a previous session
lana --policy auto                      # override execution policy
lana --debug                            # write redacted API traffic to .lana-data/logs/
lana --show-thinking                    # show model reasoning (dim-styled)
lana --config path/to/config.json       # use a different config file
lana --acp                              # ACP mode (JSON-RPC over stdio, for IDE integration)
lana --version                          # print version and exit
lana -p "fix the bug in auth.py"        # headless: run one prompt and exit
lana -p "..." --output-format jsonl     # headless: output AgentEvents as JSON Lines
```

**Exit codes** (headless mode): 0 = completed, 2 = config error, 3 = provider/API failure, 4 = stopped without completion.

## Tests

```powershell
pytest                      # offline suite (~200 tests, no API keys needed)
pytest -m live              # live smoke tests (requires API keys, budget-capped)
```

## Distribution (Windows x64 Binary)

Build a standalone `lana.exe` that includes Python and all dependencies (no Python install required on the target machine):

```powershell
_InstallAndCompileDependencies.bat   # once: creates .venv
_ship.bat                            # builds dist\lana-{version}-win-x64.exe + SHA256SUMS.txt
```

- **Build requirements**: Rust toolchain + MSVC Build Tools (the script offers to install Rust), network access
- **Two modes**: `lana.exe` (interactive CLI) and `lana.exe --acp` (ACP agent for IDEs)
- **First run**: 1-5 minutes (extracts embedded Python, installs dependencies from PyPI -- requires network); subsequent starts take ~1.3 seconds
- **Interrupted first run**: local cache is broken -- fix with `lana.exe self restore` or delete `%LOCALAPPDATA%\pyapp\data\lana\`
- **Updates**: replace the `lana.exe` file
- **Code signing**: set `LANA_SIGN_THUMBPRINT` to an installed certificate thumbprint before running `_ship.bat`

## Specifications

- `specs/_SPEC_LANA_MVP-1.md [LANAAGNT-SP01]` -- CLI agent specification
- `specs/_SPEC_LANA_MVP-2_ACP.md [LANAACPB-SP01]` -- ACP protocol specification
- `_Sessions/_2026-08-30_LanaDistribution/_SPEC_LANADIST.md [LANADIST-SP01]` -- distribution pipeline specification
