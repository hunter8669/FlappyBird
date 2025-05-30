#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云部署版服务器
适配 Railway, Render, Heroku 等云平台
"""

import os
from simple_server import GameAPIHandler
from http.server import HTTPServer

def run_cloud_server():
    """启动云部署服务器"""
    # 从环境变量获取端口，云平台会自动分配
    port = int(os.environ.get('PORT', 8000))
    
    # 监听所有网络接口（云部署必需）
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, GameAPIHandler)
    
    print("☁️" + "="*50)
    print(f"🚀 FlapPy Bird 云服务器启动成功!")
    print(f"📍 监听端口: {port}")
    print(f"🌐 等待云平台分配域名...")
    print("="*52)
    print("📱 全世界都可以访问您的游戏了！")
    print("🎮 部署完成后获得公网访问地址")
    print("="*52)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        httpd.server_close()

if __name__ == "__main__":
    run_cloud_server() 