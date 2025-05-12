import pygame
import random
import math
# from camera import Camera

class Player:
    def __init__(self, x, y, is_human=False):
        # render stuff
        self.pos = pygame.Vector2(x, y)
        self.width = 32
        self.height = 32
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.sprite = pygame.image.load("res/player.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        
        # stats
        self.health = 100
        self.bullet_speed = 13
        self.is_human = is_human
        
        # movement
        self.max_speed = 2.5
        self.sprint_max_speed = 5
        self.acceleration = 0.15
        self.deceleration = 0.08
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.rotation_offset = -10

        # shooting
        self.shoot_timer = 0
        self.shoot_position_offset = pygame.Vector2(0,0)
        
        # AI players
        self.view_range = 400  # AI can only see players within this range
        self.preferred_distance = 150  # AI will try to keep this distance from other players

    def find_nearest(self, others):
        min_dist = float('inf')
        nearest = None
        for other in others:
            if other != self:
                dist = self.pos.distance_to(other.pos)
                # Only consider players within view range for AI
                if dist < min_dist and (self.is_human or dist <= self.view_range):
                    min_dist = dist
                    nearest = other
        return nearest

    def move_towards(self, target, world_objects, players):
        direction = target.pos - self.pos
        if direction.length() > 0:
            direction.normalize_ip()
            
            # Apply acceleration towards target
            self.velocity += direction * self.acceleration
            
            # Limit velocity to max speed
            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)
            
            # Calculate new position
            new_pos = self.pos + self.velocity
            
            # Check for collisions with world objects
            new_rect_x = pygame.Rect(new_pos.x, self.pos.y, self.width, self.height)
            new_rect_y = pygame.Rect(self.pos.x, new_pos.y, self.width, self.height)
            
            # Move in X direction if no collision
            x_collision = False
            for obj in world_objects:
                if obj.collides_with(new_rect_x):
                    x_collision = True
                    self.velocity.x = 0  # Stop X velocity on collision
                    break
            
            # Check collision with other players in X direction
            for player in players:
                if player != self and new_rect_x.colliderect(player.rect):
                    x_collision = True
                    self.velocity.x = 0  # Stop X velocity on collision
                    break
            
            if not x_collision:
                self.pos.x = new_pos.x
            
            # Move in Y direction if no collision
            y_collision = False
            for obj in world_objects:
                if obj.collides_with(new_rect_y):
                    y_collision = True
                    self.velocity.y = 0  # Stop Y velocity on collision
                    break
            
            # Check collision with other players in Y direction
            for player in players:
                if player != self and new_rect_y.colliderect(player.rect):
                    y_collision = True
                    self.velocity.y = 0  # Stop Y velocity on collision
                    break
            
            if not y_collision:
                self.pos.y = new_pos.y
            
            # Update rect position
            self.rect.topleft = (self.pos.x, self.pos.y)

    def handle_movement(self, keys, world_objects, players):
        """Handle human player movement with WASD keys using acceleration and deceleration"""
        if not self.is_human:
            return
        
        # check for sprinting
        max_speed = self.max_speed
        if keys[pygame.K_LSHIFT]:
            max_speed = self.sprint_max_speed

        # Apply acceleration based on key presses
        # W - move up
        if keys[pygame.K_w]:
            self.velocity.y -= self.acceleration
        # S - move down
        elif keys[pygame.K_s]:
            self.velocity.y += self.acceleration
        # If neither W nor S is pressed, apply deceleration in Y direction
        else:
            if self.velocity.y > 0:
                self.velocity.y = max(0, self.velocity.y - self.deceleration)
            elif self.velocity.y < 0:
                self.velocity.y = min(0, self.velocity.y + self.deceleration)
        
        # A - move left
        if keys[pygame.K_a]:
            self.velocity.x -= self.acceleration
        # D - move right
        elif keys[pygame.K_d]:
            self.velocity.x += self.acceleration
        # If neither A nor D is pressed, apply deceleration in X direction
        else:
            if self.velocity.x > 0:
                self.velocity.x = max(0, self.velocity.x - self.deceleration)
            elif self.velocity.x < 0:
                self.velocity.x = min(0, self.velocity.x + self.deceleration)
        
        # Limit velocity to max speed
        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)
        
        # Calculate new positions based on velocity
        new_pos = self.pos + self.velocity
        
        # Check for collisions with world objects in X direction
        new_rect_x = pygame.Rect(new_pos.x, self.pos.y, self.width, self.height)
        x_collision = False
        for obj in world_objects:
            if obj.collides_with(new_rect_x):
                x_collision = True
                self.velocity.x = 0  # Stop X velocity on collision
                break
        
        # Check for collisions with other players in X direction
        for player in players:
            if player != self and new_rect_x.colliderect(player.rect):
                x_collision = True
                self.velocity.x = 0  # Stop X velocity on collision
                break
        
        if not x_collision:
            self.pos.x = new_pos.x
        
        # Check for collisions with world objects in Y direction
        new_rect_y = pygame.Rect(self.pos.x, new_pos.y, self.width, self.height)
        y_collision = False
        for obj in world_objects:
            if obj.collides_with(new_rect_y):
                y_collision = True
                self.velocity.y = 0  # Stop Y velocity on collision
                break
        
        # Check for collisions with other players in Y direction
        for player in players:
            if player != self and new_rect_y.colliderect(player.rect):
                y_collision = True
                self.velocity.y = 0  # Stop Y velocity on collision
                break
        
        if not y_collision:
            self.pos.y = new_pos.y
        
        # Update rect position
        self.rect.topleft = (self.pos.x, self.pos.y)
    
    def handle_shooting(self, keys, mouse_pos, mouse_buttons, camera, projectiles):
        """Handle human player shooting with left mouse button"""
        if not self.is_human:
            return
            
        # Convert mouse position to world coordinates
        world_mouse_pos = pygame.Vector2(camera.screen_to_world_pos(mouse_pos[0], mouse_pos[1]))
        
        # Calculate direction from player to mouse
        player_center = self.pos + pygame.Vector2(16, 16)
        direction = world_mouse_pos - player_center
        
        # Update rotation angle to face mouse
        if direction.length() > 0:
            # Calculate angle in radians and convert to degrees
            angle = math.atan2(direction.y, direction.x)
            self.rotation = math.degrees(angle) + self.rotation_offset
        
        # Handle shooting with left mouse button (button 0)
        if mouse_buttons[0] and self.shoot_timer >= 30:
            self.shoot_timer = 0
            
            # Normalize direction
            if direction.length() > 0:
                direction.normalize_ip()
                
            projectiles.append(Projectile(player_center.x + self.shoot_position_offset.x, player_center.y + self.shoot_position_offset.y, 
                                        direction.x * self.bullet_speed, direction.y * self.bullet_speed, self))
    
    def move_away_from(self, target, world_objects, players):
        """Move away from a target while avoiding obstacles"""
        direction = self.pos - target.pos  # Direction away from target
        if direction.length() > 0:
            direction.normalize_ip()
            
            # Apply acceleration away from target
            self.velocity += direction * self.acceleration
            
            # Limit velocity to max speed
            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)
            
            # Calculate new position
            new_pos = self.pos + self.velocity
            
            # Check for collisions with world objects
            new_rect_x = pygame.Rect(new_pos.x, self.pos.y, self.width, self.height)
            new_rect_y = pygame.Rect(self.pos.x, new_pos.y, self.width, self.height)
            
            # Move in X direction if no collision
            x_collision = False
            for obj in world_objects:
                if obj.collides_with(new_rect_x):
                    x_collision = True
                    self.velocity.x = 0  # Stop X velocity on collision
                    break
            
            # Check collision with other players in X direction
            for player in players:
                if player != self and new_rect_x.colliderect(player.rect):
                    x_collision = True
                    self.velocity.x = 0  # Stop X velocity on collision
                    break
            
            if not x_collision:
                self.pos.x = new_pos.x
            
            # Move in Y direction if no collision
            y_collision = False
            for obj in world_objects:
                if obj.collides_with(new_rect_y):
                    y_collision = True
                    self.velocity.y = 0  # Stop Y velocity on collision
                    break
            
            # Check collision with other players in Y direction
            for player in players:
                if player != self and new_rect_y.colliderect(player.rect):
                    y_collision = True
                    self.velocity.y = 0  # Stop Y velocity on collision
                    break
            
            if not y_collision:
                self.pos.y = new_pos.y
            
            # Update rect position
            self.rect.topleft = (self.pos.x, self.pos.y)

    def update(self, projectiles, players, world_objects):
        if not self.is_human:
            self.shoot_timer += 1
            
            # Find nearest player
            nearest = self.find_nearest(players)
            
            # Handle shooting and rotation
            if nearest:
                # Calculate direction to nearest player
                player_center = self.pos + pygame.Vector2(16, 16)
                direction = nearest.pos - player_center
                dist = direction.length()
                
                # Update rotation to face the target
                if dist > 0:
                    angle = math.atan2(direction.y, direction.x)
                    self.rotation = math.degrees(angle) + self.rotation_offset
                
                # Handle shooting
                if self.shoot_timer >= 60:
                    self.shoot_timer = 0
                    if dist <= self.view_range:  # Only shoot if within view range
                        if direction.length() > 0:
                            direction.normalize_ip()
                        projectiles.append(Projectile(player_center.x + self.shoot_position_offset.x, 
                                                      player_center.y + self.shoot_position_offset.y, 
                                                      direction.x * self.bullet_speed, direction.y * self.bullet_speed, self))
            
            # Handle movement based on distance to nearest player
            if nearest and self.pos.distance_to(nearest.pos) <= self.view_range:
                current_distance = self.pos.distance_to(nearest.pos)
                
                # If too close, move away
                if current_distance < self.preferred_distance - 20:  # Add a small buffer
                    self.move_away_from(nearest, world_objects, players)
                # If too far, move closer
                elif current_distance > self.preferred_distance + 20:  # Add a small buffer
                    self.move_towards(nearest, world_objects, players)
                # If at a good distance, apply deceleration to slow down
                else:
                    # Apply deceleration in X direction
                    if self.velocity.x > 0:
                        self.velocity.x = max(0, self.velocity.x - self.deceleration)
                    elif self.velocity.x < 0:
                        self.velocity.x = min(0, self.velocity.x + self.deceleration)
                    
                    # Apply deceleration in Y direction
                    if self.velocity.y > 0:
                        self.velocity.y = max(0, self.velocity.y - self.deceleration)
                    elif self.velocity.y < 0:
                        self.velocity.y = min(0, self.velocity.y + self.deceleration)
            # Apply deceleration if no target or target out of range
            else:
                # Apply deceleration in X direction
                if self.velocity.x > 0:
                    self.velocity.x = max(0, self.velocity.x - self.deceleration)
                elif self.velocity.x < 0:
                    self.velocity.x = min(0, self.velocity.x + self.deceleration)
                
                # Apply deceleration in Y direction
                if self.velocity.y > 0:
                    self.velocity.y = max(0, self.velocity.y - self.deceleration)
                elif self.velocity.y < 0:
                    self.velocity.y = min(0, self.velocity.y + self.deceleration)
        else:
            # Human player shoots on spacebar press, handled separately
            self.shoot_timer += 1

    def draw(self, screen, camera):
        # Get camera-adjusted position
        camera_rect = camera.apply(self.rect)
        
        # Rotate the sprite to face the aiming direction
        rotated_sprite = pygame.transform.rotate(self.sprite, -self.rotation)
        
        # Get the rect of the rotated sprite
        rot_rect = rotated_sprite.get_rect(center=camera_rect.center)
        
        # Draw the rotated sprite
        screen.blit(rotated_sprite, rot_rect.topleft)
        
        # Draw health bar with camera offset
        health_width = 30 * (self.health / 100)
        health_bar_pos = camera.world_to_screen_pos(self.pos.x + 1, self.pos.y - 10)
        pygame.draw.rect(screen, (255, 0, 0), (health_bar_pos[0], health_bar_pos[1], 30, 5))
        pygame.draw.rect(screen, (0, 255, 0), (health_bar_pos[0], health_bar_pos[1], health_width, 5))

