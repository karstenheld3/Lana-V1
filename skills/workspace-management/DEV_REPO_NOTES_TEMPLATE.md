<!-- DEV_REPO_NOTES TEMPLATE. Remove this comment after creating. -->

# NOTES

## Workspace Constants

[WORKSPACE_FOLDER]: `[current workspace root path]`
- Root folder of the workspace. All other paths compose from this.

[WORKSPACE_FILE]: `[WORKSPACE_FOLDER]\main.code-workspace`
- WORKSPACE mode only. Omit if SINGLE-PROJECT or MONOREPO.

<!-- Conditional: Omit the following constants for GENERAL workspaces (WS-CT-09). -->

[PRODUCT_REPO_FOLDER]: `[WORKSPACE_FOLDER]\..\[product-repo-name]`
- Product repository folder. In SINGLE-PROJECT mode, equals [WORKSPACE_FOLDER]. In WORKSPACE mode, may be outside [WORKSPACE_FOLDER].

[PRODUCT_SOURCE_FOLDER]: `[PRODUCT_REPO_FOLDER]\src`
- Source code folder. Applies to ProductRepo only.

[PRODUCT_DOCS_FOLDER]: `[PRODUCT_REPO_FOLDER]\docs`
- Product documentation folder.

[PRODUCT_VERSION]: `X.Y`
- Current product version. Format: `X.Y`, `X.Y.Z`, or `YYYY-MM-DD`. Used to compose version-dependent folder names and for release version extraction.

[DEV_KNOWLEDGE_FOLDER]: `[WORKSPACE_FOLDER]\knowledge`
- Knowledge bundles folder (synced from upstream in SYNCED repos).

[DEV_SPECS_FOLDER]: `[WORKSPACE_FOLDER]\specs`
- Specs folder containing shared specifications, design guidelines, SOPs.

[AGENT_FOLDER]: `[WORKSPACE_FOLDER]\.devin`
- Agent config folder. Sync target — copy of PromptSystem source content.

[SESSIONS_FOLDER]: `[WORKSPACE_FOLDER]\_PrivateSessions_gitignore`
- Base folder for session folders.

[SESSION_ARCHIVE_FOLDER]: `[SESSIONS_FOLDER]\..\Archive`
- Archive folder for closed sessions.

[SKILL_TOOLS_FOLDER]: `[WORKSPACE_FOLDER]\..\.tools\`
- Command line tools used by various PromptSystem skills. Shared across workspaces.

[API_KEYS_FILE]: `[SKILL_TOOLS_FOLDER]\.api-keys.txt`
- API keys file for skill scripts. Pass via `--keys-file [API_KEYS_FILE]`.

<!-- Conditional: Required for SYNCED only. Remove if SELF-CONTAINED. -->

[COMPANY_REPO_FOLDER]: `[WORKSPACE_FOLDER]\..\Company`
- Company repository folder (upstream source for knowledge and specs).

[KNOWLEDGE_SOURCE_FOLDER]: `[COMPANY_REPO_FOLDER]\knowledge`
- Upstream knowledge source. Sync target is [DEV_KNOWLEDGE_FOLDER].

[SPECS_SOURCE_FOLDER]: `[COMPANY_REPO_FOLDER]\specs`
- Upstream specs source. Sync target is [DEV_SPECS_FOLDER].

<!-- Release constants: Required for /project-release workflow. -->

[SOPS_FILE]: `SOPS.md`
- SOPS filename in workspace root.

[RELEASE_NOTES_FOLDER]: `[PRODUCT_DOCS_FOLDER]\ReleaseNotes`
- Release notes directory. Naming: `RELEASE_NOTES_v{VERSION}_{DATE}.md`.

<!-- Instructions:
- Replace [product-repo-name] with your product repository folder name
- Adjust [COMPANY_REPO_FOLDER] if your company folder is in a different location
- All paths should be relative to [WORKSPACE_FOLDER]
- [WORKSPACE_FILE] is the main.code-workspace file that defines which repos belong to the workspace
- Repos referenced in it may be physically outside [WORKSPACE_FOLDER] (e.g., ../ProductRepo)
- Omit [WORKSPACE_FILE] in SINGLE-PROJECT and MONOREPO modes
- Remove the SYNCED-only constants if your repo is SELF-CONTAINED (no external sync sources)
- [PROMPTSYSTEM_FOLDER] is repo-specific — compose as [WORKSPACE_FOLDER]\PromptSystem[PRODUCT_VERSION] in NOTES.md -->

<!-- Conditional: Remove this entire section if SELF-CONTAINED (no external sync sources). -->

## Sync Sources

### How Syncing Works

Sync configuration lives in `promptsystem-sync.json` at `[WORKSPACE_FOLDER]` root. This file defines:
- **Sources**: upstream repos to sync from (relative paths)
- **Bundles**: named content groups (e.g., `Windsurf`, `AI-Standards`) with include/exclude file patterns
- **never_overwrite**: glob patterns protecting local files from being overwritten or deleted
- **deprecated**: files that have been renamed or removed and should be cleaned up in targets

The `sync.ps1` script in `@skills:workspace-management` performs the actual sync. Always preview with `-diff` before executing.

### Sync Streams

Three content streams sync independently, each from its source to its target:

- **Prompt System**: `[promptsystem-source]\PromptSystem*` → `[AGENT_FOLDER]` — rules, workflows, skills
- **Knowledge**: `[KNOWLEDGE_SOURCE_FOLDER]` → `[DEV_KNOWLEDGE_FOLDER]` — reference documents by topic
- **Specs**: `[SPECS_SOURCE_FOLDER]` → `[DEV_SPECS_FOLDER]` — shared specifications and SOPs

### Usage Examples

Preview changes (no files modified):
```powershell
# Preview sync from a single source
& sync.ps1 -diff -sources "../MyDevRepo/PromptSystem1.0" -targets "." -configs "promptsystem-sync.json"

