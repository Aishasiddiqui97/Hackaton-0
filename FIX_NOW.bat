@echo off
cls
echo.
echo ========================================
echo   TWITTER INTEGRATION - FINAL STEP
echo ========================================
echo.
echo SITUATION:
echo   - Everything is built and ready
echo   - Automatic login has selector issues
echo   - Solution: Login manually ONCE
echo.
echo WHAT HAPPENS NOW:
echo   1. Browser opens
echo   2. You login manually (2 minutes)
echo   3. Session saves automatically
echo   4. Future logins: INSTANT
echo.
echo ========================================
echo.
echo Ready to fix this in 2 minutes?
echo.
pause

cls
echo.
echo ========================================
echo   STEP 1: Manual Login
echo ========================================
echo.
echo Browser will open in 3 seconds...
echo.
echo WHAT TO DO IN THE BROWSER:
echo   1. Enter username: @AISHA726035158
echo   2. Click Next
echo   3. Enter password: Aisha97@
echo   4. Click Log in
echo   5. Complete 2FA if asked
echo   6. Wait for home page
echo.
echo The script will detect when you're logged in
echo and save the session automatically.
echo.
timeout /t 3 >nul

node manual_login.js

echo.
echo ========================================
echo   STEP 2: Test Automatic Login
echo ========================================
echo.
echo Now let's test if the session was saved.
echo.
echo Press any key to start the server...
pause >nul

echo.
echo Starting server in NEW terminal...
echo.
start cmd /k "cd /d "%~dp0" && .\start_twitter_autonomous.bat"

echo.
echo ========================================
echo   WATCH THE NEW TERMINAL
echo ========================================
echo.
echo You should see:
echo   - Server starts
echo   - Checks session
echo   - "Logged in (session restored)"  ← INSTANT!
echo   - "Server ready"
echo.
echo If you see that, SUCCESS! ✅
echo.
echo Press any key to test posting a tweet...
pause >nul

echo.
echo ========================================
echo   STEP 3: Test Tweet Posting
echo ========================================
echo.
echo Testing autonomous tweet posting...
echo.
python test_autonomous_login.py

echo.
echo ========================================
echo   COMPLETE!
echo ========================================
echo.
echo If you saw:
echo   ✅ Auto-login successful
echo   ✅ Tweet posted successfully
echo.
echo Then your Twitter integration is WORKING!
echo.
echo NEXT STEPS:
echo   - Post tweets: curl -X POST http://localhost:3006/post_tweet -H "Content-Type: application/json" -d "{\"text\":\"Your tweet\"}"
echo   - Start watcher: .\start_twitter_watcher.bat
echo   - Check dashboard: AI_Employee_Vault\Dashboard.md
echo.
echo ========================================
echo.
pause
