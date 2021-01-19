from abaqusGui import *

from pyauxetic.classes import auxetic_unit_cell_params, auxetic_structure_params
from helper import replace_combo_items


def welcome_tab(self, form, tab_book, border_size):
    
    # Create the welcome tab.
    FXTabItem(tab_book, 'Welcome')
    #tab_main_frame = FXVerticalFrame(tab_book, FRAME_RAISED|FRAME_SUNKEN)
    tab_main_frame = FXVerticalFrame(tab_book, LAYOUT_FILL_X, LAYOUT_FILL_Y,
                         pl=border_size, pr=border_size, pt=border_size, pb=border_size)
    
    # Welcome text.
    AFXVerticalAligner(tab_main_frame)
    welcome_text_aligner = AFXVerticalAligner(tab_main_frame)
    FXLabel(welcome_text_aligner,
        'Welcome to the PyAuxetic Abaqus plugin.\n' +
        'This plugin automates modeling, analysis, and post processing of ' +
        'Auxetic structures.\n' +
        'You can also use the plugins aplication programming interface (API)\n' +
        'for more fucntionality and further automate your research workflow.\n' +
        'Learn more in our online documentation.', opts=JUSTIFY_CENTER_Y )
    
    # Information buttons.
    #TODO: make buttons work. consider a matrix
    info_buttons_aligner = FXHorizontalFrame(tab_main_frame, LAYOUT_CENTER_X)
    FXButton(info_buttons_aligner, 'Program Website'     , tgt=self, sel=self.ID_URL_WEBSITE)
    FXButton(info_buttons_aligner, 'Online Documentation', tgt=self, sel=self.ID_URL_DOCS   )
    FXButton(info_buttons_aligner, 'About the Author'    , tgt=self, sel=self.ID_URL_AUTHOR )
    
    copyright_text = FXLabel(tab_main_frame,
        ('Copyright \xA9 2021, The PyAuxetic Team\n' + 
         'This is an open source software published under the GNU AGPLv3 license.')
        , opts=LAYOUT_BOTTOM|LAYOUT_CENTER_X)
    copyright_text.setTextColor( FXRGB(31,31,31) )
    copyright_text.disable()
#

