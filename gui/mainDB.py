import webbrowser
from abaqusGui import *

from pyauxetic.classes import auxetic_unit_cell_params
from helper import replace_combo_items
import tabs
import custom_input_forms

###########################################################################
# Class definition
###########################################################################

class MainDB(AFXDataDialog):
    
    # Define message IDs as class variables.
    [
        ID_URL_WEBSITE, ID_URL_DOCS, ID_URL_AUTHOR,
        ID_SELECT_UNIT_CELL_NAME   , ID_SELECT_STRUCTURE_TYPE,
        ID_SELECT_MODELING_MODE    , ID_INPUT_STRUCTURE_PARAMS_DIALOGBOX,
        ID_MATERIAL_MODEL
    ] = range(AFXDataDialog.ID_LAST, AFXDataDialog.ID_LAST+8)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #
        self.form = form
        AFXDataDialog.__init__(self, form, 'PuAuxetic',
                               DECOR_RESIZE|DIALOG_ACTIONS_SEPARATOR)
        
        border_size = 15
        
        
        ## Define the mapping functions.
        # Used in Tab 1: Welcome.
        FXMAPFUNC(self, SEL_COMMAND, self.ID_URL_WEBSITE, MainDB.open_url)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_URL_DOCS   , MainDB.open_url)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_URL_AUTHOR , MainDB.open_url)
        
        # Used in Tab 2: Modeling.
        FXMAPFUNC(self, SEL_COMMAND, self.ID_SELECT_UNIT_CELL_NAME,
                  MainDB.select_unit_cell_name)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_SELECT_STRUCTURE_TYPE,
                  MainDB.select_structure_type)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_SELECT_MODELING_MODE,
                  MainDB.select_modeling_mode)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_INPUT_STRUCTURE_PARAMS_DIALOGBOX,
                  MainDB.input_structure_params_dialogbox)
        
        # Used in Tab 3: Analysis.
        FXMAPFUNC(self, SEL_COMMAND, self.ID_MATERIAL_MODEL, MainDB.select_material_model)
        
        
        #showAFXInformationDialog(self,  sender.getText() )
        
        # Create the action buttons.
        self.appendActionButton('Run', self, self.ID_CLICKED_APPLY)
        self.appendActionButton(self.CANCEL)
        
        ## Make a tab book.
        tab_book = FXTabBook(self, None, 0, TABBOOK_LEFTTABS|LAYOUT_FILL_X)
        
        ## Tab 1: Welcome
        tabs.welcome_tab(self, form, tab_book, border_size)
        
        ## Tab 2: Modeling
        tabs.modeling_tab(self, form, tab_book, border_size)
        
        ## Tab 3: Analysis
        tabs.analysis_tab(self, form, tab_book, border_size)
        
        ## Tab 4: Post-Processing and Results
        tabs.results_tab(self, form, tab_book, border_size)
        
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def show(self):
        
        # Note: This method is only necessary because the prototype
        # application allows changes to be made in the dialog code and
        # reloaded while the application is still running. Normally you
        # would not need to have a show() method in your dialog.
        
        # Resize the dialog to its default dimensions to account for
        # any widget changes that may have been made.
        #
        self.resize(self.getDefaultWidth(), self.getDefaultHeight())
        AFXDataDialog.show(self)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def open_url(self, sender, sel, ptr):
        if   SELID(sel) == self.ID_URL_WEBSITE:
            webbrowser.open('http://www.google.com', new=2)
        elif SELID(sel) == self.ID_URL_DOCS:
            webbrowser.open('http://www.yahoo.com', new=2)
        elif SELID(sel) == self.ID_URL_AUTHOR:
            webbrowser.open('http://www.bing.com', new=2)
        else:
            raise ValueError('Invalid selector. This should not have happened.'+str(sel))
        return 1
    
    def select_unit_cell_name(self, sender, sel, ptr):
        sender_text = sender.getText()
        try:
            unit_cell_variant_list = auxetic_unit_cell_params.unit_cell_variant_dict[sender_text]
        except KeyError:
            raise RuntimeError("'%s' has not been defined in auxetic_unit_cell_params.unit_cell_variant_dict"%sender_text)
        replace_combo_items(self.unit_cell_variant_combo, unit_cell_variant_list)
        self.form.unit_cell_name_kw.setValue( sender_text )
        if sender_text in auxetic_unit_cell_params.unit_cells_3d_list:
            self.uniform_num_cell_repeat_z.enable()
            self.batch_num_cell_repeat_z.enable()
        else:
            self.uniform_num_cell_repeat_z.disable()
            self.batch_num_cell_repeat_z.disable()
        return 1
    
    def select_modeling_mode(self, sender, sel, ptr):
        sender_text = sender.getText()
        if   sender_text == 'Uniform (Single)':
            self.structure_params_sw.handle(self, MKUINT(FXSwitcher.ID_OPEN_SECOND, SEL_COMMAND), None)
            self.loading_direction_text.setTarget(self.form.uniform_loading_direction_kw)
        elif sender_text == 'Uniform (Batch)':
            self.structure_params_sw.handle(self, MKUINT(FXSwitcher.ID_OPEN_THIRD, SEL_COMMAND), None)
            self.loading_direction_text.setTarget(self.form.batch_loading_direction_kw)
        elif sender_text == 'Non-Uniform':
            self.structure_params_sw.handle(self, MKUINT(FXSwitcher.ID_OPEN_FOURTH , SEL_COMMAND), None)
            self.loading_direction_text.setTarget(self.form.nonuniform_loading_direction_kw)
        else:
            raise ValueError("Invalid modeling_mode:'%s'. This should not have happened. "%sender_text)
        self.form.modeling_mode_kw.setValue( sender_text )
        return 1
    
    def select_structure_type(self, sender, sel, ptr):
        sender_text = sender.getText()
        if sender_text in auxetic_unit_cell_params.all_structure_types_list:
            self.form.structure_type_kw.setValue( sender_text )
        else:
            raise ValueError("Invalid structure_type:'%s'. This should not have happened. "%sender_text)
        if sender_text in auxetic_unit_cell_params.all_tubular_structure_types_list:
            self.uniform_tube_radius.enable()
            self.batch_tube_radius.enable()
        else:
            self.uniform_tube_radius.disable()
            self.batch_tube_radius.disable()
        return 1
    
    def input_structure_params_dialogbox(self, sender, sel, ptr):
        
        if self.form.unit_cell_name_kw.getValue() == '':
            showAFXErrorDialog(getAFXApp().getAFXMainWindow(),
                               'No unit cell has been selected.')
            return 1
        if self.form.unit_cell_variant_kw.getValue() == '':
            showAFXErrorDialog(getAFXApp().getAFXMainWindow(),
                               'No unit cell variant has been selected.')
            return 1
        self.form.handle(self, MKUINT(self.form.ID_GET_NEXT, SEL_COMMAND), None)
        return 1
    
    def select_material_model(self, sender, sel, ptr):
        sender_text = sender.getText()
        if   sender_text == 'Elastic':
            self.material_type_sw.handle(self, MKUINT(FXSwitcher.ID_OPEN_SECOND, SEL_COMMAND), None)
        elif sender_text in ['Hyperelastic - Ogden', 'Hyperelastic - Marlow']:
            self.material_type_sw.handle(self, MKUINT(FXSwitcher.ID_OPEN_THIRD , SEL_COMMAND), None)
        else:
            raise ValueError("Invalid text:'%s'. This should not have happened. "%sender_text)
        self.form.material_type_kw.setValue( sender_text )
        return 1