REM filepath: D:\code\python\selenium\gymticket\gym_visible.bat
@echo off
cd /d %~dp0
echo Running pytest tests/test_gym.py with visible browser and slowmo 1000ms...
uv run python -m pytest tests/test_gym.py --headed --slowmo 1000
if %errorlevel% neq 0 (
    echo Tests failed.
) else (
    echo Tests passed.
)
echo Test run finished.
pause
