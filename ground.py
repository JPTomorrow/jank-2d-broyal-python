import pygame

from globals import WORLD_WIDTH, WORLD_HEIGHT

class Ground:
    def __init__(self):
        self.width = 32
        self.height = 32
        self.sprite = pygame.image.load("res/ground.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))

    def draw(self, screen: pygame.Surface, camera):
        width = int(WORLD_WIDTH / self.width)
        height = int(WORLD_HEIGHT / self.height)

        for y in range(0, height):
            for x in range(0, width):
                self_rect = pygame.Rect(x * self.width, y* self.height, self.width, self.height)
                camera_rect = camera.apply(self_rect)
                spr_rect = self.sprite.get_rect(center=camera_rect.center)
                screen.blit(self.sprite, spr_rect.topleft)
                