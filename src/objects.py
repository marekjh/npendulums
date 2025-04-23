import pygame
from config import *
import numpy as np

class Trace():
    # Parameters for dictating how the trace looks
    a = 0.01
    A = 6
    M = 100

    def __init__(self, color):
        self.on = True
        self.color = color
        self.spritelist = []
    
    def update(self, x, y):
        sprite = TraceSprite(self.color)
        sprite.rect.centerx = x
        sprite.rect.centery = y
        self.spritelist.insert(0, sprite)
        if len(self.spritelist) > Trace.M:
            del self.spritelist[-1]
        for i, sprite in enumerate(self.spritelist):
            sprite.update(i)
    
    def draw(self, surface):
        for sprite in self.spritelist:
            surface.blit(sprite.image, sprite.rect)

    @classmethod
    def size(cls, x):
        return cls.A*np.exp(-cls.a*x)


class TraceSprite(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()

        self.image = pygame.Surface((2*Trace.A, 2*Trace.A))
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, color, (Trace.A, Trace.A), Trace.A)

        self.rect = self.image.get_rect()
    
    def update(self, i):
        size = Trace.size(i)
        self.image = pygame.transform.scale(self.image, (2*size, 2*size))


class MassGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
    
    def update(self, x, y):
        for i, sprite in enumerate(self.sprites()):
            sprite.update(x[i], y[i])


class Mass(pygame.sprite.Sprite):
    def __init__(self, m, radius, color):
        super().__init__()

        self.m = m

        self.image = pygame.Surface((2*radius, 2*radius))
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, color, (radius, radius), radius)

        self.rect = self.image.get_rect()
    
    def update(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

