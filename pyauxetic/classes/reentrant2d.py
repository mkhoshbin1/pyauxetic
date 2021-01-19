from collections import namedtuple
import logging
from math import sin, cos, tan
import numpy as np

from abaqusConstants import *

from .. import helper

from .auxetic_structure import AuxeticStructure
from .auxetic_unit_cell import AuxeticUnitCell
from .auxetic_unit_cell_params import *

logger = logging.getLogger(__name__)

class Reentrant2DUnitCell(AuxeticUnitCell):
    """Class defining a 2D Re-Entrant unit cell.
    """
    #TODO: add link to page describing it.
    
    params_class_list = reentrant2d_ucp_list
    
    def __init__(self, model, params):
        """Initialize the object with the given parameters.
        
        Calls :meth:`.auxetic_unit_cell.AuxeticUnitCell.__init__()`
        which creates self.sketch and self.part_main.
        
        Args:
            model (Model):  Abaqus Model object in which the unit cell will be created.
            params:         Parameters describing the unit cell geometry.
                            It must be from a suitable class based on the list defined
                            in auxetic_unit_cell_params.reentrant2d_ucp_list.
        """
        #TODO: reference doc page for reentrant2d.
        
        # Make sure params is from a valid unit cell parameter class,
        # based on the list defined in auxetic_unit_cell_params.reentrant2d_ucp_list.
        if not isinstance(params, reentrant2d_ucp_list):
            raise ValueError('params must one of the unit cell parameter' +
                             ' classes defind for the Re-Entrant 2D unit cell.')
        
        self.name  = 'reentrant2d-%03i'%(params.id)
        super(Reentrant2DUnitCell, self).__init__(model, params)
        logger.info('Created Reentrant2DUnitCell object named %s.', self.name)
    
    def create_part_main(self):
        """Create the main part of the unit cell based on the sketch."""
        self._create_part_main_planar()
    
    def create_part_3dprint(self):
        """Create the part used for 3D printing based on the sketch."""
        self._create_part_3dprint_planar()
    
    def create_sketch(self):
        """Create the 2D sketch for the unit cell.
        A suitable creation method is called based on the
        unit cell parameters class passed to the unit cell object.
        """
        #TODO: doc. reference reentrant page.
        #TODO: The sketch is created based on the 2D reentrant unit cell proposed by 
        #TODO: Evans et al. in https://doi.org/10.1016/0956-7151(94)90145-7 .
        
        if   isinstance(self.params, Reentrant2DUcpFull):
            (sk, dg, dd) = create_sketch_reentrant2d_full(self.model, self.params,
                                                          self.sketch_name)
        elif isinstance(self.params, Reentrant2DUcpBox):
            (sk, dg, dd) = create_sketch_reentrant2d_box(self.model, self.params,
                                                         self.sketch_name)
        elif isinstance(self.params, Reentrant2DUcpSimple):
            (sk, dg, dd) = create_sketch_reentrant2d_simple(self.model, self.params,
                                                            self.sketch_name)
        else:
            raise TypeError('self.params is of incorrect type.' +
                            ' This is not supposed to happen.')
        self.sketch = sk
#

