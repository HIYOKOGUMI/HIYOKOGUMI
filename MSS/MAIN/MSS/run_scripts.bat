@echo off
cd /d "%~dp0\src"

echo Running fetch_urls.py...
python fetch_urls.py
if %errorlevel% neq 0 (
    echo Error: fetch_urls.py failed
    exit /b %errorlevel%
)

echo Running fetch_product.py...
python fetch_product.py
if %errorlevel% neq 0 (
    echo Error: fetch_product.py failed
    exit /b %errorlevel%
)

echo Running generate_distribution_chart.py and statistics.py simultaneously...
start "" /b python generate_distribution_chart.py
start "" /b python statistics.py

echo Waiting for generate_distribution_chart.py and statistics.py to complete...
:wait_loop
ping -n 2 127.0.0.1 >nul
tasklist /fi "imagename eq python.exe" 2>nul | find /i "generate_distribution_chart.py" >nul
if not errorlevel 1 goto wait_loop
tasklist /fi "imagename eq python.exe" 2>nul | find /i "statistics.py" >nul
if not errorlevel 1 goto wait_loop

echo All scripts executed successfully.
pause
