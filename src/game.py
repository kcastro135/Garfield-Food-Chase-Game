import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Collect & Avoid Game")

# Game settings
FPS = 60
PLAYER_SPEED = 5
POINT_SPEED = 5
OBSTACLE_SPEED = 7
POINT_SPAWN_RATE = 30
OBSTACLE_SPAWN_RATE = 60

# Fonts
font = pygame.font.SysFont("Arial", 48, bold=True)       # Game font
lose_font = pygame.font.SysFont("Arial", 36, bold=True)  # Lose screen font
clock = pygame.time.Clock()

# Load images
home_screen_image = pygame.image.load("home_screen.png").convert()
lose_screen_image = pygame.image.load("lose_screen.png").convert()
background_image = pygame.image.load("background.png").convert()
SPRITE_SHEET = pygame.image.load("JumpCabt.png").convert_alpha()
LASGNA_IMAGE = pygame.transform.scale(pygame.image.load("lasagna.png").convert_alpha(), (40, 40))
NERMAL_IMAGE = pygame.transform.scale(pygame.image.load("nermal.png").convert_alpha(), (50, 50))

# Load character frames
FRAME_WIDTH, FRAME_HEIGHT, NUM_FRAMES = 44, 32, 8

def load_frames(sheet, num_frames, frame_width, frame_height, scale=2):
    return [
        pygame.transform.scale(
            sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)),
            (frame_width * scale, frame_height * scale)
        )
        for i in range(num_frames)
    ]

CHARACTER_FRAMES = load_frames(SPRITE_SHEET, NUM_FRAMES, FRAME_WIDTH, FRAME_HEIGHT)

# Load victory frames
VICTORY_FOLDER = "victory_frames"
VICTORY_FRAMES = []
i = 0
while True:
    path = os.path.join(VICTORY_FOLDER, f"victory_{i}.png")
    if os.path.exists(path):
        VICTORY_FRAMES.append(pygame.image.load(path).convert_alpha())
        i += 1
    else:
        break

# --- Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = CHARACTER_FRAMES
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 4, HEIGHT // 2)
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100

    def update(self, keys):
        moved = False
        if keys[pygame.K_LEFT]: self.rect.x -= PLAYER_SPEED; moved = True
        if keys[pygame.K_RIGHT]: self.rect.x += PLAYER_SPEED; moved = True
        if keys[pygame.K_UP]: self.rect.y -= PLAYER_SPEED; moved = True
        if keys[pygame.K_DOWN]: self.rect.y += PLAYER_SPEED; moved = True

        self.rect.clamp_ip(screen.get_rect())

        if moved:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

class Point(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = LASGNA_IMAGE
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)

    def update(self):
        self.rect.x -= POINT_SPEED
        if self.rect.right < 0:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = NERMAL_IMAGE
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)

    def update(self):
        self.rect.x -= OBSTACLE_SPEED
        if self.rect.right < 0:
            self.kill()

# --- Screens ---
def show_victory():
    for _ in range(3):
        for frame in VICTORY_FRAMES:
            screen.fill((0, 0, 0))
            rect = frame.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(frame, rect)
            pygame.display.flip()
            clock.tick(10)

def show_lose_screen():
    screen.blit(lose_screen_image, (0, 0))
    text = lose_font.render("Boo you lose and now Garfield is stuck with Nermal >:(", True, (255, 255, 255))
    rect = text.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
    screen.blit(text, rect)
    pygame.display.flip()
    wait_for_key()

def show_main_menu():
    screen.blit(home_screen_image, (0, 0))
    text = font.render("Help Garfield collect 30 lasagnas to win!", True, (255, 255, 0))
    screen.blit(text, (20, 20))
    pygame.display.flip()
    wait_for_key()

def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                return

# --- Main Game Loop ---
def main():
    show_main_menu()

    player = Player()
    all_sprites = pygame.sprite.Group(player)
    point_group = pygame.sprite.Group()
    obstacle_group = pygame.sprite.Group()

    score = 0
    frame_count = 0
    running = True

    while running:
        clock.tick(FPS)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys)

        if frame_count % POINT_SPAWN_RATE == 0:
            point = Point()
            all_sprites.add(point)
            point_group.add(point)

        if frame_count % OBSTACLE_SPAWN_RATE == 0:
            obstacle = Obstacle()
            all_sprites.add(obstacle)
            obstacle_group.add(obstacle)

        point_group.update()
        obstacle_group.update()

        if pygame.sprite.spritecollideany(player, obstacle_group):
            show_lose_screen()
            running = False
            continue

        collected = pygame.sprite.spritecollide(player, point_group, True)
        score += len(collected)

        # --- Drawing ---
        screen.blit(background_image, (0, 0))  # <-- Background here
        all_sprites.draw(screen)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

        if score >= 30:
            show_victory()
            screen.fill((0, 0, 0))
            win_text = font.render("You Win!", True, (255, 255, 0))
            screen.blit(win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            pygame.display.flip()
            wait_for_key()
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
