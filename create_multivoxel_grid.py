

from plot_settings import add_vertical_line_with_text, apply_common_plot_settingsMV
from matplotlib import path, pyplot as plt
from matplotlib.gridspec import GridSpec
from determine_type_and_load import read_files
from os import path, makedirs, listdir
from status import update_status
from numpy import isnan
from pandas import notna
from os import path



def get_row_data(dataTable, x_pos, y_pos, case_id):
    """Get intensity data for specific x,y position"""
    mask = (dataTable['x_pos'] == str(x_pos)) & (dataTable['y_pos'] == str(y_pos)) & (dataTable['ID'].str.startswith(case_id + '_X_'))
    filtered_data = dataTable[mask]
    
    if filtered_data.empty:
        return None, None 
    
    # Get PPM columns (intensity data)
    ppm_columns = [col for col in filtered_data.columns if col.startswith('PPM_')]
    if not ppm_columns:
        return None, None
        
    # Get the first row's intensity data
    intensity_data = filtered_data[ppm_columns].iloc[0].values
    tissue_type = filtered_data['TissueType'].iloc[0]
    return intensity_data, tissue_type




def create_multivoxel_plot(output_directory, xaxis, dataTable, include_mean, include_sdev, 
                   plot_individual_plots, add_vertical_lines, ppm_list_vertical, selected_color, ppm_range, 
                   y_limits=None, export_figure=False, save_subplot=False, canvas_width=None, 
                   canvas_height=None, dpi=None, statusbar=None, fig=None,  legend_visible=False,
                   use_auto_grid=True, grid_rows=2, grid_cols=2):
    """
    Create a multivoxel grid plot similar to the MATLAB tiledlayout
    
    Parameters:
    -----------
    output_directory : str
        Directory to save outputs
    xaxis : array
        PPM values for x-axis
    dataTable : DataFrame
        Data table containing XaxisAttribute, YaxisAttribute, and PPM data
    ppm_range : list
        PPM range [min, max]
    export_figure : bool
        Whether to export the figure
    dpi : int
        DPI for saved figures
    statusbar : object
        Status bar for updates
    fig : matplotlib.figure.Figure
        Figure to use (if None, creates new one)
    
    Returns:
    --------
    Figure: The matplotlib figure object
    """
    if 'x_pos' not in dataTable.columns or 'y_pos' not in dataTable.columns:
        if fig is None:
            fig = plt.figure(figsize=figsize) 
        else:
            fig.clear()
            
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'This file does not contain x and y positions.\nPlease select "Subplot" or "Superimposed plot" instead.', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes)
        ax.set_xlabel("PPM")
        ax.set_ylabel("Intensity")
        return fig
        

    x_values = sorted([int(float(x)) for x in dataTable['x_pos'].unique()])
    y_values = sorted([int(float(y)) for y in dataTable['y_pos'].unique()])
    xlen = len(x_values)
    ylen = len(y_values)
    n = xlen * ylen
    
    # Get min/max for range - convert to integers
    xmin, xmax = min(x_values), max(x_values)
    ymin, ymax = min(y_values), max(y_values)

    if y_limits is None:
        from global_intensities import calculate_y_limit
        global_minIntensity, global_maxIntensity = calculate_y_limit(dataTable, False, include_sdev)
    else:
        global_minIntensity, global_maxIntensity = y_limits
    
    # if selected_color and isinstance(selected_color, dict):
    #     selected_labels = list(selected_color.keys())
    #     if 'TissueType' in dataTable.columns:
    #         dataTable = dataTable[dataTable['TissueType'].isin(selected_labels)].copy()


    # Calculate figure size based on canvas dimensions if provided
    if canvas_width is not None and canvas_height is not None:
        # Convert pixels to inches for matplotlib
        width_inches = canvas_width / dpi
        height_inches = canvas_height / dpi
        figsize = (width_inches, height_inches)
    else:
        figsize = (24, 12) 
    
    # Track if exported any figures
    exported_count = 0

    all_tissue_types = sorted(dataTable['TissueType'].unique())
    case_ids = dataTable['ID'].str.extract(r'^(.+?)_X_').iloc[:, 0].unique().tolist()

    for case in case_ids:
        if fig is None:
            fig = plt.figure(figsize=figsize)
        else:
            fig.clear()
        filename = case  
        fig.suptitle(filename, fontweight='bold', fontsize=12)
        
        # Create grid layout
        gs = GridSpec(ylen, xlen, figure=fig, hspace=0.0, wspace=0.0)
        
        counter = 0
        
        for y_idx, y_pos in enumerate(range(ymin, ymax+1)): 
            for x_idx, x_pos in enumerate(range(xmin, xmax+1)):
                ax = fig.add_subplot(gs[y_idx, x_idx])

                
                # Get intensity data for this position
                result = get_row_data(dataTable, x_pos, y_pos, case)
                if result[0] is not None:  
                    intensity_data, tissue_type = result
                else:
                    intensity_data, tissue_type = None, None

                if intensity_data is not None and len(intensity_data) > 0 and not all(isnan(intensity_data)):
                    # Valid data exists
                    if tissue_type in selected_color:
                        color_current = selected_color[tissue_type]
                    else:
                        color_current = "#000000"
                    
                    # Add coordinate label
                    coord_label = f"{x_pos}-{y_pos}"
                    total_subplots = len(x_values) * len(y_values)
                    if total_subplots > 16:
                        font_size = 6
                        x_al, y_al = 0.02, 0.98
                        LW=0.5
                    elif total_subplots > 9:
                        font_size = 7
                        x_al, y_al = 0.03, 0.92
                        LW=0.6
                    else:
                        font_size = 8
                        x_al, y_al = 0.05, 0.85
                        LW=0.9

                    # Plot the spectrum
                    ax.plot(xaxis, intensity_data, color=color_current, linewidth=LW)
                    apply_common_plot_settingsMV(global_minIntensity, global_maxIntensity, ppm_range, legend_visible=legend_visible, ax=ax)

                    fileending = ''
                     # Add vertical reference lines if requested
                    if add_vertical_lines:
                        for i, item in enumerate(ppm_list_vertical):
                            add_vertical_line_with_text(ax, item, float(global_maxIntensity), str(item))
                            fileending = 'vertical_'
                    else:
                        fileending=''

                    

                    ax.text(x_al, y_al, coord_label, transform=ax.transAxes,
                            verticalalignment='top', fontweight='bold', fontsize=font_size)
                    
                    # ax.text(0.05, 0.85, coord_label, transform=ax.transAxes, 
                    #     verticalalignment='bottom', fontweight='bold', fontsize=8)
                else:
                    # Empty plot for missing/invalid data
                    ax.text(0.5, 0.5, 'No Data', transform=ax.transAxes, 
                        horizontalalignment='center', verticalalignment='center',
                        fontsize=10, alpha=0.5)
                    
                    coord_label = f"{x_pos}-{y_pos}"
                    ax.text(0.05, 0.85, coord_label, transform=ax.transAxes, 
                        verticalalignment='bottom', fontweight='bold', 
                        fontsize=8, alpha=0.5)
                # Set axis properties
                ax.set_xticks([])
                ax.set_yticks([])

                
                
                counter += 1

        if output_directory and export_figure:
            try:
                # Ensure directory exists
                makedirs(output_directory, exist_ok=True)
                # Define output path
                filename = f"{case}_{fileending}grid.png"
                outPath = path.join(output_directory, filename)
                
                # Save the figure
                fig.savefig(outPath, dpi=dpi, bbox_inches='tight')

                # Update status bar if available
                if statusbar:
                    update_status(statusbar,f"Saving results as {filename} to {output_directory}", 5000)
                else:
                    print(f'Saving results as {filename} to {output_directory}')
                    
                exported_count += 1
    
                update_status(statusbar,f'Successfully saved multivoxel plot as {filename} to {output_directory}', 3000)
            except Exception as e:
                update_status(statusbar,f'Error saving multivoxel plot: {str(e)}', 5000)
        return fig


