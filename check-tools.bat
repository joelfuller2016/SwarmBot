@echo off
echo Checking for development tools...
echo.

echo Node.js:
where node >nul 2>&1
if %errorlevel%==0 (
    node --version
) else (
    echo Node.js is NOT installed
)
echo.

echo NPM:
where npm >nul 2>&1
if %errorlevel%==0 (
    npm --version
) else (
    echo NPM is NOT installed
)
echo.

echo NPX:
where npx >nul 2>&1
if %errorlevel%==0 (
    npx --version
) else (
    echo NPX is NOT installed
)
echo.

echo UVX (Python):
where uvx >nul 2>&1
if %errorlevel%==0 (
    uvx --version
) else (
    echo UVX is NOT installed
    echo Checking for Python and UV:
    where python >nul 2>&1
    if %errorlevel%==0 (
        echo Python is installed:
        python --version
        echo Checking if UV is installed via pip:
        python -m pip show uv >nul 2>&1
        if %errorlevel%==0 (
            echo UV is installed via pip
        ) else (
            echo UV is NOT installed via pip
        )
    ) else (
        echo Python is NOT installed
    )
)
echo.
echo PATH environment variable locations:
echo %PATH%
