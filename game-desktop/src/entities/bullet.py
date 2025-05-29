import pygame
import copy
import math

from ..utils import GameConfig
from .entity import Entity


class Bullet(Entity):
    """玩家发射的子弹类"""
    
    def __init__(self, config: GameConfig, x: int, y: int) -> None:
        # 创建子弹表面
        size = 8
        color = (255, 255, 0)  # 黄色子弹
        
        # 创建子弹图像
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (size//2, size//2), size//2)
        
        # 子弹速度
        self.vel_x = 10  # 水平速度
        self.vel_y = 0   # 垂直速度
        self.damage = 10  # 默认伤害
        self.color = color  # 子弹颜色，用于特效
        
        # 特殊子弹属性
        self.is_laser = False
        self.is_homing = False
        self.is_splitter = False
        self.is_lightning = False  # 闪电特效
        self.split_time = 0
        self.target = None
        self.speed = 10
        self.turn_rate = 0
        self.delay = 0  # 延迟发射
        self.trail_frames = []
        self.trail_length = 0
        
        # 闪电zigzag效果点
        self.zigzag_points = []
        self.width = 2  # 闪电宽度
        
        # 初始化实体
        super().__init__(config, surface, x, y)
        
        # 保存原始图像用于旋转
        self.original_image = self.image.copy()
    
    def draw(self) -> None:
        # 处理延迟发射
        if self.delay > 0:
            self.delay -= 1
            super().draw()  # 仍然绘制子弹但不移动
            return
        
        # 特殊子弹类型的更新逻辑
        if self.is_homing and hasattr(self, 'update_homing'):
            self.update_homing(self)
        elif self.is_lightning and hasattr(self, 'zigzag_points') and len(self.zigzag_points) > 1:
            # 闪电效果特殊处理
            self.draw_lightning()
            return
        else:
            # 普通更新
            self.x += self.vel_x
            self.y += self.vel_y
        
        # 处理激光拖尾效果
        if self.trail_length > 0:
            # 保存当前位置信息
            self.trail_frames.append((self.x, self.y, self.image.copy()))
            
            # 只保留最近的几帧
            if len(self.trail_frames) > self.trail_length:
                self.trail_frames.pop(0)
            
            # 绘制拖尾效果（半透明）
            for i, (trail_x, trail_y, trail_img) in enumerate(self.trail_frames[:-1]):
                alpha = 128 * (i + 1) // len(self.trail_frames)  # 越早的帧越透明
                trail_img.set_alpha(alpha)
                self.config.screen.blit(trail_img, (trail_x, trail_y))
        
        # 分裂子弹逻辑
        if self.is_splitter:
            self.split_time -= 1
            if self.split_time <= 0 and not hasattr(self, 'has_split'):
                self.has_split = True
                self.split()
        
        super().draw()  # 调用父类绘制方法
    
    def draw_lightning(self) -> None:
        """绘制闪电效果"""
        if not hasattr(self, 'zigzag_points') or len(self.zigzag_points) < 2:
            return
            
        # 获取闪电颜色
        lightning_color = self.color if hasattr(self, 'color') else (0, 150, 255)
        
        # 绘制主闪电
        for i in range(len(self.zigzag_points) - 1):
            start = self.zigzag_points[i]
            end = self.zigzag_points[i + 1]
            
            # 绘制闪电线条
            pygame.draw.line(
                self.config.screen,
                lightning_color,
                start,
                end,
                int(self.width)
            )
            
            # 添加发光效果
            glow_width = self.width * 0.7
            pygame.draw.line(
                self.config.screen,
                (lightning_color[0], lightning_color[1], lightning_color[2], 128),
                start,
                end,
                int(glow_width * 2)
            )
            
        # 更新子弹的实际位置，用于碰撞检测
        if len(self.zigzag_points) > 0:
            last_point = self.zigzag_points[-1]
            self.x, self.y = last_point
    
    def split(self) -> None:
        """分裂子弹逻辑"""
        # 创建3个分裂子弹
        angles = [-30, 0, 30]
        for angle in angles:
            # 创建新子弹
            new_x = self.x
            new_y = self.y
            
            bullet = Bullet(self.config, new_x, new_y)
            bullet.damage = self.damage // 2  # 伤害减半
            
            # 设置速度
            angle_rad = math.radians(angle)
            speed = 8
            bullet.vel_x = speed * math.cos(angle_rad)
            bullet.vel_y = speed * math.sin(angle_rad)
            
            # 设置外观 - 小一点的绿色子弹
            size = 5
            bullet_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(bullet_surface, (0, 255, 0), (size//2, size//2), size//2)
            bullet.image = bullet_surface
            bullet.color = (0, 255, 0)
            
            # 添加到父弹所属的子弹列表中
            if hasattr(self, 'parent') and hasattr(self.parent, 'bullets'):
                self.parent.bullets.append(bullet)
        
    def is_out_of_screen(self) -> bool:
        """检查子弹是否超出屏幕范围"""
        return (self.x > self.config.window.width or
                self.x < -self.w or
                self.y > self.config.window.height or
                self.y < -self.h)
