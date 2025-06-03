#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员权限管理模块
提供管理员认证、权限控制和用户管理功能
"""

import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta

class AdminManager:
    def __init__(self):
        self.admin_file = 'admin.json'
        self.admin_tokens_file = 'admin_tokens.json'
        self.ensure_default_admin()
    
    def ensure_default_admin(self):
        """确保存在默认管理员账户"""
        if not os.path.exists(self.admin_file):
            # 创建默认管理员账户
            default_admin = {
                'admin': {
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
            
            with open(self.admin_file, 'w', encoding='utf-8') as f:
                json.dump(default_admin, f, ensure_ascii=False, indent=2)
            
            print("[管理员] 默认管理员账户已创建 (用户名: admin, 密码: admin123)")
    
    def authenticate_admin(self, username, password):
        """管理员认证"""
        try:
            if not os.path.exists(self.admin_file):
                return None
            
            with open(self.admin_file, 'r', encoding='utf-8') as f:
                admin_data = json.load(f)
            
            for admin_id, admin_info in admin_data.items():
                if admin_info.get('username') == username and admin_info.get('is_active', True):
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    if admin_info.get('password_hash') == password_hash:
                        # 更新最后登录时间
                        admin_info['last_login'] = datetime.now().isoformat()
                        admin_data[admin_id] = admin_info
                        
                        with open(self.admin_file, 'w', encoding='utf-8') as f:
                            json.dump(admin_data, f, ensure_ascii=False, indent=2)
                        
                        # 生成管理员token
                        token = self.generate_admin_token(admin_id, admin_info)
                        return {
                            'admin_id': admin_id,
                            'token': token,
                            'admin_info': {
                                'username': admin_info['username'],
                                'email': admin_info.get('email'),
                                'role': admin_info.get('role'),
                                'permissions': admin_info.get('permissions', [])
                            }
                        }
            
            return None
            
        except Exception as e:
            print(f"[管理员] 认证错误: {e}")
            return None
    
    def generate_admin_token(self, admin_id, admin_info):
        """生成管理员token"""
        try:
            token = f"admin_{secrets.token_hex(32)}"
            
            # 保存token
            tokens_data = {}
            if os.path.exists(self.admin_tokens_file):
                with open(self.admin_tokens_file, 'r', encoding='utf-8') as f:
                    tokens_data = json.load(f)
            
            tokens_data[token] = {
                'admin_id': admin_id,
                'username': admin_info['username'],
                'role': admin_info.get('role'),
                'permissions': admin_info.get('permissions', []),
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=8)).isoformat(),  # 8小时过期
                'last_used': datetime.now().isoformat()
            }
            
            # 清理过期token
            current_time = datetime.now()
            expired_tokens = []
            for token_key, token_info in tokens_data.items():
                try:
                    expires_at = datetime.fromisoformat(token_info['expires_at'])
                    if current_time > expires_at:
                        expired_tokens.append(token_key)
                except:
                    expired_tokens.append(token_key)
            
            for expired_token in expired_tokens:
                del tokens_data[expired_token]
            
            with open(self.admin_tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            return token
            
        except Exception as e:
            print(f"[管理员] Token生成错误: {e}")
            return None
    
    def verify_admin_token(self, token):
        """验证管理员token"""
        try:
            if not token or not token.startswith('admin_'):
                return None
            
            if not os.path.exists(self.admin_tokens_file):
                return None
            
            with open(self.admin_tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
            
            if token not in tokens_data:
                return None
            
            token_info = tokens_data[token]
            
            # 检查token是否过期
            expires_at = datetime.fromisoformat(token_info['expires_at'])
            if datetime.now() > expires_at:
                # 删除过期token
                del tokens_data[token]
                with open(self.admin_tokens_file, 'w', encoding='utf-8') as f:
                    json.dump(tokens_data, f, ensure_ascii=False, indent=2)
                return None
            
            # 更新最后使用时间
            token_info['last_used'] = datetime.now().isoformat()
            tokens_data[token] = token_info
            
            with open(self.admin_tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            return token_info
            
        except Exception as e:
            print(f"[管理员] Token验证错误: {e}")
            return None
    
    def has_permission(self, token, permission):
        """检查管理员权限"""
        token_info = self.verify_admin_token(token)
        if not token_info:
            return False
        
        permissions = token_info.get('permissions', [])
        return permission in permissions or 'super_admin' in permissions
    
    def revoke_admin_token(self, token):
        """撤销管理员token"""
        try:
            if not os.path.exists(self.admin_tokens_file):
                return True
            
            with open(self.admin_tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
            
            if token in tokens_data:
                del tokens_data[token]
                
                with open(self.admin_tokens_file, 'w', encoding='utf-8') as f:
                    json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"[管理员] Token撤销错误: {e}")
            return False
    
    def get_all_admins(self):
        """获取所有管理员信息"""
        try:
            if not os.path.exists(self.admin_file):
                return {}
            
            with open(self.admin_file, 'r', encoding='utf-8') as f:
                admin_data = json.load(f)
            
            # 移除敏感信息
            safe_admin_data = {}
            for admin_id, admin_info in admin_data.items():
                safe_admin_data[admin_id] = {
                    'username': admin_info.get('username'),
                    'email': admin_info.get('email'),
                    'role': admin_info.get('role'),
                    'created_at': admin_info.get('created_at'),
                    'last_login': admin_info.get('last_login'),
                    'is_active': admin_info.get('is_active', True),
                    'permissions': admin_info.get('permissions', [])
                }
            
            return safe_admin_data
            
        except Exception as e:
            print(f"[管理员] 获取管理员列表错误: {e}")
            return {}
    
    def create_admin(self, username, password, email, role='admin', permissions=None):
        """创建新管理员"""
        try:
            if permissions is None:
                permissions = ['user_management', 'data_management']
            
            admin_data = {}
            if os.path.exists(self.admin_file):
                with open(self.admin_file, 'r', encoding='utf-8') as f:
                    admin_data = json.load(f)
            
            # 检查用户名是否已存在
            for admin_info in admin_data.values():
                if admin_info.get('username') == username:
                    return False, "管理员用户名已存在"
            
            # 创建新管理员
            admin_id = secrets.token_hex(16)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            admin_data[admin_id] = {
                'username': username,
                'password_hash': password_hash,
                'email': email,
                'role': role,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True,
                'permissions': permissions
            }
            
            with open(self.admin_file, 'w', encoding='utf-8') as f:
                json.dump(admin_data, f, ensure_ascii=False, indent=2)
            
            return True, f"管理员 {username} 创建成功"
            
        except Exception as e:
            print(f"[管理员] 创建管理员错误: {e}")
            return False, f"创建失败: {str(e)}"
    
    def update_admin(self, admin_id, updates):
        """更新管理员信息"""
        try:
            if not os.path.exists(self.admin_file):
                return False, "管理员文件不存在"
            
            with open(self.admin_file, 'r', encoding='utf-8') as f:
                admin_data = json.load(f)
            
            if admin_id not in admin_data:
                return False, "管理员不存在"
            
            admin_info = admin_data[admin_id]
            
            # 更新允许的字段
            if 'email' in updates:
                admin_info['email'] = updates['email']
            if 'role' in updates:
                admin_info['role'] = updates['role']
            if 'permissions' in updates:
                admin_info['permissions'] = updates['permissions']
            if 'is_active' in updates:
                admin_info['is_active'] = updates['is_active']
            if 'password' in updates:
                admin_info['password_hash'] = hashlib.sha256(updates['password'].encode()).hexdigest()
            
            admin_info['updated_at'] = datetime.now().isoformat()
            admin_data[admin_id] = admin_info
            
            with open(self.admin_file, 'w', encoding='utf-8') as f:
                json.dump(admin_data, f, ensure_ascii=False, indent=2)
            
            return True, "管理员信息更新成功"
            
        except Exception as e:
            print(f"[管理员] 更新管理员错误: {e}")
            return False, f"更新失败: {str(e)}"
    
    def delete_admin(self, admin_id):
        """删除管理员"""
        try:
            if not os.path.exists(self.admin_file):
                return False, "管理员文件不存在"
            
            with open(self.admin_file, 'r', encoding='utf-8') as f:
                admin_data = json.load(f)
            
            if admin_id not in admin_data:
                return False, "管理员不存在"
            
            # 不能删除超级管理员
            if admin_data[admin_id].get('role') == 'super_admin':
                return False, "不能删除超级管理员"
            
            username = admin_data[admin_id].get('username')
            del admin_data[admin_id]
            
            with open(self.admin_file, 'w', encoding='utf-8') as f:
                json.dump(admin_data, f, ensure_ascii=False, indent=2)
            
            # 撤销该管理员的所有token
            if os.path.exists(self.admin_tokens_file):
                with open(self.admin_tokens_file, 'r', encoding='utf-8') as f:
                    tokens_data = json.load(f)
                
                tokens_to_remove = []
                for token, token_info in tokens_data.items():
                    if token_info.get('admin_id') == admin_id:
                        tokens_to_remove.append(token)
                
                for token in tokens_to_remove:
                    del tokens_data[token]
                
                with open(self.admin_tokens_file, 'w', encoding='utf-8') as f:
                    json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            return True, f"管理员 {username} 删除成功"
            
        except Exception as e:
            print(f"[管理员] 删除管理员错误: {e}")
            return False, f"删除失败: {str(e)}"

# 全局管理员管理器实例
admin_manager = AdminManager() 