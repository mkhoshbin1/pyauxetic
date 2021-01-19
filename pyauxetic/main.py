""" Main functions of the PyAuxetic API.

This package contains the main functions used in the PyAuxetic API which are
used for creating and analyzing one or more auxetic structures.
It also defines the bindings for the GUI library used in the Abaqus plugin.
"""
import os, logging
from math import sin, tan
import numpy as np

from . import classes
from . import helper
from . import postprocessing
from .version import __version__
from .classes.auxetic_structure_params import *

logger = logging.getLogger(__name__)

#TODO: put the main procedure in try/except/log.

def main_single(unit_cell_name  , structure_name   ,
                unit_cell_params, pattern_params   ,
                material_params ,                   
                loading_params  , mesh_params      ,
                job_params      , output_params    ,
                step_params=None, run_analysis=True,
                is_part_of_batch=False):
    """Model and analyze a single auxetic structure.
    
    Args:
        unit_cell_name (str): Type of the structure. See #TODO for a complete list of values.
        structure_name (str): Name of the structure. Used for all output files.
        
        unit_cell_params: Parameters describing the unit cell geometry.
                          Valid classes must be selected from
                          :mod:`.classes.auxetic_unit_cell_params` based on *unit_cell_name*.
                          For nonuniform structures, must be a tuple where all unit cell ids
                          used in *structure_map* are defined.
        
        pattern_params(PatternParams):   Special namedtuple describing the parameters
                                         for patterning the unit cell(s).
                                         See class for full description of options.
        
        material_params(MaterialParams): Special namedtuple describing the material
                                         used for modeling and analysis.
                                         See class for full description of options.
        
        step_params(StepParams):         Special namedtuple describing
                                         the step defined for analysis.
                                         If not specified, the default values of
                                         the namedtuple are used.
                                         See class for full description of options.
                                         Defaults to :obj:`None` which uses
                                         the default step values.
        
        loading_params(LoadingParams):   Special namedtuple describing the loading
                                         and boundary conditions applied to the model.
                                         See class for full description of options.
        
        mesh_params(MeshParams):         Special namedtuple describing
                                         the mesh applied to the model.
                                         See class for full description of options.
        
        job_params(JobParams):           Special namedtuple describing
                                         the job created for analysis.
                                         See class for full description of options.
        
        output_params(OutputParams):     Special namedtuple describing the parameters
                                         for outputting the results of modeling and analysis.
                                         See class for full description of options.
        
        run_analysis(bool):              If :obj:`True`, The model is analyzed.
                                         Otherwise *material_params*, *step_params*,
                                         *mesh_params*, *job_params*, and *output_params*
                                         are need not be defined. Defaults to :obj:`True`.
        
        is_part_of_batch(bool):          If calling from :func:`.main_batch`, 
                                         must be set to :obj:`True`. Defaults to :obj:`False`.
        
    Returns:
        An object of a subclass of :class:`AuxeticStructure` class.
    
    """
    
    #TODO: doc=> step_params = (init_inc_size, min_inc_size, max_inc_size, max_num_inc)
    #TODO: cae, etc. are not exported when run_analysis=False.
    #TODO: don't need material type when run_analysis=False.
    #TODO: add step_params as namedtuple.
    
    
    if not is_part_of_batch:
        logger.info('Starting pyAuxetic v%s', __version__)
    logger.info('Starting modeling and analysis for %s structure %s.',
                pattern_params.pattern_mode, structure_name)
    
    unit_cell_class = classes.return_unit_cell_class(unit_cell_name)
    logger.info('The structure is of type %s.', unit_cell_class.pretty_name)
    
    
    folder_path = helper.return_results_folder_path(structure_name, output_params.result_folder_name)
    logger.info('Results will be placed in %s.', folder_path)
    if os.path.isdir(folder_path):
        raise RuntimeError("'%s' already exists. Delete it before proceeding."%folder_path)
    
    # The abaqus module cannot be imported in the GUI code,
    # so only import it when running. #TODO: test. there is a abaqus.session somewhere else.
    logger.info('Creating the model.')
    logger.debug('Opening a new Mdb.')
    from abaqus import Mdb
    
    logger.info('Modeling structure geometry.')
    auxeticObj = unit_cell_class(model=Mdb().models.values()[0],
                                 name=structure_name, loading_params=loading_params)
    
    auxeticObj.add_unit_cells(unit_cell_params)
    auxeticObj.add_pattern_params(pattern_params)
    auxeticObj.assemble_structure(for_3dprint=False, delete_all=True)
    logger.info('Modeling of structure geometry completed.')
    #TODO: save mdb here.
    
    if run_analysis:
        logger.info('Preparing the analysis.')
        auxeticObj.assign_material(material_params)
        if step_params is not None:
            auxeticObj.define_step(step_params)
        else:
            auxeticObj.define_step()
        auxeticObj.define_bcs(loading_params)
        auxeticObj.mesh_part(mesh_params)
        auxeticObj.create_job(job_params)
        auxeticObj.submit_job()
        auxeticObj.output_results(output_params)
        logger.info('Analysis of structure %s completed.', structure_name)
    
    logger.info('Modeling and analysis of structure %s completed.', structure_name)
    return auxeticObj

