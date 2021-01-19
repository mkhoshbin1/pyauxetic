"""This module contains instances of :class:`namedtuple` that are used for defining
the different aspects of the structure."""

#TODO: imports
#TODO: order in docs is not ok. check again.
#TODO: re-read at the end. also doc them.

from collections import namedtuple

#### Begin PatternParams ####
PatternParams = \
    namedtuple('PatternParams',
               ['pattern_mode', 'num_cell_repeat', 'structure_map'] )
PatternParams.__new__.__defaults__ = (None, None, None)
try:
    #TODO: OutputParams.export_extrusion_depth.__doc__
    PatternParams.__doc__ = """namedtuple instance describing the parameters
                           for patterning the unit cell(s) that make up the structure.
                           """
    PatternParams.pattern_mode.__doc__ = \
                           """(:class:`str`) The type of patterning used for the structure:
                           
                           * **'uniform'**: A singular unit cell is repeated
                             based on *PatternParams.num_cell_repeat*.
                           
                           * **'nonuniform'**: A number of unit cells are patterned
                             based on *PatternParams.structure_map*.
                           
                           Raises :obj:`ValueError` for other values.
                           Defaults to :obj:`None`, which also raises the error.
                           """
    PatternParams.num_cell_repeat.__doc__ = \
                           """(:class:`Tuple`) A Tuple of integers in the shape of *(x,y)*
                           or *(x,y,z)* defining the number of times the unit cell
                           is to be repeated in the x, y, and z directions.
                           
                           Used only when *PatternParams.pattern_mode == 'uniform'*.
                           
                           Defaults to :obj:`None`.
                           """
    PatternParams.structure_map.__doc__ = \
                           """(:class:`np.array`) A numpy array containing integer ids of
                           unit cells and how they are distributed in the structure.
                           The unit cells must be compatible for patterning.
                           
                           Used only when *PatternParams.pattern_mode == 'nonuniform'*.
                           
                           Defaults to :obj:`None`.
                           """#TODO: elaboarte and crossref.
except (AttributeError, TypeError) as e:
    pass
#### End   PatternParams ####

#### Begin MaterialParams ####
##TODO: check docs.
MaterialParams = \
    namedtuple('MaterialParams',
               ['elastic', 'density', 'hyperelastic'] )
MaterialParams.__new__.__defaults__ = (None, None, None)
try:
    MaterialParams.__doc__ = """namedtuple instance describing the material used for modeling and analysis.
                             Care should be taken not to define contradicting properties.
                             """
    
    MaterialParams.elastic.__doc__ = \
                           """(:class:`Tuple`) Isotropic and temperature independent
                           elastic property. It should be a Tuple :math:`(E, \\nu)`
                           where :math:`E` is Young's Modulus
                           and :math:`\\nu` is Poisson's Ratio.
                           
                           Defaults to :obj:`None`, which does not define this property.
                           """
    
    MaterialParams.density.__doc__      = \
                           """(:class:`Float`) Isotropic and temperature independent
                           material Density.
                           
                           Defaults to :obj:`None`, which does not define this property.
                           """
    
    MaterialParams.hyperelastic.__doc__ = \
                           """(:class:`Tuple`) Isotropic and temperature independent
                           hyperelastic property.
                           It should be a Tuple *(type, data)* where *data* is
                           one of the following:
                           
                           * **'ogden'**: The Ogden form of strain energy potential hyperelastic model.
                             *data* must be an iterable
                             :math:`( (\\sigma_0,\\epsilon_0), (\\sigma_1,\\epsilon_1), ...)`
                             where each pair :math:`(\\sigma_i,\\epsilon_i)` are a point in the
                             isotropic uniaxial stress-strain test data.
                           * **'marlow'**: The Marlow form of strain energy potential hyperelastic model.
                             *data* is similar to the *'ogden'* option.
                           
                           Defaults to :obj:`None`, which does not define this property.
                           """
except (AttributeError, TypeError) as e:
    pass
#### End   MaterialParams ####

#### Begin StepParams ####
StepParams = \
    namedtuple('StepParams',
               ['time_period' , 'init_inc_size',
                'min_inc_size', 'max_inc_size' , 'max_num_inc'] )
