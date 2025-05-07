@echo off
echo --- Initializing Project ---

echo Checking for uv...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv not found. Installing uv...
    pip install uv
    if %errorlevel% neq 0 (
        echo Error: Failed to install uv. Please ensure Python and pip are in your system's PATH.
        pause
        exit /b 1
    )
    echo uv installed successfully.
) else (
    echo uv found.
)

echo Synchronizing dependencies with uv sync...
uv sync
if %errorlevel% neq 0 (
    echo Error: Failed to synchronize dependencies. Please check your requirements.txt or pyproject.toml file.
    pause
    exit /b 1
)
echo Dependencies synchronized.

echo Creating config directory...
if not exist config mkdir config
if %errorlevel% neq 0 (
    echo Error: Failed to create config directory.
    pause
    exit /b 1
)
echo config directory created (or already exists).

echo Creating initial settings.json...
rem Create an empty JSON object initially, will be overwritten
echo {} > config\settings.json
if %errorlevel% neq 0 (
    echo Error: Failed to create settings.json.
    pause
    exit /b 1
)
echo settings.json created.

echo --- Configuration ---
set /p username="Enter username: "
set /p password="Enter password: "

echo Writing configuration to config\settings.json...
rem Construct the JSON string. Careful with quotes and batch escaping.
rem Using ^" to escape quotes within echo when redirecting is common.
echo {^"username^": ^"%username%^", ^"password^": ^"%password%^"} > config\settings.json
if %errorlevel% neq 0 (
    echo Error: Failed to write settings to settings.json.
    pause
    exit /b 1
)
echo Configuration saved to config\settings.json.
echo --- Configuration Complete ---

echo Initialization complete.
pause
exit /b 0