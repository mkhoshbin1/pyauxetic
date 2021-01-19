import numpy as np
import matplotlib.pyplot as plt

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join('..','..')))

from arrows import Arrow3D, draw_cartesian_coord_system

# Use calibri font.
calibri_font = hfont = {'fontname':'Calibri'}

# Create the figure.
fig = plt.figure()
ax = plt.gca()

# Setup the dimensions.
h = 0.6
w = 0.8
x = (0.1, 0.1+w)
y = (0.1, 0.1+h)

# Create the rectangle.
rectangle = plt.Rectangle((x[0], y[0]), w, h, fill=True)
rectangle.set_color( '#6699cc' )
ax.add_patch(rectangle)

# Create and annotate the edges.
ld_edge_1 = ax.plot((x[0], x[0]), (y[0], y[1]), linewidth=3, c='r')
ax.annotate('LD-Edge-1', xy=(x[0], y[0]+0.9*h), xycoords='data',
            xytext=(-70,20), textcoords='offset points',
            arrowprops=dict(arrowstyle="->"), **calibri_font)
ld_edge_2 = ax.plot((x[1], x[1]), (y[0], y[1]), linewidth=3, c='r')
ax.annotate('LD-Edge-2', xy=(x[1], y[0]+0.9*h), xycoords='data',
            xytext=(30,20), textcoords='offset points',
            arrowprops=dict(arrowstyle="->"), **calibri_font)

# Create and annotate the reference points.
rp = ax.scatter( (0.05, 0.95), [(y[0]+y[1])/2]*2, c='r', marker='o')
ax.annotate('RP-1', xy=(0.05, (y[0]+y[1])/2), xycoords='data',
            xytext=(-45,30), textcoords='offset points',
            arrowprops=dict(arrowstyle="->"), **calibri_font)
ax.annotate('RP-2', xy=(0.95, (y[0]+y[1])/2), xycoords='data',
            xytext=(20,30), textcoords='offset points',
            arrowprops=dict(arrowstyle="->"), **calibri_font)

draw_cartesian_coord_system(ax, '2d')

plt.xlim([-0.05, 1.05])
plt.ylim([-0.05, 1.05*y[1]])

ax.set_axis_off()
fig.tight_layout()
fig.show()
#TODO: recheck the figure.