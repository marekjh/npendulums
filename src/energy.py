from main import Sim, TIME_STEP
import matplotlib.pyplot as plt
import numpy as np
import sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2
T = 100

def main():
    sim = Sim(theta=np.ones(N)*np.pi, thetad=np.zeros(N), l=np.ones(N), g=9.81) 
    t = np.arange(0, T, TIME_STEP)
    m = np.array([mass.m for mass in sim.mass])
    kinetic, potential, total = [], [], []
    for _ in range(len(t)):
        ke, pe, te = compute_energy(sim.theta, sim.thetad, sim.g, sim.l, m)
        kinetic.append(ke)
        potential.append(pe)
        total.append(te)
        sim.compute_next()
    kinetic, potential, total = np.array(kinetic), np.array(potential), np.array(total)
    
    plt.figure()
    plt.plot(t, kinetic, label="KE")
    plt.plot(t, potential, label="PE")
    plt.plot(t, total, label="TE")
    plt.legend()
    plt.show()

def compute_energy(theta, thetad, g, l, m):
    ke = 0
    for i in range(1, len(theta)+1):
        ke += m[i-1]*(l[i-1]*np.sum(thetad[:i]*np.cos(theta[:i]))**2 + np.sum(l[i-1]*thetad[:i]*np.sin(theta[:i]))**2)
    ke *= 1/2
    pe = 0
    for i in range(1, len(theta)+1):
        pe += m[i-1]*np.sum(l[i-1]*np.cos(theta[:i]))
    pe *= -g
    te = ke + pe
    return ke, pe, te

main()