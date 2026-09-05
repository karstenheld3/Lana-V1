@echo off
pushd "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [INFO] .venv not found - running InstallBuildTools.bat...
  call "%~dp0InstallBuildTools.bat" /noPause
  if errorlevel 1 exit /b 1
)
.venv\Scripts\python.exe -m pytest -n auto -m "not live" --tb=short -q %*
popd
