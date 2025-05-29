@echo off
chcp 65001 >nul
echo ==========================================
echo    FlapPy Bird 桌面版游戏启动
echo ==========================================
echo.

REM 设置当前目录
cd /d "%~dp0"

echo 🎮 启动桌面版游戏...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未检测到Python环境
    echo.
    echo 请先安装Python 3.9或更高版本：
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 检查pygame是否安装
python -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装游戏依赖pygame...
    pip install pygame
    if %errorlevel% neq 0 (
        echo 错误：pygame安装失败
        pause
        exit /b 1
    )
)

echo 启动游戏中...
cd game-desktop
python main.py

if %errorlevel% neq 0 (
    echo.
    echo 游戏启动失败
    pause
) 