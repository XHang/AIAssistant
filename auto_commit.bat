@echo off
echo ================================
echo   Git Auto Commit & Push Tool
echo ================================
echo.

:: Step 1: add all changes
git add .
echo 已执行：git add .

:: Step 2: ask for commit message
set /p msg=请输入提交说明（commit message）: 

:: Step 3: commit
git commit -m "%msg%"
echo 已执行：git commit -m "%msg%"

:: Step 4: push
git push
echo 已执行：git push

echo.
echo 完成！
pause
