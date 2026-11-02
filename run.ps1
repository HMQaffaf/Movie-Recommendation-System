# CineMatch AI - PowerShell Launcher
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "    CineMatch AI - Intelligent Movie Recommendation System         " -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python is not found in your PATH!" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/ or the Microsoft Store." -ForegroundColor Yellow
    Write-Host "Make sure 'Add Python to PATH' is checked during setup." -ForegroundColor Yellow
    Read-Host "Press Enter to exit..."
    exit
}

Write-Host "[1/2] Installing requirements (pandas, numpy)..." -ForegroundColor Green
pip install -r requirements.txt --quiet --disable-pip-version-check

Write-Host "[2/2] Starting CineMatch AI..." -ForegroundColor Green
python app.py
