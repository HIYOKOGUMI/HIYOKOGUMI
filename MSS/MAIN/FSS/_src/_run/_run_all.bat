@echo off
cd /d "%~dp0"
cd ..

echo Running _fetch_urls.py
python _fetch_urls.py
if %ERRORLEVEL% neq 0 (
    echo _fetch_urls.py failed!
    pause
    exit /b %ERRORLEVEL%
)

echo Running _fetch_product.py
python _fetch_product.py
if %ERRORLEVEL% neq 0 (
    echo _fetch_product.py failed!
    pause
    exit /b %ERRORLEVEL%
)

echo Running _suggestion.py
python _suggestion.py
if %ERRORLEVEL% neq 0 (
    echo _suggestion.py failed!
    pause
    exit /b %ERRORLEVEL%
)

echo Running send_to_gchat.py
cd send
python send_to_gchat.py
if %ERRORLEVEL% neq 0 (
    echo send_to_gchat.py failed!
    pause
    exit /b %ERRORLEVEL%
)

echo All scripts executed successfully.
