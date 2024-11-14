@echo off
echo Starting cleaning process...

pushd "%~dp0\.."

echo Running detect_outliers.py...
python detect_outliers.py
if %ERRORLEVEL% NEQ 0 (
    echo detect_outliers.py encountered an error.
    popd
    exit /b %ERRORLEVEL%
)

echo Running statistics.py...
python statistics.py
if %ERRORLEVEL% NEQ 0 (
    echo statistics.py encountered an error.
    popd
    exit /b %ERRORLEVEL%
)

popd
echo Cleaning process completed.