def modeling_tab(self, form, tab_book, border_size):
    
    FXTabItem(tab_book, 'Modeling')
    tab_main_frame = FXVerticalFrame(tab_book, LAYOUT_FILL_X, LAYOUT_FILL_Y,
                         pl=border_size, pr=border_size, pt=border_size, pb=border_size)
    
    ## Basic Structure Information
    basic_info_ncols = 16
    basic_info_box = FXGroupBox(tab_main_frame, 'Basic Structure Information', FRAME_GROOVE|LAYOUT_FILL_X)
    basic_info_matrix = FXMatrix(basic_info_box, n=1, opts=MATRIX_BY_ROWS)
    
    left_basic_info_aligner  = AFXVerticalAligner(basic_info_matrix)
    right_basic_info_aligner = AFXVerticalAligner(basic_info_matrix)
    
    # Add the structure_type combo box.
    unit_cell_name_combo = AFXComboBox(left_basic_info_aligner, basic_info_ncols, 3, 'Unit Cell:', tgt=self, sel=self.ID_SELECT_UNIT_CELL_NAME)
    replace_combo_items(unit_cell_name_combo, auxetic_unit_cell_params.unit_cells_list)
    
    # Add the unit_cell_variant combo box.
    unit_cell_variant_combo = AFXComboBox(right_basic_info_aligner, basic_info_ncols, 3, 'Unit Cell Variant:', tgt=form.unit_cell_variant_kw)
    unit_cell_variant_combo.appendItem('Full Parameters')
    unit_cell_variant_combo.appendItem('Bounding Box')
    unit_cell_variant_combo.appendItem('Simplified')
    self.unit_cell_variant_combo = unit_cell_variant_combo
    
    # Add the structure_type combo box.
    structure_type_combo = AFXComboBox(left_basic_info_aligner, basic_info_ncols, 3, 'Structure Type:', tgt=self, sel=self.ID_SELECT_STRUCTURE_TYPE)
    structure_type_combo.appendItem('Planar Shell')
    structure_type_combo.setText('')
    
    # Add the modeling_mode combo box.
    modeling_mode_combo = AFXComboBox(right_basic_info_aligner, basic_info_ncols, 3, 'Modeling Mode:', tgt=self, sel=self.ID_SELECT_MODELING_MODE)
    modeling_mode_combo.appendItem('Uniform (Single)')
    modeling_mode_combo.appendItem('Uniform (Batch)')
    modeling_mode_combo.appendItem('Non-Uniform')
    modeling_mode_combo.setText('')
    
    
    ### Structure Parameters.
    # Add the analysis_mode hframe and switcher.
    structure_params_box = FXGroupBox(tab_main_frame, 'Structure Parameters',
                                      FRAME_GROOVE|LAYOUT_FILL_X)
    structure_params_sw  = FXSwitcher(structure_params_box, LAYOUT_FILL_X|SWITCHER_VCOLLAPSE)
    self.structure_params_sw = structure_params_sw
    structure_params_vframe1 = FXVerticalFrame(structure_params_sw)
    FXLabel(structure_params_vframe1, 'Select a modeling mode to input data.')
    
    ## Single Structure Parameters
    # General parameters.
    structure_params_vframe2 = FXVerticalFrame(structure_params_sw, LAYOUT_CENTER_X|LAYOUT_FILL_X)
    uniform_general_params_aligner = AFXVerticalAligner(structure_params_vframe2)
    AFXTextField(uniform_general_params_aligner, 16, 'Structure Name:', opts=AFXTEXTFIELD_STRING, tgt=form.uniform_structure_name_kw)
    uniform_loading_dir_combo = AFXComboBox(uniform_general_params_aligner, 14, 2, 'Loading Direction:', tgt=form.uniform_loading_direction_kw)
    uniform_loading_dir_combo.appendItem('X-direction')
    uniform_loading_dir_combo.appendItem('Y-direction')
    
    uniform_structure_hframe = FXHorizontalFrame(structure_params_vframe2, LAYOUT_FILL_X)
    uniform_unit_cell_params_box = FXGroupBox(uniform_structure_hframe, 'Unit Cell Parameters',
                                      FRAME_GROOVE|LAYOUT_TOP)
    # Unit cell parameters.
    uniform_unit_cell_params_aligner = AFXVerticalAligner(uniform_unit_cell_params_box, LAYOUT_FILL_X)
    self.uniform_tube_radius = AFXTextField(uniform_unit_cell_params_aligner, 16, 'Tube Radius:       ', opts=AFXTEXTFIELD_FLOAT)
    FXVerticalFrame(uniform_unit_cell_params_box, LAYOUT_FILL_X)
    FXButton(uniform_unit_cell_params_box, 'Input\nStructure Parameters',
             tgt=self, sel=self.ID_INPUT_STRUCTURE_PARAMS_DIALOGBOX,
             opts=BUTTON_NORMAL|LAYOUT_CENTER_X|LAYOUT_BOTTOM)
    
    # uniform_num_cell_repeat parameters.
    uniform_num_cell_repeat_box = FXGroupBox(uniform_structure_hframe, 'Number of Unit Cells',
                                     FRAME_GROOVE|LAYOUT_TOP|LAYOUT_RIGHT|LAYOUT_FILL_X|LAYOUT_FILL_Y)
    uniform_num_cell_repeat_aligner = AFXVerticalAligner(uniform_num_cell_repeat_box, LAYOUT_FILL_X)
    AFXTextField(uniform_num_cell_repeat_aligner, 10, 'X-direction:', opts=AFXTEXTFIELD_INTEGER, tgt=form.uniform_num_cell_repeat_kw, sel=1)
    AFXTextField(uniform_num_cell_repeat_aligner, 10, 'Y-direction:', opts=AFXTEXTFIELD_INTEGER, tgt=form.uniform_num_cell_repeat_kw, sel=2)
    self.uniform_num_cell_repeat_z = AFXTextField(uniform_num_cell_repeat_aligner, 10, 'Z-direction:', opts=AFXTEXTFIELD_INTEGER, tgt=form.uniform_num_cell_repeat_kw, sel=3)
    
    ## Batch Structure Parameters
    structure_params_vframe3 = FXVerticalFrame(structure_params_sw, LAYOUT_CENTER_X)
    batch_general_params_aligner = AFXVerticalAligner(structure_params_vframe3)
    AFXTextField(batch_general_params_aligner, 16, 'Structure Prefix: ', opts=AFXTEXTFIELD_STRING, tgt=form.batch_structure_prefix_kw)
    batch_loading_dir_combo = AFXComboBox(batch_general_params_aligner, 14, 2, 'Loading Direction:', tgt=form.batch_loading_direction_kw)
    batch_loading_dir_combo.appendItem('X-direction')
    batch_loading_dir_combo.appendItem('Y-direction')
    
    batch_structure_hframe = FXHorizontalFrame(structure_params_vframe3, LAYOUT_FILL_X)
    batch_unit_cell_params_box = FXGroupBox(batch_structure_hframe, 'Unit Cell Parameters',
                                    FRAME_GROOVE|LAYOUT_TOP)
    batch_unit_cell_params_aligner = AFXVerticalAligner(batch_unit_cell_params_box,
                                                        LAYOUT_FILL_X)
    self.batch_tube_radius = AFXTextField(batch_unit_cell_params_aligner, 15, 'Tube Radius:', opts=AFXTEXTFIELD_FLOAT)
    batch_num_analysis = AFXTextField(batch_unit_cell_params_aligner, 15, 'Number of Analyses:')
    self.batch_num_analysis = batch_num_analysis
    batch_num_analysis.setReadOnlyState(True)
    batch_num_analysis.setText('Not Specified')
    FXVerticalFrame(batch_unit_cell_params_box)
    FXButton(batch_unit_cell_params_box, 'Input\n Structure Parameters',
             tgt=self, sel=self.ID_INPUT_STRUCTURE_PARAMS_DIALOGBOX,
             opts=BUTTON_NORMAL|LAYOUT_CENTER_X|LAYOUT_BOTTOM)
    
    batch_num_cell_repeat_box = FXGroupBox(batch_structure_hframe, 'Number of Unit Cells',
                                    FRAME_GROOVE|LAYOUT_TOP|LAYOUT_RIGHT|LAYOUT_FILL_X|LAYOUT_FILL_Y)
    batch_num_cell_repeat_aligner = AFXVerticalAligner(batch_num_cell_repeat_box, LAYOUT_FILL_X)
    AFXTextField(batch_num_cell_repeat_aligner, 10, 'X-direction:', opts=AFXTEXTFIELD_INTEGER, tgt=form.batch_num_cell_repeat_kw, sel=1)
    AFXTextField(batch_num_cell_repeat_aligner, 10, 'Y-direction:', opts=AFXTEXTFIELD_INTEGER, tgt=form.batch_num_cell_repeat_kw, sel=2)
    self.batch_num_cell_repeat_z = AFXTextField(batch_num_cell_repeat_aligner, 10, 'Z-direction:', opts=AFXTEXTFIELD_INTEGER, tgt=form.batch_num_cell_repeat_kw, sel=3)
    
    ## Non-Uniform Structure Parameters
    #TODO: see if the button is prettier if left justified.
    structure_params_vframe4 = FXVerticalFrame(structure_params_sw, LAYOUT_CENTER_X|LAYOUT_FILL_X)
    nonuniform_structure_params_aligner = AFXVerticalAligner(structure_params_vframe4)
    AFXTextField(nonuniform_structure_params_aligner, 16, 'Structure Name:', opts=AFXTEXTFIELD_STRING, tgt=form.nonuniform_structure_name_kw)
    nonuniform_loading_dir_combo = AFXComboBox(nonuniform_structure_params_aligner, 14, 2, 'Loading Direction:', tgt=form.nonuniform_loading_direction_kw)
    nonuniform_loading_dir_combo.appendItem('X-direction')
    nonuniform_loading_dir_combo.appendItem('Y-direction')
    nonuniform_structure_size = AFXTextField(nonuniform_structure_params_aligner, 16, 'Structure Size:')
    self.nonuniform_structure_size = nonuniform_structure_size
    nonuniform_structure_size.setReadOnlyState(True)
    nonuniform_structure_size.setText('Not Specified')
    nonuniform_num_unit_cells = AFXTextField(nonuniform_structure_params_aligner, 16, 'Number of\nUnique Unit Cells:')
    self.nonuniform_num_unit_cells = nonuniform_num_unit_cells
    nonuniform_num_unit_cells.setReadOnlyState(True)
    nonuniform_num_unit_cells.setText('Not Specified')
    FXVerticalFrame(structure_params_vframe4)
    FXButton(structure_params_vframe4, 'Input\n Structure Parameters',
             tgt=self, sel=self.ID_INPUT_STRUCTURE_PARAMS_DIALOGBOX,
             opts=BUTTON_NORMAL|LAYOUT_CENTER_X|LAYOUT_BOTTOM)
