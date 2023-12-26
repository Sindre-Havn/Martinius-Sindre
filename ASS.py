import pygame
import sys
import math
import random
import os

def find_file(filename, search_paths):
    for directory in search_paths:
        for root, dirs, files in os.walk(directory):
            if filename in files:
                return os.path.join(root, filename)
    return None

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("Shooter Game with 'fat Geck'")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Player settings
player_speed = 5 / 4  # Reduced speed for player

# Projectile settings
projectiles = []
projectile_speed = player_speed * 2

# Enemy settings
enemy_pos = [random.randint(0, width), random.randint(0, height)]
enemy_speed = 2 / 3  # Reduced speed for enemy
enemy_size = 20

# Scoring and weapon upgrade
score = 0
weapon_upgraded = False
last_shot_time = 0
shot_interval = 500  # milliseconds

# Search for 'fat Geck' image
game_folder_name = "IMADETHIS"
filename = "fat_geck.png"
possible_paths = [
    os.path.expanduser(f"~/{'Skrivebord'}"),  # Home directory
    os.path.join(os.environ[''], os.environ['HOMEPATH'], "Desktop", game_folder_name),  # Desktop directory
    # Add any other likely directories where the game folder might be
]

# Load the player image
full_path = find_file(filename, possible_paths)
if full_path:
    print(f"Found '{filename}' at '{full_path}'")
    player_image = pygame.image.load(full_path).convert_alpha()
    player_rect = player_image.get_rect(center=(width // 2, height // 2))
else:
    print(f"File '{filename}' not found in specified directories.")
    sys.exit()

def add_projectile(position, angle):
    dx = math.cos(angle) * projectile_speed
    dy = math.sin(angle) * projectile_speed
    projectiles.append([position, [dx, dy]])

def is_off_screen(pos):
    x, y = pos
    return x < 0 or x > width or y < 0 or y > height

def restart_game():
    global player_rect, enemy_pos, projectiles, score, weapon_upgraded
    player_rect.center = (width // 2, height // 2)
    enemy_pos = [random.randint(0, width), random.randint(0, height)]
    projectiles = []
    score = 0
    weapon_upgraded = False

def move_towards(target, position, speed):
    angle = math.atan2(target[1] - position[1], target[0] - position[0])
    position[0] += math.cos(angle) * speed
    position[1] += math.sin(angle) * speed

# Main game loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN or (weapon_upgraded and current_time - last_shot_time > shot_interval):
            add_projectile(player_rect.center, math.atan2(mouse_y - player_rect.centery, mouse_x - player_rect.centerx))
            last_shot_time = current_time

    # Handle keyboard input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_rect.centery = max(0, player_rect.centery - player_speed)
    if keys[pygame.K_s]:
        player_rect.centery = min(height, player_rect.centery + player_speed)
    if keys[pygame.K_a]:
        player_rect.centerx = max(0, player_rect.centerx - player_speed)
    if keys[pygame.K_d]:
        player_rect.centerx = min(width, player_rect.centerx + player_speed)

    # Get mouse position and calculate angle
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Move enemy towards player
    move_towards(player_rect.center, enemy_pos, enemy_speed)

    # Check for collisions
    if math.hypot(player_rect.centerx - enemy_pos[0], player_rect.centery - enemy_pos[1]) < enemy_size + player_rect.width // 2:
        restart_game()

    # Update projectiles and check for hits
    for projectile in projectiles[:]:
        projectile[0][0] += projectile[1][0]
        projectile[0][1] += projectile[1][1]
        if math.hypot(projectile[0][0] - enemy_pos[0], projectile[0][1] - enemy_pos[1]) < enemy_size:
            score += 1
            enemy_pos = [random.randint(-100, width + 100), random.randint(-100, height + 100)]
            projectiles.remove(projectile)
        if is_off_screen(projectile[0]):
            projectiles.remove(projectile)

    # Upgrade weapon at score 25
    if score >= 25 and not weapon_upgraded:
        weapon_upgraded = True
        shot_interval = 100  # Faster shooting interval

    # Clear screen
    screen.fill(BLACK)

    # Draw the player image
    screen.blit(player_image, player_rect.topleft)

    # Draw projectiles
    for projectile in projectiles:
        pygame.draw.circle(screen, WHITE, [int(projectile[0][0]), int(projectile[0][1])], 5)

    # Draw enemy
    pygame.draw.circle(screen, WHITE, [int(enemy_pos[0]), int(enemy_pos[1])], enemy_size)

    # Display score
    font = pygame.font.SysFont(None, 36)
    text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(text, (10, 10))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
