# The prototypeApp framework was is taken from
# https://github.com/saullocastro/programming/archive/master.zip
# by Saullo G P Castro of TU Delft.
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
