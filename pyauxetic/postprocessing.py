"""postprocessing"""
#TODO TODO: doc. add to sphinx.
import sys
import os
import logging
import numpy as np

from abaqusConstants import *  # noqa: F403 # Consider removing

from . import __version__

logger = logging.getLogger(__name__)

_output_table_labels = ('Inc', 'Time',
                        'U_ld', 'U_td_mean', 'U_td_midpoint',
                        'strain_ld', 'strain_td_mean', 'strain_td_midpoint',
                        'poisson_midpoint', 'poisson_mean')
_single_output_fmt   = ('%d','%.2f',
                        '%.8f','%.8f','%.8f','%.8f','%.8f','%.8f','%.8f','%.8f')

def get_numerical_output(obj, odb):
    
    logger.info('Calculating the numerical output.')
    load_dir  = obj.loading_direction
    trans_dir = obj.transverse_direction
    # TODO: Make sure there is only one step and instance.
    instance = odb.rootAssembly.instances[ obj.part_main_instance.name ]
    step = odb.steps.values()[0]
    
    # Retrieve the sets.
    logger.debug('Retrieving the sets.')
    ld_edge_sets  = (instance.nodeSets['LD-EDGE-1'],
                     instance.nodeSets['LD-EDGE-2'])
    td_edge_sets  = (instance.nodeSets['TD-EDGE-1'],
                     instance.nodeSets['TD-EDGE-2'])
    midpoint_sets = (instance.nodeSets['MID-VERTICE-1'],
                     instance.nodeSets['MID-VERTICE-2'])
    
    frameId            = []
    frameValue         = []
    ld_disp            = []
    td_disp_mean       = []
    td_disp_midpoint   = []
    ld_strain          = []
    td_strain_mean     = []
    td_strain_midpoint = []
    poisson_mean       = []
    poisson_midpoint   = []
    
    # Get the undeformed lengths for calculating strains.
    ld_dist_0 = ( ld_edge_sets[1].nodes[0].coordinates[load_dir] -
                  ld_edge_sets[0].nodes[0].coordinates[load_dir] )
    midpoint_dist_0 = ( midpoint_sets[1].nodes[0].coordinates[trans_dir] -
                        midpoint_sets[0].nodes[0].coordinates[trans_dir] )
    mean_dist_0 = ( td_edge_sets[1].nodes[0].coordinates[trans_dir] -
                    td_edge_sets[0].nodes[0].coordinates[trans_dir] )
    logger.debug('Calculated the undeformed lengths for calculating strains.')
    
    for frame in step.frames:
        frameId.append(frame.frameId)
        frameValue.append(frame.frameValue)
        u_output = frame.fieldOutputs['U']
        # Get displacement of the reference points (loading direction).
        ld_disp.append(
                u_output.getSubset(region=ld_edge_sets[1]).values[0].data[load_dir] -
                u_output.getSubset(region=ld_edge_sets[0]).values[0].data[load_dir]
                      )
        # Get displacement of the midpoints (transverse direction).
        td_disp_midpoint.append(
                u_output.getSubset(region=midpoint_sets[1]).values[0].data[trans_dir] -
                u_output.getSubset(region=midpoint_sets[0]).values[0].data[trans_dir]
                               )
        # Get mean displacement of the transverse edge. (transverse direction).
        edge1_disp = [i.data[trans_dir] for i in u_output.getSubset(region=td_edge_sets[0]).values]
        edge1_disp_mean = np.mean(edge1_disp)
        edge2_disp = [i.data[trans_dir] for i in u_output.getSubset(region=td_edge_sets[1]).values]
        edge2_disp_mean = np.mean(edge2_disp)
        td_disp_mean.append( edge2_disp_mean - edge1_disp_mean )
        
        # Calculate strains.
        if frame.incrementNumber == 0:
            ld_strain.append(0)
            td_strain_mean.append(0)
            td_strain_midpoint.append(0)
            poisson_mean.append(0)
            poisson_midpoint.append(0)
        else:
            ld_strain.append( (ld_disp[-1] - ld_disp[-2]) / ld_dist_0 )
            td_strain_midpoint.append(
                (td_disp_midpoint[-1] - td_disp_midpoint[-2]) / midpoint_dist_0 )
            td_strain_mean.append( (td_disp_mean[-1] - td_disp_mean[-2]) / mean_dist_0 )
            poisson_midpoint.append( -1.0 * td_strain_midpoint[-1] / ld_strain[-1] )
            poisson_mean.append(     -1.0 * td_strain_mean[-1]     / ld_strain[-1] )
        logger.debug('Calculated the output data for frame %i (t=%.2f).',
                     frameId[-1], frameValue[-1])
    
    # Assemble the lists to an array.
    logger.debug('Assembling frame output data into a table.')
    output_table = np.column_stack(
                        (frameId, frameValue,
                         ld_disp, td_disp_mean, td_disp_midpoint,
                         ld_strain, td_strain_mean, td_strain_midpoint,
                         poisson_mean, poisson_midpoint) )
    
    logger.info('Calculated the numerical output.')
    return output_table
