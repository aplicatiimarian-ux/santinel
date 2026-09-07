@echo off
cd /d "F:\Proiecte AI\santinel"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix_git_push.ps1"
pause
