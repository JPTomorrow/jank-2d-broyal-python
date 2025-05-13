import pygame
import random
import os
import colors
from pygame import mask

class Buildings:
    def __init__(self, x, y, building_type=1, rotation=0):
        self.pos = pygame.Vector2(x, y)
        self.building_type = building_type
        self.rotation = rotation  # Rotation in degrees
        
        # Load original wall and floor sprites
        self.original_wall_sprite = pygame.image.load(f"res/buildings/building_{building_type}.png").convert_alpha()
        self.original_floor_sprite = pygame.image.load(f"res/buildings/building_floor_{building_type}.png").convert_alpha()
        
        # Rotate sprites
        self.wall_sprite = pygame.transform.rotate(self.original_wall_sprite, self.rotation)
        self.floor_sprite = pygame.transform.rotate(self.original_floor_sprite, self.rotation)
        
        # Set dimensions based on rotated sprite size
        self.width = self.wall_sprite.get_width()
        self.height = self.wall_sprite.get_height()
        
        # Create rect for basic positioning, centered at the rotation point
        self.rect = self.wall_sprite.get_rect(center=(x + self.original_wall_sprite.get_width() // 2, 
                                                     y + self.original_wall_sprite.get_height() // 2))
        self.pos = pygame.Vector2(self.rect.x, self.rect.y)  # Update position to match the rect
        
        # Generate collision mask from rotated wall sprite
        self.collision_mask = mask.from_surface(self.wall_sprite)
        self.collision_outline = self.collision_mask.outline()
        
        # Adjust collision outline to world coordinates
        self.world_collision_outline = [(self.pos.x + point[0], self.pos.y + point[1]) 
                                        for point in self.collision_outline]
    
    def draw(self, screen, camera):
        # Get camera-adjusted position for both sprites
        camera_rect = camera.apply_rect(self.rect)
        
        # Draw floor sprite first
        screen.blit(self.floor_sprite, camera_rect.topleft)
        
        # Draw wall sprite on top
        screen.blit(self.wall_sprite, camera_rect.topleft)
        
        # Debug: Draw collision outline
        # camera_outline = [(camera.world_to_screen_pos(x, y)) for x, y in self.world_collision_outline]
        # if len(camera_outline) > 2:
        #     pygame.draw.polygon(screen, colors.RED, camera_outline, 1)
    
    def collides_with(self, rect):
        """Check if the given rect collides with the building's collision mask"""
        # First do a quick check with the bounding rect
        if not rect.colliderect(self.rect):
            return False
        
        # If the bounding rects collide, do a more precise check with the mask
        # Create a rect for the object relative to the building's position
        rel_rect = pygame.Rect(
            rect.x - self.pos.x,
            rect.y - self.pos.y,
            rect.width,
            rect.height
        )
        
        # Create a mask for the object
        obj_mask = mask.Mask((rel_rect.width, rel_rect.height), fill=True)
        
        # Check if the masks overlap
        offset = (rel_rect.x, rel_rect.y)
        return self.collision_mask.overlap(obj_mask, offset) is not None

def create_buildings(WORLD_WIDTH, WORLD_HEIGHT):
    """Create buildings for the game world"""
    buildings = []
    
    # Get available building types
    building_types = []
    for file in os.listdir("res/buildings"):
        if file.startswith("building_") and file.endswith(".png") and not "floor" in file:
            # Extract the building type number
            type_num = int(file.split("_")[1].split(".")[0])
            if type_num not in building_types:
                building_types.append(type_num)
    
    # If no building types found, use default type 1
    if not building_types:
        building_types = [1]
    
    # Create some random buildings
    num_buildings = 30
    
    # Create a list to track building positions to avoid overlap
    building_rects = []
    
    for _ in range(num_buildings):
        # Randomly select a building type
        building_type = random.choice(building_types)
        
        # Load the sprite to get its dimensions
        temp_sprite = pygame.image.load(f"res/buildings/building_{building_type}.png").convert_alpha()
        width = temp_sprite.get_width()
        height = temp_sprite.get_height()
        
        # Try to find a position that doesn't overlap with existing buildings
        max_attempts = 50
        for attempt in range(max_attempts):
            # Generate random position
            x = random.randint(50, WORLD_WIDTH - width - 50)
            y = random.randint(50, WORLD_HEIGHT - height - 50)
            
            # Create a rect for this position
            new_rect = pygame.Rect(x, y, width, height)
            
            # Check for overlap with existing buildings
            overlap = False
            for existing_rect in building_rects:
                # Add some padding to avoid buildings being too close
                padded_rect = existing_rect.inflate(50, 50)
                if padded_rect.colliderect(new_rect):
                    overlap = True
                    break
            
            # If no overlap, we can place the building here
            if not overlap:
                building_rects.append(new_rect)
                # Generate random rotation (0, 90, 180, or 270 degrees)
                rotation = random.choice([0, 90, 180, 270])
                buildings.append(Buildings(x, y, building_type, rotation))
                break
    
    return buildings