#

def analysis_tab(self, form, tab_book, border_size):
    
    FXTabItem(tab_book, 'Analysis')
    tab_main_frame = FXVerticalFrame(tab_book, LAYOUT_FILL_X, LAYOUT_FILL_Y,
                         pl=border_size, pr=border_size, pt=border_size, pb=border_size)
    
    # This check button enables or disables all other widgets in the tab.
    FXCheckButton(tab_main_frame, 'Run the finite element analysis.', tgt=form.run_analysis_kw)
    
    ## The material group box.
    material_prop_box = FXGroupBox(tab_main_frame, 'Material Properties',
                                   FRAME_GROOVE|LAYOUT_TOP|LAYOUT_LEFT|LAYOUT_FILL_X)
    # Add the material_type combo box.
    material_type_combo = AFXComboBox(material_prop_box, 0, 3, 'Material Model:', tgt=self, sel=self.ID_MATERIAL_MODEL)
    material_type_combo.appendItem('Elastic')
    material_type_combo.appendItem('Hyperelastic - Ogden')
    material_type_combo.appendItem('Hyperelastic - Marlow')
    material_type_combo.setText('')
    
    material_type_sw  = FXSwitcher(material_prop_box)
    self.material_type_sw = material_type_sw
    material_type_vframe1 = FXVerticalFrame(material_type_sw)
    FXLabel(material_type_vframe1, 'Select a material model to input data.')
    material_type_vframe2 = FXVerticalFrame(material_type_sw)
    FXLabel(material_type_vframe2, 'Material Data:')
    #prop_table_frame = FXVerticalFrame(material_prop_box)
    elastic_table_frame = FXVerticalFrame(material_type_vframe2,
                                    FRAME_SUNKEN|FRAME_THICK|LAYOUT_RIGHT, 0,0,0,0, 0,0,0,0)
    elastic_table = AFXTable(elastic_table_frame, 2,2, 2,2, opts=AFXTABLE_EDITABLE, tgt=form.material_elastic_table_kw)
    elastic_table.setLeadingRows(1)
    elastic_table.showVerticalGrid(True)
    elastic_table.setColumnWidthInChars(-1, 15)
    elastic_table.setColumnType(-1, AFXTable.FLOAT)
    elastic_table.setDefaultJustify(AFXTable.CENTER)
    elastic_table.setPopupOptions(
        AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE)
    elastic_table.setLeadingRowLabels("Young's Modulus\tPoisson's Ratio")
    
    material_type_vframe3 = FXVerticalFrame(material_type_sw)
    FXLabel(material_type_vframe3, 'Material Data:')
    stress_strain_table_frame = FXVerticalFrame(material_type_vframe3,
                                    FRAME_SUNKEN|FRAME_THICK|LAYOUT_RIGHT, 0,0,0,0, 0,0,0,0)
    stress_strain_table = AFXTable(stress_strain_table_frame, 4,3, 4,3,
                            opts=AFXTABLE_EDITABLE|AFXTABLE_EXTENDED_SELECT, tgt=form.material_stress_strain_table_kw)
    stress_strain_table.setLeadingRows(1)
    stress_strain_table.setLeadingColumns(1)
    stress_strain_table.showVerticalGrid(True)
    stress_strain_table.showHorizontalGrid(True)
    stress_strain_table.setColumnWidthInChars(-1, 15)
    stress_strain_table.setColumnType(-1, AFXTable.FLOAT)
    stress_strain_table.setDefaultJustify(AFXTable.CENTER)
    stress_strain_table.setStretchableColumn( stress_strain_table.getNumColumns()-1 )
    stress_strain_table.setPopupOptions(
        AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|AFXTable.POPUP_PASTE|AFXTable.POPUP_INSERT_ROW|AFXTable.POPUP_DELETE_ROW|AFXTable.POPUP_CLEAR_CONTENTS)
    stress_strain_table.setLeadingRowLabels('Stress\tStrain')
    
    ## Create a matrix for storing step, job, load, and mesh boxes.
    step_job_load_mesh_matrix = FXMatrix(tab_main_frame, 2, MATRIX_BY_COLUMNS,
                                         pl=0, pr=0, pt=0, pb=0)
    ## The step group box.
    step_box = FXGroupBox(step_job_load_mesh_matrix, 'Step Parameters', FRAME_GROOVE|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y)
    step_vframe = FXVerticalFrame(step_box)
    step_aligner = AFXVerticalAligner(step_vframe, LAYOUT_FILL_X)
    AFXTextField(step_aligner, 8, 'Time Period:'                  , opts=AFXTEXTFIELD_FLOAT, tgt=form.step_time_period_kw)
    AFXTextField(step_aligner, 8, 'Maximum number  \nof increments:', opts=AFXTEXTFIELD_FLOAT, tgt=form.step_max_num_inc_kw)
    step_size_hframe = FXHorizontalFrame(step_vframe)
    FXLabel(step_size_hframe, 'Increment Size:', opts=LAYOUT_BOTTOM)
    AFXTextField(step_size_hframe, 6, 'Initial', opts=AFXTEXTFIELD_FLOAT|AFXTEXTFIELD_VERTICAL|LAYOUT_BOTTOM, tgt=form.step_init_inc_size_kw)
    AFXTextField(step_size_hframe, 6, 'Min'    , opts=AFXTEXTFIELD_FLOAT|AFXTEXTFIELD_VERTICAL|LAYOUT_BOTTOM, tgt=form.step_min_inc_size_kw)
    AFXTextField(step_size_hframe, 6, 'Max'    , opts=AFXTEXTFIELD_FLOAT|AFXTEXTFIELD_VERTICAL|LAYOUT_BOTTOM, tgt=form.step_max_inc_size_kw)
    
    ## The job group box.
    job_box = FXGroupBox(step_job_load_mesh_matrix, 'Job Parameters', FRAME_GROOVE|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y)
    job_vframe = FXVerticalFrame(job_box)
    job_aligner = AFXVerticalAligner(job_vframe, LAYOUT_FILL_X)
    AFXSpinner(job_aligner, 8, 'Number of CPU Cores:'  , opts=AFXTEXTFIELD_INTEGER, tgt=form.job_num_cpu_kw)
    AFXSpinner(job_aligner, 8, 'Max Allocated RAM (%):', opts=AFXTEXTFIELD_INTEGER, tgt=form.job_max_ram_kw)
    job_precision_combo = AFXComboBox(job_aligner, 8, 2, 'Precision:', tgt=form.job_precision_kw)
    job_precision_combo.appendItem('Single')
    job_precision_combo.appendItem('Double')
    
    ## The loading group box.
    loading_box = FXGroupBox(step_job_load_mesh_matrix, 'Loading Parameters',
                      FRAME_GROOVE|LAYOUT_TOP|LAYOUT_LEFT|LAYOUT_FILL_X|LAYOUT_FILL_Y)
    loading_aligner = AFXVerticalAligner(loading_box, LAYOUT_FILL_X)
    self.loading_direction_text = AFXTextField(loading_aligner, 10, 'Loading Direction:')
    self.loading_direction_text.setReadOnlyState(True)
    loading_type_combo = AFXComboBox(loading_aligner, 12, 2, 'Loading Type:', tgt=form.loading_type_kw)
    loading_type_combo.appendItem('Displacement')
    loading_type_combo.appendItem('Force')
    loading_type_combo.setText('')
    AFXTextField(loading_aligner, 15, 'Loading Value:', tgt=form.loading_value_kw)
    
    ## The mesh group box.
    mesh_box = FXGroupBox(step_job_load_mesh_matrix, 'Mesh Parameters',
                   FRAME_GROOVE|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y)
    mesh_aligner = AFXVerticalAligner(mesh_box, LAYOUT_FILL_X)
    elem_shape_combo = AFXComboBox(mesh_aligner, 20, 2, 'Element Shape:'  , tgt=form.mesh_elem_shape_kw)
    replace_combo_items(elem_shape_combo, auxetic_structure_params.all_elem_shape_list)
    elem_code_combo = AFXComboBox(mesh_aligner , 20, 2, 'Element Code(s):', tgt=form.mesh_elem_code_kw)
    replace_combo_items(elem_code_combo, auxetic_structure_params.all_elem_code_list)
    AFXTextField(mesh_aligner, 22, 'Seed Size', opts=AFXTEXTFIELD_FLOAT, tgt=form.mesh_seed_size_kw)
