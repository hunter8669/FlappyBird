@echo off
chcp 65001 >nul
color 0A
title FlapPy Bird 完整增强版服务器启动器

echo.
echo ======================================================
echo           🎮 FlapPy Bird 完整增强版 🎮
echo ======================================================
echo.
echo 正在启动完整增强版服务器...
echo 端口: 8001
echo 功能: 100%% 桌面版功能 (5种模式+道具+Boss+武器)
echo.

cd /d "%~dp0"

echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH环境变量
    echo 请安装Python 3.7+并重新运行此脚本
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 🚀 启动服务器 (端口8001)...
echo.
echo 访问地址:
echo 📋 项目主页: http://localhost:8001/
echo 🎮 完整增强版: http://localhost:8001/game-enhanced.html
echo 🎯 基础版: http://localhost:8001/game.html
echo.
echo 💡 提示:
echo - 按 Ctrl+C 停止服务器
echo - 游戏支持键盘、鼠标、触摸控制
echo - Boss模式: 数字键1-4切换武器，P键暂停
echo.

echo 🌟 正在打开浏览器...
timeout /t 2 /nobreak >nul
start http://localhost:8001/game-enhanced.html

echo.
echo 📊 服务器日志:
echo ----------------------------------------
python -m http.server 8001

pause 