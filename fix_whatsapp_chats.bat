@echo off
cls
echo ============================================================
echo WhatsApp Business Agent - Quick Fix Guide
echo ============================================================
echo.
echo If the bot is not detecting chats, follow these steps:
echo.
echo STEP 1: Run the bot with visible browser
echo ----------------------------------------------
python whatsapp_agent.py --headful --loop
echo.
echo STEP 2: When you see "No chats detected" error:
echo ----------------------------------------------
echo 1. DO NOT close the terminal
echo 2. Look at the browser window that opened
echo 3. If you see WhatsApp Web but no chats:
echo    - Press F5 to refresh the page manually
echo    - WAIT 30 seconds for chats to load
echo    - The bot will automatically detect them!
echo.
echo STEP 3: If still not working:
echo ----------------------------------------------
echo 1. Close the browser window
echo 2. Check your internet connection
echo 3. Open WhatsApp on your phone
echo 4. Make sure it has internet
echo 5. Run this script again
echo.
echo ============================================================
echo Current Status: Running bot now...
echo ============================================================
echo.

REM Run the bot
python whatsapp_agent.py --headful --loop

pause
