#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块
处理用户注册、登录、数据管理等功能
"""

import json
import os
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class UserManager:
    def __init__(self, data_file="users.json"):
        self.data_file = data_file
        self.users = self.load_users()
        self.sessions = {}  # 存储用户会话
    
    def load_users(self) -> Dict:
        """加载用户数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[用户系统] 加载用户数据失败: {e}")
                return {"users": {}, "total_users": 0}
        else:
            return {"users": {}, "total_users": 0}
    
    def save_users(self):
        """保存用户数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[用户系统] 保存用户数据失败: {e}")
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self) -> str:
        """生成会话令牌"""
        return str(uuid.uuid4())
    
    def register_user(self, username: str, password: str, email: str) -> Dict:
        """用户注册"""
        # 检查用户名是否存在
        if username in self.users["users"]:
            return {"success": False, "message": "用户名已存在"}
        
        # 检查邮箱是否存在
        for user_data in self.users["users"].values():
            if user_data.get("email") == email:
                return {"success": False, "message": "邮箱已被注册"}
        
        # 创建用户
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "password": self.hash_password(password),
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "login_count": 0,
            "total_score": 0,
            "best_score": 0,
            "games_played": 0,
            "total_playtime": 0,  # 总游戏时间（秒）
            "achievements": [],
            "status": "active"
        }
        
        self.users["users"][username] = user_data
        self.users["total_users"] = len(self.users["users"])
        self.save_users()
        
        print(f"[用户系统] 新用户注册: {username}")
        return {"success": True, "message": "注册成功", "user_id": user_id}
    
    def login_user(self, username: str, password: str) -> Dict:
        """用户登录"""
        if username not in self.users["users"]:
            return {"success": False, "message": "用户名不存在"}
        
        user_data = self.users["users"][username]
        
        if user_data["password"] != self.hash_password(password):
            return {"success": False, "message": "密码错误"}
        
        if user_data["status"] != "active":
            return {"success": False, "message": "账号已被禁用"}
        
        # 更新登录信息
        user_data["last_login"] = datetime.now().isoformat()
        user_data["login_count"] += 1
        
        # 生成会话令牌
        token = self.generate_token()
        self.sessions[token] = {
            "username": username,
            "login_time": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24)
        }
        
        self.save_users()
        
        print(f"[用户系统] 用户登录: {username}")
        return {
            "success": True, 
            "message": "登录成功",
            "token": token,
            "user": {
                "username": username,
                "email": user_data["email"],
                "total_score": user_data["total_score"],
                "best_score": user_data["best_score"],
                "games_played": user_data["games_played"]
            }
        }
    
    def validate_session(self, token: str) -> Optional[str]:
        """验证会话令牌"""
        if token not in self.sessions:
            return None
        
        session = self.sessions[token]
        if datetime.now() > session["expires_at"]:
            del self.sessions[token]
            return None
        
        return session["username"]
    
    def logout_user(self, token: str) -> bool:
        """用户登出"""
        if token in self.sessions:
            username = self.sessions[token]["username"]
            del self.sessions[token]
            print(f"[用户系统] 用户登出: {username}")
            return True
        return False
    
    def update_user_score(self, username: str, score: int, playtime: int) -> bool:
        """更新用户游戏分数"""
        if username not in self.users["users"]:
            return False
        
        user_data = self.users["users"][username]
        user_data["total_score"] += score
        user_data["games_played"] += 1
        user_data["total_playtime"] += playtime
        
        if score > user_data["best_score"]:
            user_data["best_score"] = score
            # 添加成就
            if score >= 100 and "高分达人" not in user_data["achievements"]:
                user_data["achievements"].append("高分达人")
        
        # 其他成就检查
        if user_data["games_played"] >= 10 and "游戏新手" not in user_data["achievements"]:
            user_data["achievements"].append("游戏新手")
        
        if user_data["games_played"] >= 100 and "游戏专家" not in user_data["achievements"]:
            user_data["achievements"].append("游戏专家")
        
        self.save_users()
        return True
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        if username not in self.users["users"]:
            return None
        
        user_data = self.users["users"][username].copy()
        del user_data["password"]  # 不返回密码
        return user_data
    
    def get_all_users(self) -> List[Dict]:
        """获取所有用户信息（管理员功能）"""
        users = []
        for username, user_data in self.users["users"].items():
            user_info = user_data.copy()
            del user_info["password"]  # 不返回密码
            users.append(user_info)
        
        # 按注册时间排序
        users.sort(key=lambda x: x["created_at"], reverse=True)
        return users
    
    def get_user_stats(self) -> Dict:
        """获取用户统计信息"""
        total_users = len(self.users["users"])
        active_users = len([u for u in self.users["users"].values() if u["status"] == "active"])
        
        # 计算今日注册用户
        today = datetime.now().date().isoformat()
        today_registered = len([
            u for u in self.users["users"].values() 
            if u["created_at"].split("T")[0] == today
        ])
        
        # 计算今日活跃用户
        today_active = len([
            u for u in self.users["users"].values() 
            if u["last_login"] and u["last_login"].split("T")[0] == today
        ])
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "today_registered": today_registered,
            "today_active": today_active,
            "total_games_played": sum(u["games_played"] for u in self.users["users"].values()),
            "total_playtime": sum(u["total_playtime"] for u in self.users["users"].values())
        }
    
    def delete_user(self, username: str) -> bool:
        """删除用户（管理员功能）"""
        if username in self.users["users"]:
            del self.users["users"][username]
            self.users["total_users"] = len(self.users["users"])
            self.save_users()
            print(f"[用户系统] 删除用户: {username}")
            return True
        return False
    
    def ban_user(self, username: str) -> bool:
        """禁用用户（管理员功能）"""
        if username in self.users["users"]:
            self.users["users"][username]["status"] = "banned"
            self.save_users()
            print(f"[用户系统] 禁用用户: {username}")
            return True
        return False
    
    def unban_user(self, username: str) -> bool:
        """解禁用户（管理员功能）"""
        if username in self.users["users"]:
            self.users["users"][username]["status"] = "active"
            self.save_users()
            print(f"[用户系统] 解禁用户: {username}")
            return True
        return False 