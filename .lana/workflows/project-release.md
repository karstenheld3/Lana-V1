---
description: Create a semver release with release notes, tag, and GitHub release
auto_execution_mode: 1
---

# Project Release Workflow

Create a release with comprehensive release notes, git tag, and GitHub release.

## Prerequisites

- Version already bumped via `_ship.bat` (pyproject.toml updated, committed)
- Binary built via `_build.bat` (dist/ contains the artifact)
- All work committed
- GitHub CLI (`gh`) installed and authenticated

## Pipeline Order

```
_build.bat   -> builds dist\lana-{version}-win-x64.exe
_ship.bat    -> bumps version in pyproject.toml based on commit types
/project-release -> this workflow: release notes, tag, GitHub release
```

## Steps

### 1. Read Version and Determine Scope

```powershell
$version = (Select-String -Path pyproject.toml -Pattern '^version\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
$lastTag = git tag --sort=-creatordate | Select-Object -First 1
```

Compare changes since last release:
- List commits: `git log [LAST_TAG]..HEAD --oneline`
- List changed files: `git diff --name-status [LAST_TAG]..HEAD`

### 2. Inventory Sessions

Find all session folders in `_Sessions/`:
```powershell
Get-ChildItem "_Sessions" -Directory | Where-Object { $_.Name -notlike "Archive*" }
```

For each session, collect:
- Session name and date
- Goal (from NOTES.md header)
- Status (from PROGRESS.md - complete/in-progress)
- Artifacts: `_INFO_*.md`, `_SPEC_*.md`, `_IMPL_*.md`
- Key findings (from NOTES.md)

### 3. Generate Release Notes

Create `docs/ReleaseNotes/RELEASE_NOTES_v[VERSION].md`:

```markdown
# Release Notes: v[VERSION]

## Summary

[One paragraph: what this release adds/fixes/changes]

## Changes

### Features
- [feat commits summarized]

### Fixes
- [fix commits summarized]

### Other
- [docs/refactor/chore commits summarized]

## Sessions

### [Session_Name]

**Goal**: [from NOTES.md]
**Outcome**: [summary]
**Artifacts**: [key documents]

---

[Repeat for each session since last release]

## Test Results

- **Offline tests**: [N] passed
- **Live tests**: [N] passed (if run)

## Binary

- `dist/lana-[VERSION]-win-x64.exe` ([N] MB, [signed/unsigned])
- SHA256: [from dist/SHA256SUMS.txt]

## Document History

**[YYYY-MM-DD HH:MM]**
- Initial release notes created
```

### 4. Commit Release Notes

```powershell
git add "docs/ReleaseNotes/RELEASE_NOTES_v[VERSION].md"
git commit -q -m "docs: add release notes for v[VERSION]"
```

### 5. Create Tag

Tag format: `v[VERSION]` (e.g., `v0.2.0`)

```powershell
git tag -a "v[VERSION]" -m "Release v[VERSION]: [brief summary]"
git push origin "v[VERSION]"
git push
```

### 6. User Confirmation

Present summary to user:
- Version and tag name
- Number of sessions
- Binary artifact path and size
- Key changes

Ask: "Create GitHub release with these notes and attach the binary? (y/n)"

### 7. Create GitHub Release

```powershell
$version = "v[VERSION]"
$binary = Get-ChildItem dist -Filter "lana-*-win-x64.exe" | Select-Object -First 1
$checksums = Join-Path dist "SHA256SUMS.txt"
gh release create $version --title "Lana $version" --notes-file "docs/ReleaseNotes/RELEASE_NOTES_$version.md" $binary.FullName $checksums
```

Report release URL to user.

## Notes

- Tag format is semver: `v0.1.0`, `v0.2.0`, `v1.0.0`
- Include ALL sessions since last release, not just completed ones
- Mark in-progress sessions clearly in release notes
- If `gh` not installed, provide manual release URL and instruct to attach binary manually
- Binary and SHA256SUMS.txt are attached as release assets
