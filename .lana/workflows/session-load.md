---
description: Resume a development session
auto_execution_mode: 3
---

# Load Session Workflow

## Required Skills

- @skills:session-management for session file structure

## MUST-NOT-FORGET

- Run `/prime` workflow BEFORE reading session documents
- `/prime` loads FAILS.md, ID-REGISTRY.md, !NOTES.md - critical workspace context

## Step 1: Identify Session

Check if user provided a session path:
- If path provided with NOTES.md, PROGRESS.md, PROBLEMS.md: Use that session
- If no path provided: Find most recently modified session folder:

**Path resolution** - if the provided path does not exist:
1. Split the path into segments
2. Validate from root: check each segment exists (e.g., does `E:\Dev` exist? Does `E:\Dev\MyProject` exist?)
3. Find the first segment that fails (the divergence point)
4. Search within the last valid parent only (NOT the entire drive) using `find_by_name` with the missing segment name
5. Never search more than one level above the divergence point

```powershell
Get-ChildItem -Path "[DEFAULT_SESSIONS_FOLDER]" -Directory -Filter "_*" | Where-Object { Test-Path "$($_.FullName)\NOTES.md" } | Sort-Object { (Get-ChildItem $_.FullName -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime } -Descending | Select-Object -First 1 -ExpandProperty FullName
```

**Topic Folder Detection:** Run @skills:session-management **Topic Folder Detection** procedure. If target matches `T##_*`, load parent session context before proceeding.

## Step 2: Load Context

Run `/prime` workflow now. If the session path is in a **different workspace** (not under the current working directory), `/prime` MUST target the session's parent workspace (the folder containing `_Sessions/`), not the current working directory.

## Step 3: Read Session Documents

Read **root-level** session documents only: NOTES.md, PROGRESS.md, PROBLEMS.md, and any _INFO/_SPEC/_IMPL/_TASK files at the session root.

**Do NOT** read topic subfolder (`T##_*/`) or step subfolder (`S##_*/`) documents unless the user's target path points inside a specific subfolder. The root NOTES.md contains topic summaries - reading subfolder contents wastes context.

Restore phase state from NOTES.md "Current Phase" section.

Make sure all state progress is documented in `NOTES.md` and `PROGRESS.md` and `PROBLEMS.md`

## Step 4: Summarize and Propose
Start with single row: "Read [a] .md files ([b] priority), [c] code files ( [d] .py, [e] ...). Mode: [scenario]"

Example: "Read 5 .md files (2 priority), 12 code files (10 .py, 2 .html). Mode: SINGLE-PROJECT + SINGLE-VERSION + SESSION-MODE"

Then:
- Summarize findings and propose next steps.
- Answer with max 20 short lines of text.

## Step 5: Verify MUST-NOT-FORGET

Review each MNF item above and confirm compliance.