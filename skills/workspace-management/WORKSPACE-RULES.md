# Workspace Management Rules

Verifiable rules for workspace setup and integrity.

## Rule Index

Files (FL)
- WS-FL-01: DevRepo must contain required tracking files
- WS-FL-02: ProductRepo must contain README.md
- WS-FL-03: CompanyRepo must contain NOTES.md if it exists
- WS-FL-04: ID-REGISTRY.md Project Topics must have inline datestamps

Constants (CT)
- WS-CT-01: DevRepo NOTES.md must define all required workspace constants
- WS-CT-02: Constants must not contain hardcoded project-specific paths
- WS-CT-03: Constants must use [WORKSPACE_FOLDER] as base where applicable
- WS-CT-04: [WORKSPACE_FOLDER] and [WORKSPACE_FILE] must not be conflated
- WS-CT-05: Projects must use local environments by default
- WS-CT-06: Synced repos must have promptsystem-sync.json at [WORKSPACE_FOLDER] root
- WS-CT-08: Release Configuration conditional on workspace type
- WS-CT-09: GENERAL workspaces must omit dev-only constants and sections

Structure (ST)
- WS-ST-01: Agent folder must contain specs/, workflows/, skills/ subfolders
- WS-ST-02: Workspace structure must match declared mode
- WS-ST-04: No deprecated files in agent folder

Sync (SY)
- WS-SY-01: promptsystem-sync.json source paths must be relative
- WS-SY-02: promptsystem-sync.json must define source, selected_bundles, bundles, include, exclude, deprecated, never_overwrite per source entry
- WS-SY-03: never_overwrite files must not be overwritten or deleted during sync
- WS-SY-04: last_sync timestamp must be updated after successful execute
- WS-SY-05: Source repo is read-only during downstream sync

Templates (TM)
- WS-TM-01: Templates must use _TEMPLATE suffix
- WS-TM-02: Templates must follow TEMPLATE_RULES.md
- WS-TM-03: Templates must mark required vs optional sections
- WS-TM-04: Template annotations must use XML comments

Privacy (PR)
- WS-PR-01: No real identifiers, project names, or paths in skill files
- WS-PR-02: No real identifiers in template examples or placeholder values

## WS-FL-01: Required DevRepo Files

DevRepo must contain:
- NOTES.md
- PROBLEMS.md
- PROGRESS.md
- ID-REGISTRY.md
- SOPS.md
- FAILS.md

BAD: DevRepo missing ID-REGISTRY.md - workspace IDs cannot be tracked
GOOD: All 6 required files present in DevRepo root

## WS-CT-01: Required Workspace Constants

DevRepo NOTES.md must define all required workspace constants:
- Always required (all types): [WORKSPACE_FOLDER], [DEV_KNOWLEDGE_FOLDER], [DEV_SPECS_FOLDER], [AGENT_FOLDER], [SESSIONS_FOLDER], [SESSION_ARCHIVE_FOLDER], [SKILL_TOOLS_FOLDER], [API_KEYS_FILE]
- Required for SOFTWARE-DEV only: [PRODUCT_REPO_FOLDER], [PRODUCT_SOURCE_FOLDER], [PRODUCT_DOCS_FOLDER], [PRODUCT_VERSION], [SOPS_FILE]
- Required for SYNCED only: [COMPANY_REPO_FOLDER], [KNOWLEDGE_SOURCE_FOLDER], [SPECS_SOURCE_FOLDER]
- Required for WORKSPACE mode only: [WORKSPACE_FILE]
- Repo-specific (not in template): [PROMPTSYSTEM_FOLDER] — compose as `[WORKSPACE_FOLDER]\PromptSystem[PRODUCT_VERSION]`
- SELF-CONTAINED repos pass without sync source constants
- GENERAL repos pass without SOFTWARE-DEV-only constants (WS-CT-09)

