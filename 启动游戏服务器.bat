@echo off
chcp 65001 >nul
title FlapPy Bird 游戏服务器
color 0A

echo.
echo ===============================================
echo           🐦 FlapPy Bird 游戏服务器           
echo ===============================================
echo.
echo 🚀 正在启动服务器...
echo.

:: 检查是否在正确的目录
if not exist "backend\simple_server_fixed.py" (
    echo ❌ 错误：找不到服务器文件！
    echo 请确保脚本在 FlapPyBird-master1 根目录下运行
    echo.
    pause
    exit /b 1
)

:: 进入backend目录并启动服务器
cd backend
echo 📁 已切换到backend目录
echo.

:: 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python环境！
    echo 请确保已安装Python并添加到系统PATH
    echo.
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.
echo 🎮 启动游戏服务器中...
echo ⚠️  按 Ctrl+C 可停止服务器
echo.

:: 启动服务器
python simple_server_fixed.py

:: 如果服务器意外停止，暂停以便查看错误信息
echo.
echo ⚠️  服务器已停止
pause 