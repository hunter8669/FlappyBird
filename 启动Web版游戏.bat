@echo off
chcp 65001 >nul
echo.
echo 🌐 FlapPy Bird Web版启动器
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

echo ✅ Python环境检查通过
echo.

:: 启动服务器
echo 🚀 正在启动Web服务器...
echo 📍 游戏地址: http://localhost:8000
echo 🌐 Web版游戏: http://localhost:8000/game.html
echo 📋 管理后台: http://localhost:8000/admin
echo.
echo 💡 提示: 
echo • 按 Ctrl+C 停止服务器
echo • 服务器启动后，在浏览器中访问上述地址
echo.

cd /d "%~dp0\backend"
python simple_server.py

echo.
echo 🛑 服务器已停止
pause 