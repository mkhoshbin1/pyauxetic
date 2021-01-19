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

draw_cartesian_coord_system(ax, '2d')

plt.xlim([-0.05, 1.05])
plt.ylim([-0.05, 1.05*y[1]])

ax.set_axis_off()
fig.tight_layout()
fig.show()
#TODO: recheck the figure.