@echo off
REM Manual Login Helper - Easiest Way
echo ========================================
echo   EASIEST FIX: Manual Login Once
echo ========================================
echo.
echo Instead of debugging selectors, let's do this:
echo.
echo 1. Open browser
echo 2. YOU login manually (just once)
echo 3. Session gets saved
echo 4. Future logins: AUTOMATIC!
echo.
echo This is faster and more reliable than debugging
echo Twitter's changing selectors.
echo.
echo ========================================
echo.
echo Press any key to start manual login helper...
pause >nul

echo.
echo Starting manual login helper...
echo.
node manual_login.js

echo.
pause
