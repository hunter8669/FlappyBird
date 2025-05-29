@echo off
chcp 65001 >nul
echo ==========================================
echo    FlapPy Bird 游戏网站启动
echo ==========================================
echo.

REM 设置当前目录
cd /d "%~dp0"

echo 🚀 启动游戏服务器...
echo.
echo 📍 服务地址: http://localhost:8000
echo 💡 浏览器会自动打开网站
echo.

REM 启动服务器并自动打开浏览器
cd backend
start "" http://localhost:8000
python simple_server.py

pause 