import pygame
import sys
import time
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Via Ferrata Platforming")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)  # Color for winning platform

# Game constants (fixed value will not change)
GROUND_HEIGHT = 550
STARTING_POS = [100, 450]

#camera variables
camera_x = 0
camera_y = 0

def reset_player():
    return {
        'pos': STARTING_POS.copy(),
        'size': 50,
        'velocity': 5,
        'vertical_velocity': 0,
        'is_jumping': False,
        'is_climbing': False
    }

player = reset_player()
gravity = 0.5
jump_strength = 15

# Loading the background image with proper path handling
try:
    background_path = os.path.join('assets', 'Klettersteig-Route-Alpspitze.jpeg')
    background = pygame.image.load(background_path)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Unable to load background image: {e}")
    print("Make sure the 'assets' folder contains 'Klettersteig-Route-Alpspitze.jpeg'")
    background = None

# Ground and platform settings
platforms = [
    # Starting area
    pygame.Rect(100, 500, 150, 10),  # Starting platform
    pygame.Rect(350, 400, 150, 10),
    pygame.Rect(200, 300, 150, 10),

    # Mid section
    pygame.Rect(500, 250, 150, 10),
    pygame.Rect(300, 150, 150, 10),
    pygame.Rect(600, 100, 150, 10),
    pygame.Rect(100, 50, 150, 10),

    # Higher section
    pygame.Rect(450, 0, 150, 10),
    pygame.Rect(250, -100, 150, 10),
    pygame.Rect(550, -200, 150, 10),

    # Advanced climbing section
    pygame.Rect(200, -300, 100, 10),
    pygame.Rect(400, -400, 100, 10),
    pygame.Rect(150, -500, 100, 10),
    pygame.Rect(500, -600, 100, 10),

    # Expert section
    pygame.Rect(300, -700, 80, 10),
    pygame.Rect(100, -800, 80, 10),
    pygame.Rect(500, -900, 80, 10),
    pygame.Rect(250, -1000, 80, 10),

    # Final challenge
    pygame.Rect(400, -1100, 60, 10),
    pygame.Rect(200, -1200, 60, 10),
    pygame.Rect(350, -1300, 60, 10),
]

# Winning platform (golden platform at the top)
winning_platform = pygame.Rect(300, -1400, 200, 20)

# Ladder settings
ladders = [
    # Starting area ladders
    pygame.Rect(220, 350, 20, 150),
    pygame.Rect(520, 100, 20, 150),

    # Mid section ladders
    pygame.Rect(320, -50, 20, 150),
    pygame.Rect(470, -200, 20, 150),

    # Higher section ladders
    pygame.Rect(220, -300, 20, 200),
    pygame.Rect(420, -500, 20, 200),

    # Advanced section ladders
    pygame.Rect(170, -700, 20, 200),
    pygame.Rect(520, -900, 20, 200),

    # Final section ladders
    pygame.Rect(320, -1100, 20, 200),
    pygame.Rect(220, -1300, 20, 200),
]


def show_message(text, duration=2):
    font = pygame.font.Font(None, 74)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))

    # Create a semi-transparent background for the text
    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    screen.blit(s, (0, 0))

    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    time.sleep(duration)


