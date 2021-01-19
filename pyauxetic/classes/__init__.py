# See if the code is run from a Kernel or a GUI python interpreter.
try:
    import part
    is_kernel = True
except ImportError:
    is_kernel = False
except:
    raise

# Import all structure modules here using this style
# and in alphabetical order.
if is_kernel:
    from . import reentrant2d


def return_unit_cell_class(unit_cell_name):
    """TODO"""
    #TODO: reconcile with the dict.
    if unit_cell_name == 'reentrant2d_planar_shell':
        unit_cell_class = reentrant2d.Reentrant2DPlanarShellStructure
    else:
        raise ValueError('Invalid value for unit_cell_name.' +
                         ' See docs for a list of currently supported values.')
    return unit_cell_class