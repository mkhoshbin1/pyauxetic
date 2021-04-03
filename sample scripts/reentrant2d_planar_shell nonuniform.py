import sys
import numpy as np

# Change this variable to to the path to the folder containing
# the pyauxetic repository. This could be any folder such as
# your Desktop, or Abaqus' plugin path: C:\SIMULIA\CAE\plugins\2021\pyauxetic.
# Note that if you downloaded pyauxetic as a zip file,
# it will probably have a version suffix which you should remove.
pyauxetic_library_path = r'C:\path\to\pyauxetic'
sys.path.append(pyauxetic_library_path)

from pyauxetic.classes.auxetic_unit_cell_params import *
from pyauxetic.classes.auxetic_structure_params import *
from pyauxetic.main import main_single

structure_type = 'reentrant2d_planar_shell'
structure_name = 'unnamed'

unit_cell_params = []
# (id, extrusion_depth, horz_bounding_box, vert_bounding_box, vert_strut_thickness, diag_strut_thickness, diag_strut_angle)
unit_cell_params.append( Reentrant2DUcpBox( 1, 5, 20, 24, 3.0, 1.5, 60) )
unit_cell_params.append( Reentrant2DUcpBox( 2, 5, 20, 24, 3.0, 1.5, 60) )
unit_cell_params.append( Reentrant2DUcpBox( 3, 5, 20, 24, 2.0, 1.5, 60) )
unit_cell_params.append( Reentrant2DUcpBox( 4, 5, 20, 24, 2.0, 1.5, 65) )
unit_cell_params.append( Reentrant2DUcpBox( 5, 5, 20, 24, 2.0, 1.5, 60) )
unit_cell_params.append( Reentrant2DUcpBox( 6, 5, 20, 24, 2.0, 1.5, 60) )
unit_cell_params.append( Reentrant2DUcpBox( 7, 5, 20, 24, 2.0, 1.5, 80) )
unit_cell_params.append( Reentrant2DUcpBox( 8, 5, 20, 24, 2.0, 1.5, 60) )
unit_cell_params.append( Reentrant2DUcpBox( 9, 5, 20, 24, 2.0, 1.5, 70) )
unit_cell_params.append( Reentrant2DUcpBox(10, 5, 20, 24, 2.0, 3.0, 60) )

structure_map = np.array([
    [1, 2, 4, 9, 10, 8, 7, 4, 2, 2],
    [1, 2, 4, 9, 10, 8, 1, 4, 2, 2],
    [1, 2, 4, 9, 10, 8, 7, 4, 2, 2],
    [1, 2, 4, 9, 10, 8, 7, 4, 2, 2],
])
pattern_params = PatternParams(
    pattern_mode    = 'nonuniform',
    num_cell_repeat = None        ,
    structure_map = np.fliplr( structure_map.T )
)

material_params = MaterialParams(
    elastic      = None,
    density      = None,
    hyperelastic = ('marlow',
                    ((0.0,0.0),(1.87019,0.021918),(3.76788,0.041096),(5.63806,0.062101),(7.48075,0.086758),(9.15842,0.122374),(10.4785,0.170776),(11.4686,0.226484),(12.3212,0.285845),(13.0638,0.346119),(13.7514,0.407306),(14.5215,0.468493),(15.4015,0.526941),(16.3916,0.583562),(17.3542,0.641096),(18.2893,0.699543),(19.2244,0.757078),(20.242,0.812785),(21.3146,0.866667),(22.3872,0.921461),(23.4598,0.977169),(24.5325,1.03288),(25.6601,1.08676),(26.7877,1.14064),(27.8603,1.19543),(28.8779,1.25205),(29.868,1.30868),(30.7756,1.36621),(31.6832,1.42557),(32.5908,1.48402),(33.4983,1.54247),(34.3784,1.60091),(35.286,1.65936),(36.1661,1.71781),(37.0462,1.77626),(37.9813,1.8347),(38.8889,1.89315),(39.824,1.9516),(40.7591,2.00913),(41.7217,2.06667),(42.6843,2.1242),(43.7019,2.18082),(44.7195,2.23653),(45.7096,2.29315),(46.6997,2.34977),(47.7173,2.40639),(48.6249,2.46484),(49.505,2.5242),(50.44,2.58265),(51.4301,2.63927),(52.3927,2.6968),(53.3828,2.75434),(54.3454,2.81096),(55.198,2.87032),(55.8581,2.93242))
                   )
    )

step_params = StepParams(
    time_period   = 1.0 ,
    init_inc_size = 0.1 ,
    min_inc_size  = 0.05,
    max_inc_size  = 0.1 ,
    max_num_inc   = 100
    )

loading_params = LoadingParams(
    type      = 'disp',
    direction = 'x'   ,
    data      = 20.0
    )

mesh_params = MeshParams(
    seed_size    = 1.0,
    elem_shape   = 'QUAD' ,
    elem_code    = ('CPE4H'),
    elem_library = 'STANDARD'
    )

job_params = JobParams(
    description          = '',
    numCpus              = 2 ,
    memoryPercent        = 80,
    explicitPrecision    = 'SINGLE',
    nodalOutputPrecision = 'SINGLE',
    )

output_params = OutputParams(
    result_folder_name     = None,
    save_cae               = True,
    save_odb               = True,
    save_job_files         = True,
    export_ribbon_width    = 4.0 ,
    export_stl             = True,
    export_stp             = True
    )

run_analysis = True

auxeticObj = main_single(structure_type  , structure_name,
                         unit_cell_params, pattern_params,
                         material_params ,                
                         loading_params  , mesh_params   ,
                         job_params      , output_params ,
                         step_params     , run_analysis)
