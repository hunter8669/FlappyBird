#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
局域网访问版服务器
允许同一网络下的其他设备访问
"""

import socket
from simple_server import run_server, GameAPIHandler
from http.server import HTTPServer

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 连接到一个远程地址来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run_public_server(port=8000):
    """启动可公网访问的服务器"""
    local_ip = get_local_ip()
    
    # 监听所有网络接口
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, GameAPIHandler)
    
    print("🌐" + "="*50)
    print(f"🚀 FlapPy Bird 公网服务器启动成功!")
    print("📍 访问地址:")
    print(f"   本机访问: http://localhost:{port}")
    print(f"   局域网访问: http://{local_ip}:{port}")
    print(f"   管理后台: http://{local_ip}:{port}/admin")
    print("="*52)
    print("📱 同一WiFi下的其他设备可以通过局域网地址访问")
    print("🔒 注意: 确保防火墙允许此端口访问")
    print("🛑 按 Ctrl+C 停止服务器...")
    print("="*52)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        httpd.server_close()

if __name__ == "__main__":
    run_public_server() 