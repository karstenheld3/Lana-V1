<#
.SYNOPSIS
    Generic PromptSystem sync script with -diff and -execute modes.
.DESCRIPTION
    Reads all sync configuration from target's promptsystem-sync.json.
    Source repo is purely a content provider (read-only during sync).
    Supports multi-source, multi-target, multi-config in a single call.
.PARAMETER diff
    Preview mode: show changes, modify nothing.
.PARAMETER execute
    Apply mode: copy, delete, update last_sync timestamp.
.PARAMETER sources
    Source repo paths to filter on (JSON array or single string).
    Filters which source entries in config to sync.
.PARAMETER targets
    Target repo paths (JSON array or single string).
.PARAMETER configs
    Paths to promptsystem-sync.json files, paired 1:1 with targets.
.PARAMETER output_file
    File path for full diff report. Default: console.
.PARAMETER showVerbose
    Show excluded files and skip reasons in output.
.EXAMPLE
    sync.ps1 -diff -sources "../IPPS/DevSystemV4.3" -targets "." -configs "promptsystem-sync.json"
.EXAMPLE
    sync.ps1 -execute -sources '["../IPPS/DevSystemV4.3"]' -targets '["../Lana-V2-Dev"]' -configs '["promptsystem-sync.json"]'
#>

[CmdletBinding()]
param(
    [switch]$diff,
    [switch]$execute,
    [string]$sources,
    [string]$targets,
    [string]$configs,
    [string]$output_file,
    [switch]$showVerbose
)

# ============================================================
# Functions
# ============================================================

function Resolve-PathParam {
    param([string]$Value, [string]$ParamName)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        Write-Error "Parameter -$ParamName is required."
        exit 2
    }
    $trimmed = $Value.Trim()
    if ($trimmed.StartsWith('[') -and $trimmed.EndsWith(']')) {
        try {
            $array = $trimmed | ConvertFrom-Json
            $resolved = @()
            foreach ($item in $array) {
                $resolved += [System.IO.Path]::GetFullPath($item)
            }
            return $resolved
        } catch {
            Write-Error "Parameter -$ParamName contains invalid JSON: $trimmed"
            exit 2
        }
    }
    $fullPath = [System.IO.Path]::GetFullPath($trimmed)
    return , $fullPath
}

function Test-SyncConfig {
    param([object]$Config, [string]$ConfigPath)
    $errors = @()
    if (-not $Config.sources) {
        $errors += "Missing 'sources' array in '$ConfigPath'."
    }
    foreach ($src in $Config.sources) {
        if (-not $src.source) { $errors += "Source entry missing 'source' field in '$ConfigPath'." }
        if (-not $src.selected_bundles) { $errors += "Source '$($src.source)' missing 'selected_bundles' array." }
        if (-not $src.bundles) { $errors += "Source '$($src.source)' missing 'bundles' definitions." }
        if (-not $src.include) { $errors += "Source '$($src.source)' missing 'include' array." }
        foreach ($field in @('selected_bundles', 'include', 'exclude', 'deprecated', 'never_overwrite')) {
            $val = $src.$field
            if ($null -ne $val -and $val -isnot [array]) {
                $errors += "Source '$($src.source)' field '$field' must be an array, got $($val.GetType().Name)."
            }
        }
        foreach ($bundleName in $src.selected_bundles) {
            if (-not $src.bundles.$bundleName) {
                $errors += "Source '$($src.source)' selects bundle '$bundleName' but bundle not defined in 'bundles'."
            }
        }
    }
    if ($errors.Count -gt 0) {
        foreach ($e in $errors) { Write-Error $e }
        exit 2
    }
}

function Test-GlobMatch {
    param([string]$Path, [string[]]$Patterns)
    $options = if ($IsLinux -or $IsMacOS) {
        [System.Management.Automation.WildcardOptions]::None
    } else {
        [System.Management.Automation.WildcardOptions]::IgnoreCase
    }
    foreach ($pattern in $Patterns) {
        $wildcard = [System.Management.Automation.WildcardPattern]::new(
            $pattern,
            $options
        )
        if ($wildcard.IsMatch($Path)) { return $true }
    }
    return $false
}

