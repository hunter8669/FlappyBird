from enum import Enum
from itertools import cycle
from typing import List

import pygame

from ..utils import GameConfig, clamp
from .entity import Entity
from .floor import Floor
from .pipe import Pipe, Pipes
from .powerup import PowerUpType
from .bullet import Bullet


class PlayerMode(Enum):
    """玩家模式枚举"""
    NORMAL = "NORMAL"  # 正常模式
    SHM = "SHM"  # 静止模式
    CRASH = "CRASH"  # 撞击模式
    CRASHED = "CRASHED"  # 撞击模式
    REVERSE = "REVERSE"  # 反向模式
    BOSS = "BOSS"  # Boss模式


class Player(Entity):
    def __init__(self, config: GameConfig) -> None:
        image = config.images.player[0]
        x = int(config.window.width * 0.2)
        y = int((config.window.height - image.get_height()) / 2)
        super().__init__(config, image, x, y)
        self.min_y = -2 * self.h
        self.max_y = config.window.viewport_height - self.h * 0.75
        self.img_idx = 0
        self.img_gen = cycle([0, 1, 2, 1])
        self.frame = 0
        self.crashed = False
        self.crash_entity = None
        # 道具效果相关属性
        self.speed_modifier = 1.0  # 速度修改器
        self.invincible = False    # 无敌状态
        self.size_modifier = 1.0   # 大小修改器
        self.original_image = None # 保存原始图像
        self.is_reverse_mode = False  # 是否为反向模式
        
        # 子弹相关
        self.bullets: List[Bullet] = []  # 玩家发射的子弹
        self.bullet_cooldown = 0  # 子弹冷却时间
        self.bullet_rate = 20  # 多少帧发射一次子弹
        self.bullet_damage = 10  # 子弹伤害
        
        self.set_mode(PlayerMode.SHM)
        
    def apply_powerup_effect(self, powerup_type: PowerUpType) -> None:
        """应用道具效果"""
        if powerup_type == PowerUpType.SPEED_BOOST:
            self.speed_modifier = 1.5
        elif powerup_type == PowerUpType.INVINCIBLE:
            self.invincible = True
        elif powerup_type == PowerUpType.SLOW_MOTION:
            self.speed_modifier = 0.5
        elif powerup_type == PowerUpType.SMALL_SIZE:
            # 缩小玩家
            if self.size_modifier == 1.0:
                self.original_image = self.image
                self.size_modifier = 0.6
                self._resize_player()
    
    def remove_powerup_effect(self, powerup_type: PowerUpType) -> None:
        """移除道具效果"""
        if powerup_type == PowerUpType.SPEED_BOOST or powerup_type == PowerUpType.SLOW_MOTION:
            self.speed_modifier = 1.0
        elif powerup_type == PowerUpType.INVINCIBLE:
            self.invincible = False
        elif powerup_type == PowerUpType.SMALL_SIZE:
            if self.original_image:
                self.size_modifier = 1.0
                self.image = self.original_image
                self.w = self.image.get_width()
                self.h = self.image.get_height()
                self.original_image = None
    
    def _resize_player(self) -> None:
        """根据size_modifier调整玩家大小"""
        if self.size_modifier != 1.0:
            new_width = int(self.image.get_width() * self.size_modifier)
            new_height = int(self.image.get_height() * self.size_modifier)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
            self.w = self.image.get_width()
            self.h = self.image.get_height()

    def set_mode(self, mode: PlayerMode) -> None:
        self.mode = mode
        if mode == PlayerMode.NORMAL:
            self.reset_vals_normal()
            self.config.sounds.wing.play()
        elif mode == PlayerMode.SHM:
            self.reset_vals_shm()
        elif mode == PlayerMode.REVERSE:
            self.reset_vals_reverse()
            self.config.sounds.wing.play()
        elif mode == PlayerMode.BOSS:
            self.reset_vals_boss()
            self.config.sounds.wing.play()
        elif mode == PlayerMode.CRASH:
            self.stop_wings()
            self.config.sounds.hit.play()
            if self.crash_entity == "pipe":
                self.config.sounds.die.play()
            self.reset_vals_crash()

    def reset_vals_normal(self) -> None:
        self.vel_y = -9  # player's velocity along Y axis
        self.max_vel_y = 10  # max vel along Y, max descend speed
        self.min_vel_y = -8  # min vel along Y, max ascend speed
        self.acc_y = 1  # players downward acceleration

        self.rot = 80  # player's current rotation
        self.vel_rot = -3  # player's rotation speed
        self.rot_min = -90  # player's min rotation angle
        self.rot_max = 20  # player's max rotation angle

        self.flap_acc = -9  # players speed on flapping
        self.flapped = False  # True when player flaps
        
    def reset_vals_reverse(self) -> None:
        # 反向模式下的初始化值
        self.vel_y = 9  # 反向的初始速度（向下）
        self.max_vel_y = 8  # 反向模式下的最大上升速度（实际是下降）
        self.min_vel_y = -10  # 反向模式下的最小下降速度（实际是上升）
        self.acc_y = -1  # 反向的重力加速度（向上）

        self.rot = -80  # 反向的初始旋转角度
        self.vel_rot = 3  # 反向的旋转速度
        self.rot_min = -20  # 反向的最小旋转角度
        self.rot_max = 90  # 反向的最大旋转角度

        self.flap_acc = 9  # 反向的拍打加速度
        self.flapped = False  # 拍打状态
        
    def reset_vals_boss(self) -> None:
        """设置Boss模式下的值"""
        # 与正常模式类似但速度较慢
        self.vel_y = -6  # 初始速度
        self.max_vel_y = 8  # 最大下降速度
        self.min_vel_y = -6  # 最小上升速度
        self.acc_y = 0.8  # 重力加速度

        self.rot = 60  # 初始旋转角度
        self.vel_rot = -2  # 旋转速度
        self.rot_min = -60  # 最小旋转角度
        self.rot_max = 15  # 最大旋转角度

        self.flap_acc = -7  # 拍打加速度
        self.flapped = False  # 拍打状态
        
        # 重置子弹
        self.bullets = []
        self.bullet_cooldown = 0

    def reset_vals_shm(self) -> None:
        self.vel_y = 1  # player's velocity along Y axis
        self.max_vel_y = 4  # max vel along Y, max descend speed
        self.min_vel_y = -4  # min vel along Y, max ascend speed
        self.acc_y = 0.5  # players downward acceleration

        self.rot = 0  # player's current rotation
        self.vel_rot = 0  # player's rotation speed
        self.rot_min = 0  # player's min rotation angle
        self.rot_max = 0  # player's max rotation angle

        self.flap_acc = 0  # players speed on flapping
        self.flapped = False  # True when player flaps

    def reset_vals_crash(self) -> None:
        self.acc_y = 2
        self.vel_y = 7
        self.max_vel_y = 15
        self.vel_rot = -8

    def update_image(self):
        self.frame += 1
        if self.frame % 5 == 0:
            self.img_idx = next(self.img_gen)
            orig_image = self.config.images.player[self.img_idx]
            
            # 应用大小修改
            if self.size_modifier != 1.0:
                new_width = int(orig_image.get_width() * self.size_modifier)
                new_height = int(orig_image.get_height() * self.size_modifier)
                self.image = pygame.transform.scale(orig_image, (new_width, new_height))
            else:
                self.image = orig_image
                
            self.w = self.image.get_width()
            self.h = self.image.get_height()

    def tick_shm(self) -> None:
        if self.vel_y >= self.max_vel_y or self.vel_y <= self.min_vel_y:
            self.acc_y *= -1
        self.vel_y += self.acc_y
        self.y += self.vel_y

    def tick_normal(self) -> None:
        if self.vel_y < self.max_vel_y and not self.flapped:
            self.vel_y += self.acc_y
        if self.flapped:
            self.flapped = False

        # 应用速度修改器
        adjusted_vel_y = self.vel_y * self.speed_modifier
        self.y = clamp(self.y + adjusted_vel_y, self.min_y, self.max_y)
        self.rotate()
        
    def tick_reverse(self) -> None:
        # 反向模式的移动逻辑
        if self.vel_y > self.min_vel_y and not self.flapped:
            self.vel_y += self.acc_y  # 注意这里acc_y是负值，所以是减速
        if self.flapped:
            self.flapped = False

        # 应用速度修改器
        adjusted_vel_y = self.vel_y * self.speed_modifier
        self.y = clamp(self.y + adjusted_vel_y, self.min_y, self.max_y)
        self.rotate()
        
    def tick_boss(self) -> None:
        """Boss模式的更新逻辑"""
        # 类似正常模式的移动
        if self.vel_y < self.max_vel_y and not self.flapped:
            self.vel_y += self.acc_y
        if self.flapped:
            self.flapped = False

        # 应用速度修改器
        adjusted_vel_y = self.vel_y * self.speed_modifier
        self.y = clamp(self.y + adjusted_vel_y, self.min_y, self.max_y)
        self.rotate()
        
        # 更新子弹冷却时间
        self.bullet_cooldown += 1
        
        # 更新并绘制子弹
        for bullet in list(self.bullets):
            bullet.tick()
            # 移除超出屏幕的子弹
            if bullet.is_out_of_screen():
                self.bullets.remove(bullet)

    def tick_crash(self) -> None:
        if self.min_y <= self.y <= self.max_y:
            self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
            # rotate only when it's a pipe crash and bird is still falling
            if self.crash_entity != "floor":
                self.rotate()

        # player velocity change
        if self.vel_y < 15:
            self.vel_y += self.acc_y

    def rotate(self) -> None:
        self.rot = clamp(self.rot + self.vel_rot, self.rot_min, self.rot_max)

    def draw(self) -> None:
        self.update_image()
        if self.mode == PlayerMode.SHM:
            self.tick_shm()
        elif self.mode == PlayerMode.NORMAL:
            self.tick_normal()
        elif self.mode == PlayerMode.REVERSE:
            self.tick_reverse()
        elif self.mode == PlayerMode.BOSS:
            self.tick_boss()
        elif self.mode == PlayerMode.CRASH:
            self.tick_crash()
        
        self.draw_player()

    def draw_player(self) -> None:
        # Rotate bird for normal mode bird and crashed bird (in air)
        if (
            self.mode == PlayerMode.NORMAL
            or self.mode == PlayerMode.REVERSE
            or self.mode == PlayerMode.BOSS
            or (self.mode == PlayerMode.CRASH and self.y < self.max_y - 30)
        ):
            rotation = self.rot if self.mode != PlayerMode.REVERSE else -self.rot
            # pygame.transform.rotate rotates clockwise (opposite of what we want)
            img = pygame.transform.rotate(self.image, rotation)
            rotated_rect = img.get_rect(center=(self.x + self.w // 2, self.y + self.h // 2))
            self.config.screen.blit(img, rotated_rect)
        # For crashed bird on ground or message bird
        else:
            self.config.screen.blit(self.image, (self.x, self.y))
    
    def shoot(self) -> None:
        """玩家发射子弹"""
        # 检查是否可以发射子弹
        if self.bullet_cooldown < self.bullet_rate:
            return
            
        # 重置冷却时间
        self.bullet_cooldown = 0
        
        # 从玩家位置发射子弹
        bullet_x = self.x + self.w
        bullet_y = self.y + self.h // 2 - 4  # 稍微调整位置使其从鸟嘴部发射
        
        # 创建子弹
        bullet = Bullet(self.config, bullet_x, bullet_y)
        self.bullets.append(bullet)
        
        # 播放声音效果
        self.config.sounds.swoosh.play()

    def stop_wings(self) -> None:
        self.img_gen = cycle([0])

    def flap(self) -> None:
        if self.mode != PlayerMode.CRASH:
            if self.mode == PlayerMode.REVERSE:
                # 反向模式下的拍打
                self.vel_y = self.flap_acc
            else:
                # 正常模式或Boss模式下的拍打
                self.vel_y = self.flap_acc
            
            self.flapped = True
            # 重置旋转值
            if self.mode == PlayerMode.NORMAL or self.mode == PlayerMode.BOSS:
                self.rot = 80
            elif self.mode == PlayerMode.REVERSE:
                self.rot = -80

    def crossed(self, pipe: Pipe) -> bool:
        return pipe.x < self.x < pipe.x + pipe.w

    def collided(self, pipes: Pipes, floor: Floor) -> bool:
        """检查是否与管道或地板发生碰撞"""
        if (
            self.y + self.h >= floor.y - 1  # bird on floor
            or self.y < 0  # bird above viewport
        ):
            self.crash_entity = "floor"
            return True

        for pipe in pipes.upper + pipes.lower:
            if self.collide(pipe):
                self.crash_entity = "pipe"
                return True

        return False
        
    def check_boss_bullet_collision(self, boss) -> bool:
        """检查是否与Boss的子弹碰撞"""
        for bullet in list(boss.bullets):
            if self.collide(bullet):
                boss.bullets.remove(bullet)
                if not self.invincible:
                    return True
        return False
        
    def check_bullet_hit_boss(self, boss) -> None:
        """检查玩家的子弹是否击中Boss"""
        for bullet in list(self.bullets):
            if bullet.collide(boss):
                self.bullets.remove(bullet)
                boss.take_damage(self.bullet_damage)
                return True
        return False
