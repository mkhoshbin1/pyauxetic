import os
from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import mainForm
import pyauxetic

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    object=mainForm.MainForm(toolset),
    buttonText        = 'PyAuxetic',
    messageId         = AFXMode.ID_ACTIVATE,
    icon              = None,
    kernelInitString  = '',#TODO: add some commands here.
    applicableModules = ALL,
    version           = pyauxetic.__version__,
    author            = pyauxetic.__author__,
    description       = pyauxetic.__description__,
    helpUrl           = pyauxetic.__docs__
)