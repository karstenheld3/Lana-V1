@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Lana V1 - Install Build Tools (Python 3.12+, Rust/Cargo)
REM Idempotent: installs missing tools via winget, then runs _InstallAndCompileDependencies.bat
REM Usage: _InstallBuildTools.bat           (interactive, pauses at end)
REM        _InstallBuildTools.bat /noPause  (non-interactive, called from _build.ps1)

set NO_PAUSE=%~1

echo ==================================================
echo Lana V1 - Install Build Tools
echo ==================================================

REM --- Check winget availability ---
where winget >nul 2>nul
if errorlevel 1 (
  echo [ERROR] winget not found. Install App Installer from Microsoft Store.
  if /i not "%NO_PAUSE%"=="/noPause" pause
  exit /b 1
)

REM --- Python 3.12+ ---
set PY_FOUND=0
where py >nul 2>nul
if not errorlevel 1 (
  py -3.12 --version >nul 2>nul
  if not errorlevel 1 (
    echo [OK] Python 3.12 found via py launcher.
    set PY_FOUND=1
  )
)
if "%PY_FOUND%"=="0" (
  where python >nul 2>nul
  if not errorlevel 1 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
    echo [INFO] Found python %PY_VER%
    echo %PY_VER% | findstr /r "^3\.1[2-9] ^3\.[2-9][0-9]" >nul
    if not errorlevel 1 (
      echo [OK] Python %PY_VER% meets version requirement.
      set PY_FOUND=1
    )
  )
)
if "%PY_FOUND%"=="0" (
  echo [INFO] Python 3.12+ not found. Installing via winget...
  winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
  if errorlevel 1 (
    echo [ERROR] Failed to install Python 3.12.
    if /i not "%NO_PAUSE%"=="/noPause" pause
    exit /b 1
  )
  echo [OK] Python 3.12 installed.
  REM Refresh PATH for current session
  set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
)

REM --- Rust/Cargo ---
set CARGO_FOUND=0
where cargo >nul 2>nul
if not errorlevel 1 (
  echo [OK] Cargo found on PATH.
  set CARGO_FOUND=1
)
if "%CARGO_FOUND%"=="0" (
  if exist "%USERPROFILE%\.cargo\bin\cargo.exe" (
    echo [OK] Cargo found in ~/.cargo/bin.
    set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    set CARGO_FOUND=1
  )
)
if "%CARGO_FOUND%"=="0" (
  echo [INFO] Rust/Cargo not found. Installing via winget...
  winget install Rustlang.Rustup --silent --accept-package-agreements --accept-source-agreements
  if errorlevel 1 (
    echo [ERROR] Failed to install Rust toolchain.
    if /i not "%NO_PAUSE%"=="/noPause" pause
    exit /b 1
  )
  set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
  echo [OK] Rust toolchain installed.
)

REM --- Now run dependency installer (venv + pip install) ---
REM Skip when called from _InstallAndCompileDependencies.bat (/skipDeps) to avoid circular call
set SKIP_DEPS=0
if /i "%~2"=="/skipDeps" set SKIP_DEPS=1
if "%SKIP_DEPS%"=="0" (
  echo.
  echo [INFO] Running _InstallAndCompileDependencies.bat...
  call "%~dp0_InstallAndCompileDependencies.bat" /noPause
  if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    if /i not "%NO_PAUSE%"=="/noPause" pause
    exit /b 1
  )
)

echo.
echo [DONE] All build tools and dependencies installed.
if /i not "%NO_PAUSE%"=="/noPause" pause
exit /b 0
