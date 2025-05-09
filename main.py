import pygame
import random
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

class Player:
    def __init__(self, x, y, is_human=False):
        self.x = x
        self.y = y
        self.health = 100
        self.speed = 2
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.shoot_timer = 0
        self.is_human = is_human

    def find_nearest(self, others):
        min_dist = float('inf')
        nearest = None
        for other in others:
            if other != self:
                dist = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest = other
        return nearest

    def move_towards(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > 0:
            dx /= dist
            dy /= dist
            self.x += dx * self.speed
            self.y += dy * self.speed
            self.x = max(0, min(self.x, WIDTH - 32))
            self.y = max(0, min(self.y, HEIGHT - 32))
            self.rect.topleft = (self.x, self.y)

    def update(self, projectiles, players):
        if not self.is_human:
            self.shoot_timer += 1
            if self.shoot_timer >= 60:
                self.shoot_timer = 0
                nearest = self.find_nearest(players)
                if nearest:
                    dx = nearest.x - self.x
                    dy = nearest.y - self.y
                    dist = (dx ** 2 + dy ** 2) ** 0.5
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                        projectiles.append(Projectile(self.x + 16, self.y + 16, dx * 5, dy * 5, self))
        else:
            # Human player shoots on spacebar press, handled in main loop
            self.shoot_timer += 1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        health_width = 30 * (self.health / 100)
        pygame.draw.rect(screen, (255, 0, 0), (self.x + 1, self.y - 10, 30, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x + 1, self.y - 10, health_width, 5))

class Projectile:
    def __init__(self, x, y, dx, dy, owner):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.rect = pygame.Rect(x, y, 5, 5)
        self.owner = owner

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.rect)

def setup():
    global players, projectiles, safe_area, shrink_timer, human_player
    # Create 9 AI players
    players = [Player(random.randint(0, WIDTH - 32), random.randint(0, HEIGHT - 32)) for _ in range(9)]
    # Create 1 human player in the center
    human_player = Player(WIDTH // 2, HEIGHT // 2, is_human=True)
    human_player.color = (0, 0, 255)  # Blue color for human player
    players.append(human_player)
    projectiles = []
    safe_area = pygame.Rect(0, 0, WIDTH, HEIGHT)
    shrink_timer = 0

def update_game_state():
    global players, projectiles, safe_area, shrink_timer, human_player

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
        # W - move up
        if keys[pygame.K_w]:
            human_player.y -= human_player.speed
        # S - move down
        if keys[pygame.K_s]:
            human_player.y += human_player.speed
        # A - move left
        if keys[pygame.K_a]:
            human_player.x -= human_player.speed
        # D - move right
        if keys[pygame.K_d]:
            human_player.x += human_player.speed
            
        # Keep player within bounds
        human_player.x = max(0, min(human_player.x, WIDTH - 32))
        human_player.y = max(0, min(human_player.y, HEIGHT - 32))
        human_player.rect.topleft = (human_player.x, human_player.y)
        
        # Handle shooting for human player
        if keys[pygame.K_SPACE] and human_player.shoot_timer >= 30:
            human_player.shoot_timer = 0
            # Shoot in the direction the player is facing (default: right)
            direction_x, direction_y = 1, 0
            if keys[pygame.K_w]: direction_y = -1
            if keys[pygame.K_s]: direction_y = 1
            if keys[pygame.K_a]: direction_x = -1
            if keys[pygame.K_d]: direction_x = 1
            
            # Normalize direction
            magnitude = (direction_x**2 + direction_y**2)**0.5
            if magnitude > 0:
                direction_x /= magnitude
                direction_y /= magnitude
                
            projectiles.append(Projectile(human_player.x + 16, human_player.y + 16, 
                                         direction_x * 5, direction_y * 5, human_player))

    # Update AI players and projectiles
    for player in players[:]:
        if not player.is_human:
            player.update(projectiles, players)
            # AI players move towards nearest player
            nearest = player.find_nearest(players)
            if nearest:
                player.move_towards(nearest)

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

    # Remove dead players and out-of-bounds projectiles
    players[:] = [p for p in players if p.health > 0]
    projectiles[:] = [p for p in projectiles if 0 <= p.x <= WIDTH and 0 <= p.y <= HEIGHT]

def draw_game():
    screen.fill((255, 255, 255))
    
    # Draw everything
    for player in players:
        player.draw(screen)
    for projectile in projectiles:
        projectile.draw(screen)
    pygame.draw.rect(screen, (0, 255, 0), safe_area, 1)

    pygame.display.flip()

def draw_winner():
    screen.fill((255, 255, 255))
    if players:
        winner = players[0]
        winner.draw(screen)
        font = pygame.font.SysFont(None, 36)
        text = font.render("Winner!", True, (0, 0, 0))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 50))
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
