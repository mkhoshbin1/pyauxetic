"""This module contains instances of :class:`namedtuple` that are used for defining
the different unit cells that can be used for creating auxetic structures."""

from collections import namedtuple

# The contents must be ordered as follows:
# + namedtuple objects defining variants of each unit cell.
# + A list named xxx_ucp_list, where xxx is the name of the unit cell,
#   that contains the namedtuple objects for each unit cell.
# + General definitions for all unit cells.


#TODO: docstring, consider moving to own module.
# id(int): Numeric ID of the unit cell. This ID must be unique in the structure.

#TODO: only one is defined. Convert to list. fix checking in add_unit_cells.
#TODO: doc them based on the reentrant2d.

#### Begin Re-Entrant 2D Unit Cells ####
Reentrant2DUcpFull = \
    namedtuple('Reentrant2DUcpFull',
               ['id', 'extrusion_depth',
                'tail_strut_length', 'tail_strut_thickness',
                'diag_strut_length', 'diag_strut_thickness', 'diag_strut_angle',
                'vert_strut_length', 'vert_strut_thickness' ] )
Reentrant2DUcpFull.unit_cell_type = 'Re-Entrant 2D'
Reentrant2DUcpFull.formal_names   = {
    'id'                  : 'Unit Cell ID'              ,
    'extrusion_depth'     : 'Output Extrusion Depth'    ,
    'tail_strut_length'   : 'Tail Strut Length'         ,
    'tail_strut_thickness': 'Tail Strut Thickness'      ,
    'diag_strut_length'   : 'Diagonal Strut Length'     ,
    'diag_strut_thickness': 'Diagonal Strut Thickness'  ,
    'diag_strut_angle'    : 'Diagonal Strut Angle (rad)',
    'vert_strut_length'   : 'Vertical Strut Length'     ,
    'vert_strut_thickness': 'Vertical Strut Thickness'
}

Reentrant2DUcpBox = \
    namedtuple('Reentrant2DUcpBox',
               ['id', 'extrusion_depth',
                'horz_bounding_box'    , 'vert_bounding_box',
                'vert_strut_thickness' ,
                'diag_strut_thickness' , 'diag_strut_angle' ] )
Reentrant2DUcpBox.unit_cell_type = 'Re-Entrant 2D'
Reentrant2DUcpBox.formal_names   = {
    'id'                  : 'Unit Cell ID'              ,
    'extrusion_depth'     : 'Output Extrusion Depth'    ,
    'horz_bounding_box'   : 'Vertical Bounding Box'     ,
    'vert_bounding_box'   : 'Horizontal Bounding Box'   ,
    'vert_strut_thickness': 'Vertical Strut Thickness'  ,
    'diag_strut_thickness': 'Diagonal Strut Thickness'  ,
    'diag_strut_angle'    : 'Diagonal Strut Angle (rad)'
}

Reentrant2DUcpSimple = \
    namedtuple('Reentrant2DUcpSimple',
               ['id', 'extrusion_depth',
                'vert_strut_length'   , 'vert_strut_thickness',
                'diag_strut_thickness', 'diag_strut_angle' ] )
Reentrant2DUcpSimple.unit_cell_type = 'Re-Entrant 2D'
Reentrant2DUcpSimple.formal_names   = {
    'id'                  : 'Unit Cell ID'              ,
    'extrusion_depth'     : 'Output Extrusion Depth'    ,
    'vert_strut_length'   : 'Vertical Strut Length'     ,
    'vert_strut_thickness': 'Vertical Strut Thickness'  ,
    'diag_strut_thickness': 'Diagonal Strut Thickness'  ,
    'diag_strut_angle'    : 'Diagonal Strut Angle (rad)'
}

reentrant2d_ucp_list = (Reentrant2DUcpFull, Reentrant2DUcpBox, Reentrant2DUcpSimple)
#### End   Re-Entrant 2D Unit Cells ####

#### Begin General Unit Cell Definitions####
unit_cells_list    = ['Re-Entrant 2D']
unit_cells_3d_list = []
unit_cell_variant_dict = {
    'Re-Entrant 2D': ['Full Parameters', 'Bounding Box', 'Simplified']
}
all_structure_types_list         = ['Planar Shell', 'Tubular Shell',
                                    'Planar Solid', 'Tubular Solid']
all_tubular_structure_types_list = ['Tubular Shell', 'Tubular Solid']
structure_type_dict       = {
    'Re-Entrant 2D': ['Planar Shell']
}
unit_cell_name_dict = {
    ('Re-Entrant 2D','Planar Shell'   ): 'reentrant2d_planar_shell'
}
unit_cell_params_class_dict = {
    ('Re-Entrant 2D','Full Parameters'): Reentrant2DUcpFull  ,
    ('Re-Entrant 2D','Bounding Box'   ): Reentrant2DUcpBox   ,
    ('Re-Entrant 2D','Simplified'     ): Reentrant2DUcpSimple,
}
#### End   General Unit Cell Definitions####