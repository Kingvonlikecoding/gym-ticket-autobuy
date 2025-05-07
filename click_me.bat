@echo off
:: 设置标题
title 自动化购票测试运行器

:: 检查 settings.json 是否存在
if not exist "config/settings.json" (
    echo ❌ 找不到 config/settings.json，请先运行 init.bat 完成初始化！
    pause
    exit /b
)

:: 运行测试
echo.
echo 正在运行...
uv run python -m pytest ./tests/test_buy_ticket.py

:: 完成
echo.
echo ✅ 完成！
pause