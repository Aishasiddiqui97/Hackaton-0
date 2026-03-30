@echo off
REM Complete Fix and Test - All in One
echo.
echo ========================================
echo   TWITTER BROWSER FIX - COMPLETE
echo ========================================
echo.
echo This will fix the browser visibility issue.
echo.
echo WHAT HAPPENED:
echo - Old session existed but Twitter logged you out
echo - Code thought you were logged in (session file exists)
echo - But you weren't actually logged in
echo - So posting failed (couldn't find compose button)
echo.
echo WHAT'S FIXED:
echo - Browser now MUST be visible (you'll see Chrome)
echo - Better session validation (checks actual login)
echo - More logging (you'll see what's happening)
echo - Screenshots on errors (debug_before_post.png)
echo.
echo ========================================
echo.

REM Step 1: Check if server is running
echo [Step 1/5] Checking if server is running...
curl -s http://localhost:3006/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   √ Server is running
    echo.
    echo   ACTION REQUIRED:
    echo   1. Go to your SERVER TERMINAL
    echo   2. Press Ctrl+C to stop the server
    echo   3. Come back here and press any key
    echo.
    pause
) else (
    echo   ! Server not running (that's okay)
)

echo.
echo [Step 2/5] Deleting old session...
if exist "sessions\twitter" (
    rmdir /s /q "sessions\twitter"
    echo   √ Old session deleted
) else (
    echo   ! No old session found
)

echo.
echo [Step 3/5] Creating fresh session directory...
mkdir "sessions\twitter" 2>nul
echo   √ Fresh session directory ready

echo.
echo [Step 4/5] Ready to start server with fixes
echo.
echo ========================================
echo   IMPORTANT: WATCH FOR CHROME WINDOW
echo ========================================
echo.
echo When you start the server, you WILL see:
echo   1. Chrome window opens (maximized)
echo   2. Navigates to Twitter login page
echo   3. Enters username automatically
echo   4. Clicks Next
echo   5. Enters password automatically
echo   6. Clicks Log in
echo   7. If 2FA: Enter code manually in browser
echo   8. Success! Browser stays open
echo.
echo ========================================
echo.
echo ACTION REQUIRED:
echo   1. Open a NEW terminal
echo   2. Run: cd "E:\Python.py\Hackaton 0"
echo   3. Run: .\start_twitter_autonomous.bat
echo   4. WATCH for Chrome window to open
echo   5. Come back here when you see "Server ready"
echo.
pause

echo.
echo [Step 5/5] Testing with visual feedback...
echo.
echo Running visual test...
echo (This will show you each step in the browser)
echo.
python test_visual_browser.py

echo.
echo ========================================
echo   FIX COMPLETE
echo ========================================
echo.
echo Did you see the Chrome window?
echo   YES → Everything is working! 🎉
echo   NO  → Check server terminal for errors
echo.
echo Next steps:
echo   - Test again: python test_autonomous_login.py
echo   - Post manually: curl -X POST http://localhost:3006/post_tweet -H "Content-Type: application/json" -d "{\"text\":\"Test tweet\"}"
echo   - Check logs: AI_Employee_Vault\Logs\Twitter_Log.md
echo.
pause
