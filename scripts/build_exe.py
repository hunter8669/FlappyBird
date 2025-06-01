#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlapPy Bird EXE构建脚本
使用PyInstaller将游戏打包成独立可执行文件
"""

import os
import sys
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

def check_dependencies():
    """检查必要的依赖"""
    print("[检查] 检查构建依赖...")
    
    try:
        import PyInstaller
        print("[成功] PyInstaller 已安装")
    except ImportError:
        print("[错误] PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("[成功] PyInstaller 安装完成")
    
    try:
        import pygame
        print("[成功] Pygame 已安装")
    except ImportError:
        print("[错误] Pygame 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pygame"], check=True)
        print("[成功] Pygame 安装完成")

def create_build_spec():
    """创建PyInstaller构建配置文件"""
    print("[配置] 创建构建配置...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../game-desktop/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../game-desktop/src', 'src'),
        ('../assets', 'assets'),
        ('../data', 'data'),
    ],
    hiddenimports=[
        'pygame',
        'pygame.locals',
        'pygame.mixer',
        'pygame.font',
        'pygame.image',
        'pygame.transform',
        'pygame.sprite',
        'pygame.rect',
        'pygame.surface',
        'pygame.display',
        'pygame.event',
        'pygame.key',
        'pygame.time',
        'pygame.math',
    ],
    hookspath=[],
    hooksconfig={},
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
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../flappy.ico',  # 使用项目图标
)
'''
    
    with open('FlapPyBird.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("[成功] 构建配置已创建")

def build_exe():
    """构建EXE文件"""
    print("[构建] 开始构建EXE文件...")
    
    # 运行PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm", 
        "FlapPyBird.spec"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[成功] EXE文件构建成功！")
        return True
    else:
        print("[错误] EXE文件构建失败:")
        print(result.stdout)
        print(result.stderr)
        return False

def create_installer_package():
    """创建完整的安装包"""
    print("[打包] 创建安装包...")
    
    dist_dir = Path("dist")
    exe_file = dist_dir / "FlapPyBird.exe"
    
    if not exe_file.exists():
        print("[错误] EXE文件不存在，无法创建安装包")
        return False
    
    # 创建安装包目录
    package_dir = Path("FlapPyBird-v1.2.0")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # 复制EXE文件
    shutil.copy2(exe_file, package_dir / "FlapPyBird.exe")
    
    # 创建启动脚本（备用）
    startup_script = '''@echo off
title FlapPy Bird - 增强版
echo ==========================================
echo        FlapPy Bird 增强版
echo ==========================================
echo 正在启动游戏...
echo.

start "" "FlapPyBird.exe"

REM 如果EXE无法运行，显示帮助信息
timeout /t 2 >nul
tasklist /fi "imagename eq FlapPyBird.exe" | find "FlapPyBird.exe" >nul
if %errorlevel% neq 0 (
    echo.
    echo [警告] 游戏可能无法正常启动
    echo.
    echo 解决方案：
    echo 1. 右键"FlapPyBird.exe" → 以管理员身份运行
    echo 2. 确保Windows版本为Windows 7或更高
    echo 3. 如仍有问题，请联系开发者
    echo.
    pause
)
'''
    
    with open(package_dir / "启动游戏.bat", 'w', encoding='gbk') as f:
        f.write(startup_script)
    
    # 创建使用说明
    readme_content = '''FlapPy Bird 增强版 - 独立版本
==================================

[游戏] 游戏说明：
这是经典FlappyBird的增强版本，包含四种游戏模式：
- 经典模式：原版体验
- 限时挑战：90秒挑战
- 反向模式：重力反转
- Boss战斗：武器对战

[安装] 安装说明：
1. 双击"FlapPyBird.exe"直接开始游戏
2. 或者双击"启动游戏.bat"运行
3. 首次运行可能需要Windows安全确认

[控制] 游戏控制：
- 空格键/上箭头：飞行/射击
- Q/E键：切换武器（Boss模式）
- 数字键1-4：选择武器（Boss模式）

[系统] 系统要求：
- Windows 7/8/10/11 (64位)
- 至少100MB磁盘空间
- 建议分辨率：1024x768或更高

[问答] 常见问题：
1. 如果提示"Windows已保护你的电脑"：
   点击"更多信息" → "仍要运行"

2. 如果游戏无法启动：
   - 右键"FlapPyBird.exe" → "以管理员身份运行"
   - 确保已安装最新的Windows更新

3. 如果提示缺少DLL文件：
   - 安装Microsoft Visual C++ Redistributable

[信息] 项目信息：
版本：v1.2.0
更新时间：''' + str(Path.cwd().parent) + '''
开源地址：https://github.com/yourusername/FlapPyBird

享受游戏吧！
'''
    
    with open(package_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # 复制图标文件（如果存在）
    icon_file = Path("../flappy.ico")
    if icon_file.exists():
        shutil.copy2(icon_file, package_dir / "game.ico")
    
    # 创建ZIP压缩包
    zip_filename = f"FlapPyBird-v1.2.0-Windows-x64.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
    
    # 获取文件大小
    zip_size = Path(zip_filename).stat().st_size
    exe_size = exe_file.stat().st_size
    
    print(f"[成功] 安装包创建完成:")
    print(f"   [文件夹] 文件夹: {package_dir}")
    print(f"   [压缩包] 压缩包: {zip_filename} ({zip_size/1024/1024:.1f} MB)")
    print(f"   [大小] EXE大小: {exe_size/1024/1024:.1f} MB")
    
    return True

def main():
    """主构建流程"""
    print("[启动] FlapPy Bird EXE构建器")
    print("=" * 50)
    
    # 切换到脚本目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        # 1. 检查依赖
        check_dependencies()
        
        # 2. 创建构建配置
        create_build_spec()
        
        # 3. 构建EXE
        if not build_exe():
            return False
        
        # 4. 创建安装包
        if not create_installer_package():
            return False
        
        print("\n[完成] 构建完成！")
        print("现在您可以将生成的ZIP文件提供给用户下载")
        print("用户只需解压并双击EXE文件即可游戏")
        
        return True
        
    except Exception as e:
        print(f"[错误] 构建过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 