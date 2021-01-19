Batch Modeling
==============

Batch modeling refers to running a series of modeling and analysis operations in consecutive order. Afterwards, output data are compiled into a separate report. Currently, this operation in only available for uniform structures.

Batch Modeling using the GUI
----------------------------

Definition of a batch modeling job is similar to a single analysis discussed in :doc:`defining-unit-cells`. After *Modeling Mode* is set to *Uniform (Batch)*, the only differences are:

  + Instead of a *structure name*, a *structure prefix* is input. The number *unit cell ID* (see below) will then be appended to the prefix to form *structure name*.
  + Unit cell parameters pop-up window shows a table for entering the parameters. This is discussed in :doc:`defining-unit-cells`. Here, each row is used for a separate analysis and its number (and name) is equal to *unit cell ID* of that row.
  + After all analyses are complete, the results are compiled automatically. See #TODO for more information.


Batch Modeling using the API
----------------------------

First, *structure_prefix* and *unit_cell_params_list* must be defined. For example:

.. code-block:: python2
  
  ## Define structure_prefix.
  structure_prefix = 'unnamed'
  
  ## Define unit_cell_params_list.
  # Define three unit cells for a batch of uniform structures.
  # Note that the first argument (id) is unique for each unit cell.
  unit_cell_params_list = []
  # (id, extrusion_depth, horz_bounding_box, vert_bounding_box,
  #  vert_strut_thickness, diag_strut_thickness, diag_strut_angle)
  unit_cell_params_list.append( Reentrant2DUcpBox(1, 5, 20, 24, 3.0, 1.5, 60) )
  unit_cell_params_list.append( Reentrant2DUcpBox(2, 5, 20, 24, 3.0, 1.5, 60) )
  unit_cell_params_list.append( Reentrant2DUcpBox(3, 5, 20, 24, 2.0, 1.5, 60) )
  
  # structures will be named 'unnamed-001', 'unnamed-003', and 'unnamed-003'.

Afterwards, the :func:`pyauxetic.main.main_batch` function is called for analysis. See #TODO for more information.