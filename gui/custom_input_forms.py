from abaqusGui import *

from collections import namedtuple

class StructureParamsDB(AFXDataDialog):
    """Defines a dialog box for inputting structure parameters.
    Has three different appearances based on the value of self.param_input_mode."""
    # Define message IDs as class variables.
    [ID_CHANGE_COLUMNS, ID_CHANGE_ROWS
    ] = range(AFXDataDialog.ID_LAST, AFXDataDialog.ID_LAST+2)
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form, param_obj_class, param_input_mode,
                 border_size, default_num_unit_cells_x=5, default_num_unit_cells_y=5):
        self.form = form
        self.param_input_mode = param_input_mode
        self.param_obj_class  = param_obj_class
        if   param_input_mode == 'Uniform (Single)':
            title = 'Parameters for a Single Uniform Structure'
            num_param_rows = 11  #Dummy value. Not used.
            params_table_first_col_name = ''
            single_params_table_target  = form.uniform_structure_params_table_kw
            batch_params_table_target   = None
            structure_map_target        = None
        elif param_input_mode == 'Uniform (Batch)':
            title = 'Parameters for a Batch of Uniform Structures'
            num_param_rows = 11
            params_table_first_col_name = 'Run ID\t'
            single_params_table_target  = None
            batch_params_table_target   = form.batch_structure_params_table_kw
            structure_map_target        = None
        elif param_input_mode == 'Non-Uniform':
            title = 'Parameters for a Single Non-Uniform Structure'
            num_param_rows = 6
            params_table_first_col_name = 'Unit Cell ID\t'
            single_params_table_target  = None
            batch_params_table_target   = form.nonuniform_structure_params_table_kw
            structure_map_target        = form.nonuniform_structure_map_table_kw
        else:
            raise ValueError('Unexpected value for param_input_mode.')
        
        # Construct the base class.
        AFXDataDialog.__init__(self, form, title,
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR|DIALOG_UNPOST_DESTROY)
        
        # Map the message functions.
        FXMAPFUNC(self, SEL_COMMAND, self.ID_CHANGE_COLUMNS, StructureParamsDB.update_structure_map_table)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_CHANGE_ROWS   , StructureParamsDB.update_structure_map_table)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_CLICKED_OK    , StructureParamsDB.clicked_ok)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_CLICKED_CANCEL, StructureParamsDB.clicked_cancel)
        
        
        # Create frame for all widgets.
        main_frame = FXVerticalFrame(self,
                                     pl=border_size, pr=border_size)
        
        # Create frame for the parameters tables.
        params_frame = FXVerticalFrame(main_frame)
        FXLabel(params_frame, 'Enter the parameters for the %s unit cell(s): '%param_obj_class.unit_cell_type)
        
        # Compile the list of field names based on param_obj_class.
        param_obj_class_formal_field_list = [param_obj_class.formal_names[f] for f in param_obj_class._fields]
        num_params = len(param_obj_class._fields)
        
        # Create the input table for a single uniform structure.
        single_params_table_frame = FXVerticalFrame(params_frame, FRAME_SUNKEN|FRAME_THICK)
        single_params_table = AFXTable(single_params_table_frame, num_params,2, num_params,2,
                                opts=AFXTABLE_EDITABLE|AFXTABLE_EXTENDED_SELECT, tgt=single_params_table_target)
        self.single_params_table = single_params_table
        single_params_table.setLeadingRows(1)
        single_params_table.setLeadingColumns(1)
        single_params_table.showVerticalGrid(True)
        single_params_table.showHorizontalGrid(True)
        single_params_table.setDefaultType(AFXTable.FLOAT)
        single_params_table.setDefaultJustify(AFXTable.CENTER)
        single_params_table.setColumnJustify(0, AFXTable.LEFT)
        single_params_table.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|
            AFXTable.POPUP_PASTE|AFXTable.POPUP_CLEAR_CONTENTS)
        single_params_table.setLeadingRowLabels('Value')
        single_params_table.setLeadingColumnLabels(
            params_table_first_col_name+ '\t'.join(param_obj_class_formal_field_list[1:]) )
        
        # Create the input table for a batch of uniform structures.
        batch_params_table_frame = FXVerticalFrame(params_frame, FRAME_SUNKEN|FRAME_THICK)
        batch_params_table = AFXTable(batch_params_table_frame, num_param_rows,num_params, num_param_rows,num_params,
                                      opts=AFXTABLE_EDITABLE|AFXTABLE_EXTENDED_SELECT, tgt=batch_params_table_target)
        self.batch_params_table = batch_params_table
        batch_params_table.setLeadingRows(1)
        batch_params_table.showVerticalGrid(True)
        batch_params_table.showHorizontalGrid(True)
        batch_params_table.setDefaultType(AFXTable.FLOAT)
        batch_params_table.setColumnType(0, AFXTable.INT)
        batch_params_table.setDefaultJustify(AFXTable.CENTER)
        batch_params_table.setStretchableColumn( batch_params_table.getNumColumns()-1 )
        batch_params_table.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|
            AFXTable.POPUP_PASTE|AFXTable.POPUP_INSERT_ROW|
            AFXTable.POPUP_DELETE_ROW|AFXTable.POPUP_CLEAR_CONTENTS)
        batch_params_table.setLeadingRowLabels(
            params_table_first_col_name+ '\t'.join(param_obj_class_formal_field_list[1:]) )
        for i in range( len(param_obj_class_formal_field_list) ):
            batch_params_table.setColumnWidthInChars(i, len(param_obj_class_formal_field_list[i])-3)
        for i in range( 1, batch_params_table.getNumRows() ):
            batch_params_table.setItemIntValue(i, 0, i)
        
        # Create a horizontal seperator.
        h_separator =  FXHorizontalSeparator(main_frame, opts=SEPARATOR_GROOVE| LAYOUT_FILL_X)
        
        
        # Create the input table the structure map of a nonuniform structure.
        structure_map_frame  = FXVerticalFrame(main_frame)
        num_unit_cells_frame = FXHorizontalFrame(structure_map_frame, pl=0, pr=0, pt=0, pb=0)
        x_spinner = AFXSpinner(num_unit_cells_frame, 3, 'Enter number of unit cells in the:      X-direction:', self, self.ID_CHANGE_COLUMNS)
        x_spinner.setRange(2, sys.maxint)
        x_spinner.setValue(default_num_unit_cells_x)
        y_spinner = AFXSpinner(num_unit_cells_frame, 3, '     Y-direction:', self, self.ID_CHANGE_ROWS)
        y_spinner.setRange(2, sys.maxint)
        y_spinner.setValue(default_num_unit_cells_y)
        
        FXLabel(structure_map_frame, 'Enter the structure map.', pb=0)
        
        structure_map_table_frame = FXVerticalFrame(structure_map_frame, FRAME_SUNKEN|FRAME_THICK)
        structure_map_table = AFXTable(structure_map_table_frame, 6,24, default_num_unit_cells_y+1,default_num_unit_cells_x+1,
                                opts=AFXTABLE_EDITABLE|AFXTABLE_EXTENDED_SELECT,
                                tgt=structure_map_target)
        self.structure_map_table = structure_map_table
        structure_map_table.setLeadingRows(1)
        structure_map_table.setLeadingColumns(1)
        structure_map_table.showVerticalGrid(True)
        structure_map_table.showHorizontalGrid(True)
        structure_map_table.setDefaultType(AFXTable.INT)
        structure_map_table.setDefaultJustify(AFXTable.CENTER)
        structure_map_table.setPopupOptions(
            AFXTable.POPUP_CUT|AFXTable.POPUP_COPY|
            AFXTable.POPUP_PASTE|AFXTable.POPUP_INSERT_ROW|
            AFXTable.POPUP_DELETE_ROW|AFXTable.POPUP_CLEAR_CONTENTS)
        for i in range( 1, structure_map_table.getNumColumns() ):
            structure_map_table.setColumnWidthInChars(i, 3)
        structure_map_table.setDefaultColumnWidth(structure_map_table.getColumnWidth(1))
        for i in range( 1, structure_map_table.getNumRows() ):
            structure_map_table.setRowHeight(i, structure_map_table.getColumnWidth(1))
        structure_map_table.setDefaultRowHeight(structure_map_table.getColumnWidth(1))
        
        AFXNote(structure_map_frame,
                'Each cell in this table represents a unit cell in the structure selected using\n' +
                'the integer ID assigned to it in the above table. An ID of zero denotes empty space.', NOTE_INFORMATION)
        
        if   param_input_mode == 'Uniform (Single)':
            batch_params_table_frame.hide()
            structure_map_frame.hide()
            h_separator.hide()
        elif param_input_mode == 'Uniform (Batch)':
            single_params_table_frame.hide()
            structure_map_frame.hide()
            h_separator.hide()
        elif param_input_mode == 'Non-Uniform':
            single_params_table_frame.hide()
        else:
            raise ValueError('Unexpected value for param_input_mode. This should not happen.')
    #
    
    def update_structure_map_table(self, sender, sel, ptr):
        """Increase or decrease size of structure_map_table."""
        sender_value = sender.getValue() + 1 #Because of the leading row/column.
        if   SELID(sel) == self.ID_CHANGE_COLUMNS:
            self.structure_map_table.setTableSize(self.structure_map_table.getNumRows(), sender_value, True)
        elif SELID(sel) == self.ID_CHANGE_ROWS:
            self.structure_map_table.setTableSize(sender_value, self.structure_map_table.getNumColumns(), True)
        else:
            raise ValueError("Invalid text:'%s'. This should not have happened. "%sender_text)
        return 1
    
    def clicked_ok(self, sender, sel, ptr):
        """Called if the OK button is pressed."""
        #TODO: show error if numrows is zero, and empty cells.
        
        # Sync table keywords so they can be reverted later
        # and change the information values on the main dialog box.
        single_params_table_target = self.single_params_table.getTarget()
        batch_params_table_target  = self.batch_params_table.getTarget()
        structure_map_target       = self.structure_map_table.getTarget()
        
        if   self.param_input_mode == 'Uniform (Single)':
            single_params_table_target.syncPreviousValue()
        
        elif self.param_input_mode == 'Uniform (Batch)':
            batch_params_table_target.syncPreviousValue()
            self.form.main_dialogbox.batch_num_analysis.setText(
                str( batch_params_table_target.getNumRows() )
                )
        
        elif self.param_input_mode == 'Non-Uniform':
            batch_params_table_target.syncPreviousValue()
            structure_map_target.syncPreviousValue()
            self.form.main_dialogbox.nonuniform_structure_size.setText(
                str( max([structure_map_target.getNumColumns(row)\
                          for row in range(structure_map_target.getNumRows()) ]+[0]) )
                 + ' by ' +
                str( self.structure_map_table.getTarget().getNumRows() )
                )    
            self.form.main_dialogbox.nonuniform_num_unit_cells.setText(
                str( batch_params_table_target.getNumRows() ) 
                )
        
        else:
            raise ValueError('Unexpected value for self.param_input_mode.' +
                             'This should have been caught in the constructor.')
        
        self.form.handle(self, MKUINT(self.form.ID_GET_NEXT, SEL_COMMAND), None)
        return 1
    
    def clicked_cancel(self, sender, sel, ptr):
        """Called if the Cancel button is pressed."""
        
        # Return keywords to their previous values.
        try:
            self.single_params_table.getTarget().setValueToPrevious()
            self.batch_params_table.getTarget().setValueToPrevious()
            if self.structure_map_table.getTarget() is not None:
                self.structure_map_table.getTarget().setValueToPrevious()
        except AttributeError:
            pass
        self.form.handle(self, MKUINT(self.form.ID_GET_NEXT, SEL_COMMAND), None)
        return 1