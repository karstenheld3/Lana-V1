# CLI (`ant`)

**Doc ID**: ANTAPI-IN46
**Goal**: Document the `ant` command-line interface for the Anthropic API
**API version**: anthropic-version 2023-06-01

**Depends on:**
- `_INFO_ANTAPI-03_INTRODUCTION.md [ANTAPI-IN03]` for base URL, auth headers
- `_INFO_ANTAPI-07_SDKS.md [ANTAPI-IN07]` for SDK overview

## Summary

The `ant` CLI provides command-line access to the Anthropic API. It supports shell scripting with typed flags, native integration with Claude Code, YAML-based API resource versioning, and access to all API features including Messages, Managed Agents, Files, and Batches. The CLI can be used standalone or alongside the Python SDK. Launched April 8, 2026.

## Key Facts

- **Command**: `ant`
- **Auth**: `ANTHROPIC_API_KEY` env var, or `ant auth login` (browser-based OAuth)
- **Output**: JSON (default), YAML, JSONL, pretty, raw, or interactive explorer TUI
- **Transforms**: GJSON paths via `--transform` to reshape output (like `jq`)
- **Input**: Flags, stdin (JSON/YAML), or `@file` references
- **Beta Access**: `ant beta:` prefix (auto-sends `anthropic-beta` header)
- **Profiles**: Named profiles for multi-workspace switching
- **Debugging**: `--debug` prints full HTTP request/response to stderr
- **Shell completion**: bash, zsh, fish, PowerShell
- **Status**: GA (launched April 8, 2026)

## Authentication

### API Key

Set `ANTHROPIC_API_KEY` environment variable, or pass `--api-key` per invocation. Override the API host with `ANTHROPIC_BASE_URL` or `--base-url`.

### Interactive Login (OAuth)

```bash
# Browser-based OAuth flow (stores credentials in $ANTHROPIC_CONFIG_DIR)
ant auth login

# Remote host without browser
ant auth login --no-browser

# Bind to specific workspace (skip browser picker)
ant auth login --workspace-id wrkspc_01...

# Create/use a named profile
ant auth login --profile staging
```

Token is scoped to the selected workspace. For CI/servers/containers, use Workload Identity Federation instead.

### Check Status

```bash
ant auth status
# Shows: credential source, active profile, workspace, config paths
```

### Multi-Workspace Profiles

```bash
# Create profile for another workspace
ant auth login --profile other-ws

# Activate profile as default
ant profile activate other-ws

# Use profile for single command
ant --profile other-ws models list
ANTHROPIC_PROFILE=other-ws ant models list

# Manage profiles
ant profile list
ant profile get --profile other-ws
ant profile set workspace_id wrkspc_01... --profile other-ws
```

Writable profile keys: `workspace_id`, `base_url`, `organization_id`, `scope`, `client_id`, `console_url`.

If `ANTHROPIC_API_KEY` is set, it overrides all profiles. Unset it before switching profiles.

### Logout

```bash
ant auth logout              # current profile
ant auth logout --all        # all profiles
```

## Command Structure

Commands follow `ant <resource>[:<subresource>] <action> [flags]`:

```bash
ant models list
ant messages create --model claude-opus-5 --max-tokens 1024 ...
ant beta:agents retrieve --agent-id agent_01...
ant beta:sessions:events list --session-id session_01...
```

Beta resources (agents, sessions, deployments, environments, skills) live under `beta:` and auto-send the appropriate `anthropic-beta` header. Use `--beta <header>` only to override.

Run `ant --help` for the full resource list. Append `--help` to any subcommand for its flags.

### Global Flags

- `--profile` / `ANTHROPIC_PROFILE` - Select named profile
- `--format` - Output format: `auto`, `json`, `jsonl`, `yaml`, `pretty`, `raw`, `explore`
- `--transform` - GJSON path to reshape output
- `-r` / `--raw-output` - Strip JSON quotes from string results (like `jq -r`)
- `--base-url` - Override API host
- `--debug` - Print full HTTP request/response to stderr (keys redacted)
- `--format-error` / `--transform-error` - Apply `--format`/`--transform` to error responses

## Quick Reference

