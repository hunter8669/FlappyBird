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
from .weapon import Weapon, WeaponType


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
        self.config = config
        images = config.images.player  # 获取玩家图像

        # 根据模式设置当前图像
        x = int(config.window.width * 0.2)
        y = int((config.window.height - images[0].get_height()) / 2)

        super().__init__(config, images[0], x, y)  # 初始化父类

        # 设置碰撞的管道或地板
        self.crash_entity = None

        # 生成用于显示图像的索引
        self.img_gen = self.generate_index()
        next(self.img_gen)  # 初始化索引

        # 速度修改器
        self.speed_modifier = 1.0
        self.size_modifier = 1.0  # 大小修改器
        
        # 子弹
        self.bullets = []
        self.bullet_damage = 10  # 默认伤害值
        self.invincible = False  # 是否无敌
        
        # 武器系统
        self.weapons = [
            Weapon(config, WeaponType.NORMAL),
            Weapon(config, WeaponType.TRIPLE),
            Weapon(config, WeaponType.LASER),
            Weapon(config, WeaponType.HOMING)
        ]
        self.current_weapon_index = 0
        self.bullet_rate = 15  # 子弹发射冷却时间
        self.bullet_cooldown = 0  # 当前冷却计时器
        
        # 爆炸特效
        self.explosions = []
        
        # 添加弹药显示
        self.bullet_ui_pos = (10, config.window.height - 40)

        # 设置值
        self.min_y = -self.h - 10  # 最小y坐标
        self.max_y = config.window.height - 1  # 最大y坐标

        self.mode = PlayerMode.SHM  # 设置玩家模式为SHM（静止模式）
        # 初始化索引
        self.loopIter = 0
        self.playerIndex = 0

        # player velocity, max velocity, downward acceleration, acceleration on flap
        self.reset_vals_shm()

    def generate_index(self):
        """生成用于循环显示图像的索引"""
        while True:
            for i in cycle([0, 1, 2, 1]):
                yield i

    def set_mode(self, mode: PlayerMode):
        """设置玩家模式"""
        if mode == self.mode:
            return

        # 记忆原始模式
        self.old_mode = self.mode
        self.mode = mode

        # 根据不同的模式设置不同的值
        if mode == PlayerMode.NORMAL:
            self.reset_vals_normal()
        elif mode == PlayerMode.SHM:
            self.reset_vals_shm()
        elif mode == PlayerMode.REVERSE:
            self.reset_vals_reverse()
        elif mode == PlayerMode.BOSS:
            self.reset_vals_boss()
        elif mode == PlayerMode.CRASH:
            self.reset_vals_crash()

    def reset_vals_normal(self) -> None:
        """设置正常模式下的值"""
        self.vel_y = -9  # 初始速度
        self.max_vel_y = 10  # 最大下降速度
        self.min_vel_y = -8  # 最小上升速度
        self.acc_y = 1  # 重力加速度

        self.rot = 60  # 初始旋转角度
        self.vel_rot = -3  # 旋转速度
        self.rot_min = -90  # 最小旋转角度
        self.rot_max = 20  # 最大旋转角度

        self.flap_acc = -9  # 拍打加速度
        self.flapped = False  # 拍打状态

    def reset_vals_reverse(self) -> None:
        """设置反向模式下的值"""
        self.vel_y = 9  # 初始速度
        self.max_vel_y = 8  # 最大下降速度
        self.min_vel_y = -10  # 最小上升速度
        self.acc_y = -1  # 重力加速度

        self.rot = -60  # 初始旋转角度
        self.vel_rot = 3  # 旋转速度
        self.rot_min = -20  # 最小旋转角度
        self.rot_max = 90  # 最大旋转角度

        self.flap_acc = 9  # 拍打加速度
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
        self.boss_target = None  # 存储Boss引用，用于追踪弹
        
        # 重置武器弹药
        for weapon in self.weapons:
            if weapon.weapon_type == WeaponType.NORMAL:
                weapon.ammo = -1  # 无限弹药
            elif weapon.weapon_type == WeaponType.TRIPLE:
                weapon.ammo = 30
            elif weapon.weapon_type == WeaponType.LASER:
                weapon.ammo = 100
            elif weapon.weapon_type == WeaponType.HOMING:
                weapon.ammo = 10

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

    def update_image(self) -> None:
        """更新玩家的图像"""
        size_scale = getattr(self, 'size_modifier', 1.0)
        if size_scale != 1.0:
            # 应用缩放
            idx = next(self.img_gen)
            original_img = self.config.images.player[idx]
            new_width = int(original_img.get_width() * size_scale)
            new_height = int(original_img.get_height() * size_scale)
            self.image = pygame.transform.scale(original_img, (new_width, new_height))
            self.w = new_width
            self.h = new_height
        else:
            # 正常大小
            self.image = self.config.images.player[next(self.img_gen)]
            self.w = self.image.get_width()
            self.h = self.image.get_height()

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
        """反向模式的更新逻辑"""
        if self.vel_y > self.min_vel_y and not self.flapped:
            self.vel_y += self.acc_y
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
        
        # 更新武器冷却时间
        self.update_weapons()
        
        # 更新并绘制子弹
        self.update_bullets()
        
        # 更新爆炸特效
        self.update_explosions()
        
        # 绘制武器UI
        self.draw_weapon_ui()
    
    def update_weapons(self):
        """更新所有武器状态"""
        for weapon in self.weapons:
            weapon.update()
    
    def update_bullets(self):
        """更新并绘制所有子弹"""
        for bullet in list(self.bullets):
            if hasattr(bullet, 'is_homing') and bullet.is_homing:
                # 更新追踪弹的目标
                bullet.target = self.boss_target
                
            bullet.tick()
            # 移除超出屏幕的子弹
            if bullet.is_out_of_screen():
                self.bullets.remove(bullet)
    
    def draw_weapon_ui(self):
        """绘制当前武器信息UI"""
        weapon = self.weapons[self.current_weapon_index]
        
        # 创建武器信息背景
        bg_width = 150
        bg_height = 50
        bg = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        
        self.config.screen.blit(bg, self.bullet_ui_pos)
        
        # 显示武器名称
        font = pygame.font.SysFont('microsoftyahei', 14)
        name_text = font.render(f"武器: {weapon.weapon_type.value}", True, weapon.color)
        self.config.screen.blit(name_text, (self.bullet_ui_pos[0] + 10, self.bullet_ui_pos[1] + 10))
        
        # 显示弹药信息
        ammo_text = "无限" if weapon.ammo < 0 else f"{weapon.ammo}"
        ammo_surface = font.render(f"弹药: {ammo_text}", True, (255, 255, 255))
        self.config.screen.blit(ammo_surface, (self.bullet_ui_pos[0] + 10, self.bullet_ui_pos[1] + 30))
        
        # 显示切换提示
        small_font = pygame.font.SysFont('microsoftyahei', 10)
        hint_text = small_font.render("按Q/E切换武器", True, (200, 200, 200))
        self.config.screen.blit(hint_text, (self.bullet_ui_pos[0] + 10, self.bullet_ui_pos[1] + 45))

    def update_explosions(self):
        """更新并绘制爆炸特效"""
        explosions_to_remove = []
        
        for explosion in self.explosions:
            # 更新帧
            explosion['frame'] += 0.2
            
            # 如果动画结束，标记为删除
            if explosion['frame'] >= explosion['max_frame']:
                explosions_to_remove.append(explosion)
                continue
                
            # 绘制爆炸
            size = explosion['size']
            alpha = 255 * (1 - explosion['frame'] / explosion['max_frame'])
            
            # 创建爆炸表面
            explosion_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(
                explosion_surf, 
                (255, 165, 0, alpha), 
                (size, size), 
                size * (1 - explosion['frame'] / explosion['max_frame'])
            )
            
            # 绘制爆炸
            self.config.screen.blit(
                explosion_surf, 
                (explosion['x'] - size, explosion['y'] - size)
            )
        
        # 移除已完成的爆炸
        for explosion in explosions_to_remove:
            if explosion in self.explosions:
                self.explosions.remove(explosion)

    def tick_shm(self) -> None:
        """有规律地上下移动玩家，用于显示欢迎界面"""
        self.loopIter = (self.loopIter + 1) % 28
        if self.loopIter == 0:
            self.playerIndex = next(self.img_gen)
            self.image = self.config.images.player[self.playerIndex]

        if self.loopIter % 14 == 0:
            self.vel_y = -self.vel_y

        self.y += self.vel_y

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
    
    def switch_weapon(self, direction: int) -> None:
        """切换武器 (1: 下一个, -1: 上一个)"""
        self.current_weapon_index = (self.current_weapon_index + direction) % len(self.weapons)
        
        # 更新子弹伤害值
        self.bullet_damage = self.weapons[self.current_weapon_index].damage
        
        # 播放切换音效
        self.config.sounds.swoosh.play()

    def shoot(self) -> None:
        """玩家发射子弹"""
        weapon = self.weapons[self.current_weapon_index]
        
        if not weapon.can_fire():
            return
            
        # 使用当前武器开火
        new_bullets = weapon.fire(
            self.x + self.w,
            self.y + self.h // 2 - 4,
            target=self.boss_target  # 用于追踪弹
        )
        
        # 添加到子弹列表
        self.bullets.extend(new_bullets)

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
        
    def check_bullet_hit_boss(self, boss):
        """检查子弹是否击中Boss"""
        # 存储Boss引用以便追踪导弹使用
        self.boss_target = boss
        
        if not boss or not self.bullets:
            return False
        
        hit = False
        bullets_to_remove = []
        
        for bullet in self.bullets:
            # 使用对象属性而不是字典访问方式
            bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.image.get_width(), bullet.image.get_height())
            
            if bullet_rect.colliderect(boss.rect):
                # 应用伤害 - 直接使用子弹自身的伤害值
                boss.take_damage(bullet.damage)
                
                # 添加碰撞特效
                if hasattr(self, 'explosions'):
                    explosion = {
                        'x': bullet.x,
                        'y': bullet.y,
                        'frame': 0,
                        'max_frame': 5,
                        'size': 20
                    }
                    self.explosions.append(explosion)
                
                # 标记要移除的子弹
                bullets_to_remove.append(bullet)
                hit = True
        
        # 从列表中移除命中的子弹
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
        
        return hit
