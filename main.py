#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlapPy Bird Web版 - Replit启动文件
适配Replit环境的主程序入口
"""

import os
import sys

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def main():
    """主函数 - 启动Web服务器"""
    print("🐦 FlapPy Bird Web版正在启动...")
    print("🌐 适配Replit环境")
    print("=" * 50)
    
    try:
        # 导入并启动服务器
        from simple_server_fixed import run_server
        run_server()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖文件都在正确位置")
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 