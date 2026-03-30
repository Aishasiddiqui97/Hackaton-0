@echo off
echo ========================================
echo Updating Gemini API Package
echo ========================================
echo.
echo Step 1: Uninstalling old package...
pip uninstall google-generativeai -y
echo.
echo Step 2: Installing new package...
pip install google-genai
echo.
echo ========================================
echo Update Complete!
echo ========================================
echo.
echo Now you can run: python autonomous_whatsapp_agent.py
echo.
pause