# Preview sync to a single target
& sync.ps1 -diff -sources "../MyDevRepo/PromptSystem1.0" -targets "../ProductRepo" -configs "promptsystem-sync.json"
```

Apply changes (copies, overwrites, deletes deprecated files):
```powershell
# Execute sync from a single source
& sync.ps1 -execute -sources "../MyDevRepo/PromptSystem1.0" -targets "." -configs "promptsystem-sync.json"

# Execute sync to multiple targets in one call
& sync.ps1 -execute -sources '["../MyDevRepo/PromptSystem1.0"]' -targets '["../ProductRepo", "../OtherRepo"]' -configs '["promptsystem-sync.json", "promptsystem-sync.json"]'
```

Or use the `/sync` workflow which wraps these commands:
- `/sync workspace` — preview and sync all streams from configured sources
- `/sync knowledge from source` — sync only knowledge bundles
- `/sync specs to targets` — push specs to downstream repos

<!-- Instructions:
- Adjust source paths in promptsystem-sync.json if your PromptSystem source or Company folder is in a different location
- All bundle definitions, filters, deprecated, and never_overwrite patterns are defined in promptsystem-sync.json
- See WSKMGMT-SP01 section 10 for the JSON schema -->

## Project Info

- Project name: [project-name]
- Project goal: [one-sentence-description]
- Workspace type: [SOFTWARE-DEV|GENERAL]
- Workspace mode: [SINGLE-PROJECT|MONOREPO|WORKSPACE] (omit if GENERAL)
- Version strategy: [SINGLE-VERSION|MULTI-VERSION] (omit if GENERAL)

<!-- Instructions: Replace placeholder values with your project information. -->

<!-- Conditional: Omit Build/Test, Runtime Environment, and Release Configuration for GENERAL workspaces (WS-CT-09). -->

## Build/Test Rules

- Build command: [build-command]
- Test command: [test-command]
- Lint command: [lint-command]

<!-- Instructions: Define commands for building, testing, and linting your product repo. -->

<!-- Conditional: Applies to ProductRepo only. DevRepo and CompanyRepo are exempt (no buildable source code). -->

## Runtime Environment

- Runtime: [node|bun|deno|python|rust|zig]
- Version file: [.nvmrc|.python-version|rust-toolchain.toml|build.zig.zon]
- Environment dir: [node_modules|.venv|target|zig-cache]
- Activate command: [n/a for rust/zig|.venv\Scripts\activate for python|fnm use for node]

<!-- Instructions:
- Every ProductRepo must use a local environment
- See LOCAL_ENVIRONMENTS.md in workspace-management skill for setup details
- Pin runtime version in a committed version file
- Gitignore the environment directory -->

<!-- Conditional: Omit for GENERAL workspaces. -->

## Release Configuration

<!-- Instructions:
- Configure for /project-release workflow
- All paths use workspace constants from ## Workspace Constants section above
- See _SPEC_RELEASE_PROJECT_WORKFLOW.md [RLSPROJ-SP01] for full config schema and decision guide -->

```
[RELEASE_CONFIG]
sops_file: [SOPS_FILE]
sessions_folder: [SESSIONS_FOLDER]
release_notes_dir: [RELEASE_NOTES_FOLDER]
release_notes_naming: RELEASE_NOTES_v{VERSION}_{DATE}.md
tag_annotation_template: Release {TAG}: {SUMMARY}

# Single-repo: one [RELEASE_REPO] block
# Multi-repo: product block first, then dev block(s)

[RELEASE_REPO: product]
path: [WORKSPACE_FOLDER]
role: product
tag_format: [date or semver]
version_source: [promptsystem_folder or pyproject_toml or package_json or none]
# version_file: [PRODUCT_REPO_FOLDER]\pyproject.toml  # Required when version_source is pyproject_toml or package_json
post_release_bump: [promptsystem_rename or patch_bump or minor_bump or none]
# binary_build: true     # Uncomment if product has a binary
# binary_path_pattern: dist/[appname]-{version}-win-x64.exe  # Required when binary_build is true
# version_gate: true     # Uncomment if version consistency check needed
# test_command: [command]  # Uncomment if tests not already defined in ## Build/Test Rules
github_release: true
# github_release_assets:  # Uncomment if binary assets to attach
#   - dist/[appname]-{version}-win-x64.exe

# [RELEASE_REPO: dev]    # Uncomment for multi-repo
# path: [WORKSPACE_FOLDER]
# role: dev
# tag_format: [date or semver]
# version_source: [promptsystem_folder or pyproject_toml or package_json or none]
# post_release_bump: [promptsystem_rename or patch_bump or minor_bump or none]
# test_command: [command]
# github_release: true
# github_release_notes: reference  # Dev repo references product release
```

<!-- Instructions:
- Replace placeholder values
- test_command lookup order: (1) [RELEASE_REPO] config, (2) ## Build/Test Rules section above, (3) skip
- If test_command already defined in Build/Test Rules, omit it from [RELEASE_REPO] config -->