function Get-FileHash256 {
    param([string]$Path)
    if (-not (Test-Path $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -Path $Path -Algorithm SHA256).Hash
}

function Get-SourceFiles {
    param([string]$SourceRoot)
    $files = @()
    $sourceRootFull = [System.IO.Path]::GetFullPath($SourceRoot)
    $enumerated = [System.IO.Directory]::EnumerateFiles(
        $sourceRootFull,
        '*',
        [System.IO.SearchOption]::AllDirectories
    )
    foreach ($fullPath in $enumerated) {
        $relativePath = [System.IO.Path]::GetRelativePath($sourceRootFull, $fullPath)
        $relativePath = $relativePath -replace '\\', '/'
        $files += [PSCustomObject]@{
            FullPath     = $fullPath
            RelativePath = $relativePath
        }
    }
    return $files
}

function Invoke-FileFilter {
    param(
        [object]$SourceEntry,
        [array]$Files
    )
    $result = @{
        Included = @()
        Excluded = @()
    }

    $bundleIncludes = @()
    $bundleExcludes = @()
    foreach ($bundleName in $SourceEntry.selected_bundles) {
        $bundle = $SourceEntry.bundles.$bundleName
        if ($bundle.include) { $bundleIncludes += @($bundle.include) }
        if ($bundle.exclude) { $bundleExcludes += @($bundle.exclude) }
    }

    foreach ($file in $Files) {
        $relPath = $file.RelativePath
        $excludeReason = $null

        # Step 1: source include
        $passesInclude = $false
        foreach ($pattern in $SourceEntry.include) {
            if (Test-GlobMatch -Path $relPath -Patterns @($pattern)) {
                $passesInclude = $true
                break
            }
        }
        if (-not $passesInclude) {
            $excludeReason = 'source include'
        }

        # Step 2: source exclude
        if ($excludeReason -eq $null) {
            if (Test-GlobMatch -Path $relPath -Patterns @($SourceEntry.exclude)) {
                $excludeReason = 'source exclude'
            }
        }

        # Step 3: bundle include (union)
        if ($excludeReason -eq $null -and $bundleIncludes.Count -gt 0) {
            $passesBundleInclude = $false
            foreach ($pattern in $bundleIncludes) {
                if (Test-GlobMatch -Path $relPath -Patterns @($pattern)) {
                    $passesBundleInclude = $true
                    break
                }
            }
            if (-not $passesBundleInclude) {
                $excludeReason = 'bundle include'
            }
        }

        # Step 4: bundle exclude (union)
        if ($excludeReason -eq $null -and $bundleExcludes.Count -gt 0) {
            if (Test-GlobMatch -Path $relPath -Patterns @($bundleExcludes)) {
                $excludeReason = 'bundle exclude'
            }
        }

        if ($excludeReason) {
            $result.Excluded += [PSCustomObject]@{
                File   = $file
                Reason = $excludeReason
            }
        } else {
            $result.Included += $file
        }
    }

    return $result
}

function Test-BreakingChange {
    param([string]$SourcePath, [string]$TargetPath)
    # Heuristic: detect structural changes (removed headers/sections) in source vs target
    # A breaking change is when source has removed structural markers that target still has
    $structuralPattern = '^\s{0,3}(#{1,6}\s|-\s\*\*\[|##\s)'
    try {
        $sourceLines = Get-Content -Path $SourcePath -Encoding UTF8
        $targetLines = Get-Content -Path $TargetPath -Encoding UTF8
        $sourceStructural = $sourceLines | Where-Object { $_ -match $structuralPattern } | ForEach-Object { $_.Trim() }
        $targetStructural = $targetLines | Where-Object { $_ -match $structuralPattern } | ForEach-Object { $_.Trim() }
        # If target has structural markers that source no longer has -> breaking change
        $removedFromSource = $targetStructural | Where-Object { $_ -notin $sourceStructural }
        return $removedFromSource.Count -gt 0
    } catch {
        return $false
    }
}

function Compare-Files {
    param(
        [array]$SourceFiles,
        [string]$TargetRoot,
        [string[]]$Deprecated,
        [string[]]$NeverOverwrite,
        [string]$LastSync
    )
    $targetRootFull = [System.IO.Path]::GetFullPath($TargetRoot)
    $results = @()

    # Classify source files
    foreach ($file in $SourceFiles) {
        $relPath = $file.RelativePath
        $targetPath = [System.IO.Path]::Join($targetRootFull, ($relPath -replace '/', '\'))
        $isNeverOverwrite = Test-GlobMatch -Path $relPath -Patterns $NeverOverwrite

        if (Test-Path $targetPath -PathType Leaf) {
            $sourceHash = Get-FileHash256 -Path $file.FullPath
            $targetHash = Get-FileHash256 -Path $targetPath
            if ($sourceHash -eq $targetHash) {
                $results += [PSCustomObject]@{
                    Action = 'UNCHANGED'
                    RelativePath = $relPath
                    SourcePath = $file.FullPath
                    TargetPath = $targetPath
                }
            } else {
                if ($isNeverOverwrite) {
                    $results += [PSCustomObject]@{
                        Action = 'SKIP'
                        RelativePath = $relPath
                        Reason = 'never_overwrite'
                        SourcePath = $file.FullPath
                        TargetPath = $targetPath
                    }
                } else {
                    # Check if target was locally modified after last_sync (NFR-02, FR-14)
                    $isLocallyModified = $false
                    if ($LastSync) {
                        try {
                            $lastSyncDate = [datetime]::Parse($LastSync)
                            $targetLastWrite = (Get-Item $targetPath).LastWriteTime
                            if ($targetLastWrite -gt $lastSyncDate) {
                                $isLocallyModified = $true
                            }
                        } catch {
                            # Invalid last_sync format, skip check
                        }
                    }

                    if ($isLocallyModified) {
                        # Check for breaking change (FR-16): source removed structural markers
                        $isBreaking = Test-BreakingChange -SourcePath $file.FullPath -TargetPath $targetPath
                        if ($isBreaking) {
                            $results += [PSCustomObject]@{
                                Action = 'BREAKING_CHANGE'
                                RelativePath = $relPath
                                SourcePath = $file.FullPath
                                TargetPath = $targetPath
                            }
                        } else {
                            $results += [PSCustomObject]@{
                                Action = 'LOCALLY_MODIFIED'
                                RelativePath = $relPath
                                SourcePath = $file.FullPath
                                TargetPath = $targetPath
                            }
                        }
                    } else {
                        $results += [PSCustomObject]@{
                            Action = 'MODIFY'
                            RelativePath = $relPath
                            SourcePath = $file.FullPath
                            TargetPath = $targetPath
                        }
                    }
                }
            }
        } else {
            if ($isNeverOverwrite) {
                $results += [PSCustomObject]@{
                    Action = 'SKIP'
                    RelativePath = $relPath
                    Reason = 'never_overwrite'
                    SourcePath = $file.FullPath
                    TargetPath = $targetPath
                }
            } else {
                $results += [PSCustomObject]@{
                    Action = 'ADD'
                    RelativePath = $relPath
                    SourcePath = $file.FullPath
                    TargetPath = $targetPath
                }
            }
        }
    }

    # Check deprecated files at target
    if ($Deprecated -and $Deprecated.Count -gt 0) {
        $targetFiles = @()
        if (Test-Path $targetRootFull) {
            $targetFiles = [System.IO.Directory]::EnumerateFiles(
                $targetRootFull,
                '*',
                [System.IO.SearchOption]::AllDirectories
            )
        }
        foreach ($targetFullPath in $targetFiles) {
            $relPath = [System.IO.Path]::GetRelativePath($targetRootFull, $targetFullPath)
            $relPath = $relPath -replace '\\', '/'
            if (Test-GlobMatch -Path $relPath -Patterns $Deprecated) {
                $isNeverOverwrite = Test-GlobMatch -Path $relPath -Patterns $NeverOverwrite
                if ($isNeverOverwrite) {
                    $results += [PSCustomObject]@{
                        Action = 'SKIP'
                        RelativePath = $relPath
                        Reason = 'never_overwrite protects deletion'
                        SourcePath = $null
                        TargetPath = $targetFullPath
                    }
                } else {
                    $results += [PSCustomObject]@{
                        Action = 'DELETE'
                        RelativePath = $relPath
                        SourcePath = $null
                        TargetPath = $targetFullPath
                    }
                }
            }
        }
    }

    return $results
}

function Get-Header {
    param([string]$Title)
    $line = "=" * 100
    $startIdx = $line.IndexOf('=') + 30
    $headerText = "START: $Title"
    $endIdx = $startIdx + $headerText.Length
    $header = $line.Substring(0, $startIdx) + $headerText + $line.Substring($endIdx)
    if ($header.Length -gt 100) { $header = $header.Substring(0, 100) }
    while ($header.Length -lt 100) { $header += '=' }
    return $header
}

function Get-Footer {
    param([string]$Title)
    $line = "=" * 100
    $footerText = "END: $Title"
    $startIdx = 32
    $endIdx = $startIdx + $footerText.Length
    $footer = $line.Substring(0, $startIdx) + $footerText + $line.Substring($endIdx)
    if ($footer.Length -gt 100) { $footer = $footer.Substring(0, 100) }
    while ($footer.Length -lt 100) { $footer += '=' }
    return $footer
}

function Format-Duration {
    param([double]$Seconds)
    if ($Seconds -lt 60) {
        return "$([math]::Round($Seconds, 1)) secs"
    }
    $mins = [int]($Seconds / 60)
    $secs = [int]($Seconds % 60)
    return "$mins min $secs secs"
}

function New-DiffReport {
    param(
        [array]$Results,
        [string]$SourcePath,
        [string]$TargetPath,
        [string]$ConfigPath,
        [array]$Excluded,
        [bool]$VerboseMode,
        [datetime]$StartTime
    )
    $sb = [System.Text.StringBuilder]::new()
    $timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')

    $adds = $Results | Where-Object { $_.Action -eq 'ADD' }
    $modifies = $Results | Where-Object { $_.Action -eq 'MODIFY' }
    $deletes = $Results | Where-Object { $_.Action -eq 'DELETE' }
    $skips = $Results | Where-Object { $_.Action -eq 'SKIP' }
    $unchanged = $Results | Where-Object { $_.Action -eq 'UNCHANGED' }
    $locallyModified = $Results | Where-Object { $_.Action -eq 'LOCALLY_MODIFIED' }
    $breakingChanges = $Results | Where-Object { $_.Action -eq 'BREAKING_CHANGE' }

    [void]$sb.AppendLine((Get-Header -Title 'WORKSPACE SYNC PREVIEW'))
    [void]$sb.AppendLine("[$timestamp]")
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine("Syncing from '$SourcePath' to '$TargetPath'...")
    [void]$sb.AppendLine("  Reading '$ConfigPath'...")
    [void]$sb.AppendLine('    OK.')

    $totalChanges = $adds.Count + $modifies.Count + $locallyModified.Count + $breakingChanges.Count + $deletes.Count + $skips.Count
    $hasChanges = $totalChanges -gt 0

    if ($adds.Count -gt 0) {
        [void]$sb.AppendLine('  Comparing files...')
        for ($i = 0; $i -lt $adds.Count; $i++) {
            $idx = $i + 1
            [void]$sb.AppendLine("    [ $idx / $($adds.Count) ] Adding '$($adds[$i].RelativePath)'...")
        }
        [void]$sb.AppendLine("    $($adds.Count) new file$(if ($adds.Count -ne 1) {'s'}) found.")
    }

    if ($modifies.Count -gt 0) {
        [void]$sb.AppendLine('  Comparing modified files...')
        for ($i = 0; $i -lt $modifies.Count; $i++) {
            $idx = $i + 1
            [void]$sb.AppendLine("    [ $idx / $($modifies.Count) ] '$($modifies[$i].RelativePath)' differs...")
        }
        [void]$sb.AppendLine("    $($modifies.Count) modified file$(if ($modifies.Count -ne 1) {'s'}) found.")
    }

    if ($locallyModified.Count -gt 0) {
        [void]$sb.AppendLine('  Checking locally-modified files...')
        for ($i = 0; $i -lt $locallyModified.Count; $i++) {
            $idx = $i + 1
            [void]$sb.AppendLine("    [ $idx / $($locallyModified.Count) ] '$($locallyModified[$i].RelativePath)' LOCALLY_MODIFIED - will be overwritten...")
        }
        [void]$sb.AppendLine("    $($locallyModified.Count) locally-modified file$(if ($locallyModified.Count -ne 1) {'s'}) found.")
    }

    if ($breakingChanges.Count -gt 0) {
        [void]$sb.AppendLine('  WARNING: Breaking changes detected...')
        for ($i = 0; $i -lt $breakingChanges.Count; $i++) {
            $idx = $i + 1
            [void]$sb.AppendLine("    [ $idx / $($breakingChanges.Count) ] '$($breakingChanges[$i].RelativePath)' BREAKING_CHANGE - content migration required before overwrite...")
        }
        [void]$sb.AppendLine("    $($breakingChanges.Count) breaking change$(if ($breakingChanges.Count -ne 1) {'s'}) detected.")
    }

    [void]$sb.AppendLine('  Checking deprecated files...')
    if ($deletes.Count -gt 0) {
        for ($i = 0; $i -lt $deletes.Count; $i++) {
            $idx = $i + 1
            [void]$sb.AppendLine("    [ $idx / $($deletes.Count) ] '$($deletes[$i].RelativePath)' marked for deletion...")
        }
        [void]$sb.AppendLine("    $($deletes.Count) deprecated file$(if ($deletes.Count -ne 1) {'s'}) found.")
    } else {
        [void]$sb.AppendLine('    0 deprecated files found.')
    }

    [void]$sb.AppendLine('  Checking never-overwrite files...')
    if ($skips.Count -gt 0) {
        $skipPaths = $skips | ForEach-Object { "'$($_.RelativePath)'" }
        [void]$sb.AppendLine("    $($skips.Count) file$(if ($skips.Count -ne 1) {'s'}) protected: $($skipPaths -join ', ').")
    } else {
        [void]$sb.AppendLine('    0 files protected.')
    }

    if ($VerboseMode -and $Excluded.Count -gt 0) {
        [void]$sb.AppendLine('')
        [void]$sb.AppendLine("EXCLUDED ($($Excluded.Count)):")
        for ($i = 0; $i -lt $Excluded.Count; $i++) {
            $idx = $i + 1
            [void]$sb.AppendLine("  [ $idx / $($Excluded.Count) ] '$($Excluded[$i].File.RelativePath)' excluded -> $($Excluded[$i].Reason)")
        }
        [void]$sb.AppendLine("  $($Excluded.Count) file$(if ($Excluded.Count -ne 1) {'s'}) excluded.")
    }

    [void]$sb.AppendLine('')
    $summaryParts = @()
    $summaryParts += "$($adds.Count) add"
    $summaryParts += "$($modifies.Count) modify"
    $summaryParts += "$($locallyModified.Count) locally_modified"
    $summaryParts += "$($breakingChanges.Count) breaking_change"
    $summaryParts += "$($deletes.Count) delete"
    $summaryParts += "$($skips.Count) skip"
    $summaryParts += "$($unchanged.Count) unchanged"
    [void]$sb.AppendLine("Summary: $($summaryParts -join ', ').")

    if ($hasChanges) {
        [void]$sb.AppendLine('RESULT: CHANGES FOUND')
    } else {
        [void]$sb.AppendLine('RESULT: NO CHANGES')
    }

    $endTime = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    [void]$sb.AppendLine((Get-Footer -Title 'WORKSPACE SYNC PREVIEW'))
    [void]$sb.AppendLine("[$endTime] ($(Format-Duration -Seconds ((Get-Date) - $startTime).TotalSeconds))")

    return $sb.ToString()
}

function Invoke-Execute {
    param(
        [array]$Results,
        [string]$SourcePath,
        [string]$TargetPath,
        [string]$ConfigPath
    )
    $sb = [System.Text.StringBuilder]::new()
    $timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $startTime = Get-Date

    $adds = $Results | Where-Object { $_.Action -eq 'ADD' }
    $modifies = $Results | Where-Object { $_.Action -eq 'MODIFY' }
    $deletes = $Results | Where-Object { $_.Action -eq 'DELETE' }
    $skips = $Results | Where-Object { $_.Action -eq 'SKIP' }
    $locallyModified = $Results | Where-Object { $_.Action -eq 'LOCALLY_MODIFIED' }
    $breakingChanges = $Results | Where-Object { $_.Action -eq 'BREAKING_CHANGE' }

    [void]$sb.AppendLine((Get-Header -Title 'WORKSPACE SYNC EXECUTE'))
    [void]$sb.AppendLine("[$timestamp]")
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine("Syncing from '$SourcePath' to '$TargetPath'...")
    [void]$sb.AppendLine("  Reading '$ConfigPath'...")
    [void]$sb.AppendLine('    OK.')

    $hasErrors = $false

    # Adding files
    if ($adds.Count -gt 0) {
        [void]$sb.AppendLine('  Adding files...')
        for ($i = 0; $i -lt $adds.Count; $i++) {
            $idx = $i + 1
            [void]$sb.AppendLine("    [ $idx / $($adds.Count) ] Copying '$($adds[$i].RelativePath)'...")
            $targetDir = [System.IO.Path]::GetDirectoryName($adds[$i].TargetPath)
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            try {
                Copy-Item -Path $adds[$i].SourcePath -Destination $adds[$i].TargetPath -Force
                [void]$sb.AppendLine('      OK.')
            } catch {
                $hasErrors = $true
                [void]$sb.AppendLine("      ERROR: Failed to copy '$($adds[$i].RelativePath)' -> $($_.Exception.Message)")
            }
        }
        [void]$sb.AppendLine("    $($adds.Count) file$(if ($adds.Count -ne 1) {'s'}) added.")
    }

    # Modifying files (includes LOCALLY_MODIFIED and BREAKING_CHANGE - all get backup + overwrite)
    $allModifies = @($modifies) + @($locallyModified) + @($breakingChanges)
    if ($allModifies.Count -gt 0) {
        [void]$sb.AppendLine('  Modifying files...')
        for ($i = 0; $i -lt $allModifies.Count; $i++) {
            $idx = $i + 1
            $warningTag = if ($allModifies[$i].Action -eq 'LOCALLY_MODIFIED') { ' [LOCALLY_MODIFIED]' } elseif ($allModifies[$i].Action -eq 'BREAKING_CHANGE') { ' [BREAKING_CHANGE]' } else { '' }
            [void]$sb.AppendLine("    [ $idx / $($allModifies.Count) ] Updating '$($allModifies[$i].RelativePath)'$warningTag...")
            $backupPath = $allModifies[$i].TargetPath + '.tmp_bak'
            try {
                Copy-Item -Path $allModifies[$i].TargetPath -Destination $backupPath -Force
                Copy-Item -Path $allModifies[$i].SourcePath -Destination $allModifies[$i].TargetPath -Force
                Remove-Item -Path $backupPath -Force
                [void]$sb.AppendLine('      OK.')
            } catch {
                $hasErrors = $true
                if (Test-Path $backupPath) {
                    Copy-Item -Path $backupPath -Destination $allModifies[$i].TargetPath -Force
                    Remove-Item -Path $backupPath -Force
                }
                [void]$sb.AppendLine("      ERROR: Failed to update '$($allModifies[$i].RelativePath)' -> $($_.Exception.Message)")
            }
        }
        [void]$sb.AppendLine("    $($allModifies.Count) file$(if ($allModifies.Count -ne 1) {'s'}) modified.")
    }

    # Deleting deprecated files
    if ($deletes.Count -gt 0) {
        [void]$sb.AppendLine('  Deleting deprecated files...')
        for ($i = 0; $i -lt $deletes.Count; $i++) {
            $idx = $i + 1
            [void]$sb.AppendLine("    [ $idx / $($deletes.Count) ] Deleting '$($deletes[$i].RelativePath)'...")
            try {
                Remove-Item -Path $deletes[$i].TargetPath -Force
                [void]$sb.AppendLine('      OK.')
            } catch {
                $hasErrors = $true
                [void]$sb.AppendLine("      ERROR: Failed to delete '$($deletes[$i].RelativePath)' -> $($_.Exception.Message)")
            }
        }
        [void]$sb.AppendLine("    $($deletes.Count) file$(if ($deletes.Count -ne 1) {'s'}) deleted.")
    }

    # Skipping protected files
    if ($skips.Count -gt 0) {
        [void]$sb.AppendLine('  Skipping protected files...')
        foreach ($skip in $skips) {
            [void]$sb.AppendLine("    SKIP: '$($skip.RelativePath)' -> $($skip.Reason).")
        }
    }

    # Update last_sync
    if (-not $hasErrors) {
        [void]$sb.AppendLine("  Updating 'last_sync' timestamp...")
        try {
            $utcTimestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
            Update-LastSync -ConfigPath $ConfigPath -Timestamp $utcTimestamp
            [void]$sb.AppendLine("    OK. last_sync='$utcTimestamp'.")
        } catch {
            $hasErrors = $true
            [void]$sb.AppendLine("      ERROR: Failed to update 'last_sync' -> $($_.Exception.Message)")
        }
    }

    $summaryParts = @()
    $summaryParts += "$($adds.Count) added"
    $summaryParts += "$($modifies.Count) modified"
    $summaryParts += "$($locallyModified.Count) locally_modified"
    $summaryParts += "$($breakingChanges.Count) breaking_change"
    $summaryParts += "$($deletes.Count) deleted"
    $summaryParts += "$($skips.Count) skipped"
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine("Summary: $($summaryParts -join ', ').")

    if ($hasErrors) {
        [void]$sb.AppendLine('RESULT: PARTIAL FAIL')
    } else {
        [void]$sb.AppendLine('RESULT: OK')
    }

    $endTime = (Get-Date)
    $duration = ($endTime - $startTime).TotalSeconds
    $endTimeStr = $endTime.ToString('yyyy-MM-dd HH:mm:ss')
    [void]$sb.AppendLine((Get-Footer -Title 'WORKSPACE SYNC EXECUTE'))
    [void]$sb.AppendLine("[$endTimeStr] ($(Format-Duration -Seconds $duration))")

    return @{
        Output = $sb.ToString()
        HasErrors = $hasErrors
    }
}

function Update-LastSync {
    param([string]$ConfigPath, [string]$Timestamp)
    $configRaw = Get-Content -Path $ConfigPath -Raw -Encoding UTF8
    $config = $configRaw | ConvertFrom-Json
    $config.last_sync = $Timestamp
    $config | ConvertTo-Json -Depth 10 | Set-Content -Path $ConfigPath -Encoding UTF8
}

function Write-VerboseLog {
    param([string]$Message)
    if ($showVerbose) {
        [Console]::Error.WriteLine($Message)
    }
}

# ============================================================
# Main Execution
# ============================================================

# IS-02: Mode validation
if ($diff -and $execute) {
    Write-Error 'Cannot specify both -diff and -execute.'
    exit 2
}
if (-not $diff -and -not $execute) {
    Write-Error 'Must specify either -diff or -execute.'
    exit 2
}

# IS-01: Parse parameters
$sourceList = @(Resolve-PathParam -Value $sources -ParamName 'sources')
$targetList = @(Resolve-PathParam -Value $targets -ParamName 'targets')
$configList = @(Resolve-PathParam -Value $configs -ParamName 'configs')

# IS-14: Target-config pairing
if ($configList.Count -eq 1 -and $targetList.Count -gt 1) {
    $configList = @($configList) * $targetList.Count
}
if ($targetList.Count -ne $configList.Count) {
    Write-Error "Number of targets ($($targetList.Count)) must match number of configs ($($configList.Count)), or provide a single config."
    exit 2
}

$startTime = Get-Date
$allOutput = [System.Text.StringBuilder]::new()
$hasAnyChanges = $false
$hasAnyErrors = $false

for ($t = 0; $t -lt $targetList.Count; $t++) {
    $targetPath = $targetList[$t]
    $configPath = $configList[$t]

    # IS-03: Read config
    if (-not (Test-Path $configPath -PathType Leaf)) {
        Write-Error "Config file not found: '$configPath'."
        exit 2
    }
    try {
        $configRaw = Get-Content -Path $configPath -Raw -Encoding UTF8
        $config = $configRaw | ConvertFrom-Json
    } catch {
        Write-Error "Invalid JSON in config: '$configPath'."
        exit 2
    }

    # IS-04: Validate config
    Test-SyncConfig -Config $config -ConfigPath $configPath

    # IS-04: Check target exists
    if (-not (Test-Path $targetPath -PathType Container)) {
        Write-Error "Target path not found: '$targetPath'."
        exit 4
    }

    $configDir = [System.IO.Path]::GetDirectoryName($configPath)

    foreach ($srcEntry in $config.sources) {
        # Resolve source path relative to config file's directory
        $sourcePath = if ([System.IO.Path]::IsPathRooted($srcEntry.source)) {
            $srcEntry.source
        } else {
            [System.IO.Path]::GetFullPath([System.IO.Path]::Join($configDir, $srcEntry.source))
        }

        # IS-14: Source filtering
        $sourceMatches = $false
        foreach ($filterSource in $sourceList) {
            $filterFull = [System.IO.Path]::GetFullPath($filterSource)
            if ($sourcePath -ieq $filterFull) {
                $sourceMatches = $true
                break
            }
        }
        if (-not $sourceMatches) { continue }

        # IS-03: Check source exists
        if (-not (Test-Path $sourcePath -PathType Container)) {
            Write-Error "Source path not found: '$sourcePath'."
            exit 3
        }

        # IS-05: Discover and filter source files
        $allFiles = Get-SourceFiles -SourceRoot $sourcePath
        $filterResult = Invoke-FileFilter -SourceEntry $srcEntry -Files $allFiles

        Write-VerboseLog "Source: '$sourcePath'"
        Write-VerboseLog "  Total files: $($allFiles.Count)"
        Write-VerboseLog "  Included: $($filterResult.Included.Count)"
        Write-VerboseLog "  Excluded: $($filterResult.Excluded.Count)"

        # IS-07, IS-08: Compare against target
        $deprecated = @($srcEntry.deprecated)
        $neverOverwrite = @($srcEntry.never_overwrite)
        $results = Compare-Files -SourceFiles $filterResult.Included -TargetRoot $targetPath -Deprecated $deprecated -NeverOverwrite $neverOverwrite -LastSync $config.last_sync

        # Check for changes
        $changes = $results | Where-Object { $_.Action -in @('ADD', 'MODIFY', 'LOCALLY_MODIFIED', 'BREAKING_CHANGE', 'DELETE', 'SKIP') }
        if ($changes.Count -gt 0) { $hasAnyChanges = $true }

        if ($diff) {
            # IS-20: Generate diff report
            $report = New-DiffReport -Results $results -SourcePath $srcEntry.source -TargetPath $targetPath -ConfigPath $configPath -Excluded $filterResult.Excluded -VerboseMode:$showVerbose -StartTime $startTime
            [void]$allOutput.AppendLine($report)
            [void]$allOutput.AppendLine('')
        } elseif ($execute) {
            # IS-11, IS-21: Execute operations
            $execResult = Invoke-Execute -Results $results -SourcePath $srcEntry.source -TargetPath $targetPath -ConfigPath $configPath
            [void]$allOutput.AppendLine($execResult.Output)
            [void]$allOutput.AppendLine('')
            if ($execResult.HasErrors) { $hasAnyErrors = $true }
        }
    }
}

# Output
$outputContent = $allOutput.ToString().TrimEnd()

if ($output_file) {
    $outputFileFull = [System.IO.Path]::GetFullPath($output_file)
    $outputContent | Set-Content -Path $outputFileFull -Encoding UTF8

    # Print summary to stdout
    $adds = ($outputContent | Select-String '(\d+) add' -AllMatches).Matches
    $totalAdds = 0
    foreach ($m in $adds) { $totalAdds += [int]$m.Groups[1].Value }
    Write-Output "Summary: see full report at '$outputFileFull'."
} else {
    Write-Output $outputContent
}

# Exit codes
if ($hasAnyErrors) {
    exit 5
}
if ($hasAnyChanges) {
    exit 1
}
exit 0