```bash
# Send a message
ant messages create \
  --model claude-opus-5 \
  --max-tokens 1024 \
  --message '{role: user, content: "Hello, Claude"}'

# Create a managed agent (beta)
ant beta:agents create \
  --name "Coding Assistant" \
  --model '{id: claude-opus-5}' \
  --system "You are a helpful coding assistant." \
  --tool '{type: agent_toolset_20260401}'

# Create an environment (beta)
ant beta:environments create \
  --name "my-env" \
  --config '{type: cloud, networking: {type: unrestricted}}'

# List models
ant models list

# Upload a file
ant beta:files upload --file ./report.pdf
```

## Output Formats

`--format auto` (default) pretty-prints JSON for create/update commands. List/retrieve commands open the interactive explorer TUI when connected to a terminal, or fall back to pretty JSON when piped.

```bash
# YAML output
ant models retrieve --model-id claude-opus-5 --format yaml

# Interactive explorer (TUI with fold/search, arrow keys, / to search, q to exit)
ant models list --format explore
```

List endpoints auto-paginate. In `jsonl` mode, each item prints as one compact JSON object per line. In `yaml` mode, each item is a separate YAML document.

### GJSON Transforms

`--transform` reshapes responses using GJSON path syntax. For list endpoints, the transform runs per-item (not on the pagination envelope).

```bash
# Filter fields from a list
ant beta:agents list \
  --transform "{id,name,model}" \
  --format jsonl

# Extract a scalar into a shell variable
AGENT_ID=$(ant beta:agents create \
  --name "My Agent" \
  --model '{id: claude-sonnet-4-6}' \
  --transform id --raw-output)
printf '%s\n' "$AGENT_ID"
```

`--raw-output` strips JSON quotes (like `jq -r`). Distinct from `--format raw` which prints raw JSON bytes without auto-pagination.

## Passing Request Bodies

### Flags

Scalar fields map to flags. Structured fields accept relaxed YAML-like syntax or strict JSON:

```bash
ant beta:sessions create \
  --agent '{type: agent, id: agent_01..., version: 1}' \
  --environment-id env_01... \
  --title "CLI docs test session"
```

Repeatable flags build arrays (each `--tool` or `--event` appends one element):

```bash
ant beta:agents create \
  --name "Research Agent" \
  --model '{id: claude-opus-5}' \
  --tool '{type: agent_toolset_20260401}' \
  --tool '{type: custom, name: search_docs, input_schema: {type: object, properties: {query: {type: string}}}}'
```

### Stdin

Pipe JSON or YAML for the full request body. Fields from stdin merge with flags (flags take precedence):

```bash
# JSON via pipe
echo '{"description": "Updated agent.", "version": 1}' | \
  ant beta:agents update --agent-id "$AGENT_ID"

# YAML via heredoc (quote delimiter to disable variable expansion)
ant beta:agents create <<'YAML'
name: Research Agent
model: claude-opus-5
system: |
  You are a research assistant. Cite sources for every claim.
tools:
  - type: agent_toolset_20260401
YAML
```

### File References

`--file` accepts a bare path for upload commands. Prefix `@` to inline file contents into a string field:

```bash
# Upload a file
ant beta:files upload --file ./report.pdf

# Inline file contents into a system prompt
ant beta:agents create \
  --name "Researcher" --model '{id: claude-sonnet-4-6}' \
  --system @./prompts/researcher.txt

# Send a PDF via Messages API (auto base64-encodes binary files)
ant messages create \
  --model claude-opus-5 \
  --max-tokens 1024 \
  --message '{role: user, content: [
    {type: document, source: {type: base64, media_type: application/pdf, data: "@./scan.pdf"}},
    {type: text, text: "Extract the text from this document."}
  ]}' \
  --transform 'content.0.text' --raw-output
```

Use `@file://` for plain text, `@data://` for base64. Escape literal `@` with `\@`.

## Version-Controlling API Resources

Define agents, environments, and other resources as YAML files in your repo:

```yaml
# summarizer.agent.yaml
name: Summarizer
model: claude-sonnet-4-6
system: |
  You are a helpful assistant that writes concise summaries.
tools:
  - type: agent_toolset_20260401
```

```bash
# Create from YAML
ant beta:agents create < summarizer.agent.yaml

# Update (pass agent ID and current version)
ant beta:agents update \
  --agent-id agent_01... --version 1 \
  < summarizer.agent.yaml
```

