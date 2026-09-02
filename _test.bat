@echo off
pushd "%~dp0"
.venv\Scripts\python.exe -m pytest -n auto -m "not live" --tb=short -q %*
popd
