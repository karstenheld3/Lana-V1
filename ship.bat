@echo off
setlocal EnableExtensions

REM Lana version bump launcher. Analyzes commits since last tag, determines semver bump, updates pyproject.toml.
where pwsh >nul 2>nul
if errorlevel 1 (
  echo [ERROR] PowerShell 7 'pwsh' not found. Install: winget install Microsoft.PowerShell
  pause
  exit /b 1
)

pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0ship.ps1"
if errorlevel 1 (
  echo.
  echo [ERROR] Version bump failed. See output above.
  pause
  exit /b 1
)

pause
exit /b 0
