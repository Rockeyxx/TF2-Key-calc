@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "iwr -useb https://raw.githubusercontent.com/Rockeyxx/TF2-Key-calc/main/run.ps1 | iex"
pause
