@echo off
pushd "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv not found. Run _InstallBuildTools.bat first.
  exit /b 1
)
.venv\Scripts\python.exe -m pytest -n auto -m "not live" --tb=short -q %*
popd
