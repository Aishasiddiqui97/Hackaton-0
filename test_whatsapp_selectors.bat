@echo off
echo ========================================
echo Testing Fixed WhatsApp Selectors
echo ========================================
echo.
python test_whatsapp_selectors.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Test failed! Check the errors above.
    pause
    exit /b %ERRORLEVEL%
)
pause
