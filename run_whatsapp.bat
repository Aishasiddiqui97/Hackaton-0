@echo off
title WhatsApp Autonomous Agent – Digital FTE
cd /d "e:\Python.py\Hackaton 0"
call venv\Scripts\activate.bat

echo ============================================
echo   WhatsApp Autonomous Agent – Digital FTE
echo ============================================
echo.
echo [1] FIRST RUN – Scan QR code (headful browser)
echo [2] RUN NOW   – Session already logged in (headless)
echo [3] RUN NOW   – Session logged in (visible browser)
echo.
set /p choice="Choice (1/2/3): "

if "%choice%"=="1" (
    echo Opening browser for QR scan...
    python run_whatsapp_now.py --headful
) else if "%choice%"=="2" (
    echo Running headless...
    python run_whatsapp_now.py
) else if "%choice%"=="3" (
    echo Running with visible browser...
    python run_whatsapp_now.py --headful
) else (
    python run_whatsapp_now.py
)

echo.
pause
