@echo off
echo ========================================
echo Fix Facebook Credentials
echo ========================================
echo.
echo This will:
echo 1. Get your correct Page ID
echo 2. Get your Page Access Token
echo 3. Update .env file automatically
echo 4. Test posting
echo.
pause

python get_facebook_page_id.py

pause
