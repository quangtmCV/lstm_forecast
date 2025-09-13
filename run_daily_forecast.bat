@echo off
echo ========================================
echo Daily LSTM Weather Forecast System
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import tensorflow, pandas, numpy, sklearn, requests, schedule" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Available modes:
echo 1. Daily Forecast (once)
echo 2. Daily Scheduler (continuous)
echo 3. Retrain Model
echo 4. Web Dashboard Only
echo 5. Daily Forecast + Web Dashboard
echo.

set /p choice="Select mode (1-5): "

if "%choice%"=="1" (
    echo Running daily forecast (once)...
    python src/main.py --mode once --no-web
) else if "%choice%"=="2" (
    echo Running daily scheduler...
    echo Press Ctrl+C to stop
    python src/main.py --mode scheduler
) else if "%choice%"=="3" (
    echo Retraining model...
    python src/main.py --mode retrain --no-web
) else if "%choice%"=="4" (
    echo Starting web dashboard only...
    echo Dashboard will be available at: http://127.0.0.1:5000
    echo Press Ctrl+C to stop
    python src/main.py --mode web
) else if "%choice%"=="5" (
    echo Running daily forecast with web dashboard...
    python src/main.py --mode once
) else (
    echo Invalid choice. Running default mode...
    python src/main.py --mode once --no-web
)

echo.
echo Press any key to exit...
pause >nul
