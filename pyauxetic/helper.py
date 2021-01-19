""" Helper functions used in the PyAuxetic library for various operations."""

from collections import Iterable
import os, logging

from abaqusConstants import *
from part import EdgeArray, VertexArray

logger = logging.getLogger(__name__)

def create_ribbon_part(model, length_x, length_y, is3d, extrusion_depth):
    """Create a rectangular ribbon part.
    
    Args:
        model(Model):           Model object in which the part will be created.
        length_x(float):        Length of the part in the x (1st) direction
        length_y(float):        Length of the part in the y (2nd) direction
        is3d(bool):             If :obj:`True`, the part is extruded.
        extrusion_depth(float): Extrusion depth used if *is3d* is :obj:`True`.
    
    Returns:
        The created part object.
    """
    #TODO: validate input.
    sk = model.ConstrainedSketch(name='ribbon', sheetSize=2*max(length_x,length_y))
    sk.rectangle(point1=(0.0, 0.0), point2=(length_x, length_y))
    
    if is3d:
        ribbon_part = model.Part(name='ribbon_3d', dimensionality=THREE_D,
                                 type=DEFORMABLE_BODY)
        ribbon_part.BaseSolidExtrude(sketch=sk, depth=extrusion_depth)
        logger.debug('Created the 3D ribbon part.')
        
    else:
        ribbon_part = model.Part(name='ribbon_2d', dimensionality=TWO_D_PLANAR,
                                 type=DEFORMABLE_BODY)
        ribbon_part.BaseShell(sketch=sk)
        logger.debug('Created the 2D ribbon part.')
    
    return ribbon_part
#

def draw_line(sketch, point1, point2):
    """Draw a line using two points and return the second point.
    
    Output of this function is intended to be used as point1 for
    future uses.
    
    Args:
        sketch(ConstrainedSketch): The sketch in which the line is drawn.
        point1(tuple):             2D Cartesian coordinates of the first point.
        point2(tuple):             2D Cartesian coordinates of the second point.
    
    Returns:
        A tuple in the form of *( (x,y), lineObj )*
        containing 2D Cartesian coordinates of the second point
        and the created line object.
    """
    
    line = sketch.Line(point1=point1, point2=point2)
    return (point2, line)
#

def find_edges_from_coords(part, coord, value):
    """Find edges of a part that exist on a certain value along a given coordinate axis.
    
    Args:
        part(Part):   The part in question.
        coord(int):   The coordinate axis used for the operation. Valid values are 1, 2, or 3.
        value(float): Value of the coordinate specified in *coord*.
    
    Returns:
        An EdgeArray object containing one or more edges
        which have a point on the given coordinates.
    
    Raises:
        RuntimeError: If no edges are found.
    """
    #TODO: this is 2D. thick of 3D.
    found_edges = []
    for e in part.edges:
        if abs(e.pointOn[0][coord] - value) < 1E-6:
            found_edges.append( e )
    if len(found_edges) == 0:
        raise RuntimeError('No edges were found')
    
    return EdgeArray(found_edges)
#

def find_vertices_from_coords(part, coord, value):
    """Find vertices of a part that exist on a certain value along a given coordinate axis.
    
    Args:
        part(Part):   The part in question.
        coord(int):   The coordinate axis used for the operation. Valid values are 1, 2, or 3.
        value(float): Value of the coordinate specified in *coord*.
    
    Returns:
        A VertexArray object containing one or more vertices
        which have a point on the given coordinates.
    
    Raises:
        RuntimeError: If no vertices are found.
    """
    #TODO: this is 2D. thick of 3D.
    found_vertices = []
    for v in part.vertices:
        if abs(v.pointOn[0][coord] - value) < 1E-6:
            found_vertices.append( v )
    if len(found_vertices) == 0:
        raise RuntimeError('No vertices were found')
    
    return VertexArray(found_vertices)
#

def find_vertices_from_coords_minmax(part, coord, value):
    """Find the first and last vertices of a part that exist
    on a certain value along a given coordinate axis.
    
    Args:
        part(Part):   The part in question.
        coord(int):   The coordinate axis used for the operation. Valid values are 1, 2, or 3.
        value(float): Value of the coordinate specified in *coord*.
    
    Returns:
        A Tuple of two VertexArray objects for the first and last vertices.
    
    Raises:
        RuntimeError: If no vertices are found.
    """
    #TODO: this is 2D. thick of 3D.
    if coord == 0:
        other_coord = 1
    elif coord == 1:
        other_coord = 0
    elif coord == 3:
        raise NotImplementedError("This function has not been implemented for coord == 'z'.")
    else:
        raise ValueError("coord must be equal to 0, 1, or 2.")
    
    all_found_vertices = find_vertices_from_coords(part, coord, value)
    
    min_vertex = all_found_vertices[0]
    max_vertex = all_found_vertices[0]
    
    for v in all_found_vertices:
        if (v.pointOn[0][other_coord]) < (min_vertex.pointOn[0][other_coord]):
            min_vertex = v
        if (v.pointOn[0][other_coord]) > (max_vertex.pointOn[0][other_coord]):
            max_vertex = v
    
    return ( VertexArray((min_vertex,)), VertexArray((max_vertex,)) )
#