BAD: NOTES.md defines [DEV_KNOWLEDGE_FOLDER] but not [KNOWLEDGE_SOURCE_FOLDER] (SYNCED repo) - sync cannot find source
GOOD: All required constants defined with paths relative to [WORKSPACE_FOLDER]

## WS-CT-02: No Hardcoded Project Paths

Constants must use [WORKSPACE_FOLDER] as base, not absolute paths.

BAD: [PRODUCT_REPO_FOLDER]: e:\Dev\MyProject
GOOD: [PRODUCT_REPO_FOLDER]: [WORKSPACE_FOLDER]\..\MyProject

## WS-CT-04: [WORKSPACE_FOLDER] vs [WORKSPACE_FILE] Distinction

[WORKSPACE_FOLDER] is the filesystem path of the workspace root. [WORKSPACE_FILE] is the main.code-workspace file that defines workspace membership. These must not be conflated.

- [WORKSPACE_FOLDER]: always present, the directory path
- [WORKSPACE_FILE]: only in WORKSPACE mode, the .code-workspace file
- Repos referenced in [WORKSPACE_FILE] may be physically outside [WORKSPACE_FOLDER]
- Commit scope in WORKSPACE mode = repos in [WORKSPACE_FILE], not repos inside [WORKSPACE_FOLDER]
- DevRepo NOTES.md should define [WORKSPACE_FILE] in WORKSPACE mode, omit in SINGLE-PROJECT/MONOREPO

BAD: Filtering commit scope by repos whose .git is inside [WORKSPACE_FOLDER] - excludes ProductRepo at ../ProductRepo
GOOD: Commit scope = repos referenced in [WORKSPACE_FILE], regardless of physical location

## WS-CT-05: Local Environments by Default

Every **source-code repo** (typically ProductRepo) must use a local runtime environment. No global package installs for project dependencies. DevRepo, CompanyRepo, and other non-source repos are exempt - they contain documentation and configuration, not buildable applications.

- Runtime version pinned in a committed version file (`.nvmrc`, `.python-version`, `rust-toolchain.toml`, `build.zig.zon`)
- Environment directory gitignored (`node_modules/`, `.venv/`, `target/`, `zig-cache/`)
- Lock file committed (`package-lock.json`, `requirements.txt`, `Cargo.lock`)
- See LOCAL_ENVIRONMENTS.md for per-runtime setup instructions

BAD: Running `npm install -g express` globally - version conflicts, no reproducibility
GOOD: `.nvmrc` + `npm install` in project root - isolated, reproducible

## WS-CT-06: promptsystem-sync.json Required for SYNCED Repos

SYNCED repos must have a promptsystem-sync.json at [WORKSPACE_FOLDER] root. SELF-CONTAINED repos do not need one.

BAD: SYNCED repo with no promptsystem-sync.json - sync script cannot find configuration
GOOD: promptsystem-sync.json at [WORKSPACE_FOLDER] root with sources, bundles, and filters defined

## WS-ST-01: Agent Folder Structure

Agent folder must contain specs/, workflows/, skills/ subfolders.

BAD: Agent folder has specs/ and workflows/ but no skills/ - skills cannot be loaded
GOOD: Agent folder has all three subfolders with content

## WS-ST-02: Workspace Structure Matches Declared Mode

Workspace structure must match the declared mode in NOTES.md Project Info:
- SINGLE-PROJECT: One project, no main.code-workspace file
- MONOREPO: Multiple projects in subfolders, no main.code-workspace file
- WORKSPACE: main.code-workspace file present, references repos that may be outside [WORKSPACE_FOLDER]

BAD: NOTES.md declares WORKSPACE mode but no main.code-workspace file exists
GOOD: Declared mode matches actual workspace structure

## WS-SY-01: Relative Source Paths in promptsystem-sync.json

promptsystem-sync.json source paths must be relative (e.g., `../IPPS/DevSystemV4.3`), not absolute.

BAD: source: "e:\\Dev\\IPPS\\DevSystemV4.3" - machine-specific, breaks portability
GOOD: source: "../IPPS/DevSystemV4.3" - portable across machines

