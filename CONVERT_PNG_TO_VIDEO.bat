@echo off
setlocal
cd /d "%~dp0"
title KIRTSOY Zero-Loss Video Compiler (ProRes 4444 and WebM Alpha)

echo ========================================================
echo  KIRTSOY 3D INTRO -- AUTOMATIC ZERO-LOSS VIDEO COMPILER
echo ========================================================
echo.

if "%~1"=="" (
    echo [*] Searching for latest kirtsoy_intro ZIP archive...
    python -u "%~dp0convert_png_to_video.py"
) else (
    echo [*] Processing dropped file: %~1
    python -u "%~dp0convert_png_to_video.py" "%~1"
)

echo.
pause