def main_batch(unit_cell_name       , structure_prefix,
               unit_cell_params_list, pattern_params  ,
               material_params      ,                  
               loading_params       , mesh_params     ,
               job_params           , output_params   ,
               step_params=None     , run_analysis=True):
    """Run a number of analysis in succession and merge the results to a single csv file.
    
    All paramters of this function are the same as :func:`.main_single`.
    
    The exceptions are:
    
    Args:
        structure_prefix (str): The prefix used for all structures.
                                This prefix together with a number is used
                                for defining *structure_name*.
        
        unit_cell_params_list:  A list of unit_cell_params for the structures.
                                The id in each parameter must be unique and is
                                used for defining *structure_name*.
    
    All other parameters are passed without change or validation.
    """
    
    #TODO: better doc. outline unit_cell_params_list,
    #structure_prefix and result_folder_name.
    #TODO: raise on nonuniform.
    
    logger.info('Starting pyAuxetic v%s', __version__)
    logger.info('Starting batch modeling and analysis of %i structures.',
                len(unit_cell_params_list))
    
    folder_path = helper.return_results_folder_path(structure_prefix+'-batch run',
                                                    output_params.result_folder_name)
    logger.info('Results will be placed in %s.', folder_path)
    if os.path.isdir(folder_path):
        raise RuntimeError("'%s' already exists. Delete it before proceeding."%folder_path)
    output_params._replace(result_folder_name=folder_path) # TODO FIXME: this does not work.
    
    analysis_id          = 1
    analysis_ids         = []
    structure_names      = []
    results_folder_paths = []
    for unit_cell_params in unit_cell_params_list:
        structure_name = structure_prefix + '-%03i'%analysis_id
    
        auxeticObj = main_single(unit_cell_name  , structure_name,
                                 unit_cell_params, pattern_params,
                                 material_params ,                
                                 loading_params  , mesh_params   ,
                                 job_params      , output_params ,
                                 step_params     , run_analysis  ,
                                 is_part_of_batch=True)
        analysis_ids.append(analysis_id)
        structure_names.append(structure_name)
        results_folder_paths.append( auxeticObj.results_folder_path )#TODO: does not work if run_analysis==False.
        analysis_id += 1
    
    postprocessing.write_batch_numerical_output(1.0, unit_cell_params_list,
                                 structure_names, analysis_ids, results_folder_paths,
                                 folder_path=os.path.split(results_folder_paths[0])[0])
    logger.info('Batch modeling and analysis completed.')
#

