import pygame

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
        
        # 初始化实体
        super().__init__(config, surface, x, y)
    
    def draw(self) -> None:
        self.x += self.vel_x  # 更新位置
        super().draw()  # 调用父类绘制方法
        
    def is_out_of_screen(self) -> bool:
        """检查子弹是否超出屏幕范围"""
        return self.x > self.config.window.width
