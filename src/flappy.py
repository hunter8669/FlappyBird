import asyncio
import sys

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT, K_q, K_e, K_1, K_2, K_3, K_4

from .entities import (
    Background,
    Floor,
    GameOver,
    Pipes,
    Player,
    PlayerMode,
    Score,
    WelcomeMessage,
)
from .entities.powerup import PowerUpManager, PowerUpType
from .entities.boss import Boss, BossType
from .entities.bullet import Bullet
from .entities.weapon import WeaponType
from .utils import GameConfig, Images, Sounds, Window
from enum import Enum


class GameMode(Enum):
    """游戏模式枚举"""
    CLASSIC = "经典模式"    # 经典无限模式
    TIMED = "限时挑战"      # 限时挑战模式
    REVERSE = "反向模式"    # 重力反转模式
    BOSS = "打BOSS模式"     # BOSS战模式


class Flappy:
    def __init__(self):
        """
        初始化Flappy Bird游戏
        """
        pygame.init()  # 初始化pygame
        pygame.display.set_caption("Flappy Bird")  # 设置窗口标题
        window = Window(288, 512)  # 创建窗口对象
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
        # 记录上一帧的时间，用于计算delta_time
        self.last_frame_time = pygame.time.get_ticks()
        
        # 游戏模式相关
        self.game_mode = GameMode.CLASSIC  # 默认为经典模式
        self.time_limit = 60 * 1000  # 限时模式的时间限制（毫秒）
        self.time_remaining = self.time_limit  # 剩余时间
        
        # Boss相关
        self.boss_level = 0  # 当前Boss等级
        self.boss = None  # Boss对象

    async def start(self):
        """
        启动游戏循环
        """
        while True:
            self.background = Background(self.config)  # 创建背景对象
            self.floor = Floor(self.config)  # 创建地面对象
            self.player = Player(self.config)  # 创建玩家对象
            self.welcome_message = WelcomeMessage(self.config)  # 创建欢迎信息对象
            self.game_over_message = GameOver(self.config)  # 创建游戏结束信息对象
            self.pipes = Pipes(self.config)  # 创建管道对象
            self.score = Score(self.config)  # 创建得分对象
            self.powerup_manager = PowerUpManager(self.config)  # 创建道具管理器
            await self.splash()  # 显示欢迎界面
            await self.play()  # 开始游戏
            await self.game_over()  # 游戏结束

    async def splash(self):
        """
        显示欢迎界面和模式选择
        """
        self.player.set_mode(PlayerMode.SHM)  # 设置玩家模式为SHM（静止模式）
        
        # 初始化字体 - 使用系统默认字体并设置更大的字号
        title_font = pygame.font.Font(None, 36)  # 标题字体
        mode_font = pygame.font.Font(None, 28)  # 模式选择字体
        instruction_font = pygame.font.Font(None, 22)  # 指示字体
        
        # 创建文本 - 添加标题和更美观的文本
        title_text = title_font.render("Game Mode Selection", True, (255, 255, 0))  # 黄色标题
        classic_text = mode_font.render("Classic Mode", True, (255, 255, 255))
        timed_text = mode_font.render("Timed Challenge", True, (255, 255, 255))
        reverse_text = mode_font.render("Reverse Mode", True, (255, 255, 255))  # 添加反向模式文本
        boss_text = mode_font.render("Boss Mode", True, (255, 255, 255))  # 添加Boss模式文本
        instruction_text = instruction_font.render("UP/DOWN to select, SPACE to start", True, (220, 220, 220))
        
        # 为选择框准备颜色和大小
        box_color_active = (255, 255, 0)  # 活跃选择的颜色
        box_color_inactive = (100, 100, 100, 128)  # 非活跃选择的颜色
        
        # 计算文本位置 - 调整间距使界面更加平衡
        title_pos = (self.config.window.width//2 - title_text.get_width()//2, self.config.window.height//2 - 100)  # 调整标题位置
        classic_pos = (self.config.window.width//2 - classic_text.get_width()//2, 
                      self.config.window.height//2 - 30)  # 调整经典模式位置
        timed_pos = (self.config.window.width//2 - timed_text.get_width()//2, 
                    self.config.window.height//2 + 20)  # 调整限时模式位置
        reverse_pos = (self.config.window.width//2 - reverse_text.get_width()//2, 
                      self.config.window.height//2 + 70)  # 添加反向模式位置
        boss_pos = (self.config.window.width//2 - boss_text.get_width()//2, 
                   self.config.window.height//2 + 120)  # 添加Boss模式位置
        instruction_pos = (self.config.window.width//2 - instruction_text.get_width()//2, 
                          self.config.window.height//2 + 180)  # 调整指示文本位置
        
        # 为按钮创建矩形
        classic_rect = pygame.Rect(classic_pos[0] - 20, classic_pos[1] - 10, 
                                 classic_text.get_width() + 40, classic_text.get_height() + 20)
        timed_rect = pygame.Rect(timed_pos[0] - 20, timed_pos[1] - 10, 
                               timed_text.get_width() + 40, timed_text.get_height() + 20)
        reverse_rect = pygame.Rect(reverse_pos[0] - 20, reverse_pos[1] - 10, 
                                 reverse_text.get_width() + 40, reverse_text.get_height() + 20)  # 添加反向模式矩形
        boss_rect = pygame.Rect(boss_pos[0] - 20, boss_pos[1] - 10, 
                              boss_text.get_width() + 40, boss_text.get_height() + 20)  # 添加Boss模式矩形
        
        # 默认选择经典模式
        self.game_mode = GameMode.CLASSIC
        selected_index = 0  # 0表示经典模式，1表示限时模式，2表示反向模式，3表示Boss模式

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)  # 检查退出事件
                
                # 处理模式选择
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        # 向下切换模式
                        selected_index = (selected_index + 1) % 4  # 循环切换四种模式
                        if selected_index == 0:
                            self.game_mode = GameMode.CLASSIC
                        elif selected_index == 1:
                            self.game_mode = GameMode.TIMED
                            # 重置计时器
                            self.time_remaining = self.time_limit
                        elif selected_index == 2:
                            self.game_mode = GameMode.REVERSE
                        elif selected_index == 3:
                            self.game_mode = GameMode.BOSS
                        self.config.sounds.swoosh.play()
                    elif event.key == pygame.K_UP:
                        # 向上切换模式
                        selected_index = (selected_index - 1) % 4  # 循环切换四种模式
                        if selected_index == 0:
                            self.game_mode = GameMode.CLASSIC
                        elif selected_index == 1:
                            self.game_mode = GameMode.TIMED
                            # 重置计时器
                            self.time_remaining = self.time_limit
                        elif selected_index == 2:
                            self.game_mode = GameMode.REVERSE
                        elif selected_index == 3:
                            self.game_mode = GameMode.BOSS
                        self.config.sounds.swoosh.play()
                
                # 空格或上箭头开始游戏
                if self.is_tap_event(event):
                    return
            
            # 绘制背景、地面和玩家
            self.background.tick()  # 更新背景
            self.floor.tick()  # 更新地面
            self.player.tick()  # 更新玩家
            self.welcome_message.tick()  # 更新欢迎信息
            
            # 绘制标题
            self.config.screen.blit(title_text, title_pos)
            
            # 绘制经典模式按钮
            if selected_index == 0:
                # 活跃按钮 - 绘制填充和边框
                pygame.draw.rect(self.config.screen, (50, 50, 50), classic_rect)  # 深色填充
                pygame.draw.rect(self.config.screen, box_color_active, classic_rect, 3, border_radius=5)  # 边框
            else:
                # 非活跃按钮 - 只绘制边框
                pygame.draw.rect(self.config.screen, (30, 30, 30), classic_rect)  # 浅色填充
                pygame.draw.rect(self.config.screen, box_color_inactive, classic_rect, 2, border_radius=5)  # 边框
            
            # 绘制限时模式按钮
            if selected_index == 1:
                # 活跃按钮
                pygame.draw.rect(self.config.screen, (50, 50, 50), timed_rect)  # 深色填充
                pygame.draw.rect(self.config.screen, box_color_active, timed_rect, 3, border_radius=5)  # 边框
            else:
                # 非活跃按钮
                pygame.draw.rect(self.config.screen, (30, 30, 30), timed_rect)  # 浅色填充
                pygame.draw.rect(self.config.screen, box_color_inactive, timed_rect, 2, border_radius=5)  # 边框
            
            # 绘制反向模式按钮
            if selected_index == 2:
                # 活跃按钮
                pygame.draw.rect(self.config.screen, (50, 50, 50), reverse_rect)  # 深色填充
                pygame.draw.rect(self.config.screen, box_color_active, reverse_rect, 3, border_radius=5)  # 边框
            else:
                # 非活跃按钮
                pygame.draw.rect(self.config.screen, (30, 30, 30), reverse_rect)  # 浅色填充
                pygame.draw.rect(self.config.screen, box_color_inactive, reverse_rect, 2, border_radius=5)  # 边框
                
            # 绘制Boss模式按钮
            if selected_index == 3:
                # 活跃按钮
                pygame.draw.rect(self.config.screen, (50, 50, 50), boss_rect)  # 深色填充
                pygame.draw.rect(self.config.screen, box_color_active, boss_rect, 3, border_radius=5)  # 边框
            else:
                # 非活跃按钮
                pygame.draw.rect(self.config.screen, (30, 30, 30), boss_rect)  # 浅色填充
                pygame.draw.rect(self.config.screen, box_color_inactive, boss_rect, 2, border_radius=5)  # 边框
            
            # 绘制文本
            self.config.screen.blit(classic_text, classic_pos)
            self.config.screen.blit(timed_text, timed_pos)
            self.config.screen.blit(reverse_text, reverse_pos)
            self.config.screen.blit(boss_text, boss_pos)
            self.config.screen.blit(instruction_text, instruction_pos)
            
            pygame.display.update()  # 刷新显示
            await asyncio.sleep(0)  # 等待下一帧
            self.config.tick()  # 更新游戏配置

    def check_quit_event(self, event):
        """
        检查退出事件
        """
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()  # 退出pygame
            sys.exit()  # 退出程序

    def is_tap_event(self, event):
        """
        检查点击事件
        """
        m_left, _, _ = pygame.mouse.get_pressed()  # 检查鼠标左键是否按下
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )  # 检查空格键或上箭头是否按下
        screen_tap = event.type == pygame.FINGERDOWN  # 检查触摸事件
        return m_left or space_or_up or screen_tap  # 返回是否有点击事件

    def calculate_delta_time(self):
        """
        计算两帧之间的时间差
        """
        current_time = pygame.time.get_ticks()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        return delta_time

    def check_powerup_collisions(self):
        """
        检查玩家与道具的碰撞
        """
        # 创建一个要删除的道具列表
        powerups_to_remove = []
        
        # 检查所有道具
        for powerup in self.powerup_manager.powerups:
            # 如果玩家碰到了道具
            if self.player.collide(powerup):
                # 应用道具效果
                self.player.apply_powerup_effect(powerup.power_type)
                # 激活道具在管理器中的效果
                self.powerup_manager.activate_effect(powerup.power_type)
                # 播放得分声音
                self.config.sounds.point.play()
                # 添加到要删除的列表
                powerups_to_remove.append(powerup)
        
        # 从管理器中删除已收集的道具
        for powerup in powerups_to_remove:
            if powerup in self.powerup_manager.powerups:
                self.powerup_manager.powerups.remove(powerup)

    def update_player_effects(self):
        """
        根据当前激活的效果更新玩家状态
        """
        # 检查每种效果是否已过期
        for power_type in list(PowerUpType):
            if self.powerup_manager.has_effect(power_type):
                # 效果仍然激活，确保效果被应用
                self.player.apply_powerup_effect(power_type)
            else:
                # 效果已过期，移除
                self.player.remove_powerup_effect(power_type)
    
    def render_active_effects(self):
        """
        在屏幕上显示当前激活的效果及其剩余时间
        """
        active_effects = []
        for power_type in PowerUpType:
            if self.powerup_manager.has_effect(power_type):
                remaining_ms = self.powerup_manager.get_remaining_time(power_type)
                if remaining_ms is not None:
                    active_effects.append((power_type, remaining_ms))
        
        # 如果有激活的效果，在屏幕上显示
        if active_effects:
            font = pygame.font.SysFont('Arial', 10)
            y_offset = 10
            
            for power_type, remaining_ms in active_effects:
                remaining_sec = remaining_ms / 1000
                
                # 根据道具类型选择显示文本和颜色
                if power_type == PowerUpType.SPEED_BOOST:
                    text = f"Speed Boost: {remaining_sec:.1f}s"
                    color = (255, 165, 0)  # 橙色
                elif power_type == PowerUpType.INVINCIBLE:
                    text = f"Invincible: {remaining_sec:.1f}s"
                    color = (255, 215, 0)  # 金色
                elif power_type == PowerUpType.SLOW_MOTION:
                    text = f"Slow Motion: {remaining_sec:.1f}s"
                    color = (0, 191, 255)  # 天蓝色
                elif power_type == PowerUpType.SMALL_SIZE:
                    text = f"Small Size: {remaining_sec:.1f}s"
                    color = (147, 112, 219)  # 紫色
                
                # 创建文本表面
                text_surface = font.render(text, True, color)
                text_rect = text_surface.get_rect()
                text_rect.topleft = (10, y_offset)
                
                # 绘制文本
                self.config.screen.blit(text_surface, text_rect)
                
                # 更新下一个文本的位置
                y_offset += 20

    def check_pipe_pass(self):
        """
        检查玩家是否通过管道并更新分数
        """
        # 为每个上管道检查是否通过
        for pipe in self.pipes.upper:
            # 管道中心点
            pipe_centerx = pipe.x + pipe.w/2
            # 检查玩家是否刚刚通过管道中心点
            if (pipe.x < self.player.x < pipe.x + pipe.w) and not hasattr(pipe, 'passed'):
                # 标记该管道已通过
                pipe.passed = True
                # 增加分数
                self.score.add()
                # 播放得分声音
                self.config.sounds.point.play()

    async def play(self):
        """
        主要游戏循环
        """
        # 当玩家开始游戏时
        # 根据游戏模式设置玩家模式
        if self.game_mode == GameMode.REVERSE:
            self.player.set_mode(PlayerMode.REVERSE)  # 设置玩家模式为REVERSE（反向模式）
        elif self.game_mode == GameMode.BOSS:
            self.player.set_mode(PlayerMode.BOSS)  # 设置玩家模式为BOSS（Boss模式）
            self.create_boss()  # 创建初始Boss实体
            self.pipes.upper.clear()  # 清空管道
            self.pipes.lower.clear()  # 清空管道
        else:
            self.player.set_mode(PlayerMode.NORMAL)  # 设置玩家模式为NORMAL（正常模式）
            
        self.powerup_manager.powerups = []  # 清空道具列表
        self.powerup_manager.active_effects = {}  # 清空活跃效果
        
        # 重置计时器（如果是限时模式）
        if self.game_mode == GameMode.TIMED:
            self.time_remaining = self.time_limit
            
        # 创建字体用于显示剩余时间 - 使用Windows默认字体
        time_font = pygame.font.SysFont('microsoftyahei', 24)  # 微软雅黑
        game_over = False

        while True:
            # 计算帧间隔时间
            current_time = pygame.time.get_ticks()
            delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time

            for event in pygame.event.get():
                self.check_quit_event(event)  # 检查退出事件
                if self.is_tap_event(event):
                    self.player.flap()  # 玩家点击，执行拍打动作
                    # Boss模式下，空格键也用于射击
                    if self.game_mode == GameMode.BOSS:
                        self.player.shoot()
                
                # 添加键盘事件处理
                if event.type == KEYDOWN:
                    # 武器切换 - Q/E键
                    if event.key == K_q and self.game_mode == GameMode.BOSS:
                        self.player.switch_weapon(-1)  # 上一个武器
                    elif event.key == K_e and self.game_mode == GameMode.BOSS:
                        self.player.switch_weapon(1)   # 下一个武器
                    
                    # 数字键1-4直接选择武器
                    if self.game_mode == GameMode.BOSS:
                        if event.key == K_1 and len(self.player.weapons) > 0:
                            self.player.current_weapon_index = 0
                        elif event.key == K_2 and len(self.player.weapons) > 1:
                            self.player.current_weapon_index = 1
                        elif event.key == K_3 and len(self.player.weapons) > 2:
                            self.player.current_weapon_index = 2
                        elif event.key == K_4 and len(self.player.weapons) > 3:
                            self.player.current_weapon_index = 3

            # 限时模式时间更新
            if self.game_mode == GameMode.TIMED:
                self.time_remaining -= delta_time
                if self.time_remaining <= 0:
                    self.time_remaining = 0
                    game_over = True
            
            # 更新道具管理器
            self.powerup_manager.tick(delta_time)
            
            # 检查道具碰撞
            self.check_powerup_collisions()
            
            # 更新玩家状态效果
            self.update_player_effects()
            
            # 检查管道通过情况并更新分数
            if self.game_mode != GameMode.BOSS:
                self.check_pipe_pass()

            self.background.tick()  # 更新背景
            self.floor.tick()  # 更新地面
            
            # Boss模式下不渲染管道
            if self.game_mode != GameMode.BOSS:
                self.pipes.tick()  # 更新管道
                
            self.score.tick()  # 更新得分
            self.player.tick()  # 更新玩家
            
            # Boss模式特有的逻辑
            if self.game_mode == GameMode.BOSS:
                # 更新Boss
                self.boss.tick()
                
                # 检查玩家子弹是否击中Boss
                if self.player.check_bullet_hit_boss(self.boss):
                    # 增加分数
                    self.score.add()
                    
                # 检查是否应该进化Boss
                self.evolve_boss()
                    
                # 检查Boss是否被击败
                if self.boss.is_defeated():
                    # 增加Boss等级
                    self.boss_level += 1
                    
                    # 检查是否击败了所有Boss
                    if self.boss_level >= 4:  # 已经打败了所有4种Boss
                        # Boss被击败，显示胜利信息
                        victory_font = pygame.font.SysFont('microsoftyahei', 48)
                        victory_text = victory_font.render("完全胜利！", True, (255, 215, 0))
                        victory_rect = victory_text.get_rect(center=(self.config.window.width//2, self.config.window.height//2))
                        
                        # 绘制胜利信息
                        for i in range(100):  # 显示约3秒
                            self.background.tick()
                            self.floor.tick()
                            self.player.tick()
                            
                            # 添加一个半透明背景
                            overlay = pygame.Surface((self.config.window.width, self.config.window.height), pygame.SRCALPHA)
                            overlay.fill((0, 0, 0, 128))
                            self.config.screen.blit(overlay, (0, 0))
                            
                            # 绘制胜利文本
                            self.config.screen.blit(victory_text, victory_rect)
                            
                            pygame.display.update()
                            await asyncio.sleep(0.03)
                        
                        # 跳过游戏结束画面，直接返回主菜单
                        return
                    else:
                        # 创建下一个Boss
                        await self.next_boss()
                
                # 检查玩家是否被Boss子弹击中
                if self.player.check_boss_bullet_collision(self.boss):
                    if not self.player.invincible:
                        return  # 玩家死亡
            
            # 绘制道具
            for powerup in self.powerup_manager.powerups:
                powerup.tick()
                
            # 绘制活跃效果提示
            self.render_active_effects()
            
            # 如果是限时模式，显示剩余时间
            if self.game_mode == GameMode.TIMED:
                seconds_left = max(0, int(self.time_remaining / 1000))
                
                # 创建一个半透明的计时器背景
                timer_bg = pygame.Surface((100, 40), pygame.SRCALPHA)
                alpha = 180  # 透明度
                timer_bg.fill((0, 0, 0, alpha))
                self.config.screen.blit(timer_bg, (self.config.window.width - 110, 5))
                
                # 绘制计时器文本
                time_text = time_font.render(f"Time: {seconds_left}s", True, (255, 255, 255))
                time_rect = time_text.get_rect(center=(self.config.window.width - 60, 25))
                self.config.screen.blit(time_text, time_rect)
                
                # 当时间小于10秒时闪烁显示并添加红色警告效果
                if seconds_left <= 10 and self.time_remaining > 0:
                    # 闪烁效果
                    if (current_time // 500) % 2 == 0:  # 每500毫秒闪烁一次
                        # 创建警告背景
                        warning_bg = pygame.Surface((200, 40), pygame.SRCALPHA)
                        warning_bg.fill((255, 0, 0, 150))  # 半透明红色
                        warning_rect = warning_bg.get_rect(center=(self.config.window.width//2, 50))
                        self.config.screen.blit(warning_bg, warning_rect)
                        
                        # 警告文本
                        warning_text = time_font.render("Time running out!", True, (255, 255, 255))
                        warning_text_rect = warning_text.get_rect(center=(self.config.window.width//2, 50))
                        self.config.screen.blit(warning_text, warning_text_rect)

            pygame.display.update()  # 刷新显示
            await asyncio.sleep(0)  # 等待下一帧
            self.config.tick()  # 更新游戏配置
            
            # 玩家碰撞检测（Boss模式下不检测管道碰撞）
            if self.game_mode != GameMode.BOSS:
                if self.player.collided(self.pipes, self.floor):
                    return
            else:
                # Boss模式下只检测与地板的碰撞
                if self.player.y + self.player.h >= self.floor.y - 1 or self.player.y < 0:
                    return
            
            # 限时模式结束
            if game_over:
                return

    async def game_over(self):
        """
        玩家死亡并显示游戏结束界面
        """
        self.player.set_mode(PlayerMode.CRASH)  # 设置玩家模式为CRASH（死亡模式）
        if hasattr(self, 'pipes') and self.game_mode != GameMode.BOSS:
            self.pipes.stop()  # 停止管道
        if hasattr(self, 'floor'):
            self.floor.stop()  # 停止地面

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)  # 检查退出事件
                if self.is_tap_event(event):
                    if self.player.y + self.player.h >= self.floor.y - 1:
                        return  # 如果玩家落到地面，结束游戏

            self.background.tick()  # 更新背景
            self.floor.tick()  # 更新地面
            
            # Boss模式下不需要更新管道
            if self.game_mode != GameMode.BOSS and hasattr(self, 'pipes'):
                self.pipes.tick()  # 更新管道
                
            self.score.tick()  # 更新得分
            self.player.tick()  # 更新玩家
            self.game_over_message.tick()  # 更新游戏结束信息

            pygame.display.update()  # 刷新显示
            await asyncio.sleep(0)  # 等待下一帧

    def create_boss(self):
        """创建对应等级的Boss"""
        if self.boss_level == 0:
            self.boss = Boss(self.config, BossType.NORMAL)
        elif self.boss_level == 1:
            self.boss = Boss(self.config, BossType.SPEEDY)
        elif self.boss_level == 2:
            self.boss = Boss(self.config, BossType.SPLITTER)
        elif self.boss_level == 3:
            self.boss = Boss(self.config, BossType.TANK)
    
    def evolve_boss(self):
        """根据得分演化Boss的难度"""
        # 仅当Boss生命低于一定比例时，增加其攻击频率
        if self.boss.health < self.boss.max_health * 0.5:
            if self.boss.boss_type == BossType.NORMAL:
                if self.boss.bullet_rate > 45:  # 不要让它变得太快
                    self.boss.bullet_rate -= 1
                    
            elif self.boss.boss_type == BossType.SPEEDY:
                if self.boss.bullet_rate > 20:
                    self.boss.bullet_rate -= 1
                    
            elif self.boss.boss_type == BossType.SPLITTER:
                if self.boss.bullet_rate > 70:
                    self.boss.bullet_rate -= 1
                    
            elif self.boss.boss_type == BossType.TANK:
                if self.boss.bullet_rate > 100:
                    self.boss.bullet_rate -= 1
    
    async def next_boss(self):
        """显示Boss转场动画并创建下一个Boss"""
        # 创建动画字体
        font = pygame.font.SysFont('microsoftyahei', 36)
        
        # 根据下一个Boss类型显示文本
        if self.boss_level == 1:
            text = font.render("速度型Boss出现！", True, (0, 0, 255))
        elif self.boss_level == 2:
            text = font.render("分裂型Boss出现！", True, (0, 255, 0))
        elif self.boss_level == 3:
            text = font.render("坦克型Boss出现！最终挑战！", True, (128, 0, 128))
        
        rect = text.get_rect(center=(self.config.window.width//2, self.config.window.height//2))
        
        # 显示过渡动画
        for i in range(60):  # 约2秒
            # 绘制游戏元素
            self.background.tick()
            self.floor.tick()
            self.player.tick()
            
            # 添加半透明背景
            overlay = pygame.Surface((self.config.window.width, self.config.window.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.config.screen.blit(overlay, (0, 0))
            
            # 绘制文本
            self.config.screen.blit(text, rect)
            
            pygame.display.update()
            await asyncio.sleep(0.03)
        
        # 创建新Boss
        self.create_boss()
        
        # 更新玩家 - 恢复一些武器弹药
        for weapon in self.player.weapons:
            if weapon.weapon_type == WeaponType.TRIPLE and weapon.ammo < 15:
                weapon.ammo = 15
            elif weapon.weapon_type == WeaponType.LASER and weapon.ammo < 50:
                weapon.ammo = 50
            elif weapon.weapon_type == WeaponType.HOMING and weapon.ammo < 5:
                weapon.ammo = 5