## WS-SY-02: promptsystem-sync.json Source Entry Validation

Each source entry in promptsystem-sync.json must define: source, selected_bundles, bundles, include, exclude, deprecated, never_overwrite.

BAD: Source entry missing 'never_overwrite' array - sync script cannot protect files from overwrite
GOOD: All 7 required fields present per source entry

## WS-SY-03: never_overwrite Enforcement

Files matching never_overwrite patterns must never be overwritten or deleted during sync, regardless of source changes or deprecated status.

BAD: Sync overwrites 'specs/sops/project-release.md' because source has newer version, destroying local customizations
GOOD: Sync skips 'specs/sops/project-release.md' because it matches never_overwrite pattern

## WS-TM-01: Template Suffix

Template files must use _TEMPLATE suffix (SK-FL-07).

BAD: DEV_REPO_NOTES.md (looks like an operational file, may be used directly without adaptation)
GOOD: DEV_REPO_NOTES_TEMPLATE.md (clearly a template requiring adaptation)

## WS-TM-04: Template Annotations Use XML Comments

All template annotations (instructions, conditionals, removal notices) must use XML comments per TEMPLATE_RULES.md TMPL-AN-01. No prose paragraphs disguised as content.

BAD: `Instructions: Replace placeholder values with your project information.`
GOOD: `<!-- Instructions: Replace placeholder values with your project information. -->`

## WS-FL-04: ID-REGISTRY.md Inline Datestamps

ID-REGISTRY.md Project Topics entries must include a datestamp after the description. No Document History section required.

BAD: `- **WSKMGMT** - Workspace Management Skill (PromptSystem V5.0)` (no datestamp)
GOOD: `- **WSKMGMT** - Workspace Management Skill (PromptSystem V5.0) - 2026-09-03`

## WS-CT-08: Release Configuration Conditional on Workspace Type

NOTES.md must contain a Release Configuration section with [RELEASE_CONFIG] and at least one [RELEASE_REPO] block for SOFTWARE-DEV workspaces. GENERAL workspaces must omit Release Configuration entirely.

BAD: SOFTWARE-DEV workspace with no Release Configuration section
GOOD: SOFTWARE-DEV workspace with [RELEASE_CONFIG] and [RELEASE_REPO: product] block
BAD: GENERAL workspace with Release Configuration section (no product to release)
GOOD: GENERAL workspace with no Release Configuration section

## WS-CT-09: GENERAL Workspace Constraints

GENERAL workspace type (Dimension 5) must omit dev-only constants and sections. Code allowed only in session folders (IMPL-ISOLATED default). Dimension 1 = N/A.

Omitted constants: [PRODUCT_REPO_FOLDER], [PRODUCT_SOURCE_FOLDER], [PRODUCT_DOCS_FOLDER], [PRODUCT_VERSION], [WORKSPACE_FILE], [SOPS_FILE], [RELEASE_NOTES_FOLDER]
Omitted sections: Build/Test Rules, Runtime Environment, Release Configuration
Required constants: [WORKSPACE_FOLDER], [DEV_KNOWLEDGE_FOLDER], [DEV_SPECS_FOLDER], [AGENT_FOLDER], [SESSIONS_FOLDER], [SESSION_ARCHIVE_FOLDER], [SKILL_TOOLS_FOLDER], [API_KEYS_FILE]

BAD: GENERAL workspace with [PRODUCT_REPO_FOLDER] and Build/Test Rules section
GOOD: GENERAL workspace with only base constants, no dev-only sections

## WS-PR-01: Privacy Gate

No real identifiers, project names, paths, names of real people, or session-specific references in skill files.

BAD: [PRODUCT_REPO_FOLDER]: [WORKSPACE_FOLDER]\..\MyRealProject
GOOD: [PRODUCT_REPO_FOLDER]: [WORKSPACE_FOLDER]\..\[product-repo-name]
