#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用户脚本
"""

from user_manager import UserManager

def create_test_users():
    user_manager = UserManager()
    
    # 创建测试用户
    test_users = [
        {"username": "admin", "password": "admin123", "email": "admin@example.com"},
        {"username": "testuser", "password": "123456", "email": "test@example.com"},
        {"username": "gamer", "password": "password", "email": "gamer@example.com"}
    ]
    
    for user_data in test_users:
        result = user_manager.register_user(
            user_data["username"], 
            user_data["password"], 
            user_data["email"]
        )
        print(f"创建用户 {user_data['username']}: {result['message']}")
        
        # 为测试用户添加一些游戏数据
        if result["success"]:
            user_manager.update_user_score(user_data["username"], 50, 120)  # 50分，2分钟
            user_manager.update_user_score(user_data["username"], 75, 180)  # 75分，3分钟
            user_manager.update_user_score(user_data["username"], 120, 240) # 120分，4分钟

if __name__ == "__main__":
    create_test_users()
    print("测试用户创建完成！")
    print("可用测试账号：")
    print("1. admin / admin123")
    print("2. testuser / 123456") 
    print("3. gamer / password") 