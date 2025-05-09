import pygame

# World dimensions (same as in main.py)
WORLD_WIDTH, WORLD_HEIGHT = 3000, 3000

class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
    
    def update(self, target):
        # Center the camera on the target
        x = target.x + target.rect.width // 2 - self.width // 2
        y = target.y + target.rect.height // 2 - self.height // 2
        
        # Keep the camera within world bounds (optional, can be removed for truly unbounded world)
        # x = max(0, min(x, WORLD_WIDTH - self.width))
        # y = max(0, min(y, WORLD_HEIGHT - self.height))
        
        self.rect.x = x
        self.rect.y = y
    
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
        screen_x = world_x - self.rect.x
        screen_y = world_y - self.rect.y
        return screen_x, screen_y
    
    def screen_to_world_pos(self, screen_x, screen_y):
        # Convert screen coordinates to world coordinates
        world_x = screen_x + self.rect.x
        world_y = screen_y + self.rect.y
        return world_x, world_y
