import pygame
import sys
from pygame.locals import QUIT
import random
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_d, K_a


pygame.init()


FPS = 60
FramePerSec = pygame.time.Clock()

level = 1
score = 0
health = 100
DAMAGE_PER_HIT = 10


screen_width = 800
screen_height = 800

display = pygame.display.set_mode((screen_width, screen_height))
display.fill((255, 255, 255))
font = pygame.font.SysFont(None, 36)
level = 1
level_start_ticks = pygame.time.get_ticks()
LEVEL_UP_INTERVAL = 10000  # milliseconds (20 seconds)

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
        if (pressed_keys[K_LEFT] or pressed_keys[K_a]) and self.rect.left > 0:
            self.rect.move_ip(-10, 0)
        if (pressed_keys[K_RIGHT] or pressed_keys[K_d]) and self.rect.right < screen_width:
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
        self.speed = random.randint(5, int(level * 1.5 + 4))
 
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > screen_height:
            self.rect.center = (random.randint(40, screen_width - 40), 0)
            self.speed = random.randint(5, int(level * 1.5 + 4))
 
    def draw(self, surface):
        surface.blit(self.image, self.rect)

def spawn_enemies(group, count):
    for _ in range(int(count)):
        group.add(Enemy())

P1 = Player()
enemies = pygame.sprite.Group()
spawn_enemies(enemies, level)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    P1.update()
    enemies.update()
    # handle collisions: remove colliding enemies and reduce player health
    collided = pygame.sprite.spritecollide(P1, enemies, dokill=True)
    if collided:
        health -= DAMAGE_PER_HIT * len(collided)
        if health < 0:
            sys.exit()
    display.fill((255, 255, 255))
    P1.draw(display)
    enemies.draw(display)

    # Level timer: increase level every 10 seconds
    now = pygame.time.get_ticks()
    if now - level_start_ticks >= LEVEL_UP_INTERVAL:
        level += 1
        level_start_ticks = now
        # make enemies a bit faster each level
        for e in enemies:
            e.speed += 1
        # spawn additional enemies so total equals current level
        needed = level - len(enemies)
        if needed > 0:
            spawn_enemies(enemies, needed)

    # draw level on screen
    level_surf = font.render(f'Level: {level}', True, (0, 0, 0))
    health_surf = font.render(f'Health: {health}', True, (0, 0, 0))
    display.blit(level_surf, (10, 10))
    display.blit(health_surf, (10, 50))

    # draw health
    health_surf = font.render(f'Health: {health}', True, (200, 0, 0))
    display.blit(health_surf, (10, 40))

    # game over if health depleted
    if health <= 0:
        over_surf = font.render('Game Over', True, (255, 0, 0))
        display.blit(over_surf, (screen_width//2 - over_surf.get_width()//2, screen_height//2))
        pygame.display.update()
        pygame.time.wait(2000)
        sys.exit()

    if level % 5 == 1 and level > 1:
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)
    
    
    
    
    