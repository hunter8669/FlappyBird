#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络管理模块
处理游戏与服务器的通信，包括用户登录、分数上传等
"""

import json
import time
import threading
from typing import Optional, Dict, Any
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("警告: requests模块未安装，网络功能将被禁用")
    requests = None

class NetworkManager:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.user_info = None
        self.is_online = False
        self.last_ping = 0
        
        # 创建会话，复用连接
        if requests:
            self.session = requests.Session()
            # 设置连接池参数
            retry_strategy = Retry(
                total=2,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(
                pool_connections=10,
                pool_maxsize=10
            )
            adapter.max_retries = retry_strategy
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        else:
            self.session = None
        
        # 检查服务器连接
        self.check_server_connection()
    
    def check_server_connection(self):
        """检查服务器连接状态"""
        if not requests or not self.session:
            self.is_online = False
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=3)
            self.is_online = response.status_code == 200
            return self.is_online
        except Exception as e:
            print(f"[网络] 服务器连接失败: {e}")
            self.is_online = False
            return False
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        if not self.is_online or not self.session:
            return {"success": False, "message": "网络不可用"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/users/login",
                json={"username": username, "password": password},
                timeout=5
            )
            
            data = response.json()
            if data.get("success"):
                self.token = data.get("token")
                self.user_info = data.get("user")
                print(f"[网络] 登录成功: {username}")
                return data
            else:
                print(f"[网络] 登录失败: {data.get('message')}")
                return data
                
        except Exception as e:
            print(f"[网络] 登录请求失败: {e}")
            return {"success": False, "message": f"网络错误: {str(e)}"}
    
    def register(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """用户注册"""
        if not self.is_online or not self.session:
            return {"success": False, "message": "网络不可用"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/users/register",
                json={"username": username, "password": password, "email": email},
                timeout=5
            )
            
            data = response.json()
            if data.get("success"):
                print(f"[网络] 注册成功: {username}")
            else:
                print(f"[网络] 注册失败: {data.get('message')}")
            return data
            
        except Exception as e:
            print(f"[网络] 注册请求失败: {e}")
            return {"success": False, "message": f"网络错误: {str(e)}"}
    
    def logout(self) -> bool:
        """用户登出"""
        if not self.is_online or not self.session or not self.token:
            self.token = None
            self.user_info = None
            return True
        
        try:
            self.session.post(
                f"{self.base_url}/api/users/logout",
                json={"token": self.token},
                timeout=3
            )
            self.token = None
            self.user_info = None
            print("[网络] 登出成功")
            return True
            
        except Exception as e:
            print(f"[网络] 登出请求失败: {e}")
            self.token = None
            self.user_info = None
            return False
    
    def upload_score(self, score: int, playtime: int, game_mode: str = "classic") -> bool:
        """上传游戏分数"""
        if not self.is_online or not self.session or not self.token:
            print("[网络] 无法上传分数: 未登录或网络不可用")
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/users/score",
                json={
                    "token": self.token,
                    "score": score,
                    "playtime": playtime,
                    "game_mode": game_mode
                },
                timeout=5
            )
            
            data = response.json()
            if data.get("success"):
                print(f"[网络] 分数上传成功: {score}分")
                # 更新本地用户信息
                if self.user_info:
                    self.user_info["total_score"] = self.user_info.get("total_score", 0) + score
                    self.user_info["games_played"] = self.user_info.get("games_played", 0) + 1
                    if score > self.user_info.get("best_score", 0):
                        self.user_info["best_score"] = score
                return True
            else:
                print(f"[网络] 分数上传失败: {data.get('message')}")
                return False
                
        except Exception as e:
            print(f"[网络] 分数上传请求失败: {e}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        return self.user_info
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.token is not None and self.user_info is not None
    
    def ping_server(self) -> bool:
        """ping服务器检查连接"""
        current_time = time.time()
        if current_time - self.last_ping < 60:  # 增加到60秒内不重复ping
            return self.is_online
        
        self.last_ping = current_time
        was_online = self.is_online
        
        # 使用更短的超时时间，避免阻塞
        try:
            if not self.session:
                self.is_online = False
                return False
                
            response = self.session.get(f"{self.base_url}/health", timeout=1)
            self.is_online = response.status_code == 200
        except Exception:
            # 静默处理连接失败，避免过多日志输出
            self.is_online = False
        
        if was_online != self.is_online:
            status = "在线" if self.is_online else "离线"
            print(f"[网络] 服务器状态变更: {status}")
        
        return self.is_online
    
    def get_leaderboard(self, limit: int = 10) -> Optional[Dict[str, Any]]:
        """获取排行榜数据"""
        if not self.is_online or not self.session:
            return {"success": False, "message": "网络不可用"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/scores/leaderboard?limit={limit}",
                timeout=5
            )
            
            data = response.json()
            if data.get("success"):
                print(f"[网络] 排行榜获取成功，包含{len(data.get('data', []))}条记录")
                return data
            else:
                print(f"[网络] 排行榜获取失败: {data.get('message')}")
                return data
                
        except Exception as e:
            print(f"[网络] 排行榜请求失败: {e}")
            return {"success": False, "message": f"网络错误: {str(e)}"} 