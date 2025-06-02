#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlapPy Bird Web版 - Replit启动文件
专为Replit公网环境优化
"""

import os
import sys

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def main():
    """主函数 - 启动Web服务器"""
    print("🐦 FlapPy Bird Replit公网版正在启动...")
    print("🌐 配置公网访问环境")
    print("=" * 60)
    
    try:
        # 导入并启动服务器
        from simple_server_fixed import run_server
        print("✅ 服务器模块导入成功")
        run_server()
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("📦 尝试使用备用服务器...")
        try:
            from simple_server import run_server
            print("✅ 备用服务器模块导入成功")
            run_server()
        except ImportError as e2:
            print(f"❌ 备用服务器也失败: {e2}")
            print("🔧 请检查backend目录和server文件")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 