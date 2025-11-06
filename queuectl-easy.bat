@echo off
REM QueueCTL Easy Launcher for Windows
REM Usage: queuectl-easy.bat [command]

if "%1"=="" (
    echo Starting QueueCTL with ASCII art...
    python queuectl.py
) else if "%1"=="add" (
    python queuectl.py add %2 %3 %4 %5 %6 %7 %8 %9
) else (
    python queuectl.py %*
)