def find_regular_geometries(sketch):
    """Searches the sketch and returns a list of *REGULAR* geometries.
    
    Geometries in an Abaqus sketch are either *REGULAR* or *CONSTRUCTION*, 
    the latter of which is used for defining relationships.
    This function is intended to filter out construction lines
    defined for mirroring parts.
    
    Args:
        sketch(ConstrainedSketch): The sketch in which the line is drawn.
    
    Returns:
        A list of ConstrainedSketchGeometry objects which are *REGULAR*.
    """
    
    geom_list = []
    for geom in sketch.geometry.values():
        if geom.type == REGULAR:
            geom_list.append( geom )
    return geom_list
#

def get_part_box_size(part):
    """Calculates size of a part's rectangular boundary.
    
    Args:
        part(Part): The part which is queried.
    
    Returns:
        A tuple in the form of (x,y,z) containing size of
        the part's rectangular boundary in the Cartesian coordinate system.
    """
    
    if str(type(part)) != "<type 'Part'>":
        raise ValueError('part must be a Part object.')
    
    bb = part.queryGeometry(printResults=False)['boundingBox']
    box_size = [bb[1][0] - bb[0][0],
                bb[1][1] - bb[0][1],
                bb[1][2] - bb[0][2] ]
    # Fix the small amount of numerical inaccuracy.
    for i in range(len(box_size)):
        if box_size[i] < 1e-8:
            box_size[i] = 0
    return tuple(box_size)
#

def get_box_coords(object_list):
    """Find the minimum and maximum Cartesian coordinates for a Part or PartInstance.
    
    Args:
        object_list(Part/PartInstance/Repository/tuple):
               The part(s) or instance(s) which are queried.
    
    Returns:
        A tuple of tuples in the form of
        *( (min_x, min_y, min_z), (max_x, max_y, max_z) )*
        the minimum and maximum Cartesian coordinates of the parts.
    """
    
    # Check type. The base classes are inaccessable, so don't improve.
    if isinstance(object_list, Iterable):
        pass
    elif (str(type(object_list)) == "<type 'PartInstance'>"
          or str(type(object_list)) == "<type 'Part'>" ):
        object_list = (object_list,)
    elif str(type(object_list)) == "<type 'Repository'>":
        object_list = object_list.values()
    else:
        raise ValueError('object_list must be a Part, PartInstance, '
                         + 'Repository, or an iterable containing Part or PartInstance objects.')
    
    min_coords = 3*[float('inf')]
    max_coords = 3*[float('-inf')]
    for instance in object_list:
        for vertice in instance.vertices:
            point = vertice.pointOn[0]
            min_coords[0] = min( point[0], min_coords[0] )  # min_x
            min_coords[1] = min( point[1], min_coords[1] )  # min_y
            min_coords[2] = min( point[2], min_coords[2] )  # min_z
            max_coords[0] = max( point[0], max_coords[0] )  # max_x
            max_coords[1] = max( point[1], max_coords[1] )  # max_y
            max_coords[2] = max( point[2], max_coords[2] )  # max_z
    return (min_coords, max_coords)
#

def return_results_folder_path(structure_name, root_folder_name=None):
    """Return a unified path for storing results of analysis of a structure.
    
    Args:
        structure_name(str):   Name of the structure for which the folder is created.
        root_folder_name(str): Name for the root folder. Defaults to None.
    
    Returns:
        Absolute path for the results folder.
    """
    #TODO: validate the string. size, start with letter.
    if root_folder_name is None:
        return os.path.join(os.getcwd(), structure_name)
    else:
        return os.path.join(os.getcwd(), root_folder_name, structure_name)
#

def return_sketch_name(base_name):
    """Return a unified name for a sketch based on a base name.
    
    Args:
        base_name(str): Base name to which a suffix is added.
    
    Returns:
        A suitable name for an Abaqus sketch.
    """
    #TODO: validate the string. size, start with letter.
    return (base_name + '-sketch')
#

def return_unit_cell_name_main(base_name):
    """Return the name of a main part based on a unit cell.
    
    Args:
        base_name(str): Base name to which a suffix is added.
    
    Returns:
        A suitable name for an Abaqus part.
    """
    #TODO: validate the string. size, start with letter.
    return (base_name + '-main')
#

def return_unit_cell_name_3dprint(base_name):
    """Return the name of a 3D printing part based on a unit cell.
    Use this function only for naming parts that are used for 3D printing.
    
    Args:
        base_name(str): Base name to which a suffix is added.
    
    Returns:
        A suitable name for an Abaqus part.
    """
    #TODO: validate the string. size, start with letter.
    return (base_name + '-3dprint')
#

def return_instance_name(base_name, suffix=''):
    """Return the name of an instance based on a unit cell.
    
    Args:
        base_name(str): Base name to which a suffix is added.
                        Defaults to an empty string.
    
    Returns:
        A suitable name for an Abaqus instance.
    """
    
    return (base_name + '-ins'+suffix)
#

def transfer_instance_to_zero(model, instance):
    """Transfer a PartInstance so it's vertex with minimum coordinates
    is at global *(0,0,0)*.
    
    Args:
        model(Model):           Model object in which the instance is defined.
        instance(PartInstance): The instance to be moved.
    """
    #TODO: doc
    instance_coords = get_box_coords(object_list=instance)
    if instance_coords[0] != [0,0,0]:
        model.rootAssembly.translate(instanceList=(instance.name, ),
                           vector= [-i for i in instance_coords[0]] )
#