Same pattern for environments:

```yaml
# summarizer.environment.yaml
name: summarizer-env
config:
  type: cloud
  networking:
    type: unrestricted
```

```bash
ant beta:environments create < summarizer.environment.yaml
ant beta:environments update \
  --environment-id env_01... \
  < summarizer.environment.yaml
```

Full session workflow:

```bash
# Start session
ant beta:sessions create \
  --agent agent_01... \
  --environment-id env_01... \
  --title "Summarization task"

# Send message
ant beta:sessions:events send \
  --session-id session_01... \
  --event '{type: user.message, content: [{type: text, text: "Summarize the benefits of type safety."}]}'

# Read conversation
ant beta:sessions:events list \
  --session-id session_01... \
  --transform 'content.0.text' --format auto --raw-output

# Stream events live
ant beta:sessions:events stream --session-id session_01...
```

## Scripting Patterns

```bash
# Chain: list agents, get first ID, list its versions
FIRST_AGENT=$(ant beta:agents list \
  --transform id --raw-output | head -1)
ant beta:agents:versions list \
  --agent-id "$FIRST_AGENT" \
  --transform "{version,created_at}" --format jsonl

# Inspect error messages
ant beta:agents retrieve --agent-id bogus \
  --transform-error error.message --format-error yaml 2>&1
```

## Claude Code Integration

Claude Code knows how to use `ant` out of the box. With the CLI installed and authenticated, ask Claude Code to operate on API resources directly:

- "List my recent agent sessions and summarize which ones errored."
- "Upload every PDF in ./reports to the Files API and print the resulting IDs."
- "Pull the events for session session_01... and tell me where the agent got stuck."

Claude Code shells out to `ant`, parses structured output, and reasons over results (no custom integration code required).

## Gotchas and Quirks

- Beta features use `ant beta:` prefix (auto-sends correct `anthropic-beta` header)
- Relaxed YAML syntax for structured flags: `'{key: value}'` (no quotes on keys)
- Repeatable flags (`--tool`, `--event`, `--message`) build arrays
- `--raw-output` strips JSON quotes; `--format raw` is different (prints raw bytes, no auto-pagination)
- `ANTHROPIC_API_KEY` overrides all profiles; unset it to use profile-based auth
- `ant auth login` tokens are workspace-scoped; use named profiles for multi-workspace
- `--debug` redacts API keys in output
- List endpoints auto-paginate; transforms run per-item, not on envelope
- `@file` in structured flag values needs quotes: `data: "@./file.pdf"`
- Shell completion available for bash, zsh, fish, PowerShell

## Related Endpoints

- `_INFO_ANTAPI-07_SDKS.md [ANTAPI-IN07]` - SDK overview (CLI listed alongside SDKs)
- `_INFO_ANTAPI-40_MANAGED_AGENTS.md [ANTAPI-IN40]` - Managed Agents (CLI support)
- `_INFO_ANTAPI-30_FILES_API.md [ANTAPI-IN30]` - Files API (`ant beta:files` commands)
- `_INFO_ANTAPI-12_BATCHES.md [ANTAPI-IN12]` - Batches API (`ant messages:batches` commands)

## Sources

- ANTAPI-SC-ANTH-CLI - https://platform.claude.com/docs/en/api/sdks/cli - CLI documentation

## Document History

**[2026-07-26]**
- Updated from Anthropic_API_2026-05-22
- Changed: Model references to claude-opus-5, SDK version to 0.120.0

**[2026-05-22]**
- Changed: Expanded from stub to full documentation based on official CLI docs
- Added: Authentication (OAuth login, API key, profiles, multi-workspace, logout)
- Added: Command structure, global flags, beta: prefix
- Added: Output formats (JSON/YAML/JSONL/explore TUI), GJSON transforms
- Added: Input methods (flags with relaxed YAML, stdin, @file references)
- Added: Version-controlling API resources (YAML definitions, create/update workflow)
- Added: Full session workflow (create/send/list/stream)
- Added: Scripting patterns (chaining, error inspection)
- Added: Claude Code integration
- Added: Expanded gotchas (14 items)

**[2026-05-22]**
- Initial documentation created from CLI documentation and release notes
