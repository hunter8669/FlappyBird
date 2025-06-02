@echo off
chcp 65001 >nul
color 0B
title FlapPy Bird 完整增强版服务器 (Frontend目录)

echo.
echo ======================================================
echo      🚀 FlapPy Bird 完整增强版 (Frontend服务) 🚀
echo ======================================================
echo.
echo 启动模式: Frontend目录服务
echo 端口: 8001
echo 目录: frontend/
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
echo 📁 切换到frontend目录...
if not exist "frontend" (
    echo ❌ frontend目录不存在
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

cd frontend

echo.
echo 🚀 启动Frontend服务器 (端口8001)...
echo.
echo 🎮 推荐访问地址:
echo ⭐ 完整增强版: http://localhost:8001/game-enhanced.html
echo 📋 基础版: http://localhost:8001/game.html
echo 🏠 项目主页: http://localhost:8001/index.html
echo.
echo 🎯 增强版功能特色:
echo - ✅ 5种游戏模式 (经典/限时/反向/Boss/金币)
echo - ✅ 5种道具系统 (护盾/磁铁/慢速/双倍/生命)
echo - ✅ 4种Boss战斗 (普通/火焰/冰霜/电击)
echo - ✅ 4种武器系统 (激光/火箭/等离子/冰冻)
echo - ✅ 移动端优化 (触摸控制/响应式设计)
echo.

echo 🌟 正在打开完整增强版...
timeout /t 2 /nobreak >nul
start http://localhost:8001/game-enhanced.html

echo.
echo 📊 服务器运行日志:
echo ----------------------------------------
python -m http.server 8001

pause 