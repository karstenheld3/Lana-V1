@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Determine paths (script lives in workspace root)
set ROOT_DIR=%~dp0
set SRC_DIR=%ROOT_DIR%src
set VENV_DIR=%ROOT_DIR%.venv
set VENV_PY=%VENV_DIR%\Scripts\python.exe
set VENV_UV=%VENV_DIR%\Scripts\uv.exe

echo ==================================================
echo Lana V1 - Install Dependencies
echo Root dir : %ROOT_DIR%
echo Src dir  : %SRC_DIR%
echo Venv dir : %VENV_DIR%
echo ==================================================

REM Ensure virtual environment exists (prefer Python 3.12, fallback to 3.13)
if exist "%VENV_PY%" (
  echo [OK] Virtual environment already exists.
) else (
  echo [INFO] Creating virtual environment...
  set PY_CMD=
  where py >nul 2>nul
  if not errorlevel 1 set PY_CMD=py -3.12
  if not defined PY_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set PY_CMD=python
  )
  if not defined PY_CMD (
    echo [INFO] Python not found - running _InstallBuildTools.bat...
    call "%~dp0_InstallBuildTools.bat" /noPause /skipDeps
    if errorlevel 1 exit /b 1
    set PY_CMD=py -3.12
    if not defined PY_CMD set PY_CMD=python
  )
  %PY_CMD% -m venv "%VENV_DIR%" 2>nul
  if errorlevel 1 (
    echo [WARN] venv creation failed with '%PY_CMD%'. Trying 'py -3.13'...
    py -3.13 -m venv "%VENV_DIR%"
    if errorlevel 1 (
      echo [ERROR] Failed to create virtual environment.
      if /i not "%~1"=="/noPause" pause
      exit /b 1
    )
  )
  echo [OK] Virtual environment created at %VENV_DIR%.
)

REM Upgrade pip inside venv
echo [INFO] Upgrading pip...
"%VENV_PY%" -m pip install -U pip >nul
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip in the virtual environment.
  if /i not "%~1"=="/noPause" pause
  exit /b 1
)

REM Ensure 'uv' is installed in the venv (fast resolver)
if exist "%VENV_UV%" (
  echo [OK] uv is already installed in the venv.
) else (
  echo [INFO] Installing uv into the venv...
  "%VENV_PY%" -m pip install uv >nul
  if errorlevel 1 (
    echo [ERROR] Failed to install 'uv' in the virtual environment.
    if /i not "%~1"=="/noPause" pause
    exit /b 1
  )
)

REM Install project in editable mode with dev dependencies
echo [INFO] Installing lana + dev dependencies...
pushd "%ROOT_DIR%" >nul
"%VENV_UV%" pip install -e .[dev]
if errorlevel 1 (
  echo [WARN] Dependency installation failed via 'uv'. Trying 'uv --native-tls'...
  "%VENV_UV%" --native-tls pip install -e .[dev]
  if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    popd >nul
    if /i not "%~1"=="/noPause" pause
    exit /b 1
  )
)
popd >nul

REM Compile/export pinned requirements.txt for reproducible builds
echo [INFO] Generating requirements.txt at repo root...
"%VENV_UV%" pip compile "%ROOT_DIR%pyproject.toml" -o "%ROOT_DIR%requirements.txt" >nul 2>nul
if errorlevel 1 (
  echo [WARN] 'uv pip compile' failed. Falling back to 'pip freeze'.
  "%VENV_UV%" pip freeze > "%ROOT_DIR%requirements.txt"
  if errorlevel 1 (
    echo [ERROR] Failed to generate requirements.txt.
    if /i not "%~1"=="/noPause" pause
    exit /b 1
  ) else (
    echo [OK] requirements.txt generated via pip freeze.
  )
) else (
  echo [OK] requirements.txt generated via 'uv pip compile'.
)

echo.
echo [DONE] Dependencies installed. Activate the venv with:
echo   %VENV_DIR%\Scripts\activate
echo.
echo To run lana:
echo   lana
echo.
echo To run tests:
echo   _test.bat
echo.

if /i "%~1"=="/noPause" exit /b 0

pause
exit /b 0
