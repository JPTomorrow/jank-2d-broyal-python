import pygame
import colors
from globals import WORLD_WIDTH, WORLD_HEIGHT

class KillCircle:
    def __init__(self):
        self.safe_area = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
        self.shrink_timer = 0
        self.damage = 1
    
    def update(self, players):
        self.shrink_timer += 1
        if self.shrink_timer >= 1800:  # Shrink every 30 seconds
            self.shrink_timer = 0
            new_width = self.safe_area.width * 0.9
            new_height = self.safe_area.height * 0.9
            new_pos = pygame.Vector2(
                self.safe_area.x + (self.safe_area.width - new_width) / 2,
                self.safe_area.y + (self.safe_area.height - new_height) / 2
            )
            self.safe_area = pygame.Rect(new_pos.x, new_pos.y, new_width, new_height)

        # Damage players outside of area
        for player in players:
            if not self.safe_area.contains(player.rect):
                player.health -= self.damage

    # Draw safe area with camera offset
    def draw(self, screen, main_cam): 
        safe_area_camera = main_cam.apply_rect(self.safe_area)
        pygame.draw.rect(screen, colors.RED, safe_area_camera, 5, border_radius=20)