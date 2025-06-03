#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块
提供完整的用户管理功能，包括增删改查、数据统计等
"""

import json
import os
import hashlib
from datetime import datetime, timedelta

class UserAdmin:
    def __init__(self):
        self.users_file = 'users.json'
        self.tokens_file = 'user_tokens.json'
        self.sms_file = 'sms_codes.json'
        self.stats_file = 'download_stats.json'
    
    def get_all_users(self, page=1, page_size=20, search=None, sort_by='created_at', order='desc'):
        """获取所有用户（分页、搜索、排序）"""
        try:
            if not os.path.exists(self.users_file):
                return {
                    'users': [],
                    'total': 0,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': 0
                }
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            # 转换为列表格式便于处理
            users_list = []
            for user_id, user_info in users_data.items():
                # 修复：确保只对字典类型的用户数据调用.copy()方法
                if isinstance(user_info, dict):
                    user_dict = user_info.copy()
                    user_dict['user_id'] = user_id
                    # 移除敏感信息
                    user_dict.pop('password_hash', None)
                    users_list.append(user_dict)
                else:
                    print(f"[警告] 用户数据格式错误: {user_id} = {type(user_info)}")
                    continue
            
            # 搜索过滤
            if search:
                search_lower = search.lower()
                filtered_users = []
                for user in users_list:
                    if (search_lower in user.get('username', '').lower() or
                        search_lower in user.get('phone', '') or
                        search_lower in user.get('email', '').lower()):
                        filtered_users.append(user)
                users_list = filtered_users
            
            # 排序
            reverse = (order == 'desc')
            if sort_by in ['created_at', 'last_login']:
                users_list.sort(key=lambda x: x.get(sort_by) or '', reverse=reverse)
            elif sort_by in ['best_score', 'total_score', 'games_played']:
                users_list.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
            else:
                users_list.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)
            
            # 分页
            total = len(users_list)
            total_pages = (total + page_size - 1) // page_size
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_users = users_list[start_idx:end_idx]
            
            return {
                'users': page_users,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages
            }
            
        except Exception as e:
            print(f"[用户管理] 获取用户列表错误: {e}")
            return {
                'users': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'total_pages': 0
            }
    
    def get_user_detail(self, user_id):
        """获取用户详细信息"""
        try:
            if not os.path.exists(self.users_file):
                return None
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            if user_id not in users_data:
                return None
            
            # 修复：确保用户数据是字典类型
            user_info = users_data[user_id]
            if not isinstance(user_info, dict):
                print(f"[警告] 用户数据格式错误: {user_id} = {type(user_info)}")
                return None
            
            user_info = user_info.copy()
            user_info['user_id'] = user_id
            user_info.pop('password_hash', None)  # 移除密码哈希
            
            # 获取用户的token信息
            user_info['active_tokens'] = 0
            if os.path.exists(self.tokens_file):
                with open(self.tokens_file, 'r', encoding='utf-8') as f:
                    tokens_data = json.load(f)
                
                current_time = datetime.now()
                for token_info in tokens_data.values():
                    if token_info.get('user_id') == user_id:
                        try:
                            expires_at = datetime.fromisoformat(token_info['expires_at'])
                            if current_time <= expires_at:
                                user_info['active_tokens'] += 1
                        except:
                            pass
            
            return user_info
            
        except Exception as e:
            print(f"[用户管理] 获取用户详情错误: {e}")
            return None
    
    def update_user(self, user_id, updates):
        """更新用户信息"""
        try:
            if not os.path.exists(self.users_file):
                return False, "用户文件不存在"
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            if user_id not in users_data:
                return False, "用户不存在"
            
            user_info = users_data[user_id]
            
            # 更新允许的字段
            allowed_fields = ['username', 'email', 'best_score', 'total_score', 'games_played', 'is_active']
            for field in allowed_fields:
                if field in updates:
                    if field == 'username':
                        # 检查用户名是否已被其他用户使用
                        for uid, uinfo in users_data.items():
                            if uid != user_id and uinfo.get('username') == updates[field]:
                                return False, "用户名已被使用"
                    user_info[field] = updates[field]
            
            # 如果更新了密码
            if 'password' in updates and updates['password']:
                user_info['password_hash'] = hashlib.sha256(updates['password'].encode()).hexdigest()
            
            user_info['updated_at'] = datetime.now().isoformat()
            users_data[user_id] = user_info
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            
            return True, "用户信息更新成功"
            
        except Exception as e:
            print(f"[用户管理] 更新用户错误: {e}")
            return False, f"更新失败: {str(e)}"
    
    def delete_user(self, user_id):
        """删除用户"""
        try:
            if not os.path.exists(self.users_file):
                return False, "用户文件不存在"
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            if user_id not in users_data:
                return False, "用户不存在"
            
            username = users_data[user_id].get('username')
            del users_data[user_id]
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            
            # 删除用户的所有token
            if os.path.exists(self.tokens_file):
                with open(self.tokens_file, 'r', encoding='utf-8') as f:
                    tokens_data = json.load(f)
                
                tokens_to_remove = []
                for token, token_info in tokens_data.items():
                    if token_info.get('user_id') == user_id:
                        tokens_to_remove.append(token)
                
                for token in tokens_to_remove:
                    del tokens_data[token]
                
                with open(self.tokens_file, 'w', encoding='utf-8') as f:
                    json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            return True, f"用户 {username} 删除成功"
            
        except Exception as e:
            print(f"[用户管理] 删除用户错误: {e}")
            return False, f"删除失败: {str(e)}"
    
    def create_user(self, username, phone, password, email=None):
        """创建新用户"""
        try:
            users_data = {}
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
            
            # 检查用户名和手机号是否已存在
            for user_info in users_data.values():
                if user_info.get('username') == username:
                    return False, "用户名已存在"
                if user_info.get('phone') == phone:
                    return False, "手机号已被注册"
            
            # 创建新用户
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
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            
            return True, f"用户 {username} 创建成功"
            
        except Exception as e:
            print(f"[用户管理] 创建用户错误: {e}")
            return False, f"创建失败: {str(e)}"
    
    def batch_delete_users(self, user_ids):
        """批量删除用户"""
        try:
            if not os.path.exists(self.users_file):
                return False, "用户文件不存在"
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            deleted_users = []
            not_found_users = []
            
            for user_id in user_ids:
                if user_id in users_data:
                    username = users_data[user_id].get('username')
                    del users_data[user_id]
                    deleted_users.append(username)
                else:
                    not_found_users.append(user_id)
            
            if deleted_users:
                with open(self.users_file, 'w', encoding='utf-8') as f:
                    json.dump(users_data, f, ensure_ascii=False, indent=2)
                
                # 删除这些用户的所有token
                if os.path.exists(self.tokens_file):
                    with open(self.tokens_file, 'r', encoding='utf-8') as f:
                        tokens_data = json.load(f)
                    
                    tokens_to_remove = []
                    for token, token_info in tokens_data.items():
                        if token_info.get('user_id') in user_ids:
                            tokens_to_remove.append(token)
                    
                    for token in tokens_to_remove:
                        del tokens_data[token]
                    
                    with open(self.tokens_file, 'w', encoding='utf-8') as f:
                        json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            message = f"成功删除 {len(deleted_users)} 个用户"
            if not_found_users:
                message += f"，{len(not_found_users)} 个用户不存在"
            
            return True, message
            
        except Exception as e:
            print(f"[用户管理] 批量删除用户错误: {e}")
            return False, f"批量删除失败: {str(e)}"
    
    def get_user_statistics(self):
        """获取用户统计信息"""
        try:
            stats = {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'users_today': 0,
                'users_this_week': 0,
                'users_this_month': 0,
                'top_players': [],
                'recent_registrations': [],
                'activity_chart': []
            }
            
            if not os.path.exists(self.users_file):
                return stats
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            current_time = datetime.now()
            today = current_time.date()
            week_ago = current_time - timedelta(days=7)
            month_ago = current_time - timedelta(days=30)
            
            all_users = []
            for user_id, user_info in users_data.items():
                # 修复：确保只对字典类型的用户数据调用.copy()方法
                if isinstance(user_info, dict):
                    user_dict = user_info.copy()
                    user_dict['user_id'] = user_id
                    user_dict.pop('password_hash', None)
                    all_users.append(user_dict)
                else:
                    print(f"[警告] 用户统计数据格式错误: {user_id} = {type(user_info)}")
                    continue
            
            stats['total_users'] = len(all_users)
            
            # 统计活跃状态
            for user in all_users:
                if user.get('is_active', True):
                    stats['active_users'] += 1
                else:
                    stats['inactive_users'] += 1
                
                # 统计注册时间
                try:
                    created_at = datetime.fromisoformat(user.get('created_at', ''))
                    if created_at.date() == today:
                        stats['users_today'] += 1
                    if created_at >= week_ago:
                        stats['users_this_week'] += 1
                    if created_at >= month_ago:
                        stats['users_this_month'] += 1
                except:
                    pass
            
            # 获取最高分玩家
            sorted_users = sorted(all_users, key=lambda x: x.get('best_score', 0), reverse=True)
            stats['top_players'] = sorted_users[:10]
            
            # 获取最近注册用户
            sorted_by_date = sorted(all_users, key=lambda x: x.get('created_at', ''), reverse=True)
            stats['recent_registrations'] = sorted_by_date[:10]
            
            # 生成活动图表数据（最近30天）
            activity_data = {}
            for i in range(30):
                date = (current_time - timedelta(days=i)).date()
                activity_data[date.isoformat()] = 0
            
            for user in all_users:
                try:
                    created_at = datetime.fromisoformat(user.get('created_at', ''))
                    date_str = created_at.date().isoformat()
                    if date_str in activity_data:
                        activity_data[date_str] += 1
                except:
                    pass
            
            stats['activity_chart'] = [{'date': k, 'count': v} for k, v in sorted(activity_data.items())]
            
            return stats
            
        except Exception as e:
            print(f"[用户管理] 获取统计信息错误: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'users_today': 0,
                'users_this_week': 0,
                'users_this_month': 0,
                'top_players': [],
                'recent_registrations': [],
                'activity_chart': []
            }
    
    def force_logout_user(self, user_id):
        """强制用户登出（删除所有token）"""
        try:
            if not os.path.exists(self.tokens_file):
                return True, "用户已登出"
            
            with open(self.tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
            
            tokens_to_remove = []
            for token, token_info in tokens_data.items():
                if token_info.get('user_id') == user_id:
                    tokens_to_remove.append(token)
            
            for token in tokens_to_remove:
                del tokens_data[token]
            
            with open(self.tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            return True, f"已强制登出用户，删除 {len(tokens_to_remove)} 个会话"
            
        except Exception as e:
            print(f"[用户管理] 强制登出错误: {e}")
            return False, f"强制登出失败: {str(e)}"
    
    def reset_user_password(self, user_id, new_password):
        """重置用户密码"""
        try:
            if not os.path.exists(self.users_file):
                return False, "用户文件不存在"
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            if user_id not in users_data:
                return False, "用户不存在"
            
            user_info = users_data[user_id]
            user_info['password_hash'] = hashlib.sha256(new_password.encode()).hexdigest()
            user_info['password_reset_at'] = datetime.now().isoformat()
            users_data[user_id] = user_info
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            
            # 同时强制用户登出
            self.force_logout_user(user_id)
            
            return True, f"用户密码重置成功，用户需要重新登录"
            
        except Exception as e:
            print(f"[用户管理] 重置密码错误: {e}")
            return False, f"重置密码失败: {str(e)}"
    
    def export_users_data(self, format='json'):
        """导出用户数据"""
        try:
            if not os.path.exists(self.users_file):
                return None, "用户文件不存在"
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            # 移除敏感信息
            export_data = {}
            for user_id, user_info in users_data.items():
                # 修复：确保只对字典类型的用户数据调用.copy()方法
                if isinstance(user_info, dict):
                    safe_info = user_info.copy()
                    safe_info.pop('password_hash', None)
                    safe_info['user_id'] = user_id
                    export_data[user_id] = safe_info
                else:
                    print(f"[警告] 导出数据格式错误: {user_id} = {type(user_info)}")
                    continue
            
            if format == 'json':
                return json.dumps(export_data, ensure_ascii=False, indent=2), "users_export.json"
            elif format == 'csv':
                # 转换为CSV格式
                import csv
                import io
                
                output = io.StringIO()
                if export_data:
                    fieldnames = list(next(iter(export_data.values())).keys())
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    for user_info in export_data.values():
                        writer.writerow(user_info)
                
                return output.getvalue(), "users_export.csv"
            
            return None, "不支持的导出格式"
            
        except Exception as e:
            print(f"[用户管理] 导出数据错误: {e}")
            return None, f"导出失败: {str(e)}"

# 全局用户管理器实例
user_admin = UserAdmin() 