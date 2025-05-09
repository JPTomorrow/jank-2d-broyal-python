import pygame
import random
import sys
import math

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
BROWN = (139, 69, 19)

# Camera class to follow the player
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

# World object class for obstacles (buildings)
class WorldObject:
    def __init__(self, x, y, width, height, wall_thickness=10, door_width=48, is_complex=False, sub_rooms=None):
        self.rect = pygame.Rect(x, y, width, height)  # Outer rectangle (full building)
        self.wall_thickness = wall_thickness
        self.door_width = door_width
        self.color = BROWN
        self.is_complex = is_complex
        self.sub_rooms = sub_rooms or []  # List of sub-rooms for complex buildings
        
        # Create inner rectangle (hollow area)
        inner_x = x + wall_thickness
        inner_y = y + wall_thickness
        inner_width = max(0, width - 2 * wall_thickness)
        inner_height = max(0, height - 2 * wall_thickness)
        self.inner_rect = pygame.Rect(inner_x, inner_y, inner_width, inner_height)
        
        # Wall rectangles for collision detection
        self.wall_rects = []
        
        # Door rectangles (no collision)
        self.door_rects = []
        
        if not is_complex:
            # Simple building with one room
            # Determine which wall will have the door (randomly)
            self.door_wall = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left
            
            # Calculate door position (centered on the wall)
            if self.door_wall == 0:  # Top wall
                door_x = x + (width - door_width) // 2
                door_y = y
                door_width_actual = door_width
                door_height = wall_thickness
            elif self.door_wall == 1:  # Right wall
                door_x = x + width - wall_thickness
                door_y = y + (height - door_width) // 2
                door_width_actual = wall_thickness
                door_height = door_width
            elif self.door_wall == 2:  # Bottom wall
                door_x = x + (width - door_width) // 2
                door_y = y + height - wall_thickness
                door_width_actual = door_width
                door_height = wall_thickness
            else:  # Left wall
                door_x = x
                door_y = y + (height - door_width) // 2
                door_width_actual = wall_thickness
                door_height = door_width
            
            self.door_rects.append(pygame.Rect(door_x, door_y, door_width_actual, door_height))
            
            # Create wall rectangles for collision detection (excluding the door area)
            if self.door_wall == 0:  # Top wall with door
                self.wall_rects = [
                    pygame.Rect(x, y, door_x - x, wall_thickness),  # Top wall left of door
                    pygame.Rect(door_x + door_width, y, x + width - (door_x + door_width), wall_thickness),  # Top wall right of door
                    pygame.Rect(x, y + height - wall_thickness, width, wall_thickness),  # Bottom wall
                    pygame.Rect(x, y + wall_thickness, wall_thickness, height - 2 * wall_thickness),  # Left wall
                    pygame.Rect(x + width - wall_thickness, y + wall_thickness, wall_thickness, height - 2 * wall_thickness)  # Right wall
                ]
            elif self.door_wall == 1:  # Right wall with door
                self.wall_rects = [
                    pygame.Rect(x, y, width, wall_thickness),  # Top wall
                    pygame.Rect(x, y + height - wall_thickness, width, wall_thickness),  # Bottom wall
                    pygame.Rect(x, y + wall_thickness, wall_thickness, height - 2 * wall_thickness),  # Left wall
                    pygame.Rect(x + width - wall_thickness, y, wall_thickness, door_y - y),  # Right wall above door
                    pygame.Rect(x + width - wall_thickness, door_y + door_height, wall_thickness, y + height - (door_y + door_height) - wall_thickness)  # Right wall below door
                ]
            elif self.door_wall == 2:  # Bottom wall with door
                self.wall_rects = [
                    pygame.Rect(x, y, width, wall_thickness),  # Top wall
                    pygame.Rect(x, y + height - wall_thickness, door_x - x, wall_thickness),  # Bottom wall left of door
                    pygame.Rect(door_x + door_width, y + height - wall_thickness, x + width - (door_x + door_width), wall_thickness),  # Bottom wall right of door
                    pygame.Rect(x, y + wall_thickness, wall_thickness, height - 2 * wall_thickness),  # Left wall
                    pygame.Rect(x + width - wall_thickness, y + wall_thickness, wall_thickness, height - 2 * wall_thickness)  # Right wall
                ]
            else:  # Left wall with door
                self.wall_rects = [
                    pygame.Rect(x, y, width, wall_thickness),  # Top wall
                    pygame.Rect(x, y + height - wall_thickness, width, wall_thickness),  # Bottom wall
                    pygame.Rect(x, y, wall_thickness, door_y - y),  # Left wall above door
                    pygame.Rect(x, door_y + door_height, wall_thickness, y + height - (door_y + door_height) - wall_thickness),  # Left wall below door
                    pygame.Rect(x + width - wall_thickness, y + wall_thickness, wall_thickness, height - 2 * wall_thickness)  # Right wall
                ]
        else:
            # Complex building with multiple rooms
            # Each sub-room is a tuple (rect, has_door_north, has_door_east, has_door_south, has_door_west)
            for room_data in self.sub_rooms:
                room_rect, has_door_north, has_door_east, has_door_south, has_door_west = room_data
                
                # Add exterior walls for this room
                room_x, room_y = room_rect.x, room_rect.y
                room_width, room_height = room_rect.width, room_rect.height
                
                # Add walls for this room (with doors where specified)
                # North wall
                if has_door_north:
                    door_x = room_x + (room_width - door_width) // 2
                    door_y = room_y
                    self.door_rects.append(pygame.Rect(door_x, door_y, door_width, wall_thickness))
                    # Add wall segments on either side of the door
                    self.wall_rects.append(pygame.Rect(room_x, room_y, door_x - room_x, wall_thickness))
                    self.wall_rects.append(pygame.Rect(door_x + door_width, room_y, 
                                                     room_x + room_width - (door_x + door_width), wall_thickness))
                else:
                    self.wall_rects.append(pygame.Rect(room_x, room_y, room_width, wall_thickness))
                
                # East wall
                if has_door_east:
                    door_x = room_x + room_width - wall_thickness
                    door_y = room_y + (room_height - door_width) // 2
                    self.door_rects.append(pygame.Rect(door_x, door_y, wall_thickness, door_width))
                    # Add wall segments above and below the door
                    self.wall_rects.append(pygame.Rect(door_x, room_y + wall_thickness, 
                                                     wall_thickness, door_y - (room_y + wall_thickness)))
                    self.wall_rects.append(pygame.Rect(door_x, door_y + door_width, 
                                                     wall_thickness, room_y + room_height - wall_thickness - (door_y + door_width)))
                else:
                    self.wall_rects.append(pygame.Rect(room_x + room_width - wall_thickness, 
                                                     room_y + wall_thickness, 
                                                     wall_thickness, 
                                                     room_height - 2 * wall_thickness))
                
                # South wall
                if has_door_south:
                    door_x = room_x + (room_width - door_width) // 2
                    door_y = room_y + room_height - wall_thickness
                    self.door_rects.append(pygame.Rect(door_x, door_y, door_width, wall_thickness))
                    # Add wall segments on either side of the door
                    self.wall_rects.append(pygame.Rect(room_x, door_y, door_x - room_x, wall_thickness))
                    self.wall_rects.append(pygame.Rect(door_x + door_width, door_y, 
                                                     room_x + room_width - (door_x + door_width), wall_thickness))
                else:
                    self.wall_rects.append(pygame.Rect(room_x, room_y + room_height - wall_thickness, 
                                                     room_width, wall_thickness))
                
                # West wall
                if has_door_west:
                    door_x = room_x
                    door_y = room_y + (room_height - door_width) // 2
                    self.door_rects.append(pygame.Rect(door_x, door_y, wall_thickness, door_width))
                    # Add wall segments above and below the door
                    self.wall_rects.append(pygame.Rect(door_x, room_y + wall_thickness, 
                                                     wall_thickness, door_y - (room_y + wall_thickness)))
                    self.wall_rects.append(pygame.Rect(door_x, door_y + door_width, 
                                                     wall_thickness, room_y + room_height - wall_thickness - (door_y + door_width)))
                else:
                    self.wall_rects.append(pygame.Rect(room_x, room_y + wall_thickness, 
                                                     wall_thickness, room_height - 2 * wall_thickness))
            
            # Add exterior door (randomly placed on the outer perimeter)
            outer_perimeter = []
            
            # Find the outer perimeter walls
            for wall in self.wall_rects:
                # Check if this wall is on the outer perimeter
                is_outer = True
                for room_data in self.sub_rooms:
                    room_rect = room_data[0]
                    # If the wall is completely inside another room, it's not on the outer perimeter
                    if (wall.x > room_rect.x and wall.x + wall.width < room_rect.x + room_rect.width and
                        wall.y > room_rect.y and wall.y + wall.height < room_rect.y + room_rect.height):
                        is_outer = False
                        break
                
                if is_outer:
                    outer_perimeter.append(wall)
            
            # Add an exterior door on a random outer wall
            if outer_perimeter:
                outer_wall = random.choice(outer_perimeter)
                
                # Determine if it's a horizontal or vertical wall
                if outer_wall.height <= wall_thickness:  # Horizontal wall
                    door_x = outer_wall.x + (outer_wall.width - door_width) // 2
                    door_y = outer_wall.y
                    door_rect = pygame.Rect(door_x, door_y, door_width, wall_thickness)
                    
                    # Remove the wall segment where the door will be
                    self.wall_rects.remove(outer_wall)
                    
                    # Add wall segments on either side of the door
                    if door_x > outer_wall.x:
                        self.wall_rects.append(pygame.Rect(outer_wall.x, outer_wall.y, 
                                                         door_x - outer_wall.x, wall_thickness))
                    if door_x + door_width < outer_wall.x + outer_wall.width:
                        self.wall_rects.append(pygame.Rect(door_x + door_width, outer_wall.y, 
                                                         outer_wall.x + outer_wall.width - (door_x + door_width), 
                                                         wall_thickness))
                    
                    self.door_rects.append(door_rect)
                    
                else:  # Vertical wall
                    door_x = outer_wall.x
                    door_y = outer_wall.y + (outer_wall.height - door_width) // 2
                    door_rect = pygame.Rect(door_x, door_y, wall_thickness, door_width)
                    
                    # Remove the wall segment where the door will be
                    self.wall_rects.remove(outer_wall)
                    
                    # Add wall segments above and below the door
                    if door_y > outer_wall.y:
                        self.wall_rects.append(pygame.Rect(outer_wall.x, outer_wall.y, 
                                                         wall_thickness, door_y - outer_wall.y))
                    if door_y + door_width < outer_wall.y + outer_wall.height:
                        self.wall_rects.append(pygame.Rect(outer_wall.x, door_y + door_width, 
                                                         wall_thickness, 
                                                         outer_wall.y + outer_wall.height - (door_y + door_width)))
                    
                    self.door_rects.append(door_rect)
        
        # Remove any wall rects with zero or negative dimensions
        self.wall_rects = [rect for rect in self.wall_rects if rect.width > 0 and rect.height > 0]
    
    def draw(self, screen, camera):
        # Draw the outer walls
        for wall_rect in self.wall_rects:
            # Apply camera offset to wall rect
            camera_wall_rect = pygame.Rect(
                wall_rect.x - camera.rect.x,
                wall_rect.y - camera.rect.y,
                wall_rect.width,
                wall_rect.height
            )
            pygame.draw.rect(screen, self.color, camera_wall_rect)
    
    def collides_with(self, rect):
        """Check if the given rect collides with any of the building's walls"""
        for wall_rect in self.wall_rects:
            if rect.colliderect(wall_rect):
                return True
        return False

