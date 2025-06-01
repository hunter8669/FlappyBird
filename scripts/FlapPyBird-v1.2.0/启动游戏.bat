@echo off
title FlapPy Bird - 增强版
echo ==========================================
echo        FlapPy Bird 增强版
echo ==========================================
echo 正在启动游戏...
echo.

start "" "FlapPyBird.exe"

REM 如果EXE无法运行，显示帮助信息
timeout /t 2 >nul
tasklist /fi "imagename eq FlapPyBird.exe" | find "FlapPyBird.exe" >nul
if %errorlevel% neq 0 (
    echo.
    echo [警告] 游戏可能无法正常启动
    echo.
    echo 解决方案：
    echo 1. 右键"FlapPyBird.exe" → 以管理员身份运行
    echo 2. 确保Windows版本为Windows 7或更高
    echo 3. 如仍有问题，请联系开发者
    echo.
    pause
)
