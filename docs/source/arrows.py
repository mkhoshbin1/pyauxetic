"""Functions and classes used for drawing arrows and coordinate systems."""

from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d


class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs
    
    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)
#

def draw_cartesian_coord_system(axis, dim):
    
    arrow_prop_dict = dict(mutation_scale=20, linewidth=2, arrowstyle='->',shrinkA=0, shrinkB=0)
    
    if   dim.lower() == '2d':
        axis.add_artist( FancyArrowPatch([0,0], [0,0.2], **arrow_prop_dict, color='r') )
        axis.add_artist( FancyArrowPatch([0,0], [0.2,0], **arrow_prop_dict, color='b') )
        axis.text(-0.02, -0.02, r'$O$')
        axis.text(0.22 , 0    , r'$X$')
        axis.text(0    , 0.22 , r'$Y$')
    elif dim.lower() == '3d':
        arrow_prop_dict = dict(mutation_scale=20, arrowstyle='->',shrinkA=0, shrinkB=0)
        axis.add_artist( Arrow3D([0,1], [0,0], [0,0], **arrow_prop_dict, color='r') )
        axis.add_artist( Arrow3D([0,0], [0,1], [0,0], **arrow_prop_dict, color='b') )
        axis.add_artist( Arrow3D([0,0], [0,0], [0,1], **arrow_prop_dict, color='g') )
        axis.text(0.0,0.0,-0.1,r'$O$')
        axis.text(1.1,0,0,r'$X$')
        axis.text(0,1.1,0,r'$Y$')
        axis.text(0,0,1.1,r'$Z$')
    else:
        raise ValueError('dim must be 2D or 3D.')
#