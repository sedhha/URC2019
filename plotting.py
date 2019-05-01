# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import numpy as np
x = np.asarray([1,2,3,4,5,6])
y = np.asarray([2,4,6,8,10,12])
def animate(i,factor):
    line.set_xdata(x[:i])
    line.set_ydata(y[:i])
    line2.set_xdata(x[:i])
    line2.set_ydata(factor*y[:i])
    return line,line2
K = 0 # any factor 
fig = plt.figure()
ax = fig.add_subplot(111)
line, = ax.plot([],[], '-')
line2, = ax.plot([],[],'--')
for i in range(5):
    ax.set_xlim(np.min(x), np.max(x))
    ax.set_ylim(np.min(y), np.max(y))
    ani = animation.FuncAnimation(fig, animate, frames=len(x), fargs=(K,),
                              interval=100, blit=True)
    plt.pause(0.5)
