import asyncio
import pygame
import numpy as np
from compute import RK4, sigma

# TODO: Add UI to make things like masses and pendulum lengths customizeable

N = 2 # TODO: Rework to get user input from frontend
SIM_DIMENSION = 600
BUFFER = 150
SIZE = SIM_DIMENSION + BUFFER
TIME_STEP = 0.02
WHITE = pygame.Color("white")
BLACK = pygame.Color("black")
RED = pygame.Color("red")
BLUE = pygame.Color("blue")


class Sim:
    def __init__(self, **kwargs):
        self.mass = [Mass(1, RED, 6) for _ in range(N)]
        self.theta, self.thetad, self.l, self.g = kwargs.values()
        self.time_scale = 1
        self.paused = True
        self.adjust_mode = 0
        self.step = 0
        self.bg = WHITE
        if __name__ == "__main__":
            self.screen = pygame.display.set_mode((SIZE, SIZE))
            self.trace = Trace()
            asyncio.run(self.main())

    async def main(self):
        pygame.init()
        pygame.display.set_caption("N-Pendulum Sim")
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keyboard(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_drag(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up()
            
            self.screen.fill(self.bg)
            self.draw()
            if not self.paused:
                self.compute_next()
                self.step += 1

            clock.tick(self.time_scale/TIME_STEP)
            pygame.display.flip()
            await asyncio.sleep(0)

    def compute_next(self):
        def F(th, thd):
            return thd
        
        # Used info at https://www.researchgate.net/publication/336868500_Equations_of_Motion_Formulation_of_a_Pendulum_Containing_N-point_Masses and
        # https://travisdoesmath.github.io/pendulum-explainer/ for equations of motion
        def G(th, thd):
            a = []
            b = []
            for j in range(N):
                b_entry = 0 
                for k in range(N):
                    m_sum = sum(self.mass[i].m*sigma(j, i) for i in range(k, N))
                    if j == k:
                        a.append(sum(self.mass[i].m*self.l[j]**2*sigma(j, i) for i in range(N)))
                    else:
                        a.append(m_sum*self.l[j]*self.l[k]*np.cos(th[j] - th[k]))
                    b_entry -= (self.g*self.l[j]*np.sin(th[j])*self.mass[k].m*sigma(j, k) +
                               m_sum*self.l[j]*self.l[k]*np.sin(th[j] - th[k])*thd[j]*thd[k] + 
                               m_sum*self.l[j]*self.l[k]*np.sin(th[k] - th[j])*(thd[j] - thd[k])*thd[k])
                b.append(b_entry)

            a = np.array(a).reshape(N, N)
            b = np.array(b)
            return np.linalg.solve(a, b)

        self.thetaprev, self.thetadprev = self.theta, self.thetad
        self.theta, self.thetad = RK4(F, G, self.theta, self.thetad, TIME_STEP)
        
    def get_cartesian(self, th):
        scale = SIM_DIMENSION / (2*(np.sum(self.l)))
        x, y = [scale*self.l[0]*np.sin(th[0]) + SIZE/2], [scale*self.l[0]*np.cos(th[0]) + SIZE/2]
        for i in range(1, N):
            x.append(x[i-1] + scale*self.l[i]*np.sin(th[i]))
            y.append(y[i-1] + scale*self.l[i]*np.cos(th[i]))
        return np.array(x), np.array(y)

    def draw(self):
        x, y = self.get_cartesian(self.theta)

        if self.trace.on and self.step > 0:
            xprev, yprev = self.get_cartesian(self.thetaprev)
            if not self.adjust_mode:
                self.trace.update(x[-1], y[-1], xprev[-1], yprev[-1])
            self.trace.draw(self.screen)

        pygame.draw.line(self.screen, BLACK, (SIZE/2, SIZE/2), (x[0], y[0]), 5)
        for i in range(1, N):
            pygame.draw.line(self.screen, BLACK, (x[i-1], y[i-1]), (x[i], y[i]), 5)

        for i in range(N):
            self.mass[i].rect.centerx, self.mass[i].rect.centery = x[i], y[i]
            self.mass[i].draw(self.screen)
            

    def handle_keyboard(self, key):
        if key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_t:
            self.trace.on = not self.trace.on
        elif key == pygame.K_r:
            self.trace.screen.fill(BLACK)

    def handle_mouse_click(self, mousepos):
        for i, mass in enumerate(self.mass):
            if mass.rect.collidepoint(mousepos):
                self.paused = True
                self.trace.screen.fill(BLACK)
                self.adjust_mode = i + 1
    
    def handle_mouse_drag(self, mousepos):
        if self.adjust_mode:
            x, y = self.get_cartesian(self.theta)
            x -= SIZE/2
            y -= SIZE/2
            mouse_x, mouse_y = mousepos
            mouse_x -= SIZE/2
            mouse_y -= SIZE/2
            if self.adjust_mode == 1:
                self.theta[0] = np.arctan2(-mouse_y, mouse_x) + np.pi/2
            else:
                self.theta[self.adjust_mode-1] = np.arctan2(y[self.adjust_mode-2] - mouse_y, mouse_x - x[self.adjust_mode-2]) + np.pi/2

    
    def handle_mouse_up(self):
        if self.adjust_mode:
            self.thetad = np.zeros(N)
            self.step, self.adjust_mode = 0, 0

class Trace:
    def __init__(self):
        self.screen = pygame.Surface((SIZE, SIZE))
        self.screen.set_colorkey(BLACK) # Makes black background transparent
        self.on = False

    def update(self, xcurr, ycurr, xprev, yprev):
        pygame.draw.line(self.screen, BLUE, (xcurr, ycurr), (xprev, yprev), 3)
    
    def draw(self, screen):
        screen.blit(self.screen, (0, 0))

class Mass(pygame.sprite.Sprite):
    def __init__(self, m, color, radius):
        super().__init__()

        self.m = m
        self.image = pygame.Surface((2*radius, 2*radius))
        self.image.set_colorkey(BLACK)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)


if __name__ == "__main__":
    Sim(theta=np.ones(N)*np.pi/2, thetad=np.zeros(N), l=np.ones(N), g=9.81) 