def main_gui_proxy(**kwargs):
    """This function is not documented.
    You need extensive knowledge of Abaqus GUI design to modify it.
    Use caution and test extensively.
    """
    #Note: When defining namedtuples, assign using the parameters name
    #      so it does not break if the order or number of parameters changes.
    
    ## Modeling tab
    # General Parameters.
    unit_cell_name    = kwargs['unit_cell_name'   ]
    unit_cell_variant = kwargs['unit_cell_variant']
    structure_type    = kwargs['structure_type'   ]
    modeling_mode     = kwargs['modeling_mode'    ]
    
    if unit_cell_name not in classes.auxetic_unit_cell_params.unit_cells_list:
        raise RuntimeError('unit_cell_name is invalid.'
                           ' This should not have been available in the GUI.')
    if unit_cell_variant not in \
            classes.auxetic_unit_cell_params.unit_cell_variant_dict[unit_cell_name]:
        raise RuntimeError('unit_cell_variant is invalid for this unit cell.'
                           ' This should not have been available in the GUI.')
    if structure_type not in \
            classes.auxetic_unit_cell_params.structure_type_dict[unit_cell_name]:
        raise RuntimeError('structure_type is invalid for this unit cell.'
                           ' This should not have been available in the GUI.')
    
    # Parameters that depend on structure modeling mode.
    if   modeling_mode == 'Uniform (Single)':
        structure_mode         = 'uniform'#TODO: delete
        pattern_mode           = 'uniform'
        structure_name         = kwargs['uniform_structure_name'        ]
        loading_direction      = kwargs['uniform_loading_direction'     ]
        structure_params_table = kwargs['uniform_structure_params_table']
        num_cell_repeat        = kwargs['uniform_num_cell_repeat'       ]
        structure_map          = None
        
    elif modeling_mode == 'Uniform (Batch)':
        structure_mode         = 'batch'#TODO: delete
        pattern_mode           = 'uniform'
        structure_prefix       = kwargs['batch_structure_prefix'      ]
        loading_direction      = kwargs['batch_loading_direction'     ]
        structure_params_table = kwargs['batch_structure_params_table']#TODO: rename to table. also add to uniform.
        num_cell_repeat        = kwargs['batch_num_cell_repeat'       ]
        structure_map          = None
        
    elif modeling_mode == 'Non-Uniform':
        structure_mode         = 'nonuniform'#TODO: delete
        pattern_mode           = 'nonuniform'
        structure_name         = kwargs['nonuniform_structure_name'        ]
        loading_direction      = kwargs['nonuniform_loading_direction'     ]
        structure_params_table = kwargs['nonuniform_structure_params_table']#TODO: rename to table. also add to uniform.
        structure_map          = np.fliplr(
                                     np.array(
                                         kwargs['nonuniform_structure_map_table']).T )
        num_cell_repeat        = None
        
    else:
        raise ValueError('Invalid value for modeling_mode.')
    
    if loading_direction[0].lower() not in ['x', 'y']:
        raise ValueError("loading_direction[0].lower() must be 'x' or 'y'.")
    loading_direction = loading_direction[0].lower()
    
    # Get objects related to the unit cell.
    unit_cell_params_class = classes.auxetic_unit_cell_params.unit_cell_params_class_dict[
                                 (unit_cell_name, unit_cell_variant) ]
    full_unit_cell_name = classes.auxetic_unit_cell_params.unit_cell_name_dict[
                                 (unit_cell_name, structure_type) ]
    # Define pattern_params.
    pattern_params = PatternParams(pattern_mode    = pattern_mode   ,
                                   num_cell_repeat = num_cell_repeat,
                                   structure_map   = structure_map  )
    
    # Define loading_params with only loading direction.
    # It may be defined later.
    loading_params = LoadingParams(direction=loading_direction)
    
    # Define unit_cell_params.
    if modeling_mode == 'Uniform (Single)':
        # unit_cell_params is shaped as: ((2,), (3,), (4,), (5,))
        # Unit Cell ID is not imported and also not in the form,
        # prepend an arbitrary number, e.g. 1, as a placeholder.
        unit_cell_params = \
            unit_cell_params_class( *([1,]+[ r[0] for r in structure_params_table ]) )
    else:  # It has been validated to be either 'Uniform (Batch)' or 'Non-Uniform'.
        # unit_cell_params is shaped as: (r1, r2, r3, r4)
        # where rx are rows containing full list of parameters
        # including Unit Cell ID.
        unit_cell_params = [ 
            unit_cell_params_class( *params ) for params in structure_params_table ]
    
    ## Analysis tab
    if kwargs['run_analysis']:
        run_analysis = True
    else:
        run_analysis = False
    
    if run_analysis:
        # Define material_params.
        if   kwargs['material_type'] == 'Elastic':
            material_params = MaterialParams(elastic = kwargs['material_elastic_table'])
        elif kwargs['material_type'] == 'Hyperelastic - Ogden':
            material_params = MaterialParams(hyperelastic = ('ogden', kwargs['material_stress_strain_table']))
        elif kwargs['material_type'] == 'Hyperelastic - Marlow':
            material_params = MaterialParams(hyperelastic = ('marlow',kwargs['material_stress_strain_table']))
        else:
            raise ValueError("Unexpected value for 'material_type'.")
        
        # Define step_params.
        step_params = StepParams(time_period   = kwargs['step_time_period'  ],
                                 init_inc_size = kwargs['step_init_inc_size'],
                                 min_inc_size  = kwargs['step_min_inc_size' ],
                                 max_inc_size  = kwargs['step_max_inc_size' ],
                                 max_num_inc   = kwargs['step_max_num_inc'  ])
        
        # Define job_params.
        job_params = JobParams(description          = '',
                               numCpus              = kwargs['job_num_cpu'  ],
                               memoryPercent        = kwargs['job_max_ram'  ],
                               explicitPrecision    = kwargs['job_precision'],
                               nodalOutputPrecision = kwargs['job_precision'])
        
        # Re-Define loading_params with the rest of arguments.
        loading_params = LoadingParams(type      = kwargs['loading_type' ],
                                       direction = loading_direction      ,
                                       data      = kwargs['loading_value'])
        
        # Define mesh_params.
        mesh_params = MeshParams(seed_size    = kwargs['mesh_seed_size' ],
                                 elem_shape   = kwargs['mesh_elem_shape'],
                                 elem_code    = kwargs['mesh_elem_code' ],
                                 elem_library = 'STANDARD') #This must change.
    else:
        material_params = MaterialParams()
        step_params     = StepParams()
        job_params      = JobParams()
        mesh_params     = MeshParams()
        # loading_params has already been defined.
    
    # Define output_params.
    output_params = OutputParams(result_folder_name     = None                         ,
                                 save_cae               = kwargs['save_cae'           ],
                                 save_odb               = kwargs['save_odb'           ],
                                 save_job_files         = kwargs['save_job_files'     ],
                                 export_extrusion_depth = kwargs['extrusion_depth'    ],
                                 export_ribbon_width    = kwargs['export_ribbon_width'],
                                 export_stl             = kwargs['export_stl'         ],
                                 export_stp             = kwargs['export_stp'         ])
    # The following are not used. They must first be implemented in the API.
    #write_results       = kwargs['write_results'      ]
    #output_pic_poi      = kwargs['output_pic_poi'     ]
    #output_pic_deformed = kwargs['output_pic_deformed'] # Not in GUI.
    #output_pic_mises    = kwargs['output_pic_mises'   ]
    #output_pic_peeq     = kwargs['output_pic_peeq'    ]
    #output_pic_all_inc  = kwargs['output_pic_all_inc' ]
    #export_3d_model_kw  = kwargs['export_3d_model_kw' ] # Not in GUI.
    #output_pic_poi, output_pic_mises, output_pic_peeq, output_pic_all_inc
    #result_folder_name
    
    
    if modeling_mode == 'Uniform (Batch)':
        main_batch(full_unit_cell_name, structure_prefix,
                   unit_cell_params   , pattern_params  ,
                   material_params    ,                  
                   loading_params     , mesh_params     ,
                   job_params         , output_params   ,
                   step_params        , run_analysis)
    
    else:  # It has been validated to be either 'Uniform (Single)' or 'Non-Uniform'.
        main_single(full_unit_cell_name, structure_name,
                    unit_cell_params   , pattern_params,
                    material_params    ,                
                    loading_params     , mesh_params   ,
                    job_params         , output_params ,
                    step_params        , run_analysis)
    
    #TODO: catch KeyError for when a required parameter is not input in GUI.
    # this should probably be done when calling this function.
    # perhaps the focus can be set to that field, but it's unlikely.
    #TODO: unused unit cells in nonuniform structures are leftover. delete them.
    #TODO: what happens if in the unit_cell_params_list gui there are empty cells
    # which have an id?
    #TODO: extrusion_depth in unit_cell_params is meant for solid models only,
    # remove/hide it in the GUI.