import pygame
import random
import colors

import buildings

from player import Player
from game_state import GameState
from camera import Camera
from globals import WORLD_WIDTH, WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
from kill_circle import KillCircle
from ground import Ground
    
game_state = GameState()
_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
main_camera = Camera()
kill_circle = KillCircle()
ground = Ground()

""" 
:SETUP
"""

def create_buildings():
    game_state.buildings = buildings.create_buildings(WORLD_WIDTH, WORLD_HEIGHT)

""" Create 9 AI players spread across the world (ensuring they don't spawn inside walls)
Create 1 human player in the center of the world (ensuring they don't spawn inside walls) """
def spawn_players():
    for _ in range(9):
        valid_spawn = False
        while not valid_spawn:
            spawn_pos = pygame.Vector2(
                random.randint(0, WORLD_WIDTH - 32),
                random.randint(0, WORLD_HEIGHT - 32)
            )
            player_rect = pygame.Rect(spawn_pos.x, spawn_pos.y, 32, 32)
            valid_spawn = True
            for obj in game_state.buildings:
                if obj.collides_with(player_rect):
                    valid_spawn = False
                    break
        game_state.players.append(Player(spawn_pos.x, spawn_pos.y))
    
    valid_spawn = False
    spawn_pos = pygame.Vector2(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
    while not valid_spawn:
        player_rect = pygame.Rect(spawn_pos.x, spawn_pos.y, 32, 32)
        valid_spawn = True
        for obj in game_state.buildings:
            if obj.collides_with(player_rect):
                spawn_pos += pygame.Vector2(50, 50)  # Try a bit to the right and down
                player_rect = pygame.Rect(spawn_pos.x, spawn_pos.y, 32, 32)
                if not obj.collides_with(player_rect):
                    valid_spawn = True
                    break
                else:
                    valid_spawn = False
    
    human_player = Player(spawn_pos.x, spawn_pos.y, is_human=True)
    human_player.color = colors.BLUE  # Blue color for human player
    game_state.human_player = human_player
    game_state.players.append(human_player)

"""
:UPDATE
"""

def update_players(keys):
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

def update_projectiles():
    # update projectiles
    for projectile in game_state.projectiles[:]:
        projectile.update()

    handle_projectile_collisions(game_state.projectiles, game_state.players, game_state.buildings)   

""" handle the projectile collisions """
def handle_projectile_collisions(projectiles, players, buildings):
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
                        player.health -= 35
                        if projectile in projectiles:  # Double-check before removing
                            projectiles.remove(projectile)
                        break

def update_kill_circle():
    kill_circle.update(game_state.players)

""" Cleanup dead players and expired projectiles and what not"""
def expired_entity_cleanup():
    game_state.players[:] = [p for p in game_state.players if p.health > 0] # Remove dead players and expired projectiles
    game_state.projectiles[:] = [p for p in game_state.projectiles if p.lifetime > 0]

""" 
:DRAW
"""

def clear_screen():
    _screen.fill(colors.WHITE)

def draw_kill_circle():
    kill_circle.draw(_screen, main_camera)

def draw_winner():
    _screen.fill(colors.WHITE)
    if game_state.players:
        winner = game_state.players[0]
        # Center the camera on the winner
        main_camera.update(winner)
        
        # Draw buildings
        for obj in game_state.buildings:
            obj.draw(_screen, main_camera)
            
        winner.draw(_screen, main_camera)
        font = pygame.font.SysFont(None, 36)
        text = font.render("Winner!", True, colors.BLACK)
        _screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 50))
    pygame.display.flip()

""" draw all debug elements """
def draw_debug():
    # draw_grid_lines()
    draw_debug_coords()

def draw_grid_lines():
    # Draw grid lines to show movement (optional)
    grid_size = 32
    for x in range(0, WORLD_WIDTH, grid_size):
        _screen_x, _ = main_camera.world_to_screen_pos(x, 0)
        if 0 <= _screen_x <= SCREEN_WIDTH:
            pygame.draw.line(_screen, colors.GRAY, 
                            (_screen_x, 0), 
                            (_screen_x, SCREEN_HEIGHT))
    for y in range(0, WORLD_HEIGHT, grid_size):
        _, _screen_y = main_camera.world_to_screen_pos(0, y)
        if 0 <= _screen_y <= SCREEN_HEIGHT:
            pygame.draw.line(_screen, colors.GRAY, 
                            (0, _screen_y), 
                            (SCREEN_WIDTH, _screen_y))
            
def draw_ground():
    ground.draw(_screen, main_camera)
            
def draw_debug_coords():
    if game_state.human_player in game_state.players:
        font = pygame.font.SysFont(None, 24)
        coords_text = f"X: {int(game_state.human_player.pos.x)}, Y: {int(game_state.human_player.pos.y)}"
        text_surface = font.render(coords_text, True, colors.BLACK)
        _screen.blit(text_surface, (10, 10))
            
def draw_buildings():
    for building in game_state.buildings:
        building.draw(_screen, main_camera)

""" Draw everything with camera offset """
def draw_camera_offset_entities():
    for player in game_state.players:
        player.draw(_screen, main_camera)
    for projectile in game_state.projectiles:
        projectile.draw(_screen, main_camera)