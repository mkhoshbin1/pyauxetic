Installation and Usage
======================

The software can be used as both a plugin to the Abaqus software or as a library for developing Abaqus scripts. Installation for either mode is very straightforward.


Installing as a Plugin
----------------------

To install the software as a plugin to Abaqus, follow these steps:
  + Obtain a copy of the software from Github. You can either clone/fork the repository or download as a zip.
  + Copy the software to you Abaqus *plugins* folder. This is generally in ``C:\SIMULIA\CAE\plugins\VERSION``, where *VERSION* refers to abaqus version, e.g. *2021*.
  
  + Restart Abaqus.
  
  + The plugin can now be seen in the *plugins* menu (:numref:`install-menu`).
      
      .. figure:: ../images/install-menu.png
          :name: install-menu
          :scale: 100%
          :align: center
          :alt: Installed plugin in the plugins menu.
          
          Installed plugin in the plugins menu.

The plugin can now be opened and used. Throughout the manual, there are sections describing how to use the plugin GUI.


Installing as a Library
-----------------------

The software has an API which can be used for writing Python scripts for Abaqus. In order to import the software as a library, simply add the path to the plugin to the search path in your script:

.. code-block:: python2
  
  import sys
  sys.path.append(r'C:\SIMULIA\CAE\plugins\2017\pyauxetic')

Now you can import the library using ``import pyauxetic``. Throughout the manual, there are sections describing how to use the API to define objects about various parts of the modeling and analysis process. These are then passed to the main API functions. Refer to :ref:`examples` for more information.


Updating the Software
---------------------

In order to update the software, simply delete the old files and replace them with the new copy of the software.