# INFO: Cascade Tool Definitions - Verbatim Source for Lana MVP-1

**Doc ID**: LANAAGNT-IN02
**Goal**: Provide the complete, verbatim tool descriptions and parameter contracts for the 15 MVP-1 tools, transcribed from a live Cascade session, as the single transcription source for LANAAGNT-IP01-IS-06
**Timeline**: Created 2026-08-29, Updated 0 times

**Depends on:**
- `_IMPL_LANA_MVP-1.md [LANAAGNT-IP01]` IS-06 consumes this document
- `HowWindsurfCascadeWorks.md` chapters 8-9 for cross-checking (incomplete for 3 tools, see Summary)

## Summary

- The ebook chapters 8-9 contain full "Description (verbatim)" blocks for 12 of the 15 MVP-1 tools but NOT for `multi_edit` (schema + constraints only), `command_status` (schema only), and `skill` (explicitly "abbreviated") - transcription from the ebook alone would force paraphrasing, violating LANAAGNT-DD-11 [VERIFIED against ebook text]
- This document captures all 15 descriptions verbatim from a live Cascade session (2026-08-29, same system family as the V2.3.15 ebook capture) while the source is available
- Parameter contracts are transcribed as compact parameter lists (name, type, required, enum, default); all Cascade schemas share: JSON Schema Draft 2020-12, `additionalProperties: false`
- Two definitions contain per-host dynamic content that Lana must substitute: `run_command` (OS + shell) and `skill` (available skill list)

## Table of Contents

