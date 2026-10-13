@echo off
title KIRTSOY - Liquid Metal & 3D Logo Studio
color 0B
cd /d "%~dp0"

echo =========================================================================
echo   KIRTSOY - LIQUID METAL & 3D CHROME LOGO STUDIO
echo =========================================================================
echo.

echo [1/3] Checking background server status...
netstat -ano | findstr ":8590 " >nul
if errorlevel 1 (
    echo [INFO] Starting Python background server on port 8590...
    start /b "" python server.py >nul 2>&1
    timeout /t 2 /nobreak >nul
) else (
    echo [INFO] Server is already running on port 8590.
)

echo [2/3] Opening 3D Studio in your browser...
start http://localhost:8590

echo [3/3] Ready!
echo =========================================================================
echo   Studio launched at http://localhost:8590
echo =========================================================================
echo.
timeout /t 3 >nul
