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

    def send_cors_headers(self):
        """发送CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

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
            # 显示首页而不是直接跳转到游戏
            self.serve_static_file('/index.html')
            
        elif path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        elif path == '/api/downloads/desktop':
            try:
                print(f"[下载] 收到下载请求: {path}")
                print(f"[下载] 请求方法: {self.command}")
                print(f"[下载] 用户代理: {self.headers.get('User-Agent', 'Unknown')}")
                
                # 解析查询参数
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                download_type = query_params.get('type', ['exe'])[0]
                
                print(f"[下载] 请求类型: {download_type}")
                print(f"[下载] 当前目录: {os.getcwd()}")
                
                # 获取项目根目录
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                print(f"[下载] 项目根目录: {project_root}")
                
                if download_type == 'source':
                    # 提供源码版本
                    print("[下载] 提供源码版本...")
                    self._serve_source_download(project_root)
                elif download_type == 'compatibility':
                    # 提供兼容性说明
                    print("[下载] 提供兼容性说明...")
                    self._serve_compatibility_guide()
                else:
                    # 尝试提供EXE版本
                    exe_path = os.path.join(project_root, 'scripts', 'FlapPyBird.exe')
                    print(f"[下载] 查找EXE文件: {exe_path}")
                    
                    if os.path.exists(exe_path):
                        file_size = os.path.getsize(exe_path)
                        print(f"[下载] 找到EXE文件，大小: {file_size / (1024*1024):.1f} MB")
                        
                        # 检查文件大小，如果太小可能是Git LFS指针文件
                        if file_size < 10 * 1024 * 1024:  # 小于10MB
                            print(f"[下载] 警告: EXE文件大小异常 ({file_size} bytes)")
                            print("[下载] 可能是Git LFS指针文件，自动切换到源码版本")
                            self._serve_source_download(project_root)
                            return
                        
                        print("[下载] 直接提供EXE文件...")
                        
                        # 设置响应头
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/octet-stream')
                        self.send_header('Content-Disposition', 'attachment; filename="FlapPyBird.exe"')
                        self.send_header('Content-Length', str(file_size))
                        self.end_headers()
                        
                        # 流式传输文件
                        print("[下载] 开始发送EXE文件...")
                        bytes_sent = 0
                        chunk_size = 64 * 1024  # 64KB chunks
                        
                        with open(exe_path, 'rb') as f:
                            while True:
                                chunk = f.read(chunk_size)
                                if not chunk:
                                    break
                                
                                self.wfile.write(chunk)
                                bytes_sent += len(chunk)
                                
                                # 每10MB显示一次进度
                                if bytes_sent % (10 * 1024 * 1024) == 0:
                                    mb_sent = bytes_sent / (1024 * 1024)
                                    print(f"[下载] 已发送: {mb_sent:.1f} MB")
                        
                        total_mb = bytes_sent / (1024 * 1024)
                        print(f"[下载] EXE文件发送完成: {total_mb:.1f} MB")
                        
                    else:
                        print("[下载] EXE文件不存在，提供源码版本...")
                        self._serve_source_download(project_root)
                        
            except Exception as e:
                print(f"[下载] 错误: {e}")
                import traceback
                traceback.print_exc()
                self.send_error(500, f"下载失败: {str(e)}")
            
        else:
            # 提供静态文件服务
            self.serve_static_file(path)

    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/downloads/track':
            self.handle_download_tracking()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": "Not Found"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

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

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

    def _serve_source_download(self, project_root):
        """提供源码版本下载"""
        try:
            import zipfile
            import io
            import time
            
            # 创建内存中的ZIP文件
            zip_buffer = io.BytesIO()
            timestamp = time.strftime("%Y%m%d")
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # 添加游戏源码
                game_dir = os.path.join(project_root, 'game-desktop')
                if os.path.exists(game_dir):
                    for root, dirs, files in os.walk(game_dir):
                        for file in files:
                            if file.endswith(('.py', '.png', '.wav', '.ico', '.json')):
                                file_path = os.path.join(root, file)
                                arc_name = os.path.relpath(file_path, project_root)
                                zip_file.write(file_path, arc_name)
                
                # 添加启动脚本
                run_script = os.path.join(project_root, '启动桌面游戏.bat')
                if os.path.exists(run_script):
                    zip_file.write(run_script, '启动桌面游戏.bat')
                
                # 添加兼容性说明
                compatibility_file = os.path.join(project_root, 'scripts', '兼容性解决方案.txt')
                if os.path.exists(compatibility_file):
                    zip_file.write(compatibility_file, '兼容性解决方案.txt')
                
                # 添加README
                readme_content = f"""🎮 FlapPy Bird 源码版 - {timestamp}

