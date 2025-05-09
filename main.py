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

# World object class for obstacles
class WorldObject:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BROWN
    
    def draw(self, screen, camera):
        camera_rect = camera.apply(self)
        pygame.draw.rect(screen, self.color, camera_rect)

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
                if new_rect_x.colliderect(obj.rect):
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
                if new_rect_y.colliderect(obj.rect):
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
    num_obstacles = 50
    for _ in range(num_obstacles):
        width = random.randint(50, 200)
        height = random.randint(50, 200)
        x = random.randint(0, WORLD_WIDTH - width)
        y = random.randint(0, WORLD_HEIGHT - height)
        world_objects.append(WorldObject(x, y, width, height))
    
    # Create 9 AI players spread across the world (ensuring they don't spawn inside obstacles)
    players = []
    for _ in range(9):
        valid_spawn = False
        while not valid_spawn:
            x = random.randint(0, WORLD_WIDTH - 32)
            y = random.randint(0, WORLD_HEIGHT - 32)
            player_rect = pygame.Rect(x, y, 32, 32)
            valid_spawn = True
            for obj in world_objects:
                if player_rect.colliderect(obj.rect):
                    valid_spawn = False
                    break
        players.append(Player(x, y))
    
    # Create 1 human player in the center of the world (ensuring they don't spawn inside obstacles)
    valid_spawn = False
    while not valid_spawn:
        x = WORLD_WIDTH // 2
        y = WORLD_HEIGHT // 2
        player_rect = pygame.Rect(x, y, 32, 32)
        valid_spawn = True
        for obj in world_objects:
            if player_rect.colliderect(obj.rect):
                x += 50  # Try a bit to the right
                y += 50  # and down
                player_rect = pygame.Rect(x, y, 32, 32)
                if not player_rect.colliderect(obj.rect):
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

    # Handle human player movement with WASD keys
    keys = pygame.key.get_pressed()
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
            if new_rect_x.colliderect(obj.rect):
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
            if new_rect_y.colliderect(obj.rect):
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
