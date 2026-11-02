@echo off
title CineMatch AI - Movie Recommendation System
color 0A

echo ===================================================================
echo     CineMatch AI - Intelligent Movie Recommendation System
echo ===================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your Windows PATH!
    echo Please install Python 3.9+ from https://www.python.org/ or Windows Store.
    echo (Make sure to check 'Add Python to PATH' during installation!)
    echo.
    pause
    exit /b
)

echo [1/2] Checking dependencies (pandas, numpy)...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo [2/2] Launching CineMatch AI Application...
echo.
python app.py

pause
