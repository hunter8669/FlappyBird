@echo off
title FlapPy Bird - 增强版游戏
echo ==========================================
echo        FlapPy Bird 增强版
echo ==========================================
echo.
echo 正在启动游戏...
echo.

cd /d "%~dp0"
if exist "FlapPyBird.exe" (
    start "" "FlapPyBird.exe"
    echo 游戏已启动！
) else (
    echo 错误：找不到 FlapPyBird.exe
    echo 请确保文件完整
    pause
)
