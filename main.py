import pygame
import sys
import game

from game import game_state
from globals import FPS


# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()

def setup():
    game.create_buildings()
    game.spawn_players()
    
def update_game():
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_ESCAPE]: # handle esc key closing game
        return False 
    
    game.update_kill_circle()    
    game.update_players(keys)
    game.update_projectiles()

    game.expired_entity_cleanup()
    return True  # Continue the game

def draw_frame():
    game.clear_screen()
    game.draw_debug()
    game.draw_buildings()
    game.draw_kill_circle()
    game.draw_camera_offset_entities()

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
            game.draw_winner()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
