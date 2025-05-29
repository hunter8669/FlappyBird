import asyncio
import os
import sys

# 确保使用UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the current directory to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.flappy import Flappy

async def main():
    """Web版游戏主函数"""
    game = Flappy()
    await game.start()

if __name__ == "__main__":
    # 对于Web版，使用异步循环
    asyncio.run(main()) 