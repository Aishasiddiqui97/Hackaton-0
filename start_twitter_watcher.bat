@echo off
REM Start Twitter Watcher
echo Starting Twitter Watcher...
cd /d "%~dp0"
python scripts/twitter_watcher.py
