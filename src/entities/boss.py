import random
import pygame
from typing import List

from ..utils import GameConfig
from .entity import Entity
from .bullet import Bullet


class Boss(Entity):
    """Boss实体类"""
    
    def __init__(self, config: GameConfig) -> None:
        # 创建Boss图像
        self.base_size = 100
        self.y_offset = 0
        self.health = 100  # Boss生命值
        self.max_health = 100
        self.speed = 2  # Boss移动速度
        self.direction = 1  # 移动方向
        self.bullets: List[Bullet] = []  # Boss发射的子弹
        self.bullet_cooldown = 0  # 子弹冷却时间
        self.bullet_rate = 60  # 多少帧发射一次子弹
        self.hit_flash = 0  # 受击闪烁效果
        
        # 创建Boss图像
        surface = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        self.default_color = (255, 0, 0)  # 红色Boss
        pygame.draw.circle(surface, self.default_color, (self.base_size//2, self.base_size//2), self.base_size//2)
        
        # 添加眼睛
        eye_size = self.base_size // 6
        eye_offset = self.base_size // 4
        pygame.draw.circle(surface, (255, 255, 255), 
                          (self.base_size//2 - eye_offset, self.base_size//2 - eye_offset), 
                          eye_size)
        pygame.draw.circle(surface, (255, 255, 255), 
                          (self.base_size//2 + eye_offset, self.base_size//2 - eye_offset), 
                          eye_size)
        
        # 添加眼球
        pupil_size = eye_size // 2
        pygame.draw.circle(surface, (0, 0, 0), 
                          (self.base_size//2 - eye_offset, self.base_size//2 - eye_offset), 
                          pupil_size)
        pygame.draw.circle(surface, (0, 0, 0), 
                          (self.base_size//2 + eye_offset, self.base_size//2 - eye_offset), 
                          pupil_size)
        
        # 添加嘴巴
        mouth_width = self.base_size // 2
        mouth_height = self.base_size // 8
        mouth_rect = pygame.Rect(
            self.base_size//2 - mouth_width//2,
            self.base_size//2 + eye_offset,
            mouth_width,
            mouth_height
        )
        pygame.draw.rect(surface, (0, 0, 0), mouth_rect)
        
        # 设置位置 (右侧屏幕)
        x = config.window.width - self.base_size - 40
        y = config.window.height // 2 - self.base_size // 2
        
        super().__init__(config, surface, x, y)
        
        # 动画属性
        self.animation_tick = 0
        
    def draw(self) -> None:
        # 受击闪烁效果
        if self.hit_flash > 0:
            self.hit_flash -= 1
            flash_color = (255, 255, 255)
            surface = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
            pygame.draw.circle(surface, flash_color, (self.base_size//2, self.base_size//2), self.base_size//2)
            self.image = surface
        else:
            # 恢复正常显示
            surface = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
            pygame.draw.circle(surface, self.default_color, (self.base_size//2, self.base_size//2), self.base_size//2)
            
            # 添加眼睛
            eye_size = self.base_size // 6
            eye_offset = self.base_size // 4
            pygame.draw.circle(surface, (255, 255, 255), 
                              (self.base_size//2 - eye_offset, self.base_size//2 - eye_offset), 
                              eye_size)
            pygame.draw.circle(surface, (255, 255, 255), 
                              (self.base_size//2 + eye_offset, self.base_size//2 - eye_offset), 
                              eye_size)
            
            # 添加眼球
            pupil_size = eye_size // 2
            pygame.draw.circle(surface, (0, 0, 0), 
                              (self.base_size//2 - eye_offset, self.base_size//2 - eye_offset), 
                              pupil_size)
            pygame.draw.circle(surface, (0, 0, 0), 
                              (self.base_size//2 + eye_offset, self.base_size//2 - eye_offset), 
                              pupil_size)
            
            # 添加嘴巴
            mouth_width = self.base_size // 2
            mouth_height = self.base_size // 8
            mouth_rect = pygame.Rect(
                self.base_size//2 - mouth_width//2,
                self.base_size//2 + eye_offset,
                mouth_width,
                mouth_height
            )
            pygame.draw.rect(surface, (0, 0, 0), mouth_rect)
            
            self.image = surface
        
        # 移动Boss
        self.move()
        
        # 绘制Boss
        super().draw()
        
        # 发射子弹
        self.shoot()
        
        # 更新并绘制子弹
        for bullet in list(self.bullets):
            bullet.tick()
            # 移除超出屏幕的子弹
            if bullet.x < -bullet.w:
                self.bullets.remove(bullet)
        
        # 绘制生命条
        self.draw_health_bar()
        
    def move(self) -> None:
        """移动Boss"""
        # 简单的上下移动
        self.animation_tick += 1
        
        # 更改方向
        if self.y <= 50:
            self.direction = 1
        elif self.y >= self.config.window.viewport_height - self.h - 50:
            self.direction = -1
            
        # 随机变换方向
        if self.animation_tick % 120 == 0 and random.random() < 0.3:
            self.direction *= -1
            
        # 应用移动
        self.y += self.speed * self.direction
    
    def shoot(self) -> None:
        """Boss发射子弹"""
        self.bullet_cooldown += 1
        
        if self.bullet_cooldown >= self.bullet_rate:
            self.bullet_cooldown = 0
            
            # 创建子弹
            bullet_surface = pygame.Surface((15, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(bullet_surface, (255, 0, 0), bullet_surface.get_rect())
            
            # 从嘴巴位置发射
            bullet_x = self.x - 10
            bullet_y = self.y + self.h // 2
            
            bullet = Bullet(self.config, bullet_x, bullet_y)
            bullet.image = bullet_surface
            bullet.vel_x = -8  # 向左飞行
            
            self.bullets.append(bullet)
            
            # 播放声音效果
            self.config.sounds.swoosh.play()
    
    def take_damage(self, damage: int) -> None:
        """Boss受到伤害"""
        self.health -= damage
        self.hit_flash = 5  # 设置闪烁帧数
        
        # 播放受击声音
        self.config.sounds.hit.play()
        
        # 确保生命值不为负
        if self.health < 0:
            self.health = 0
    
    def is_defeated(self) -> bool:
        """检查Boss是否被击败"""
        return self.health <= 0
    
    def draw_health_bar(self) -> None:
        """绘制Boss生命条"""
        bar_width = 200
        bar_height = 20
        x = self.config.window.width - bar_width - 20
        y = 20
        
        # 绘制底部背景
        pygame.draw.rect(self.config.screen, (50, 50, 50), 
                        (x, y, bar_width, bar_height))
        
        # 计算当前生命值对应的宽度
        health_width = int((self.health / self.max_health) * bar_width)
        
        # 根据生命值选择颜色
        if self.health > self.max_health * 0.6:
            color = (0, 255, 0)  # 绿色
        elif self.health > self.max_health * 0.3:
            color = (255, 255, 0)  # 黄色
        else:
            color = (255, 0, 0)  # 红色
            
        # 绘制生命值
        pygame.draw.rect(self.config.screen, color, 
                        (x, y, health_width, bar_height))
        
        # 绘制边框
        pygame.draw.rect(self.config.screen, (200, 200, 200), 
                        (x, y, bar_width, bar_height), 2)
        
        # 添加文字
        font = pygame.font.SysFont('microsoftyahei', 16)
        text = font.render(f"BOSS HP: {self.health}/{self.max_health}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
        self.config.screen.blit(text, text_rect) 