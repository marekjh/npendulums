import asyncio
import pygame
import numpy as np
from objects import *
from compute import *
from config import *

# TODO: Add UI to make things like masses and pendulum lengths customizeable

class Sim:
    def __init__(self):
        self.screen = pygame.display.set_mode((SIZE, SIZE))

        self.N = 2
        self.g = 9.81
        self.theta = np.ones(self.N)*np.pi/2
        self.thetad = np.zeros(self.N)
        self.l = np.ones(self.N)

        self.traces = self.initialize_traces()
        self.masses = self.initialize_masses()
        self.time_step = 0.01
        self.time_scale = 1
        self.paused = False
        self.adjust_mode = 0
        self.step = 0
        self.bg = WHITE

        if __name__ == "__main__":
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

            clock.tick(self.time_scale/self.time_step)
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
            for j in range(self.N):
                b_entry = 0 
                for k in range(self.N):
                    m_sum = sum(self.masses[i].m*sigma(j, i) for i in range(k, self.N))
                    if j == k:
                        a.append(sum(self.masses[i].m*self.l[j]**2*sigma(j, i) for i in range(self.N)))
                    else:
                        a.append(m_sum*self.l[j]*self.l[k]*np.cos(th[j] - th[k]))
                    b_entry -= (self.g*self.l[j]*np.sin(th[j])*self.masses[k].m*sigma(j, k) +
                               m_sum*self.l[j]*self.l[k]*np.sin(th[j] - th[k])*thd[j]*thd[k] + 
                               m_sum*self.l[j]*self.l[k]*np.sin(th[k] - th[j])*(thd[j] - thd[k])*thd[k])
                b.append(b_entry)

            a = np.array(a).reshape(self.N, self.N)
            b = np.array(b)
            return np.linalg.solve(a, b)

        self.thetaprev, self.thetadprev = self.theta, self.thetad
        self.theta, self.thetad = RK4(F, G, self.theta, self.thetad, self.time_step)
        
    def get_cartesian(self, th):
        scale = SIM_DIMENSION / (2*(np.sum(self.l)))
        x, y = [scale*self.l[0]*np.sin(th[0]) + SIZE/2], [scale*self.l[0]*np.cos(th[0]) + SIZE/2]
        for i in range(1, self.N):
            x.append(x[i-1] + scale*self.l[i]*np.sin(th[i]))
            y.append(y[i-1] + scale*self.l[i]*np.cos(th[i]))
        return np.array(x), np.array(y)

    def draw(self):
        x, y = self.get_cartesian(self.theta)
        xprev, yprev = self.get_cartesian(self.thetaprev)

        # draw the traces that are currently enabled
        if self.step > 0:
            for i, trace in enumerate(self.traces):
                if trace.on:
                    trace.update(x[i], y[i], xprev[i], yprev[i])
                    trace.draw(self.screen)
                
        # draw massless connections between masses
        pygame.draw.line(self.screen, BLACK, (SIZE/2, SIZE/2), (x[0], y[0]), 5)
        for i in range(1, self.N):
            pygame.draw.line(self.screen, BLACK, (x[i-1], y[i-1]), (x[i], y[i]), 5)

        # draw masses
        self.masses.update()
        self.masses.draw(self.screen)

    def handle_keyboard(self, key):
        if key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_t:
            self.trace.on = not self.trace.on
        elif key == pygame.K_r:
            self.trace.screen.fill(BLACK)

    def handle_mouse_click(self, mousepos):
        for i, mass in enumerate(self.masses):
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
            self.thetad = np.zeros(self.N)
            self.step, self.adjust_mode = 0, 0
    
    def initialize_traces(self):
        traces = []
        for i in range(self.N):
            trace = Trace(TRACE_COLORS[i % len(TRACE_COLORS)])
            traces.append(trace)
        return traces

    def initialize_masses(self):
        group = pygame.sprite.Group()
        for _ in range(self.N):
            mass = Mass(1, 6, RED)
            group.add(mass)
        return group


if __name__ == "__main__":
    Sim()