@echo off
echo Running pytest tests/test_basketball.py...

uv run python -m pytest tests/test_basketball.py
if %errorlevel% neq 0 (
    echo Tests failed.
) else (
    echo Tests passed.
)

echo Test run finished.
pause