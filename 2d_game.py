import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1200
MAP_WIDTH, MAP_HEIGHT = 1600, 1200
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Lost City: Ruin Explorer")

SKY = (15, 25, 35)
STONE = (50, 55, 60)
LADDER_COLOR = (90, 50, 20)
HERO_COLOR = (180, 140, 90)
ENEMY_COLOR = (130, 40, 40)
WHITE, BLACK, RED = (255, 255, 255), (0, 0, 0), (220, 20, 20)

try:
    bg_custom = pygame.image.load("image.jpg").convert()
    bg_custom = pygame.transform.scale(bg_custom, (MAP_WIDTH, MAP_HEIGHT))
except:
    bg_custom = None

font_msg = pygame.font.SysFont("Arial", 50, bold=True)
font_ui = pygame.font.SysFont("Arial", 22, bold=True)

platforms = [
    pygame.Rect(0, 1150, 1600, 50),      #Пол
    pygame.Rect(0, 0, 1600, 20),         #потолок
    pygame.Rect(0, 0, 20, 1200),         #лево
    pygame.Rect(1600, 0, 20, 1200),      #право
    #вутренние платформы
    pygame.Rect(300, 1000, 400, 40),
    pygame.Rect(800, 950, 300, 40),
    pygame.Rect(100, 800, 500, 40),
    pygame.Rect(1000, 750, 400, 40),
    pygame.Rect(500, 550, 600, 40),
    pygame.Rect(50, 350, 300, 40),
    pygame.Rect(1200, 400, 300, 40),
]

ladders = [
    pygame.Rect(500, 1000, 50, 150),
    pygame.Rect(850, 950, 50, 250),
    pygame.Rect(200, 800, 50, 400),
    pygame.Rect(1200, 750, 50, 450),
    pygame.Rect(600, 550, 50, 250),
]

def draw_background(surface, cam_x, cam_y):
    if bg_custom:
        surface.blit(bg_custom, (-cam_x, -cam_y))
    else:
        surface.fill(SKY)
        for i in range(0, MAP_WIDTH, 400):
            col_x = i - cam_x * 0.3
            pygame.draw.rect(surface, (25, 35, 45), (col_x, 0, 80, MAP_HEIGHT))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 1050, 40, 60)
        self.vel_y = 0
        self.speed = 7
        self.on_ground = False
        self.on_ladder = False
        self.facing_right = True

    def update(self, keys):
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.facing_right = True

        self.on_ladder = any(self.rect.colliderect(lad) for lad in ladders)
        
        if self.on_ladder:
            self.vel_y = 0
            if keys[pygame.K_UP]: self.rect.y -= self.speed
            if keys[pygame.K_DOWN]: self.rect.y += self.speed
        else:
            if keys[pygame.K_UP] and self.on_ground:
                self.vel_y = -16
                self.on_ground = False
            
            self.vel_y += 0.8
            if self.vel_y > 15: self.vel_y = 15

        self.rect.x += dx
        for p in platforms:
            if self.rect.colliderect(p):
                if dx > 0: self.rect.right = p.left
                if dx < 0: self.rect.left = p.right

        if not self.on_ladder:
            self.rect.y += self.vel_y
            self.on_ground = False
            for p in platforms:
                if self.rect.colliderect(p):
                    if self.vel_y > 0:
                        self.rect.bottom = p.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.rect.top = p.bottom
                        self.vel_y = 0

    def draw(self, surface, cam):
        r = self.rect.move(-cam[0], -cam[1])
        pygame.draw.rect(surface, HERO_COLOR, r)
        pygame.draw.rect(surface, (100, 70, 40), (r.x-5, r.y, 50, 10))
        eye_x = r.x + 25 if self.facing_right else r.x + 5
        pygame.draw.rect(surface, WHITE, (eye_x, r.y + 15, 8, 8))

class Enemy:
    def __init__(self, p_rect, cam_x, cam_y):
        side = random.choice(['L', 'R', 'U', 'D'])
        if side == 'L': self.x, self.y = cam_x - 50, cam_y + random.randint(0, 600)
        elif side == 'R': self.x, self.y = cam_x + 850, cam_y + random.randint(0, 600)
        elif side == 'U': self.x, self.y = cam_x + random.randint(0, 800), cam_y - 50
        else: self.x, self.y = cam_x + random.randint(0, 800), cam_y + 650
        
        self.rect = pygame.Rect(self.x, self.y, 40, 40)
        self.speed = random.uniform(1.5, 3.5)

    def move(self, target):
        if self.rect.x < target.x: self.rect.x += self.speed
        else: self.rect.x -= self.speed
        if self.rect.y < target.y: self.rect.y += self.speed
        else: self.rect.y -= self.speed

    def draw(self, surface, cam):
        r = self.rect.move(-cam[0], -cam[1])
        pygame.draw.rect(surface, ENEMY_COLOR, r)
        inner = r.inflate(-20, -20)
        pygame.draw.rect(surface, RED, inner)

