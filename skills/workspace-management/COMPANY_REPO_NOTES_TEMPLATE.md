# CompanyRepo NOTES Template

Template for CompanyRepo NOTES.md. Copy and adapt for your company repository.

Replace all `[placeholder]` values with your organization-specific content.

## Company Info

- Company folder: [COMPANY_REPO_FOLDER]
- Description: [one-sentence-description]
- Maintainer: [role-or-team]

## Downstream Repositories

This section is informational only. Each downstream repo owns its own sync configuration in `promptsystem-sync.json` at its `[WORKSPACE_FOLDER]` root. The source repo does NOT contain bundle definitions or sync configuration.

### [downstream-repo-1]

- Repo path: ../[downstream-repo-1] (relative path only)
- Sync sources used: Prompt System, Knowledge, Specs
- Knowledge bundles received: [bundle-1], [bundle-2]
- Specs bundles received: [bundle-1]
- PromptSystem version: PromptSystemV[X.Y]

### [downstream-repo-2]

- Repo path: ../[downstream-repo-2] (relative path only)
- Sync sources used: Prompt System, Knowledge
- Knowledge bundles received: [bundle-3]
- Specs bundles received: (none)
- PromptSystem version: PromptSystemV[X.Y]

Instructions: Add one section per downstream repo. Use RELATIVE paths only (e.g., `../MyProject`), never absolute paths. This list is informational — it helps `/sync to targets` workflows know which repos to push to. The actual sync configuration (bundles, filters, never_overwrite, deprecated) lives in each target repo's `promptsystem-sync.json`.

## Source Content

### Knowledge Bundles

Folders in `[COMPANY_REPO_FOLDER]\knowledge\` available for sync:

- [bundle-1]/ - [description]
- [bundle-2]/ - [description]
- [bundle-3]/ - [description]

### Specs Bundles

Folders in `[COMPANY_REPO_FOLDER]\specs\` available for sync:

- [bundle-1]/ - [description]

Instructions: List available knowledge and specs bundles that downstream repos can select in their `promptsystem-sync.json` `selected_bundles` arrays. Add or remove bundles as content evolves.
