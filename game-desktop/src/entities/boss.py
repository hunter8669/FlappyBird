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


# 新增伤害数字显示类
class DamageText:
    """显示伤害数值的飘动文本"""
    def __init__(self, config, x, y, damage, color=(255, 255, 255)):
        self.config = config
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.life = 30  # 显示帧数
        self.velocity_y = -1.5  # 向上飘动速度
        self.alpha = 255  # 透明度
        
        # 创建字体
        try:
            self.font = pygame.font.SysFont('Arial', 14)
        except:
            self.font = pygame.font.Font(None, 14)
    
    def tick(self):
        """更新伤害文本状态"""
        self.life -= 1
        self.y += self.velocity_y
        
        # 逐渐降低透明度
        if self.life < 10:
            self.alpha = int(self.alpha * 0.8)
        
        # 渲染文本
        text = self.font.render(f"{self.damage}", True, self.color)
        text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))  # 透明背景
        text_surface.blit(text, (0, 0))
        
        # 应用透明度
        text_surface.set_alpha(self.alpha)
        
        # 绘制到屏幕上
        self.config.screen.blit(text_surface, (self.x, self.y))
        
        return self.life > 0  # 返回是否仍然存活


class Boss(Entity):
    """Boss实体类"""
    
    def __init__(self, config: GameConfig, boss_type: BossType = BossType.NORMAL) -> None:
        # 设置Boss类型
        self.boss_type = boss_type
        
        # 添加准备阶段属性
        self.preparation_time = 60  # 准备时间（帧数）：约2秒
        self.is_preparing = True    # 是否处于准备阶段
        
        # 新增伤害文本列表
        self.damage_texts = []
        
        # 怒气系统新增属性
        self.rage = 0               # 当前怒气值
        self.max_rage = 100         # 最大怒气值
        
        # 根据Boss类型调整怒气获取速度和阈值
        if boss_type == BossType.NORMAL:
            self.rage_gain_on_hit = 8    # 普通Boss受击怒气增加
            self.rage_gain_over_time = 0.15  # 普通Boss随时间获取怒气速度
            self.rage_threshold = 90   # 普通Boss触发大招的怒气阈值
        elif boss_type == BossType.SPEEDY:
            self.rage_gain_on_hit = 5    # 速度Boss受击怒气增加
            self.rage_gain_over_time = 0.25  # 速度Boss随时间获取怒气速度
            self.rage_threshold = 80   # 速度Boss触发大招的怒气阈值
        elif boss_type == BossType.SPLITTER:
            self.rage_gain_on_hit = 10    # 分裂Boss受击怒气增加
            self.rage_gain_over_time = 0.1  # 分裂Boss随时间获取怒气速度
            self.rage_threshold = 95   # 分裂Boss触发大招的怒气阈值
        elif boss_type == BossType.TANK:
            self.rage_gain_on_hit = 12    # 坦克Boss受击怒气增加
            self.rage_gain_over_time = 0.08  # 坦克Boss随时间获取怒气速度
            self.rage_threshold = 100   # 坦克Boss触发大招的怒气阈值
            
        self.is_using_ultimate = False  # 是否正在释放大招
        self.ultimate_duration = 0   # 大招剩余持续时间
        self.ultimate_cooldown = 0   # 大招冷却时间
        self.ultimate_effect_particles = []  # 大招特效粒子
        self.ultimate_warning_shown = False  # 是否已显示大招警告
        self.pre_ultimate_delay = 0  # 大招释放前的延迟
        
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
        
        # 为Boss添加循环级别属性
        self.level = 1  # 默认级别为1
        
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
    
    def tick(self) -> None:
        """更新Boss状态"""
        self.move()
        
        # 更新准备阶段
        if self.is_preparing:
            self.preparation_time -= 1
            if self.preparation_time <= 0:
                self.is_preparing = False
                # 播放准备完成音效
                self.config.sounds.swoosh.play()
            # 准备阶段不攻击
            self.update_bullets()
            self.animation_tick += 1
            self.special_behavior()
            
            # 更新并绘制伤害文本
            self.update_damage_texts()
            
            self.draw()
            return
            
        # 管理射击冷却
        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1
        
        # 检查是否可以射击
        if self.bullet_cooldown <= 0:
            self.shoot()
            self.bullet_cooldown = self.bullet_rate
        
        # 更新动画
        self.animation_tick += 1
        
        # 更新并绘制子弹
        self.update_bullets()
        
        # 更新并绘制伤害文本
        self.update_damage_texts()
        
        # 更新怒气和大招状态
        self.update_rage()
        
        # 特殊行为
        self.special_behavior()
        
        # 绘制Boss
        self.draw()
    
    def draw(self) -> None:
        # 受击闪烁效果
        if self.hit_flash > 0:
            self.hit_flash -= 1
            flash_color = (255, 255, 255)
            surface = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
            pygame.draw.circle(surface, flash_color, (self.base_size//2, self.base_size//2), self.base_size//2)
            self.config.screen.blit(surface, (self.x, self.y))
        else:
            # 确保恢复正常显示
            if not hasattr(self, 'normal_displayed') or not self.normal_displayed:
                self.image = self.create_boss_appearance()
                self.normal_displayed = True
            # 正常绘制
            self.config.screen.blit(self.image, (self.x, self.y))
            
        # 直接在Boss头上方绘制血条
        self.draw_health_bar_overhead()
        
        # 绘制怒气条
        self.draw_rage_bar(self.x, self.y + self.base_size + 5, self.base_size, 4)
        
        # 大招准备中显示警告特效
        if self.pre_ultimate_delay > 0:
            self.draw_ultimate_warning()
        
        # 准备阶段显示提示和准备进度条
        if self.is_preparing:
            try:
                warning_font = pygame.font.SysFont('Arial', 18)
            except:
                warning_font = pygame.font.Font(None, 18)
                
            warning_text = warning_font.render("准备攻击...", True, (255, 50, 50))
            text_x = self.x + (self.base_size - warning_text.get_width()) // 2
            text_y = self.y - 30
            self.config.screen.blit(warning_text, (text_x, text_y))
            
            # 添加准备进度条
            # 获取初始准备时间
            if not hasattr(self, 'initial_preparation_time'):
                self.initial_preparation_time = 60  # 默认值
                if hasattr(self, 'preparation_time'):
                    # 在第一次调用时设置初始准备时间
                    self.initial_preparation_time = self.preparation_time
            
            # 计算进度
            progress = 1.0
            if self.initial_preparation_time > 0:
                progress = max(0, min(1, self.preparation_time / self.initial_preparation_time))
            
            # 绘制进度条背景
            bar_width = self.base_size * 0.8
            bar_height = 6
            bar_x = self.x + (self.base_size - bar_width) // 2
            bar_y = self.y - 40
            
            # 背景
            pygame.draw.rect(self.config.screen, (50, 50, 50, 180), 
                            pygame.Rect(bar_x, bar_y, bar_width, bar_height))
            
            # 进度
            progress_width = bar_width * progress
            if progress > 0:
                # 修改颜色渐变逻辑，使用更平滑的黄色到绿色过渡，去除红色
                if progress > 0.5:
                    # 从黄色到绿色
                    green = 255
                    red = int(255 * 2 * (1 - progress))
                    bar_color = (red, green, 0)
                else:
                    # 从橙色到黄色
                    red = 255
                    green = int(255 * progress * 2)
                    bar_color = (red, green, 0)
                
                pygame.draw.rect(self.config.screen, bar_color, 
                                pygame.Rect(bar_x, bar_y, progress_width, bar_height))
            
            # 边框 - 使用白色半透明边框
            pygame.draw.rect(self.config.screen, (255, 255, 255, 100), 
                            pygame.Rect(bar_x, bar_y, bar_width, bar_height), 1)
    
    def draw_health_bar_overhead(self) -> None:
        """直接在Boss头上方绘制生命条"""
        # 血条宽度为Boss直径的80%
        bar_width = int(self.base_size * 0.8)
        bar_height = 6
        
        # 位置：居中在Boss顶部上方
        bar_x = self.x + (self.base_size - bar_width) // 2
        bar_y = self.y - bar_height - 5  # 在Boss上方5像素
        
        # 确保血条不会超出屏幕顶部
        if bar_y < 0:
            bar_y = 0
        
        # 绘制背景
        bg_color = (0, 0, 0, 180)  # 半透明黑色
        bg_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        self.config.screen.blit(bg_surface, (bar_x, bar_y))
        
        # 计算血条长度
        health_percent = self.health / self.max_health
        health_width = int(bar_width * health_percent)
        
        # 根据血量选择颜色
        if health_percent > 0.7:
            health_color = (0, 255, 0)  # 绿色
        elif health_percent > 0.3:
            health_color = (255, 255, 0)  # 黄色
        else:
            health_color = (255, 0, 0)  # 红色
        
        # 绘制血条
        if health_width > 0:  # 确保血量大于0才绘制
            health_surface = pygame.Surface((health_width, bar_height), pygame.SRCALPHA)
            health_surface.fill(health_color)
            self.config.screen.blit(health_surface, (bar_x, bar_y))
        
        # 添加边框
        pygame.draw.rect(self.config.screen, (255, 255, 255, 100), 
                         pygame.Rect(bar_x, bar_y, bar_width, bar_height), 1)
        
        # 添加血量数值显示
        try:
            hp_font = pygame.font.SysFont('Arial', 10)
        except:
            hp_font = pygame.font.Font(None, 10)
        
        hp_text = hp_font.render(f"{int(self.health)}/{self.max_health}", True, (255, 255, 255))
        hp_text_rect = hp_text.get_rect(midleft=(bar_x + bar_width + 5, bar_y + bar_height // 2))
        self.config.screen.blit(hp_text, hp_text_rect)
        
        # 如果是Boss战斗的第二轮或以上，在血条旁显示等级
        if hasattr(self, 'level') and self.level > 1:
            # 使用小字体
            try:
                level_font = pygame.font.SysFont('Arial', 12)
            except:
                level_font = pygame.font.Font(None, 12)
            
            level_text = level_font.render(f"Lv{self.level}", True, (255, 255, 255))
            self.config.screen.blit(level_text, (bar_x + bar_width + 2, bar_y))
    
    def draw_rage_bar(self, x, y, width, height):
        """绘制怒气条"""
        # 确保怒气条不会超出屏幕底部
        if y + height > self.config.window.height:
            y = self.config.window.height - height - 2
            
        # 绘制背景
        bg_color = (0, 0, 0, 150)  # 半透明黑色
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        self.config.screen.blit(bg_surface, (x, y))
        
        # 计算怒气条长度
        rage_percent = self.rage / self.max_rage
        rage_width = int(width * rage_percent)
        
        # 怒气条颜色 - 从紫色渐变到红色
        if rage_percent < 0.5:
            # 从紫色到粉红色
            red = int(128 + 127 * rage_percent * 2)
            green = 0
            blue = int(128 * (1 - rage_percent * 2))
            rage_color = (red, green, blue)
        else:
            # 从粉红色到红色
            red = 255
            green = 0
            blue = int(127 * (1 - (rage_percent - 0.5) * 2))
            rage_color = (red, green, blue)
        
        # 怒气接近满时闪烁效果
        if rage_percent > 0.8:
            pulse = (math.sin(pygame.time.get_ticks() / 100) + 1) / 2  # 0到1的脉动
            glow_alpha = int(100 + 155 * pulse)  # 闪烁透明度
            
            # 创建发光效果
            glow_surface = pygame.Surface((width, height + 6), pygame.SRCALPHA)
            glow_color = (rage_color[0], rage_color[1], rage_color[2], glow_alpha)
            pygame.draw.rect(glow_surface, glow_color, 
                            pygame.Rect(0, 0, rage_width, height + 6))
            self.config.screen.blit(glow_surface, (x, y - 3))
            
        # 绘制怒气条
        if rage_width > 0:
            rage_surface = pygame.Surface((rage_width, height), pygame.SRCALPHA)
            rage_surface.fill(rage_color)
            self.config.screen.blit(rage_surface, (x, y))
            
        # 绘制边框
        pygame.draw.rect(self.config.screen, (200, 200, 200, 150), 
                         pygame.Rect(x, y, width, height), 1)
                         
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
        # 准备阶段或大招状态下不射击
        if self.is_preparing or self.is_using_ultimate:
            return
            
        # 根据Boss类型选择射击模式
        if self.boss_type == BossType.NORMAL:
            self.normal_shoot()
        elif self.boss_type == BossType.SPEEDY:
            self.speedy_shoot()
        elif self.boss_type == BossType.SPLITTER:
            self.splitter_shoot()
        elif self.boss_type == BossType.TANK:
            self.tank_shoot()
            
        # 重置射击冷却时间
        self.bullet_cooldown = self.bullet_rate
            
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
        
    def update_rage(self):
        """更新怒气值和大招状态"""
        # 准备阶段不更新怒气
        if self.is_preparing:
            return
            
        # 如果正在大招释放前的等待时间
        if self.pre_ultimate_delay > 0:
            self.pre_ultimate_delay -= 1
            
            # 播放警告音效
            if self.pre_ultimate_delay % 10 == 0:
                self.config.sounds.swoosh.play()
                
            # 等待结束，正式开始大招
            if self.pre_ultimate_delay <= 0:
                self.is_using_ultimate = True
                
                # 设置大招持续时间 - 根据Boss类型调整
                if self.boss_type == BossType.NORMAL:
                    self.ultimate_duration = 90  # 3秒
                elif self.boss_type == BossType.SPEEDY:
                    self.ultimate_duration = 120  # 4秒
                elif self.boss_type == BossType.SPLITTER:
                    self.ultimate_duration = 60  # 2秒
                elif self.boss_type == BossType.TANK:
                    self.ultimate_duration = 150  # 5秒
                
                # 播放大招开始音效
                self.config.sounds.point.play()
                
                # 创建大招特效
                self.prepare_ultimate_effect()
            
            return
            
        # 如果正在使用大招，处理大招效果
        if self.is_using_ultimate:
            self.ultimate_duration -= 1
            
            # 更新大招特效
            self.update_ultimate_particles()
            
            # 执行大招效果
            self.perform_ultimate_effect()
            
            # 大招结束
            if self.ultimate_duration <= 0:
                self.is_using_ultimate = False
                self.ultimate_cooldown = 180  # 设置冷却时间
                
                # 播放大招结束音效
                self.config.sounds.hit.play()
                
            return
            
        # 冷却中不增加怒气
        if self.ultimate_cooldown > 0:
            self.ultimate_cooldown -= 1
            return
            
        # 随时间增加怒气，根据Boss类型有不同速度
        self.rage += self.rage_gain_over_time
        
        # 确保怒气值不超过最大值
        if self.rage > self.max_rage:
            self.rage = self.max_rage
        
        # 检查是否应该释放大招
        if self.rage >= self.rage_threshold:
            self.trigger_ultimate()
            
    def trigger_ultimate(self):
        """触发Boss大招"""
        # 设置大招状态
        self.rage = 0  # 重置怒气
        self.pre_ultimate_delay = 60  # 设置2秒的准备时间
        self.ultimate_warning_shown = True
        
        # 播放大招准备音效
        self.config.sounds.hit.play()
    
    def prepare_ultimate_effect(self):
        """准备大招特效"""
        # 清空现有特效
        self.ultimate_effect_particles = []
        
        # 根据Boss类型创建不同的特效
        if self.boss_type == BossType.NORMAL:
            # 普通Boss - 火焰环特效
            for i in range(30):
                angle = random.random() * math.pi * 2
                distance = self.base_size * (0.7 + random.random() * 0.3)
                speed = 1 + random.random() * 2
                
                particle = {
                    'x': self.x + self.base_size // 2,
                    'y': self.y + self.base_size // 2,
                    'angle': angle,
                    'distance': distance,
                    'speed': speed,
                    'size': 3 + random.random() * 5,
                    'color': (255, 100 + random.randint(0, 155), 0, 255),
                    'phase': random.random() * math.pi * 2
                }
                self.ultimate_effect_particles.append(particle)
                
        elif self.boss_type == BossType.SPEEDY:
            # 速度型Boss - 蓝色闪电特效
            for i in range(20):
                x = self.x + random.randint(0, self.base_size)
                y = self.y + random.randint(0, self.base_size)
                
                particle = {
                    'x': x,
                    'y': y,
                    'target_x': self.x - 200 - random.random() * 100,
                    'target_y': random.randint(50, self.config.window.height - 50),
                    'progress': 0,
                    'speed': 0.03 + random.random() * 0.02,
                    'thickness': 1 + random.random() * 2,
                    'color': (0, 100 + random.randint(0, 155), 255, 255),
                    'branches': []
                }
                
                # 添加分支
                if random.random() > 0.5:
                    num_branches = random.randint(1, 3)
                    for j in range(num_branches):
                        branch = {
                            'start_progress': 0.3 + random.random() * 0.4,
                            'target_x': particle['target_x'] + random.randint(-100, 100),
                            'target_y': particle['target_y'] + random.randint(-100, 100),
                            'progress': 0,
                            'speed': 0.04 + random.random() * 0.02,
                            'thickness': 0.5 + random.random() * 1.5,
                            'color': particle['color']
                        }
                        particle['branches'].append(branch)
                        
                self.ultimate_effect_particles.append(particle)
                
        elif self.boss_type == BossType.SPLITTER:
            # 分裂型Boss - 绿色能量爆炸特效
            for i in range(50):
                angle = random.random() * math.pi * 2
                
                particle = {
                    'x': self.x + self.base_size // 2,
                    'y': self.y + self.base_size // 2,
                    'vel_x': math.cos(angle) * (2 + random.random() * 4),
                    'vel_y': math.sin(angle) * (2 + random.random() * 4),
                    'size': 2 + random.random() * 4,
                    'color': (0, 255, 0, 255),
                    'fade_speed': 3 + random.random() * 5
                }
                self.ultimate_effect_particles.append(particle)
                
        elif self.boss_type == BossType.TANK:
            # 坦克型Boss - 紫色能量波特效
            for i in range(5):
                particle = {
                    'x': self.x + self.base_size // 2,
                    'y': self.y + self.base_size // 2,
                    'radius': 10,
                    'max_radius': 300 + random.random() * 100,
                    'growth_speed': 3 + random.random() * 2,
                    'thickness': 4 + random.random() * 3,
                    'color': (128, 0, 128, 200),
                    'delay': i * 15  # 每个波浪之间的延迟
                }
                self.ultimate_effect_particles.append(particle)
    
    def update_ultimate_particles(self):
        """更新大招特效粒子"""
        # 根据Boss类型更新不同类型的特效
        if self.boss_type == BossType.NORMAL:
            # 普通Boss - 火焰环特效
            for particle in self.ultimate_effect_particles:
                # 更新相位
                particle['phase'] += 0.1
                
                # 计算位置
                angle = particle['angle'] + math.sin(particle['phase']) * 0.2
                x = self.x + self.base_size // 2 + math.cos(angle) * particle['distance']
                y = self.y + self.base_size // 2 + math.sin(angle) * particle['distance']
                
                # 绘制粒子
                pygame.draw.circle(self.config.screen, particle['color'], 
                                  (int(x), int(y)), int(particle['size']))
                
        elif self.boss_type == BossType.SPEEDY:
            # 速度型Boss - 蓝色闪电特效
            for particle in list(self.ultimate_effect_particles):
                # 更新进度
                particle['progress'] += particle['speed']
                
                # 如果进度完成，移除粒子
                if particle['progress'] >= 1:
                    self.ultimate_effect_particles.remove(particle)
                    continue
                    
                # 计算当前位置
                x1 = particle['x']
                y1 = particle['y']
                x2 = particle['x'] + (particle['target_x'] - particle['x']) * particle['progress']
                y2 = particle['y'] + (particle['target_y'] - particle['y']) * particle['progress']
                
                # 绘制闪电
                pygame.draw.line(self.config.screen, particle['color'], 
                                (int(x1), int(y1)), (int(x2), int(y2)), 
                                int(particle['thickness']))
                
                # 更新分支
                for branch in particle['branches']:
                    # 只有当主闪电进度超过分支起始进度时才绘制分支
                    if particle['progress'] >= branch['start_progress']:
                        # 计算分支起始位置
                        branch_x1 = particle['x'] + (particle['target_x'] - particle['x']) * branch['start_progress']
                        branch_y1 = particle['y'] + (particle['target_y'] - particle['y']) * branch['start_progress']
                        
                        # 更新分支进度
                        if branch['progress'] < 1:
                            branch['progress'] += branch['speed']
                            
                        # 计算分支当前位置
                        branch_x2 = branch_x1 + (branch['target_x'] - branch_x1) * branch['progress']
                        branch_y2 = branch_y1 + (branch['target_y'] - branch_y1) * branch['progress']
                        
                        # 绘制分支
                        pygame.draw.line(self.config.screen, branch['color'], 
                                        (int(branch_x1), int(branch_y1)), 
                                        (int(branch_x2), int(branch_y2)), 
                                        int(branch['thickness']))
                
        elif self.boss_type == BossType.SPLITTER:
            # 分裂型Boss - 绿色能量爆炸特效
            for particle in list(self.ultimate_effect_particles):
                # 更新位置
                particle['x'] += particle['vel_x']
                particle['y'] += particle['vel_y']
                
                # 更新透明度
                if 'color' in particle and len(particle['color']) > 3:
                    r, g, b, a = particle['color']
                    a = max(0, a - particle['fade_speed'])
                    
                    # 如果完全透明，移除粒子
                    if a <= 0:
                        self.ultimate_effect_particles.remove(particle)
                        continue
                        
                    particle['color'] = (r, g, b, a)
                
                # 绘制粒子
                if 'color' in particle and 'size' in particle:
                    surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)), pygame.SRCALPHA)
                    pygame.draw.circle(surface, particle['color'], 
                                      (int(particle['size']), int(particle['size'])), 
                                      int(particle['size']))
                    self.config.screen.blit(surface, 
                                           (int(particle['x'] - particle['size']), 
                                            int(particle['y'] - particle['size'])))
                
        elif self.boss_type == BossType.TANK:
            # 坦克型Boss - 紫色能量波特效
            for particle in list(self.ultimate_effect_particles):
                # 处理延迟
                if 'delay' in particle and particle['delay'] > 0:
                    particle['delay'] -= 1
                    continue
                
                # 更新半径
                particle['radius'] += particle['growth_speed']
                
                # 如果超过最大半径，移除粒子
                if particle['radius'] >= particle['max_radius']:
                    self.ultimate_effect_particles.remove(particle)
                    continue
                
                # 计算透明度，随半径增大而降低
                alpha = int(200 * (1 - particle['radius'] / particle['max_radius']))
                color = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)
                
                # 绘制能量波
                pygame.draw.circle(self.config.screen, color, 
                                  (int(particle['x']), int(particle['y'])), 
                                  int(particle['radius']), 
                                  int(particle['thickness']))
    
    def perform_ultimate_effect(self):
        """执行大招效果"""
        # 根据Boss类型执行不同的大招
        if self.boss_type == BossType.NORMAL:
            self.normal_ultimate()
        elif self.boss_type == BossType.SPEEDY:
            self.speedy_ultimate()
        elif self.boss_type == BossType.SPLITTER:
            self.splitter_ultimate()
        elif self.boss_type == BossType.TANK:
            self.tank_ultimate()
    
    def normal_ultimate(self):
        """普通Boss的大招：火焰爆发"""
        # 每8帧发射一颗火球(增加频率)
        if self.ultimate_duration % 8 == 0:
            # 从Boss周围随机位置发射
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            
            # 创建火球子弹
            bullet_surface = pygame.Surface((25, 25), pygame.SRCALPHA)  # 增大火球尺寸
            pygame.draw.circle(bullet_surface, (255, 100, 0), (12, 12), 12)
            
            # 添加更多火焰效果
            for i in range(8):  # 增加火焰数量
                flame_size = 6 + random.random() * 6
                flame_x = 12 + random.randint(-8, 8)
                flame_y = 12 + random.randint(-8, 8)
                flame_color = (255, 200 + random.randint(0, 55), 0, 150)
                pygame.draw.circle(bullet_surface, flame_color, (flame_x, flame_y), flame_size)
            
            bullet = Bullet(self.config, self.x + offset_x, self.y + offset_y)
            bullet.image = bullet_surface
            bullet.vel_x = -7 - random.random() * 3  # 略微提高速度
            bullet.vel_y = -3 + random.random() * 6
            bullet.damage = 3  # 增加伤害
            bullet.color = (255, 100, 0)
            
            self.bullets.append(bullet)
            
            # 播放发射音效
            self.config.sounds.swoosh.play()
    
    def speedy_ultimate(self):
        """速度型Boss的大招：闪电风暴"""
        # 每4帧发射一道闪电(增加频率)
        if self.ultimate_duration % 4 == 0:
            # 从Boss周围发射多个闪电
            for i in range(4):  # 增加闪电数量
                start_x = self.x + random.randint(0, self.base_size)
                start_y = self.y + random.randint(0, self.base_size)
                
                # 目标位置朝左侧
                target_x = -20 + random.randint(-100, 100)
                target_y = random.randint(50, self.config.window.height - 50)
                
                # 计算方向向量
                dx = target_x - start_x
                dy = target_y - start_y
                length = math.sqrt(dx * dx + dy * dy)
                dx /= length
                dy /= length
                
                # 添加扭曲效果，每隔一段距离改变一次方向
                zigzag_points = []
                zigzag_points.append((start_x, start_y))
                
                # 闪电段数
                segments = 5 + random.randint(0, 3)
                segment_length = length / segments
                
                current_x = start_x
                current_y = start_y
                
                for j in range(segments):
                    # 添加随机偏移
                    offset = 10 + random.random() * 20
                    if random.random() > 0.5:
                        offset = -offset
                        
                    # 添加垂直于方向的偏移
                    perp_x = -dy * offset
                    perp_y = dx * offset
                    
                    next_x = current_x + dx * segment_length + perp_x
                    next_y = current_y + dy * segment_length + perp_y
                    
                    zigzag_points.append((next_x, next_y))
                    
                    current_x = next_x
                    current_y = next_y
                
                # 创建闪电子弹
                bullet = Bullet(self.config, start_x, start_y)
                bullet.target_x = target_x
                bullet.target_y = target_y
                bullet.zigzag_points = zigzag_points
                bullet.width = 3 + random.random() * 2  # 增加闪电宽度
                bullet.vel_x = -14 - random.random() * 6  # 增加速度
                bullet.vel_y = -3 + random.random() * 6
                bullet.damage = 2  # 增加伤害
                bullet.color = (30, 180, 255)  # 更亮的蓝色
                bullet.is_lightning = True
                
                self.bullets.append(bullet)
            
            # 播放闪电音效
            self.config.sounds.point.play()
    
    def splitter_ultimate(self):
        """分裂型Boss的大招：分裂爆炸"""
        # 在大招开始时释放大量分裂子弹
        if self.ultimate_duration == 60:  # 只在开始时释放一次
            num_bullets = 16  # 增加子弹数量
            for i in range(num_bullets):
                angle = 2 * math.pi * i / num_bullets
                
                # 创建更大的分裂子弹
                bullet_surface = pygame.Surface((18, 18), pygame.SRCALPHA)
                pygame.draw.circle(bullet_surface, (0, 255, 0), (9, 9), 9)
                
                # 从Boss中心发射
                bullet = Bullet(self.config, self.x + self.base_size // 2, self.y + self.base_size // 2)
                bullet.image = bullet_surface
                bullet.vel_x = math.cos(angle) * 6  # 增加速度
                bullet.vel_y = math.sin(angle) * 6
                bullet.damage = 2  # 增加伤害
                bullet.color = (0, 255, 0)
                bullet.is_splitter = True
                bullet.split_time = 25  # 缩短分裂时间
                bullet.parent = self
                
                self.bullets.append(bullet)
                
            # 播放爆炸音效
            self.config.sounds.hit.play()
    
    def tank_ultimate(self):
        """坦克型Boss的大招：能量冲击波"""
        # 每25帧释放一次冲击波
        if self.ultimate_duration % 25 == 0:
            # 创建冲击波子弹
            bullet_surface = pygame.Surface((50, 50), pygame.SRCALPHA)  # 增大尺寸
            
            # 绘制紫色能量球
            pygame.draw.circle(bullet_surface, (128, 0, 128, 200), (25, 25), 25)
            
            # 添加能量环效果
            for i in range(4):  # 增加环数
                ring_radius = 6 + i * 6
                pygame.draw.circle(bullet_surface, (220, 120, 255, 150), (25, 25), ring_radius, 2)
            
            bullet = Bullet(self.config, self.x, self.y + self.base_size // 2 - 25)
            bullet.image = bullet_surface
            bullet.vel_x = -4  # 降低速度，因为威力大
            bullet.vel_y = 0
            bullet.damage = 5  # 大幅增加伤害
            bullet.color = (150, 0, 150)
            
            self.bullets.append(bullet)
            
            # 播放能量冲击波音效
            self.config.sounds.swoosh.play()
    
    def take_damage(self, damage: int) -> None:
        """Boss受到伤害"""
        self.health -= damage
        self.hit_flash = 5  # 设置闪烁帧数
        
        # 增加怒气值，根据Boss类型有不同增加速度
        self.rage += self.rage_gain_on_hit
        
        # 当Boss血量低于一半时，怒气获取更快
        if self.health < self.max_health * 0.5:
            self.rage += self.rage_gain_on_hit * 0.5  # 额外50%怒气
        
        # 播放受击声音
        self.config.sounds.hit.play()
        
        # 坦克Boss在低血量时受到的伤害减半
        if self.boss_type == BossType.TANK and self.health < self.max_health * 0.5:
            self.health += damage // 2  # 恢复一半伤害
        
        # 确保生命值不为负
        if self.health < 0:
            self.health = 0
            
        # 创建伤害数值显示
        # 在Boss身体上随机位置显示，增加一些随机性
        x_offset = random.randint(-int(self.base_size * 0.3), int(self.base_size * 0.3))
        y_offset = random.randint(-int(self.base_size * 0.3), int(self.base_size * 0.3))
        
        # 根据伤害值选择颜色
        if damage >= 5:
            color = (255, 50, 50)  # 大伤害红色
        elif damage >= 3:
            color = (255, 255, 0)  # 中等伤害黄色
        else:
            color = (255, 255, 255)  # 普通伤害白色
            
        # 添加到伤害文本列表
        damage_text = DamageText(
            self.config, 
            self.x + self.base_size // 2 + x_offset, 
            self.y + self.base_size // 2 + y_offset,
            damage,
            color
        )
        self.damage_texts.append(damage_text)
    
    def is_defeated(self) -> bool:
        """检查Boss是否被击败"""
        # 不再输出调试信息
        if self.health <= 0:
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
        
        # 添加文字和Boss类型 - 使用默认字体避免乱码
        try:
            # 尝试使用Arial字体 - 几乎所有Windows系统都有
            font = pygame.font.SysFont('Arial', 16)
            # 显示简化的文本
            text = font.render(f"HP: {self.health}/{self.max_health}", True, (255, 255, 255))
        except:
            # 如果失败，使用系统默认字体
            font = pygame.font.Font(None, 16)
            text = font.render(f"HP: {self.health}/{self.max_health}", True, (255, 255, 255))
            
        text_rect = text.get_rect(center=(x + bar_width // 2, y + bar_height // 2))
        self.config.screen.blit(text, text_rect)
    
    def update_bullets(self):
        """更新并绘制Boss的子弹"""
        for bullet in list(self.bullets):
            bullet.tick()
            # 移除超出屏幕的子弹
            if bullet.is_out_of_screen():
                self.bullets.remove(bullet) 
    
    def update_damage_texts(self):
        """更新并绘制伤害文本"""
        # 保存仍然存活的伤害文本
        active_texts = []
        
        # 更新并绘制每个伤害文本
        for damage_text in self.damage_texts:
            if damage_text.tick():  # 如果文本仍然存活
                active_texts.append(damage_text)
        
        # 更新伤害文本列表
        self.damage_texts = active_texts 

    def draw_ultimate_warning(self):
        """绘制大招释放警告"""
        # 创建警告闪烁效果
        pulse = (math.sin(pygame.time.get_ticks() / 100) + 1) / 2  # 0到1的脉动
        warning_alpha = int(100 + 155 * pulse)  # 闪烁透明度
        
        # 根据Boss类型选择警告颜色
        if self.boss_type == BossType.NORMAL:
            warning_color = (255, 100, 0, warning_alpha)  # 橙红色
        elif self.boss_type == BossType.SPEEDY:
            warning_color = (0, 150, 255, warning_alpha)  # 蓝色
        elif self.boss_type == BossType.SPLITTER:
            warning_color = (0, 255, 0, warning_alpha)  # 绿色
        elif self.boss_type == BossType.TANK:
            warning_color = (128, 0, 128, warning_alpha)  # 紫色
        
        # 创建圆形光环
        radius = self.base_size * 0.8 + pulse * 10  # 脉动半径
        glow_surface = pygame.Surface((int(radius*2), int(radius*2)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, warning_color, 
                          (int(radius), int(radius)), int(radius), 4)
        
        # 绘制到Boss周围
        glow_rect = glow_surface.get_rect(center=(self.x + self.base_size//2, 
                                                 self.y + self.base_size//2))
        self.config.screen.blit(glow_surface, glow_rect)
        
        # 绘制警告文本
        try:
            warning_font = pygame.font.SysFont('SimHei', 22, bold=True)
        except:
            warning_font = pygame.font.Font(None, 22)
            
        # 根据Boss类型显示不同的警告文本
        if self.boss_type == BossType.NORMAL:
            warning_text = "火焰爆发!"
        elif self.boss_type == BossType.SPEEDY:
            warning_text = "闪电风暴!"
        elif self.boss_type == BossType.SPLITTER:
            warning_text = "分裂爆炸!"
        elif self.boss_type == BossType.TANK:
            warning_text = "能量冲击!"
            
        text_surface = warning_font.render(warning_text, True, warning_color[:3])
        text_rect = text_surface.get_rect(center=(self.x + self.base_size//2, 
                                                self.y - 30))
        self.config.screen.blit(text_surface, text_rect) 