#

def write_single_numerical_output(output_table, structure_name, folder_path):
    with open(os.path.join(folder_path, structure_name+' results.csv') ,'w') as file:
        file.write('Modeling and post-processing done by PyAuxetic v0.1.0.\n')
        #TODO: add model info.
        file.write( ', '.join(_output_table_labels) + '\n' )
        np.savetxt(fname=file, X=output_table, fmt=_single_output_fmt,
                   delimiter=', ', newline='\n')
    logger.info('Exported the the numerical output for structure %s.', structure_name)
#

def write_batch_numerical_output(time_value, unit_cell_params_list,
                                 structure_names, analysis_ids,
                                 results_folder_paths, folder_path):
    # TODO: doc. interpolate for time_value.
    
    logger.info('Assembling results of multiple analysis at t=%.2f.', time_value)
    # Read the results of individual analyses.
    results_tables = []
    logger.debug('Reading numerical output of the structures.')
    for i in range(len(structure_names)):
        with open(os.path.join(results_folder_paths[i], structure_names[i]+' results.csv'),
                  'r') as file:
            results_tables.append( 
                np.loadtxt(fname=file, skiprows=2, delimiter=',') )
        logger.debug('Read numerical output of structure %s.', structure_names[i])
    
    # Find the target rows based on the given model time.
    target_rows = []
    for table in results_tables:
        row_index = np.where( table[:,1] == time_value)
        target_rows.append( table[row_index] )
    
    # Compile the target rows.
    row_list = []
    for i in range( len(unit_cell_params_list) ):
        row_list.append(
            np.hstack((analysis_ids[i], unit_cell_params_list[i][1:], target_rows[i][0][2:].T)) )
    batch_output_table = np.vstack(row_list)
    logger.debug('Compiled numerical output of the structures into one table.')
    
    # Write batch_output_table to file.
    unit_cell_params_list_fields = unit_cell_params_list[0]._fields[1:]
    fmt = ('%i',) + ('%f',)*len(unit_cell_params_list_fields) + _single_output_fmt[2:]
    with open(os.path.join(folder_path, 'batch results.csv') ,'w') as file:
        file.write('Modeling and post-processing done by PyAuxetic %s\n'%__version__)
        file.write('Results of batch analysis.\n')
        file.write('Model Time = %.2f.\n'%time_value)
        file.write(
            ', '.join( ('Run #',)+unit_cell_params_list_fields+_output_table_labels[2:] ) + '\n')
        np.savetxt(fname=file, X=batch_output_table, fmt=fmt, delimiter=', ', newline='\n')
    logger.debug('Compiled numerical output of the structures into one table.')
    logger.info('Exported results of multiple analysis at t=%.2f.', time_value)
#

def export_part_stl(obj, folder_path):
    #TODO: doc
    
    #Seems to only work in part, assembly, and mesh. the part must be in focus.
    #Not meant to be front facing. use export_structure instead.
    sys.path.append(r'c:/SIMULIA/CAE/2017/win_b64/code/python2.7/lib/abaqus_plugins/stlExport')
    import stlExport_kernel
    
    # The abaqus module cannot be imported in the GUI code,
    # so only import it when running.
    from abaqus import session
    
    session.viewports.values()[0].setValues(displayedObject=obj.part_3dprint)
    stlExport_kernel.STLExport(moduleName='Part', 
        stlFileName=os.path.join(folder_path, obj.name + '.stl'),
        stlFileType='ASCII')
    logger.debug('Exported the part in the STL format.')
#