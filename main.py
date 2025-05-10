import pygame
import sys
import buildings
import colors
import game

from game import game_state, main_camera
from globals import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,  FPS


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

def setup():
    global safe_area, shrink_timer
    
    # Create buildings (obstacles)
    game_state.buildings = buildings.create_buildings(WORLD_WIDTH, WORLD_HEIGHT)

    game.spawn_players()
    
    # Create a safe area that's initially the entire world
    safe_area = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
    shrink_timer = 0
    
def update_game():
    global safe_area, shrink_timer

    # Update safe area
    shrink_timer += 1
    if shrink_timer >= 1800:  # Shrink every 30 seconds
        shrink_timer = 0
        new_width = safe_area.width * 0.9
        new_height = safe_area.height * 0.9
        new_pos = pygame.Vector2(
            safe_area.x + (safe_area.width - new_width) / 2,
            safe_area.y + (safe_area.height - new_height) / 2
        )
        safe_area = pygame.Rect(new_pos.x, new_pos.y, new_width, new_height)

    
    # get keys that have been pressed
    keys = pygame.key.get_pressed()
    
    # handle esc key closing game
    if keys[pygame.K_ESCAPE]:
        return False  # Signal to main loop that we should exit

    # Handle human player updates if it exists
    if game_state.human_player in game_state.players:
        # Handle movement
        game_state.human_player.handle_movement(keys, game_state.buildings, game_state.players)
        
        # Update camera to follow human player
        main_camera.update(game_state.human_player)
        
        # Handle shooting
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        game_state.human_player.handle_shooting(keys, mouse_pos, mouse_buttons, main_camera, game_state.projectiles)

    # Update players
    for player in game_state.players[:]:
        if player.is_human:
            player.update(game_state.projectiles, game_state.players, game_state.buildings)
        else:
            player.update(game_state.projectiles, game_state.players, game_state.buildings)
            # AI players move towards nearest player if one is found
            nearest = player.find_nearest(game_state.players)
            if nearest:
                player.move_towards(nearest, game_state.buildings, game_state.players)

    # update projectiles
    for projectile in game_state.projectiles[:]:
        projectile.update()
    
    game.handle_projectile_collisions(game_state.projectiles, game_state.players, game_state.buildings)   

    # Damage players outside safe area
    for player in game_state.players:
        if not safe_area.contains(player.rect):
            player.health -= 1

    # Remove dead players and expired projectiles
    game_state.players[:] = [p for p in game_state.players if p.health > 0]
    game_state.projectiles[:] = [p for p in game_state.projectiles if p.lifetime > 0]
    
    return True  # Continue the game

def draw_frame():
    screen.fill(colors.WHITE)
    
    # Draw safe area with camera offset
    safe_area_camera = main_camera.apply_rect(safe_area)
    pygame.draw.rect(screen, colors.GREEN, safe_area_camera, 1)
    
    # Draw grid lines to show movement (optional)
    grid_size = 100
    for x in range(0, WORLD_WIDTH, grid_size):
        screen_x, _ = main_camera.world_to_screen_pos(x, 0)
        if 0 <= screen_x <= SCREEN_WIDTH:
            pygame.draw.line(screen, colors.GRAY, 
                            (screen_x, 0), 
                            (screen_x, SCREEN_HEIGHT))
    for y in range(0, WORLD_HEIGHT, grid_size):
        _, screen_y = main_camera.world_to_screen_pos(0, y)
        if 0 <= screen_y <= SCREEN_HEIGHT:
            pygame.draw.line(screen, colors.GRAY, 
                            (0, screen_y), 
                            (SCREEN_WIDTH, screen_y))
    
    # Draw buildings (obstacles)
    for obj in game_state.buildings:
        obj.draw(screen, main_camera)
    
    # Draw everything with camera offset
    for player in game_state.players:
        player.draw(screen, main_camera)
    for projectile in game_state.projectiles:
        projectile.draw(screen, main_camera)
    
    # Draw coordinates for debugging
    if game_state.human_player in game_state.players:
        font = pygame.font.SysFont(None, 24)
        coords_text = f"X: {int(game_state.human_player.pos.x)}, Y: {int(game_state.human_player.pos.y)}"
        text_surface = font.render(coords_text, True, colors.BLACK)
        screen.blit(text_surface, (10, 10))

    pygame.display.flip()

def draw_winner():
    screen.fill(colors.WHITE)
    if game_state.players:
        winner = game_state.players[0]
        # Center the camera on the winner
        main_camera.update(winner)
        
        # Draw buildings
        for obj in game_state.buildings:
            obj.draw(screen, main_camera)
            
        winner.draw(screen, main_camera)
        font = pygame.font.SysFont(None, 36)
        text = font.render("Winner!", True, colors.BLACK)
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
        if len(game_state.players) > 1 and not game_over:
            result = update_game()
            if not result:  # Check if ESC was pressed
                running = False
                break
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
