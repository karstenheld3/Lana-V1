# Lana build pipeline (LANADIST-SP01, LANADIST-IP01): sync .lana/ -> bundled, wheel -> PyApp single binary -> sign -> checksum -> cleanup.
# Output: dist\lana-{version}-win-x64.exe + dist\SHA256SUMS.txt
$ErrorActionPreference = 'Stop'

# Pinned build inputs (LANADIST-NFR-02 reproducible builds)
$PYAPP_VERSION  = '0.29.0'
$PYTHON_TARGET  = '3.12'
$TIMESTAMP_URL  = 'http://timestamp.digicert.com'
$SMOKE_TIMEOUT_SECONDS = 300  # covers PyApp first run: extraction + venv + dependency install from PyPI (EC-11)

$RootDir   = $PSScriptRoot
$VenvPy    = Join-Path $RootDir '.venv\Scripts\python.exe'
$BundleDir = Join-Path $RootDir 'src\lana\bundled'
$BuildDir  = Join-Path $RootDir 'build'
$DistDir   = Join-Path $RootDir 'dist'
$Script:CurrentStep = 0
$Script:Artifact = $null

function Fail([string]$Message) {
  if ($Script:Artifact -and (Test-Path $Script:Artifact)) {  # IG-02: no partial artifacts
    Remove-Item $Script:Artifact -Force
    Write-Host "  Removed partial artifact $Script:Artifact."
  }
  # Restore _old.exe if pre-flight renamed it and the new build never completed
  if ($Script:Artifact -and $oldExe -and (Test-Path $oldExe) -and -not (Test-Path $Script:Artifact)) {
    Rename-Item $oldExe $Script:Artifact -Force
    Write-Host "  Restored previous binary from _old.exe."
  }
  Write-Host "FAILED at step $($Script:CurrentStep): $Message"
  exit 1
}

function Step([string]$Title) {
  $Script:CurrentStep++
  Write-Host "[ $Script:CurrentStep / 8 ] $Title"
}

# ---------------------------------------------------------------------------- version from pyproject.toml (single source of truth, FR-05)
$pyprojectPath = Join-Path $RootDir 'pyproject.toml'
$versionMatch = Select-String -Path $pyprojectPath -Pattern '^version\s*=\s*"([^"]+)"'
if (-not $versionMatch) { $Script:CurrentStep = 1; Fail "cannot parse version from pyproject.toml (EC-03)." }
$Version = $versionMatch.Matches[0].Groups[1].Value
$ExeName = "lana-$Version-win-x64.exe"

Write-Host "Building Lana $Version (win-x64)..."

# ---------------------------------------------------------------------------- pre-flight: ensure target is not locked
$Script:Artifact = Join-Path $DistDir $ExeName
$oldExe = Join-Path $DistDir ($ExeName -replace '\.exe$', '_old.exe')
if (Test-Path $Script:Artifact) {
  try {
    Rename-Item $Script:Artifact $oldExe -Force -ErrorAction Stop
    Write-Host "  Pre-flight: renamed existing $ExeName to _old.exe (file was unlocked)."
  } catch {
    Write-Host "  Pre-flight: $ExeName is locked (in use by another process)." -ForegroundColor Yellow
    while ($true) {
      Write-Host '  Close all Lana instances (Devin Desktop, terminals, etc.) then press SPACE to retry...' -ForegroundColor Yellow
      $key = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
      if ($key.VirtualKeyCode -eq 32) {
        try {
          Rename-Item $Script:Artifact $oldExe -Force -ErrorAction Stop
          Write-Host '  Pre-flight: renamed to _old.exe. Continuing.'
          break
        } catch {
          Write-Host "  Still locked: $($_.Exception.Message)" -ForegroundColor Red
        }
      }
    }
  }
}

# ---------------------------------------------------------------------------- [ 1 / 8 ] toolchain
Step 'Verifying toolchain...'
if (-not (Test-Path $VenvPy)) { Fail ".venv missing - run _InstallAndCompileDependencies.bat first (EC-02)." }
$pythonVersion = (& $VenvPy --version) -replace 'Python ', ''
$cargo = Get-Command cargo -ErrorAction SilentlyContinue
if (-not $cargo) {
  $cargoHome = Join-Path $env:USERPROFILE '.cargo\bin\cargo.exe'
  if (Test-Path $cargoHome) { $env:PATH = "$(Split-Path $cargoHome);$env:PATH"; $cargo = Get-Command cargo }
}
if (-not $cargo) {
  $answer = Read-Host '  Cargo not found. Install Rust toolchain now via winget? [y/N]'
  if ($answer -eq 'y') {
    winget install Rustlang.Rustup --silent --accept-package-agreements --accept-source-agreements
    $env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
    $cargo = Get-Command cargo -ErrorAction SilentlyContinue
  }
  if (-not $cargo) { Fail 'Rust toolchain required. Install manually: https://rustup.rs (EC-01)' }
}
$cargoVersion = ((cargo --version) -split ' ')[1]
Write-Host "  Python $pythonVersion (.venv) OK. Cargo $cargoVersion OK."
$signThumbprint = $env:LANA_SIGN_THUMBPRINT
if ($signThumbprint) {
  if (-not (Get-Command signtool -ErrorAction SilentlyContinue)) { Fail 'LANA_SIGN_THUMBPRINT set but signtool.exe not on PATH - install Windows SDK (EC-09).' }
  Write-Host '  Signing ON (LANA_SIGN_THUMBPRINT set), signtool OK.'
} else {
  Write-Host '  NOTICE: LANA_SIGN_THUMBPRINT not set - binary will be UNSIGNED.'
}

