@echo off
chcp 65001 >nul
echo 🐦 FlapPy Bird 游戏启动器
echo ================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    echo 📥 下载链接: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python已安装
python --version

:: 检查pygame是否安装
python -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo 📦 pygame未安装，正在自动安装...
    pip install pygame
    if %errorlevel% neq 0 (
        echo ❌ pygame安装失败，请手动安装: pip install pygame
        pause
        exit /b 1
    )
)

echo ✅ pygame已就绪
echo.
echo 🚀 启动游戏...
echo.

:: 启动游戏
cd /d "%~dp0"
cd game-desktop
python main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 游戏启动失败
    echo 💡 请检查错误信息或联系技术支持
    pause
) else (
    echo.
    echo �� 游戏已正常退出
)

pause 