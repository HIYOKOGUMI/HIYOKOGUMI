@echo off
echo Starting scraping process...

pushd "%~dp0\.."

echo Running fetch_urls.py...
python fetch_urls.py
if %ERRORLEVEL% NEQ 0 (
    echo fetch_urls.py encountered an error.
    popd
    exit /b %ERRORLEVEL%
)

echo Running fetch_product.py...
python fetch_product.py
if %ERRORLEVEL% NEQ 0 (
    echo fetch_product.py encountered an error.
    popd
    exit /b %ERRORLEVEL%
)

echo Running generate_distribution_chart.py...
python generate_distribution_chart.py
if %ERRORLEVEL% NEQ 0 (
    echo generate_distribution_chart.py encountered an error.
    popd
    exit /b %ERRORLEVEL%
)

popd
echo Scraping process completed.
