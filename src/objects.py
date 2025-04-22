import pygame
from config import *
import numpy as np

class Trace(pygame.sprite.Group):
    # Parameters for dictating how the trace looks
    a = 1
    A = 5
    M = 50

    def __init__(self, color):
        super().__init__()

        self.on = True
        self.color = color
    
    def update(self, x, y, xprev, yprev):
        sprite = TraceSprite(x, y, xprev, yprev, self.color)
        self.sprites().insert(0, sprite)
        if len(self.sprites()) > Trace.M:
            del self.sprites()[-1]
        for i, sprite in enumerate(self.sprites()):
            sprite.update(i)

    @classmethod
    def height(cls, x):
        return cls.A*np.exp(-cls.a*x)


class TraceSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, xprev, yprev, color):
        super().__init__()

        size = np.sqrt((x-xprev)**2 + (y-yprev)**2)

        self.image = pygame.Surface((size, size))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.midleft = (xprev, yprev)
        self.rect.midright = (x, y)
    
    def update(self, i):
        self.rect.height = Trace.height(i)


class Mass(pygame.sprite.Sprite):
    def __init__(self, m, radius, color):
        super().__init__()

        self.m = m

        self.image = pygame.Surface((2*radius, 2*radius))
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, color, (radius, radius), radius)

        self.rect = self.image.get_rect()
    
    def update(self, xcurr, ycurr):
        self.rect.centerx = xcurr
        self.rect.centery = ycurr

