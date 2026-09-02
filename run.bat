@echo off
echo Starting AI Global Pulse Dashboard...
powershell -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
pause
