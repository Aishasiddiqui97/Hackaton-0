@echo off
echo ========================================
echo Reset WhatsApp Session
echo ========================================
echo.
echo This will delete the old WhatsApp session
echo so you can scan a fresh QR code.
echo.
pause

echo Deleting whatsapp_session folder...
if exist "whatsapp_session" (
    rmdir /s /q whatsapp_session
    echo ✅ Session deleted successfully!
) else (
    echo ℹ️  No existing session found.
)

echo.
echo ========================================
echo Now run one of these commands:
echo ========================================
echo.
echo 1. For testing (shows browser):
echo    python whatsapp_agent.py --headful
echo.
echo 2. For debug test:
echo    .\debug_whatsapp.bat
echo.
pause
