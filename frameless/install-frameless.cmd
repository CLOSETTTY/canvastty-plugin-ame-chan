@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0frameless.ps1" -Action apply
pause
