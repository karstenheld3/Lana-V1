# Lana

Lana is an ACP-compatible AI agent that runs in your terminal. You type requests, Lana reads your files, writes code, runs commands, and manages work sessions -- powered by OpenAI or Anthropic models.

Lana uses a **prompt system** called [IPPS](https://github.com/karstenheld3/IPPS) (rules, workflows, skills) that defines how it behaves: coding conventions to follow, workflows like `/prime` (load project context) or `/commit` (create git commits), and skills for specialized tasks. The prompt system ships with this project in the `.lana/` folder.

## Prerequisites

- **Windows x64** -- Lana currently targets Windows only (shell commands, binary distribution, path handling)
- **Python 3.12+** (`python --version` to check)
- **An API key** for at least one provider: [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com/settings/keys)

## Quick Start

```powershell
# 1. Install (editable mode, includes test dependencies)
pip install -e .[dev]

# 2. Run
lana
```

On first run, Lana creates `config/.api-keys.txt` (and `config/lana-config.json`, `.lana-data/`). Open the key file and uncomment your provider(s):

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Why a key file instead of environment variables?** Environment variables are global to the user session -- every process can read them, including other tools, extensions, or scripts that happen to run alongside Lana. `config/.api-keys.txt` is read only by Lana's own startup code and is gitignored by default, so keys stay scoped to this workspace and never leak into child processes or other applications. If both exist, the environment variable wins per provider -- useful for temporary CI overrides. The startup banner shows where each key came from (`env` or `.api-keys.txt`).

## What Lana Can Do

Once running, you interact by typing at the `>` prompt:

- **Free text** -- ask Lana to read code, fix bugs, write features, explain files
- **`/workflow`** -- invoke a workflow (e.g. `/prime` to load project context, `/commit` to create git commits, `/verify` to check work against specs)
- **Web research** -- Lana can search the web and read URLs to gather information, powering workflows like `/deep-research` and `/research`
- **Session resume** -- every session is saved as a JSONL file; pick up where you left off with `--resume`
- **Headless automation** -- run a single prompt (`-p "..."`) or a [queue of prompts](docs/PROMPT_FILE_FORMAT.md) (`--prompt-file`) for scripted workflows and CI pipelines
- **`/selftest`** -- verify environment health: config, prompt system, model connectivity
- **`/help`** -- list all loaded workflows
- **`/cost`** -- show API spend for the current session
- **`/exit`** or **Ctrl+C** -- stop

Lana has 16 built-in tools: read/write/edit files, run shell commands, search code, manage todos, do web research, and more. Every destructive action (file writes, command execution) requires your approval in `manual` mode. Lana automatically manages context length via checkpoint compaction -- long sessions work without manual intervention.

## Configuration

**`config/lana-config.json`** controls which AI models Lana uses and how it behaves:

- **`roles`** -- which model handles each task (generation, summarization, web search)
- **`agent_folder`** -- path to the prompt system (default: `.lana/`)
- **`execution_policy`** -- safety level for tool execution:
  - `manual` (default) -- every file write and command needs your approval
  - `auto` -- safe operations run automatically, destructive ones still ask
  - `turbo` -- everything runs automatically (use only in trusted workspaces)
- **`command_denylist`** -- commands that are always blocked (e.g. `rm`, `del`, `format`)

**API keys** resolve in order: environment variables (`OPENAI_API_KEY` / `ANTHROPIC_API_KEY`) first, then `config/.api-keys.txt`. The key file is recommended (see Quick Start).

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
lana --prompt-file PROMPTS.md           # headless: run a queue of prompts in one session
```

**Exit codes** (headless mode): 0 = completed, 2 = config error, 3 = provider/API failure, 4 = stopped without completion.

See [Prompt Queue File Format](docs/PROMPT_FILE_FORMAT.md) for the `--prompt-file` input format and [Standard Operating Procedures](SOPS.md) for versioning, building, and releasing.

## Tests

```powershell
pytest                      # offline suite (~280 tests, no API keys needed)
pytest -m live              # live smoke tests (requires API keys, budget-capped)
```

## Distribution (Windows x64 Binary)

Build a standalone `lana.exe` that includes Python and all dependencies (no Python install required on the target machine):

```powershell
_InstallAndCompileDependencies.bat   # once: creates .venv
_ship.bat                            # bumps version in pyproject.toml based on commit types
_build.bat                           # builds dist\lana-{version}-win-x64.exe + SHA256SUMS.txt
```

Then run `/project-release` to create release notes, tag the repo, and publish a GitHub release with the binary attached.

**Pipeline order matters**: ship (bump version) before build (so the binary carries the new version).

- **Build requirements**: Rust toolchain + MSVC Build Tools (the script offers to install Rust), network access
- **Two modes**: `lana.exe` (interactive CLI) and `lana.exe --acp` (ACP agent for IDEs)
- **First run**: 1-5 minutes (extracts embedded Python, installs dependencies from PyPI -- requires network); subsequent starts take ~1.3 seconds
- **Interrupted first run**: local cache is broken -- fix with `lana.exe self restore` or delete `%LOCALAPPDATA%\pyapp\data\lana\`
- **Updates**: replace the `lana.exe` file
- **Code signing**: set `LANA_SIGN_THUMBPRINT` to an installed certificate thumbprint before running `_build.bat`

## ACP Integration (Devin Desktop)

Lana can run as an ACP agent inside [Devin Desktop](https://devin.ai/download) (or Devin Next). The IDE spawns `lana.exe --acp` as a subprocess and communicates via JSON-RPC over stdio.

**Setup:**

1. Add Lana to the local ACP registry. Use `Ctrl+Shift+P` > **`Open Local ACP Registry Config`** to create/open the file at the correct path. On Windows both Devin Desktop and Next share `%APPDATA%\Code\User\acp\registry.json`; on macOS/Linux the paths are per-channel (`~/.windsurf/acp/` or `~/.windsurf-next/acp/`):

```json
{
  "version": "1.0.0",
  "agents": [
    {
      "id": "lana",
      "name": "Lana",
      "version": "1.1.0",
      "description": "CLI agent running IPPS prompt system on OpenAI/Anthropic backends",
      "authors": ["Karsten Held"],
      "license": "proprietary",
      "distribution": {
        "binary": {
          "windows-x86_64": {
            "archive": "",
            "cmd": "C:/path/to/lana.exe",
            "args": ["--acp"]
          }
        }
      }
    }
  ],
  "extensions": []
}
```

2. Restart Devin Desktop (or run `Reload ACP Connections` from the Command Palette)
3. Open `Ctrl+Shift+P` > **Devin User Settings** > **Agents** tab > enable **Lana**
4. Start a new conversation and select **Lana** from the agent selector

**Notes:**
- `cmd` must be an absolute path to the `.exe` binary -- Devin Desktop does not download from `archive` URLs and cannot spawn `.bat` files
- To open the debug console alongside ACP, add `"--debug-console"` before `"--acp"` in the `args` array
- Configure API keys for Lana via the `...` button next to the agent in the Agents tab, or place keys in `config/.api-keys.txt` relative to the workspace
- See [SOP 7](SOPS.md#sop-7-register-lana-as-acp-agent) for the full step-by-step procedure and troubleshooting

## Specifications

- [`_SPEC_LANA_MVP-1.md`](specs/_SPEC_LANA_MVP-1.md) [LANAAGNT-SP01] -- CLI agent specification
- [`_SPEC_LANA_MVP-2_ACP.md`](specs/_SPEC_LANA_MVP-2_ACP.md) [LANAACPB-SP01] -- ACP protocol specification
- [`_SPEC_LANADIST.md`](_Sessions/_2026-08-30_LanaDistribution/_SPEC_LANADIST.md) [LANADIST-SP01] -- distribution pipeline specification