class Player:
    def __init__(self, x, y, is_human=False):
        self.x = x
        self.y = y
        self.health = 100
        self.speed = 2
        self.width = 32
        self.height = 32
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.shoot_timer = 0
        self.is_human = is_human
        # Add a view range for AI players
        self.view_range = 400  # AI can only see players within this range
        # Add velocity for collision resolution
        self.vx = 0
        self.vy = 0

    def find_nearest(self, others):
        min_dist = float('inf')
        nearest = None
        for other in others:
            if other != self:
                dist = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
                # Only consider players within view range for AI
                if dist < min_dist and (self.is_human or dist <= self.view_range):
                    min_dist = dist
                    nearest = other
        return nearest

    def move_towards(self, target, world_objects, players):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > 0:
            dx /= dist
            dy /= dist
            
            # Calculate new position
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            # Check for collisions with world objects
            new_rect_x = pygame.Rect(new_x, self.y, self.width, self.height)
            new_rect_y = pygame.Rect(self.x, new_y, self.width, self.height)
            
            # Move in X direction if no collision
            x_collision = False
            for obj in world_objects:
                if obj.collides_with(new_rect_x):
                    x_collision = True
                    break
            
            # Check collision with other players in X direction
            for player in players:
                if player != self and new_rect_x.colliderect(player.rect):
                    x_collision = True
                    break
            
            if not x_collision:
                self.x = new_x
            
            # Move in Y direction if no collision
            y_collision = False
            for obj in world_objects:
                if obj.collides_with(new_rect_y):
                    y_collision = True
                    break
            
            # Check collision with other players in Y direction
            for player in players:
                if player != self and new_rect_y.colliderect(player.rect):
                    y_collision = True
                    break
            
            if not y_collision:
                self.y = new_y
            
            # Update rect position
            self.rect.topleft = (self.x, self.y)

    def update(self, projectiles, players, world_objects):
        if not self.is_human:
            self.shoot_timer += 1
            if self.shoot_timer >= 60:
                self.shoot_timer = 0
                nearest = self.find_nearest(players)
                if nearest:
                    dx = nearest.x - self.x
                    dy = nearest.y - self.y
                    dist = (dx ** 2 + dy ** 2) ** 0.5
                    if dist > 0 and dist <= self.view_range:  # Only shoot if within view range
                        dx /= dist
                        dy /= dist
                        projectiles.append(Projectile(self.x + 16, self.y + 16, dx * 5, dy * 5, self))
        else:
            # Human player shoots on spacebar press, handled in main loop
            self.shoot_timer += 1

    def draw(self, screen, camera):
        # Draw player with camera offset
        camera_rect = camera.apply(self)
        pygame.draw.rect(screen, self.color, camera_rect)
        
        # Draw health bar with camera offset
        health_width = 30 * (self.health / 100)
        health_bar_x = self.x - camera.rect.x + 1
        health_bar_y = self.y - camera.rect.y - 10
        pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, 30, 5))
        pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, health_width, 5))

