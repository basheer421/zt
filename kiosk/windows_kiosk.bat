@echo off
REM Zero-Trust Kiosk Launcher for Windows
REM This script launches Firefox in kiosk mode with the built app

REM Change to the script's directory
cd /d "%~dp0"

REM Set port for local server
set PORT=5173

echo Note that there has to be a web server running on port %PORT% serving the kiosk app.

REM Launch Firefox in kiosk mode
set "KIOSK_URL=https://zt-two.vercel.app"
echo Launching kiosk mode at %KIOSK_URL%

REM Common Firefox installation paths (tries multiple locations)
if exist "C:\Program Files\Mozilla Firefox\firefox.exe" (
    start "" "C:\Program Files\Mozilla Firefox\firefox.exe" --kiosk "%KIOSK_URL%" --private-window
) else if exist "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" (
    start "" "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" --kiosk "%KIOSK_URL%" --private-window
) else if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" (
    start "" "%ProgramFiles%\Mozilla Firefox\firefox.exe" --kiosk "%KIOSK_URL%" --private-window
) else (
    echo ERROR: Firefox not found!
    echo Please install Firefox or update the path in this script.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Kiosk mode launched successfully!
echo Press Alt+F4 to exit kiosk mode
echo.
echo ========================================
