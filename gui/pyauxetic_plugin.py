from abaqusGui import getAFXApp, Activator, AFXMode
from abaqusConstants import ALL
import os
import mainForm

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    object=mainForm.MainForm(toolset),
    buttonText='PyAuxetic',
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,          #TODO
    kernelInitString='',
    applicableModules=ALL,
    version='N/A',      #TODO
    author='The PyAuxetic Team',
    description='N/A',  #TODO
    helpUrl='N/A'       #TODO
)
