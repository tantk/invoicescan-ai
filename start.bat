@echo off
echo Starting InvoiceScan AI...
echo.

:: Start server in background
start "InvoiceScan Server" /min cmd /c "cd /d C:\dev\geminilive2\server && python main.py"

:: Wait for server to be ready
echo Waiting for server...
timeout /t 5 /nobreak >nul

:: Start desktop app in foreground
echo Server ready. Launching desktop app...
echo.
echo   F2 (hold) = Talk to agent
echo   F3        = Scan screen
echo   ESC / X   = Quit
echo.
cd /d C:\dev\geminilive2\desktop
python main.py
