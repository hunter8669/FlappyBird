#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动启动服务器和游戏的脚本
"""

import os
import sys
import time
import subprocess
import threading
import requests
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import pygame
        import requests
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "install_deps.py"])
            return True
        except:
            print("❌ 依赖安装失败，请手动运行: python install_deps.py")
            return False

def check_server_running():
    """检查服务器是否运行"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_server():
    """启动服务器"""
    backend_dir = Path(__file__).parent.parent / "backend"
    server_script = backend_dir / "simple_server.py"
    
    if not server_script.exists():
        print(f"❌ 服务器脚本不存在: {server_script}")
        return None
    
    print("🚀 启动服务器...")
    try:
        # 在新进程中启动服务器
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待服务器启动
        for i in range(20):  # 最多等待20秒
            time.sleep(1)
            if check_server_running():
                print("✅ 服务器启动成功!")
                return process
            print(f"⏳ 等待服务器启动... ({i+1}/20)")
        
        print("❌ 服务器启动超时")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        return None

def start_game():
    """启动游戏"""
    print("🎮 启动游戏...")
    try:
        # 导入并运行游戏
        import asyncio
        from src.flappy import Flappy
        
        game = Flappy()
        asyncio.run(game.start())
        
    except Exception as e:
        print(f"❌ 游戏启动失败: {e}")
        input("按回车键退出...")

def main():
    print("🐦 FlapPy Bird 增强版启动器")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        return
    
    # 检查服务器状态
    server_process = None
    if check_server_running():
        print("✅ 服务器已运行")
    else:
        print("📡 服务器未运行，正在启动...")
        server_process = start_server()
        if not server_process:
            print("⚠️  服务器启动失败，游戏将以离线模式运行")
            time.sleep(2)
    
    print("\n🎮 游戏功能:")
    print("- 在线模式: 登录注册、分数上传、排行榜")
    print("- 离线模式: 本地游戏体验")
    print("- 游戏内按 U 键打开用户界面")
    print("\n正在启动游戏...")
    time.sleep(2)
    
    try:
        # 启动游戏
        start_game()
    finally:
        # 游戏结束后清理服务器进程
        if server_process:
            print("\n🛑 关闭服务器...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except:
                server_process.kill()
            print("✅ 服务器已关闭")

if __name__ == "__main__":
    main() 