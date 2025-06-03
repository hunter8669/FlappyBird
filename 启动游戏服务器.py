#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlapPy Bird 游戏服务器启动脚本
支持Windows/Linux/macOS
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("\n" + "="*50)
    print("          🐦 FlapPy Bird 游戏服务器")
    print("="*50)
    print()

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查是否在正确的目录
    backend_path = Path("backend/simple_server_fixed.py")
    if not backend_path.exists():
        print("❌ 错误：找不到服务器文件！")
        print("请确保脚本在项目根目录下运行")
        return False
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("❌ 错误：需要Python 3.6或更高版本")
        print(f"当前版本：Python {sys.version}")
        return False
    
    print(f"✅ Python环境检查通过：{sys.version.split()[0]}")
    return True

def start_server():
    """启动服务器"""
    print("\n🚀 启动游戏服务器...")
    print("⚠️  按 Ctrl+C 可停止服务器")
    print()
    
    try:
        # 切换到backend目录
        os.chdir("backend")
        print("📁 已切换到backend目录")
        
        # 启动服务器
        print("🎮 服务器启动中...")
        subprocess.run([sys.executable, "simple_server_fixed.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  用户手动停止服务器")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 服务器启动失败：{e}")
    except Exception as e:
        print(f"\n❌ 未知错误：{e}")
    finally:
        print("\n⚠️  服务器已停止")

def main():
    """主函数"""
    print_banner()
    
    if not check_environment():
        input("\n按回车键退出...")
        sys.exit(1)
    
    try:
        start_server()
    except Exception as e:
        print(f"启动过程中发生错误：{e}")
    finally:
        input("\n按回车键退出...")

if __name__ == "__main__":
    main() 