import pygame
import sys
from pygame.locals import QUIT
import random
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_d, K_a, K_SPACE


pygame.init()


FPS = 60
FramePerSec = pygame.time.Clock()

level = 1
score = 100
health = 100
speed = 10
reload_speed = 500  # milliseconds between shots
DAMAGE_PER_HIT = 1
GAME= "game"
DASHBOARD= "dashboard"
state = DASHBOARD


screen_width = 800
screen_height = 800

display = pygame.display.set_mode((screen_width, screen_height))
display.fill((0, 0, 0))
font = pygame.font.SysFont(None, 36)
level = 1
level_start_ticks = pygame.time.get_ticks()
LEVEL_UP_INTERVAL = 2000  # milliseconds (20 seconds)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        img = pygame.image.load("player.png").convert_alpha()
        w, h = img.get_size()
        self.image = pygame.transform.smoothscale(img, (w // 5, h // 5))
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height - 120)
        # smaller collision hitbox (keeps visual rect but uses a reduced box for collisions)
        self.hitbox = self.rect.inflate(-40, -40)
 
    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if (pressed_keys[K_LEFT] or pressed_keys[K_a]) and self.rect.left > 0:
            self.rect.move_ip(-speed, 0)
        if (pressed_keys[K_RIGHT] or pressed_keys[K_d]) and self.rect.right < screen_width:
            self.rect.move_ip(speed, 0)
        # optional vertical movement (disabled):
        # if pressed_keys[K_UP] and self.rect.top > 0:
        #     self.rect.move_ip(0, -5)
        # keep hitbox centered on the player
        self.hitbox.center = self.rect.center
            
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
        # give enemies a health value so bullets can deal damage
        self.health = 20 + level * 2
 
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > screen_height:
            # enemy reached bottom: deduct player health and respawn enemy
            global health
            health -= DAMAGE_PER_HIT
            self.rect.center = (random.randint(40, screen_width - 40), 0)
            self.speed = random.randint(5, int(level * 1.5 + 4))
 
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Button_Dashboard:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, (180, 180, 180), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        txt = font.render(self.text, True, (0, 0, 0))
        surface.blit(txt, (
            self.rect.centerx - txt.get_width() // 2,
            self.rect.centery - txt.get_height() // 2
        ))
    
    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

def spawn_enemies(group, count):
    for _ in range(int(count)):
        group.add(Enemy())

class Speed_Upgrade:
    def __init__(self, x, y, w, h, text, cost):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.cost = cost
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, (180, 180, 180), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        txt = font.render(self.text, True, (0, 0, 0))
        surface.blit(txt, (
            self.rect.centerx - txt.get_width() // 2,
            self.rect.centery - txt.get_height() // 2
        ))
    
    def clicked(self, event):
        global speed, score
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if score >= self.cost:
                speed += 5
                score -= self.cost
                return True
        return False

class Damage_Upgrade:
    def __init__(self, x, y, w, h, text, cost):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.cost = cost
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, (180, 180, 180), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        txt = font.render(self.text, True, (0, 0, 0))
        surface.blit(txt, (
            self.rect.centerx - txt.get_width() // 2,
            self.rect.centery - txt.get_height() // 2
        ))
    
    def clicked(self, event):
        global DAMAGE_PER_HIT, score
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if score >= self.cost:
                DAMAGE_PER_HIT += 5
                score -= self.cost
                return True
        return False
    
class Button_Game:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, (180, 180, 180), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        txt = font.render(self.text, True, (0, 0, 0))
        surface.blit(txt, (
            self.rect.centerx - txt.get_width() // 2,
            self.rect.centery - txt.get_height() // 2
        ))
    
    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class Reload_Upgrade:
    def __init__(self, x, y, w, h, text, cost):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.cost = cost
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, (180, 180, 180), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        txt = font.render(self.text, True, (0, 0, 0))
        surface.blit(txt, (
            self.rect.centerx - txt.get_width() // 2,
            self.rect.centery - txt.get_height() // 2
        ))
    
    def clicked(self, event):
        global reload_speed, score
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if score >= self.cost:
                reload_speed -= 45
                score -= self.cost
                return True
        return False

P1 = Player()
enemies = pygame.sprite.Group()
spawn_enemies(enemies, (level + 1) // 2)

dashboard_button = Button_Dashboard(
    x=620,
    y=10,
    w=160,
    h=40,
    text="Dashboard"
)

game_button = Button_Game(
    x=620,
    y=10,
    w=160,
    h=40,
    text="Back to Game"
)

upgrade_speed_button = Speed_Upgrade(
    x=50,
    y=300,
    w=350,
    h=50,
    text="Upgrade Speed (10 points)",
    cost=10
)

upgrade_damage_button = Damage_Upgrade(
    x=425,
    y=300,
    w=350,
    h=50,
    text="Upgrade Damage (10 points)",
    cost=10
)

upgrade_reload_button = Reload_Upgrade(
    x=50,
    y=400,
    w=350,
    h=50,
    text="Upgrade Reload Speed (10 points)",
    cost=10
)


# Shooting / bullets
last_shot_time = 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, damage):
        super().__init__()
        self.image = pygame.Surface((6, 12))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(midbottom=pos)
        self.speed = -15
        self.damage = damage

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom < 0:
            self.kill()


bullets = pygame.sprite.Group()


def player_enemy_collide(player, enemy):
    # use the player's smaller hitbox for collision checks
    return player.hitbox.colliderect(enemy.rect)


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # handle clicks and other event-time logic per state
        if state == GAME:
            if dashboard_button.clicked(event):
                state = DASHBOARD
            # shooting: spacebar fires if reload timer allows
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                now = pygame.time.get_ticks()
                if now - last_shot_time >= reload_speed:
                    bullets.add(Bullet(P1.rect.midtop, DAMAGE_PER_HIT))
                    last_shot_time = now
        elif state == DASHBOARD:
            # process upgrade button clicks while in dashboard
            if upgrade_speed_button.clicked(event):
                pass
            if upgrade_damage_button.clicked(event):
                pass
            if upgrade_reload_button.clicked(event):
                pass
            if game_button.clicked(event):
                state = GAME

    if state == GAME:    
        P1.update()
        enemies.update()
        bullets.update()
        # bullets vs enemies: bullets deal damage, enemies die when health <= 0
        collisions = pygame.sprite.groupcollide(bullets, enemies, True, False)
        for bullet, hit_enemies in collisions.items():
            for enemy in hit_enemies:
                enemy.health -= bullet.damage
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    score += 50

            # player collisions: do not remove enemies on player contact
        collided = pygame.sprite.spritecollide(P1, enemies, dokill=False, collided=player_enemy_collide)
        if collided:
            # touching enemies no longer costs health
            pass
        display.fill((0, 0, 0))
        P1.draw(display)
        enemies.draw(display)
        bullets.draw(display)

        # dashboard_button click is handled in the event loop now

        # Level timer: increase level every 10 seconds
        now = pygame.time.get_ticks()
        if now - level_start_ticks >= LEVEL_UP_INTERVAL:
            level += 1
            level_start_ticks = now
            # make enemies a bit faster each level
            for e in enemies:
                e.speed += 1
            # spawn enemies so total equals ceil(level/2)
            desired = (level + 1) // 2
            needed = desired - len(enemies)
            if needed > 0:
                spawn_enemies(enemies, needed)

        # draw level on screen
        level_surf = font.render(f'Level: {level}', True, (255, 255, 255))
        health_surf = font.render(f'Health: {health}', True, (255, 255, 255))
        display.blit(level_surf, (10, 10))
        display.blit(health_surf, (10, 50))

        # show reload speed in ms
        reload_surf = font.render(f'Reload: {reload_speed} ms', True, (255, 255, 255))
        display.blit(reload_surf, (10, 80))

        # draw health
        health_surf = font.render(f'Health: {health}', True, (200, 0, 0))
        display.blit(health_surf, (10, 40))

        dashboard_button.draw(display)

        # game over if health depleted
        if health <= 0:
            over_surf = font.render('Game Over', True, (255, 0, 0))
            display.blit(over_surf, (screen_width//2 - over_surf.get_width()//2, screen_height//2))
            pygame.display.update()
            pygame.time.wait(2000)
            sys.exit()

        if level % 5 == 1 and level > 1:
            state = DASHBOARD

    elif state == DASHBOARD:
        display.fill((220, 220, 220))
        title = font.render("UPGRADE DASHBOARD", True, (0,0,0))
        display.blit(title, (screen_width//2 - title.get_width()//2, 150))

        display.blit(font.render(f"Upgrade Points: {score}", True, (0,0,0)), (10,10))
        upgrade_speed_button.draw(display)
        upgrade_damage_button.draw(display)
        game_button.draw(display)
        upgrade_reload_button.draw(display)


    pygame.display.update()
    FramePerSec.tick(FPS)
    
    
    
    
    