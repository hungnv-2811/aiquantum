@echo off
REM ============================================================
REM  SmartAudit-Quantum - Chay dashboard demo
REM  Doi AQ2026-064 | AI-Quantum Challenge 2026
REM
REM  Phuc vu prototype/ qua HTTP server cuc bo thay vi mo bang
REM  file:// - mot so trinh duyet chan tai font qua file:// vi CORS.
REM  Khong can mang: Chart.js va font da dong goi trong vendor/.
REM ============================================================

setlocal
set PORT=8000
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python trong PATH.
    echo       Cai Python tu https://python.org roi chay lai.
    echo.
    pause
    exit /b 1
)

python scripts\check_environment.py
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo   SmartAudit-Quantum - dashboard dang chay
echo   ---------------------------------------
echo   Dia chi : http://localhost:%PORT%
echo   Dung lai: nhan Ctrl+C
echo.

start "" "http://localhost:%PORT%"
python -m http.server %PORT% --bind 127.0.0.1 --directory prototype

endlocal
