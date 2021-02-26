# The prototypeApp framework was is from Abaqus,
# But was taken from the GitHub repository of
# Saullo G P Castro of TU Delft.
# https://github.com/saullocastro/programming
"""
This script will create the prototype application.
"""

from abaqusGui import *
import sys
from prototypeMainWindow import PrototypeMainWindow

# Initialize the application object.
#
app = AFXApp('ABAQUS/CAE', 'ABAQUS, Inc.')
app.init(sys.argv)

# Construct the main window.
#
PrototypeMainWindow(app)

# Create the application and run it.
#
app.create()
app.run()