📁 文件说明:
• game-desktop/ : 游戏源代码
• 启动桌面游戏.bat : 一键启动脚本
• 兼容性解决方案.txt : 详细说明文档

🚀 运行方法:
方法1: 双击 启动桌面游戏.bat (推荐)
方法2: 命令行运行 python game-desktop/main.py

📋 系统要求:
• Python 3.8+
• pygame库 (会自动安装)

✨ 特点:
• 100%兼容性保证
• 无需额外运行时库
• 启动速度快
• 文件体积小

🔧 如果遇到问题，请查看"兼容性解决方案.txt"
"""
                zip_file.writestr('README.txt', readme_content.encode('utf-8'))
            
            zip_data = zip_buffer.getvalue()
            zip_size = len(zip_data)
            
            print(f"[下载] 源码ZIP创建成功，大小: {zip_size / 1024:.1f} KB")
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', f'attachment; filename="FlapPyBird-Source-{timestamp}.zip"')
            self.send_header('Content-Length', str(zip_size))
            self.end_headers()
            
            # 发送文件数据
            self.wfile.write(zip_data)
            print(f"[下载] 源码版本发送完成: {zip_size / 1024:.1f} KB")
            
        except Exception as e:
            print(f"[下载] 源码打包错误: {e}")
            self.send_error(500, f"源码打包失败: {str(e)}")
    
    def _serve_compatibility_guide(self):
        """提供兼容性说明下载"""
        try:
            guide_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', '兼容性解决方案.txt')
            
            if os.path.exists(guide_path):
                with open(guide_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content_bytes = content.encode('utf-8')
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                # 使用URL编码的文件名避免中文编码问题
                import urllib.parse
                filename_encoded = urllib.parse.quote('兼容性解决方案.txt')
                self.send_header('Content-Disposition', f'attachment; filename*=UTF-8\'\'{filename_encoded}')
                self.send_header('Content-Length', str(len(content_bytes)))
                self.end_headers()
                
                self.wfile.write(content_bytes)
                print("[下载] 兼容性说明发送完成")
            else:
                self.send_error(404, "兼容性说明文件不存在")
                
        except Exception as e:
            print(f"[下载] 兼容性说明错误: {e}")
            # 使用英文错误信息避免编码问题
            self.send_error(500, "Compatibility guide download failed")

def run_server(port=None):
    """启动服务器 - 适配Replit环境"""
    # 自动检测运行环境和端口
    if port is None:
        port = int(os.environ.get('PORT', 8000))  # Replit使用PORT环境变量
    
    # Replit环境需要绑定到0.0.0.0，本地开发可以使用localhost
    if os.environ.get('REPL_ID'):  # Replit环境
        host = '0.0.0.0'
        repl_slug = os.environ.get('REPL_SLUG', 'flappybird')
        repl_owner = os.environ.get('REPL_OWNER', 'user')
        server_url = f"https://{repl_slug}.{repl_owner}.repl.co"
        print(f"🌐 Replit环境检测成功")
        print(f"🚀 FlapPy Bird Web版公网服务器启动!")
        print(f"📍 公网地址: {server_url}")
        print(f"🎮 直接游戏: {server_url} (自动跳转到游戏)")
        print(f"🎯 游戏页面: {server_url}/game.html")
        print(f"❤️  状态检查: {server_url}/health")
    else:  # 本地环境
        host = ''
        print(f"💻 本地开发环境")
        print(f"🚀 FlapPy Bird API服务器启动成功!")
        print(f"📍 本地地址: http://localhost:{port}")
        print(f"🎮 直接游戏: http://localhost:{port}")
        print(f"🎯 游戏页面: http://localhost:{port}/game.html")
        print(f"❤️  状态检查: http://localhost:{port}/health")
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, GameAPIHandler)
    
    print(f"🔧 服务器配置: {host if host else 'localhost'}:{port}")
    print("💡 按 Ctrl+C 停止服务器")
    print("🎉 一切就绪！在浏览器中访问上面的链接开始游戏!")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        httpd.server_close()

if __name__ == "__main__":
    run_server() 