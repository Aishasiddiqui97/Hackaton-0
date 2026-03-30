@echo off
title WhatsApp Business Agent – Digital FTE
cd /d "e:\Python.py\Hackaton 0"

echo ============================================
echo   WhatsApp Business Agent – Digital FTE
echo ============================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [1] FIRST RUN (scan QR code) – headful mode
echo [2] NORMAL RUN – single pass (headless)
echo [3] LOOP MODE – continuous monitoring every 2 minutes (headless)
echo [4] LOOP MODE – headful (visible browser, continuous)
echo.
set /p choice="Enter choice (1/2/3/4): "

if "%choice%"=="1" (
    echo Starting in HEADFUL mode for QR scan...
    python whatsapp_agent.py --headful
) else if "%choice%"=="2" (
    echo Starting single-pass headless scan...
    python whatsapp_agent.py
) else if "%choice%"=="3" (
    echo Starting continuous loop (headless, every 120s)...
    python whatsapp_agent.py --loop --interval 120
) else if "%choice%"=="4" (
    echo Starting continuous loop (headful, every 120s)...
    python whatsapp_agent.py --loop --interval 120 --headful
) else (
    echo Invalid choice. Running single-pass headless by default...
    python whatsapp_agent.py
)

echo.
echo Agent session ended.
pause
