@echo off
echo Running pytest tests/test_gym.py...

uv run python -m pytest tests/test_gym.py
if %errorlevel% neq 0 (
    echo Tests failed.
) else (
    echo Tests passed.
)

echo Test run finished.
pause