class Projectile:
    def __init__(self, x, y, dx, dy, owner):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.rect = pygame.Rect(x, y, 5, 5)
        self.owner = owner
        self.lifetime = 300  # Add lifetime to prevent projectiles from traveling forever

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.topleft = (self.x, self.y)
        self.lifetime -= 1

    def draw(self, screen, camera):
        # Draw projectile with camera offset
        camera_rect = camera.apply(self)
        pygame.draw.rect(screen, (0, 0, 0), camera_rect)

def setup():
    global players, projectiles, safe_area, shrink_timer, human_player, camera, world_objects
    
    # Create world objects (obstacles)
    world_objects = []
    
    # Create some random walls/obstacles
    num_buildings = 30  # Reduced number of initial buildings to make room for complex shapes
    
    # First, create a list of building rectangles
    building_rects = []
    
    # Create some complex L-shaped and U-shaped buildings
    num_complex_buildings = 10
    for _ in range(num_complex_buildings):
        # Decide on a complex shape (L or U)
        shape_type = random.choice(["L", "U"])
        
        # Base rectangle dimensions
        base_width = random.randint(80, 150)
        base_height = random.randint(80, 150)
        base_x = random.randint(100, WORLD_WIDTH - 300)
        base_y = random.randint(100, WORLD_HEIGHT - 300)
        
        # Add the base rectangle
        base_rect = pygame.Rect(base_x, base_y, base_width, base_height)
        building_rects.append(base_rect)
        
        if shape_type == "L":
            # Add a second rectangle to form an L-shape
            # Randomly decide which side to extend from
            if random.choice([True, False]):
                # Extend horizontally
                extension_width = random.randint(80, 150)
                extension_height = random.randint(50, base_height - 20)
                extension_x = base_x + base_width - 10  # Overlap slightly
                extension_y = base_y + random.randint(0, base_height - extension_height)
            else:
                # Extend vertically
                extension_width = random.randint(50, base_width - 20)
                extension_height = random.randint(80, 150)
                extension_x = base_x + random.randint(0, base_width - extension_width)
                extension_y = base_y + base_height - 10  # Overlap slightly
            
            extension_rect = pygame.Rect(extension_x, extension_y, extension_width, extension_height)
            building_rects.append(extension_rect)
            
        elif shape_type == "U":
            # Add two extensions to form a U-shape
            # Decide orientation (horizontal or vertical U)
            if random.choice([True, False]):
                # Horizontal U
                # Left extension
                left_width = random.randint(40, 80)
                left_height = random.randint(80, 120)
                left_x = base_x - left_width + 10  # Overlap slightly
                left_y = base_y + (base_height - left_height) // 2
                
                # Right extension
                right_width = random.randint(40, 80)
                right_height = random.randint(80, 120)
                right_x = base_x + base_width - 10  # Overlap slightly
                right_y = base_y + (base_height - right_height) // 2
                
                building_rects.append(pygame.Rect(left_x, left_y, left_width, left_height))
                building_rects.append(pygame.Rect(right_x, right_y, right_width, right_height))
            else:
                # Vertical U
                # Top extension
                top_width = random.randint(80, 120)
                top_height = random.randint(40, 80)
                top_x = base_x + (base_width - top_width) // 2
                top_y = base_y - top_height + 10  # Overlap slightly
                
                # Bottom extension
                bottom_width = random.randint(80, 120)
                bottom_height = random.randint(40, 80)
                bottom_x = base_x + (base_width - bottom_width) // 2
                bottom_y = base_y + base_height - 10  # Overlap slightly
                
                building_rects.append(pygame.Rect(top_x, top_y, top_width, top_height))
                building_rects.append(pygame.Rect(bottom_x, bottom_y, bottom_width, bottom_height))
    
    # Add some regular buildings
    for _ in range(num_buildings):
        width = random.randint(50, 200)
        height = random.randint(50, 200)
        x = random.randint(0, WORLD_WIDTH - width)
        y = random.randint(0, WORLD_HEIGHT - height)
        
        # Create a new rectangle for this building
        new_rect = pygame.Rect(x, y, width, height)
        
        # Check if this building overlaps with any existing buildings
        overlaps = False
        for existing_rect in building_rects:
            if new_rect.colliderect(existing_rect):
                # If they overlap, create a combined shape by adding a connecting corridor
                # Find the overlapping area
                overlap_rect = new_rect.clip(existing_rect)
                
                # If the overlap is significant, just use the union of both rectangles
                if overlap_rect.width > 20 and overlap_rect.height > 20:
                    # Create a union rectangle that encompasses both buildings
                    union_left = min(new_rect.left, existing_rect.left)
                    union_top = min(new_rect.top, existing_rect.top)
                    union_right = max(new_rect.right, existing_rect.right)
                    union_bottom = max(new_rect.bottom, existing_rect.bottom)
                    
                    # Create a new rectangle for the combined shape
                    combined_rect = pygame.Rect(union_left, union_top, 
                                              union_right - union_left, 
                                              union_bottom - union_top)
                    
                    # Replace the existing rectangle with the combined one
                    building_rects.remove(existing_rect)
                    building_rects.append(combined_rect)
                    overlaps = True
                    break
        
        # If no significant overlap, check if buildings are close enough for a corridor
        if not overlaps:
            for existing_rect in building_rects:
                # If buildings are very close (within 40 pixels)
                if new_rect.inflate(80, 80).colliderect(existing_rect):
                    # Create a connecting corridor between buildings
                    if abs(new_rect.centerx - existing_rect.centerx) < abs(new_rect.centery - existing_rect.centery):
                        # Buildings are more aligned horizontally, create vertical corridor
                        if new_rect.centery < existing_rect.centery:
                            corridor_x = max(new_rect.left, existing_rect.left) + 20
                            corridor_y = new_rect.bottom - 10
                            corridor_width = min(new_rect.right, existing_rect.right) - corridor_x - 20
                            corridor_height = existing_rect.top - corridor_y + 10
                        else:
                            corridor_x = max(new_rect.left, existing_rect.left) + 20
                            corridor_y = existing_rect.bottom - 10
                            corridor_width = min(new_rect.right, existing_rect.right) - corridor_x - 20
                            corridor_height = new_rect.top - corridor_y + 10
                        
                        # Add the corridor as a new building if it has valid dimensions
                        if corridor_width > 40 and corridor_height > 20:
                            corridor_rect = pygame.Rect(corridor_x, corridor_y, corridor_width, corridor_height)
                            building_rects.append(corridor_rect)
                    else:
                        # Buildings are more aligned vertically, create horizontal corridor
                        if new_rect.centerx < existing_rect.centerx:
                            corridor_x = new_rect.right - 10
                            corridor_y = max(new_rect.top, existing_rect.top) + 20
                            corridor_width = existing_rect.left - corridor_x + 10
                            corridor_height = min(new_rect.bottom, existing_rect.bottom) - corridor_y - 20
                        else:
                            corridor_x = existing_rect.right - 10
                            corridor_y = max(new_rect.top, existing_rect.top) + 20
                            corridor_width = new_rect.left - corridor_x + 10
                            corridor_height = min(new_rect.bottom, existing_rect.bottom) - corridor_y - 20
                        
                        # Add the corridor as a new building if it has valid dimensions
                        if corridor_width > 20 and corridor_height > 40:
                            corridor_rect = pygame.Rect(corridor_x, corridor_y, corridor_width, corridor_height)
                            building_rects.append(corridor_rect)
                    break
        
        # Add the new building rectangle if it doesn't overlap significantly
        if not overlaps:
            building_rects.append(new_rect)
    
    # Process building rectangles to create complex buildings with interior doors
    processed_rects = set()
    
    # First, identify groups of overlapping rectangles
    building_groups = []
    
    for i, rect in enumerate(building_rects):
        if i in processed_rects:
            continue
        
        # Start a new group with this rectangle
        current_group = [i]
        processed_rects.add(i)
        
        # Find all rectangles that overlap with any rectangle in the current group
        changed = True
        while changed:
            changed = False
            for j, other_rect in enumerate(building_rects):
                if j in processed_rects:
                    continue
                
                # Check if this rectangle overlaps with any in the current group
                for group_idx in current_group:
                    if building_rects[group_idx].colliderect(other_rect) or \
                       building_rects[group_idx].inflate(20, 20).colliderect(other_rect):
                        current_group.append(j)
                        processed_rects.add(j)
                        changed = True
                        break
        
        # Add the group if it has more than one rectangle (complex building)
        if len(current_group) > 1:
            building_groups.append([building_rects[idx] for idx in current_group])
        else:
            # Single rectangle, create a simple building
            rect = building_rects[current_group[0]]
            world_objects.append(WorldObject(rect.x, rect.y, rect.width, rect.height))
    
    # Create complex buildings from the groups
    for group in building_groups:
        # Create sub-rooms with doors between them
        sub_rooms = []
        
        for i, room_rect in enumerate(group):
            # Determine which walls should have doors (connecting to other rooms)
            has_door_north = False
            has_door_east = False
            has_door_south = False
            has_door_west = False
            
            # Check for adjacent rooms in each direction
            for other_rect in group:
                if room_rect == other_rect:
                    continue
                
                # Check if rooms are adjacent or overlapping
                if room_rect.colliderect(other_rect) or room_rect.inflate(20, 20).colliderect(other_rect):
                    # Determine the relative position of the other room
                    if other_rect.centery < room_rect.centery and \
                       (other_rect.right > room_rect.left and other_rect.left < room_rect.right):
                        # Other room is to the north
                        has_door_north = True
                    
                    if other_rect.centerx > room_rect.centerx and \
                       (other_rect.bottom > room_rect.top and other_rect.top < room_rect.bottom):
                        # Other room is to the east
                        has_door_east = True
                    
                    if other_rect.centery > room_rect.centery and \
                       (other_rect.right > room_rect.left and other_rect.left < room_rect.right):
                        # Other room is to the south
                        has_door_south = True
                    
                    if other_rect.centerx < room_rect.centerx and \
                       (other_rect.bottom > room_rect.top and other_rect.top < room_rect.bottom):
                        # Other room is to the west
                        has_door_west = True
            
            # Add this room to the sub-rooms list
            sub_rooms.append((room_rect, has_door_north, has_door_east, has_door_south, has_door_west))
        
        # Find the bounding rectangle for the entire complex building
        min_x = min(rect.x for rect in group)
        min_y = min(rect.y for rect in group)
        max_x = max(rect.x + rect.width for rect in group)
        max_y = max(rect.y + rect.height for rect in group)
        
        # Create a complex building with the sub-rooms
        complex_building = WorldObject(
            min_x, min_y, max_x - min_x, max_y - min_y, 
            is_complex=True, sub_rooms=sub_rooms
        )
        
        world_objects.append(complex_building)
    
    # Create 9 AI players spread across the world (ensuring they don't spawn inside walls)
    players = []
    for _ in range(9):
        valid_spawn = False
        while not valid_spawn:
            x = random.randint(0, WORLD_WIDTH - 32)
            y = random.randint(0, WORLD_HEIGHT - 32)
            player_rect = pygame.Rect(x, y, 32, 32)
            valid_spawn = True
            for obj in world_objects:
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
        for obj in world_objects:
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