class Projectile:
    def __init__(self, x, y, dx, dy, owner, dmg = 35):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(dx, dy)
        self.proj_length_decay = 1
        self.rect = pygame.Rect(x, y, 30, 3)
        self.owner = owner
        self.lifetime = 40  # Add lifetime to prevent projectiles from traveling forever
        self.mark_destroyed = False
        self.damage = dmg
        
        # Calculate rotation angle based on velocity direction
        if self.velocity.length() > 0:
            angle = math.atan2(self.velocity.y, self.velocity.x)
            self.rotation = math.degrees(angle)
        else:
            self.rotation = 0

    def update(self):
        self.pos += self.velocity
        self.rect.topleft = (self.pos.x, self.pos.y)
        self.lifetime -= 1
        if self.rect.width > 2:
            self.rect.width -= self.proj_length_decay

    def draw(self, screen, camera):
        # Get camera-adjusted position
        camera_rect = camera.apply(self.rect)
        
        # Create a surface for the projectile
        projectile_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(projectile_surface, (0, 0, 0), (0, 0, self.rect.width, self.rect.height))
        
        # Rotate the surface
        rotated_surface = pygame.transform.rotate(projectile_surface, -self.rotation)
        
        # Get the rect of the rotated surface centered at the camera-adjusted position
        rotated_rect = rotated_surface.get_rect(center=camera_rect.center)
        
        # Draw the rotated projectile
        screen.blit(rotated_surface, rotated_rect.topleft)
