REM filepath: D:\code\python\selenium\gymticket\gym.bat
@echo off
cd /d %~dp0
echo Running pytest tests/test_gym.py
uv run python -m pytest tests/test_gym.py
if %errorlevel% neq 0 (
    echo Tests failed.
) else (
    echo Tests passed.
)
echo Test run finished.
pause
