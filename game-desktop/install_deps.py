#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装游戏依赖脚本
"""

import subprocess
import sys

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {package} 安装失败")
        return False

def main():
    print("🎮 FlapPy Bird 依赖安装器")
    print("=" * 30)
    
    # 需要安装的依赖
    dependencies = [
        "pygame",
        "requests"
    ]
    
    print("正在安装依赖...")
    
    success_count = 0
    for dep in dependencies:
        print(f"\n安装 {dep}...")
        if install_package(dep):
            success_count += 1
    
    print("\n" + "=" * 30)
    if success_count == len(dependencies):
        print("🎉 所有依赖安装成功！")
        print("\n现在你可以运行游戏了:")
        print("python main.py")
    else:
        print(f"⚠️  {len(dependencies) - success_count} 个依赖安装失败")
        print("请手动安装失败的依赖")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main() 