def update_game_state():
    global players, projectiles, safe_area, shrink_timer, human_player, camera, world_objects

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

    # Handle human player movement with WASD keys
    if human_player in players:
        # Calculate new positions based on key presses
        new_x = human_player.x
        new_y = human_player.y
        
        # W - move up
        if keys[pygame.K_w]:
            new_y -= human_player.speed
        # S - move down
        if keys[pygame.K_s]:
            new_y += human_player.speed
        # A - move left
        if keys[pygame.K_a]:
            new_x -= human_player.speed
        # D - move right
        if keys[pygame.K_d]:
            new_x += human_player.speed
        
        # Check for collisions with world objects in X direction
        new_rect_x = pygame.Rect(new_x, human_player.y, human_player.width, human_player.height)
        x_collision = False
        for obj in world_objects:
            if obj.collides_with(new_rect_x):
                x_collision = True
                break
        
        # Check for collisions with other players in X direction
        for player in players:
            if player != human_player and new_rect_x.colliderect(player.rect):
                x_collision = True
                break
        
        if not x_collision:
            human_player.x = new_x
        
        # Check for collisions with world objects in Y direction
        new_rect_y = pygame.Rect(human_player.x, new_y, human_player.width, human_player.height)
        y_collision = False
        for obj in world_objects:
            if obj.collides_with(new_rect_y):
                y_collision = True
                break
        
        # Check for collisions with other players in Y direction
        for player in players:
            if player != human_player and new_rect_y.colliderect(player.rect):
                y_collision = True
                break
        
        if not y_collision:
            human_player.y = new_y
        
        # Update rect position
        human_player.rect.topleft = (human_player.x, human_player.y)
        
        # Update camera to follow human player
        camera.update(human_player)
        
        # Handle shooting for human player
        if keys[pygame.K_SPACE] and human_player.shoot_timer >= 30:
            human_player.shoot_timer = 0
            
            # Get mouse position (in screen coordinates)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Convert mouse position to world coordinates
            world_mouse_x = mouse_x + camera.rect.x
            world_mouse_y = mouse_y + camera.rect.y
            
            # Calculate direction from player to mouse
            direction_x = world_mouse_x - (human_player.x + 16)
            direction_y = world_mouse_y - (human_player.y + 16)
            
            # Normalize direction
            magnitude = (direction_x**2 + direction_y**2)**0.5
            if magnitude > 0:
                direction_x /= magnitude
                direction_y /= magnitude
                
            projectiles.append(Projectile(human_player.x + 16, human_player.y + 16, 
                                         direction_x * 5, direction_y * 5, human_player))

    # Update players and projectiles
    for player in players[:]:
        if player.is_human:
            player.update(projectiles, players, world_objects)
        else:
            player.update(projectiles, players, world_objects)
            # AI players move towards nearest player if one is found
            nearest = player.find_nearest(players)
            if nearest:
                player.move_towards(nearest, world_objects, players)

    for projectile in projectiles[:]:
        projectile.update()

    # Check collisions
    for projectile in projectiles[:]:
        if projectile in projectiles:  # Check if projectile still exists
            # Check collision with buildings
            for obj in world_objects:
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

