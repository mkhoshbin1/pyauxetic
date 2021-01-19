# The prototypeApp framework was is taken from
# https://github.com/saullocastro/programming/archive/master.zip
# by Saullo G P Castro of TU Delft.
from abaqusGui import *
from appIcons import *

import os
sys.path.append(os.path.split( os.getcwd() )[0])
import mainForm

###########################################################################
# Class definition
###########################################################################

class PrototypeToolsetGui(AFXToolsetGui):

    [
        ID_FORM,
    ] = range(AFXToolsetGui.ID_LAST, AFXToolsetGui.ID_LAST+1)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):

        # Construct the base class.
        #
        AFXToolsetGui.__init__(self, 'Test Toolset')
        
        FXMAPFUNC(self, SEL_COMMAND, self.ID_FORM, PrototypeToolsetGui.onCmdForm)
      
        self.form = mainForm.MainForm(self)
        
        # Toolbox buttons
        #
        group = AFXToolboxGroup(self)
        formIcon = FXXPMIcon(getAFXApp(), formIconData)
        AFXToolButton(group, '\tReload Form', formIcon, self,
            self.ID_FORM)
        dialogIcon = FXXPMIcon(getAFXApp(), dialogIconData)
        self.dialogBtn = AFXToolButton(group, '\tPost Dialog', dialogIcon, self.form, 
            AFXMode.ID_ACTIVATE)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCmdForm(self, sender, sel, ptr):

        # Reload the form module and reconstruct the form so that any
        # changes to that module are updated.
        #
        reload(mainForm)
        self.form = mainForm.MainForm(self)
        self.dialogBtn.setTarget(self.form)
        getAFXApp().getAFXMainWindow().writeToMessageArea(
            'The form has been reloaded.')
        
        return 1