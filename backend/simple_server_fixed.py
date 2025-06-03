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
                    'phone': phone,
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