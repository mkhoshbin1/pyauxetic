Adjusting Step Parameters
=========================

The analysis is done in one step. The main parameters of this step can (and should) be adjusted to complete the analysis in a timely manner.


Adjusting Step Parameters using the GUI
---------------------------------------

The *Step Parameters* frame of the analysis tab can be seen in :numref:`step-parameters-frame`. Note that in a batch analysis these parameters are used for all models. Therefore, care should be taken to select a set of parameters suitable for all analysis. If a model needs a different set, it should be run as a single analysis.

.. figure:: ../images/step-parameters-frame.png
    :name: step-parameters-frame
    :scale: 100%
    :align: center
    :alt: Step parameters frame with the default values.
    
    Step parameters frame with the default values.


Adjusting Step Parameters using the API
---------------------------------------

Step parameters are defined by defining a *StepParams* object. A list of all attributes and their significance can be found in :class:`.classes.auxetic_structure_params.StepParams`. An example is shown below:

.. code-block:: python2
  
  # Define the step_params object.
  # Undefined attributes default to None.
  step_params = StepParams(
      time_period   = 0.1  ,
      init_inc_size = 0.01 ,
      min_inc_size  = 0.005,
      max_inc_size  = 0.05 ,
      max_num_inc   = 10000
  )