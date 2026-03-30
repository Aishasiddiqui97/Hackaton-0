@echo off
echo ============================================================
echo AUTONOMOUS WHATSAPP BUSINESS AGENT
echo ============================================================
echo.
echo This bot will:
echo   1. Open WhatsApp Web
echo   2. Ask "QR CODE SCAN KARO" if QR appears
echo   3. Scan for unread chats every 15 seconds
echo   4. Read customer messages (ONLY incoming)
echo   5. Generate professional replies
echo   6. Send replies automatically
echo   7. Loop forever (24/7 operation)
echo.
echo ============================================================
echo EXPECTED OUTPUT:
echo ============================================================
echo [TIME] STEP 1: Navigating to https://web.whatsapp.com
echo [TIME] ⚠️ QR CODE SCAN KARO - Please scan QR code
echo [TIME] ✅ Found 15 total chats in list
echo [TIME] 🔔 UNREAD found: John Doe
echo [TIME] CONTACT: John Doe | MSG: Hello... | REPLY: Thank you...
echo ============================================================
echo.
echo Starting autonomous agent now...
echo.

python autonomous_whatsapp_agent.py

echo.
echo ============================================================
echo Agent stopped. Press any key to exit...
echo ============================================================
pause >nul
