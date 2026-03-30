@echo off
REM Diagnose Login Issue
echo ========================================
echo   Login Issue Diagnostic
echo ========================================
echo.

REM Check 1: Credentials in .env
echo [Check 1/5] Checking .env file...
if not exist ".env" (
    echo   X .env file not found!
    echo   Solution: Copy .env.template to .env
    goto :end
)

findstr /C:"TWITTER_USERNAME" .env >nul
if %errorlevel% neq 0 (
    echo   X TWITTER_USERNAME not found in .env
    goto :end
)

findstr /C:"TWITTER_PASSWORD" .env >nul
if %errorlevel% neq 0 (
    echo   X TWITTER_PASSWORD not found in .env
    goto :end
)

echo   √ Credentials found in .env
echo.

REM Check 2: Twitter accessibility
echo [Check 2/5] Checking if Twitter is accessible...
curl -s -o nul -w "%%{http_code}" https://x.com > temp_status.txt
set /p STATUS=<temp_status.txt
del temp_status.txt

if "%STATUS%"=="200" (
    echo   √ Twitter is accessible
) else (
    echo   X Twitter returned status: %STATUS%
    echo   Check your internet connection
)
echo.

REM Check 3: Account format
echo [Check 3/5] Checking username format...
findstr /C:"TWITTER_USERNAME=@" .env >nul
if %errorlevel% equ 0 (
    echo   √ Username has @ symbol
    echo   Format: @AISHA726035158
) else (
    echo   ! Username might not have @ symbol
    echo   Try adding @ in .env: TWITTER_USERNAME=@AISHA726035158
)
echo.

REM Check 4: Common issues
echo [Check 4/5] Checking for common issues...
echo.
echo   Common reasons manual login fails:
echo   1. Wrong password
echo   2. Account locked/suspended
echo   3. 2FA required
echo   4. Suspicious activity detected
echo   5. Username format wrong (try with/without @)
echo.

REM Check 5: Next steps
echo [Check 5/5] Recommended next steps...
echo.
echo ========================================
echo   WHAT TO DO NOW
echo ========================================
echo.
echo 1. TEST IN REGULAR CHROME:
echo    - Open Chrome (not Playwright)
echo    - Go to: https://x.com/login
echo    - Try: @AISHA726035158
echo    - Password: Aisha97@
echo.
echo 2. IF LOGIN WORKS IN CHROME:
echo    - Session can be copied
echo    - Run: .\copy_chrome_session.bat
echo.
echo 3. IF LOGIN FAILS IN CHROME:
echo    A) Wrong password?
echo       → Reset password on Twitter
echo       → Update .env file
echo.
echo    B) Account locked?
echo       → Unlock account first
echo       → Then try automation
echo.
echo    C) 2FA required?
echo       → Complete 2FA in Chrome
echo       → Copy session
echo.
echo    D) Suspicious activity?
echo       → Complete Twitter verification
echo       → Then try again
echo.
echo 4. ALTERNATIVE: USE TWITTER API
echo    - You already have API tokens in .env
echo    - More reliable than browser automation
echo    - Run: .\switch_to_api.bat
echo.
echo ========================================
echo.

:end
echo Press any key to open Twitter login in your browser...
pause >nul

echo.
echo Opening Twitter login in your default browser...
start https://x.com/login

echo.
echo Try logging in there and tell me what happens:
echo   A) Login works → We'll copy the session
echo   B) Wrong password → Reset and update .env
echo   C) Account locked → Unlock first
echo   D) 2FA required → Complete it, then copy session
echo.
pause