1. [Transcription Rules](#1-transcription-rules)
2. [File Reading Tools](#2-file-reading-tools)
3. [File Editing Tools](#3-file-editing-tools)
4. [Execution Tools](#4-execution-tools)
5. [State, Prompt System, Interaction Tools](#5-state-prompt-system-interaction-tools)
6. [Web Research Tools](#6-web-research-tools)
7. [Next Steps](#7-next-steps)
8. [Sources](#8-sources)
9. [Document History](#9-document-history)

## 1. Transcription Rules

- Description blocks below are LITERAL - copy character-for-character into `tools/definitions.py` (AP-PR-13 applies)
- `{OS}` and `{SHELL}` in `run_command` and `{SKILL_LIST}` in `skill` are Lana substitution points - everything else is fixed text
- Parameter lists are lossless renderings of the JSON Schemas: rebuild each schema as Draft 2020-12 with `additionalProperties: false`, listed properties, and the stated `required` array
- IS-06 acceptance: a diff between this document's description blocks and `definitions.py` strings shows zero differences outside substitution points

## 2. File Reading Tools

### 2.1 read_file

**Parameters:** `file_path` (string, required) | `offset` (integer) | `limit` (integer)

**Description [LITERAL]:**
```text
Reads a file at the specified relative path.
This tool is only able to read files in the workspace that are not gitignored.
If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.

Usage:
- The file_path parameter must be an absolute path, not a relative path
- You can optionally specify a line offset and limit to read files that are larger than 1000 lines. For other files, do not provide these parameters to read the whole file.
- Any lines longer than 2000 characters will be truncated
- Text files are returned with 1-indexed line numbers in cat -n format
- Image files (jpg, jpeg, png, gif, bmp, webp, svg, tiff, ico, heic, heif) are automatically presented visually
- You have the capability to call multiple tools in a single response. It is always better to speculatively read multiple files as a batch that are potentially useful.
- You will regularly be asked to read screenshots. If the user provides a path to a screenshot ALWAYS use this tool to view the file at the path. This tool will work with all temporary file paths like /var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png
- If you read a file that exists but has empty contents you will receive a system reminder warning in place of file contents.
```

### 2.2 list_dir

**Parameters:** `DirectoryPath` (string, required)

**Description [LITERAL]:**
```text
Lists files and directories in a given path. The path parameter must be an absolute path to a directory that exists. For each item in the directory, output will have: relative path to the file or directory, and size in bytes if file or number of items (recursive) if directory. You should generally prefer the find_by_name and grep_search tools, if you know which directories to search.
```

### 2.3 grep_search

**Parameters:** `SearchPath` (string, required) | `Query` (string, required) | `CaseSensitive` (boolean) | `FixedStrings` (boolean) | `Includes` (string[]) | `MatchPerLine` (boolean)

**Description [LITERAL]:**
```text
A powerful search tool built on ripgrep

Usage:
- NEVER invoke `grep` or `rg` as a Bash command, use this tool instead. The Grep tool has
been optimized for correct permissions and access.
- DO NOT USE MatchPerLine for initial searches that may have a large number of results. Use it only when you
know it is a very specific, targeted search.
- By default, Query is treated as a regular expression. Set FixedStrings to true to treat Query as a literal string (no regex).
- Filter files with Includes parameter in glob format (e.g., "*.js", "**/*.tsx")
- If the result is truncated, you must narrow down your search using a more specific query or more filters.
```

### 2.4 find_by_name

**Parameters:** `SearchDirectory` (string, required) | `Pattern` (string, required) | `Excludes` (string[]) | `Extensions` (string[]) | `FullPath` (boolean) | `MaxDepth` (integer) | `Type` (string, enum: file/directory/any)

**Description [LITERAL]:**
```text
Search for files and subdirectories within a specified directory using fd.
Search uses smart case and will ignore gitignored files by default.
Pattern and Excludes both use the glob format. If you are searching for Extensions, there is no need to specify both Pattern AND Extensions.
To avoid overwhelming output, the results are capped at 50 matches. Use the various arguments to filter the search scope as needed.
Results will include the type, size, modification time, and relative path.
```

## 3. File Editing Tools

### 3.1 edit

**Parameters:** `explanation` (string) | `file_path` (string, required) | `old_string` (string, required) | `new_string` (string, required) | `replace_all` (boolean)

**Description [LITERAL]:**
```text
Performs exact string replacements in files.

Usage:
- You must use your `Read` tool at least once in the conversation before editing. This tool will error if you attempt an edit without reading the file.
- When editing text from Read tool output, ensure you preserve the exact indentation (tabs/spaces) as it appears AFTER the line number prefix. The line number prefix format is: spaces + line number + tab. Everything after that tab is the actual file content to match. Never include any part of the line number prefix in the old_string or new_string.
- ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required.
- Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked.
- The edit will FAIL if `old_string` is not unique in the file. Either provide a larger string with more surrounding context to make it unique or use `replace_all` to change every instance of `old_string`.
- Use `replace_all` for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance.
- The edit will FAIL if `old_string` and `new_string` are identical. This is considered a no-op and will throw an error.
- Include an `explanation` field to describe the change you are making.
IMPORTANT: You must generate the following arguments first, before any others: [file_path]
```

### 3.2 multi_edit (NOT fully verbatim in the ebook - this is the primary source)

**Parameters:** `explanation` (string) | `file_path` (string, required) | `edits` (array of objects {`old_string` (string, required), `new_string` (string, required), `replace_all` (boolean)}, minItems 1, required)

**Description [LITERAL]:**
```text
This is a tool for making multiple edits to a single file in one operation. It is built on top of the Edit tool and allows you to perform multiple find-and-replace operations efficiently. Prefer this tool over the Edit tool when you need to make multiple edits to the same file.

Before using this tool:

1. Use the Read tool to understand the file's contents and context
2.Verify the directory path is correct

To make multiple file edits, provide the following: 
1.file_path: The path to the file to modify, relative to the root of the repository
2.edits: An array of edit operations to perform, where each edit contains: 
   - old_string: The text to replace(must match the file contents exactly, including all whitespace and indentation) 
 - new_string: The edited text to replace the old_string
 - replace_all: Replace all occurrences of old_string.This parameter is optional and defaults to false.
3.explanation: A description of the change to be made

IMPORTANT: 
 - All edits are applied in sequence, in the order they are provided
 - Each edit operates on the result of the previous edit
 - All edits must be valid for the operation to succeed - if any edit fails, none will be applied
 - This tool is ideal when you need to make several changes to different parts of the same file
 - For Jupyter notebooks(.ipynb files), use the NotebookEdit instead

CRITICAL REQUIREMENTS: 
1.All edits follow the same requirements as the single Edit tool
2.The edits are atomic - either all succeed or none are applied
3.Plan your edits carefully to avoid conflicts between sequential operations

WARNING: 
 - The tool will fail if edits.old_string doesn't match the file contents exactly (including whitespace)
- The tool will fail if edits.old_string and edits.new_string are the same
- Since edits are applied in sequence, ensure that earlier edits don't affect the text that later edits are trying to find

When making edits: 
 - Ensure all edits result in idiomatic, correct code
 - Do not leave the code in a broken state
 - Always use absolute file paths(starting with /) 
 - Only use emojis if the user explicitly requests it.Avoid adding emojis to files unless asked.
 - Use replace_all for replacing and renaming strings across the file.This parameter is useful if you want to rename a variable for instance.

If you want to create a new file, use: 
 - A new file path, including dir name if needed
 - First edit: empty old_string and the new file's contents as new_string
- Subsequent edits: normal edit operations on the created content
IMPORTANT: You must generate the following arguments first, before any others: [file_path]
```

### 3.3 write_to_file

**Parameters:** `TargetFile` (string, required) | `CodeContent` (string, required) | `EmptyFile` (boolean, required)

**Description [LITERAL]:**
```text
Use this tool to create new files. The file and any parent directories will be created for you if they do not already exist.
		Follow these instructions:
		1. NEVER use this tool to modify or overwrite existing files. Always first confirm that TargetFile does not exist before calling this tool.
		2. You MUST specify the full TargetFile before any of the code contents.
IMPORTANT: You must generate the following arguments first, before any others: [TargetFile]
```

## 4. Execution Tools

### 4.1 run_command

**Parameters:** `CommandLine` (string, required) | `Cwd` (string) | `Blocking` (boolean) | `SafeToAutoRun` (boolean) | `WaitMsBeforeAsync` (integer)

**Description [LITERAL], `{OS}`/`{SHELL}` substituted at startup:**
```text
PROPOSE a command to run on behalf of the user. Operating System: {OS}. Shell: {SHELL}.
**NEVER PROPOSE A cd COMMAND**.
If you have this tool, note that you DO have the ability to run commands directly on the USER's system.
Make sure to specify CommandLine exactly as it should be run in the shell.
Note that the user will have to approve the command before it is executed. The user may reject it if it is not to their liking.
The actual command will NOT execute until the user approves it. The user may not approve it immediately.
If the step is WAITING for user approval, it has NOT started running.
Commands will be run with PAGER=cat. You may want to limit the length of output for commands that usually rely on paging and may contain very long output (e.g. git log, use git log -n <N>).
```

### 4.2 command_status (NOT fully verbatim in the ebook - this is the primary source)

**Parameters:** `CommandId` (string, required) | `OutputCharacterCount` (integer, required) | `WaitDurationSeconds` (integer, default 0)

**Description [LITERAL]:**
```text
Check the status of a previously started terminal command by its ID. Returns the current status (running or done), output lines as specified by output priority, and any error if present. If WaitDurationSeconds is specified, this tool will also wait up to that many seconds for the command to finish. Otherwise, this tool will directly return the current status of the command. Do not try to check the status of any IDs other than Background command IDs.
```

## 5. State, Prompt System, Interaction Tools

### 5.1 todo_list

**Parameters:** `todos` (array of objects {`id` (string, required), `content` (string, required), `status` (enum: pending/in_progress/completed, required), `priority` (enum: high/medium/low, required)}, required)

**Description [LITERAL]:**
```text
Use this tool to create, update, or manage a todo list. This tool helps you organize tasks with different statuses and priorities. You can add new todos, update existing ones, mark them as completed, or reorganize the entire list.

The tool accepts a list of todo items, each with:
- content: The task description
- status: pending, in_progress, or completed
- priority: high, medium, or low
- id: A unique identifier for the todo item

Use this tool when you need to:
- Create a new todo list (mark the first item as in_progress to indicate what you're currently working on)
- Add items to an existing todo list
- Update the status of todo items
- Change priorities of tasks
- Mark tasks as completed
- Reorganize or restructure the todo list
```

### 5.2 skill (ebook version explicitly abbreviated - this is the primary source)

**Parameters:** `SkillName` (string, required)

**Description [LITERAL], `{SKILL_LIST}` substituted at startup from loaded skills:**
```text
Invoke a skill to get detailed instructions or knowledge for a task.
Use this when a task matches a skill's description.
Available skills:
{SKILL_LIST}
```

`{SKILL_LIST}` format, one line per skill: `- [name]: [description] ([N] supporting files)` - the supporting-file count suffix appears only when the skill folder has files besides SKILL.md.

### 5.3 ask_user_question

**Parameters:** `question` (string, required) | `options` (array of objects {`label` (string, required), `description` (string, required)}, required) | `allowMultiple` (boolean, required)

**Description [LITERAL]:**
```text
Ask the user a question with predefined options. Use this when you need the user to make a choice between specific options.
You can provide up to 4 options, each with a label and description.
NEVER include "other" as an option - the user can always automatically provide a custom response.
Set allowMultiple to true if the user should be able to select more than one option.
```

## 6. Web Research Tools

### 6.1 search_web

**Parameters:** `query` (string, required) | `domain` (string)

**Description [LITERAL]:**
```text
Performs a web search to get a list of relevant web documents for the given query and optional domain filter.
```

### 6.2 read_url_content

**Parameters:** `Url` (string, required)

**Description [LITERAL]:**
```text
Read content from a URL. URL must be an HTTP or HTTPS URL that points to a valid internet resource accessible via web browser.
Note that the user will have to approve the web request before it is fetched. The user may reject it if it is not to their liking.
The actual fetch will NOT execute until the user approves it. The user may not approve it immediately.
```

### 6.3 view_content_chunk

**Parameters:** `document_id` (string, required) | `position` (integer, required)

**Description [LITERAL]:**
```text
View a specific chunk of a web or knowledge base document content using its DocumentId and chunk position. The DocumentId must have already been read by the read_url_content tool before this can be used on that particular DocumentId.
```

## 7. Session Trajectory Tools (added 2026-08-30)

### 7.1 trajectory_search

**Parameters:** `ID` (string, required) | `Query` (string, required) | `SearchType` (string, enum: cascade/user, required)

**Description [LITERAL]:**
```text
Semantic search or retrieve trajectory. Trajectories are one of conversations. Returns chunks from the trajectory, scored, sorted, and filtered by relevance. Maximum number of chunks returned is 50. Call this tool when the user @mentions a @conversation. Do NOT call this tool with SearchType: 'user'. IGNORE @activity mentions.
```

Parameter descriptions (for the JSON Schema): `ID` = "The ID of the trajectory to search or retrieve: cascade ID for conversations, trajectory ID for user activities."; `Query` = "The query string to search for within the trajectory. An empty query will return all trajectory steps."; `SearchType` = "The type of item to search or retrieve: 'cascade' for conversations, or 'user' for user activities."

## 8. Next Steps

1. LANAAGNT-IP01-IS-06 transcribes from this document (primary) with the ebook chapters 8-9 as cross-check for the 12 tools both sources cover
2. During IS-06: verify each `required` array against provider acceptance in the Phase D smoke tests (schemas are transcriptions; provider round trips upgrade them to [TESTED])

## 9. Sources

**Primary Sources:**
- `LANAAGNT-IN02-SC-CSCD-LIVSSN`: Live Cascade session tool definitions (2026-08-29, same system family as the V2.3.15 wire capture) - all 15 descriptions and parameter contracts
- `LANAAGNT-IN02-SC-CSMP-EBK`: `docs/Windsurf/HowCascadeWorks/HowWindsurfCascadeWorks.md` chapters 8-9 - cross-check source; confirms 12 of 15 verbatim, documents the gap for `multi_edit`, `command_status`, `skill`

## 10. Document History

**[2026-08-30 06:10]**
- Added: section 7 trajectory_search (16th tool) - transcribed verbatim from the same live Cascade session family; consumed by LANAAGNT-SP01 FR-15 / LANAAGNT-IP01 IS-23
- Changed: section numbering (Next Steps/Sources/History shifted by one)

**[2026-08-29 22:08]**
- Initial document created from `/improve` run 2 on LANAAGNT-IP01: 15 verbatim tool descriptions + parameter contracts, substitution points marked