def export_mv_grid(output_directory, xaxis, dataTable, include_mean, include_sdev,
                   plot_individual_plots, add_vertical_lines, ppm_list_vertical, selected_color, ppm_range,
                   y_limits=None, export_figure=True, dpi=300, statusbar=None):
    """
    Export multivoxel grid plots for all cases in the loaded dataTable
    """
    
    # Check if this is multivoxel data
    if 'x_pos' not in dataTable.columns or 'y_pos' not in dataTable.columns:
        if statusbar:
            update_status(statusbar, "Data is not suitable for multivoxel grid export", 3000)
        return
    
    # Get all unique case IDs from the loaded data
    case_ids = dataTable['ID'].str.extract(r'^(.+?)_X_').iloc[:, 0].unique()
    case_ids = [c for c in case_ids if notna(c)]
    
    
    for case_id in case_ids:
        try:
            # Filter data for this specific case
            case_data = dataTable[dataTable['ID'].str.startswith(case_id + '_X_')].copy()
            
            if case_data.empty:
                continue
                
            # Create the plot for this case
            fig = create_multivoxel_plot(
                output_directory=output_directory, 
                xaxis=xaxis,
                dataTable=case_data,
                include_mean=include_mean, 
                include_sdev=include_sdev,
                plot_individual_plots=plot_individual_plots, 
                add_vertical_lines=add_vertical_lines, 
                ppm_list_vertical=ppm_list_vertical, 
                selected_color=selected_color, 
                ppm_range=ppm_range,
                y_limits=y_limits, 
                export_figure=export_figure, 
                dpi=dpi, 
                statusbar=statusbar,
                fig=None 
            )
            
            # Close the figure to free memory
            if fig:
                plt.close(fig)
                
            if statusbar:
                update_status(statusbar,f"Saving results of {case_id} to {output_directory}", 5000)
                
        except Exception as e:
            if statusbar:
                update_status(statusbar, f"Error exporting {case_id}: {str(e)}", 3000)
    