StepParams.__new__.__defaults__ = (1, 0.1, 0.05, 0.1, 100)
try:
    StepParams.__doc__ = """namedtuple instance describing the step defined for analysis."""
    StepParams.time_period.__doc__   = """(:class:`float`) Total time period of the step. Defaults to 1."""
    StepParams.init_inc_size.__doc__ = """(:class:`float`) Inital increment size. Defaults to 0.1."""
    StepParams.min_inc_size.__doc__  = """(:class:`float`) Minimum increment size. Defaults to 0.05."""
    StepParams.max_inc_size.__doc__  = """(:class:`float`) Maximum increment size. Defaults to 0.1."""
    StepParams.max_num_inc.__doc__   = """(:class:`float`) Maximum number of increments. Defaults to 100."""

except (AttributeError, TypeError) as e:
    pass
#### End   StepParams ####

#### Begin LoadingParams ####
LoadingParams = \
    namedtuple('LoadingParams',
               ['type', 'direction', 'data'] )
LoadingParams.__new__.__defaults__ = (None, None,None)
try:
    LoadingParams.__doc__ = """namedtuple instance describing the loading applied to the model.
                           """
    LoadingParams.type.__doc__ = \
                           """(:class:`str`) The type of loading applied to the model.
                           Valid values are:
                           
                           * **'disp'**: Uniaxial monotonic displacement boundary condition.
                             *loading_data* must be a :class:`float`.
                           
                           * **'force'**: Uniaxial monotonic concentrated force.
                             *loading_data* must be a :class:`float`.
                           
                           Raises :obj:`ValueError` for other values.
                           Defaults to :obj:`None`, which also raises the error.
                           """
    LoadingParams.direction.__doc__ = \
                           """(:class:`str`) Direction of loading applied to the model.
                           Must be *'x'* or *'y'*. *'z'* is currently not supported.
                           Note that this also affects the positioning of the ribbons.
                           
                           Raises :obj:`ValueError` for other values.
                           Defaults to :obj:`None`, which also raises the error.
                           """
    LoadingParams.data.__doc__ = \
                           """The amount of loading applied to the model.
                           See *loading_type* for format.
                           
                           This variable is not validated, except for default Abaqus validations
                           for each BC/Loading type. Define with caution.
                           
                           Defaults to :obj:`None`.
                           """
except (AttributeError, TypeError) as e:
    pass
#### End   LoadingParams ####

#### Begin MeshParams ####
MeshParams = \
    namedtuple('MeshParams',
               ['seed_size', 'elem_shape', 'elem_code', 'elem_library'] )
MeshParams.__new__.__defaults__ = (None, None, None, None)
try:
    MeshParams.__doc__  = \
                               """namedtuple instance describing the mesh applied to the model.
                               See Abaqus documentation for definitions and discussions
                               of each parameter's significance.
                               """
    MeshParams.seed_size.__doc__    = \
                               """(:class:`float`) Size of the seed used for mesh generation.
                               Defaults to :obj:`None` which raises an error.
                               """
    MeshParams.elem_shape.__doc__   = \
                               """(:class:`str`) Shape of the elements used in the mesh.
                               Valid values are *'QUAD'*, *'QUAD_DOMINATED'*, *'TRI'*,
                               *'HEX'*, *'HEX_DOMINATED'*, *'TET'*, and *'WEDGE'*.
                               
                               Specified values must be correct with respect to
                               *MeshParams.elem_code* and structure geometry.
                               No validation is performed except for errors
                               raised by Abaqus CAE or solver.
                               
                               Defaults to :obj:`None` which raises an error.
                               """
    MeshParams.elem_code.__doc__    = \
                               """(:class:`str`) Element code used in the mesh.
                               Values must be upper-case strings naming the element code,
                               such as 'C3D10HS', 'CPE4H', or 'C3D8R'.
                               Can also be a tuple of mentioned values for
                               QUAD_DOMINATED or HEX_DOMINATED element shapes.
                               
                               Specified element code(s) must be correct with respect to
                               *MeshParams.elem_shape* and structure geometry.
                               
                               Defaults to :obj:`None` which raises an error.
                               """
    MeshParams.elem_library.__doc__  = \
                               """(:class:`str`) Element library used in the mesh.
                               Must be the same as the analysis type defined in *StepParams*.
                               Valid values are *'STANDARD'* and *'EXPLICIT'*,
                               
                               Defaults to :obj:`None` which raises an error.
                               """                               
