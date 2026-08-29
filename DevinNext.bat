@echo off
set "DIR=%~dp0"
set "DIR=%DIR:~0,-1%"
start "" "%LOCALAPPDATA%\Programs\Devin Next\Devin - Next.exe" "%DIR%"
