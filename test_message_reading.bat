@echo off
echo ========================================
echo Message Reading Debug Test
echo ========================================
echo.
echo This will test all message reading strategies
echo and show detailed debugging information.
echo.
python test_message_reading.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Test failed! Check errors above.
    pause
    exit /b %ERRORLEVEL%
)
pause