def draw_game():
    screen.fill(WHITE)
    
    # Draw safe area with camera offset
    safe_area_camera = pygame.Rect(
        safe_area.x - camera.rect.x,
        safe_area.y - camera.rect.y,
        safe_area.width,
        safe_area.height
    )
    pygame.draw.rect(screen, GREEN, safe_area_camera, 1)
    
    # Draw grid lines to show movement (optional)
    grid_size = 100
    for x in range(0, WORLD_WIDTH, grid_size):
        if 0 <= x - camera.rect.x <= SCREEN_WIDTH:
            pygame.draw.line(screen, GRAY, 
                            (x - camera.rect.x, 0), 
                            (x - camera.rect.x, SCREEN_HEIGHT))
    for y in range(0, WORLD_HEIGHT, grid_size):
        if 0 <= y - camera.rect.y <= SCREEN_HEIGHT:
            pygame.draw.line(screen, GRAY, 
                            (0, y - camera.rect.y), 
                            (SCREEN_WIDTH, y - camera.rect.y))
    
    # Draw world objects (obstacles)
    for obj in world_objects:
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
        text_surface = font.render(coords_text, True, (0, 0, 0))
        screen.blit(text_surface, (10, 10))

    pygame.display.flip()

def draw_winner():
    screen.fill(WHITE)
    if players:
        winner = players[0]
        # Center the winner on screen
        camera.rect.x = winner.x + winner.rect.width // 2 - SCREEN_WIDTH // 2
        camera.rect.y = winner.y + winner.rect.height // 2 - SCREEN_HEIGHT // 2
        
        # Draw world objects
        for obj in world_objects:
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
            update_game_state()
            draw_game()
        elif not game_over:
            game_over = True
            draw_winner()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
