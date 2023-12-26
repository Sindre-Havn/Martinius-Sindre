import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display in fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("Triangle Shooter Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Triangle settings
triangle_size = 15
triangle_pos = [width // 2, height // 2]
triangle_speed = 5 / 4  # Reduced speed for player

# Projectile settings
projectiles = []
projectile_speed = triangle_speed * 2

# Enemy settings
enemy_pos = [random.randint(0, width), random.randint(0, height)]
enemy_speed = 2 / 3  # Reduced speed for enemy
enemy_size = 20

# Scoring and weapon upgrade
score = 0
weapon_upgraded = False
last_shot_time = 0
shot_interval = 500  # milliseconds

def get_triangle_points(position, angle, size):
    top_point = (position[0] + size * math.cos(angle), position[1] + size * math.sin(angle))
    left_point = (position[0] + size * math.cos(angle + 2 * math.pi / 3), 
                  position[1] + size * math.sin(angle + 2 * math.pi / 3))
    right_point = (position[0] + size * math.cos(angle - 2 * math.pi / 3), 
                   position[1] + size * math.sin(angle - 2 * math.pi / 3))
    return [top_point, left_point, right_point]

def add_projectile(position, angle):
    dx = math.cos(angle) * projectile_speed
    dy = math.sin(angle) * projectile_speed
    projectiles.append([position, [dx, dy]])

def is_off_screen(pos):
    x, y = pos
    return x < 0 or x > width or y < 0 or y > height

def restart_game():
    global triangle_pos, enemy_pos, projectiles, score, weapon_upgraded
    triangle_pos = [width // 2, height // 2]
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
            add_projectile(list(triangle_points[0]), angle)
            last_shot_time = current_time

    # Handle keyboard input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        triangle_pos[1] = max(0, triangle_pos[1] - triangle_speed)
    if keys[pygame.K_s]:
        triangle_pos[1] = min(height, triangle_pos[1] + triangle_speed)
    if keys[pygame.K_a]:
        triangle_pos[0] = max(0, triangle_pos[0] - triangle_speed)
    if keys[pygame.K_d]:
        triangle_pos[0] = min(width, triangle_pos[0] + triangle_speed)

    # Get mouse position and calculate angle
    mouse_x, mouse_y = pygame.mouse.get_pos()
    angle = math.atan2(mouse_y - triangle_pos[1], mouse_x - triangle_pos[0])

    # Move enemy towards player
    move_towards(triangle_pos, enemy_pos, enemy_speed)

    # Check for collisions
    if math.hypot(triangle_pos[0] - enemy_pos[0], triangle_pos[1] - enemy_pos[1]) < enemy_size + triangle_size:
        restart_game()

    # Update projectiles and check for hits
    for projectile in projectiles:
        projectile[0][0] += projectile[1][0]
        projectile[0][1] += projectile[1][1]
        if math.hypot(projectile[0][0] - enemy_pos[0], projectile[0][1] - enemy_pos[1]) < enemy_size:
            score += 1
            enemy_pos = [random.randint(-100, width + 100), random.randint(-100, height + 100)]
            projectiles.remove(projectile)

    projectiles = [p for p in projectiles if not is_off_screen(p[0])]

    # Upgrade weapon at score 25
    if score >= 25 and not weapon_upgraded:
        weapon_upgraded = True
        shot_interval = 100  # Faster shooting interval

    # Clear screen
    screen.fill(BLACK)

    # Get and draw triangle points
    triangle_points = get_triangle_points(triangle_pos, angle, triangle_size)
    pygame.draw.polygon(screen, WHITE, triangle_points)

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