import pygame
import random
import colors

# Class for buildings
class Buildings:
    def __init__(self, x, y, width, height, wall_thickness=10, door_width=48, is_complex=False, sub_rooms=None):
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, width, height)  # Outer rectangle (full building)
        self.wall_thickness = wall_thickness
        self.door_width = door_width
        self.color = colors.BROWN
        self.is_complex = is_complex
        self.sub_rooms = sub_rooms or []  # List of sub-rooms for complex buildings
        
        # Create inner rectangle (hollow area)
        inner_pos = self.pos + pygame.Vector2(wall_thickness, wall_thickness)
        inner_width = max(0, width - 2 * wall_thickness)
        inner_height = max(0, height - 2 * wall_thickness)
        self.inner_rect = pygame.Rect(inner_pos.x, inner_pos.y, inner_width, inner_height)
        
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
                door_pos = pygame.Vector2(
                    x + (width - door_width) // 2,
                    y
                )
                door_width_actual = door_width
                door_height = wall_thickness
            elif self.door_wall == 1:  # Right wall
                door_pos = pygame.Vector2(
                    x + width - wall_thickness,
                    y + (height - door_width) // 2
                )
                door_width_actual = wall_thickness
                door_height = door_width
            elif self.door_wall == 2:  # Bottom wall
                door_pos = pygame.Vector2(
                    x + (width - door_width) // 2,
                    y + height - wall_thickness
                )
                door_width_actual = door_width
                door_height = wall_thickness
            else:  # Left wall
                door_pos = pygame.Vector2(
                    x,
                    y + (height - door_width) // 2
                )
                door_width_actual = wall_thickness
                door_height = door_width
            
            self.door_rects.append(pygame.Rect(door_pos.x, door_pos.y, door_width_actual, door_height))
            
            # Create wall rectangles for collision detection (excluding the door area)
            if self.door_wall == 0:  # Top wall with door
                self.wall_rects = [
                    pygame.Rect(x, y, door_pos.x - x, wall_thickness),  # Top wall left of door
                    pygame.Rect(door_pos.x + door_width, y, x + width - (door_pos.x + door_width), wall_thickness),  # Top wall right of door
                    pygame.Rect(x, y + height - wall_thickness, width, wall_thickness),  # Bottom wall
                    pygame.Rect(x, y + wall_thickness, wall_thickness, height - 2 * wall_thickness),  # Left wall
                    pygame.Rect(x + width - wall_thickness, y + wall_thickness, wall_thickness, height - 2 * wall_thickness)  # Right wall
                ]
            elif self.door_wall == 1:  # Right wall with door
                self.wall_rects = [
                    pygame.Rect(x, y, width, wall_thickness),  # Top wall
                    pygame.Rect(x, y + height - wall_thickness, width, wall_thickness),  # Bottom wall
                    pygame.Rect(x, y + wall_thickness, wall_thickness, height - 2 * wall_thickness),  # Left wall
                    pygame.Rect(x + width - wall_thickness, y, wall_thickness, door_pos.y - y),  # Right wall above door
                    pygame.Rect(x + width - wall_thickness, door_pos.y + door_height, wall_thickness, y + height - (door_pos.y + door_height) - wall_thickness)  # Right wall below door
                ]
            elif self.door_wall == 2:  # Bottom wall with door
                self.wall_rects = [
                    pygame.Rect(x, y, width, wall_thickness),  # Top wall
                    pygame.Rect(x, y + height - wall_thickness, door_pos.x - x, wall_thickness),  # Bottom wall left of door
                    pygame.Rect(door_pos.x + door_width, y + height - wall_thickness, x + width - (door_pos.x + door_width), wall_thickness),  # Bottom wall right of door
                    pygame.Rect(x, y + wall_thickness, wall_thickness, height - 2 * wall_thickness),  # Left wall
                    pygame.Rect(x + width - wall_thickness, y + wall_thickness, wall_thickness, height - 2 * wall_thickness)  # Right wall
                ]
            else:  # Left wall with door
                self.wall_rects = [
                    pygame.Rect(x, y, width, wall_thickness),  # Top wall
                    pygame.Rect(x, y + height - wall_thickness, width, wall_thickness),  # Bottom wall
                    pygame.Rect(x, y, wall_thickness, door_pos.y - y),  # Left wall above door
                    pygame.Rect(x, door_pos.y + door_height, wall_thickness, y + height - (door_pos.y + door_height) - wall_thickness),  # Left wall below door
                    pygame.Rect(x + width - wall_thickness, y + wall_thickness, wall_thickness, height - 2 * wall_thickness)  # Right wall
                ]
        else:
            # Complex building with multiple rooms
            # Each sub-room is a tuple (rect, has_door_north, has_door_east, has_door_south, has_door_west)
            for room_data in self.sub_rooms:
                room_rect, has_door_north, has_door_east, has_door_south, has_door_west = room_data
                
                # Add exterior walls for this room
                # room_pos.x, room_pos.y = room_rect.x, room_rect.y
                room_width, room_height = room_rect.width, room_rect.height
                
                # Add walls for this room (with doors where specified)
                room_pos = pygame.Vector2(room_rect.x, room_rect.y)
                
                # North wall
                if has_door_north:
                    door_pos = pygame.Vector2(
                        room_pos.x + (room_width - door_width) // 2,
                        room_pos.y
                    )
                    self.door_rects.append(pygame.Rect(door_pos.x, door_pos.y, door_width, wall_thickness))
                    # Add wall segments on either side of the door
                    self.wall_rects.append(pygame.Rect(room_pos.x, room_pos.y, door_pos.x - room_pos.x, wall_thickness))
                    self.wall_rects.append(pygame.Rect(door_pos.x + door_width, room_pos.y, 
                                                     room_pos.x + room_width - (door_pos.x + door_width), wall_thickness))
                else:
                    self.wall_rects.append(pygame.Rect(room_pos.x, room_pos.y, room_width, wall_thickness))
                
                # East wall
                if has_door_east:
                    door_pos = pygame.Vector2(
                        room_pos.x + room_width - wall_thickness,
                        room_pos.y + (room_height - door_width) // 2
                    )
                    self.door_rects.append(pygame.Rect(door_pos.x, door_pos.y, wall_thickness, door_width))
                    # Add wall segments above and below the door
                    self.wall_rects.append(pygame.Rect(door_pos.x, room_pos.y + wall_thickness, 
                                                     wall_thickness, door_pos.y - (room_pos.y + wall_thickness)))
                    self.wall_rects.append(pygame.Rect(door_pos.x, door_pos.y + door_width, 
                                                     wall_thickness, room_pos.y + room_height - wall_thickness - (door_pos.y + door_width)))
                else:
                    self.wall_rects.append(pygame.Rect(room_pos.x + room_width - wall_thickness, 
                                                     room_pos.y + wall_thickness, 
                                                     wall_thickness, 
                                                     room_height - 2 * wall_thickness))
                
                # South wall
                if has_door_south:
                    door_pos = pygame.Vector2(
                        room_pos.x + (room_width - door_width) // 2,
                        room_pos.y + room_height - wall_thickness
                    )
                    self.door_rects.append(pygame.Rect(door_pos.x, door_pos.y, door_width, wall_thickness))
                    # Add wall segments on either side of the door
                    self.wall_rects.append(pygame.Rect(room_pos.x, door_pos.y, door_pos.x - room_pos.x, wall_thickness))
                    self.wall_rects.append(pygame.Rect(door_pos.x + door_width, door_pos.y, 
                                                     room_pos.x + room_width - (door_pos.x + door_width), wall_thickness))
                else:
                    self.wall_rects.append(pygame.Rect(room_pos.x, room_pos.y + room_height - wall_thickness, 
                                                     room_width, wall_thickness))
                
                # West wall
                if has_door_west:
                    door_pos = pygame.Vector2(
                        room_pos.x,
                        room_pos.y + (room_height - door_width) // 2
                    )
                    self.door_rects.append(pygame.Rect(door_pos.x, door_pos.y, wall_thickness, door_width))
                    # Add wall segments above and below the door
                    self.wall_rects.append(pygame.Rect(door_pos.x, room_pos.y + wall_thickness, 
                                                     wall_thickness, door_pos.y - (room_pos.y + wall_thickness)))
                    self.wall_rects.append(pygame.Rect(door_pos.x, door_pos.y + door_width, 
                                                     wall_thickness, room_pos.y + room_height - wall_thickness - (door_pos.y + door_width)))
                else:
                    self.wall_rects.append(pygame.Rect(room_pos.x, room_pos.y + wall_thickness, 
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
                    door_pos = pygame.Vector2(
                        outer_wall.x + (outer_wall.width - door_width) // 2,
                        outer_wall.y
                    )
                    door_rect = pygame.Rect(door_pos.x, door_pos.y, door_width, wall_thickness)
                    
                    # Remove the wall segment where the door will be
                    self.wall_rects.remove(outer_wall)
                    
                    # Add wall segments on either side of the door
                    if door_pos.x > outer_wall.x:
                        self.wall_rects.append(pygame.Rect(outer_wall.x, outer_wall.y, 
                                                         door_pos.x - outer_wall.x, wall_thickness))
                    if door_pos.x + door_width < outer_wall.x + outer_wall.width:
                        self.wall_rects.append(pygame.Rect(door_pos.x + door_width, outer_wall.y, 
                                                         outer_wall.x + outer_wall.width - (door_pos.x + door_width), 
                                                         wall_thickness))
                    
                    self.door_rects.append(door_rect)
                    
                else:  # Vertical wall
                    door_pos = pygame.Vector2(
                        outer_wall.x,
                        outer_wall.y + (outer_wall.height - door_width) // 2
                    )
                    door_rect = pygame.Rect(door_pos.x, door_pos.y, wall_thickness, door_width)
                    
                    # Remove the wall segment where the door will be
                    self.wall_rects.remove(outer_wall)
                    
                    # Add wall segments above and below the door
                    if door_pos.y > outer_wall.y:
                        self.wall_rects.append(pygame.Rect(outer_wall.x, outer_wall.y, 
                                                         wall_thickness, door_pos.y - outer_wall.y))
                    if door_pos.y + door_width < outer_wall.y + outer_wall.height:
                        self.wall_rects.append(pygame.Rect(outer_wall.x, door_pos.y + door_width, 
                                                         wall_thickness, 
                                                         outer_wall.y + outer_wall.height - (door_pos.y + door_width)))
                    
                    self.door_rects.append(door_rect)
        
        # Remove any wall rects with zero or negative dimensions
        self.wall_rects = [rect for rect in self.wall_rects if rect.width > 0 and rect.height > 0]
    
    def draw(self, screen, camera):
        # Draw the outer walls
        for wall_rect in self.wall_rects:
            # Apply camera offset to wall rect
            camera_wall_rect = camera.apply_rect(wall_rect)
            pygame.draw.rect(screen, self.color, camera_wall_rect)
    
    def collides_with(self, rect):
        """Check if the given rect collides with any of the building's walls"""
        for wall_rect in self.wall_rects:
            if rect.colliderect(wall_rect):
                return True
        return False

def create_buildings(WORLD_WIDTH, WORLD_HEIGHT):
    """Create buildings for the game world"""
    buildings = []
    
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
        base_pos = pygame.Vector2(
            random.randint(100, WORLD_WIDTH - 300),
            random.randint(100, WORLD_HEIGHT - 300)
        )
        
        # Add the base rectangle
        base_rect = pygame.Rect(base_pos.x, base_pos.y, base_width, base_height)
        building_rects.append(base_rect)
        
        if shape_type == "L":
            # Add a second rectangle to form an L-shape
            # Randomly decide which side to extend from
            if random.choice([True, False]):
                # Extend horizontally
                extension_width = random.randint(80, 150)
                extension_height = random.randint(50, base_height - 20)
                extension_pos = pygame.Vector2(
                    base_pos.x + base_width - 10,  # Overlap slightly
                    base_pos.y + random.randint(0, base_height - extension_height)
                )
            else:
                # Extend vertically
                extension_width = random.randint(50, base_width - 20)
                extension_height = random.randint(80, 150)
                extension_pos = pygame.Vector2(
                    base_pos.x + random.randint(0, base_width - extension_width),
                    base_pos.y + base_height - 10  # Overlap slightly
                )
            
            extension_rect = pygame.Rect(extension_pos.x, extension_pos.y, extension_width, extension_height)
            building_rects.append(extension_rect)
            
        elif shape_type == "U":
            # Add two extensions to form a U-shape
            # Decide orientation (horizontal or vertical U)
            if random.choice([True, False]):
                # Horizontal U
                # Left extension
                left_width = random.randint(40, 80)
                left_height = random.randint(80, 120)
                left_pos = pygame.Vector2(
                    base_pos.x - left_width + 10,  # Overlap slightly
                    base_pos.y + (base_height - left_height) // 2
                )
                
                # Right extension
                right_width = random.randint(40, 80)
                right_height = random.randint(80, 120)
                right_pos = pygame.Vector2(
                    base_pos.x + base_width - 10,  # Overlap slightly
                    base_pos.y + (base_height - right_height) // 2
                )
                
                building_rects.append(pygame.Rect(left_pos.x, left_pos.y, left_width, left_height))
                building_rects.append(pygame.Rect(right_pos.x, right_pos.y, right_width, right_height))
            else:
                # Vertical U
                # Top extension
                top_width = random.randint(80, 120)
                top_height = random.randint(40, 80)
                top_pos = pygame.Vector2(
                    base_pos.x + (base_width - top_width) // 2,
                    base_pos.y - top_height + 10  # Overlap slightly
                )
                
                # Bottom extension
                bottom_width = random.randint(80, 120)
                bottom_height = random.randint(40, 80)
                bottom_pos = pygame.Vector2(
                    base_pos.x + (base_width - bottom_width) // 2,
                    base_pos.y + base_height - 10  # Overlap slightly
                )
                
                building_rects.append(pygame.Rect(top_pos.x, top_pos.y, top_width, top_height))
                building_rects.append(pygame.Rect(bottom_pos.x, bottom_pos.y, bottom_width, bottom_height))
    
    # Add some regular buildings
    for _ in range(num_buildings):
        width = random.randint(50, 200)
        height = random.randint(50, 200)
        building_pos = pygame.Vector2(
            random.randint(0, WORLD_WIDTH - width),
            random.randint(0, WORLD_HEIGHT - height)
        )
        
        # Create a new rectangle for this building
        new_rect = pygame.Rect(building_pos.x, building_pos.y, width, height)
        
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
                    union_min = pygame.Vector2(
                        min(new_rect.left, existing_rect.left),
                        min(new_rect.top, existing_rect.top)
                    )
                    union_max = pygame.Vector2(
                        max(new_rect.right, existing_rect.right),
                        max(new_rect.bottom, existing_rect.bottom)
                    )
                    
                    # Create a new rectangle for the combined shape
                    combined_rect = pygame.Rect(
                        union_min.x, union_min.y,
                        union_max.x - union_min.x,
                        union_max.y - union_min.y
                    )
                    
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
                            corridor_pos = pygame.Vector2(
                                max(new_rect.left, existing_rect.left) + 20,
                                new_rect.bottom - 10
                            )
                            corridor_width = min(new_rect.right, existing_rect.right) - corridor_pos.x - 20
                            corridor_height = existing_rect.top - corridor_pos.y + 10
                        else:
                            corridor_pos = pygame.Vector2(
                                max(new_rect.left, existing_rect.left) + 20,
                                existing_rect.bottom - 10
                            )
                            corridor_width = min(new_rect.right, existing_rect.right) - corridor_pos.x - 20
                            corridor_height = new_rect.top - corridor_pos.y + 10
                        
                        # Add the corridor as a new building if it has valid dimensions
                        if corridor_width > 40 and corridor_height > 20:
                            corridor_rect = pygame.Rect(corridor_pos.x, corridor_pos.y, corridor_width, corridor_height)
                            building_rects.append(corridor_rect)
                    else:
                        # Buildings are more aligned vertically, create horizontal corridor
                        if new_rect.centerx < existing_rect.centerx:
                            corridor_pos = pygame.Vector2(
                                new_rect.right - 10,
                                max(new_rect.top, existing_rect.top) + 20
                            )
                            corridor_width = existing_rect.left - corridor_pos.x + 10
                            corridor_height = min(new_rect.bottom, existing_rect.bottom) - corridor_pos.y - 20
                        else:
                            corridor_pos = pygame.Vector2(
                                existing_rect.right - 10,
                                max(new_rect.top, existing_rect.top) + 20
                            )
                            corridor_width = new_rect.left - corridor_pos.x + 10
                            corridor_height = min(new_rect.bottom, existing_rect.bottom) - corridor_pos.y - 20
                        
                        # Add the corridor as a new building if it has valid dimensions
                        if corridor_width > 20 and corridor_height > 40:
                            corridor_rect = pygame.Rect(corridor_pos.x, corridor_pos.y, corridor_width, corridor_height)
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
            buildings.append(Buildings(rect.x, rect.y, rect.width, rect.height))
    
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
        min_pos = pygame.Vector2(
            min(rect.x for rect in group),
            min(rect.y for rect in group)
        )
        max_pos = pygame.Vector2(
            max(rect.x + rect.width for rect in group),
            max(rect.y + rect.height for rect in group)
        )
        
        # Create a complex building with the sub-rooms
        complex_building = Buildings(
            min_pos.x, min_pos.y, max_pos.x - min_pos.x, max_pos.y - min_pos.y, 
            is_complex=True, sub_rooms=sub_rooms
        )
        
        buildings.append(complex_building)
    
    return buildings
