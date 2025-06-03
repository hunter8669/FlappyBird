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
from datetime import datetime, timedelta
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        super().end_headers()

    def send_cors_headers(self):
        """发送CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
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
            
        # 路由重定向 - 让用户友好的URL重定向到实际的HTML文件
        elif path == '/login':
            self.send_response(302)
            self.send_header('Location', '/login.html')
            self.end_headers()
            
        elif path == '/register':
            self.send_response(302)
            self.send_header('Location', '/register.html')
            self.end_headers()
            
        elif path == '/about':
            self.send_response(302)
            self.send_header('Location', '/about.html')
            self.end_headers()
            
        elif path == '/download':
            self.send_response(302)
            self.send_header('Location', '/test_download.html')
            self.end_headers()
            
        elif path == '/admin':
            # 管理后台首页
            self.send_response(302)
            self.send_header('Location', '/admin_dashboard.html')
            self.end_headers()
        
        elif path == '/admin-login':
            # 管理员登录页面
            self.send_response(302)
            self.send_header('Location', '/admin_login.html')
            self.end_headers()
            
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
            
        elif path == '/api/downloads/track':
            self.handle_download_tracking()
        elif path == '/api/sms/send':
            self.handle_sms_send()
        elif path == '/api/users/register':
            self.handle_user_register()
        elif path == '/api/users/login':
            self.handle_user_login()
        elif path == '/api/users/check':
            self.handle_user_check()
        elif path == '/api/users/logout':
            self.handle_user_logout()
        elif path == '/api/game/submit':
            self.handle_game_submit_score()
        elif path == '/api/game/leaderboard':
            self.handle_game_leaderboard()
        elif path == '/api/game/history':
            self.handle_user_game_history()
        elif path == '/api/admin/login':
            self.handle_admin_login()
        elif path == '/api/admin/logout':
            self.handle_admin_logout()
        elif path == '/api/admin/check':
            self.handle_admin_check()
        elif path == '/api/admin/stats':
            self.handle_admin_stats()
        elif path == '/api/admin/logs/recent':
            self.handle_admin_logs_recent()
        elif path.startswith('/api/admin/users'):
            self.handle_admin_users_api(path)
        elif path.startswith('/api/admin/admins'):
            self.handle_admin_admins_api(path)
        elif path.startswith('/api/admin/frontend'):
            self.handle_admin_frontend_api(path)
        elif path == '/api/admin/stats':
            self.handle_admin_stats()
        elif path == '/api/admin/logs/recent':
            self.handle_admin_logs_recent()
        else:
            # 提供静态文件服务
            self.serve_static_file(path)

    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/downloads/track':
            self.handle_download_tracking()
        elif path == '/api/sms/send':
            self.handle_sms_send()
        elif path == '/api/users/register':
            self.handle_user_register()
        elif path == '/api/users/login':
            self.handle_user_login()
        elif path == '/api/users/check':
            self.handle_user_check()
        elif path == '/api/users/logout':
            self.handle_user_logout()
        elif path == '/api/game/submit':
            self.handle_game_submit_score()
        elif path == '/api/game/leaderboard':
            self.handle_game_leaderboard()
        elif path == '/api/game/history':
            self.handle_user_game_history()
        elif path == '/api/admin/login':
            self.handle_admin_login()
        elif path == '/api/admin/logout':
            self.handle_admin_logout()
        elif path == '/api/admin/check':
            self.handle_admin_check()
        elif path == '/api/admin/stats':
            self.handle_admin_stats()
        elif path == '/api/admin/logs/recent':
            self.handle_admin_logs_recent()
        elif path.startswith('/api/admin/users'):
            self.handle_admin_users_api(path)
        elif path.startswith('/api/admin/admins'):
            self.handle_admin_admins_api(path)
        elif path.startswith('/api/admin/frontend'):
            self.handle_admin_frontend_api(path)
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": "Not Found"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_PUT(self):
        """处理PUT请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith('/api/admin/admins/'):
            self.handle_admin_admins_api(path)
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": "Not Found"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_DELETE(self):
        """处理DELETE请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith('/api/admin/admins/'):
            self.handle_admin_admins_api(path)
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

    def handle_sms_send(self):
        """处理短信验证码发送"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                phone = data.get('phone', '').strip()
                
                print(f"[短信] 收到验证码发送请求: {phone}")
                
                # 手机号格式验证
                import re
                if not re.match(r'^1[3-9]\d{9}$', phone):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "手机号格式不正确"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 生成6位验证码
                import random
                verification_code = str(random.randint(100000, 999999))
                
                # 保存验证码到临时存储（实际项目中应该使用Redis或数据库）
                sms_storage_file = 'sms_codes.json'
                if os.path.exists(sms_storage_file):
                    with open(sms_storage_file, 'r', encoding='utf-8') as f:
                        sms_data = json.load(f)
                else:
                    sms_data = {}
                
                # 清理过期验证码（超过10分钟）
                current_time = datetime.now()
                for stored_phone in list(sms_data.keys()):
                    code_time = datetime.fromisoformat(sms_data[stored_phone]['timestamp'])
                    if (current_time - code_time).total_seconds() > 600:  # 10分钟
                        del sms_data[stored_phone]
                
                # 存储新验证码
                sms_data[phone] = {
                    'code': verification_code,
                    'timestamp': current_time.isoformat(),
                    'attempts': 0
                }
                
                with open(sms_storage_file, 'w', encoding='utf-8') as f:
                    json.dump(sms_data, f, ensure_ascii=False, indent=2)
                
                print(f"[短信] 验证码已生成: {phone} -> {verification_code}")
                
                # 模拟短信发送（实际项目中应该调用短信服务商API）
                # 这里我们直接返回成功，验证码会打印在控制台
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {
                    "success": True, 
                    "message": f"验证码已发送到 {phone[:3]}****{phone[-4:]}",
                    "debug_code": verification_code  # 演示版本显示验证码
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
        except Exception as e:
            print(f"[短信] 发送失败: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": "短信发送失败，请稍后重试"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_register(self):
        """处理用户注册"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                username = data.get('username', '').strip()
                phone = data.get('phone', '').strip()
                sms_code = data.get('sms_code', '').strip()
                password = data.get('password', '')
                email = data.get('email', '').strip()
                
                print(f"[注册] 收到注册请求: {username}, {phone}")
                
                # 输入验证
                import re
                if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]{3,20}$', username):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户名格式不正确"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                if not re.match(r'^1[3-9]\d{9}$', phone):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "手机号格式不正确"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                if len(password) < 6:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "密码至少需要6个字符"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 验证短信验证码
                sms_storage_file = 'sms_codes.json'
                if os.path.exists(sms_storage_file):
                    with open(sms_storage_file, 'r', encoding='utf-8') as f:
                        sms_data = json.load(f)
                    
                    if phone not in sms_data:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        response = {"success": False, "message": "请先获取验证码"}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return
                    
                    stored_code = sms_data[phone]['code']
                    code_time = datetime.fromisoformat(sms_data[phone]['timestamp'])
                    current_time = datetime.now()
                    
                    # 检查验证码是否过期（10分钟）
                    if (current_time - code_time).total_seconds() > 600:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        response = {"success": False, "message": "验证码已过期，请重新获取"}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return
                    
                    # 检查验证码是否正确
                    if stored_code != sms_code:
                        # 记录错误次数
                        sms_data[phone]['attempts'] = sms_data[phone].get('attempts', 0) + 1
                        with open(sms_storage_file, 'w', encoding='utf-8') as f:
                            json.dump(sms_data, f, ensure_ascii=False, indent=2)
                        
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        response = {"success": False, "message": "验证码不正确"}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return
                else:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "请先获取验证码"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 检查用户是否已存在
                users_file = 'users.json'
                if os.path.exists(users_file):
                    with open(users_file, 'r', encoding='utf-8') as f:
                        users_data = json.load(f)
                else:
                    users_data = {}
                
                # 检查用户名和手机号是否已被使用
                for user_id, user_info in users_data.items():
                    if user_info.get('username') == username:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        response = {"success": False, "message": "用户名已被使用"}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return
                    if user_info.get('phone') == phone:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        response = {"success": False, "message": "手机号已被注册"}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return
                
                # 创建新用户
                import hashlib
                import secrets
                
                user_id = secrets.token_hex(16)
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                user_info = {
                    'user_id': user_id,
                    'username': username,
                    'phone': phone if phone else None,
                    'email': email if email else None,
                    'password_hash': password_hash,
                    'created_at': datetime.now().isoformat(),
                    'last_login': None,
                    'best_score': 0,
                    'total_score': 0,
                    'games_played': 0,
                    'is_active': True
                }
                
                users_data[user_id] = user_info
                
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                
                # 删除已使用的验证码
                if phone in sms_data:
                    del sms_data[phone]
                    with open(sms_storage_file, 'w', encoding='utf-8') as f:
                        json.dump(sms_data, f, ensure_ascii=False, indent=2)
                
                print(f"[注册] 用户注册成功: {username} ({user_id})")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {
                    "success": True, 
                    "message": "注册成功！",
                    "user_id": user_id
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
        except Exception as e:
            print(f"[注册] 注册失败: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": "注册失败，请稍后重试"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_login(self):
        """处理用户登录"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                login_id = data.get('login_id', '').strip()  # 可以是用户名或手机号
                password = data.get('password', '')
                
                print(f"[登录] 收到登录请求: {login_id}")
                
                # 查找用户
                users_file = 'users.json'
                if not os.path.exists(users_file):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                user_info = None
                user_id = None
                for uid, info in users_data.items():
                    if info.get('username') == login_id or info.get('phone') == login_id:
                        user_info = info
                        user_id = uid
                        break
                
                if not user_info:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 验证密码
                import hashlib
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                if user_info.get('password_hash') != password_hash:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "密码不正确"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 更新最后登录时间
                user_info['last_login'] = datetime.now().isoformat()
                users_data[user_id] = user_info
                
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                
                # 生成简单的token（实际项目中应该使用JWT）
                import secrets
                token = secrets.token_hex(32)
                
                # 保存token（简化实现）
                tokens_file = 'user_tokens.json'
                if os.path.exists(tokens_file):
                    with open(tokens_file, 'r', encoding='utf-8') as f:
                        tokens_data = json.load(f)
                else:
                    tokens_data = {}
                
                tokens_data[token] = {
                    'user_id': user_id,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
                }
                
                with open(tokens_file, 'w', encoding='utf-8') as f:
                    json.dump(tokens_data, f, ensure_ascii=False, indent=2)
                
                print(f"[登录] 用户登录成功: {user_info['username']} ({user_id})")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {
                    "success": True,
                    "message": "登录成功！",
                    "token": token,
                    "user": {
                        "user_id": user_id,
                        "username": user_info['username'],
                        "phone": user_info['phone'],
                        "email": user_info.get('email'),
                        "best_score": user_info.get('best_score', 0),
                        "total_score": user_info.get('total_score', 0),
                        "games_played": user_info.get('games_played', 0)
                    }
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
        except Exception as e:
            print(f"[登录] 登录失败: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": "登录失败，请稍后重试"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_check(self):
        """处理用户登录状态检查"""
        try:
            # 从Authorization头获取token
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "未登录"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            
            # 检查token
            tokens_file = 'user_tokens.json'
            if not os.path.exists(tokens_file):
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "token无效"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            with open(tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
            
            if token not in tokens_data:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "token无效"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 检查token是否过期
            expires_at = datetime.fromisoformat(tokens_data[token]['expires_at'])
            if datetime.now() > expires_at:
                # 删除过期token
                del tokens_data[token]
                with open(tokens_file, 'w', encoding='utf-8') as f:
                    json.dump(tokens_data, f, ensure_ascii=False, indent=2)
                
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "token已过期"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 获取用户信息
            user_id = tokens_data[token]['user_id']
            users_file = 'users.json'
            
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            if user_id not in users_data:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "用户不存在"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            user_info = users_data[user_id]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {
                "success": True,
                "admin": {
                    "username": user_info['username'],
                    "role": user_info.get('role', 'admin'),
                    "permissions": user_info.get('permissions', [])
                }
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[用户检查] 失败: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": "检查失败"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_logout(self):
        """处理用户登出"""
        try:
            # 从Authorization头获取token
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "未登录"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            
            # 检查token
            tokens_file = 'user_tokens.json'
            if not os.path.exists(tokens_file):
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "token无效"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            with open(tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
            
            if token not in tokens_data:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "token无效"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 检查token是否过期
            expires_at = datetime.fromisoformat(tokens_data[token]['expires_at'])
            if datetime.now() > expires_at:
                # 删除过期token
                del tokens_data[token]
                with open(tokens_file, 'w', encoding='utf-8') as f:
                    json.dump(tokens_data, f, ensure_ascii=False, indent=2)
                
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "token已过期"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 获取用户信息
            user_id = tokens_data[token]['user_id']
            users_file = 'users.json'
            
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            if user_id not in users_data:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "用户不存在"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            user_info = users_data[user_id]
            
            # 更新用户状态为非活跃
            user_info['is_active'] = False
            users_data[user_id] = user_info
            
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            
            # 删除token
            del tokens_data[token]
            with open(tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": True, "message": "用户已登出"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[用户登出] 失败: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": "登出失败"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_game_submit_score(self):
        """处理游戏分数提交"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                user_id = data.get('user_id', '').strip()
                score = data.get('score', 0)
                
                try:
                    score = int(score)
                except (ValueError, TypeError):
                    score = 0
                
                if not user_id:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "缺少用户ID"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 获取用户数据
                users_file = 'users.json'
                if os.path.exists(users_file):
                    with open(users_file, 'r', encoding='utf-8') as f:
                        users_data = json.load(f)
                else:
                    users_data = {}
                
                # 如果用户不存在，创建匿名用户记录
                if user_id not in users_data:
                    users_data[user_id] = {
                        'user_id': user_id,
                        'username': f'游客{user_id[:8]}',
                        'phone': None,
                        'email': None,
                        'created_at': datetime.now().isoformat(),
                        'last_login': datetime.now().isoformat(),
                        'best_score': 0,
                        'total_score': 0,
                        'games_played': 0,
                        'is_active': True,
                        'created_by': 'game'
                    }
                
                # 更新用户游戏数据
                user_info = users_data[user_id]
                user_info['games_played'] = user_info.get('games_played', 0) + 1
                user_info['total_score'] = user_info.get('total_score', 0) + score
                
                # 更新最高分
                current_best = user_info.get('best_score', 0)
                if score > current_best:
                    user_info['best_score'] = score
                    is_new_record = True
                else:
                    is_new_record = False
                
                user_info['last_game_at'] = datetime.now().isoformat()
                
                # 保存用户数据
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                
                # 记录游戏历史
                history_file = 'game_history.json'
                if os.path.exists(history_file):
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                else:
                    history_data = {}
                
                if user_id not in history_data:
                    history_data[user_id] = []
                
                # 添加本次游戏记录
                game_record = {
                    'score': score,
                    'timestamp': datetime.now().isoformat(),
                    'is_new_record': is_new_record
                }
                
                history_data[user_id].append(game_record)
                
                # 只保留最近100条记录
                if len(history_data[user_id]) > 100:
                    history_data[user_id] = history_data[user_id][-100:]
                
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(history_data, f, ensure_ascii=False, indent=2)
                
                print(f"[游戏分数提交] 用户: {user_info['username']} ({user_id}), 分数: {score}, 新记录: {is_new_record}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {
                    "success": True, 
                    "message": "分数提交成功",
                    "score": score,
                    "best_score": user_info['best_score'],
                    "games_played": user_info['games_played'],
                    "is_new_record": is_new_record
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[游戏分数提交] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"分数提交失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_game_leaderboard(self):
        """处理游戏排行榜查询"""
        try:
            # 获取用户数据
            users_file = 'users.json'
            if not os.path.exists(users_file):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": True, "leaderboard": []}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            # 获取排行榜数据
            leaderboard_data = []
            for user_id, user_info in users_data.items():
                if user_info.get('best_score', 0) > 0:  # 只显示有分数的用户
                    leaderboard_data.append({
                        "rank": 0,  # 将在排序后设置
                        "user_id": user_id,
                        "username": user_info.get('username', f'用户{user_id[:8]}'),
                        "best_score": user_info.get('best_score', 0),
                        "total_score": user_info.get('total_score', 0),
                        "games_played": user_info.get('games_played', 0),
                        "last_game_at": user_info.get('last_game_at', user_info.get('created_at', ''))
                    })
            
            # 按最高分降序排序
            leaderboard_data.sort(key=lambda x: x['best_score'], reverse=True)
            
            # 设置排名
            for i, player in enumerate(leaderboard_data):
                player['rank'] = i + 1
            
            # 只返回前50名
            leaderboard_data = leaderboard_data[:50]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": True, "leaderboard": leaderboard_data}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[游戏排行榜] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"获取排行榜失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_user_game_history(self):
        """处理用户游戏历史记录查询"""
        try:
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            user_id = query_params.get('user_id', [''])[0].strip()
            
            if not user_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "缺少用户ID"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 获取用户游戏历史记录
            history_file = 'game_history.json'
            if not os.path.exists(history_file):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": True, "history": []}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            user_history = history_data.get(user_id, [])
            
            # 按时间降序排序（最新的在前面）
            user_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": True, "history": user_history}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[用户游戏历史] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"获取游戏历史失败: {str(e)}"}
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

运行方法:
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

    def handle_admin_login(self):
        """处理管理员登录"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                username = data.get('username', '').strip()
                password = data.get('password', '')
                
                # 确保默认管理员存在
                self.ensure_default_admin()
                
                # 验证管理员账号
                admin_file = 'admin.json'
                with open(admin_file, 'r', encoding='utf-8') as f:
                    admin_data = json.load(f)
                
                # 查找匹配的管理员
                found_admin = None
                admin_id = None
                
                import hashlib
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                for aid, admin_info in admin_data.items():
                    if (admin_info.get('username') == username and 
                        admin_info.get('password_hash') == password_hash and
                        admin_info.get('is_active', True)):
                        found_admin = admin_info
                        admin_id = aid
                        break
                
                if found_admin:
                    # 生成管理员token
                    import secrets
                    admin_token = f"admin_{secrets.token_hex(32)}"
                    
                    # 更新最后登录时间
                    admin_data[admin_id]['last_login'] = datetime.now().isoformat()
                    with open(admin_file, 'w', encoding='utf-8') as f:
                        json.dump(admin_data, f, ensure_ascii=False, indent=2)
                    
                    # 保存管理员token
                    admin_tokens_file = 'admin_tokens.json'
                    if os.path.exists(admin_tokens_file):
                        with open(admin_tokens_file, 'r', encoding='utf-8') as f:
                            tokens_data = json.load(f)
                    else:
                        tokens_data = {}
                    
                    tokens_data[admin_token] = {
                        'admin_id': admin_id,
                        'username': username,
                        'role': found_admin.get('role', 'admin'),
                        'created_at': datetime.now().isoformat(),
                        'expires_at': (datetime.now() + timedelta(hours=8)).isoformat(),
                        'permissions': found_admin.get('permissions', []),
                        'last_used': datetime.now().isoformat()
                    }
                    
                    with open(admin_tokens_file, 'w', encoding='utf-8') as f:
                        json.dump(tokens_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"[管理员登录] 管理员登录成功: {username}")
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {
                        "success": True,
                        "message": "登录成功",
                        "token": admin_token,
                        "admin": {
                            "username": username,
                            "role": found_admin.get('role', 'admin'),
                            "permissions": found_admin.get('permissions', [])
                        }
                    }
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                else:
                    self.send_response(401)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户名或密码不正确，或账号已被禁用"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员登录] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"登录失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_logout(self):
        """处理管理员登出"""
        try:
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "未登录"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            token = auth_header[7:]
            
            # 删除管理员token
            admin_tokens_file = 'admin_tokens.json'
            if os.path.exists(admin_tokens_file):
                with open(admin_tokens_file, 'r', encoding='utf-8') as f:
                    tokens_data = json.load(f)
                
                if token in tokens_data:
                    del tokens_data[token]
                    with open(admin_tokens_file, 'w', encoding='utf-8') as f:
                        json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": True, "message": "登出成功"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员登出] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"登出失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def verify_admin_permission(self, required_permission):
        """验证管理员权限"""
        try:
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return None, "未登录"
            
            token = auth_header[7:]
            
            admin_tokens_file = 'admin_tokens.json'
            if not os.path.exists(admin_tokens_file):
                return None, "token无效"
            
            with open(admin_tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
            
            if token not in tokens_data:
                return None, "token无效"
            
            token_info = tokens_data[token]
            
            # 检查token是否过期
            expires_at = datetime.fromisoformat(token_info['expires_at'])
            if datetime.now() > expires_at:
                del tokens_data[token]
                with open(admin_tokens_file, 'w', encoding='utf-8') as f:
                    json.dump(tokens_data, f, ensure_ascii=False, indent=2)
                return None, "token已过期"
            
            # 更新最后使用时间
            token_info['last_used'] = datetime.now().isoformat()
            tokens_data[token] = token_info
            with open(admin_tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            # 检查权限
            permissions = token_info.get('permissions', [])
            role = token_info.get('role', '')
            
            # 超级管理员拥有所有权限
            if role == 'super_admin' or required_permission in permissions:
                return token_info, None
            else:
                return None, "权限不足"
            
        except Exception as e:
            return None, f"权限验证失败: {str(e)}"

    def handle_admin_check(self):
        """处理管理员状态检查"""
        try:
            token_info, error = self.verify_admin_permission('user_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {
                "success": True,
                "admin": {
                    "username": token_info['username'],
                    "role": token_info.get('role', 'admin'),
                    "permissions": token_info['permissions']
                }
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员检查] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"检查失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_users_api(self, path):
        """处理管理员用户API路由"""
        if path == '/api/admin/users':
            self.handle_admin_users_list()
        elif path == '/api/admin/users/create':
            self.handle_admin_user_create()
        elif path == '/api/admin/users/update':
            self.handle_admin_user_update()
        elif path == '/api/admin/users/delete':
            self.handle_admin_user_delete()
        elif path == '/api/admin/users/batch-delete':
            self.handle_admin_users_batch_delete()
        elif path == '/api/admin/users/reset-password':
            self.handle_admin_user_reset_password()
        elif path.startswith('/api/admin/users/export'):
            self.handle_admin_users_export()
        elif path == '/api/admin/users/statistics':
            self.handle_admin_users_statistics()
        elif path.startswith('/api/admin/users/detail'):
            self.handle_admin_user_detail()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": "API不存在"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_users_list(self):
        """处理管理员用户列表查询"""
        try:
            token_info, error = self.verify_admin_permission('user_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 解析查询参数
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            page = int(query_params.get('page', ['1'])[0])
            limit = int(query_params.get('limit', ['20'])[0])
            search = query_params.get('search', [''])[0].strip()
            
            # 获取用户数据
            users_file = 'users.json'
            if not os.path.exists(users_file):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": True, "users": [], "total": 0, "page": page, "limit": limit}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            # 过滤用户数据
            users_list = []
            for user_id, user_info in users_data.items():
                # 搜索过滤
                if search and search.lower() not in user_info.get('username', '').lower() and search not in user_info.get('phone', ''):
                    continue
                
                users_list.append({
                    "user_id": user_id,
                    "username": user_info.get('username', ''),
                    "phone": user_info.get('phone', ''),
                    "email": user_info.get('email', ''),
                    "created_at": user_info.get('created_at', ''),
                    "last_login": user_info.get('last_login', ''),
                    "best_score": user_info.get('best_score', 0),
                    "games_played": user_info.get('games_played', 0),
                    "is_active": user_info.get('is_active', True),
                    "created_by": user_info.get('created_by', 'user')
                })
            
            # 分页
            total = len(users_list)
            start = (page - 1) * limit
            end = start + limit
            users_list = users_list[start:end]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {
                "success": True,
                "users": users_list,
                "total": total,
                "page": page,
                "limit": limit
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员用户列表] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"获取用户列表失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_stats(self):
        """处理管理员统计数据查询"""
        try:
            token_info, error = self.verify_admin_permission('data_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 获取用户统计
            users_file = 'users.json'
            users_stats = {"total": 0, "active": 0, "today": 0}
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                today = datetime.now().date()
                users_stats["total"] = len(users_data)
                
                for user_info in users_data.values():
                    # 活跃用户（最近7天登录过）
                    last_login = user_info.get('last_login')
                    if last_login:
                        try:
                            last_login_date = datetime.fromisoformat(last_login).date()
                            if (today - last_login_date).days <= 7:
                                users_stats["active"] += 1
                        except:
                            pass
                    
                    # 今日注册用户
                    created_at = user_info.get('created_at')
                    if created_at:
                        try:
                            created_date = datetime.fromisoformat(created_at).date()
                            if created_date == today:
                                users_stats["today"] += 1
                        except:
                            pass
            
            # 获取下载统计
            downloads_file = 'download_stats.json'
            downloads_stats = {"total": 0, "today": 0}
            if os.path.exists(downloads_file):
                with open(downloads_file, 'r', encoding='utf-8') as f:
                    downloads_data = json.load(f)
                
                downloads = downloads_data.get('downloads', [])
                downloads_stats["total"] = len(downloads)
                
                today = datetime.now().date()
                for download in downloads:
                    try:
                        download_date = datetime.fromisoformat(download['timestamp']).date()
                        if download_date == today:
                            downloads_stats["today"] += 1
                    except:
                        pass
            
            # 获取游戏统计
            games_stats = {"total": 0, "best_score": 0}
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                total_games = 0
                best_score = 0
                for user_info in users_data.values():
                    total_games += user_info.get('games_played', 0)
                    best_score = max(best_score, user_info.get('best_score', 0))
                
                games_stats["total"] = total_games
                games_stats["best_score"] = best_score
            
            # 系统运行时间（简化计算）
            import time
            uptime_hours = int(time.time() % (24 * 3600) / 3600)
            system_stats = {
                "uptime": f"{uptime_hours}h",
                "status": "正常"
            }
            
            stats = {
                "users": users_stats,
                "downloads": downloads_stats,
                "games": games_stats,
                "system": system_stats
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员统计] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"error": f"获取统计数据失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_logs_recent(self):
        """处理获取最近日志"""
        try:
            token_info, error = self.verify_admin_permission('system_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 模拟日志数据（实际项目中应该从日志文件读取）
            logs = [
                {
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": "用户管理系统正常运行"
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                    "level": "INFO",
                    "message": f"管理员 {token_info.get('username', 'admin')} 登录成功"
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
                    "level": "INFO",
                    "message": "系统启动完成"
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                    "level": "WARN",
                    "message": "检测到过期验证码，已自动清理"
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=20)).isoformat(),
                    "level": "INFO",
                    "message": "定时任务执行完成"
                }
            ]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": True, "logs": logs}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员日志] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"获取日志失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_users_statistics(self):
        """处理用户统计数据"""
        try:
            token_info, error = self.verify_admin_permission('data_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 获取用户数据
            users_file = 'users.json'
            if not os.path.exists(users_file):
                stats = {
                    "total_users": 0,
                    "active_users": 0,
                    "new_users_today": 0,
                    "total_games": 0,
                    "average_score": 0
                }
            else:
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                today = datetime.now().date()
                total_users = len(users_data)
                active_users = 0
                new_users_today = 0
                total_games = 0
                total_score = 0
                
                for user_info in users_data.values():
                    # 活跃用户（最近7天登录过）
                    last_login = user_info.get('last_login')
                    if last_login:
                        try:
                            last_login_date = datetime.fromisoformat(last_login).date()
                            if (today - last_login_date).days <= 7:
                                active_users += 1
                        except:
                            pass
                    
                    # 今日注册用户
                    created_at = user_info.get('created_at')
                    if created_at:
                        try:
                            created_date = datetime.fromisoformat(created_at).date()
                            if created_date == today:
                                new_users_today += 1
                        except:
                            pass
                    
                    # 游戏统计
                    total_games += user_info.get('games_played', 0)
                    total_score += user_info.get('total_score', 0)
                
                average_score = int(total_score / total_users) if total_users > 0 else 0
                
                stats = {
                    "total_users": total_users,
                    "active_users": active_users,
                    "new_users_today": new_users_today,
                    "total_games": total_games,
                    "average_score": average_score
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": True, "statistics": stats}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[用户统计] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"获取用户统计失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_user_create(self):
        """处理管理员创建用户"""
        try:
            # 检查权限：只有超级管理员才能管理其他管理员
            token_info, error = self.verify_admin_permission('admin_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 额外检查：确保是超级管理员
            current_role = token_info.get('role', '')
            if current_role != 'super_admin':
                self.send_response(403)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "只有超级管理员才能创建其他管理员"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                username = data.get('username', '').strip()
                phone = data.get('phone', '').strip()
                email = data.get('email', '').strip()
                password = data.get('password', '')
                
                # 输入验证
                import re
                if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]{3,20}$', username):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户名格式不正确"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                if phone and not re.match(r'^1[3-9]\d{9}$', phone):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "手机号格式不正确"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                if len(password) < 6:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "密码至少需要6个字符"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 检查用户是否已存在
                users_file = 'users.json'
                if os.path.exists(users_file):
                    with open(users_file, 'r', encoding='utf-8') as f:
                        users_data = json.load(f)
                else:
                    users_data = {}
                
                for user_info in users_data.values():
                    if user_info.get('username') == username:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        response = {"success": False, "message": "用户名已被使用"}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return
                    if phone and user_info.get('phone') == phone:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        response = {"success": False, "message": "手机号已被注册"}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return
                
                # 创建新用户
                import hashlib
                import secrets
                
                user_id = secrets.token_hex(16)
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                user_info = {
                    'user_id': user_id,
                    'username': username,
                    'phone': phone if phone else None,
                    'email': email if email else None,
                    'password_hash': password_hash,
                    'created_at': datetime.now().isoformat(),
                    'last_login': None,
                    'best_score': 0,
                    'total_score': 0,
                    'games_played': 0,
                    'is_active': True,
                    'created_by': 'admin'
                }
                
                users_data[user_id] = user_info
                
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                
                print(f"[管理员创建用户] 用户创建成功: {username} ({user_id})")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": True, "message": "用户创建成功", "user_id": user_id}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员创建用户] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"用户创建失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_user_update(self):
        """处理管理员更新用户信息"""
        try:
            token_info, error = self.verify_admin_permission('user_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                user_id = data.get('user_id', '').strip()
                
                if not user_id:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "缺少用户ID"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 读取用户数据
                users_file = 'users.json'
                if not os.path.exists(users_file):
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                if user_id not in users_data:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 更新用户信息
                user_info = users_data[user_id]
                old_username = user_info.get('username', '')
                
                # 检查用户名重复（如果修改了用户名）
                new_username = data.get('username', '').strip()
                if new_username and new_username != old_username:
                    for uid, uinfo in users_data.items():
                        if uid != user_id and uinfo.get('username') == new_username:
                            self.send_response(400)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            response = {"success": False, "message": "用户名已被使用"}
                            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                            return
                    user_info['username'] = new_username
                
                # 检查手机号重复（如果修改了手机号）
                new_phone = data.get('phone', '').strip()
                if new_phone and new_phone != user_info.get('phone', ''):
                    for uid, uinfo in users_data.items():
                        if uid != user_id and uinfo.get('phone') == new_phone:
                            self.send_response(400)
                            self.send_header('Content-Type', 'application/json; charset=utf-8')
                            self.end_headers()
                            response = {"success": False, "message": "手机号已被使用"}
                            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                            return
                    user_info['phone'] = new_phone
                
                # 更新其他字段
                if 'email' in data:
                    user_info['email'] = data['email'].strip()
                if 'is_active' in data:
                    user_info['is_active'] = bool(data['is_active'])
                
                # 如果有新密码
                if 'password' in data and data['password'].strip():
                    import hashlib
                    user_info['password_hash'] = hashlib.sha256(data['password'].encode()).hexdigest()
                
                # 保存数据
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                
                print(f"[管理员更新用户] 用户信息更新成功: {user_info.get('username')} ({user_id})")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": True, "message": "用户信息更新成功"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员更新用户] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"更新用户失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_user_delete(self):
        """处理管理员删除单个用户"""
        try:
            token_info, error = self.verify_admin_permission('user_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                user_id = data.get('user_id', '').strip()
                
                if not user_id:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "缺少用户ID"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 删除用户
                users_file = 'users.json'
                if not os.path.exists(users_file):
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                if user_id not in users_data:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                username = users_data[user_id].get('username', '')
                del users_data[user_id]
                
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                
                # 也删除相关的游戏历史
                history_file = 'game_history.json'
                if os.path.exists(history_file):
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                    
                    if user_id in history_data:
                        del history_data[user_id]
                        with open(history_file, 'w', encoding='utf-8') as f:
                            json.dump(history_data, f, ensure_ascii=False, indent=2)
                
                print(f"[管理员删除用户] 用户删除成功: {username} ({user_id})")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": True, "message": "用户删除成功"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员删除用户] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"用户删除失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_users_batch_delete(self):
        """处理管理员批量删除用户"""
        try:
            token_info, error = self.verify_admin_permission('user_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                user_ids = data.get('user_ids', [])
                
                if not user_ids:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "缺少用户ID列表"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 批量删除用户
                users_file = 'users.json'
                if not os.path.exists(users_file):
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户数据不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                deleted_count = 0
                for user_id in user_ids:
                    if user_id in users_data:
                        del users_data[user_id]
                        deleted_count += 1
                
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                
                # 批量删除游戏历史
                history_file = 'game_history.json'
                if os.path.exists(history_file):
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                    
                    for user_id in user_ids:
                        if user_id in history_data:
                            del history_data[user_id]
                    
                    with open(history_file, 'w', encoding='utf-8') as f:
                        json.dump(history_data, f, ensure_ascii=False, indent=2)
                
                print(f"[管理员批量删除] 删除用户数量: {deleted_count}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": True, "message": f"成功删除 {deleted_count} 个用户"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员批量删除] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"批量删除失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_user_reset_password(self):
        """处理管理员重置用户密码"""
        try:
            token_info, error = self.verify_admin_permission('user_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                user_id = data.get('user_id', '').strip()
                new_password = data.get('new_password', '')
                
                if not user_id:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "缺少用户ID"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                if len(new_password) < 6:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "密码至少需要6个字符"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 重置密码
                users_file = 'users.json'
                if not os.path.exists(users_file):
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                if user_id not in users_data:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 更新密码
                import hashlib
                password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                users_data[user_id]['password_hash'] = password_hash
                
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                
                username = users_data[user_id].get('username', '')
                print(f"[管理员重置密码] 密码重置成功: {username} ({user_id})")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": True, "message": "密码重置成功"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员重置密码] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"密码重置失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_users_export(self):
        """处理用户数据导出"""
        try:
            token_info, error = self.verify_admin_permission('data_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 解析查询参数
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            export_format = query_params.get('format', ['json'])[0]
            
            # 获取用户数据
            users_file = 'users.json'
            if not os.path.exists(users_file):
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "暂无用户数据"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            if export_format == 'csv':
                # 导出CSV格式
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # 写入标题行
                writer.writerow(['用户ID', '用户名', '手机号', '邮箱', '注册时间', '最后登录', '最高分', '游戏次数', '状态'])
                
                # 写入数据行
                for user_id, user_info in users_data.items():
                    writer.writerow([
                        user_id,
                        user_info.get('username', ''),
                        user_info.get('phone', ''),
                        user_info.get('email', ''),
                        user_info.get('created_at', ''),
                        user_info.get('last_login', ''),
                        user_info.get('best_score', 0),
                        user_info.get('games_played', 0),
                        '正常' if user_info.get('is_active', True) else '禁用'
                    ])
                
                csv_content = output.getvalue()
                output.close()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename="users_export.csv"')
                self.end_headers()
                self.wfile.write(csv_content.encode('utf-8-sig'))  # 使用BOM解决Excel中文乱码
                
            else:
                # 导出JSON格式
                # 清理敏感信息
                export_data = {}
                for user_id, user_info in users_data.items():
                    export_data[user_id] = {
                        'user_id': user_id,
                        'username': user_info.get('username', ''),
                        'phone': user_info.get('phone', ''),
                        'email': user_info.get('email', ''),
                        'created_at': user_info.get('created_at', ''),
                        'last_login': user_info.get('last_login', ''),
                        'best_score': user_info.get('best_score', 0),
                        'total_score': user_info.get('total_score', 0),
                        'games_played': user_info.get('games_played', 0),
                        'is_active': user_info.get('is_active', True),
                        'created_by': user_info.get('created_by', 'user')
                    }
                
                json_content = json.dumps(export_data, ensure_ascii=False, indent=2)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename="users_export.json"')
                self.end_headers()
                self.wfile.write(json_content.encode('utf-8'))
            
            print(f"[用户数据导出] 导出格式: {export_format}, 用户数量: {len(users_data)}")
            
        except Exception as e:
            print(f"[用户数据导出] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"数据导出失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_frontend_api(self, path):
        """处理前端管理API路由"""
        if path == '/api/admin/frontend/stats':
            self.handle_admin_frontend_stats()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": "API不存在"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_frontend_stats(self):
        """处理前端管理统计数据"""
        try:
            token_info, error = self.verify_admin_permission('system_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 前端文件统计
            frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
            
            stats = {
                "total_files": 0,
                "html_files": 0,
                "css_files": 0,
                "js_files": 0,
                "image_files": 0,
                "total_size": 0
            }
            
            if os.path.exists(frontend_dir):
                for root, dirs, files in os.walk(frontend_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        
                        stats["total_files"] += 1
                        stats["total_size"] += file_size
                        
                        if file.endswith('.html'):
                            stats["html_files"] += 1
                        elif file.endswith('.css'):
                            stats["css_files"] += 1
                        elif file.endswith('.js'):
                            stats["js_files"] += 1
                        elif file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico')):
                            stats["image_files"] += 1
            
            # 转换文件大小为MB
            stats["total_size_mb"] = round(stats["total_size"] / (1024 * 1024), 2)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": True, "stats": stats}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[前端管理统计] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"获取前端统计失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_admins_api(self, path):
        """处理管理员管理API路由"""
        if path == '/api/admin/admins':
            if self.command == 'GET':
                self.handle_admin_admins_list()
            elif self.command == 'POST':
                self.handle_admin_admin_create()
        elif path.startswith('/api/admin/admins/'):
            admin_id = path.split('/api/admin/admins/')[1]
            if self.command == 'PUT':
                self.handle_admin_admin_update(admin_id)
            elif self.command == 'DELETE':
                self.handle_admin_admin_delete(admin_id)
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": "API不存在"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_admins_list(self):
        """获取管理员列表"""
        try:
            # 检查权限：只有超级管理员才能管理其他管理员
            token_info, error = self.verify_admin_permission('admin_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 额外检查：确保是超级管理员
            current_role = token_info.get('role', '')
            if current_role != 'super_admin':
                self.send_response(403)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "只有超级管理员才能查看管理员列表"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 读取管理员数据
            admin_file = 'admin.json'
            if not os.path.exists(admin_file):
                # 创建默认管理员
                self.ensure_default_admin()
            
            with open(admin_file, 'r', encoding='utf-8') as f:
                admin_data = json.load(f)
            
            # 清理敏感信息
            safe_admin_list = []
            for admin_id, admin_info in admin_data.items():
                safe_admin_list.append({
                    'admin_id': admin_id,
                    'username': admin_info.get('username', ''),
                    'email': admin_info.get('email', ''),
                    'role': admin_info.get('role', 'admin'),
                    'created_at': admin_info.get('created_at', ''),
                    'last_login': admin_info.get('last_login', ''),
                    'is_active': admin_info.get('is_active', True),
                    'permissions': admin_info.get('permissions', [])
                })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {
                "success": True,
                "data": safe_admin_list,
                "total": len(safe_admin_list)
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员列表] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"获取管理员列表失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_admin_create(self):
        """创建新管理员"""
        try:
            token_info, error = self.verify_admin_permission('user_management')  # 降低权限要求
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                username = data.get('username', '').strip()
                password = data.get('password', '').strip()
                email = data.get('email', '').strip()
                role = data.get('role', 'admin').strip()
                permissions = data.get('permissions', [])
                
                if not username or not password:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "用户名和密码不能为空"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 读取现有管理员数据
                admin_file = 'admin.json'
                admin_data = {}
                if os.path.exists(admin_file):
                    with open(admin_file, 'r', encoding='utf-8') as f:
                        admin_data = json.load(f)
                
                # 检查用户名是否已存在
                for admin_info in admin_data.values():
                    if admin_info.get('username') == username:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        response = {"success": False, "message": "管理员用户名已存在"}
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                        return
                
                # 创建新管理员
                import secrets
                import hashlib
                
                admin_id = secrets.token_hex(16)
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # 默认权限设置
                if not permissions:
                    if role == 'super_admin':
                        permissions = ['user_management', 'data_management', 'system_management', 'admin_management']
                    else:
                        permissions = ['user_management', 'data_management']
                
                admin_data[admin_id] = {
                    'username': username,
                    'password_hash': password_hash,
                    'email': email,
                    'role': role,
                    'created_at': datetime.now().isoformat(),
                    'last_login': None,
                    'is_active': True,
                    'permissions': permissions,
                    'created_by': token_info.get('username', 'system')
                }
                
                # 保存数据
                with open(admin_file, 'w', encoding='utf-8') as f:
                    json.dump(admin_data, f, ensure_ascii=False, indent=2)
                
                print(f"[管理员创建] 新管理员创建成功: {username} (角色: {role})")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {
                    "success": True,
                    "message": f"管理员 {username} 创建成功",
                    "admin_id": admin_id
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员创建] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"创建管理员失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_admin_delete(self, admin_id):
        """删除管理员"""
        try:
            # 检查权限：只有超级管理员才能管理其他管理员
            token_info, error = self.verify_admin_permission('admin_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 额外检查：确保是超级管理员
            current_role = token_info.get('role', '')
            if current_role != 'super_admin':
                self.send_response(403)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "只有超级管理员才能删除其他管理员"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 读取管理员数据
            admin_file = 'admin.json'
            if not os.path.exists(admin_file):
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "管理员不存在"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            with open(admin_file, 'r', encoding='utf-8') as f:
                admin_data = json.load(f)
            
            if admin_id not in admin_data:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "管理员不存在"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            admin_info = admin_data[admin_id]
            
            # 不能删除超级管理员
            if admin_info.get('role') == 'super_admin':
                self.send_response(403)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "不能删除超级管理员"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 不能删除自己
            current_admin_id = token_info.get('admin_id')
            if admin_id == current_admin_id:
                self.send_response(403)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "不能删除自己"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            username = admin_info.get('username')
            del admin_data[admin_id]
            
            # 保存数据
            with open(admin_file, 'w', encoding='utf-8') as f:
                json.dump(admin_data, f, ensure_ascii=False, indent=2)
            
            # 撤销该管理员的所有token
            self.revoke_admin_tokens(admin_id)
            
            print(f"[管理员删除] 管理员删除成功: {username}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": True, "message": f"管理员 {username} 删除成功"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员删除] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"删除管理员失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def ensure_default_admin(self):
        """确保存在默认管理员"""
        admin_file = 'admin.json'
        if not os.path.exists(admin_file):
            import hashlib
            import secrets
            
            default_admin_id = secrets.token_hex(16)
            default_admin = {
                default_admin_id: {
                    'username': 'admin',
                    'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
                    'email': 'admin@flappybird.com',
                    'role': 'super_admin',
                    'created_at': datetime.now().isoformat(),
                    'last_login': None,
                    'is_active': True,
                    'permissions': [
                        'user_management',
                        'system_management', 
                        'data_management',
                        'admin_management'
                    ]
                }
            }
            
            with open(admin_file, 'w', encoding='utf-8') as f:
                json.dump(default_admin, f, ensure_ascii=False, indent=2)
            
            print("[管理员] 默认管理员账户已创建 (用户名: admin, 密码: admin123)")

    def revoke_admin_tokens(self, admin_id):
        """撤销指定管理员的所有token"""
        try:
            admin_tokens_file = 'admin_tokens.json'
            if not os.path.exists(admin_tokens_file):
                return
            
            with open(admin_tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
            
            tokens_to_remove = []
            for token, token_info in tokens_data.items():
                if token_info.get('admin_id') == admin_id:
                    tokens_to_remove.append(token)
            
            for token in tokens_to_remove:
                del tokens_data[token]
            
            with open(admin_tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            print(f"[管理员] 已撤销管理员 {admin_id} 的 {len(tokens_to_remove)} 个token")
            
        except Exception as e:
            print(f"[管理员] 撤销token失败: {e}")

    def handle_admin_admin_update(self, admin_id):
        """更新管理员信息"""
        try:
            # 检查权限：只有超级管理员才能管理其他管理员
            token_info, error = self.verify_admin_permission('admin_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 额外检查：确保是超级管理员
            current_role = token_info.get('role', '')
            if current_role != 'super_admin':
                self.send_response(403)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "只有超级管理员才能管理其他管理员"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # 读取管理员数据
                admin_file = 'admin.json'
                if not os.path.exists(admin_file):
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "管理员不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                with open(admin_file, 'r', encoding='utf-8') as f:
                    admin_data = json.load(f)
                
                if admin_id not in admin_data:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = {"success": False, "message": "管理员不存在"}
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 更新管理员信息
                admin_info = admin_data[admin_id]
                
                # 可更新的字段
                if 'email' in data:
                    admin_info['email'] = data['email'].strip()
                if 'role' in data and data['role'] in ['admin', 'super_admin']:
                    admin_info['role'] = data['role']
                if 'is_active' in data:
                    admin_info['is_active'] = bool(data['is_active'] == 'true' if isinstance(data['is_active'], str) else data['is_active'])
                
                # 如果有新密码
                if 'password' in data and data['password'].strip():
                    import hashlib
                    admin_info['password_hash'] = hashlib.sha256(data['password'].encode()).hexdigest()
                
                # 根据角色设置权限
                if 'role' in data:
                    if data['role'] == 'super_admin':
                        admin_info['permissions'] = ['user_management', 'data_management', 'system_management', 'admin_management']
                    else:
                        admin_info['permissions'] = ['user_management', 'data_management']
                
                # 如果手动设置了权限，优先使用手动设置的
                if 'permissions' in data:
                    admin_info['permissions'] = data['permissions']
                
                # 保存数据
                with open(admin_file, 'w', encoding='utf-8') as f:
                    json.dump(admin_data, f, ensure_ascii=False, indent=2)
                
                print(f"[管理员更新] 管理员信息更新成功: {admin_info.get('username')}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": True, "message": "管理员信息更新成功"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[管理员更新] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"更新管理员失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def handle_admin_user_detail(self):
        """处理用户详情查询"""
        try:
            token_info, error = self.verify_admin_permission('user_management')
            if error:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": error}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 解析查询参数
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            user_id = query_params.get('user_id', [''])[0].strip()
            
            if not user_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "缺少用户ID"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 读取用户数据
            users_file = 'users.json'
            if not os.path.exists(users_file):
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "用户不存在"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            if user_id not in users_data:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                response = {"success": False, "message": "用户不存在"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            user_info = users_data[user_id]
            
            # 获取用户游戏历史
            history_file = 'game_history.json'
            user_history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                user_history = history_data.get(user_id, [])
                # 按时间降序排序，只取最近20条
                user_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                user_history = user_history[:20]
            
            # 清理敏感信息并添加额外统计
            safe_user_info = {
                "user_id": user_id,
                "username": user_info.get('username', ''),
                "phone": user_info.get('phone', ''),
                "email": user_info.get('email', ''),
                "created_at": user_info.get('created_at', ''),
                "last_login": user_info.get('last_login', ''),
                "best_score": user_info.get('best_score', 0),
                "total_score": user_info.get('total_score', 0),
                "games_played": user_info.get('games_played', 0),
                "is_active": user_info.get('is_active', True),
                "created_by": user_info.get('created_by', 'user'),
                "average_score": round(user_info.get('total_score', 0) / max(user_info.get('games_played', 1), 1), 1),
                "recent_games": user_history
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {
                "success": True,
                "user": safe_user_info
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"[用户详情] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            response = {"success": False, "message": f"获取用户详情失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

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