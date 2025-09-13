@echo off
echo ========================================
echo Daily LSTM Weather Forecast System
echo ========================================
echo.

cd /d "%~dp0"

echo Starting daily forecast scheduler...
echo This will run forecasts every day at 6:00 AM
echo Press Ctrl+C to stop
echo.

python src/main.py --mode scheduler

pause
