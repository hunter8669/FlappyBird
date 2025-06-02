import asyncio
import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("FlapPy Bird Web Test")
clock = pygame.time.Clock()

async def main():
    running = True
    x, y = 400, 300
    vy = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    vy = -10
        
        # 简单的重力效果
        vy += 0.5
        y += vy
        
        # 边界检查
        if y > 550:
            y = 550
            vy = 0
        if y < 0:
            y = 0
            vy = 0
        
        # 绘制
        screen.fill((135, 206, 235))  # 天蓝色背景
        pygame.draw.circle(screen, (255, 255, 0), (int(x), int(y)), 20)  # 黄色小鸟
        
        # 显示文字
        font = pygame.font.Font(None, 36)
        text = font.render("Press SPACE to jump!", True, (255, 255, 255))
        screen.blit(text, (250, 50))
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main()) 