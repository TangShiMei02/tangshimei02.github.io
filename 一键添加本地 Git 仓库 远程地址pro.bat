@echo off
title Git Add Remote Pro
color 0B

if not exist .git (
    echo [ERROR] Not a Git repository!
    pause & exit /b 1
)

echo ===== Current Remotes =====
git remote -v 2>nul || echo No remotes
echo ===========================

choice /C HS /N /M "Protocol: H=HTTPS  S=SSH "
if %errorlevel%==1 (set "proto=https") else (set "proto=ssh")

echo.
echo Remote name: 1=origin  2=https  3=ssh  4=custom
choice /C 1234 /N /M "Choose: "
if %errorlevel%==1 set "remote_name=origin"
if %errorlevel%==2 set "remote_name=https"
if %errorlevel%==3 set "remote_name=ssh"
if %errorlevel%==4 (
    set /p "remote_name=Enter remote name: "
    if "%remote_name%"=="" (
        echo [ERROR] Remote name cannot be empty!
        pause & exit /b 1
    )
)

set /p "user=GitHub username: "
set /p "repo=GitHub repo name: "
if "%user%"=="" (
    echo [ERROR] Username cannot be empty!
    pause & exit /b 1
)
if "%repo%"=="" (
    echo [ERROR] Repo name cannot be empty!
    pause & exit /b 1
)

if "%proto%"=="https" (
    set "url=https://github.com/%user%/%repo%.git"
) else (
    set "url=git@github.com:%user%/%repo%.git"
)

git remote remove %remote_name% 2>nul
git remote add %remote_name% "%url%"

echo ===== Done =====
echo Remote : %remote_name%
echo Protocol: %proto%
echo URL    : %url%
echo ================
pause & exit /b