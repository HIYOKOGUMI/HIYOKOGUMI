@echo off
echo Starting all tasks...

echo Running scraping tasks...
call run_scraping.bat
if %ERRORLEVEL% NEQ 0 (
    echo scraping.bat encountered an error.
    exit /b %ERRORLEVEL%
)

echo Running cleaning tasks...
call run_cleaning.bat
if %ERRORLEVEL% NEQ 0 (
    echo cleaning.bat encountered an error.
    exit /b %ERRORLEVEL%
)

echo All tasks completed successfully.
