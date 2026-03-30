@echo off
echo ========================================
echo WhatsApp Step-by-Step Debug Test
echo ========================================
echo.
echo This will test each component individually
echo and show exactly where the problem is.
echo.
python debug_whatsapp_step_by_step.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Test failed! Check errors above.
    pause
    exit /b %ERRORLEVEL%
)
pause
