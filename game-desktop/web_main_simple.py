import asyncio
import os
import sys

# 确保使用UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the current directory to the path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

from src.entities import (
    Background,
    Floor,
    GameOver,
    Pipes,
    Player,
    PlayerMode,
    Score,
    WelcomeMessage,
)
from src.entities.powerup import PowerUpManager, PowerUpType, PowerUp
from src.entities.boss import Boss, BossType
from src.entities.bullet import Bullet
from src.entities.weapon import WeaponType
from src.entities.coin import CoinManager
from src.utils import GameConfig, Images, Sounds, Window, get_font
from enum import Enum


class GameMode(Enum):
    """游戏模式枚举"""
    CLASSIC = "经典模式"    # 经典无限模式
    TIMED = "限时挑战"      # 限时挑战模式
    REVERSE = "重力反转"    # 重力反转模式
    BOSS = "Boss战斗"     # BOSS战模式
    COIN = "金币收集"     # 金币收集模式


class FlappyWeb:
    def __init__(self):
        """
        初始化Flappy Bird Web版游戏
        """
        pygame.init()  # 初始化pygame
        pygame.display.set_caption("FlapPy Bird - Complete Web Edition")  # 设置窗口标题
        window = Window(800, 600)  # Web版使用更大的窗口
        screen = pygame.display.set_mode((window.width, window.height))  # 设置屏幕大小
        images = Images()  # 加载图像资源

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
        )
        # 设置调试模式为False，关闭调试信息显示
        self.config.debug = False
        # 记录上一帧的时间，用于计算delta_time
        self.last_frame_time = pygame.time.get_ticks()
        
        # 游戏模式相关
        self.game_mode = GameMode.CLASSIC  # 默认为经典模式
        self.time_limit = 60 * 1000  # 限时模式的时间限制（毫秒）
        self.time_remaining = self.time_limit  # 剩余时间
        
        # Boss相关
        self.boss = None
        self.boss_level = 0
        self.boss_cycle = 0  # 初始化Boss循环次数
        
        # 初始化道具管理器
        self.powerup_manager = PowerUpManager(self.config)
        
        # 初始化金币管理器
        self.coin_manager = CoinManager(self.config)
        
        # 初始化金币收集计数
        self.collected_coins = 0
        
        # 游戏状态 - Web版简化，直接进入游戏
        self.game_start_time = None
        self.total_playtime = 0

    async def start(self):
        """
        启动游戏循环 - Web版简化流程
        """
        while True:
            self.background = Background(self.config)  # 创建背景对象
            self.floor = Floor(self.config)  # 创建地面对象
            self.player = Player(self.config)  # 创建玩家对象
            self.welcome_message = WelcomeMessage(self.config)  # 创建欢迎信息对象
            self.game_over_message = GameOver(self.config)  # 创建游戏结束信息对象
            self.pipes = Pipes(self.config)  # 创建管道对象
            self.score = Score(self.config)  # 创建得分对象
            
            # Web版直接进入游戏模式选择
            await self.game_mode_selection()
            
            # 开始游戏
            await self.play()
            await self.game_over()

    async def game_mode_selection(self):
        """
        游戏模式选择界面 - Web优化版
        """
        self.player.set_mode(PlayerMode.SHM)  # 设置玩家模式为SHM（静止模式）
        
        # 初始化字体
        title_font = get_font('Arial', 36)  # 使用Web友好字体
        button_font = get_font('Arial', 20)
        desc_font = get_font('Arial', 14)
        
        # 计算布局
        window_center_x = self.config.window.width // 2
        window_center_y = self.config.window.height // 2
        
        # 按钮尺寸和位置
        button_width = 150
        button_height = 50
        button_spacing = 20
        
        # 创建5个游戏模式按钮
        modes = [
            ("经典模式", GameMode.CLASSIC, (34, 139, 34)),
            ("限时挑战", GameMode.TIMED, (255, 165, 0)),
            ("重力反转", GameMode.REVERSE, (138, 43, 226)),
            ("Boss战斗", GameMode.BOSS, (220, 20, 60)),
            ("金币收集", GameMode.COIN, (255, 215, 0)),
        ]
        
        # 计算按钮位置（2行3列）
        buttons = []
        for i, (name, mode, color) in enumerate(modes):
            row = i // 3
            col = i % 3
            x = window_center_x - (3 * button_width + 2 * button_spacing) // 2 + col * (button_width + button_spacing)
            y = window_center_y - 50 + row * (button_height + button_spacing)
            rect = pygame.Rect(x, y, button_width, button_height)
            buttons.append((rect, name, mode, color))
        
        selected_mode = GameMode.CLASSIC
        button_hover = [False] * len(buttons)
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                
                # 鼠标事件处理
                if event.type == pygame.MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                    for i, (rect, _, _, _) in enumerate(buttons):
                        button_hover[i] = rect.collidepoint(mouse_x, mouse_y)
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    for rect, name, mode, color in buttons:
                        if rect.collidepoint(mouse_x, mouse_y):
                            self.game_mode = mode
                            return  # 选择完成，返回开始游戏
            
            # 渲染背景
            self.background.draw()
            self.floor.draw()
            
            # 渲染标题
            title_text = title_font.render("🎮 选择游戏模式", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(window_center_x, window_center_y - 150))
            self.config.screen.blit(title_text, title_rect)
            
            # 渲染按钮
            for i, (rect, name, mode, color) in enumerate(buttons):
                # 按钮背景
                btn_color = tuple(min(255, c + 50) for c in color) if button_hover[i] else color
                pygame.draw.rect(self.config.screen, btn_color, rect)
                pygame.draw.rect(self.config.screen, (255, 255, 255), rect, 2)
                
                # 按钮文字
                text = button_font.render(name, True, (255, 255, 255))
                text_rect = text.get_rect(center=rect.center)
                self.config.screen.blit(text, text_rect)
            
            # 游戏模式说明
            mode_descriptions = {
                GameMode.CLASSIC: "经典无限模式，躲避管道获得高分",
                GameMode.TIMED: "在60秒内获得尽可能高的分数",
                GameMode.REVERSE: "重力反转，控制方式相反",
                GameMode.BOSS: "挑战Boss，使用武器系统战斗",
                GameMode.COIN: "收集金币，解锁新的游戏内容"
            }
            
            # 显示当前选中模式的说明
            for i, (rect, name, mode, color) in enumerate(buttons):
                if button_hover[i]:
                    desc_text = desc_font.render(mode_descriptions[mode], True, (200, 200, 200))
                    desc_rect = desc_text.get_rect(center=(window_center_x, window_center_y + 120))
                    self.config.screen.blit(desc_text, desc_rect)
                    break
            
            pygame.display.update()
            await asyncio.sleep(0)  # 让出控制权给事件循环

    async def play(self):
        """
        游戏主循环 - 简化版
        """
        self.player.set_mode(PlayerMode.NORMAL)
        
        # 根据游戏模式初始化
        if self.game_mode == GameMode.BOSS:
            self.create_boss()
        elif self.game_mode == GameMode.COIN:
            self.coin_manager.start_spawning()
        
        clock = pygame.time.Clock()
        
        while True:
            # 处理事件
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        if self.game_mode == GameMode.REVERSE:
                            self.player.flap_reverse()
                        else:
                            self.player.flap()
                    elif event.key == K_ESCAPE:
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_mode == GameMode.REVERSE:
                        self.player.flap_reverse()
                    else:
                        self.player.flap()
            
            # 更新游戏逻辑
            self.player.update()
            
            # 根据游戏模式更新
            if self.game_mode != GameMode.BOSS:
                self.pipes.update()
                # 检查管道碰撞
                if self.pipes.collides_with(self.player):
                    return  # 游戏结束
                # 检查分数
                if self.pipes.passes(self.player):
                    self.score.add()
            
            if self.game_mode == GameMode.BOSS and self.boss:
                self.update_boss()
                
            if self.game_mode == GameMode.COIN:
                self.coin_manager.update()
                self.check_coin_collection()
            
            if self.game_mode == GameMode.TIMED:
                self.time_remaining -= clock.get_time()
                if self.time_remaining <= 0:
                    return  # 时间到，游戏结束
            
            # 检查边界碰撞
            if self.player.check_bounds():
                return  # 游戏结束
            
            # 渲染
            self.background.draw()
            if self.game_mode != GameMode.BOSS:
                self.pipes.draw()
            self.floor.draw()
            self.player.draw()
            
            if self.game_mode == GameMode.BOSS and self.boss:
                self.draw_boss()
                
            if self.game_mode == GameMode.COIN:
                self.coin_manager.draw()
            
            self.score.draw()
            
            # 显示模式信息
            self.draw_mode_info()
            
            pygame.display.update()
            clock.tick(30)
            await asyncio.sleep(0)  # 让出控制权给事件循环

    def create_boss(self):
        """创建Boss"""
        self.boss = Boss(self.config, BossType.NORMAL)

    def update_boss(self):
        """更新Boss逻辑"""
        if self.boss:
            self.boss.update()
            # 简化的Boss战斗逻辑
            if self.boss.check_collision(self.player):
                # 玩家碰撞Boss，游戏结束或减血
                pass

    def draw_boss(self):
        """绘制Boss"""
        if self.boss:
            self.boss.draw()

    def check_coin_collection(self):
        """检查金币收集"""
        collected = self.coin_manager.check_collision(self.player)
        if collected:
            self.collected_coins += len(collected)
            self.score.add(len(collected) * 10)  # 金币分数加成

    def draw_mode_info(self):
        """绘制模式信息"""
        font = get_font('Arial', 16)
        
        # 模式名称
        mode_text = font.render(f"模式: {self.game_mode.value}", True, (255, 255, 255))
        self.config.screen.blit(mode_text, (10, 10))
        
        # 特殊模式信息
        if self.game_mode == GameMode.TIMED:
            time_text = font.render(f"时间: {max(0, self.time_remaining // 1000)}s", True, (255, 255, 0))
            self.config.screen.blit(time_text, (10, 30))
        elif self.game_mode == GameMode.COIN:
            coin_text = font.render(f"金币: {self.collected_coins}", True, (255, 215, 0))
            self.config.screen.blit(coin_text, (10, 30))
        elif self.game_mode == GameMode.BOSS and self.boss:
            boss_text = font.render(f"Boss血量: {self.boss.health}", True, (255, 0, 0))
            self.config.screen.blit(boss_text, (10, 30))

    async def game_over(self):
        """游戏结束界面"""
        font = get_font('Arial', 32)
        small_font = get_font('Arial', 16)
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        return  # 重新开始
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return  # 重新开始
            
            # 渲染背景
            self.background.draw()
            self.floor.draw()
            
            # 游戏结束文字
            game_over_text = font.render("游戏结束!", True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(self.config.window.width // 2, self.config.window.height // 2 - 100))
            self.config.screen.blit(game_over_text, game_over_rect)
            
            # 分数显示
            score_text = font.render(f"得分: {self.score.value}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.config.window.width // 2, self.config.window.height // 2 - 50))
            self.config.screen.blit(score_text, score_rect)
            
            # 重新开始提示
            restart_text = small_font.render("按空格键或点击重新开始", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(self.config.window.width // 2, self.config.window.height // 2 + 50))
            self.config.screen.blit(restart_text, restart_rect)
            
            pygame.display.update()
            await asyncio.sleep(0)


async def main():
    """Web版游戏主函数"""
    game = FlappyWeb()
    await game.start()


if __name__ == "__main__":
    # 对于Web版，使用异步循环
    asyncio.run(main()) 