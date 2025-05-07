@echo off
echo Running pytest tests/test_buy_ticket.py with visible browser and slowmo 1000ms...

uv run python -m pytest tests/test_buy_ticket.py --headed --slowmo 1000
if %errorlevel% neq 0 (
    echo Tests failed.
) else (
    echo Tests passed.
)

echo Test run finished.
pause