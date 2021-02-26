from abaqusGui import *

# Find the location of the the pyauxetic library.
import inspect
current_file_path = inspect.getfile(inspect.currentframe())
pyauxetic_library_path = os.path.split(os.path.split(current_file_path)[0])[0]
sys.path.append(pyauxetic_library_path)

from pyauxetic.classes import auxetic_unit_cell_params

import mainDB
import tabs
import custom_input_forms
import custom_input_forms
from helper import return_param_dialogbox

# Note: The above form of the import statement is used for the prototype
# application to allow the module to be reloaded while the application is
# still running. In a non-prototype application you would use the form:
# from myDB import MyDB

###########################################################################
# Class definition
###########################################################################

class MainForm(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):

        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.setModal(True)
                
        # Command
        #
        self.cmd = AFXGuiCommand(self, 'main_gui_proxy', 'pyauxetic.main')
        self.single_structure_params_dialogbox     = None
        self.batch_structure_params_dialogbox      = None
        self.nonuniform_structure_params_dialogbox = None
        
        ## Modeling tab
        # General Parameters.
        self.unit_cell_name_kw    = AFXStringKeyword(self.cmd, 'unit_cell_name'   , True)
        self.unit_cell_variant_kw = AFXStringKeyword(self.cmd, 'unit_cell_variant', True)
        self.structure_type_kw    = AFXStringKeyword(self.cmd, 'structure_type'   , True)
        self.modeling_mode_kw     = AFXStringKeyword(self.cmd, 'modeling_mode'    , True)
        
        # Single uniform structure modeling mode parameters.
        self.uniform_structure_name_kw         = AFXStringKeyword(self.cmd, 'uniform_structure_name'        , True , '')
        self.uniform_loading_direction_kw      = AFXStringKeyword(self.cmd, 'uniform_loading_direction'     , True)
        self.uniform_num_cell_repeat_kw        =  AFXTupleKeyword(self.cmd, 'uniform_num_cell_repeat'       , True, 3, 3, AFXTUPLE_TYPE_INT)
        self.uniform_structure_params_table_kw =  AFXTableKeyword(self.cmd, 'uniform_structure_params_table', True, opts=AFXTABLE_TYPE_FLOAT)
        
        # Batch uniform structure modeling mode parameters.
        self.batch_structure_prefix_kw       = AFXStringKeyword(self.cmd, 'batch_structure_prefix'      , True, '')
        self.batch_loading_direction_kw      = AFXStringKeyword(self.cmd, 'batch_loading_direction'     , True)
        self.batch_num_cell_repeat_kw        =  AFXTupleKeyword(self.cmd, 'batch_num_cell_repeat'       , True, 3, 3, AFXTUPLE_TYPE_INT)
        self.batch_structure_params_table_kw =  AFXTableKeyword(self.cmd, 'batch_structure_params_table', True, opts=AFXTABLE_TYPE_FLOAT)
        
        # Non-Uniform structure modeling mode parameters.
        self.nonuniform_structure_name_kw         = AFXStringKeyword(self.cmd, 'nonuniform_structure_name'        , True, '')
        self.nonuniform_loading_direction_kw      = AFXStringKeyword(self.cmd, 'nonuniform_loading_direction'     , True)
        self.nonuniform_structure_params_table_kw =  AFXTableKeyword(self.cmd, 'nonuniform_structure_params_table', True, opts=AFXTABLE_TYPE_FLOAT)
        self.nonuniform_structure_map_table_kw    =  AFXTableKeyword(self.cmd, 'nonuniform_structure_map_table'   , True, opts=AFXTABLE_TYPE_INT)
        
        ## Analysis tab
        #TODO: implement enable/disable.
        self.run_analysis_kw = AFXBoolKeyword(self.cmd, 'run_analysis', AFXBoolKeyword.TRUE_FALSE, True, False)
        
        self.material_type_kw                = AFXStringKeyword(self.cmd, 'material_type'      , False)
        self.material_elastic_table_kw       =  AFXTableKeyword(self.cmd, 'material_elastic_table'      , False, 1, 2, opts=AFXTABLE_TYPE_FLOAT)
        self.material_stress_strain_table_kw =  AFXTableKeyword(self.cmd, 'material_stress_strain_table', False, 1, 2, opts=AFXTABLE_TYPE_FLOAT)
        
        self.step_time_period_kw   = AFXFloatKeyword(self.cmd, 'step_time_period'  , True, 1.0)
        self.step_max_num_inc_kw   =   AFXIntKeyword(self.cmd, 'step_max_num_inc'  , True, 100)
        self.step_init_inc_size_kw = AFXFloatKeyword(self.cmd, 'step_init_inc_size', True, 0.1)
        self.step_min_inc_size_kw  = AFXFloatKeyword(self.cmd, 'step_min_inc_size' , True, 0.05)
        self.step_max_inc_size_kw  = AFXFloatKeyword(self.cmd, 'step_max_inc_size' , True, 0.1)
        
        self.job_num_cpu_kw   =    AFXIntKeyword(self.cmd, 'job_num_cpu'  , True, 2)
        self.job_max_ram_kw   =    AFXIntKeyword(self.cmd, 'job_max_ram'  , True, 80)
        self.job_precision_kw = AFXStringKeyword(self.cmd, 'job_precision', True, 'Single')
        
        self.loading_type_kw  = AFXStringKeyword(self.cmd, 'loading_type' , True)
        self.loading_value_kw =  AFXFloatKeyword(self.cmd, 'loading_value', False)
        
        self.mesh_elem_shape_kw = AFXStringKeyword(self.cmd, 'mesh_elem_shape', False)#TODO: if run_analysis is true, make it mandatory.
        self.mesh_elem_code_kw  = AFXStringKeyword(self.cmd, 'mesh_elem_code' , False)
        self.mesh_seed_size_kw  =  AFXFloatKeyword(self.cmd, 'mesh_seed_size' , False)
        
        ## Post-Processing and Results tab
        #TODO: rename all so they have the same prefix.
        self.write_results_kw  = AFXBoolKeyword(self.cmd, 'write_results' , AFXBoolKeyword.TRUE_FALSE, True, True)
        self.save_cae_kw       = AFXBoolKeyword(self.cmd, 'save_cae'      , AFXBoolKeyword.TRUE_FALSE, True, True)
        self.save_odb_kw       = AFXBoolKeyword(self.cmd, 'save_odb'      , AFXBoolKeyword.TRUE_FALSE, True, True)
        self.save_job_files_kw = AFXBoolKeyword(self.cmd, 'save_job_files', AFXBoolKeyword.TRUE_FALSE, True, True)
        
        self.output_pic_poi_kw      = AFXBoolKeyword(self.cmd, 'output_pic_poi'     , AFXBoolKeyword.TRUE_FALSE, True, True)
        self.output_pic_deformed_kw = AFXBoolKeyword(self.cmd, 'output_pic_deformed', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.output_pic_mises_kw    = AFXBoolKeyword(self.cmd, 'output_pic_mises'   , AFXBoolKeyword.TRUE_FALSE, True, True)
        self.output_pic_peeq_kw     = AFXBoolKeyword(self.cmd, 'output_pic_peeq'    , AFXBoolKeyword.TRUE_FALSE, True, True)
        self.output_pic_all_inc_kw  = AFXBoolKeyword(self.cmd, 'output_pic_all_inc' , AFXBoolKeyword.TRUE_FALSE, True, False)
        
        self.export_3d_model_kw = AFXBoolKeyword(self.cmd, 'export_3d_model', AFXBoolKeyword.TRUE_FALSE, True, True)
        self.export_stl_kw      = AFXBoolKeyword(self.cmd, 'export_stl'     , AFXBoolKeyword.TRUE_FALSE, True, True)
        self.export_stp_kw      = AFXBoolKeyword(self.cmd, 'export_stp'     , AFXBoolKeyword.TRUE_FALSE, True, True)
        
        self.export_ribbon_width_kw = AFXFloatKeyword(self.cmd, 'export_ribbon_width', False)
        self.extrusion_depth_kw     = AFXFloatKeyword(self.cmd, 'extrusion_depth'    , False)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        # Note: The style below is used for the prototype application to 
        # allow the dialog to be reloaded while the application is
        # still running. In a non-prototype application you would use:
        #
        # return MyDB(self)
        
        # Reload the dialog module so that any changes to the dialog 
        # are updated.
        #
        reload(mainDB)
        reload(tabs)
        reload(custom_input_forms)
        self.main_dialogbox = mainDB.MainDB(self)
        return self.main_dialogbox
    
    def getNextDialog(self, previous_dialogbox):
        #TODO: add to kw for OK and clean for Cancel (if kw is None). 
        #raise NotImplementedError('see here!!!')
        
        # If previous_dialogbox is main_dialogbox, create and return
        # the structure parameter dialog box based on modeling_mode_kw. 
        
        if previous_dialogbox == self.main_dialogbox:
            uc_name    = self.unit_cell_name_kw.getValue()
            uc_variant = self.unit_cell_variant_kw.getValue()
            new_param_class = auxetic_unit_cell_params.unit_cell_params_class_dict[
                                      (uc_name,uc_variant) ]
            modeling_mode = self.modeling_mode_kw.getValue()
            if   modeling_mode == 'Uniform (Single)':
                dialogbox = return_param_dialogbox(self,
                    self.single_structure_params_dialogbox,
                    new_param_class, 'Uniform (Single)', 15)
                self.single_structure_params_dialogbox = dialogbox
            elif modeling_mode == 'Uniform (Batch)':
                dialogbox = return_param_dialogbox(self,
                    self.batch_structure_params_dialogbox,
                    new_param_class, 'Uniform (Batch)', 15)
                self.batch_structure_params_dialogbox = dialogbox
            elif modeling_mode == 'Non-Uniform':
                dialogbox = return_param_dialogbox(self,
                    self.nonuniform_structure_params_dialogbox,
                    new_param_class, 'Non-Uniform', 15)
                self.nonuniform_structure_params_dialogbox = dialogbox
            else:
                raise ValueError('Unexpected value for modeling_mode.')
            return dialogbox
        
        # If previous_dialogbox is a structure parameter dialog box.
        elif isinstance(previous_dialogbox, custom_input_forms.StructureParamsDB):
            previous_dialogbox.hide()
            return self.main_dialogbox
        
        else:
            raise NotImplementedError('Unexpected previous_dialogbox at getNextDialog().')
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Enable this block for prototyping.
    #def issueCommands(self):
    #    cmds = self.getCommandString()
    #    getAFXApp().getAFXMainWindow().writeToMessageArea(cmds)
    #    self.deactivateIfNeeded()
    #    return TRUE
    
    # Enable this block for production.
    def getCommandString(self):
        
        cmds = ''
        cmds += "sys.path.append('%s')\n" %pyauxetic_library_path
        cmds += 'import pyauxetic.main\n'
        
        cmds += AFXForm.getCommandString(self)
        return cmds