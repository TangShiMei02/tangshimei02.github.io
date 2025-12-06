@echo off
:: 切换到 UTF-8 编码（尽量早执行）
chcp 65001 >nul

title Git 双通道一键部署（自动忽略根目录 node_modules）

:: === 0. 防呆：必须在仓库里运行 ===
if not exist .git (
    echo [错误] 当前目录不是 Git 仓库，请先进入仓库再运行！
    echo.
    pause >nul
    exit /b
)

:: === 1. 选择推送通道 ===
choice /C HS /N /M "推送方式：H=HTTPS  S=SSH "
if %errorlevel%==1 (set "remote=https") else (set "remote=ssh")

:: === 2. 没有该 remote 就自动添加（先删后加，避免冲突）===
git remote | findstr /i "^%remote%$" >nul
if %errorlevel% neq 0 (
    echo 检测到缺少 %remote% 远程，正在自动添加...
    for /f "tokens=2" %%u in ('git remote -v ^| findstr /i origin.*fetch') do set "ori=%%u"
    if not defined ori (
        echo [错误] 请先确保已有 origin 远程地址！
        echo.
        pause >nul
        exit /b
    )
    :: 自动转换 origin 地址到对应协议
    setlocal enabledelayedexpansion
    if "%remote%"=="https" (
        set "newurl=!ori:git@github.com:=https://github.com/!"
    ) else (
        set "newurl=!ori:https://github.com/=git@github.com:!"
    )
    git remote add %remote% !newurl!
    endlocal
)

:: === 3. 更新说明 ===
set /p msg=请输入更新说明（直接回车=默认"update"）：
if "%msg%"=="" set "msg=update"

:: === 4. 自动获取当前分支 ===
for /f "tokens=3" %%b in ('git symbolic-ref --short HEAD 2^>nul') do set "branch=%%b"
if not defined branch set "branch=main"

:: === 5. 强制排除根目录 node_modules（关键新增）===
if exist node_modules (
    echo 检测到根目录 node_modules，已自动剔除跟踪...
    git rm -r --cached node_modules 2>nul
)

:: === 6. 常规三板斧 ===
echo 正在添加文件...
git add .

:: 检查是否有实际改动
git diff --cached --quiet
if %errorlevel% equ 0 (
    git diff --quiet
    if %errorlevel% equ 0 (
        echo ==================================================
        echo GitHub 仓库已同步至最新，没有可以推送的新文件。
        echo ==================================================
        echo.
        pause >nul
        exit /b
    )
)

echo 正在提交...
git commit -m "%msg%"
if %errorlevel% neq 0 (
    echo [错误] 提交失败，已终止后续推送！
    echo.
    pause >nul
    exit /b
)

echo 正在推送到 %remote% (%branch%)...
git push %remote% %branch%
if %errorlevel% neq 0 (
    echo [错误] 推送失败，请检查网络或权限！
    echo.
    pause >nul
    exit /b
)

echo ==================================================
echo 推送完成！30 秒后刷新网页即可看到更新
echo ==================================================
timeout /t 30 >nul