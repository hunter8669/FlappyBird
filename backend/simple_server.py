#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版后端服务器
提供基本的API功能，支持游戏下载和统计
"""

import json
import os
import zipfile
import shutil
import tempfile
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes
from user_manager import UserManager

# 初始化用户管理器
user_manager = UserManager()

class GameAPIHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        """重写end_headers方法，确保所有响应都包含CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        super().end_headers()

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API路由
        if path == '/':
            # 重定向到前端首页
            self.send_response(302)
            self.send_header('Location', '/index.html')
            self.end_headers()
            
        elif path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        elif path == '/api/downloads/desktop':
            self.handle_download()
            
        elif path == '/api/stats':
            self.handle_stats()
            
        elif path == '/api/users/stats':
            self.handle_user_stats()
            
        elif path == '/api/users/list':
            self.handle_user_list()
            
        elif path.startswith('/api/users/'):
            self.handle_user_api(path)
            
        elif path.startswith('/api/scores/leaderboard'):
            self.handle_leaderboard()
            
        elif path == '/login' or path == '/login/':
            self.serve_login_page()
            
        elif path == '/register' or path == '/register/':
            self.serve_register_page()
            
        elif path == '/admin' or path == '/admin/':
            self.serve_admin_page()
            
        elif path == '/admin/login':
            self.serve_admin_login()
            
        elif path == '/admin/dashboard':
            self.serve_admin_dashboard()
            
        elif path.startswith('/admin/api/'):
            self.handle_admin_api(path)
            
        else:
            # 提供静态文件服务
            self.serve_static_file(path)

    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/downloads/track':
            self.handle_download_tracking()
        elif path == '/api/users/register':
            self.handle_user_register()
        elif path == '/api/users/login':
            self.handle_user_login()
        elif path == '/api/users/logout':
            self.handle_user_logout()
        elif path == '/api/users/score':
            self.handle_user_score_update()
        elif path.startswith('/api/users/admin/'):
            self.handle_user_admin_action(path)
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": "Not Found"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_download(self):
        """处理游戏下载请求"""
        try:
            print(f"[下载] 收到下载请求: {self.path}")
            print(f"[下载] 请求方法: {self.command}")
            print(f"[下载] 用户代理: {self.headers.get('User-Agent', 'Unknown')}")
            
            # 检查用户是否要求源码版本
            query_params = parse_qs(urlparse(self.path).query)
            download_type = query_params.get('type', ['exe'])[0]
            print(f"[下载] 请求类型: {download_type}")
            
            if download_type == 'exe' or download_type == 'auto':
                # 优先尝试提供真正的EXE文件
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                print(f"[下载] 当前目录: {current_dir}")
                print(f"[下载] 项目根目录: {project_root}")
                
                # 查找真正的EXE文件
                exe_file_path = os.path.join(project_root, "scripts", "FlapPyBird.exe")
                print(f"[下载] 查找EXE文件: {exe_file_path}")
                
                if os.path.exists(exe_file_path):
                    file_size = os.path.getsize(exe_file_path)
                    print(f"[下载] 找到EXE文件，大小: {file_size/1024/1024:.1f} MB")
                    
                    # 检查文件是否真的是EXE（不是Git LFS指针）
                    if file_size > 100 * 1024 * 1024:  # 大于100MB才认为是真实EXE
                        # 直接提供EXE文件下载
                        print("[下载] 直接提供EXE文件...")
                        
                        # 设置响应头
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/octet-stream')
                        self.send_header('Content-Disposition', 'attachment; filename="FlapPyBird.exe"')
                        self.send_header('Content-Length', str(file_size))
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                        self.end_headers()
                        
                        print(f"[下载] 开始发送EXE文件...")
                        
                        # 使用流式传输，避免内存不足
                        chunk_size = 8192  # 8KB chunks
                        bytes_sent = 0
                        
                        try:
                            with open(exe_file_path, 'rb') as f:
                                while True:
                                    chunk = f.read(chunk_size)
                                    if not chunk:
                                        break
                                    self.wfile.write(chunk)
                                    bytes_sent += len(chunk)
                                    
                                    # 每发送10MB打印一次进度
                                    if bytes_sent % (10 * 1024 * 1024) == 0:
                                        print(f"[下载] 已发送: {bytes_sent/1024/1024:.1f} MB")
                            
                            print(f"[下载] EXE文件发送完成: {bytes_sent/1024/1024:.1f} MB")
                            return
                        except Exception as e:
                            print(f"[错误] 文件传输失败: {e}")
                            # 注意：此时已经发送了响应头，不能再发送JSON错误
                            return
                    else:
                        print(f"[下载] EXE文件太小({file_size} bytes)，可能是Git LFS指针")
                else:
                    print(f"[下载] EXE文件不存在: {exe_file_path}")
                
                # 如果没有找到真实EXE，切换到源码版本
                print(f"[下载] 未找到真实EXE文件，自动切换到源码版本")
                download_type = 'source'
            
            if download_type == 'source':
                # 提供源码版本（现有逻辑保持不变）
                print("[下载] 创建源码安装包...")
                
                # 创建临时ZIP文件
                temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
                temp_zip.close()
                
                with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # 添加主要文件
                    for root, dirs, files in os.walk('..'):
                        # 排除不需要的目录
                        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.vscode', 'backend', 'frontend', 'dist', 'build']]
                        
                        for file in files:
                            if file.endswith(('.py', '.md', '.txt', '.ico', '.png', '.jpg', '.wav', '.mp3', '.json')):
                                file_path = os.path.join(root, file)
                                arc_name = os.path.relpath(file_path, '..')
                                zip_file.write(file_path, arc_name)
                    
                    # 创建EXE构建脚本
                    build_script = '''@echo off
title FlapPy Bird EXE构建器
echo ==========================================
echo        FlapPy Bird EXE构建器
echo ==========================================
echo.
echo 正在检查Python环境...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python环境
    echo 请先安装Python 3.9或更高版本
    pause
    exit /b 1
)

echo 正在安装构建依赖...
pip install pyinstaller pygame

echo.
echo 开始构建EXE文件...
cd scripts
python build_exe_now.py

if %errorlevel% equ 0 (
    echo.
    echo [成功] EXE文件构建完成！
    echo 可执行文件位置：scripts/FlapPyBird.exe
    echo.
) else (
    echo.
    echo [失败] 构建失败，使用源码方式运行：
    echo cd game-desktop && python main.py
    echo.
)

pause
'''
                    
                    zip_file.writestr('构建EXE.bat', build_script.encode('gbk'))
                    
                    # 创建简单的启动脚本（源码版）
                    startup_script = '''@echo off
echo ==========================================
echo    FlapPy Bird 游戏启动器 (源码版)
echo ==========================================
echo 正在启动游戏...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未检测到Python环境
    echo.
    echo 请先安装Python 3.9或更高版本：
    echo https://www.python.org/downloads/
    echo.
    echo 或者运行"构建EXE.bat"生成独立的EXE文件
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
        echo 请手动执行：pip install pygame
        pause
        exit /b 1
    )
)

echo 启动游戏中...
cd game-desktop
python main.py

if %errorlevel% neq 0 (
    echo.
    echo 游戏启动失败，请检查：
    echo 1. Python是否正确安装
    echo 2. pygame是否安装成功
    echo 3. 游戏文件是否完整
    echo.
    pause
)
'''
                    
                    zip_file.writestr('启动游戏.bat', startup_script.encode('gbk'))
                    
                    # 添加构建脚本
                    build_script_path = '../scripts/build_exe_now.py'
                    if os.path.exists(build_script_path):
                        zip_file.write(build_script_path, 'scripts/build_exe_now.py')
                    
                    # 创建README说明文件
                    readme_content = '''FlapPy Bird 增强版游戏 - 源码版
==================================

🚀 快速开始:

方法一：构建EXE文件（推荐）
1. 双击"构建EXE.bat"
2. 等待构建完成（首次需要下载依赖）
3. 运行生成的EXE文件

方法二：源码运行
1. 双击"启动游戏.bat"
2. 等待自动安装依赖
3. 游戏自动启动

🎮 游戏特色:
- 四种游戏模式（经典、限时、反向、Boss战）
- 丰富的道具系统
- Boss战斗和武器系统
- 流畅的60FPS游戏体验

📋 系统要求:
- Windows 7/10/11
- Python 3.9+（如果使用源码运行）

💡 提示:
- 推荐使用"构建EXE.bat"生成独立的EXE文件
- EXE文件可以在没有Python的电脑上运行
- 首次构建需要联网下载依赖包

🌐 项目地址: https://github.com/yourusername/FlapPyBird
版本: v1.2.0 (源码版 + EXE构建工具)
更新时间: ''' + datetime.now().strftime('%Y-%m-%d') + '''

享受游戏吧！🐦
'''
                    
                    zip_file.writestr('README.txt', readme_content.encode('utf-8'))
                
                # 发送文件
                with open(temp_zip.name, 'rb') as f:
                    file_data = f.read()
                
                file_size = len(file_data)
                print(f"[下载] 源码安装包已创建: FlapPyBird-Source-with-EXE-Builder-v1.2.0.zip ({file_size/1024/1024:.1f} MB)")
                
                # 设置响应头
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Disposition', 'attachment; filename="FlapPyBird-Source-with-EXE-Builder-v1.2.0.zip"')
                self.send_header('Content-Length', str(file_size))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                # 发送文件内容
                self.wfile.write(file_data)
                
                # 清理临时文件
                os.unlink(temp_zip.name)
                
                print(f"[下载] 源码安装包已发送: {file_size/1024/1024:.1f} MB")
                return
            
            else:
                # 未知类型，返回选项页面
                response = {
                    "status": "options",
                    "message": "请选择下载类型",
                    "options": [
                        {
                            "type": "exe",
                            "title": "EXE独立版（推荐）",
                            "description": "可直接运行的独立应用程序，无需安装Python",
                            "size": "约243 MB",
                            "download_url": f"/api/downloads/desktop?type=exe"
                        },
                        {
                            "type": "source", 
                            "title": "源码版本",
                            "description": "包含Python源码和构建工具，需要Python环境",
                            "size": "约 10 MB",
                            "download_url": f"/api/downloads/desktop?type=source"
                        }
                    ]
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
                
        except Exception as e:
            print(f"[错误] 下载处理失败: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': '下载服务暂时不可用',
                'message': str(e)
            }).encode())

    def handle_download_tracking(self):
        """处理下载统计"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 记录下载统计（简化版）
                stats_file = 'download_stats.json'
                if os.path.exists(stats_file):
                    with open(stats_file, 'r', encoding='utf-8') as f:
                        stats = json.load(f)
                else:
                    stats = {"downloads": []}
                
                stats["downloads"].append({
                    "timestamp": datetime.now().isoformat(),
                    "type": data.get("type", "unknown"),
                    "version": data.get("version", "unknown")
                })
                
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"status": "success", "message": "统计已记录"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": f"统计失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_stats(self):
        """处理统计查询"""
        try:
            stats_file = 'download_stats.json'
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            else:
                stats = {"downloads": []}
            
            # 生成统计摘要
            total_downloads = len(stats["downloads"])
            response = {
                "total_downloads": total_downloads,
                "recent_downloads": stats["downloads"][-10:],  # 最近10次下载
                "version": "1.2.0",
                "server_status": "running"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": f"获取统计失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def serve_static_file(self, path):
        """提供静态文件服务"""
        try:
            # 前端文件目录
            frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
            
            # 默认文件
            if path == '/':
                path = '/index.html'
            
            # 构建文件路径
            file_path = os.path.join(frontend_dir, path.lstrip('/'))
            
            # 安全检查：防止路径遍历攻击
            if not os.path.commonpath([frontend_dir, file_path]) == frontend_dir:
                self.send_response(403)
                self.end_headers()
                return
            
            # 检查文件是否存在
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # 获取文件类型
                content_type, _ = mimetypes.guess_type(file_path)
                if content_type is None:
                    content_type = 'text/plain'
                
                # 发送文件
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(os.path.getsize(file_path)))
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                
                print(f"[静态文件] 已提供: {path}")
            else:
                # 文件不存在
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'''<!DOCTYPE html>
<html><head><title>404 Not Found</title></head>
<body><h1>404 - File Not Found</h1><p>The requested file was not found.</p></body></html>''')
                
        except Exception as e:
            print(f"[错误] 静态文件服务失败: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'''<!DOCTYPE html>
<html><head><title>500 Server Error</title></head>
<body><h1>500 - Server Error</h1><p>Internal server error occurred.</p></body></html>''')

    def serve_admin_page(self):
        """管理后台主页"""
        self.send_response(302)
        self.send_header('Location', '/admin/login')
        self.end_headers()

    def serve_admin_login(self):
        """管理员登录页面"""
        html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlapPy Bird 管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .login-container {
            background: white; padding: 2rem; border-radius: 10px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 300px;
        }
        .logo { text-align: center; font-size: 2rem; margin-bottom: 1rem; color: #333; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; color: #333; font-weight: bold; }
        input { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; }
        .btn { width: 100%; padding: 0.8rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; }
        .btn:hover { background: #5a6fd8; }
        .stats { margin-top: 2rem; padding: 1rem; background: #f5f5f5; border-radius: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🐦 管理后台</div>
        <form onsubmit="login(event)">
            <div class="form-group">
                <label>用户名:</label>
                <input type="text" id="username" required placeholder="admin">
            </div>
            <div class="form-group">
                <label>密码:</label>
                <input type="password" id="password" required placeholder="admin123">
            </div>
            <button type="submit" class="btn">登录</button>
        </form>
        <div class="stats">
            <small>🔐 默认账号: admin / admin123</small>
        </div>
    </div>
    
    <script>
        function login(event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (username === 'admin' && password === 'admin123') {
                window.location.href = '/admin/dashboard';
            } else {
                alert('❌ 用户名或密码错误！');
            }
        }
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_admin_dashboard(self):
        """管理后台仪表板"""
        # 获取下载统计数据
        stats_file = 'download_stats.json'
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        else:
            stats = {"downloads": []}
        
        total_downloads = len(stats["downloads"])
        recent_downloads = stats["downloads"][-5:] if stats["downloads"] else []
        
        # 获取用户统计数据
        user_stats = user_manager.get_user_stats()
        recent_users = user_manager.get_all_users()[:5]  # 最近5个用户
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlapPy Bird 管理后台</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Courier New', monospace; 
            background: #f5f5f5; color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center;
        }}
        .container {{ max-width: 1400px; margin: 2rem auto; padding: 0 1rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }}
        .card {{
            background: white; padding: 1.5rem; border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .card h3 {{ margin-bottom: 1rem; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 0.5rem; }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: #667eea; }}
        .btn {{ 
            display: inline-block; padding: 0.5rem 1rem; background: #667eea; 
            color: white; text-decoration: none; border-radius: 5px; margin: 0.5rem 0.5rem 0.5rem 0;
            border: none; cursor: pointer; font-size: 0.9rem;
        }}
        .btn:hover {{ background: #5a6fd8; }}
        .btn-danger {{ background: #e74c3c; }}
        .btn-danger:hover {{ background: #c0392b; }}
        .btn-warning {{ background: #f39c12; }}
        .btn-warning:hover {{ background: #e67e22; }}
        .btn-success {{ background: #27ae60; }}
        .btn-success:hover {{ background: #229954; }}
        .download-list, .user-list {{ max-height: 200px; overflow-y: auto; }}
        .download-item, .user-item {{ 
            padding: 0.5rem; margin: 0.5rem 0; background: #f8f9fa; 
            border-left: 3px solid #667eea; border-radius: 3px; position: relative;
        }}
        .user-item {{ border-left-color: #27ae60; }}
        .user-item.banned {{ border-left-color: #e74c3c; background: #fdf2f2; }}
        .nav-links {{ display: flex; gap: 1rem; }}
        .nav-links a {{ color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 5px; }}
        .nav-links a:hover {{ background: rgba(255,255,255,0.2); }}
        .user-stats {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
        .user-stat {{ flex: 1; min-width: 120px; text-align: center; padding: 0.5rem; background: #f8f9fa; border-radius: 5px; }}
        .user-actions {{ float: right; }}
        .user-actions button {{ padding: 0.3rem 0.6rem; margin: 0 0.2rem; font-size: 0.8rem; }}
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }}
        .modal-content {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 2rem; border-radius: 8px; width: 90%; max-width: 800px; max-height: 80%; overflow-y: auto; }}
        .modal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
        .close {{ font-size: 1.5rem; cursor: pointer; }}
        .table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        .table th, .table td {{ padding: 0.8rem; text-align: left; border-bottom: 1px solid #ddd; }}
        .table th {{ background: #f8f9fa; font-weight: bold; }}
        .achievement {{ display: inline-block; background: #ffd700; color: #333; padding: 0.2rem 0.5rem; border-radius: 3px; font-size: 0.8rem; margin: 0.1rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐦 FlapPy Bird 管理后台</h1>
        <div class="nav-links">
            <a href="/">🏠 前端网站</a>
            <a href="/login">👤 用户登录</a>
            <a href="/health">💓 系统状态</a>
            <a href="#" onclick="logout()">🚪 退出</a>
        </div>
    </div>
    
    <div class="container">
        <div class="grid">
            <!-- 用户统计 -->
            <div class="card">
                <h3>👥 用户统计</h3>
                <div class="user-stats">
                    <div class="user-stat">
                        <div class="stat-number">{user_stats.get("total_users", 0)}</div>
                        <p>总用户数</p>
                    </div>
                    <div class="user-stat">
                        <div class="stat-number">{user_stats.get("active_users", 0)}</div>
                        <p>活跃用户</p>
                    </div>
                    <div class="user-stat">
                        <div class="stat-number">{user_stats.get("today_registered", 0)}</div>
                        <p>今日注册</p>
                    </div>
                    <div class="user-stat">
                        <div class="stat-number">{user_stats.get("today_active", 0)}</div>
                        <p>今日活跃</p>
                    </div>
                </div>
                <button onclick="showUserManagement()" class="btn">👥 用户管理</button>
                <button onclick="refreshStats()" class="btn">🔄 刷新数据</button>
            </div>
            
            <!-- 游戏统计 -->
            <div class="card">
                <h3>🎮 游戏统计</h3>
                <div class="stat-number">{user_stats.get("total_games_played", 0)}</div>
                <p>总游戏次数</p>
                <p>总游戏时长: {user_stats.get("total_playtime", 0) // 60} 分钟</p>
                <button onclick="showGameStats()" class="btn">📊 详细统计</button>
            </div>
            
            <!-- 下载统计 -->
            <div class="card">
                <h3>📊 下载统计</h3>
                <div class="stat-number">{total_downloads}</div>
                <p>总下载次数</p>
                <a href="#" onclick="clearStats()" class="btn btn-danger">🗑️ 清空统计</a>
                <a href="#" onclick="exportData()" class="btn">💾 导出数据</a>
            </div>
            
            <!-- 最近用户 -->
            <div class="card">
                <h3>👤 最近用户</h3>
                <div class="user-list">'''

        # 生成用户列表HTML
        if recent_users:
            for u in recent_users:
                username = u.get("username", "")
                status_class = "banned" if u.get("status") == "banned" else ""
                created_at = u.get("created_at", "").split("T")[0] if u.get("created_at") else "未知"
                best_score = u.get("best_score", 0)
                games_played = u.get("games_played", 0)
                
                if u.get("status") == "banned":
                    action_btn = f'<button onclick="unbanUser(\'{username}\', event)" class="btn btn-warning">解禁</button>'
                else:
                    action_btn = f'<button onclick="banUser(\'{username}\', event)" class="btn btn-warning">禁用</button>'
                
                html += f'''
                    <div class="user-item {status_class}">
                        <strong>{username}</strong>
                        <div class="user-actions">
                            <button onclick="viewUser('{username}', event)" class="btn btn-success">查看</button>
                            {action_btn}
                            <button onclick="deleteUser('{username}', event)" class="btn btn-danger">删除</button>
                        </div>
                        <br><small>注册: {created_at} | 最佳: {best_score}分 | 游戏: {games_played}次</small>
                    </div>'''
        else:
            html += '<p style="color: #999;">暂无用户</p>'

        html += f'''
                </div>
            </div>
            
            <!-- 最近下载 -->
            <div class="card">
                <h3>📥 最近下载记录</h3>
                <div class="download-list">'''

        # 生成下载记录HTML
        if recent_downloads:
            for d in recent_downloads:
                version = d.get("version", "未知版本")
                timestamp = d.get("timestamp", "").split("T")[0] if d.get("timestamp") else "未知时间"
                html += f'<div class="download-item">📦 {version} - {timestamp}</div>'
        else:
            html += '<p style="color: #999;">暂无下载记录</p>'

        html += f'''
                </div>
            </div>
            
            <!-- 游戏管理 -->
            <div class="card">
                <h3>🎮 游戏管理</h3>
                <p>当前版本: <strong>v1.2.0</strong></p>
                <p>游戏模式: 4种（经典、限时、反向、Boss战）</p>
                <a href="/启动桌面游戏.bat" class="btn">🎯 启动本地游戏</a>
                <a href="/api/downloads/desktop" class="btn">📦 下载游戏包</a>
            </div>
            
            <!-- 系统信息 -->
            <div class="card">
                <h3>🖥️ 系统信息</h3>
                <p>服务器状态: <span style="color: green;">✅ 正常运行</span></p>
                <p>启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Python版本: 3.9+</p>
                <a href="/health" class="btn" target="_blank">💓 健康检查</a>
                <a href="/api/stats" class="btn" target="_blank">📈 API统计</a>
            </div>
        </div>
    </div>
    
    <!-- 用户管理模态框 -->
    <div id="userModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>👥 用户管理</h3>
                <span class="close" onclick="closeModal('userModal')">&times;</span>
            </div>
            <div id="userModalContent">加载中...</div>
        </div>
    </div>
    
    <!-- 用户详情模态框 -->
    <div id="userDetailModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>👤 用户详情</h3>
                <span class="close" onclick="closeModal('userDetailModal')">&times;</span>
            </div>
            <div id="userDetailContent">加载中...</div>
        </div>
    </div>
    
    <script>
        function logout() {{
            if (confirm('确定要退出管理后台吗？')) {{
                window.location.href = '/admin/login';
            }}
        }}
        
        function refreshStats() {{
            window.location.reload();
        }}
        
        function clearStats() {{
            if (confirm('确定要清空所有下载统计吗？此操作不可恢复！')) {{
                fetch('/admin/api/clear-stats', {{method: 'POST'}})
                .then(() => window.location.reload())
                .catch(err => alert('操作失败: ' + err));
            }}
        }}
        
        function exportData() {{
            window.open('/admin/api/export-data', '_blank');
        }}
        
        function showUserManagement() {{
            document.getElementById('userModal').style.display = 'block';
            fetch('/api/users/list')
            .then(response => response.json())
            .then(users => {{
                let html = '<table class="table"><thead><tr><th>用户名</th><th>邮箱</th><th>注册时间</th><th>最后登录</th><th>游戏次数</th><th>最佳分数</th><th>状态</th><th>操作</th></tr></thead><tbody>';
                users.forEach(user => {{
                    html += `<tr>
                        <td>${{user.username}}</td>
                        <td>${{user.email}}</td>
                        <td>${{user.created_at?.split('T')[0] || '未知'}}</td>
                        <td>${{user.last_login?.split('T')[0] || '从未登录'}}</td>
                        <td>${{user.games_played}}</td>
                        <td>${{user.best_score}}</td>
                        <td>${{user.status === 'active' ? '正常' : '禁用'}}</td>
                        <td>
                            <button onclick="viewUser('${{user.username}}')" class="btn btn-success">查看</button>
                            ${{user.status === 'active' ? 
                                '<button onclick="banUser(\\''+user.username+'\\');" class="btn btn-warning">禁用</button>' : 
                                '<button onclick="unbanUser(\\''+user.username+'\\');" class="btn btn-warning">解禁</button>'
                            }}
                            <button onclick="deleteUser('${{user.username}}')" class="btn btn-danger">删除</button>
                        </td>
                    </tr>`;
                }});
                html += '</tbody></table>';
                document.getElementById('userModalContent').innerHTML = html;
            }})
            .catch(err => {{
                document.getElementById('userModalContent').innerHTML = '<p>加载失败: ' + err.message + '</p>';
            }});
        }}
        
        function viewUser(username, event) {{
            if (event) event.stopPropagation();
            document.getElementById('userDetailModal').style.display = 'block';
            fetch(`/api/users/info/${{username}}`)
            .then(response => response.json())
            .then(user => {{
                let achievements = user.achievements?.map(a => `<span class="achievement">${{a}}</span>`).join('') || '暂无成就';
                document.getElementById('userDetailContent').innerHTML = `
                    <h4>用户: ${{user.username}}</h4>
                    <p><strong>邮箱:</strong> ${{user.email}}</p>
                    <p><strong>注册时间:</strong> ${{user.created_at}}</p>
                    <p><strong>最后登录:</strong> ${{user.last_login || '从未登录'}}</p>
                    <p><strong>登录次数:</strong> ${{user.login_count}}</p>
                    <p><strong>总分数:</strong> ${{user.total_score}}</p>
                    <p><strong>最佳分数:</strong> ${{user.best_score}}</p>
                    <p><strong>游戏次数:</strong> ${{user.games_played}}</p>
                    <p><strong>游戏时长:</strong> ${{Math.floor(user.total_playtime / 60)}} 分钟</p>
                    <p><strong>账号状态:</strong> ${{user.status === 'active' ? '正常' : '禁用'}}</p>
                    <p><strong>成就:</strong><br>${{achievements}}</p>
                `;
            }})
            .catch(err => {{
                document.getElementById('userDetailContent').innerHTML = '<p>加载失败: ' + err.message + '</p>';
            }});
        }}
        
        function banUser(username, event) {{
            if (event) event.stopPropagation();
            if (confirm(`确定要禁用用户 ${{username}} 吗？`)) {{
                fetch('/api/users/admin/ban', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{username}})
                }})
                .then(response => response.json())
                .then(data => {{
                    alert(data.message);
                    window.location.reload();
                }})
                .catch(err => alert('操作失败: ' + err.message));
            }}
        }}
        
        function unbanUser(username, event) {{
            if (event) event.stopPropagation();
            if (confirm(`确定要解禁用户 ${{username}} 吗？`)) {{
                fetch('/api/users/admin/unban', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{username}})
                }})
                .then(response => response.json())
                .then(data => {{
                    alert(data.message);
                    window.location.reload();
                }})
                .catch(err => alert('操作失败: ' + err.message));
            }}
        }}
        
        function deleteUser(username, event) {{
            if (event) event.stopPropagation();
            if (confirm(`确定要删除用户 ${{username}} 吗？此操作不可恢复！`)) {{
                fetch('/api/users/admin/delete', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{username}})
                }})
                .then(response => response.json())
                .then(data => {{
                    alert(data.message);
                    window.location.reload();
                }})
                .catch(err => alert('操作失败: ' + err.message));
            }}
        }}
        
        function closeModal(modalId) {{
            document.getElementById(modalId).style.display = 'none';
        }}
        
        function showGameStats() {{
            alert('🎮 游戏详细统计功能开发中...');
        }}
        
        // 点击模态框外部关闭
        window.onclick = function(event) {{
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {{
                if (event.target === modal) {{
                    modal.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_admin_api(self, path):
        """处理管理后台API请求"""
        if path == '/admin/api/clear-stats':
            try:
                stats_file = 'download_stats.json'
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump({"downloads": []}, f)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                
        elif path == '/admin/api/export-data':
            try:
                stats_file = 'download_stats.json'
                if os.path.exists(stats_file):
                    with open(stats_file, 'rb') as f:
                        data = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Disposition', 'attachment; filename="download_stats.json"')
                    self.end_headers()
                    self.wfile.write(data)
                else:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "No data file found"}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "API not found"}).encode())

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

    def serve_login_page(self):
        """用户登录页面"""
        html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlapPy Bird - 用户登录</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .container {
            background: white; padding: 2rem; border-radius: 10px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 350px;
        }
        .logo { text-align: center; font-size: 2rem; margin-bottom: 1rem; color: #333; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; color: #333; font-weight: bold; }
        input { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; }
        .btn { width: 100%; padding: 0.8rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; margin: 0.5rem 0; }
        .btn:hover { background: #5a6fd8; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #545b62; }
        .links { text-align: center; margin-top: 1rem; }
        .links a { color: #667eea; text-decoration: none; }
        .message { padding: 0.5rem; margin: 1rem 0; border-radius: 5px; text-align: center; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🐦 用户登录</div>
        <div id="message"></div>
        <form onsubmit="login(event)">
            <div class="form-group">
                <label>用户名:</label>
                <input type="text" id="username" required placeholder="请输入用户名">
            </div>
            <div class="form-group">
                <label>密码:</label>
                <input type="password" id="password" required placeholder="请输入密码">
            </div>
            <button type="submit" class="btn">登录</button>
            <button type="button" class="btn btn-secondary" onclick="window.location.href='/register'">注册新账号</button>
            <button type="button" class="btn btn-secondary" onclick="window.location.href='/'">返回首页</button>
        </form>
        <div class="links">
            <a href="/register">没有账号？立即注册</a>
        </div>
    </div>
    
    <script>
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = '<div class="' + type + '">' + text + '</div>';
        }
        
        function login(event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            fetch('/api/users/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    localStorage.setItem('userToken', data.token);
                    localStorage.setItem('userInfo', JSON.stringify(data.user));
                    showMessage('登录成功！正在跳转...', 'success');
                    setTimeout(() => window.location.href = '/', 1500);
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(err => {
                showMessage('登录失败: ' + err.message, 'error');
            });
        }
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_register_page(self):
        """用户注册页面"""
        html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlapPy Bird - 用户注册</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Courier New', monospace; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .container {
            background: white; padding: 2rem; border-radius: 10px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 350px;
        }
        .logo { text-align: center; font-size: 2rem; margin-bottom: 1rem; color: #333; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; color: #333; font-weight: bold; }
        input { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 5px; }
        .btn { width: 100%; padding: 0.8rem; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; margin: 0.5rem 0; }
        .btn:hover { background: #5a6fd8; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #545b62; }
        .links { text-align: center; margin-top: 1rem; }
        .links a { color: #667eea; text-decoration: none; }
        .message { padding: 0.5rem; margin: 1rem 0; border-radius: 5px; text-align: center; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🐦 用户注册</div>
        <div id="message"></div>
        <form onsubmit="register(event)">
            <div class="form-group">
                <label>用户名:</label>
                <input type="text" id="username" required placeholder="请输入用户名" minlength="3">
            </div>
            <div class="form-group">
                <label>邮箱:</label>
                <input type="email" id="email" required placeholder="请输入邮箱地址">
            </div>
            <div class="form-group">
                <label>密码:</label>
                <input type="password" id="password" required placeholder="请输入密码" minlength="6">
            </div>
            <div class="form-group">
                <label>确认密码:</label>
                <input type="password" id="confirmPassword" required placeholder="请再次输入密码">
            </div>
            <button type="submit" class="btn">注册</button>
            <button type="button" class="btn btn-secondary" onclick="window.location.href='/login'">已有账号？去登录</button>
            <button type="button" class="btn btn-secondary" onclick="window.location.href='/'">返回首页</button>
        </form>
        <div class="links">
            <a href="/login">已有账号？立即登录</a>
        </div>
    </div>
    
    <script>
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = '<div class="' + type + '">' + text + '</div>';
        }
        
        function register(event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                showMessage('两次输入的密码不一致', 'error');
                return;
            }
            
            if (password.length < 6) {
                showMessage('密码长度至少6位', 'error');
                return;
            }
            
            fetch('/api/users/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, email, password})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage('注册成功！正在跳转到登录页面...', 'success');
                    setTimeout(() => window.location.href = '/login', 2000);
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(err => {
                showMessage('注册失败: ' + err.message, 'error');
            });
        }
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_user_register(self):
        """处理用户注册"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            email = data.get('email', '').strip()
            
            if not all([username, password, email]):
                response = {"success": False, "message": "请填写完整信息"}
            else:
                response = user_manager.register_user(username, password, email)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"注册失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_login(self):
        """处理用户登录"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            if not all([username, password]):
                response = {"success": False, "message": "请填写用户名和密码"}
            else:
                response = user_manager.login_user(username, password)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"登录失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_logout(self):
        """处理用户登出"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            token = data.get('token', '')
            success = user_manager.logout_user(token)
            
            response = {"success": success, "message": "登出成功" if success else "登出失败"}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"登出失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_score_update(self):
        """处理用户分数更新"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            token = data.get('token', '')
            score = data.get('score', 0)
            playtime = data.get('playtime', 0)
            
            username = user_manager.validate_session(token)
            if not username:
                response = {"success": False, "message": "请先登录"}
            else:
                success = user_manager.update_user_score(username, score, playtime)
                response = {"success": success, "message": "分数更新成功" if success else "分数更新失败"}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"更新失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_stats(self):
        """处理用户统计查询"""
        try:
            stats = user_manager.get_user_stats()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": f"获取统计失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_list(self):
        """处理用户列表查询"""
        try:
            users = user_manager.get_all_users()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(users, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": f"获取用户列表失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_api(self, path):
        """处理用户API请求"""
        try:
            # 解析路径，例如 /api/users/info/username
            parts = path.split('/')
            if len(parts) >= 4:
                action = parts[3]
                
                if action == 'info' and len(parts) >= 5:
                    username = parts[4]
                    user_info = user_manager.get_user_info(username)
                    if user_info:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(json.dumps(user_info, ensure_ascii=False).encode('utf-8'))
                    else:
                        self.send_response(404)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        response = {"error": "用户不存在"}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"error": "API不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"error": "API路径错误"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": f"API处理失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_admin_action(self, path):
        """处理用户管理员操作"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            action = path.split('/')[-1]  # 获取操作类型
            username = data.get('username', '')
            
            if action == 'delete':
                success = user_manager.delete_user(username)
                message = "删除成功" if success else "删除失败"
            elif action == 'ban':
                success = user_manager.ban_user(username)
                message = "禁用成功" if success else "禁用失败"
            elif action == 'unban':
                success = user_manager.unban_user(username)
                message = "解禁成功" if success else "解禁失败"
            else:
                success = False
                message = "未知操作"
            
            response = {"success": success, "message": message}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"操作失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_leaderboard(self):
        """处理排行榜查询"""
        try:
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            limit = int(query_params.get('limit', [10])[0])  # 默认获取前10名
            
            # 从用户管理器获取所有用户数据
            all_users = user_manager.get_all_users()
            
            # 创建排行榜数据：根据最佳分数排序
            leaderboard = []
            for user_data in all_users:
                if user_data.get('best_score', 0) > 0:  # 只包含有分数的用户
                    leaderboard.append({
                        'username': user_data.get('username', ''),
                        'score': user_data.get('best_score', 0),
                        'total_score': user_data.get('total_score', 0),
                        'games_played': user_data.get('games_played', 0),
                        'created_at': user_data.get('created_at', ''),
                        'last_login': user_data.get('last_login', '')
                    })
            
            # 按最佳分数降序排序
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            
            # 限制返回数量
            leaderboard = leaderboard[:limit]
            
            print(f"[排行榜] 获取排行榜成功，返回{len(leaderboard)}条记录")
            
            response = {
                "success": True,
                "data": leaderboard,
                "total": len(all_users),
                "message": f"成功获取前{len(leaderboard)}名排行榜"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[排行榜] 获取排行榜失败: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {
                "success": False,
                "error": f"获取排行榜失败: {str(e)}",
                "data": []
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

def run_server(port=8000):
    """启动服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, GameAPIHandler)
    print(f"🚀 FlapPy Bird API服务器启动成功!")
    print(f"📍 服务地址: http://localhost:{port}")
    print(f"📋 API文档: http://localhost:{port}")
    print(f"❤️  健康检查: http://localhost:{port}/health")
    print("按 Ctrl+C 停止服务器...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        httpd.server_close()

if __name__ == "__main__":
    run_server() 