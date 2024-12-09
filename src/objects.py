import pygame
from config import *

class Trace(pygame.sprite.Group):
    def __init__(self, i, color, *sprites):
        super().__init__(*sprites)

        self.screen = pygame.Surface((SIZE, SIZE))
        self.screen.set_colorkey(BLACK) # Makes black background transparent
        self.on = False
        self.i = i
        self.color = color

    def update(self, xcurr, ycurr, xprev, yprev):
        pygame.draw.line(self.screen, BLUE, (xcurr, ycurr), (xprev, yprev), 3)
    
    def draw(self, screen):
        screen.blit(self.screen, (0, 0))

class TraceLine(pygame.sprite.Sprite):
    def __init__(self):
        pass

class Mass(pygame.sprite.Sprite):
    def __init__(self, m, color, radius):
        super().__init__(self)

        self.m = m
        self.image = pygame.Surface((2*radius, 2*radius))
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()

