import pygame
import random
import colors
from player import Player
from game_state import GameState
from camera import Camera
from globals import WORLD_WIDTH, WORLD_HEIGHT

game_state = GameState()
main_camera = Camera()

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