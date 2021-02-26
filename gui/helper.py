"""Helper functions for the plugin GUI."""

import custom_input_forms


def replace_combo_items(combo_box, new_list, show_empty=True, show_all=True):
    """Replace items in a combo box with a new list of items."""
    
    combo_box.clearItems()
    for i in new_list:
        combo_box.appendItem(i)
    if show_all:
        combo_box.setMaxVisible(len(new_list))
        combo_box.setNumVisible(len(new_list))
    if show_empty:
        combo_box.setText('')


def return_param_dialogbox(self, dialogbox, new_param_class,
                           modeling_mode, border_size):
    
    if   dialogbox is None:
        return custom_input_forms.StructureParamsDB(self, new_param_class,
                                                    modeling_mode, border_size)
    elif dialogbox.param_obj_class != new_param_class:
        # Delete the previous AFXTableKeyword so the table is empty.
        if   modeling_mode == 'Uniform (Single)':
            self.uniform_structure_params_table_kw.setValueToDefault(ignoreUnspecified=True)
        elif modeling_mode == 'Uniform (Batch)':
            self.batch_structure_params_table_kw.setValueToDefault(ignoreUnspecified=True)
        elif modeling_mode == 'Non-Uniform':
            self.nonuniform_structure_params_table_kw.setValueToDefault(ignoreUnspecified=True)
        else:
            raise ValueError('Unexpected value for modeling_mode.')
        return custom_input_forms.StructureParamsDB(self, new_param_class,
                                                    modeling_mode, border_size)
    else:
        return dialogbox
