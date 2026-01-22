import pygame
import sys
from pygame.locals import QUIT
import random
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_d, K_a, K_SPACE, K_p
pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

level = 1
score = 250
health = 100
speed = 10
reload_speed = 500
defense = 10
DAMAGE_PER_HIT = 17.5
GAME= "game"
DASHBOARD= "dashboard"
state = DASHBOARD
jet = "basic"
dashboard_levels = set()
MAX_DIFFICULTY_LEVEL = 30


#Jet Types: Basic, Machine Gun, Laser, Bomber


screen_width = 800
screen_height = 800

display = pygame.display.set_mode((screen_width, screen_height))
display.fill((0, 0, 0))
font = pygame.font.SysFont(None, 36)
level = 1
level_start_ticks = pygame.time.get_ticks()
LEVEL_UP_INTERVAL = 5000  # milliseconds (20 seconds)
last_group_spawn = pygame.time.get_ticks()
BASE_SPAWN_INTERVAL = 5500
MIN_SPAWN_INTERVAL = 3500

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
        # use `speed_current` (set each frame) for temporary speed buffs
        s = globals().get('speed_current', speed)
        if (pressed_keys[K_LEFT] or pressed_keys[K_a]) and self.rect.left > 0:
            self.rect.move_ip(-s, 0)
        if (pressed_keys[K_RIGHT] or pressed_keys[K_d]) and self.rect.right < screen_width:
            self.rect.move_ip(s, 0)
        # optional vertical movement (disabled):
        # if pressed_keys[K_UP] and self.rect.top > 0:
        #     self.rect.move_ip(0, -5)
        # keep hitbox centered on the player
        self.hitbox.center = self.rect.center
            
    def draw(self, surface):
        surface.blit(self.image, self.rect)   

