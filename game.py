import pygame
import sys
from pygame.locals import QUIT
import random
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT
pygame.init()


FPS = 60
FramePerSec = pygame.time.Clock()

screen_width = 800
screen_height = 800

display = pygame.display.set_mode((screen_width, screen_height))
display.fill((255, 255, 255))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        img = pygame.image.load("player.png").convert_alpha()
        w, h = img.get_size()
        self.image = pygame.transform.smoothscale(img, (w // 5, h // 5))
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height - 120)
 
    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-10, 0)
        if pressed_keys[K_RIGHT] and self.rect.right < screen_width:
            self.rect.move_ip(10, 0)
        #if pressed_keys[K_UP] and self.rect.top > 0:
          #  self.rect.move_ip(0, -5)
        #if pressed_keys[K_DOWN] and self.rect.bottom < screen_height:
          # self.rect.move_ip(0, 5)
 
    def draw(self, surface):
        surface.blit(self.image, self.rect)   

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        img = pygame.image.load("enemy.png").convert_alpha()
        w, h = img.get_size()
        self.image = pygame.transform.smoothscale(img, (w // 5, h // 5))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, screen_width - 40), 0)
        self.speed = random.randint(5, 20)
 
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > screen_height:
            self.rect.center = (random.randint(40, screen_width - 40), 0)
            self.speed = random.randint(5, 20)
 
    def draw(self, surface):
        surface.blit(self.image, self.rect)

P1 = Player()
enemies = pygame.sprite.Group()
for _ in range(6):
    enemies.add(Enemy())

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    P1.update()
    enemies.update()
    display.fill((255, 255, 255))
    P1.draw(display)
    enemies.draw(display)
    
    pygame.display.update()
    FramePerSec.tick(FPS)
    
    
    
    
    