class Reentrant2DPlanarShellStructure(AuxeticStructure):
    """Class defining an auxetic structure based on the reentrant unit cell."""
    
    pretty_name     = 'Planar Shell Re-Entrant 2D'
    is_solid        = False
    is_shell        = True
    is_bulk         = False
    is_planar       = True
    is_tubular      = False
    unit_cell_class = Reentrant2DUnitCell
    
    def assemble_core_structure(self, structure_map=None, for_3dprint=False, delete_all=True):
        """Pattern the unit cells to form the core auxetic structure.
        
        It is called by :meth:`assemble_structure`, which is responsible for
        validating all input.
        
        Args:
            structure_map(:class:`np.array`):
                                A numpy array containing integer ids of unit cells
                                and how they are distributed in the structure.
                                It is defined by :meth:`assemble_structure`
                                regardless of its *pattern_params* argument.
            for_3dprint(bool):  If :obj:`True`, the structure will be a 3D part
                                suitable for export, Otherwise dimensionality will
                                be governed by the structure. Defaults to :obj:`False`.
            delete_all(bool):   If :obj:`True`, all useless parts will be deleted.
                                Defaults to :obj:`True`.
        
        Returns:
            A tuple containing the created core auxetic structure part and its instance.
        
        Raises:
            AbaqusException: Various exceptions raised by the Abaqus API.
                             Sometimes exceptions will be fatal.
        """
        
        logger.debug('Assembling the core structure.')
        assembly = self.model.rootAssembly
        unit_cell_bound_size = np.array(self.unit_cells[0].bound_size)
        
        used_ucs   = []
        instances  = []
        
        # Pattern the unit cells based on structure_map.
        logger.debug('Patterning the unit cells based on structure_map.')
        it = np.nditer(structure_map, order='C', flags=['multi_index', 'c_index'])
        for elem in it:
            if elem == 0:
                continue
            uc = self.get_unit_cell_by_id(id=elem)
            if for_3dprint:
                part = uc.part_3dprint
            else:
                part = uc.part_main
            instances.append(assembly.Instance(
                                    name=helper.return_instance_name(base_name=uc.name, suffix='-%03i'%it.index),
                                    part=part, autoOffset=OFF, dependent=ON) )
            helper.transfer_instance_to_zero(model=self.model, instance=instances[-1])
            try:
                vector = (it.multi_index[0], it.multi_index[1], it.multi_index[2]) * unit_cell_bound_size
            except IndexError:
                vector = (it.multi_index[0], it.multi_index[1], 0)*unit_cell_bound_size
            assembly.translate(instanceList=(instances[-1].name, ), vector = vector)
            # Will throw a warning for the very first instance because vector=(0,0,0).
            if not uc in used_ucs:
                used_ucs.append(uc)
        logger.debug('Patterned the unit cells based on structure_map.')
        
        # Merge the instances.
        logger.debug('Merging the patterned unit cells.')
        if delete_all:
            delete_flag       = DELETE
            delete_all_string = ' and deleted all unrelated parts'
        else:
            delete_flag       = SUPPRESS
            delete_all_string = ''
        core_instance = assembly.InstanceFromBooleanMerge(
                                    name='reentrant2d structure core',
                                    instances=instances,
                                    originalInstances=delete_flag, domain=GEOMETRY )
        logger.debug('Merged the patterned unit cells.')
        
        if delete_all:
            for uc in used_ucs:
                if for_3dprint:
                    del uc.part_3dprint
                else:
                    del uc.part_main
        
        if for_3dprint:
            self.part_3dprint          = core_instance.part
            self.part_3dprint_instance = core_instance
        else:
            self.part_main             = core_instance.part
            self.part_main_instance    = core_instance
            
            assembly.regenerate()
            assembly.clearGeometryCache()
        
        logger.debug('Assembled the core structure%s.', delete_all_string)
        return (core_instance.part, core_instance)
    #
    
    def assemble_structure(self, for_3dprint=False, output_params=None, delete_all=True):
        """Assemble one or more unit cells according to pattern parameters
        to create the auxetic structure.
        :meth:`.add_pattern_params` must be called before this.
        
        This is the implementation of
        :meth:`.auxetic_structure.AuxeticStructure.assemble_structure`
        for this class.
        
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
        #TODO: this has been somewhat decoupled. see if you can move this to parent after chiral.
        #TODO: further document. check entire function. add Raises.
        logger.info('Assembling the structure.')
        assembly = self.model.rootAssembly
        
        if max( len(assembly.instances), len(assembly.features)) != 0:
            assembly.deleteAllFeatures()
            logger.warning('The assembly was not empty. All features have been deleted.')
        assembly.DatumCsysByDefault(CARTESIAN)
        
        # All unit cells must have the same bound_size.
        logger.debug('Checking bound_size of all unit cells.')
        unit_cell_bound_size = self.unit_cells[0].bound_size
        for uc in self.unit_cells:
            if any( abs( np.array(uc.bound_size) - np.array(unit_cell_bound_size) ) > 1E-6 ):
                raise ValueError('All unit cells must have the same bound_size.')
        # bound_size and extrusion_depth are the same for all unit cells.
        structure_extrusion_depth = self.unit_cells[0].params.extrusion_depth
        unit_cell_bound_size = np.array(self.unit_cells[0].bound_size)
        logger.debug('All unit cells were of the same bound_size.')
        
        # Assemble the core auxetic structure.
        (core_part, core_instance) = \
            self.assemble_core_structure(self.structure_map, for_3dprint, delete_all)
        
        # Create the ribbon.
        logger.debug('Creating the ribbon.')
        # Width of the ribbon will be the maximum value of
        # vert_strut_thickness in all unit cells.
        ribbon_width = max(
            [uc.params.vert_strut_thickness for uc in self.unit_cells] )
        if self.loading_direction == 0:
            ribbon_size = (ribbon_width, self.num_cell_repeat[1] * unit_cell_bound_size[1] )
        else:
            ribbon_size = (self.num_cell_repeat[0] * unit_cell_bound_size[0], ribbon_width )
        
        if for_3dprint:
            if output_params is None:
                raise ValueError('for_3dprint is True, but output_params has not been specified.')
            ribbon_extrusion_depth = output_params.export_extrusion_depth
        else:
            ribbon_extrusion_depth = structure_extrusion_depth
        ribbon_part = helper.create_ribbon_part(model=self.model,
                                length_x=ribbon_size[0], length_y=ribbon_size[1],
                                is3d=for_3dprint, extrusion_depth=ribbon_extrusion_depth)
        logger.debug('Created the ribbon.')
        
        # Instantiate and position ribbon 1.
        ribbon_instance1 = assembly.Instance(name='ribbon_instance-1',
                                part=ribbon_part, autoOffset=OFF, dependent=ON)
        helper.transfer_instance_to_zero(model=self.model, instance=ribbon_instance1)
        ribbon_instance1_coords = helper.get_box_coords(object_list=ribbon_instance1)
        logger.debug('Positioned ribbon 1.')
        
        # Position the core auxetic structure.
        if self.loading_direction == 0:
            vector = (ribbon_instance1_coords[1][0],
                      ribbon_instance1_coords[0][1],
                      ribbon_instance1_coords[0][2])
        else:
            vector = (ribbon_instance1_coords[0][0],
                      ribbon_instance1_coords[1][1],
                      ribbon_instance1_coords[0][2])
        helper.transfer_instance_to_zero(model=self.model, instance=core_instance)
        assembly.translate(instanceList=(core_instance.name, ), vector=vector)
        logger.debug('Positioned the core structure.')
        
        # Instantiate and position ribbon 2.
        ribbon_instance2 = assembly.Instance(name='ribbon_instance-2',
                                part=ribbon_part, autoOffset=OFF, dependent=ON)
        ribbon_instance2_coords = helper.get_box_coords(object_list=ribbon_instance1)
        all_instance_coords = helper.get_box_coords(object_list=assembly.instances)
        if self.loading_direction == 0:
            ribbon2_vector = (
                       (all_instance_coords[1][0] - ribbon_instance2_coords[0][0]),
                       (all_instance_coords[0][1] - ribbon_instance2_coords[0][1]),
                       (all_instance_coords[0][2] - ribbon_instance2_coords[0][2]))
        else:
            ribbon2_vector = (
                       (all_instance_coords[0][0] - ribbon_instance2_coords[0][0]),
                       (all_instance_coords[1][1] - ribbon_instance2_coords[0][1]),
                       (all_instance_coords[0][2] - ribbon_instance2_coords[0][2]))
        assembly.translate(instanceList=(ribbon_instance2.name, ), vector=ribbon2_vector)
        logger.debug('Positioned ribbon 2.')
        
        # Merge the instances.
        logger.debug('Merging the instances.')
        #TODO: unused parts in gradient structures are not deleted.
        if delete_all:
            delete_flag = DELETE
            delete_all_string = ' and deleted all unrelated parts'
        else:
            delete_flag = SUPPRESS
            delete_all_string = ''
        
        if for_3dprint:
            name = 'print reentrant2d structure'
        else:
            name = 'main reentrant2d structure'
        merge_instance = assembly.InstanceFromBooleanMerge(name=name,
                                    instances=assembly.instances.values(),
                                    originalInstances=delete_flag, domain=GEOMETRY )
        logger.debug('Merged the instances.')
        
        if delete_all:
            self.model.parts.__delitem__(core_part.name)
            self.model.parts.__delitem__(ribbon_part.name)
        
        if for_3dprint:
            self.part_3dprint          = merge_instance.part
            self.part_3dprint_instance = merge_instance
        else:
            self.part_main          = merge_instance.part
            self.part_main_instance = merge_instance
        assembly.regenerate()
        assembly.clearGeometryCache()
        logger.info('Assembled the structure%s.', delete_all_string)
#

def create_sketch_reentrant2d_full(model, params, sketch_name):
    """Create the 2D sketch of a reentrant2d unit cell using
    the full set of unit cell parameters.
    
    Args:
        model (Model):               Abaqus Model object in which the unit cell
                                     will be created.
        params (Reentrant2DUcpFull): Parameters describing the unit cell geometry.
                                     See #TODO for details.
        sketch_name (str):           Name assigned to the skecth.
    """
    if not isinstance(params, Reentrant2DUcpFull):
        raise ValueError('params must be a Reentrant2DUcpFull.')
    
    if params.diag_strut_angle >= 90:
        raise ValueError('params.diag_strut_angle must be less than 90 degrees.')
    
    logger.debug('Creating sketch.')
    # The sketch is mirrored twice. Therefore some parametes need to be halved.
    tail_strut_length    = params.tail_strut_length
    tail_strut_thickness = params.tail_strut_thickness / 2.0
    diag_strut_length    = params.diag_strut_length
    diag_strut_thickness = params.diag_strut_thickness
    vert_strut_length    = params.vert_strut_length / 2.0
    vert_strut_thickness = params.vert_strut_thickness
    # The input angle is in degrees but the function uses radians internally.
    diag_strut_angle     = np.deg2rad( params.diag_strut_angle )
    
    # Create the sketch.
    sk = model.ConstrainedSketch(name=sketch_name, sheetSize=3*vert_strut_length)
    
    # Create dictionaries for lines and dimensions.
    dd = dict()
    dg = dict()
    
    # Define the first point in the sketch.
    (prev_point) = (0, 0)
    
    # Define the rest of the points.
    (prev_point,dg['tail_hline']) = helper.draw_line(sk, prev_point, point2=(-tail_strut_thickness, 0) )
    v = dg['tail_hline'].getVertices()
    dd['tail_hline_fixed']  = sk.FixedConstraint(entity=v[0])
    dd['tail_hline_horz']   = sk.HorizontalConstraint(dg['tail_hline'])
    dd['tail_hline_length'] = sk.ObliqueDimension(vertex1=v[0], vertex2=v[1],
                                    textPoint=(-tail_strut_thickness/2.0, -0.5),
                                    value=tail_strut_thickness)
    
    (prev_point,dg['tail_vline']) = helper.draw_line(sk, prev_point,
                                           point2=(-tail_strut_thickness, tail_strut_length) )
    v = dg['tail_vline'].getVertices()
    dd['tail_vline_vert']   = sk.VerticalConstraint(dg['tail_vline'])
    dd['tail_vline_length'] = sk.ObliqueDimension(vertex1=v[0], vertex2=v[1],
                                    textPoint=(0, tail_strut_length/2.0),
                                    value=tail_strut_length)
    
    (prev_point,dg['diag_line1'])      = helper.draw_line(sk, prev_point,
                                             point2=(prev_point[0] - diag_strut_length * sin(diag_strut_angle),
                                                     prev_point[1] - diag_strut_length * cos(diag_strut_angle) ))
    
    (prev_point,dg['straight_vline1']) = helper.draw_line(sk, prev_point,
                                             point2=(prev_point[0],
                                                     prev_point[1] + vert_strut_length ) )
    v = dg['straight_vline1'].getVertices()
    dd['straight_vline1_vert']   = sk.VerticalConstraint(dg['straight_vline1'])
    dd['straight_vline1_length'] = sk.ObliqueDimension(vertex1=v[0], vertex2=v[1],
                                       textPoint=(1.1*v[0].coords[0], vert_strut_length/2.0),
                                       value=vert_strut_length)
    
    # This line must be created as a construction line,
    # otherwise the mirrored geometry will self intersect.
    second_point = (prev_point[0] + vert_strut_thickness, prev_point[1] )
    dg['h_mirror_line'] = sk.ConstructionLine(point1=prev_point, point2=second_point)
    dd['h_mirror_line_fixed'] = sk.FixedConstraint(entity=dg['h_mirror_line'])
    prev_point = second_point
    
    (prev_point,dg['straight_vline2']) = helper.draw_line(sk, prev_point,
                           point2=(prev_point[0],
                                   prev_point[1] - vert_strut_length
                                    +  diag_strut_thickness / sin(diag_strut_angle)
                                    +  vert_strut_thickness / tan(diag_strut_angle) ) )
    dd['vline1_vline2_parallel'] = sk.ParallelConstraint(
                                       dg['straight_vline1'], dg['straight_vline2'])
    dd['vline1_vline2_dist']     = sk.DistanceDimension(
                                       dg['straight_vline1'], dg['straight_vline2'],
                                       textPoint=(dg['straight_vline1'].getVertices()[0].coords[0]+vert_strut_thickness, vert_strut_length),
                                       value=vert_strut_thickness)
    dd['vline1_h_mirror_line_coinc'] = sk.CoincidentConstraint(
                                           dg['h_mirror_line'],
                                           dg['straight_vline1'].getVertices()[1])
    dd['vline2_h_mirror_line_coinc'] = sk.CoincidentConstraint(
                                           dg['h_mirror_line'],
                                           dg['straight_vline2'].getVertices()[0])
    
    (prev_point,dg['diag_line2']) = helper.draw_line(sk, prev_point,
                                        point2=(prev_point[0] + diag_strut_length*sin(diag_strut_angle),
                                                prev_point[1] + diag_strut_length*cos(diag_strut_angle)))
    
    v = dg['diag_line2'].getVertices()
    dd['diag_line1_diag_line2_parallel']   = sk.ParallelConstraint(
                                                 dg['diag_line1'], dg['diag_line2'])
    dd['diag_line1_diag_line2_dist']       = sk.DistanceDimension(
                                                 dg['diag_line1'], dg['diag_line2'],
                                                 textPoint=(v[0].coords[0], 0.75*vert_strut_length),
                                                 value=diag_strut_thickness)
    dd['diag_line2_straight_vline2_angle'] = sk.AngularDimension(
                                                 line1=dg['diag_line2'], line2=dg['straight_vline2'],
                                                 textPoint=(0.6*vert_strut_length, 0.6*vert_strut_length),
                                                 value= 180 - np.rad2deg(diag_strut_angle) ) # Because of line direction.
    
    dg['v_mirror_line'] = sk.ConstructionLine(point1=(0,0), point2=(0,1) )
    dd['v_mirror_line_fixed'] = sk.FixedConstraint(entity=dg['v_mirror_line'])
    dd['v_mirror_line_diag_line2_coinc'] = sk.CoincidentConstraint(
                                               dg['v_mirror_line'],
                                               dg['diag_line2'].getVertices()[1])
    
    # Mirror the sketch horizontally.
    sk.copyMirror(mirrorLine=dg['h_mirror_line'], objectList=helper.find_regular_geometries(sketch=sk))
    
    # Mirror the sketch vertically.
    sk.copyMirror(mirrorLine=dg['v_mirror_line'], objectList=helper.find_regular_geometries(sketch=sk))
    logger.debug('Created sketch %s.', sk.name)
    
    # Validate the sketch. Does not cover all edge cases.
    diag_line2_y    = dg['diag_line2'].getVertices()[1].coords[1]
    h_mirror_line_y = dg['h_mirror_line'].pointOn[1]
    if diag_line2_y > h_mirror_line_y:
    # Vertices at the center of the unit cell pass each other,
    # meaning that the geometry self-intersects and is invalid.
        raise RuntimeError('The geometry is invalid because' +
                           ' vertices at the center of the unit cell'    +
                           ' pass each other, meaning that the geometry' +
                           ' is self-intersecting.' )
    
    return (sk, dg, dd)
#

def create_sketch_reentrant2d_box(model, params, sketch_name):
    """Create the 2D sketch of a reentrant2d unit cell using
    the 'bounding box' set of unit cell parameters.
    
    Args:
        model (Model):              Abaqus Model object in which the unit cell
                                    will be created.
        params (Reentrant2DUcpBox): Parameters describing the unit cell geometry.
                                    See #TODO for details.
        sketch_name (str):          Name assigned to the skecth.
    """
    
    if not isinstance(params, Reentrant2DUcpBox):
        raise ValueError('params must be a Reentrant2DUcpBox.')
    
    horz_bounding_box    = params.horz_bounding_box / 2.0
    vert_bounding_box    = params.vert_bounding_box / 2.0
    vert_strut_thickness = params.vert_strut_thickness
    diag_strut_angle     = params.diag_strut_angle
    diag_strut_thickness = params.diag_strut_thickness
    tail_strut_thickness = params.vert_strut_thickness
    
    diag_strut_angle_rad      = np.deg2rad(diag_strut_angle)
    tail_strut_thickness_half = tail_strut_thickness / 2.0
    diag_strut_length = (horz_bounding_box - tail_strut_thickness_half) / sin(diag_strut_angle_rad)
    vert_strut_length_half = ( vert_bounding_box
                          + (diag_strut_length         * cos(diag_strut_angle_rad) )
                          + (diag_strut_thickness      / sin(diag_strut_angle_rad) )
                          + (tail_strut_thickness_half / tan(diag_strut_angle_rad) ) ) / 2.0
    vert_strut_length = vert_strut_length_half * 2.0
    tail_strut_length = ( vert_strut_length_half
                          - (diag_strut_thickness      / sin(diag_strut_angle_rad) )
                          - (tail_strut_thickness_half / tan(diag_strut_angle_rad) ) )
    
    ## These dimensions only work if diag_line1 ends higher than tail_hline.
    if tail_strut_length < ( diag_strut_length * cos(diag_strut_angle_rad) ):
        raise RuntimeError('The formulated dimensions are incorrect for these inputs.')
    
    
    # Create the Reentrant2DUcpFull object.
    new_params = Reentrant2DUcpFull(params.id, params.extrusion_depth,
                                    tail_strut_length, tail_strut_thickness,
                                    diag_strut_length, diag_strut_thickness,
                                    diag_strut_angle,
                                    vert_strut_length, vert_strut_thickness )
    
    # Create the sketch.
    (sk, dg, dd) = create_sketch_reentrant2d_full(model, new_params, sketch_name)
    
    # Validate the sketch.
    dd['tail_centerline_length'] = sk.VerticalDimension(
                                       dg['tail_hline'].getVertices()[0],
                                       dg['diag_line2'].getVertices()[1],
                                       textPoint=(0, 1.5*tail_strut_length),
                                       reference=True)
    if abs(dd['straight_vline1_length'].value - dd['tail_centerline_length'].value) > 1E-6:
        raise RuntimeError('The geometry is invalid because' +
                           ' length of straight_vline1 and'  +
                           ' tail_centerline are not equal.' )
    
    return (sk, dg, dd)
#

def create_sketch_reentrant2d_simple(model, params, sketch_name):
    """Create the 2D sketch of a reentrant2d unit cell using
    the simplified set of unit cell parameters.
    
    Args:
        model (Model):                 Abaqus Model object in which the unit cell
                                       will be created.
        params (Reentrant2DUcpSimple): Parameters describing the unit cell geometry.
                                       See #TODO for details.
        sketch_name (str):             Name assigned to the skecth.
    """
    
    if not isinstance(params, Reentrant2DUcpSimple):
        raise ValueError('params must be a Reentrant2DUcpSimple.')
    
    # Manipulate parameters so create_sketch_reentrant2d_full() can be called.
    # Note that mirroring will be considered in create_sketch_reentrant2d_full(),
    # but sin() and tan() functions require a deg2rad conversion.
    vert_strut_length    = params.vert_strut_length
    vert_strut_thickness = params.vert_strut_thickness
    diag_strut_length    = vert_strut_length/1.5  # Dummy dimension. Determined by constraints.
    diag_strut_thickness = params.diag_strut_thickness
    diag_strut_angle     = params.diag_strut_angle
    tail_strut_thickness = params.vert_strut_thickness
    tail_strut_length    = ( ( vert_strut_length / 2.0 )
                             -  diag_strut_thickness      / sin(np.deg2rad(diag_strut_angle))
                             - (tail_strut_thickness/2.0) / tan(np.deg2rad(diag_strut_angle)) )
    
    # Create the Reentrant2DUcpFull object.
    new_params = Reentrant2DUcpFull(params.id, params.extrusion_depth,
                                    tail_strut_length, tail_strut_thickness,
                                    diag_strut_length, diag_strut_thickness,
                                    diag_strut_angle,
                                    vert_strut_length, vert_strut_thickness )
    return create_sketch_reentrant2d_full(model, new_params, sketch_name)
#