class Enemy(pygame.sprite.Sprite):
    def __init__(self, prototype=False, copy_from=None):
        super().__init__()
        # load image once per instance or copy from another
        if copy_from is not None:
            self.image = copy_from.image.copy()
        else:
            img = pygame.image.load("enemy.png").convert_alpha()
            w, h = img.get_size()
            self.image = pygame.transform.smoothscale(img, (w // 5, h // 5))
        self.rect = self.image.get_rect()
        # prototypes stay off-screen and do not participate
        if prototype:
            self.rect.topleft = (-1000, -1000)
            self.speed = 0
            self.is_prototype = True
        else:
            self.rect.center = (random.randint(40, screen_width - 40), 0)
            self.speed = random.randint(int(level * 0.67), int(level * 1.67))
            self.is_prototype = False
        # give enemies a health value so bullets can deal damage
        self.health = 12 + int(level * 1.2)
        self.speed = random.randint(1, int(level))
        if self.speed > 5:
            self.speed = 5
        self.max_health = self.health

    def clone(self):
        # return a fresh Enemy that copies appearance but is a playable instance
        return Enemy(copy_from=self)
        
    # ensure default flags exist on enemy instances
    is_boss = False
    is_prototype = False

        # default flag for boss identification
        # (kept after clone to ensure attribute exists on instances)
 
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > screen_height:
            # enemy reached bottom: deduct player health and respawn enemy
            global health
            health -= max(2 * 10/defense, (level // 2) *10/defense)
            self.kill()
 
    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Duplicate(pygame.sprite.Sprite):
    """A short-lived duplicate of the player used by the machine-gun ability.
    Follows player's y and stays offset horizontally by `offset_x`.
    """
    def __init__(self, player, offset_x):
        super().__init__()
        # copy player image
        self.image = player.image.copy()
        self.rect = self.image.get_rect()
        self.player = player
        self.offset_x = offset_x
        # position duplicates near player
        self.rect.centerx = max(0, min(player.rect.centerx + offset_x, screen_width))
        self.rect.centery = player.rect.centery
        # duplicate stats are applied dynamically from globals when firing

    def update(self):
        # follow player's y and maintain horizontal offset
        self.rect.centery = self.player.rect.centery
        self.rect.centerx = max(0, min(self.player.rect.centerx + self.offset_x, screen_width))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Boss(Enemy):
    def __init__(self):
        # create boss using enemy image but scaled larger
        super().__init__()
        try:
            img = pygame.image.load("boss.png").convert_alpha()
            w, h = img.get_size()
            self.image = pygame.transform.smoothscale(img, (w // 3, h // 3))
        except Exception:
            # fallback: scale existing image up
            w, h = self.image.get_size()
            self.image = pygame.transform.smoothscale(self.image, (w * 2, h * 2))
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, 0)
        self.speed = 2
        self.health = 500 + level * 25
        self.max_health = self.health
        self.is_boss = True

class Boss_Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load("boss_enemy.png").convert_alpha()
        w, h = img.get_size()
        self.image = pygame.transform.smoothscale(img, (w // 3, h // 3))
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, 0)
        self.speed = 2
        self.health = 100 + (level * 10)
 
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > screen_height:
            global health
            health -= 30 * 10/defense
            self.rect.center = (screen_width // 2, 0)
 
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
        # prefer cloning from a non-interactive prototype if available
        if 'enemy_prototype' in globals() and isinstance(globals().get('enemy_prototype'), Enemy):
            group.add(enemy_prototype.clone())
        else:
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
        global speed, score, BASE_SPEED
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if score >= self.cost and speed < 20:
                prev_cost = self.cost
                score -= prev_cost
                # compute new speed but cap at 20
                new_speed = speed + 2.5
                if new_speed > 20:
                    new_speed = 20
                # if no effective change, refund and don't increase cost
                if new_speed == speed:
                    score += prev_cost
                    return False
                speed = new_speed
                BASE_SPEED = speed
                self.cost += 15
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
                prev_cost = self.cost
                score -= prev_cost
                if jet == "basic":
                    DAMAGE_PER_HIT += 3
                    if DAMAGE_PER_HIT > 45:
                        DAMAGE_PER_HIT = 45
                        score += prev_cost
                    else:
                        self.cost += 15
                        # update base so abilities use new damage
                        globals()['BASE_DAMAGE'] = DAMAGE_PER_HIT
                    return True
                elif jet == "machine gun":
                    DAMAGE_PER_HIT += 2
                    if DAMAGE_PER_HIT > 20:
                        DAMAGE_PER_HIT = 20
                        score += prev_cost
                    else:
                        self.cost += 20
                        globals()['BASE_DAMAGE'] = DAMAGE_PER_HIT
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
                prev_cost = self.cost
                score -= prev_cost
                if jet == "basic":
                    reload_speed -= 45
                    if reload_speed < 100:
                        reload_speed = 100
                        score += prev_cost
                    else:
                        self.cost += 20
                        globals()['BASE_RELOAD_SPEED'] = reload_speed
                    return True
                elif jet == "machine gun":
                    reload_speed -= 35
                    if reload_speed < 30:
                        reload_speed = 30
                        score += prev_cost
                    else:
                        self.cost += 25
                        globals()['BASE_RELOAD_SPEED'] = reload_speed
                    return True
        return False

class Defense_Upgrade:
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
        global defense, score
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if score >= self.cost:
                prev_cost = self.cost
                score -= prev_cost
                defense += 2
                if defense > 30:
                    defense = 30
                    score += prev_cost
                else:
                    self.cost += 20
                return True
        return False

class Machine_Gun_Upgrade:
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
        global reload_speed, DAMAGE_PER_HIT, score, jet
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if not jet == "machine gun":
                if score >= self.cost:
                    prev_cost = self.cost
                    score -= prev_cost
                    jet = "machine gun"
                    reload_speed -= 150
                    DAMAGE_PER_HIT += 5
                    if reload_speed < 30:
                        reload_speed = 30
                    if DAMAGE_PER_HIT > 20:
                        DAMAGE_PER_HIT = 20
                    # keep base values in sync
                    globals()['BASE_RELOAD_SPEED'] = reload_speed
                    globals()['BASE_DAMAGE'] = DAMAGE_PER_HIT
                    return True
        return False

P1 = Player()
enemies = pygame.sprite.Group()
# keep a non-interactive prototype enemy so the "original" can never be killed
enemy_prototype = Enemy(prototype=True)


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
    x=10,
    y=300,
    w=410,
    h=50,
    text="Upgrade Speed (10 points)",
    cost=25
)

upgrade_damage_button = Damage_Upgrade(
    x=425,
    y=300,
    w=410,
    h=50,
    text="Upgrade Damage (10 points)",
    cost=35
)

upgrade_reload_button = Reload_Upgrade(
    x=10,
    y=400,
    w=410,
    h=50,
    text="Upgrade Reload Speed (10 points)",
    cost=50
)

upgrade_defense_button = Defense_Upgrade(
    x=425,
    y=400,
    w=410,
    h=50,
    text="Upgrade Defense (10 points)",
    cost=40
)

Machine_Gun_Upgrade_button = Machine_Gun_Upgrade(
    x=10,
    y=600,
    w=500,
    h=50,
    text="Upgrade to Machine Gun Jet (1000 points)",
    cost=1000
)


# Shooting / bullets
last_shot_time = 0

# Ability timers and state
last_basic_ability = 0
BASIC_ABILITY_COOLDOWN = 20000  # 20 seconds
BASIC_ABILITY_DURATION = 7500   # 5 seconds
basic_active_until = 0
basic_last_shot = 0

last_machine_ability = 0
MACHINE_ABILITY_COOLDOWN = 60000  # 60 seconds cooldown
MACHINE_ABILITY_DURATION = 10000  # 10 seconds active
machine_active_until = 0
duplicates = pygame.sprite.Group()

# preserve base stats so we can restore after ability ends
BASE_RELOAD_SPEED = reload_speed
BASE_DAMAGE = DAMAGE_PER_HIT
BASE_SPEED = speed
# holding space will respect `reload_speed` between shots

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, damage, velocity=(0, -15)):
        super().__init__()
        self.image = pygame.Surface((6, 12))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=pos)
        # velocity is a tuple (vx, vy)
        self.vx, self.vy = velocity
        self.damage = damage

    def update(self):
        self.rect.move_ip(self.vx, self.vy)
        # kill if offscreen
        if (self.rect.bottom < 0 or self.rect.top > screen_height or
                self.rect.right < 0 or self.rect.left > screen_width):
            self.kill()


bullets = pygame.sprite.Group()


def player_enemy_collide(player, enemy):
    # use the player's smaller hitbox for collision checks
    return player.hitbox.colliderect(enemy.rect)


while True:
    now = pygame.time.get_ticks()



    # if machine ability expired, remove duplicates
    if machine_active_until and now >= machine_active_until:
        if len(duplicates) > 0:
            duplicates.empty()
        machine_active_until = 0

    # compute current temporary stats
    current_reload_speed = BASE_RELOAD_SPEED
    current_damage = BASE_DAMAGE
    speed_current = BASE_SPEED
    if now < basic_active_until:
        current_reload_speed = 25
        current_damage = 75
    if now < machine_active_until:
        current_reload_speed = int(BASE_RELOAD_SPEED * 2 / 3)
        current_damage = BASE_DAMAGE * 1.5
        speed_current = int(BASE_SPEED * 1.25)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # handle clicks and other event-time logic per state
        if state == GAME:
            if dashboard_button.clicked(event):
                state = DASHBOARD
            # shooting: spacebar fires if reload timer allows
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if now - last_shot_time >= current_reload_speed:
                        # player shot
                        bullets.add(Bullet(P1.rect.midtop, int(current_damage)))
                        last_shot_time = now
                        # if machine ability active, spawn shots from duplicates synchronized
                        if now < machine_active_until:
                            for d in duplicates:
                                bullets.add(Bullet(d.rect.midtop, int(current_damage)))
                elif event.key == K_p:
                    # activate ability manually
                    if jet == 'basic':
                        if now - last_basic_ability >= BASIC_ABILITY_COOLDOWN:
                            basic_active_until = now + BASIC_ABILITY_DURATION
                            last_basic_ability = now
                    elif jet == 'machine gun':
                        if now - last_machine_ability >= MACHINE_ABILITY_COOLDOWN:
                            machine_active_until = now + MACHINE_ABILITY_DURATION
                            last_machine_ability = now
                            # spawn duplicates
                            if len(duplicates) == 0:
                                duplicates.add(Duplicate(P1, -100))
                                duplicates.add(Duplicate(P1, 100))
        elif state == DASHBOARD:
            # process upgrade button clicks while in dashboard
            if upgrade_speed_button.clicked(event):
                pass
            if upgrade_damage_button.clicked(event):
                pass
            if upgrade_reload_button.clicked(event):
                pass
            if upgrade_defense_button.clicked(event):
                pass
            if game_button.clicked(event):
                state = GAME
            if Machine_Gun_Upgrade_button.clicked(event):
                pass

    if state == GAME:    
        GROUP_SPAWN_INTERVAL = max(3500, 4500 - level * 120)
        # expose `speed_current` to Player.update via globals
        globals()['speed_current'] = speed_current
        P1.update()
        # continuous fire while holding space — respect reload_speed
        pressed = pygame.key.get_pressed()
        if pressed[K_SPACE]:
            now_hold = now
            if now_hold - last_shot_time >= current_reload_speed:
                bullets.add(Bullet(P1.rect.midtop, int(current_damage)))
                last_shot_time = now_hold
                if now < machine_active_until:
                    for d in duplicates:
                        bullets.add(Bullet(d.rect.midtop, int(current_damage)))
        enemies.update()
        bullets.update()
        duplicates.update()
        # bullets vs enemies: bullets deal damage, enemies die when health <= 0
        collisions = pygame.sprite.groupcollide(bullets, enemies, True, False)
        for bullet, hit_enemies in collisions.items():
            for enemy in hit_enemies:
                # Damage fall-off at higher levels
                effective_damage = bullet.damage * max(0.4, 1.0 - level * 0.03)
                enemy.health -= effective_damage
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    # larger reward for killing bosses
                    if getattr(enemy, 'is_boss', False):
                        score += 500
                    else:
                        score += 25 + level // 2

            # player collisions: do not remove enemies on player contact
        collided = pygame.sprite.spritecollide(P1, enemies, dokill=False, collided=player_enemy_collide)
        if collided:
            # touching enemies no longer costs health
            pass
        display.fill((0, 0, 0))
        P1.draw(display)
        enemies.draw(display)
        bullets.draw(display)
        # draw duplicates if any
        for d in duplicates:
            d.draw(display)

        # dashboard_button click is handled in the event loop now

        # Level timer: increase level every 10 seconds
        now = pygame.time.get_ticks()
        if now - level_start_ticks >= LEVEL_UP_INTERVAL:
            level += 1
            level_start_ticks = now

            difficulty_level = min(level, MAX_DIFFICULTY_LEVEL)

            # increase enemy speed (capped)
            for e in enemies:
                e.speed = min(e.speed + 1, int(difficulty_level * 1.5 + 4))

        MAX_ENEMIES = 2 + level // 5
        GROUP_SPAWN_INTERVAL = max(4000, 6000 - level * 100)

        if now - last_group_spawn >= GROUP_SPAWN_INTERVAL:
            missing = MAX_ENEMIES - len(enemies)

            if missing > 0:
                # spawn up to 5 at a time, never more
                spawn_count = min(5, missing)
                spawn_enemies(enemies, spawn_count)

            last_group_spawn = now


        # draw level on screen
        level_surf = font.render(f'Level: {level}', True, (255, 255, 255))
        health_surf = font.render(f'Health: {health}', True, (255, 255, 255))
        display.blit(level_surf, (10, 10))
        display.blit(health_surf, (10, 50))

        # show reload speed in ms (current)
        reload_surf = font.render(f'Reload: {int(current_reload_speed)} ms', True, (255, 255, 255))
        display.blit(reload_surf, (10, 80))

        # show ability cooldowns / active timers
        if jet == 'basic':
            if now < basic_active_until:
                t = (basic_active_until - now) / 1000.0
                txt = font.render(f'Basic Active: {t:.1f}s', True, (0, 200, 0))
            else:
                cd = max(0.0, (last_basic_ability + BASIC_ABILITY_COOLDOWN - now) / 1000.0)
                txt = font.render(f'Basic CD: {cd:.1f}s', True, (200, 200, 0))
            display.blit(txt, (10, 110))

            if level == 50:
                win_surf = font.render('You Win!', True, (0, 255, 0))
                display.blit(win_surf, (screen_width//2 - win_surf.get_width()//2, screen_height//2))
                pygame.display.update()
                pygame.time.wait(5000)
                sys.exit()

        if jet == 'machine gun':
            if now < machine_active_until:
                t2 = (machine_active_until - now) / 1000.0
                txt2 = font.render(f'MG Active: {t2:.1f}s', True, (0, 200, 0))
            else:
                cd2 = max(0.0, (last_machine_ability + MACHINE_ABILITY_COOLDOWN - now) / 1000.0)
                txt2 = font.render(f'MG CD: {cd2:.1f}s', True, (200, 200, 0))
            display.blit(txt2, (10, 140))

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

        if level % 5 == 1 and level > 1 and level not in dashboard_levels:
            dashboard_levels.add(level)
            state = DASHBOARD

    elif state == DASHBOARD:
        level_start_ticks += FramePerSec.get_time()
        last_group_spawn += FramePerSec.get_time()

        display.fill((220, 220, 220))
        title = font.render("UPGRADE DASHBOARD", True, (0,0,0))
        display.blit(title, (screen_width//2 - title.get_width()//2, 150))

        display.blit(font.render(f"Upgrade Points: {score}", True, (0,0,0)), (10,10))
        upgrade_speed_button.draw(display)
        upgrade_damage_button.draw(display)
        game_button.draw(display)
        upgrade_reload_button.draw(display)
        upgrade_defense_button.draw(display)
        Machine_Gun_Upgrade_button.draw(display)


    pygame.display.update()
    FramePerSec.tick(FPS)
    
    
    
    
    