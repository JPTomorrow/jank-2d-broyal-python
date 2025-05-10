import pygame
from globals import SCREEN_WIDTH, SCREEN_HEIGHT

class Camera:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
    
    def update(self, target):
        # Center the camera on the target
        camera_pos = pygame.Vector2(
            target.pos.x + target.rect.width // 2 - self.width // 2,
            target.pos.y + target.rect.height // 2 - self.height // 2
        )
        
        # Keep the camera within world bounds (optional, can be removed for truly unbounded world)
        # camera_pos.x = max(0, min(camera_pos.x, WORLD_WIDTH - self.width))
        # camera_pos.y = max(0, min(camera_pos.y, WORLD_HEIGHT - self.height))
        
        self.rect.x = camera_pos.x
        self.rect.y = camera_pos.y
    
    def apply(self, entity):
        # Return a rect with camera-adjusted coordinates
        return pygame.Rect(entity.rect.x - self.rect.x, entity.rect.y - self.rect.y, 
                          entity.rect.width, entity.rect.height)
    
    def apply_rect(self, rect):
        # Apply camera offset to a pygame Rect
        return pygame.Rect(
            rect.x - self.rect.x,
            rect.y - self.rect.y,
            rect.width,
            rect.height
        )
    
    def world_to_screen_pos(self, world_x, world_y):
        # Convert world coordinates to screen coordinates
        screen_pos = pygame.Vector2(world_x, world_y) - pygame.Vector2(self.rect.topleft)
        return screen_pos.x, screen_pos.y
    
    def screen_to_world_pos(self, screen_x, screen_y):
        # Convert screen coordinates to world coordinates
        world_pos = pygame.Vector2(screen_x, screen_y) + pygame.Vector2(self.rect.topleft)
        return world_pos.x, world_pos.y
