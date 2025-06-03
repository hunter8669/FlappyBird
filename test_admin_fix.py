#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员系统修复验证脚本
测试所有核心功能是否正常工作
"""

import requests
import json
import sys

def test_admin_system():
    """测试管理员系统"""
    base_url = "http://localhost:8000"
    
    print("🔍 开始测试管理员系统修复情况...")
    print("=" * 50)
    
    # 测试1: 服务器健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器健康检查通过")
        else:
            print(f"❌ 服务器健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False
    
    # 测试2: 管理员登录
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/api/admin/login", 
                               json=login_data, timeout=5)
        if response.status_code == 200:
            login_result = response.json()
            if login_result.get('success'):
                token = login_result.get('token')
                print("✅ 管理员登录成功")
                print(f"   Token: {token[:20]}...")
            else:
                print(f"❌ 管理员登录失败: {login_result.get('message')}")
                return False
        else:
            print(f"❌ 管理员登录请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 管理员登录异常: {e}")
        return False
    
    # 测试3: 管理后台页面访问
    try:
        response = requests.get(f"{base_url}/admin", timeout=5)
        if response.status_code == 200:
            print("✅ 管理后台页面访问正常")
        else:
            print(f"❌ 管理后台页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 管理后台页面访问异常: {e}")
        return False
    
    # 测试4: 用户列表API
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/api/admin/users/list?page=1&page_size=5",
                              headers=headers, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('success'):
                user_count = user_data.get('data', {}).get('total', 0)
                print(f"✅ 用户列表API正常 (共{user_count}个用户)")
            else:
                print(f"❌ 用户列表API失败: {user_data.get('message')}")
                return False
        else:
            print(f"❌ 用户列表API请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 用户列表API异常: {e}")
        return False
    
    # 测试5: 用户统计API
    try:
        response = requests.get(f"{base_url}/api/admin/users/statistics",
                              headers=headers, timeout=5)
        if response.status_code == 200:
            stats_data = response.json()
            if stats_data.get('success'):
                stats = stats_data.get('statistics', {})
                total_users = stats.get('total_users', 0)
                active_users = stats.get('active_users', 0)
                print(f"✅ 用户统计API正常 (总用户: {total_users}, 活跃: {active_users})")
            else:
                print(f"❌ 用户统计API失败: {stats_data.get('message')}")
                return False
        else:
            print(f"❌ 用户统计API请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 用户统计API异常: {e}")
        return False
    
    print("=" * 50)
    print("🎉 所有测试通过！管理员系统修复成功！")
    print()
    print("📋 可用功能:")
    print("• 管理后台页面: http://localhost:8000/admin")
    print("• 管理员登录: http://localhost:8000/admin-login")
    print("• 默认账号: admin / admin123")
    print("• 用户管理: 查看、编辑、删除用户")
    print("• 数据统计: 用户趋势、活跃度分析")
    print("• 权限控制: 基于Token的安全认证")
    
    return True

if __name__ == "__main__":
    success = test_admin_system()
    sys.exit(0 if success else 1) 