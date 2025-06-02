#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云部署版服务器
适配 Railway, Render, Heroku 等云平台
"""

import os
from simple_server_fixed import GameAPIHandler
from http.server import HTTPServer

def run_cloud_server():
    """启动云部署服务器"""
    # 从环境变量获取端口，云平台会自动分配
    port = int(os.environ.get('PORT', 8000))
    
    # 检测Replit环境并显示正确信息
    if os.environ.get('REPL_ID'):  # Replit环境
        repl_slug = os.environ.get('REPL_SLUG', 'flappybird')
        repl_owner = os.environ.get('REPL_OWNER', 'user')
        server_url = f"https://{repl_slug}.{repl_owner}.repl.co"
        print("🌐" + "="*50)
        print(f"🚀 FlapPy Bird Replit公网服务器启动!")
        print(f"📍 公网地址: {server_url}")
        print(f"🎮 直接游戏: {server_url} (自动跳转)")
        print(f"🎯 游戏页面: {server_url}/game.html")
        print(f"❤️  状态检查: {server_url}/health")
        print("="*52)
    else:
        print("☁️" + "="*50)
        print(f"🚀 FlapPy Bird 云服务器启动成功!")
        print(f"📍 监听端口: {port}")
        print(f"🌐 等待云平台分配域名...")
        print("="*52)
        print("📱 全世界都可以访问您的游戏了！")
        print("🎮 部署完成后获得公网访问地址")
        print("="*52)
    
    # 监听所有网络接口（云部署必需）
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, GameAPIHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        httpd.server_close()

if __name__ == "__main__":
    run_cloud_server() 