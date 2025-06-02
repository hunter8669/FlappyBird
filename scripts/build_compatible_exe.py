#!/usr/bin/env python3
"""
兼容性增强的EXE构建脚本
解决Windows兼容性问题
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """安装构建依赖"""
    print("📦 安装构建依赖...")
    
    # 升级pip
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # 安装pygame和pyinstaller
    packages = [
        "pygame==2.5.2",
        "pyinstaller==6.3.0",
        "pillow",  # 图像处理
        "numpy"    # 数值计算
    ]
    
    for package in packages:
        print(f"安装 {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

def build_compatible_exe():
    """构建兼容性增强的EXE"""
    project_root = Path(__file__).parent.parent
    game_dir = project_root / "game-desktop"
    scripts_dir = project_root / "scripts"
    
    # 切换到游戏目录
    os.chdir(game_dir)
    
    print(f"🎯 当前目录: {os.getcwd()}")
    print(f"📁 项目根目录: {project_root}")
    print(f"🎮 游戏目录: {game_dir}")
    
    # 构建命令 - 增强兼容性
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # 单文件模式
        "--windowed",                   # 无控制台窗口
        "--noconfirm",                  # 不确认覆盖
        "--clean",                      # 清理临时文件
        "--add-data", f"{game_dir / 'assets'};assets",  # 包含资源文件
        "--icon", f"{game_dir / 'assets' / 'icon.ico'}",  # 图标
        # 兼容性增强选项
        "--runtime-tmpdir", ".",        # 运行时临时目录
        "--exclude-module", "tkinter",  # 排除不需要的模块
        "--exclude-module", "matplotlib",
        "--exclude-module", "scipy",
        # Windows兼容性
        "--target-arch", "x86_64",      # 64位架构
        "--strip",                      # 移除调试信息
        # 包含必要的运行时库
        "--collect-all", "pygame",
        # 输出选项
        "--distpath", str(scripts_dir),
        "--specpath", str(scripts_dir),
        "--workpath", str(scripts_dir / "build_temp"),
        "main.py"
    ]
    
    print("🔨 开始构建兼容EXE...")
    print("命令:", " ".join(build_cmd))
    
    try:
        result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
        print("✅ EXE构建成功!")
        print(result.stdout)
        
        # 检查生成的文件
        exe_path = scripts_dir / "main.exe"
        if exe_path.exists():
            # 重命名为FlapPyBird.exe
            final_exe = scripts_dir / "FlapPyBird_Compatible.exe"
            if final_exe.exists():
                final_exe.unlink()
            exe_path.rename(final_exe)
            
            size_mb = final_exe.stat().st_size / (1024 * 1024)
            print(f"🎉 兼容EXE创建成功!")
            print(f"📁 文件位置: {final_exe}")
            print(f"📊 文件大小: {size_mb:.1f} MB")
            
            return final_exe
        else:
            print("❌ 未找到生成的EXE文件")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print("错误输出:", e.stderr)
        return None

def create_compatibility_info():
    """创建兼容性说明"""
    info_text = """
🎮 FlapPy Bird 兼容性说明

如果遇到"此应用无法在你的电脑上运行"错误，请尝试：

方案1: 安装Visual C++运行时库
- 下载并安装 Microsoft Visual C++ Redistributable
- 链接: https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist

方案2: 右键点击EXE -> 属性 -> 兼容性
- 勾选"以兼容模式运行这个程序"
- 选择"Windows 8"或"Windows 7"

方案3: 临时关闭杀毒软件
- 某些杀毒软件可能误报
- 临时关闭后再次尝试运行

方案4: 以管理员身份运行
- 右键点击EXE -> "以管理员身份运行"

方案5: 源码运行（推荐）
- 确保安装了Python 3.8+
- 安装pygame: pip install pygame
- 运行: python game-desktop/main.py

如果以上方案都不行，请使用源码版本，这是最稳定的方式。
"""
    
    with open("scripts/兼容性说明.txt", "w", encoding="utf-8") as f:
        f.write(info_text)
    
    print("📄 兼容性说明已创建")

if __name__ == "__main__":
    print("🐦 FlapPy Bird 兼容EXE构建器")
    print("=" * 50)
    
    try:
        # 安装依赖
        install_requirements()
        
        # 构建兼容EXE
        exe_path = build_compatible_exe()
        
        # 创建说明文档
        create_compatibility_info()
        
        if exe_path:
            print(f"\n🎉 构建完成!")
            print(f"📁 兼容EXE: {exe_path.name}")
            print(f"📄 说明文档: scripts/兼容性说明.txt")
            print("\n如果仍有问题，建议使用源码版本运行。")
        
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        print("\n📌 推荐使用源码版本:")
        print("1. 安装Python 3.8+")
        print("2. pip install pygame")
        print("3. python game-desktop/main.py") 