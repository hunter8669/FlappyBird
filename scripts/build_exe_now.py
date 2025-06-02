#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlapPy Bird EXE构建器
自动构建可执行文件
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"🔧 执行: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("✅ 成功")
            return True, result.stdout
        else:
            print(f"❌ 失败: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False, str(e)

def install_dependencies():
    """安装构建依赖"""
    print("📦 安装构建依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 安装PyInstaller
    success, output = run_command("pip install pyinstaller")
    if not success:
        print("❌ PyInstaller安装失败")
        return False
    
    # 安装pygame
    success, output = run_command("pip install pygame")
    if not success:
        print("❌ pygame安装失败")
        return False
    
    print("✅ 依赖安装完成")
    return True

def build_exe():
    """构建EXE文件"""
    print("🏗️ 开始构建EXE...")
    
    # 确定项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    game_dir = project_root / "game-desktop"
    main_py = game_dir / "main.py"
    
    print(f"📁 项目目录: {project_root}")
    print(f"🎮 游戏目录: {game_dir}")
    print(f"📄 主文件: {main_py}")
    
    if not main_py.exists():
        print(f"❌ 找不到主文件: {main_py}")
        return False
    
    # 创建构建目录
    build_dir = script_dir / "build_temp"
    build_dir.mkdir(exist_ok=True)
    
    # 复制游戏文件到构建目录
    print("📋 复制游戏文件...")
    dest_game_dir = build_dir / "game-desktop"
    if dest_game_dir.exists():
        shutil.rmtree(dest_game_dir)
    shutil.copytree(game_dir, dest_game_dir)
    
    # 创建PyInstaller规格文件
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[r'{dest_game_dir.absolute()}'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'pygame',
        'asyncio',
        'json',
        'requests',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FlapPyBird',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    spec_file = dest_game_dir / "FlapPyBird.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("📝 PyInstaller规格文件已创建")
    
    # 执行PyInstaller构建
    print("🔨 执行PyInstaller构建...")
    cmd = f"pyinstaller --clean --noconfirm FlapPyBird.spec"
    success, output = run_command(cmd, cwd=dest_game_dir)
    
    if not success:
        print("❌ PyInstaller构建失败")
        print(f"输出: {output}")
        return False
    
    # 检查生成的EXE文件
    exe_file = dest_game_dir / "dist" / "FlapPyBird.exe"
    if not exe_file.exists():
        print("❌ EXE文件未生成")
        return False
    
    # 移动EXE到scripts目录
    final_exe = script_dir / "FlapPyBird.exe"
    shutil.copy2(exe_file, final_exe)
    
    print(f"✅ EXE构建完成: {final_exe}")
    print(f"📏 文件大小: {final_exe.stat().st_size / 1024 / 1024:.1f} MB")
    
    # 清理构建目录
    print("🧹 清理临时文件...")
    shutil.rmtree(build_dir)
    
    return True

def create_launcher_script():
    """创建启动脚本"""
    script_dir = Path(__file__).parent
    launcher_content = '''@echo off
title FlapPy Bird - 增强版游戏
echo ==========================================
echo        FlapPy Bird 增强版
echo ==========================================
echo.
echo 正在启动游戏...
echo.

cd /d "%~dp0"
if exist "FlapPyBird.exe" (
    start "" "FlapPyBird.exe"
    echo 游戏已启动！
) else (
    echo 错误：找不到 FlapPyBird.exe
    echo 请确保文件完整
    pause
)
'''
    
    launcher_file = script_dir / "启动游戏.bat"
    with open(launcher_file, 'w', encoding='gbk') as f:
        f.write(launcher_content)
    
    print(f"✅ 启动脚本已创建: {launcher_file}")

def main():
    """主函数"""
    print("🐦 FlapPy Bird EXE构建器")
    print("=" * 50)
    
    # 检查环境
    print("🔍 检查构建环境...")
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        return False
    
    # 构建EXE
    if not build_exe():
        print("❌ EXE构建失败")
        return False
    
    # 创建启动脚本
    create_launcher_script()
    
    print("🎉 构建完成！")
    print("\n📦 生成文件:")
    script_dir = Path(__file__).parent
    exe_file = script_dir / "FlapPyBird.exe"
    launcher_file = script_dir / "启动游戏.bat"
    
    if exe_file.exists():
        print(f"   🎮 FlapPyBird.exe ({exe_file.stat().st_size / 1024 / 1024:.1f} MB)")
    if launcher_file.exists():
        print(f"   🚀 启动游戏.bat")
    
    print("\n🎯 使用说明:")
    print("   1. 双击 'FlapPyBird.exe' 直接运行")
    print("   2. 或双击 '启动游戏.bat' 启动")
    print("   3. 游戏支持多种模式和在线功能")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 构建成功完成！")
        else:
            print("\n❌ 构建失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 用户取消构建")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 构建异常: {e}")
        sys.exit(1) 