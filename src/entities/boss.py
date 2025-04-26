import random
import pygame
import math
from typing import List
from enum import Enum

from ..utils import GameConfig
from .entity import Entity
from .bullet import Bullet


class BossType(Enum):
    """Boss类型枚举"""
    NORMAL = "普通Boss"    # 基础红色Boss
    SPEEDY = "速度型Boss"   # 蓝色高速Boss
    SPLITTER = "分裂型Boss" # 绿色分裂Boss
    TANK = "坦克型Boss"     # 紫色高防Boss


class Boss(Entity):
    """Boss实体类"""
    
    def __init__(self, config: GameConfig, boss_type: BossType = BossType.NORMAL) -> None:
        # 设置Boss类型
        self.boss_type = boss_type
        
        # 根据Boss类型设置属性
        if boss_type == BossType.NORMAL:
            self.base_size = 100
            self.y_offset = 0
            self.health = 100  
            self.max_health = 100
            self.speed = 2     
            self.direction = 1 
            self.bullet_cooldown = 0  
            self.bullet_rate = 60     
            self.hit_flash = 0    
            self.default_color = (255, 0, 0)  # 红色Boss
            
        elif boss_type == BossType.SPEEDY:
            self.base_size = 80   # 略小一些
            self.y_offset = 0
            self.health = 80      # 血量少一些
            self.max_health = 80
            self.speed = 4        # 更快的移动速度
            self.direction = 1  
            self.bullet_cooldown = 0  
            self.bullet_rate = 30  # 更快的射击频率
            self.hit_flash = 0   
            self.default_color = (0, 0, 255)  # 蓝色Boss
            
        elif boss_type == BossType.SPLITTER:
            self.base_size = 120  # 更大一些
            self.y_offset = 0
            self.health = 120     # 血量多一些
            self.max_health = 120
            self.speed = 1.5      # 较慢
            self.direction = 1  
            self.bullet_cooldown = 0  
            self.bullet_rate = 90  # 较慢的射击频率
            self.hit_flash = 0   
            self.default_color = (0, 255, 0)  # 绿色Boss
            self.split_threshold = 40  # 血量低于此值时分裂
            self.has_split = False     # 是否已分裂
            
        elif boss_type == BossType.TANK:
            self.base_size = 140  # 非常大
            self.y_offset = 0
            self.health = 200     # 血量非常多
            self.max_health = 200
            self.speed = 1        # 非常慢
            self.direction = 1  
            self.bullet_cooldown = 0  
            self.bullet_rate = 120 # 很慢的射击频率
            self.hit_flash = 0   
            self.default_color = (128, 0, 128)  # 紫色Boss
        
        self.bullets: List[Bullet] = []  # Boss发射的子弹
        
        # 创建Boss图像
        surface = self.create_boss_appearance()
        
        # 设置位置 (右侧屏幕)
        x = config.window.width - self.base_size - 40
        y = config.window.height // 2 - self.base_size // 2
        
        super().__init__(config, surface, x, y)
        
        # 动画属性
        self.animation_tick = 0
        
    def create_boss_appearance(self):
        """根据Boss类型创建外观"""
        surface = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        
        # 绘制Boss主体
        pygame.draw.circle(surface, self.default_color, (self.base_size//2, self.base_size//2), self.base_size//2)
        
        # 根据类型添加特殊外观
        if self.boss_type == BossType.NORMAL:
            # 普通Boss - 基本的眼睛和嘴巴
            self.draw_basic_face(surface)
            
        elif self.boss_type == BossType.SPEEDY:
            # 速度型Boss - 添加速度线条和尖锐眼睛
            self.draw_basic_face(surface)
            self.draw_speed_lines(surface)
            
        elif self.boss_type == BossType.SPLITTER:
            # 分裂型Boss - 添加分裂纹理
            self.draw_basic_face(surface)
            self.draw_split_pattern(surface)
            
        elif self.boss_type == BossType.TANK:
            # 坦克型Boss - 添加装甲纹理
            self.draw_basic_face(surface)
            self.draw_armor_pattern(surface)
        
        return surface
    
    def draw_basic_face(self, surface):
        """绘制基本的脸部特征"""
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
    
    def draw_speed_lines(self, surface):
        """为速度型Boss添加速度线条"""
        for i in range(5):
            start_x = self.base_size // 10
            end_x = self.base_size // 3
            y = self.base_size // 3 + i * (self.base_size // 10)
            
            pygame.draw.line(surface, (200, 200, 255), 
                            (start_x, y), (end_x, y), 2)
    
    def draw_split_pattern(self, surface):
        """为分裂型Boss添加分裂纹理"""
        center_x = self.base_size // 2
        center_y = self.base_size // 2
        
        # 绘制分裂线
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = center_x + int(0.3 * self.base_size * math.cos(rad))
            y1 = center_y + int(0.3 * self.base_size * math.sin(rad))
            x2 = center_x + int(0.5 * self.base_size * math.cos(rad))
            y2 = center_y + int(0.5 * self.base_size * math.sin(rad))
            
            pygame.draw.line(surface, (0, 200, 0), (x1, y1), (x2, y2), 3)
    
    def draw_armor_pattern(self, surface):
        """为坦克型Boss添加装甲纹理"""
        # 绘制装甲板
        armor_rects = [
            (self.base_size//4, self.base_size//8, self.base_size//2, self.base_size//10),
            (self.base_size//8, self.base_size//3, self.base_size//10, self.base_size//3),
            (self.base_size - self.base_size//8 - self.base_size//10, self.base_size//3, self.base_size//10, self.base_size//3),
            (self.base_size//4, self.base_size - self.base_size//8 - self.base_size//10, self.base_size//2, self.base_size//10)
        ]
        
        for rect in armor_rects:
            pygame.draw.rect(surface, (180, 180, 180), rect)
            pygame.draw.rect(surface, (100, 100, 100), rect, 2)
    
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
            self.image = self.create_boss_appearance()
        
        # 移动Boss
        self.move()
        
        # 绘制Boss
        super().draw()
        
        # 特殊行为
        self.special_behavior()
        
        # 发射子弹
        self.shoot()
        
        # 更新并绘制子弹
        for bullet in list(self.bullets):
            bullet.tick()
            # 移除超出屏幕的子弹
            if bullet.is_out_of_screen():
                self.bullets.remove(bullet)
        
        # 绘制生命条
        self.draw_health_bar()
    
    def special_behavior(self):
        """根据Boss类型执行特殊行为"""
        # 分裂型Boss特殊行为
        if self.boss_type == BossType.SPLITTER and self.health <= self.split_threshold and not self.has_split:
            self.has_split = True
            self.split()
            
    def split(self):
        """分裂型Boss分裂行为"""
        # 当生命值低于阈值时，分裂出两个小Boss
        for i in range(2):
            # 创建子弹代表分裂物
            offset_y = 50 if i == 0 else -50
            bullet = Bullet(self.config, self.x, self.y + offset_y)
            
            # 设置子弹属性
            bullet.vel_x = -3
            bullet.vel_y = 1 if i == 0 else -1
            bullet.damage = 1
            
            # 设置外观 - 小一点的绿色圆形
            size = 20
            bullet_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(bullet_surface, self.default_color, (size//2, size//2), size//2)
            bullet.image = bullet_surface
            
            # 添加到子弹列表
            self.bullets.append(bullet)
            
        # 播放分裂音效
        self.config.sounds.hit.play()
        
    def move(self) -> None:
        """移动Boss"""
        # 简单的上下移动
        self.animation_tick += 1
        
        # 更改方向
        if self.y <= 50:
            self.direction = 1
        elif self.y >= self.config.window.viewport_height - self.h - 50:
            self.direction = -1
            
        # 根据Boss类型设置移动行为
        if self.boss_type == BossType.NORMAL:
            # 普通Boss - 正常移动
            if self.animation_tick % 120 == 0 and random.random() < 0.3:
                self.direction *= -1
                
        elif self.boss_type == BossType.SPEEDY:
            # 速度型Boss - 更频繁地改变方向
            if self.animation_tick % 60 == 0 and random.random() < 0.5:
                self.direction *= -1
                
        elif self.boss_type == BossType.SPLITTER:
            # 分裂型Boss - 在生命值低时更慢
            if self.health < self.split_threshold:
                actual_speed = self.speed * 0.5
            else:
                actual_speed = self.speed
                
            self.y += actual_speed * self.direction
            return
            
        elif self.boss_type == BossType.TANK:
            # 坦克型Boss - 偶尔停顿
            if self.animation_tick % 180 < 60:  # 每180帧停顿60帧
                return  # 不移动
            
        # 应用移动
        self.y += self.speed * self.direction
    
    def shoot(self) -> None:
        """Boss发射子弹"""
        self.bullet_cooldown += 1
        
        if self.bullet_cooldown >= self.bullet_rate:
            self.bullet_cooldown = 0
            
            # 根据Boss类型选择攻击模式
            if self.boss_type == BossType.NORMAL:
                self.normal_shoot()
                
            elif self.boss_type == BossType.SPEEDY:
                self.speedy_shoot()
                
            elif self.boss_type == BossType.SPLITTER:
                self.splitter_shoot()
                
            elif self.boss_type == BossType.TANK:
                self.tank_shoot()
            
    def normal_shoot(self) -> None:
        """普通Boss直线射击"""
        # 创建子弹
        bullet_surface = pygame.Surface((15, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(bullet_surface, (255, 0, 0), bullet_surface.get_rect())
        
        # 从嘴巴位置发射
        bullet_x = self.x - 10
        bullet_y = self.y + self.h // 2
        
        bullet = Bullet(self.config, bullet_x, bullet_y)
        bullet.image = bullet_surface
        bullet.vel_x = -8  # 向左飞行
        bullet.damage = 1
        
        self.bullets.append(bullet)
        
        # 播放声音效果
        self.config.sounds.swoosh.play()
    
    def speedy_shoot(self) -> None:
        """速度型Boss三连射"""
        for i in range(3):
            bullet_surface = pygame.Surface((10, 6), pygame.SRCALPHA)
            pygame.draw.ellipse(bullet_surface, (0, 0, 255), bullet_surface.get_rect())
            
            # 从嘴巴位置发射
            bullet_x = self.x - 10
            bullet_y = self.y + self.h // 2
            
            bullet = Bullet(self.config, bullet_x, bullet_y)
            bullet.image = bullet_surface
            bullet.vel_x = -12  # 更快速度
            bullet.delay = i * 5  # 设置发射延迟
            bullet.damage = 1
            
            self.bullets.append(bullet)
        
        # 播放声音效果
        self.config.sounds.swoosh.play()
    
    def splitter_shoot(self) -> None:
        """分裂型Boss发射分裂子弹"""
        bullet_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(bullet_surface, (0, 255, 0), (6, 6), 6)
        
        # 从嘴巴位置发射
        bullet_x = self.x - 10
        bullet_y = self.y + self.h // 2
        
        bullet = Bullet(self.config, bullet_x, bullet_y)
        bullet.image = bullet_surface
        bullet.vel_x = -6  # 慢一些
        bullet.is_splitter = True
        bullet.split_time = 30  # 30帧后分裂
        bullet.damage = 1
        bullet.parent = self  # 添加父对象引用
        
        self.bullets.append(bullet)
        
        # 播放声音效果
        self.config.sounds.swoosh.play()
    
    def tank_shoot(self) -> None:
        """坦克型Boss发射大型子弹"""
        bullet_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(bullet_surface, (128, 0, 128), (10, 10), 10)
        
        # 从嘴巴位置发射
        bullet_x = self.x - 20
        bullet_y = self.y + self.h // 2
        
        bullet = Bullet(self.config, bullet_x, bullet_y)
        bullet.image = bullet_surface
        bullet.vel_x = -5  # 慢一些
        bullet.damage = 2  # 伤害更高
        
        self.bullets.append(bullet)
        
        # 播放声音效果
        self.config.sounds.swoosh.play()
        
    def take_damage(self, damage: int) -> None:
        """Boss受到伤害"""
        self.health -= damage
        self.hit_flash = 5  # 设置闪烁帧数
        
        # 播放受击声音
        self.config.sounds.hit.play()
        
        # 坦克Boss在低血量时受到的伤害减半
        if self.boss_type == BossType.TANK and self.health < self.max_health * 0.5:
            self.health += damage // 2  # 恢复一半伤害
        
        # 确保生命值不为负
        if self.health < 0:
            self.health = 0
    
    def is_defeated(self) -> bool:
        """检查Boss是否被击败"""
        # 打印当前生命值，帮助调试
        if self.health <= 0:
            print(f"Boss已被击败! 类型: {self.boss_type.value}")
            return True
        return False
    
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
        
        # 添加文字和Boss类型
        font = pygame.font.SysFont('microsoftyahei', 16)
        text = font.render(f"{self.boss_type.value}: {self.health}/{self.max_health}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
        self.config.screen.blit(text, text_rect) 