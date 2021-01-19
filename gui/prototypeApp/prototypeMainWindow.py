# The prototypeApp framework was is taken from
# https://github.com/saullocastro/programming/archive/master.zip
# by Saullo G P Castro of TU Delft.
"""
This script will create the prototype application main window.
"""

from abaqusGui import *
from sessionGui import *
from canvasGui import CanvasToolsetGui
from viewManipGui import ViewManipToolsetGui
from prototypeToolsetGui import PrototypeToolsetGui


###########################################################################
# Class definition
###########################################################################

class PrototypeMainWindow(AFXMainWindow):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, app, windowTitle=''):

        # Construct the GUI infrastructure.
        #
        AFXMainWindow.__init__(self, app, windowTitle)
        
        # Register the "persistent" toolsets.
        #
        self.registerToolset(FileToolsetGui(), GUI_IN_MENUBAR|GUI_IN_TOOLBAR)
        self.registerToolset(ModelToolsetGui(), GUI_IN_MENUBAR)
        self.registerToolset(CanvasToolsetGui(), GUI_IN_MENUBAR)
        self.registerToolset(ViewManipToolsetGui(), GUI_IN_MENUBAR|GUI_IN_TOOLBAR)
        self.registerToolset(PrototypeToolsetGui(), GUI_IN_MENUBAR|GUI_IN_TOOLBOX)

        self.registerHelpToolset(HelpToolsetGui(), GUI_IN_MENUBAR|GUI_IN_TOOLBAR)

        # Register modules.
        #
        self.registerModule('Part',          'Part')
        self.registerModule('Property',      'Property')
        self.registerModule('Assembly',      'Assembly')
        self.registerModule('Step',          'Step')
        self.registerModule('Interaction',   'Interaction')
        self.registerModule('Load',          'Load')
        self.registerModule('Mesh',          'Mesh')
        self.registerModule('Job',           'Job')
        self.registerModule('Visualization', 'Visualization')
        self.registerModule('Sketch',        'Sketch')
