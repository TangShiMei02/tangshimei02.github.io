@echo off
chcp 65001 >nul
set /p msg=请输入更新说明（直接回车=默认“update”）：
if "%msg%"=="" set msg=update

echo 正在添加文件...
git add .

echo 正在提交...
git commit -m "%msg%"

echo 正在推送...
git push

echo ===== 推送完成！30 秒后刷新网页即可看到更新 =====
pause
