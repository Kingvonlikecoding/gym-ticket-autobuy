@echo off
:: 设置标题
title 自动化购票初始化配置器

cls
echo 正在初始化自动化测试环境...

:: 检查 uv 是否安装
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 uv，请先安装 https://github.com/astral-sh/uv
    pause
    exit /b
)

:: 安装依赖
echo.
echo 正在安装依赖...
uv sync --no-dev
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败！请检查网络或 pyproject.toml
    pause
    exit /b
)

:: 创建 config 目录（如果不存在）
if not exist "config" mkdir config

:: 检查是否存在 settings.example.json
if not exist "config/settings.example.json" (
    echo ❌ 找不到 settings.example.json 模板文件！
    pause
    exit /b
)

:: 如果没有 settings.json 则从 example 复制
if not exist "config/settings.json" (
    echo.
    echo 未找到 settings.json，正在从 example 创建...
    copy /Y "config/settings.example.json" "config/settings.json" >nul
)

:: 检查是否有已保存的账号信息
set "USER_JSON=.user.json"
set "USERNAME="
set "PASSWORD="

if exist "%USER_JSON%" (
    echo.
    echo 已检测到上次保存的账号信息。
    set /p USE_SAVED=是否使用上次保存的用户名？(y/n): 
    if /i "%USE_SAVED%"=="y" (
        for /f "tokens=*" %%a in ('powershell -Command "$json = Get-Content '%USER_JSON%' | ConvertFrom-Json; $json.username"') do set USERNAME=%%a
        for /f "tokens=*" %%a in ('powershell -Command "$json = Get-Content '%USER_JSON%' | ConvertFrom-Json; [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($json.password))"') do set PASSWORD=%%a
    )
)

:: 输入用户名
if "%USERNAME%"=="" (
    echo.
    set /p USERNAME=请输入用户名: 
    if "%USERNAME%"=="" (
        echo ❌ 用户名不能为空！
        pause
        exit /b
    )
)

:: 输入密码
if "%PASSWORD%"=="" (
    echo.
    set /p PASSWORD=请输入密码: 
    if "%PASSWORD%"=="" (
        echo ❌ 密码不能为空！
        pause
        exit /b
    )

    :: 询问是否保存密码
    echo.
    set /p SAVE_CRED=是否保存用户名和密码？(y/n): 
    if /i "%SAVE_CRED%"=="y" (
        echo 正在保存账号信息到本地...
        powershell -Command "$username='%USERNAME%'; $password=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('%PASSWORD%')); $json = @{ username=$username; password=$password } | ConvertTo-Json; Set-Content -Path '.user.json' -Value $json"
    ) else (
        echo 不会保存账号信息。
    )
)

:: 替换配置文件中的用户名和密码
echo.
echo 正在更新配置文件 config/settings.json...

powershell -Command "(Get-Content config/settings.json) -replace '\"YOUR_USERNAME\"', '\"%USERNAME%\"' | Set-Content config/settings.json"
powershell -Command "(Get-Content config/settings.json) -replace '\"YOUR_PASSWORD\"', '\"%PASSWORD%\"' | Set-Content config/settings.json"

:: 完成
echo.
echo ✅ 初始化完成！你可以使用 click_me.bat 来运行测试。
pause