from abc import ABCMeta, abstractmethod
import logging

from abaqusConstants import *
from abaqusExceptions import AbaqusException

from .. import helper

logger = logging.getLogger(__name__)

class AuxeticUnitCell:
    """Abstract base class for defining an auxetic unit cell.
    It defines the core behavior and must be subclassed for different unit cells.
    """
    __metaclass__ = ABCMeta
    def __init__(self, model, params):
        """Initialize the unit cell with the given parameters.
        
        Child classes must first define self.name and afterwards call this
        function using :code:`super(ChildClass, self).__init__(params)`.
        This function then creates the self.sketch and self.part_main.
        
        Logging is done in the child classes.
        
        Args:
            model (Model):  Abaqus Model object in which the unit cell will be created.
            params:         Parameters describing the unit cell geometry.
                            See child classes for valid object types.
        """
        
        self.model = model
        if params.id < 1:
            raise ValueError('id must be greater or equal to 1.')
        self.id = params.id
        self.sketch_name       = helper.return_sketch_name(self.name)
        self.part_main_name    = helper.return_unit_cell_name_main(self.name)
        self.part_3dprint_name = helper.return_unit_cell_name_3dprint(self.name)
        self.params            = params
        self._part_main        = None
        self._part_3dprint     = None
        self.create_sketch()
        # It it not necessary to make the part here,
        # but this ensures that the sketch is valid.
        self.create_part_main()
        self.bound_size = helper.get_part_box_size(part=self.part_main)
    
    @property
    def part_3dprint(self):
        """Abaqus Part object suitable for 3D export.
        If the part does not exist, it will be created.
        """
        if self._part_3dprint is None:
            logger.debug('Attempted to access nonexistent part_3dprint of unit cell %s.' +
                         ' It has been created.', self.name)
            self.create_part_3dprint()
        return self._part_3dprint
    
    @part_3dprint.deleter
    def part_3dprint(self):
        if self._part_3dprint is None:
            raise RuntimeError('Tried to delete part_3dprint but it does not exist.')
        del self.model.parts[self._part_3dprint.name]
        self._part_3dprint = None
        logger.debug('Deleted part_3dprint of unit cell %s.', self.name)
    
    @property
    def part_main(self):
        """The main Abaqus Part of the structure which can be planar or 3D.
        If the part does not exist, it will be created.
        """
        if self._part_main is None:
            logger.debug('Attempted to access nonexistent part_main of unit cell %s.' +
                         ' It has been created.', self.name)
            self.create_part_main()
        return self._part_main
    
    @part_main.deleter
    def part_main(self):
        if self._part_main is None:
            raise RuntimeError('Tried to delete part_main but it does not exist.')
        del self.model.parts[self._part_main.name]
        logger.debug('Deleted part_main of unit cell %s.', self.name)
        self._part_main = None
    
    @abstractmethod
    def create_sketch(self):
        """Create the 2D sketch for the unit cell.
        See child classes for implementation.
        """
        pass
    
    @abstractmethod
    def create_part_main(self):
        """Create the main part of the unit cell based on the sketch.
        See child classes for implementation.
        """
        pass
    
    @abstractmethod
    def create_part_3dprint(self):
        """Create the part used for 3D printng based on the sketch.
        See child classes for implementation.
        """
        pass
    
    def _create_part_main_planar(self):
        """Create the main part of a planar unit cell based on its sketch.
        
        This is a private function and is exposed
        through `create_part_main` function of the child classes.
        """
        #TODO: add try except for invalid sketches. maybe add to parent.
        self._part_main = self.model.Part(name=self.part_main_name,
                                    dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        try:
            self._part_main.BaseShell(sketch=self.sketch)
        except AbaqusException:
            raise RuntimeError('Part creation failed. Make sure the sketch is closed.')
        logger.debug('Created 2D planar main part %s from sketch %s.',
                     self.part_main_name, self.sketch.name)
    
    def _create_part_3dprint_planar(self):
        """Create the part used for 3D printng by extruding its sketch
        based on a planar unit cell's *extrusion_depth* parameter.
        
        This is a private function and is exposed
        through `create_part_3dprint` function of the child classes.
        """
        #TODO: see if you can add this to sphynx.
        #TODO: add try except for invalid sketches.
        if self.params.extrusion_depth is None:
            raise ValueError('extrusion_depth has not been defined for this unit cell.' +
                             ' This should never happen.')
        self._part_3dprint = self.model.Part(name=self.part_3dprint_name,
                                    dimensionality=THREE_D, type=DEFORMABLE_BODY)
        try:
            self._part_3dprint.BaseSolidExtrude(sketch=self.sketch, depth=self.params.extrusion_depth)
        except AbaqusException:
            raise RuntimeError('Part creation failed. Make sure the sketch is closed.')
        logger.debug('Created extruded planar part %s from sketch %s.',
                     self.part_3dprint_name, self.sketch.name)