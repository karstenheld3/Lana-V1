@echo off
setlocal EnableExtensions

REM Lana ship pipeline launcher (LANADIST-SP01 FR-03). Logic lives in _ship.ps1.
where pwsh >nul 2>nul
if errorlevel 1 (
  echo [ERROR] PowerShell 7 'pwsh' not found. Install: winget install Microsoft.PowerShell
  pause
  exit /b 1
)

pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0_ship.ps1"
if errorlevel 1 (
  echo.
  echo [ERROR] Ship pipeline failed. See output above.
  pause
  exit /b 1
)

pause
exit /b 0
