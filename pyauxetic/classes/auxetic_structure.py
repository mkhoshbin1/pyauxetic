import os
import logging
from abc import ABCMeta, abstractmethod
from collections import Iterable
import numpy as np

from abaqusConstants import *  # noqa: F403
from mesh import ElemType
from odbAccess import openOdb
from regionToolset import Region

from .  import auxetic_structure_params  # noqa: E272
from .. import helper
from .. import postprocessing

logger = logging.getLogger(__name__)


class AuxeticStructure:
    """Abstract base class for defining an auxetic structure.
    It defines the core behavior and must be subclassed for structures using different unit cells.
    
    The following methods must be called in this exact order:
    
        1. :meth:`.add_unit_cells`
        2. :meth:`.add_pattern_params`
        3. :meth:`.assemble_structure`
        4. :meth:`.define_step`
        5. :meth:`.define_bcs`
        6. :meth:`.mesh_part`
        7. :meth:`.create_job`
        8. :meth:`.submit_job`
        9. :meth:`.output_results`
    """
    __metaclass__ = ABCMeta
    
    def __init__(self, model, name, loading_params):
        """Initialize the auxetic structure.
        
        Child classes must define the following and class variables
        and then call this constructor:
        
          + pretty_name    
          + is_solid       
          + is_shell       
          + is_bulk        
          + is_planar      
          + is_tubular     
          + unit_cell_class
        
        Args:
            model (Model): Abaqus Model object in which the auxetic structure will be created.
            name (str):    Name of the structure. It will be used for all related files.
            loading_params(LoadingParams):
                           Special namedtuple describing the loading
                           and boundary conditions applied to the model.
                           Here, *loading_params.direction* is used for
                           determining positioning of loading ribbons.
        """
        
        logger.debug('Initializing AuxeticStructure object.')
        
        self.model = model
        self.name  = name
        self.unit_cells            = []           # Assigned in add_unit_cells.
        self.pattern_mode          = None         # Assigned in add_pattern_params.
        self.structure_map         = None         # Assigned in add_pattern_params.
        self.num_cell_repeat       = None         # Assigned in add_pattern_params.
        self.part_main             = None         # Assigned in assemble_structure.
        self.part_3dprint          = None         # Assigned in assemble_structure.
        self.part_main_instance    = None         # Assigned in assemble_structure.
        self.part_3dprint_instance = None         # Assigned in assemble_structure.
        self.sets                  = dict()       # Assigned in perpare_for_loading.
        self.loading_rps           = [None, None] # Assigned in perpare_for_loading.
        self.job                   = None         # Assigned in create_job.
        self.odb_path              = None         # Assigned in submit_job.
        if   loading_params.direction.lower() == 'x':
            self.loading_direction    = 0
            self.transverse_direction = 1
        elif loading_params.direction.lower() == 'y':
            self.loading_direction    = 1
            self.transverse_direction = 0
        else:
            raise ValueError("loading_params.direction must be 'x' or 'y'.")
        logger.info('Initialized AuxeticStructure object named %s.', self.name)
    #
    
    @abstractmethod
    def assemble_structure(self, for_3dprint=False, output_params=None, delete_all=True):
        """Assemble one or more unit cells according to pattern parameters
        to create the auxetic structure. :meth:`.add_pattern_params` must be called before this.
        
        This function must be defined by each child class of :class:`AuxeticStructure`
        
        Args:
            for_3dprint(bool): If :obj:`True`, the structure will be a 3D part
                               suitable for export, Otherwise dimensionality will
                               be governed by the structure. Defaults to :obj:`False`.
            output_params(OutputParams):
                               Special namedtuple describing the parameters
                               for outputting the results of modeling and analysis.
                               See class for full description of options.
                               Here, *output_params.export_extrusion_depth*
                               it is used for deteriming ribbon_extrusion_depth.
                               If for_3dprint is :obj:`False`, this need not be
                               passed. Defaults to :obj:`None`.
                               
            delete_all(bool):  If :obj:`True`, all useless parts will be deleted.
                               Defaults to :obj:`True`.
        """
        pass
    
    def add_pattern_params(self, pattern_params):
        """Add the parameters used by :meth:`.assemble_structure` for assembling the structure.
        
        Args:
            pattern_params(PatternParams): Special namedtuple describing the parameters
                                           for patterning the unit cell(s).
                                           See class for full description of options.
        """
        # This must be called after all unit cells have been added
        # and this only works for 2D patterning.
        pattern_mode    = pattern_params.pattern_mode
        num_cell_repeat = pattern_params.num_cell_repeat
        structure_map   = pattern_params.structure_map
        
        logger.debug('Adding pattern data.')
        if pattern_mode == 'uniform':  #TODO: add modes to doc.
            if len(self.unit_cells) != 1:
                raise ValueError('uniform patterning requires exactly one unit cell.')
            if (num_cell_repeat is None) or (structure_map is not None):
                raise ValueError('uniform patterning requires num_cell_repeat' +
                                 'to be defined and structure_map to be None.')
            elif not isinstance(num_cell_repeat, Iterable):
                raise ValueError('num_cell_repeat must be an iterable containing 2 or 3 integers.')
            elif len(num_cell_repeat) not in [2, 3]:
                raise ValueError('num_cell_repeat must be an iterable containing 2 or 3 integers.')
            else:
                self.pattern_mode    = pattern_mode
                self.num_cell_repeat = num_cell_repeat
                self.structure_map   = np.ones([num_cell_repeat[0], num_cell_repeat[1]]) * \
                                       self.unit_cells[0].params.id
        elif pattern_mode == 'nonuniform':
            if (structure_map is None) or (num_cell_repeat is not None):
                raise ValueError('nonuniform patterning requires structure_map' +
                                 'to be defined and num_cell_repeat to be None.')
            elif type(structure_map) is not np.ndarray:
                raise ValueError('structure_map must be a numpy ndarray.')
            else:
                self.pattern_mode    = pattern_mode
                self.structure_map   = structure_map
                self.num_cell_repeat = (structure_map.shape[0], structure_map.shape[1])
            # All elements in structure_map must correspond to a unit cell.
            uc_id_list = [uc.id for uc in self.unit_cells]
            for elem in np.unique(structure_map):
                if elem not in uc_id_list:
                    raise ValueError('structure_map contains ids' +
                                     'that are not defined as unit cells.')
        else:
            raise ValueError('Invalid value for pattern_mode.')
        logger.info('Pattern data added to the structure.')
    #
    
    def add_unit_cells(self, unit_cell_params):
        """Add one or more unit cells to the auxetic structure.
        
        Args:
            unit_cell_params: Special namedtuple describing the unit cell geometry.
                              The namedtuple must be selected from 
                              :mod:`.classes.auxetic_unit_cell_params`
                              based on the type of structure.
                              For nonuniform structures, must be a tuple
                              where all unit cell ids used in
                              *self.structure_map* are defined.
        Raises:
            RuntimeError: If :meth:`.add_pattern_params` has already been called.
            ValueError:   If *unit_cell_params* is invalid.
            ValueError:   If *unit_cell_params* contains repeated or non-positive ids.
            ValueError:   If *unit_cell_params* contains more than one value
                          for extrusion_depth or it's non-positive (planar structures only).
        """
        
        logger.debug('Adding unit cell.')
        if self.pattern_mode is not None:
            raise RuntimeError('Unit cells cannot be added after' +
                               'the pattern mode has been specified.')
        
        params_class_list = self.unit_cell_class.params_class_list
        error_msg = ('unit_cell_params must be an object' +
                     ' of the following classes or' +
                     ' a homogeneus list of one of them: %s.'
                     % ', '.join( [str(x.__name__) for x in params_class_list] ) )
        if isinstance(unit_cell_params, params_class_list):
            # If it's not an iterable, it must be valid and then turned into an iterable.
            logger.debug('A single unit cell has been defined for addition'
                         ' based on %s.' %unit_cell_params.__class__.__name__)
            unit_cell_params = (unit_cell_params,)
        
        elif isinstance(unit_cell_params, Iterable):
            # If it's an iterable, all must be valid and of the same class.
            if ( isinstance(unit_cell_params[0], params_class_list) and
                 all(isinstance(x, params_class_list) for x in unit_cell_params) ):
                logger.debug('%i unit cells have been defined for addition based on %s.'
                             %(len(unit_cell_params),unit_cell_params[0].__class__.__name__))
            else:
                raise ValueError(error_msg)
        else:
            raise ValueError(error_msg)
        
        # Make sure unit cell ids are unique.
        ucp_ids = [ucp.id for ucp in unit_cell_params]
        if len( np.unique(ucp_ids) ) != len( ucp_ids ): #TEST
            raise ValueError('unit_cell_params contains repeated ids.')
        if (np.array(ucp_ids) < 1).any(): #TEST
            raise ValueError('unit_cell_params contains non-positive ids.')
        
        if self.is_planar:
            # Make sure extrusion_depth is positive and the same for all unit cells.
            ucp_extrusion_depths = [ucp.extrusion_depth for ucp in unit_cell_params]
            if len( np.unique(ucp_extrusion_depths) ) != 1: #TEST
                raise ValueError('unit_cell_params contains more than one value for extrusion_depth.')
            if ucp_extrusion_depths[0] <= 0: #TEST
                raise ValueError('unit_cell_params contains non-positive values for ucp_extrusion_depths.')
            logger.debug('All unit cells have an extrusion_depth of %f.'%ucp_extrusion_depths[0])
        
        # Initialize the unit cells and add them to structure.
        for ucp in unit_cell_params: #TODO: make sure it's the same for all unit cells.
            self.unit_cells.append( self.unit_cell_class(self.model, ucp) )
    
    logger.info('Unit cell added added to the structure.')
    #
    
    def get_unit_cell_by_id(self, id):
        """Return a unit cell in the structure based on its id.
        
        Args:
            id(int): Unique numeric ID of the unit cell.
            
        Returns:
            The unit cell whose id is specified.
            
        Raises:
            ValueError: If the unit cell does not exist.
        """
        for uc in self.unit_cells:
            if uc.id == id:
                return uc
        raise ValueError('No unit cell with id=%i'%id)
    
    def _perpare_for_loading(self):
        """Prepare the structure for loading. This function is called by :meth:`.define_bcs`.
        
        Assigns the following in the object:
        
            - **self.sets**: which contains some the following Abaqus sets (keys are italicized):
            
                + *'LD-Edge-1'*: Fixed edge in the loading direction.
                  Coupled to *self.loading_rps[0]*.
                + *'LD-Edge-2'*: Moving edge in the loading direction.
                  Coupled to *self.loading_rps[1]*.
                + *'TD-Edge-1'*: First transverse edge (side),
                  used for caluculating average Poisson's ratio.
                + *'TD-Edge-2'*: Second transverse edge (side).
                + *'Mid-Vertice-1'*: Vertex in the middle of the first transverse edge (side),
                  used for caluculating Poisson's ratio at midpoint of structure.
                + *'Mid-Vertice-2'*: Vertex in the middle of the second transverse edge (side).
            
            - **self.loading_rps**: Tuple of abaqus reference points (RPs)
              on which the BCs are applied.
              The first RP is fixed and the second undergoes force/displacement.
              These RPs are coupled using an equation to *self.sets['LD-Edge-1']*
              and *self.sets['LD-Edge-2']*, respectively.
        
        Raises:
            RuntimeError: If the part has been previously partitioned.
            AbaqusException: Various exceptions raised by the Abaqus API.
        """
        #TODO: this is private. show in sphinx. TODO.
        logger.debug('Preparing the structure for loading.')
        part = self.part_main
        assembly = self.model.rootAssembly
        if len(part.faces) != 1:
            raise RuntimeError(
                ('The Part must have exactly one face, but has %i faces' +
                 ' This is because it has been previously partitioned')%len(part.faces))
        
        # Get coordinates of points of interest.
        coords = helper.get_box_coords(object_list=part)
        point_x1_coords = (coords[0][0]  , coords[1][1]/2.0, coords[0][2])
        point_x2_coords = (coords[1][0]  , coords[1][1]/2, coords[0][2])
        point_y1_coords = (coords[1][0]/2.0, coords[0][1]  , coords[0][2])
        point_y2_coords = (coords[1][0]/2.0, coords[1][1]  , coords[0][2])
        
        # Partition the part like a cross to have proper stress paths.
        logger.debug('Partitioning the structure.')
        part.PartitionFaceByShortestPath(point1=point_x1_coords,
                                         point2=point_x2_coords,
                                         faces=part.faces )
        part.PartitionFaceByShortestPath(point1=point_y1_coords,
                                         point2=point_y2_coords,
                                         faces=part.faces )
        assembly.regenerate()
        
        # Find which vertices are in the loading and transverse directions.
        # LD and TD are loading and transverse directions
        # and 1 and 2 denote beginning and end of the part.
        if self.loading_direction == 0:
            ld_coords = (point_x1_coords, point_x2_coords)
            td_coords = (point_y1_coords, point_y2_coords)
            ld_edge_values = (coords[0][0], coords[1][0])
            td_edge_values = (coords[0][1], coords[1][1])
        else:
            ld_coords = (point_y1_coords, point_y2_coords)
            td_coords = (point_x1_coords, point_x2_coords)  # noqa: F841
            ld_edge_values = (coords[0][1], coords[1][1])
            td_edge_values = (coords[0][0], coords[1][0])
        
        # Create sets for the edges.
        logger.debug('Creating sets for the edges.')
        self.sets['LD-Edge-1'] = part.Set(name='LD-Edge-1',
                                          edges=helper.find_edges_from_coords(
                                                part=part, coord=self.loading_direction,
                                                value=ld_edge_values[0]) )
        self.sets['LD-Edge-2'] = part.Set(name='LD-Edge-2',
                                          edges=helper.find_edges_from_coords(
                                                part=part, coord=self.loading_direction,
                                                value=ld_edge_values[1]) )
        self.sets['TD-Edge-1'] = part.Set(name='TD-Edge-1',
                                          edges=helper.find_edges_from_coords(
                                                part=part, coord=self.transverse_direction,
                                                value=td_edge_values[0]) )
        self.sets['TD-Edge-2'] = part.Set(name='TD-Edge-2',
                                          edges=helper.find_edges_from_coords(
                                                part=part, coord=self.transverse_direction,
                                                value=td_edge_values[1]) )
        
        # Create sets for the midpoint vertices.
        logger.debug('Creating sets for the midpoint vertices.')
        min_max_vertices = helper.find_vertices_from_coords_minmax(
                                part=part, coord=self.loading_direction,
                                value=(ld_edge_values[1] - ld_edge_values[0])/2.0 )
        
        self.sets['Mid-Vertice-1'] = part.Set(name='Mid-Vertice-1', vertices= min_max_vertices[0])
        self.sets['Mid-Vertice-2'] = part.Set(name='Mid-Vertice-2', vertices= min_max_vertices[1])
        
        # Create reference points for loading the structure.
        logger.debug('Creating reference points for loading the structure.')
        rp_coords = [list(ld_coords[0]), list(ld_coords[1])]  # make it mutable.
        
        rp1 = assembly.ReferencePoint(point=rp_coords[0])
        rp2 = assembly.ReferencePoint(point=rp_coords[1])
        self.loading_rps[0] = assembly.Set(referencePoints=(
                        assembly.referencePoints[rp1.id], ), name='RP-1-set')
        self.loading_rps[1] = assembly.Set(referencePoints=(
                        assembly.referencePoints[rp2.id], ), name='RP-2-set')
        
        # Tie each reference points to its respective edge.
        logger.debug('Tying reference points their respective edges.')
        self.model.Equation(name='RP-1-eq-x', terms=(
                        (1.0, self.part_main_instance.name+'.'+'LD-Edge-1', 1),
                        (-1.0, 'RP-1-set', 1) ) )
        self.model.Equation(name='RP-1-eq-y', terms=(
                        (1.0, self.part_main_instance.name+'.'+'LD-Edge-1', 2),
                        (-1.0, 'RP-1-set', 2) ) )
        
        # Note: Directions are 0,1,2 in the program,
        # but have to be 1,2,3 for an equation constraint.
        self.model.Equation(name='RP-2-eq-x', terms=(
                        (1.0, self.part_main_instance.name+'.'+'LD-Edge-2', self.loading_direction+1),
                        (-1.0, 'RP-2-set', self.loading_direction+1) ) )
        
        assembly.regenerate()
        logger.info('Prepared the structure for loading.')
    #
    
    def assign_material(self, material_params):
        """Assign material properties to the auxetic structure.
        
        Note that *material_params.material_data* is not validated.
        Duck-Typing is used for calling the API and some errors are
        caught by the API itself, but ultimately any bad values are
        carried to the CAE model.
        
        Args:
            material_params(MaterialParams): Special namedtuple describing the material
                                             used for modeling and analysis.
                                             See class for full description of options.
        
        Raises:
            ValueError:      If *material_params.hyperelastic* is invalid.
            ValueError:      If *material_params.hyperelastic* is invalid.
            AbaqusException: Various exceptions raised by the Abaqus API.
        """
        
        
        logger.debug('Defining material properties for the structure.')
        model = self.model
        part = self.part_main
        
        logger.debug('Defining material properties.')
        material = model.Material(name='material')
        
        # Define Elastic property.
        if   material_params.elastic is None:
            pass
        elif len(material_params.elastic) == 2:
            material.Elastic(table=(material_params.elastic, ))
            logger.debug('Defined elastic property.')
        else:
            raise ValueError('material_params.elastic must be a Tuple containing two floats.')
        
        # Define material Density.
        if material_params.density is not None:
            material.Density(table=((material_params.density, ), ))
            logger.debug('Defined material density.')
        
        # Define Hyperelastic property.
        if material_params.hyperelastic is not None:
            if len(material_params.hyperelastic) == 2:
                type = material_params.hyperelastic[0]
                data = material_params.hyperelastic[1]
            else:
                raise ValueError('material_params.hyperelastic must be a Tuple.')
            
            if   type == 'ogden':
                material.Hyperelastic(materialType=ISOTROPIC, type=OGDEN,
                                      volumetricResponse=VOLUMETRIC_DATA, table=())
                material.hyperelastic.UniaxialTestData(table=data)
            elif type == 'marlow':
                material.Hyperelastic(materialType=ISOTROPIC, type=MARLOW, table=())
                material.hyperelastic.UniaxialTestData(table=data)
            else:
                raise ValueError('Invalid value for material_params.hyperelastic[0]')
            logger.debug('Defined hyperelastic property based on the %s material model.', type)
        
        
        logger.debug('Assigning section to the structure.')
        section = model.HomogeneousSolidSection(name='section',
                                                material=material.name, thickness=1.0)
        
        region = Region(faces=part.faces, cells=part.cells)
        part.SectionAssignment(region=region, sectionName=section.name,
                               offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', 
                               thicknessAssignment=FROM_SECTION)
        logger.debug('Assigned section to the structure.')
        logger.info('Defined material properties for the structure.')
    #
    
    def define_step(self, step_params=None):
        """Define a single step for the analysis.
        Currently, only static general steps are supported.
        The step is named *'Step-1'*, but this name is not hard-coded elsewhere.
        Also, the nonlinear geometry (NLGEOM) parameter is always turned on.
        
        Args:
            step_params(StepParams): Special namedtuple describing
                                     the step defined for analysis.
                                     If not specified, the default values of
                                     the namedtuple are used.
                                     Also, validation of values is done by Abaqus API.
                                     See class for full description of options.
        
        Raises:
            AbaqusException: Various exceptions raised by the Abaqus API.
        """
        
        if step_params is None:
            step_params = auxetic_structure_params.StepParams()
        
        time_period   = step_params.time_period
        init_inc_size = step_params.init_inc_size
        min_inc_size  = step_params.min_inc_size
        max_inc_size  = step_params.max_inc_size
        max_num_inc   = step_params.max_num_inc
        
        logger.debug('Defining step for the analysis.')
        self.model.StaticStep(name='Step-1', previous='Initial',
                              timePeriod=time_period, nlgeom=ON, maxNumInc=max_num_inc,
                              initialInc=init_inc_size, minInc=min_inc_size, maxInc=max_inc_size)
        logger.info('Defined a static general step for the analysis.')
    #
    
    def define_bcs(self, loading_params):
        """Apply loads and boundary conditions (BCs) to the structure.
        This function must be called after :meth:`.define_step`.
        It then calls :meth:`._perpare_for_loading` and afterwards
        defines the following BCs:
        
        - An Encastre BC (fixed in all 6 directions) is applied from the initial step
          on the reference point *self.loading_rps[0]*, which is coupled to *'LD-Edge-1'*.
        - A second load/BC is applied from the single loading step of the model based on
          on the reference point *self.loading_rps[1]*, which is coupled to *'LD-Edge-2'*.
          This load/BC is governed by *loading_params* and currently
          can be one of the following:
            
            + Uniaxial monotonic displacement BC.
        
        Args:
            loading_params(LoadingParams):   Special namedtuple describing the loading and
                                             and boundary conditions applied to the model.
                                             See class for full description of options.
        
        Raises:
            RuntimeError:    If the number of steps in the model is not exactly 2.
            ValueError:      If *material_params.material_type* is invalid.
            AbaqusException: Various exceptions raised by the Abaqus API.
        """
        
        loading_type      = loading_params.type
        loading_direction = loading_params.direction
        loading_data      = loading_params.data
        
        logger.debug('Defining the BCs.')
        
        # Prepare the structure for loading.
        self._perpare_for_loading()
        
        # Make sure there is exactly one step apart from 'Initial'.
        if len(self.model.steps) != 2:
            raise RuntimeError(
                ('The number of steps in the model is not exactly 2.' +
                 ' This means that either self.define_step() has not been called,' +
                 ' or steps have been manually added to the model.'))
        loading_step = self.model.steps.values()[1]
        if loading_step.previous != 'Initial':
            raise RuntimeError("loading_step is not after 'Initial'. This should not happen.")
        
        # Define the Fixed BC.
        self.model.EncastreBC(name='Fixed-BC', createStepName='Initial', 
                              region=self.loading_rps[0], localCsys=None)
        logger.debug('Defined the fixed BC.')
        
        #Define the loading.
        loading_region = self.loading_rps[1]
        if   loading_type.lower() in ['disp', 'displacement']:
            # Uniaxial monotonic displacement BC.
            # loading_data is a float.
            (u1,u2,u3,ur1,ur2,ur3) = [UNSET]*6
            if   loading_direction.lower() == 'x':
                u1 = loading_data
            elif loading_direction.lower() == 'y':
                u2 = loading_data
            elif loading_direction.lower() == 'z':
                u3 = loading_data  # noqa: F841
            else:
                raise RuntimeError("invalid value '%s' for loading_params.direction."%loading_direction)
            logger.debug('Defining the a uniaxial monotonic displacement BC.')
            #TODO: does this work for 3D? can I write one for 2D and 3D (with u3, ur1, ur2)
            self.model.DisplacementBC(name='UM-Disp-BC', createStepName=loading_step.name, 
                                      region=loading_region,
                                      distributionType=UNIFORM, fieldName='', localCsys=None,
                                      u1=u1, u2=u2, ur3=ur3, amplitude=UNSET, fixed=OFF)
            logger.info('Defined a uniaxial monotonic displacement BC with the value of %f.', loading_data)
        
        elif loading_type.lower() == 'force':
            # Uniaxial monotonic concentrated force.
            # loading_data is a float.
            (cf1,cf2,cf3) = [UNSET]*3
            if   loading_direction.lower() == 'x':
                cf1 = loading_data
            elif loading_direction.lower() == 'y':
                cf2 = loading_data
            elif loading_direction.lower() == 'z':
                cf3 = loading_data
            else:
                raise RuntimeError("invalid value '%s' for loading_params.direction."%loading_direction)
            logger.debug('Defining the a uniaxial monotonic concentrated force.')
            self.model.ConcentratedForce(name='UM-Force-BC', createStepName=loading_step.name,
                                         region=loading_region, follower=OFF,
                                         distributionType=UNIFORM, field='', localCsys=None,
                                         amplitude=UNSET,
                                         cf1=cf1, cf2=cf2, cf3=cf3)
            logger.info('Defined a uniaxial monotonic concentrated force with the value of %f.', loading_data)
        
        else:
            raise ValueError('Invalid value for loading_type: %s'%loading_type)
    #
    
    def mesh_part(self, mesh_params):
        """Mesh the model.
        
        The following functions are used in succession:
        
        + **seedPart()**: *deviationFactor* and *minSizeFactor* are
          set to 0.1 and *constraint* is not supported.
        + **setMeshControls()**: The following parameters are not supported:
          *technique*, *algorithm*, *minTransition*, *sizeGrowth*, *allowMapped*.
        + **setElementType()**: The following constraints exist:
          
          - *region* is set to all faces/cells of the structure.
          - The *elemTypes* tuple is determined by *mesh_params.elem_code*
            and *mesh_params.elem_library*.
        
        Args:
            mesh_params(MeshParams): Special namedtuple describing the mesh applied to the model.
                                     See class for full description of options.
        
        Raises:
            ValueError:      If *mesh_params.elem_shape* is invalid.
            ValueError:      If *mesh_params.elem_shape* does not correspond to
                             the structure's dimensionality.
            ValueError:      If *mesh_params.elem_library* is invalid.
            ValueError:      If *mesh_params.elem_code is invalid.
            KeyError:        If *mesh_params.elem_code* does not correspond to a SymbolicConstant.
            ValueError:      If *mesh_params.elem_code* does not correspond to an element.
            AbaqusException: Various exceptions raised by the Abaqus API.
        """
        
        logger.debug('Meshing the part.')
        import abaqusConstants as abqConst  # So as no to pollute the namespace.
        abaqusConstants_vars = vars(abqConst)
        
        # Validate and set mesh_params.elem_shape.
        elem_shape_str = mesh_params.elem_shape
        if elem_shape_str.upper() in auxetic_structure_params.all_elem_shape_list:
            elem_shape = abaqusConstants_vars[elem_shape_str.upper()]
        else:
            raise ValueError("invalid value '%s' for mesh_params.elem_shape."%elem_shape_str)
        # Make sure element shape is consistant with the structure's dimensionality.
        if self.is_solid and (elem_shape in [QUAD, QUAD_DOMINATED, TRI]):
            raise ValueError("Structure is a solid," +
                             " but mesh_params.elem_shape is set to '%s'."%elem_shape)
        if self.is_shell and (elem_shape in [HEX, HEX_DOMINATED, TET, WEDGE]):
            raise ValueError("Structure is a shell," +
                             " but mesh_params.elem_shape is set to '%s'."%elem_shape)
        
        # Validate and set mesh_params.elem_library.
        if mesh_params.elem_library.upper() in auxetic_structure_params.all_elem_library_list:
            elem_library = abaqusConstants_vars[mesh_params.elem_library.upper()]
        
        # Validate and set mesh_params.elem_code.
        ## If it's not an iterable, convert into one.
        if   isinstance(mesh_params.elem_code, str):
            elem_code_iter = (mesh_params.elem_code,)
        elif isinstance(mesh_params.elem_code, Iterable):
            elem_code_iter = mesh_params.elem_code
        else:
            raise ValueError('Invalid value for mesh_params.elem_code.')
        ## Validate over a loop.
        elem_type_list = []
        for elem_code_str in elem_code_iter:
            # Raises KeyError if elem_code_str is not a SymbolicConstant.
            # Does not actually check if it's a valid element code.
            code = abaqusConstants_vars[elem_code_str.upper()]
            # Create ElemType objects.
            new_elem_type = ElemType(elemCode=code, elemLibrary=elem_library)
            if str(type(new_elem_type)) == "<type 'ElemType'>":
                elem_type_list.append(new_elem_type)
            else:  #Should be None, but I'm not completely sure.
                raise ValueError("Invalid value '%s' in mesh_params.elem_code."%code)
        
        # Seed the part.
        part = self.part_main
        if mesh_params.seed_size is None:
            raise ValueError('mesh_params.seed_size has not been specified.')
        part.seedPart(size=mesh_params.seed_size, deviationFactor=0.1, minSizeFactor=0.1)
        logger.debug('Seed generated.')
        
        # Set mesh controls and element type(s).
        if   self.is_shell:
            part.setMeshControls(regions=part.faces, elemShape=elem_shape)
            part.setElementType(regions=Region(faces=part.faces), elemTypes=elem_type_list)
        elif self.is_solid:
            part.setMeshControls(regions=part.cells, elemShape=elem_shape)
            part.setElementType(regions=Region(cells=part.cells), elemTypes=elem_type_list)
        else:
            raise RuntimeError('Both self.is_shell and self.is_solid are False.' +
                               ' This should not happen.')
        
        part.generateMesh()
        logger.debug('Mesh generated.')
        
        # Get text stats of element codes and types for logging.
        # This is a possible bottleneck. #TODO: test for 500K+ elements.
        elem_stats=dict()
        for elem in part.elements:
            elem_type_name = elem.type.name
            if elem_type_name in elem_stats.keys():
                elem_stats[elem_type_name] += 1
            else:
                elem_stats[elem_type_name] = 1
        elem_stats_str = elem_stats.__repr__().replace(': ',':').replace('{','').replace('}','')
        
        logger.info("Mesh generation completed with" +
                    " the following number of Abaqus/%s elements: %s."
         %(elem_library.name.capitalize(), elem_stats_str) )
    #
    
    def create_job(self, job_params):
        """Define a single step for the analysis. Assigns *self.job*.
        Current limitations are:
        
            + numDomains is set to numCpus.
            + numGPUs is set to 0.
            + User subroutine are not supported.
        
        Args:
            job_params(JobParams): Special namedtuple describing the job created for analysis.
                                   See class for full description of options.
        
        Raises:
            AbaqusException: Various exceptions raised by the Abaqus API.
        """
        # The abaqus module cannot be imported in the GUI code,
        # so only import it when running.
        from abaqus import mdb
        
        numCpus              = job_params.numCpus
        description          = job_params.description
        memoryPercent        = job_params.memoryPercent
        explicitPrecision    = job_params.explicitPrecision
        nodalOutputPrecision = job_params.nodalOutputPrecision
        
        # Validate and set job_params.explicitPrecision.
        if   job_params.explicitPrecision.upper() == 'SINGLE': explicitPrecision = SINGLE
        elif job_params.explicitPrecision.upper() == 'DOUBLE': explicitPrecision = DOUBLE
        else: raise ValueError('invalid value for job_params.explicitPrecision')
        
        # Validate and set job_params.nodalOutputPrecision.
        if   job_params.nodalOutputPrecision.upper() == 'SINGLE': nodalOutputPrecision = SINGLE
        elif job_params.nodalOutputPrecision.upper() == 'DOUBLE': nodalOutputPrecision = DOUBLE
        else: raise ValueError('invalid value for job_params.nodalOutputPrecision')
        
        self.job = mdb.Job(name=self.name, description=description,
                   model=self.model, type=ANALYSIS,
                   atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=memoryPercent,
                   memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                   explicitPrecision=explicitPrecision, nodalOutputPrecision=nodalOutputPrecision, echoPrint=OFF,
                   modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                   scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=numCpus,
                   numDomains=numCpus, numGPUs=0)
        logger.info('Created the job named %s.', self.job.name)
    #
    
    def submit_job(self):
        """Submit the job and wait for it to finish.
        Does not clean old files, but they should not be a problem.
        
        Raises:
            RuntimeError:    If the job has not been defined by :meth:`.create_job`.
            RuntimeError:    If the job does not complete successfuly.
            AbaqusException: Various exceptions raised by the Abaqus API.
        """
        
        if self.job is None:
            raise RuntimeError('The job has not been defined.' +
                               ' self.create_job() must be called first.')
        
        logger.info('Submitting the job...')
        self.job.submit()
        logger.info("Job '%s' submitted. Waiting for completion..."%self.job.name)
        self.job.waitForCompletion()
        if self.job.status == COMPLETED:
            logger.info('The job completed successfuly.')
            self.odb_path = os.path.join(os.getcwd(), self.job.name + '.odb')
        else:
            raise RuntimeError('The job was aborted or terminated.' +
                               ' Check message file for more information.')
    #
    
    def output_results(self, output_params):
        """Output the results of the analysis.
            
        Args:
            output_params(OutputParams): Special namedtuple describing the parameters
                                         for outputting the results of modeling and analysis.
                                         See class for full description of options.
        
        Raises:
            RuntimeError:    If the job has not been completed.
            ValueError:      If output_params.export_ribbon_width has not been
                             specified but STL or STP export is requested.
            AbaqusException: Various exceptions raised by the Abaqus API.
        """
        
        logger.debug('Exporting results.')
        
        if self.job.status != COMPLETED:
            raise RuntimeError('The job has not been completed.' +
                               ' Output is only possible after completion of analysis.')
        
        # Make a directory for storing results.
        # This is also done in main.main().
        # TODO: check.
        folder_path = helper.return_results_folder_path(self.name, output_params.result_folder_name)
        if os.path.isdir(folder_path):
            raise RuntimeError("'%s' already exists. Delete it before proceeding."%folder_path)
        else:
            os.makedirs(folder_path)
            logger.debug('Created the folder for analysis results: %s', folder_path)
        
        logger.debug('Opening the Odb.')
        odb = openOdb(path=self.odb_path)
        output_table = postprocessing.get_numerical_output(obj=self, odb=odb)
        postprocessing.write_single_numerical_output(output_table, self.name, folder_path)
        odb.close()
        
        if output_params.save_job_files: 
            #TODO: add function that uses shutil.move and shutil.copy2 in case of exception.
            os.rename( os.path.join(os.getcwd(), self.job.name + '.inp'),
                       os.path.join(folder_path, self.job.name + '.inp'))
            os.rename( os.path.join(os.getcwd(), self.job.name + '.msg'),
                       os.path.join(folder_path, self.job.name + '.msg'))
            #os.rename( os.path.join(os.getcwd(), self.job.name + '.log'), #investigate access error.
            #           os.path.join(folder_path, self.job.name + '.log'))
            sta_string = ''
            if os.path.isfile(os.path.join(os.getcwd(), self.job.name + '.sta')):
                sta_string = ', and sta.'
                os.rename( os.path.join(os.getcwd(), self.job.name + '.sta'),
                           os.path.join(folder_path, self.job.name + '.sta'))
        logger.debug('Saved job files to the folder: inp, msg, log%s.', sta_string)
        
        if output_params.save_odb:
            new_odb_path = os.path.join(folder_path, self.job.name + '.odb')
            os.rename(self.odb_path, new_odb_path)
            self.odb_path = new_odb_path
            logger.debug('Saved the Odb to the folder.')
        
        if output_params.export_stl or output_params.export_stp:
            # Create the exportable part. This operation is destructive
            # and the mdb should not be saved afterwards.
            #TODO FIXME: but it is. fix this. see if you can restore the originals.
            if output_params.export_ribbon_width is None:
                raise ValueError('output_params.export_ribbon_width must be specified for STL or STP export.')
            self.assemble_structure(for_3dprint=True, output_params=output_params, delete_all=True)
            
            if output_params.export_stl:
                postprocessing.export_part_stl(self, folder_path)
            
            if output_params.export_stp:
                self.part_3dprint.writeStepFile(
                    fileName=os.path.join(folder_path, self.name + '.stp'))
                logger.debug('Exported the part in the STP format.')
        
        if output_params.save_cae: # This is done last so the 3D model is also saved.
            # The abaqus module cannot be imported in the GUI code,
            # so only import it when running.
            from abaqus import mdb
            mdb.saveAs( os.path.join(folder_path, self.name) )
            logger.debug('Saved the Mdb to the folder.')
        
        self.results_folder_path = folder_path
        logger.debug('Exported the requested results.')
