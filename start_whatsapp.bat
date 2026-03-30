@echo off
REM Quick launcher for WhatsApp Agent - All modes

:menu
cls
echo ========================================
echo WhatsApp Autonomous Agent - Launcher
echo ========================================
echo.
echo Select Mode:
echo.
echo 1. Test Input Box (Recommended First)
echo 2. First Time Setup (QR Scan)
echo 3. Run Once (Single Scan)
echo 4. Autonomous Mode (Continuous)
echo 5. Loop Mode (Custom Interval)
echo 6. Force GPU Mode (If input box fails)
echo 7. Clear Session and Restart
echo 8. View Logs
echo 9. Exit
echo.
set /p choice="Enter choice (1-9): "

if "%choice%"=="1" goto test
if "%choice%"=="2" goto setup
if "%choice%"=="3" goto once
if "%choice%"=="4" goto auto
if "%choice%"=="5" goto loop
if "%choice%"=="6" goto force
if "%choice%"=="7" goto clear
if "%choice%"=="8" goto logs
if "%choice%"=="9" goto end
goto menu

:test
echo.
echo Testing input box rendering...
python test_input_box.py
pause
goto menu

:setup
echo.
echo First time setup - QR scan required
echo Browser will open, please scan QR code
python whatsapp_agent.py --headful
pause
goto menu

:once
echo.
echo Running single scan...
python whatsapp_agent.py --headful
pause
goto menu

:auto
echo.
echo Starting autonomous mode (continuous)...
echo Press Ctrl+C to stop
python autonomous_whatsapp_agent.py
pause
goto menu

:loop
echo.
set /p interval="Enter scan interval in seconds (default 120): "
if "%interval%"=="" set interval=120
echo Starting loop mode (scanning every %interval% seconds)...
echo Press Ctrl+C to stop
python whatsapp_agent.py --loop --interval %interval% --headful
pause
goto menu

:force
echo.
echo Starting with FORCE GPU rendering...
python whatsapp_agent_force_gpu.py
pause
goto menu

:clear
echo.
echo WARNING: This will delete your WhatsApp session
echo You will need to scan QR code again
set /p confirm="Are you sure? (y/n): "
if /i "%confirm%"=="y" (
    rmdir /s /q whatsapp_session
    echo Session cleared!
    echo Run option 2 to setup again
) else (
    echo Cancelled
)
pause
goto menu

:logs
echo.
echo Recent logs:
echo ========================================
if exist logs\whatsapp_agent.log (
    powershell -command "Get-Content logs\whatsapp_agent.log -Tail 30"
) else (
    echo No logs found yet
)
echo ========================================
pause
goto menu

:end
echo.
echo Goodbye!
exit