class Bullet:
    def __init__(self, x, y, right):
        self.rect = pygame.Rect(x, y, 15, 8)
        self.speed = 15 if right else -15
    def move(self): self.rect.x += self.speed
    def draw(self, surface, cam):
        pygame.draw.rect(surface, (255, 200, 0), self.rect.move(-cam[0], -cam[1]))

def main():
    clock = pygame.time.Clock()
    
    while True: 
        player = Player()
        enemies = []
        bullets = []
        score = 0
        spawn_timer = 0
        game_over = False
        running = True

        while running:
            cam_x = max(0, min(player.rect.centerx - SCREEN_WIDTH // 2, MAP_WIDTH - SCREEN_WIDTH))
            cam_y = max(0, min(player.rect.centery - SCREEN_HEIGHT // 2, MAP_HEIGHT - SCREEN_HEIGHT))
            camera = (cam_x, cam_y)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if not game_over:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                        bx = player.rect.right if player.facing_right else player.rect.left
                        bullets.append(Bullet(bx, player.rect.centery, player.facing_right))
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()
                        if SCREEN_WIDTH//2 - 160 < mx < SCREEN_WIDTH//2 - 10:
                            if SCREEN_HEIGHT//2 + 50 < my < SCREEN_HEIGHT//2 + 100:
                                running = False
                        elif SCREEN_WIDTH//2 + 10 < mx < SCREEN_WIDTH//2 + 160:
                            if SCREEN_HEIGHT//2 + 50 < my < SCREEN_HEIGHT//2 + 100:
                                pygame.quit()
                                sys.exit()

            if not game_over:
                player.update(pygame.key.get_pressed())
                
                spawn_timer += 1
                if spawn_timer > 70:
                    enemies.append(Enemy(player.rect, cam_x, cam_y))
                    spawn_timer = 0
                
                for b in bullets[:]:
                    b.move()
                    if b.rect.x < 0 or b.rect.x > MAP_WIDTH: bullets.remove(b)

                for e in enemies[:]:
                    e.move(player.rect)
                    if e.rect.colliderect(player.rect): 
                        game_over = True
                    for b in bullets[:]:
                        if e.rect.colliderect(b.rect):
                            if e in enemies: enemies.remove(e)
                            if b in bullets: bullets.remove(b)
                            score += 10

            draw_background(screen, cam_x, cam_y)
            
            for lad in ladders:
                pygame.draw.rect(screen, LADDER_COLOR, lad.move(-cam_x, -cam_y))
                for s in range(lad.y + 10, lad.bottom, 20):
                    pygame.draw.line(screen, BLACK, (lad.x-cam_x, s-cam_y), (lad.right-cam_x, s-cam_y), 2)
            
            for p in platforms:
                pygame.draw.rect(screen, STONE, p.move(-cam_x, -cam_y))
                pygame.draw.rect(screen, (30, 30, 30), p.move(-cam_x, -cam_y), 2)

            for b in bullets: b.draw(screen, camera)
            for e in enemies: e.draw(screen, camera)
            player.draw(screen, camera)

            txt = font_ui.render(f"SCORE: {score}", True, WHITE)
            screen.blit(txt, (20, 20))

            if game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(180); overlay.fill(BLACK)
                screen.blit(overlay, (0,0))
                go_txt = font_msg.render("GAME OVER", True, RED)
                screen.blit(go_txt, (SCREEN_WIDTH//2 - go_txt.get_width()//2, SCREEN_HEIGHT//2 - 60))
                
                btn_res = pygame.Rect(SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT//2 + 50, 150, 50)
                btn_cls = pygame.Rect(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT//2 + 50, 150, 50)
                
                pygame.draw.rect(screen, WHITE, btn_res, border_radius=10)
                pygame.draw.rect(screen, WHITE, btn_cls, border_radius=10)
                
                res_t = font_ui.render("RESTART", True, BLACK)
                cls_t = font_ui.render("CLOSE", True, BLACK)
                
                screen.blit(res_t, (btn_res.centerx - res_t.get_width()//2, btn_res.y + 12))
                screen.blit(cls_t, (btn_cls.centerx - cls_t.get_width()//2, btn_cls.y + 12))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    main()