except (AttributeError, TypeError) as e:
    pass

all_elem_shape_list   = ['QUAD', 'QUAD_DOMINATED', 'TRI',
                         'HEX' , 'HEX_DOMINATED' , 'TET', 'WEDGE']
all_elem_library_list = ['STANDARD', 'EXPLICIT']
# The following list is only used for the GUI.
# The API uses duck typing for element codes.
all_elem_code_list    = ['CPE4H', 'C3D8R']
#### End   MeshParams ####

#### Begin JobParams ####
JobParams = \
    namedtuple('JobParams',
               ['description', 'numCpus', 'memoryPercent',
                'explicitPrecision', 'nodalOutputPrecision'] )
JobParams.__new__.__defaults__ = ('', 1, 90, 'single', 'single')
try:
    JobParams.__doc__ = """namedtuple instance describing the job created for analysis."""
    JobParams.description.__doc__          = """(:class:`str`) Description of the job. Defaults to an empty string."""
    JobParams.numCpus.__doc__              = """(:class:`int`) Number of CPU cores used for the analysis. Defaults to 1."""
    JobParams.memoryPercent.__doc__        = """(:class:`int`) Amount of RAM in percent allocated to the analysis. Defaults to 90."""
    JobParams.explicitPrecision.__doc__    = \
                               """(:class:`str`) Precision used for Abaqus/Explicit solver.
                               Valid values are *'SINGLE'* and *'DOUBLE'*. Defaults to *'single'*.
                               """
    JobParams.nodalOutputPrecision.__doc__    = \
                               """(:class:`str`) Nodal output precision.
                               Valid values are *'SINGLE'* and *'DOUBLE'*. Defaults to *'single'*.
                               """
except (AttributeError, TypeError) as e:
    pass
#### End   JobParams ####

#### Begin OutputParams ####
OutputParams = \
    namedtuple('OutputParams',
               ['result_folder_name',
                'save_cae', 'save_odb', 'save_job_files',
                'export_extrusion_depth', 'export_ribbon_width',
                'export_stl', 'export_stp'])
OutputParams.__new__.__defaults__ = (None,
                                     True, True, True,
                                     None, None,
                                     False, False)
# This entire block only runs under Python 3.5+,
# because docstrings are immutable. However,
# it is written for documentation using sphinx.
try:
    OutputParams.__doc__ = """namedtuple instance describing the parameters
                           for outputting the results of modeling and analysis.
                           """
    OutputParams.result_folder_name.__doc__ = \
                           """Path to the folder where the requested results are to be stored.
                           Everything else is left at the working folder.
                           If set to :obj:`None`, a suitable name is selected using #TODO.
                           
                           Defaults to :obj:`None`.
                           """
    OutputParams.save_cae.__doc__ = \
                           """Whether or not to save the model database (.cae file). Defaults to :obj:`True`."""
    OutputParams.save_odb.__doc__ = \
                           """Whether or not to save the output database (.odb file). Defaults to :obj:`True`."""
    OutputParams.save_job_files.__doc__ = \
                           """Whether or not to save the miscellaneous job files
                           (inp, msg, log, and sta files). Defaults to :obj:`True`.
                           """
    OutputParams.export_extrusion_depth.__doc__ = \
                           """:class:`Float` defining the depth used for extruding a planar structure
                           for 3D export.
                           
                           Must be positive, but can be :obj:`None` if the part
                           is not planar or will not be exported
                           (both export_stl are export_stp are :obj:`False`).
                           
                           Defaults to :obj:`None`.
                           """
    OutputParams.export_ribbon_width.__doc__ = \
                           """:class:`Float` defining the ribbon width used for exporting the part.
                           Must be positive, but can be :obj:`None` if the part
                           will not be exported (both export_stl are export_stp are :obj:`False`).
                           
                           Defaults to :obj:`None`.
                           """
    OutputParams.export_stl.__doc__ = \
                           """Whether or not to export the structure in the STL format. Defaults to :obj:`False`."""
    OutputParams.export_stp.__doc__ = \
                           """Whether or not to export the structure in the STP format. Defaults to :obj:`False`."""
except (AttributeError, TypeError) as e:
    pass
#### End   OutputParams ####