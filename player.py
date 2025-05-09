import pygame
import random
from camera import Camera

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

    def handle_movement(self, keys, world_objects, players):
        """Handle human player movement with WASD keys"""
        if not self.is_human:
            return
            
        # Calculate new positions based on key presses
        new_x = self.x
        new_y = self.y
        
        # W - move up
        if keys[pygame.K_w]:
            new_y -= self.speed
        # S - move down
        if keys[pygame.K_s]:
            new_y += self.speed
        # A - move left
        if keys[pygame.K_a]:
            new_x -= self.speed
        # D - move right
        if keys[pygame.K_d]:
            new_x += self.speed
        
        # Check for collisions with world objects in X direction
        new_rect_x = pygame.Rect(new_x, self.y, self.width, self.height)
        x_collision = False
        for obj in world_objects:
            if obj.collides_with(new_rect_x):
                x_collision = True
                break
        
        # Check for collisions with other players in X direction
        for player in players:
            if player != self and new_rect_x.colliderect(player.rect):
                x_collision = True
                break
        
        if not x_collision:
            self.x = new_x
        
        # Check for collisions with world objects in Y direction
        new_rect_y = pygame.Rect(self.x, new_y, self.width, self.height)
        y_collision = False
        for obj in world_objects:
            if obj.collides_with(new_rect_y):
                y_collision = True
                break
        
        # Check for collisions with other players in Y direction
        for player in players:
            if player != self and new_rect_y.colliderect(player.rect):
                y_collision = True
                break
        
        if not y_collision:
            self.y = new_y
        
        # Update rect position
        self.rect.topleft = (self.x, self.y)
    
    def handle_shooting(self, keys, mouse_pos, camera, projectiles):
        """Handle human player shooting with spacebar"""
        if not self.is_human:
            return
            
        if keys[pygame.K_SPACE] and self.shoot_timer >= 30:
            self.shoot_timer = 0
            
            # Convert mouse position to world coordinates
            world_mouse_x, world_mouse_y = camera.screen_to_world_pos(mouse_pos[0], mouse_pos[1])
            
            # Calculate direction from player to mouse
            direction_x = world_mouse_x - (self.x + 16)
            direction_y = world_mouse_y - (self.y + 16)
            
            # Normalize direction
            magnitude = (direction_x**2 + direction_y**2)**0.5
            if magnitude > 0:
                direction_x /= magnitude
                direction_y /= magnitude
                
            projectiles.append(Projectile(self.x + 16, self.y + 16, 
                                        direction_x * 5, direction_y * 5, self))
    
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
            # Human player shoots on spacebar press, handled separately
            self.shoot_timer += 1

    def draw(self, screen, camera):
        # Draw player with camera offset
        camera_rect = camera.apply(self)
        pygame.draw.rect(screen, self.color, camera_rect)
        
        # Draw health bar with camera offset
        health_width = 30 * (self.health / 100)
        health_bar_x, health_bar_y = camera.world_to_screen_pos(self.x + 1, self.y - 10)
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