# ---------------------------------------------------------------------------- [ 2 / 8 ] bundle sync + key-leak guard
Step 'Syncing bundle...'
$lanaLibrary = Join-Path $RootDir '.lana'
if (-not (Test-Path $lanaLibrary -PathType Container)) { Fail ".lana prompt library missing - bundle would lose the agent library (EC-13)." }
$bundleConfig = Join-Path $BundleDir 'config'
$bundleAgent  = Join-Path $BundleDir 'agent'
# Empty both targets first so no stale files survive (DD-08)
if (Test-Path $bundleAgent)  { Remove-Item $bundleAgent  -Recurse -Force }
if (Test-Path $bundleConfig) { Remove-Item $bundleConfig -Recurse -Force }
New-Item -ItemType Directory -Path $bundleAgent  -Force | Out-Null
New-Item -ItemType Directory -Path $bundleConfig -Force | Out-Null
# Config trio: explicit file list - .api-keys.txt NEVER syncs (DD-09)
robocopy (Join-Path $RootDir 'config') $bundleConfig 'model-registry.json' 'model-parameter-mapping.json' 'model-pricing.json' /NJH /NJS /NDL /NC /NS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { Fail "config sync failed (robocopy exit $LASTEXITCODE)." }
# Agent library: full copy from .lana/ (DD-08)
robocopy $lanaLibrary $bundleAgent /MIR /NJH /NJS /NDL /NC /NS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { Fail "agent library sync failed (robocopy exit $LASTEXITCODE)." }
# Key-leak guard (IG-05, EC-12): API_KEY assignment with a real-key-shaped value (40+ char token) aborts; short placeholders like 'sk-proj-your-key-here' pass
$keyLeaks = Get-ChildItem $BundleDir -Recurse -File | Select-String -Pattern 'API_KEY\s*=\s*["'']?[A-Za-z0-9_-]{40,}'
if ($keyLeaks) {
  $first = $keyLeaks[0]
  Write-Host "  ERROR: possible API key in '$($first.Path)' line $($first.LineNumber)."
  Fail 'key-leak guard - remove the value, keep only placeholders (IG-05).'
}
$configCount = (Get-ChildItem $bundleConfig -File).Count
$agentFiles = Get-ChildItem $bundleAgent -Recurse -File
$agentSizeMb = [Math]::Round(($agentFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "  $configCount config files, $($agentFiles.Count) agent files ($agentSizeMb MB). Key-leak scan OK."

# ---------------------------------------------------------------------------- [ 3 / 8 ] wheel
Step 'Building wheel...'
New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null
& $VenvPy -m pip show build *> $null
if ($LASTEXITCODE -ne 0) { & $VenvPy -m pip install build --quiet }  # EC-04
$wheelDir = Join-Path $BuildDir 'wheel'
& $VenvPy -m build --wheel --outdir $wheelDir $RootDir *> (Join-Path $BuildDir 'wheel-build.log')
if ($LASTEXITCODE -ne 0) { Get-Content (Join-Path $BuildDir 'wheel-build.log') | Select-Object -Last 20 | Write-Host; Fail 'wheel build failed (EC-05).' }
$wheel = Get-ChildItem $wheelDir -Filter "lana-$Version-*.whl" | Select-Object -First 1
if (-not $wheel) { Fail "wheel lana-$Version-*.whl not found in $wheelDir." }
# Wheel content guard: agent tree present, .api-keys.txt absent (TC-16, IG-05)
$wheelList = & $VenvPy -m zipfile -l $wheel.FullName 2>$null
if (-not ($wheelList | Select-String 'lana/bundled/agent/')) { Fail 'wheel is missing the bundled agent tree - package-data declaration broken.' }
if ($wheelList | Select-String 'api-keys') { Fail 'wheel contains a key file - DD-09 violated (IG-05).' }
$wheelSizeMb = [Math]::Round($wheel.Length / 1MB, 1)
Write-Host "  $($wheel.FullName) ($wheelSizeMb MB). OK."

# ---------------------------------------------------------------------------- [ 4 / 8 ] PyApp binary
Step "Building PyApp binary (pyapp $PYAPP_VERSION, this takes 1-3 minutes)..."
Get-ChildItem env: | Where-Object Name -like 'PYAPP_*' | ForEach-Object { Remove-Item "env:$($_.Name)" }  # EC-10 stale vars
$env:PYAPP_PROJECT_NAME       = 'lana'
$env:PYAPP_PROJECT_VERSION    = $Version
$env:PYAPP_PROJECT_PATH       = $wheel.FullName
$env:PYAPP_PYTHON_VERSION     = $PYTHON_TARGET
$env:PYAPP_DISTRIBUTION_EMBED = '1'
$env:PYAPP_EXEC_MODULE        = 'lana'   # python -m lana -> __main__.py -> sys.exit(main()) - exit codes propagate
$pyappRoot = Join-Path $BuildDir 'pyapp'
cargo install pyapp --version $PYAPP_VERSION --force --root $pyappRoot *> (Join-Path $BuildDir 'cargo-build.log')
if ($LASTEXITCODE -ne 0) { Get-Content (Join-Path $BuildDir 'cargo-build.log') | Select-Object -Last 20 | Write-Host; Fail 'PyApp build failed (EC-06).' }
$pyappExe = Join-Path $pyappRoot 'bin\pyapp.exe'
if (-not (Test-Path $pyappExe)) { Fail "cargo reported success but $pyappExe is missing." }
Write-Host '  OK.'

# ---------------------------------------------------------------------------- [ 5 / 8 ] copy + smoke test
Step 'Smoke test (first run extracts Python + installs dependencies, up to 5 min)...'
New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
if (Test-Path $oldExe) {  # IG-01: report before replacement (EC-07)
  Write-Host "  Replacing existing $ExeName (pre-flight renamed to _old.exe)."
}
Copy-Item $pyappExe $Script:Artifact -Force
# Refresh lana package in PyApp cache so same-version rebuilds pick up new bundled content (LANADIST-FL-0001)
$pyappCache = Join-Path $env:LOCALAPPDATA 'pyapp\data\lana'
$cachedPip = Get-ChildItem $pyappCache -Recurse -Filter 'pip.exe' -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'Scripts' } | Select-Object -First 1
if ($cachedPip) {
  & $cachedPip.FullName install --force-reinstall --no-deps $wheel.FullName *> (Join-Path $BuildDir 'pip-refresh.log')
  if ($LASTEXITCODE -ne 0) { Get-Content (Join-Path $BuildDir 'pip-refresh.log') | Select-Object -Last 10 | Write-Host; Fail 'pip refresh of lana in PyApp cache failed.' }
  Write-Host '  Refreshed lana package in PyApp cache.'
}
$smokeJob = Start-Job -ScriptBlock { param($exe) & $exe --version 2>&1 } -ArgumentList $Script:Artifact
if (-not (Wait-Job $smokeJob -Timeout $SMOKE_TIMEOUT_SECONDS)) { Stop-Job $smokeJob; Remove-Job $smokeJob -Force; Fail "smoke test timed out after $SMOKE_TIMEOUT_SECONDS s (EC-11)." }
$smokeOutput = (Receive-Job $smokeJob) -join "`n"
Remove-Job $smokeJob -Force
if ($smokeOutput -notmatch "lana $([regex]::Escape($Version))") {
  Write-Host "  ERROR: expected 'lana $Version', got '$($smokeOutput.Trim())'."
  Fail 'smoke test version mismatch (EC-08).'
}
Write-Host "  lana --version -> lana $Version. OK."

# ---------------------------------------------------------------------------- [ 6 / 8 ] signing
if ($signThumbprint) {
  Step 'Signing...'
  signtool sign /sha1 $signThumbprint /fd SHA256 /tr $TIMESTAMP_URL /td SHA256 $Script:Artifact
  if ($LASTEXITCODE -ne 0) { Fail 'signing failed - artifact removed (EC-09, IG-02).' }
  Write-Host '  Signed + timestamped. OK.'
} else {
  Step 'Signing... SKIPPED (no certificate).'
}

# ---------------------------------------------------------------------------- [ 7 / 8 ] checksum + report
Step 'Checksum...'
$hash = (Get-FileHash $Script:Artifact -Algorithm SHA256).Hash.ToLower()
"$hash *$ExeName" | Set-Content (Join-Path $DistDir 'SHA256SUMS.txt') -Encoding ascii
Write-Host '  SHA256SUMS.txt written. OK.'

# ---------------------------------------------------------------------------- [ 8 / 8 ] cleanup bundled build artifacts
Step 'Cleaning build artifacts...'
if (Test-Path $bundleAgent) { Remove-Item $bundleAgent -Recurse -Force }
if (Test-Path $bundleConfig) { Remove-Item $bundleConfig -Recurse -Force }
New-Item -ItemType Directory -Path $bundleAgent -Force | Out-Null
New-Item -ItemType Directory -Path $bundleConfig -Force | Out-Null
Write-Host '  src/lana/bundled/agent/ and config/ cleaned (build-time only, not tracked in git).'

if (Test-Path $oldExe) { Remove-Item $oldExe -Force -ErrorAction SilentlyContinue; Write-Host '  Deleted _old.exe.' }

$sizeMb = [Math]::Round((Get-Item $Script:Artifact).Length / 1MB, 0)
$signedLabel = if ($signThumbprint) { 'signed' } else { 'unsigned' }
Write-Host "DONE: dist\$ExeName ($sizeMb MB, $signedLabel)"
exit 0
