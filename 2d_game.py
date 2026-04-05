import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Затерянный город: Исследователь руин")

BG_COLOR = (30, 50, 40)
GROUND_COLOR = (60, 60, 60)
HERO_COLOR = (50, 150, 200)
ENEMY_COLOR = (200, 50, 50)
WEAPON_COLOR = (220, 220, 220)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (150, 150, 150)

font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_small = pygame.font.SysFont("Arial", 24)

FPS = 60
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = WIDTH - 150
        self.y = HEIGHT - 100 - self.height
        self.speed = 5
        self.is_jump = False
        self.jump_velocity = 12
        self.y_velocity = 0
        self.gravity = 0.5
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.facing_left = True

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.facing_left = True
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.facing_left = False
            
        if self.x < 0: self.x = 0
        if self.x > WIDTH - self.width: self.x = WIDTH - self.width

        if not self.is_jump:
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                self.is_jump = True
                self.y_velocity = -self.jump_velocity
        else:
            self.y += self.y_velocity
            self.y_velocity += self.gravity
            if self.y >= HEIGHT - 100 - self.height:
                self.y = HEIGHT - 100 - self.height
                self.is_jump = False
                self.y_velocity = 0

        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, HERO_COLOR, self.rect)
        eye_x = self.x + 5 if self.facing_left else self.x + 25
        pygame.draw.rect(surface, WHITE, (eye_x, self.y + 10, 10, 10))

class Enemy:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = -self.width
        self.y = HEIGHT - 100 - self.height
        self.speed = random.randint(2, 4)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self):
        self.x += self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, ENEMY_COLOR, self.rect)

class Weapon:
    def __init__(self, x, y, facing_left):
        self.width = 15
        self.height = 5
        self.x = x
        self.y = y
        self.speed = -10 if facing_left else 10
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self):
        self.x += self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, WEAPON_COLOR, self.rect)

def reset_game():
    return Player(), [], [], False, 0

player, enemies, weapons, game_over, score = reset_game()
enemy_spawn_timer = 0

btn_restart = pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 50, 150, 40)
btn_close = pygame.Rect(WIDTH//2 + 10, HEIGHT//2 + 50, 150, 40)

running = True
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT - 100, WIDTH, 100)) # Земля
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_z, pygame.K_x, pygame.K_RETURN):
                    w_x = player.x if player.facing_left else player.x + player.width
                    weapons.append(Weapon(w_x, player.y + 20, player.facing_left))
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if btn_restart.collidepoint(mouse_pos):
                    player, enemies, weapons, game_over, score = reset_game()
                elif btn_close.collidepoint(mouse_pos):
                    running = False

    if not game_over:
        keys = pygame.key.get_pressed()
        player.move(keys)

        enemy_spawn_timer += 1
        if enemy_spawn_timer > 90: # Каждые 1.5 секунды
            enemies.append(Enemy())
            enemy_spawn_timer = 0

        for w in weapons[:]:
            w.move()
            if w.x < 0 or w.x > WIDTH:
                weapons.remove(w)

        for e in enemies[:]:
            e.move()
            for w in weapons[:]:
                if e.rect.colliderect(w.rect):
                    if e in enemies: enemies.remove(e)
                    if w in weapons: weapons.remove(w)
                    score += 10
                    break
            
            if e.rect.colliderect(player.rect):
                game_over = True
            
            if e.x > WIDTH:
                if e in enemies:
                    enemies.remove(e)

        player.draw(screen)
        for e in enemies: e.draw(screen)
        for w in weapons: w.draw(screen)
        
        score_text = font_small.render(f"Счет: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

    else:
        player.draw(screen)
        for e in enemies: e.draw(screen)

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        window_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 220)
        pygame.draw.rect(screen, GRAY, window_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, window_rect, 3, border_radius=10)

        go_text = font_large.render("Game over", True, RED)
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 80))

        pygame.draw.rect(screen, WHITE, btn_restart, border_radius=5)
        pygame.draw.rect(screen, WHITE, btn_close, border_radius=5)
        
        txt_restart = font_small.render("Начать заново", True, BLACK)
        txt_close = font_small.render("Закрыть", True, BLACK)
        
        screen.blit(txt_restart, (btn_restart.x + 10, btn_restart.y + 5))
        screen.blit(txt_close, (btn_close.x + 35, btn_close.y + 5))

    pygame.display.flip()

pygame.quit()
sys.exit()