# Game loop
clock = pygame.time.Clock()
game_won = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if game_won:
        show_message("You Win!", 2)
        game_won = False
        player = reset_player()
        continue

    keys = pygame.key.get_pressed()

    # Player horizontal movement
    if keys[pygame.K_LEFT]:
        player['pos'][0] -= player['velocity']
    if keys[pygame.K_RIGHT]:
        player['pos'][0] += player['velocity']

    # Create a rect for the player for collision checking
    player_rect = pygame.Rect(player['pos'][0], player['pos'][1], player['size'], player['size'])

    # Check if player has reached the winning platform
    if player_rect.colliderect(winning_platform):
        game_won = True

    # Check if player fell to ground level
    if player['pos'][1] + player['size'] >= GROUND_HEIGHT:  # Check bottom of player
        reset_game()
        continue

    # Check if the player is on a ladder
    on_ladder = False
    for ladder in ladders:
        if player_rect.colliderect(ladder):
            on_ladder = True
            break

    # Climbing movement
    if on_ladder:
        player['is_climbing'] = True
        player['vertical_velocity'] = 0

        if keys[pygame.K_UP]:
            player['pos'][1] -= player['velocity']
        if keys[pygame.K_DOWN]:
            player['pos'][1] += player['velocity']
    else:
        player['is_climbing'] = False
        # Update vertical position and velocity
        player['vertical_velocity'] += gravity
        next_y = player['pos'][1] + player['vertical_velocity']

        # Don't let player fall through ground
        if next_y + player['size'] >= GROUND_HEIGHT:
            reset_game()
            continue
        else:
            player['pos'][1] = next_y

    # Check for collisions with platforms
    on_ground = False
    for platform in platforms:
        if player_rect.colliderect(platform) and player['vertical_velocity'] >= 0:
            on_ground = True
            player['is_jumping'] = False
            player['pos'][1] = platform.top - player['size']
            player['vertical_velocity'] = 0
            break

    # Check collision with winning platform
    if player_rect.colliderect(winning_platform) and player['vertical_velocity'] >= 0:
        on_ground = True
        player['is_jumping'] = False
        player['pos'][1] = winning_platform.top - player['size']
        player['vertical_velocity'] = 0

    # Jump logic
    if keys[pygame.K_SPACE] and not player['is_jumping'] and not player['is_climbing']:
        player['is_jumping'] = True
        player['vertical_velocity'] = -jump_strength

    # Camera follow logic
    target_camera_y = player['pos'][1] - HEIGHT // 2
    target_camera_x = player['pos'][0] - WIDTH // 2

    max_camera_y = GROUND_HEIGHT - HEIGHT
    min_camera_y = -1500  # Adjusted for winning platform

    camera_y = max(min_camera_y, min(target_camera_y, max_camera_y))
    camera_x = max(0, min(target_camera_x, WIDTH))

    # World bounds
    world_min_x = 0
    world_max_x = WIDTH * 2
    world_min_y = -1500
    world_max_y = GROUND_HEIGHT

    # Keep player within bounds
    player['pos'][0] = max(world_min_x, min(player['pos'][0], world_max_x - player['size']))
    player['pos'][1] = max(world_min_y, min(player['pos'][1], world_max_y - player['size']))

    # Draw background
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(WHITE)

    # Draw ground
    pygame.draw.rect(screen, GREEN, (0 - camera_x, GROUND_HEIGHT - camera_y, WIDTH * 2, HEIGHT - GROUND_HEIGHT))

    # Draw platforms
    for platform in platforms:
        platform_screen_x = platform.x - camera_x
        platform_screen_y = platform.y - camera_y
        if (-platform.width <= platform_screen_x <= WIDTH and
                -platform.height <= platform_screen_y <= HEIGHT):
            pygame.draw.rect(screen, RED, (platform_screen_x, platform_screen_y,
                                           platform.width, platform.height))

    # Draw winning platform
    winning_platform_screen_x = winning_platform.x - camera_x
    winning_platform_screen_y = winning_platform.y - camera_y
    if (-winning_platform.width <= winning_platform_screen_x <= WIDTH and
            -winning_platform.height <= winning_platform_screen_y <= HEIGHT):
        pygame.draw.rect(screen, GOLD, (winning_platform_screen_x, winning_platform_screen_y,
                                        winning_platform.width, winning_platform.height))

    # Draw ladders
    for ladder in ladders:
        ladder_screen_x = ladder.x - camera_x
        ladder_screen_y = ladder.y - camera_y
        if (-ladder.width <= ladder_screen_x <= WIDTH and
                -ladder.height <= ladder_screen_y <= HEIGHT):
            pygame.draw.rect(screen, BROWN, (ladder_screen_x, ladder_screen_y,
                                             ladder.width, ladder.height))

    # Draw player
    player_screen_x = player['pos'][0] - camera_x
    player_screen_y = player['pos'][1] - camera_y
    pygame.draw.rect(screen, BLUE, (player_screen_x, player_screen_y,
                                    player['size'], player['size']))

    pygame.display.flip()
    clock.tick(60)