#

def results_tab(self, form, tab_book, border_size):
    
    FXTabItem(tab_book, 'Post-Processing\nand Results')
    tab_main_frame = FXVerticalFrame(tab_book, LAYOUT_FILL_X, LAYOUT_FILL_Y,
                         pl=border_size, pr=border_size, pt=border_size, pb=border_size)
    
    ## Output Options group box.
    results_hframe1 = FXHorizontalFrame(tab_main_frame, LAYOUT_FILL_X,
                                           pl=0, pr=0, pt=0, pb=0)
    
    # Analysis Files
    analysis_files_box = FXGroupBox(results_hframe1, 'Analysis Files',
                                   FRAME_GROOVE|LAYOUT_FILL_X|LAYOUT_FILL_Y)
    FXCheckButton(analysis_files_box, 'Save calculated results', tgt=form.write_results_kw)
    FXCheckButton(analysis_files_box, 'Save .cae file'         , tgt=form.save_cae_kw)
    FXCheckButton(analysis_files_box, 'Save .odb file'         , tgt=form.save_odb_kw)
    FXCheckButton(analysis_files_box, 'Save other job files'   , tgt=form.save_job_files_kw)
    
    # Pictures
    #TODO: add
    picture_box = FXGroupBox(results_hframe1, 'Pictures',
                                    FRAME_GROOVE|LAYOUT_TOP|LAYOUT_LEFT|LAYOUT_FILL_X)
    FXCheckButton(picture_box, 'Points of interest in the structure', tgt=form.output_pic_poi_kw)
    FXCheckButton(picture_box, 'Deformed Contours:', tgt=form.output_pic_deformed_kw)
    contour_matrix = FXMatrix(picture_box, 3, MATRIX_BY_COLUMNS,
                              pl=border_size, pr=border_size, pt=0, pb=0)
    contour_list = []
    contour_list.append( FXCheckButton(contour_matrix, 'MISES', tgt=form.output_pic_mises_kw) )
    contour_list.append( FXCheckButton(contour_matrix, 'PEEQ' , tgt=form.output_pic_peeq_kw ) )
    for item in contour_list:
        self.addTransition(form.output_pic_deformed_kw, AFXTransition.EQ, True,  item,
                           MKUINT(FXWindow.ID_ENABLE, SEL_COMMAND) )
        self.addTransition(form.output_pic_deformed_kw, AFXTransition.EQ, False, item,
                           MKUINT(FXWindow.ID_DISABLE, SEL_COMMAND) )
    FXCheckButton(picture_box, 'Output for all increments (slow)', tgt=form.output_pic_all_inc_kw)
    
    
    # Export Model
    export_box = FXGroupBox(tab_main_frame, 'Export Model',
                                   FRAME_GROOVE|LAYOUT_TOP|LAYOUT_LEFT|LAYOUT_FILL_X)
    FXCheckButton(export_box, 'Export 3D model:', tgt=form.export_3d_model_kw)
    export_matrix = FXMatrix(export_box, 3, MATRIX_BY_COLUMNS,
                             pl=border_size, pr=border_size, pt=0, pb=0)
    export_options_list = []
    export_options_list.append( FXCheckButton(export_matrix, 'STL', tgt=form.export_stl_kw) )
    export_options_list.append( FXCheckButton(export_matrix, 'STP', tgt=form.export_stp_kw) )
    for item in export_options_list:
        self.addTransition(form.export_3d_model_kw, AFXTransition.EQ,  True, item,
                           MKUINT(FXWindow.ID_ENABLE, SEL_COMMAND) )
        self.addTransition(form.export_3d_model_kw, AFXTransition.EQ, False, item,
                           MKUINT(FXWindow.ID_DISABLE, SEL_COMMAND) )
    
    export_nums_aligner = AFXVerticalAligner(export_box, LAYOUT_FILL_X)
    AFXTextField(export_nums_aligner, 10, 'Export Ribbon Width:', opts=AFXTEXTFIELD_FLOAT, tgt=form.export_ribbon_width_kw)
    AFXTextField(export_nums_aligner, 10, 'Extrusion Depth:'    , opts=AFXTEXTFIELD_FLOAT, tgt=form.extrusion_depth_kw)
    AFXNote(export_box, 'The 2D structure will be extruded in the Z-direction.')
    #TODO: disable if checkbox is off.
    #TODO: hide the 3d stuff if the structure is already 3d.
    AFXNote(tab_main_frame,
        'The results of each analysis will be output in corresponding folders in\n '
        +os.getcwd(), LAYOUT_BOTTOM)
#TODO: check if 8 is ok for all numeric fields.
#TODO: disable the extrude depth if not 2d.