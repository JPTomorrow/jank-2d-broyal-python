import pygame
import random
import sys
import math
from player import Player, Projectile
from camera import Camera
from buildings import Buildings, create_buildings

# Initialize Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600  # Screen dimensions
WORLD_WIDTH, WORLD_HEIGHT = 3000, 3000  # World dimensions (much larger than screen)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

def setup():
    global players, projectiles, safe_area, shrink_timer, human_player, camera, buildings
    
    # Create buildings (obstacles)
    buildings = create_buildings(WORLD_WIDTH, WORLD_HEIGHT)
    
    # Create 9 AI players spread across the world (ensuring they don't spawn inside walls)
    players = []
    for _ in range(9):
        valid_spawn = False
        while not valid_spawn:
            x = random.randint(0, WORLD_WIDTH - 32)
            y = random.randint(0, WORLD_HEIGHT - 32)
            player_rect = pygame.Rect(x, y, 32, 32)
            valid_spawn = True
            for obj in buildings:
                if obj.collides_with(player_rect):
                    valid_spawn = False
                    break
        players.append(Player(x, y))
    
    # Create 1 human player in the center of the world (ensuring they don't spawn inside walls)
    valid_spawn = False
    while not valid_spawn:
        x = WORLD_WIDTH // 2
        y = WORLD_HEIGHT // 2
        player_rect = pygame.Rect(x, y, 32, 32)
        valid_spawn = True
        for obj in buildings:
            if obj.collides_with(player_rect):
                x += 50  # Try a bit to the right
                y += 50  # and down
                player_rect = pygame.Rect(x, y, 32, 32)
                if not obj.collides_with(player_rect):
                    valid_spawn = True
                    break
                else:
                    valid_spawn = False
    
    human_player = Player(x, y, is_human=True)
    human_player.color = BLUE  # Blue color for human player
    players.append(human_player)
    projectiles = []
    
    # Create a safe area that's initially the entire world
    safe_area = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
    shrink_timer = 0
    
    # Create camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

def update_game():
    global players, projectiles, safe_area, shrink_timer, human_player, camera, buildings

    # Update safe area
    shrink_timer += 1
    if shrink_timer >= 1800:  # Shrink every 30 seconds
        shrink_timer = 0
        new_width = safe_area.width * 0.9
        new_height = safe_area.height * 0.9
        new_x = safe_area.x + (safe_area.width - new_width) / 2
        new_y = safe_area.y + (safe_area.height - new_height) / 2
        safe_area = pygame.Rect(new_x, new_y, new_width, new_height)

    
    # get keys that have been pressed
    keys = pygame.key.get_pressed()
    
    # handle esc key closing game
    if keys[pygame.K_ESCAPE]:
        pygame.quit()

    # Handle human player updates if it exists
    if human_player in players:
        # Handle movement
        human_player.handle_movement(keys, buildings, players)
        
        # Update camera to follow human player
        camera.update(human_player)
        
        # Handle shooting
        mouse_pos = pygame.mouse.get_pos()
        human_player.handle_shooting(keys, mouse_pos, camera, projectiles)

    # Update players and projectiles
    for player in players[:]:
        if player.is_human:
            player.update(projectiles, players, buildings)
        else:
            player.update(projectiles, players, buildings)
            # AI players move towards nearest player if one is found
            nearest = player.find_nearest(players)
            if nearest:
                player.move_towards(nearest, buildings, players)

    for projectile in projectiles[:]:
        projectile.update()

    # Check collisions
    for projectile in projectiles[:]:
        if projectile in projectiles:  # Check if projectile still exists
            # Check collision with buildings
            for obj in buildings:
                if obj.collides_with(projectile.rect):
                    if projectile in projectiles:  # Double-check before removing
                        projectiles.remove(projectile)
                    break
            
            # If projectile still exists, check collision with players
            if projectile in projectiles:
                for player in players:
                    if player != projectile.owner and player.rect.colliderect(projectile.rect):
                        player.health -= 10
                        if projectile in projectiles:  # Double-check before removing
                            projectiles.remove(projectile)
                        break

    # Damage players outside safe area
    for player in players:
        if not safe_area.contains(player.rect):
            player.health -= 1

    # Remove dead players and expired projectiles
    players[:] = [p for p in players if p.health > 0]
    projectiles[:] = [p for p in projectiles if p.lifetime > 0]

def draw_frame():
    screen.fill(WHITE)
    
    # Draw safe area with camera offset
    safe_area_camera = camera.apply_rect(safe_area)
    pygame.draw.rect(screen, GREEN, safe_area_camera, 1)
    
    # Draw grid lines to show movement (optional)
    grid_size = 100
    for x in range(0, WORLD_WIDTH, grid_size):
        screen_x, _ = camera.world_to_screen_pos(x, 0)
        if 0 <= screen_x <= SCREEN_WIDTH:
            pygame.draw.line(screen, GRAY, 
                            (screen_x, 0), 
                            (screen_x, SCREEN_HEIGHT))
    for y in range(0, WORLD_HEIGHT, grid_size):
        _, screen_y = camera.world_to_screen_pos(0, y)
        if 0 <= screen_y <= SCREEN_HEIGHT:
            pygame.draw.line(screen, GRAY, 
                            (0, screen_y), 
                            (SCREEN_WIDTH, screen_y))
    
    # Draw buildings (obstacles)
    for obj in buildings:
        obj.draw(screen, camera)
    
    # Draw everything with camera offset
    for player in players:
        player.draw(screen, camera)
    for projectile in projectiles:
        projectile.draw(screen, camera)
    
    # Draw coordinates for debugging
    if human_player in players:
        font = pygame.font.SysFont(None, 24)
        coords_text = f"X: {int(human_player.x)}, Y: {int(human_player.y)}"
        text_surface = font.render(coords_text, True, BLACK)
        screen.blit(text_surface, (10, 10))

    pygame.display.flip()

def draw_winner():
    screen.fill(WHITE)
    if players:
        winner = players[0]
        # Center the camera on the winner
        camera.update(winner)
        
        # Draw buildings
        for obj in buildings:
            obj.draw(screen, camera)
            
        winner.draw(screen, camera)
        font = pygame.font.SysFont(None, 36)
        text = font.render("Winner!", True, BLACK)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 50))
    pygame.display.flip()

def main():
    setup()
    running = True
    game_over = False
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update game state if there are still players
        if len(players) > 1 and not game_over:
            update_game()
            draw_frame()
        elif not game_over:
            game_over = True
            draw_winner()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
