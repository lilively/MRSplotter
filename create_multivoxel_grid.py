

from plot_settings import add_vertical_line_with_text, apply_common_plot_settingsMV

from matplotlib import path, pyplot as plt
from matplotlib.gridspec import GridSpec
from determine_type_and_load import read_files
from os import path, makedirs, listdir
from status import update_status
from conflict_handling import sort_numbers
from numpy import isnan
from pandas import notna
from os import path



def get_row_data(dataTable, x_pos, y_pos, case_id, id_mode='xml'):
    """Get intensity data for specific x,y position"""
    x_match = dataTable['x_pos'].astype(float).astype(int) == int(x_pos)
    y_match = dataTable['y_pos'].astype(float).astype(int) == int(y_pos)
    if case_id is not None:
        if id_mode == 'xml':
            id_match = dataTable['ID'].str.startswith(case_id + '_X_')
        else:
            id_match = dataTable['ID'] == case_id
        mask = x_match & y_match & id_match
    else:
        mask = x_match & y_match
    filtered_data = dataTable[mask]

    if filtered_data.empty:
        return None, None
    
    # Get PPM columns (intensity data), sorted numerically
    ppm_columns = sorted(
        [col for col in filtered_data.columns if col.startswith('PPM_')],
        key=lambda c: float(c.split('_')[1]), reverse=True
    )
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
                   use_auto_grid=True, grid_rows=2, grid_cols=2,
                   global_x_range=None, global_y_range=None):
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
        

    # Use global ranges if provided (for consistent grid sizes across cases),
    # otherwise derive from this case's data
    if global_x_range is not None:
        xmin, xmax = global_x_range
    else:
        x_values = sorted([int(float(x)) for x in dataTable['x_pos'].unique()])
        xmin, xmax = min(x_values), max(x_values)

    if global_y_range is not None:
        ymin, ymax = global_y_range
    else:
        y_values = sorted([int(float(y)) for y in dataTable['y_pos'].unique()])
        ymin, ymax = min(y_values), max(y_values)

    xlen = xmax - xmin + 1
    ylen = ymax - ymin + 1
    n = xlen * ylen

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
        # Use grid dimensions (xlen/ylen) for aspect ratio so all cases
        # produce the same figure size regardless of which cells have data
        base_size = 12
        aspect_ratio = xlen / ylen
        if aspect_ratio >= 1:
            figsize = (base_size, base_size / aspect_ratio)
        else:
            figsize = (base_size * aspect_ratio, base_size)
    
    # Track if exported any figures
    exported_count = 0

    all_tissue_types = sorted(dataTable['TissueType'].unique(), key=sort_numbers)

    # Extract case IDs: XML IDs have format "caseID_X_{x}_Y_{y}", CSV IDs may not
    extracted = dataTable['ID'].str.extract(r'^(.+?)_X_')
    has_xml_ids = extracted.iloc[:, 0].notna().any()
    if has_xml_ids:
        case_ids = extracted.iloc[:, 0].dropna().unique().tolist()
        id_mode = 'xml'
    else:
        case_ids = [c for c in dataTable['ID'].unique() if notna(c)]
        id_mode = 'csv'

    for case in case_ids:
        if fig is None:
            fig = plt.figure(figsize=figsize)
        else:
            fig.clear()
        filename = str(case) if case is not None else 'multivoxel'
        # Sanitize for filesystem
        for ch in '<>:"/\\|?*':
            filename = filename.replace(ch, '_')
        if legend_visible and filename != 'multivoxel':
            fig.suptitle(filename, fontweight='bold', fontsize=12, y=0.98)

        # Grab one valid spectrum to use as invisible placeholder in empty cells
        ppm_columns = sorted(
            [col for col in dataTable.columns if col.startswith('PPM_')],
            key=lambda c: float(c.split('_')[1]), reverse=True
        )
    
        # Create grid layout
        gs = GridSpec(ylen, xlen, figure=fig, hspace=0.0, wspace=0.0)
        fig.subplots_adjust(top=0.95)
        counter = 0
        
        for y_idx, y_pos in enumerate(range(ymin, ymax+1)): 
            for x_idx, x_pos in enumerate(range(xmin, xmax+1)):
                ax = fig.add_subplot(gs[y_idx, x_idx])

                
                # Get intensity data for this position
                result = get_row_data(dataTable, x_pos, y_pos, case, id_mode)
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
                    
                    # Adjust font size and label position based on total subplots
                    total_subplots = xlen * ylen
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

                    # Plot the spectrum (limit to xaxis length in case of column mismatch)
                    ax.plot(xaxis, intensity_data[:len(xaxis)], color=color_current, linewidth=LW)
                    apply_common_plot_settingsMV(global_minIntensity, global_maxIntensity, ppm_range, legend_visible=legend_visible, ax=ax)

                    # Add coordinate label
                    if legend_visible:
                        coord_label = f"{x_pos}-{y_pos}"
                        ax.text(x_al, y_al, coord_label, transform=ax.transAxes,
                        verticalalignment='top', fontweight='bold', fontsize=font_size)

                    fileending = ''
                     # Add vertical reference lines if requested
                    if add_vertical_lines:
                        ppm_str = ", ".join(str(p) for p in ppm_list_vertical)
                        update_status(statusbar, f"Adding vertical lines at {ppm_str} ppm")
                        for i, item in enumerate(ppm_list_vertical):
                            add_vertical_line_with_text(ax, item, float(global_maxIntensity), str(item))
                            fileending = 'vertical_'
                    else:
                        fileending=''

                    


                    
                    # ax.text(0.05, 0.85, coord_label, transform=ax.transAxes, 
                    #     verticalalignment='bottom', fontweight='bold', fontsize=8)
                else:
                    # Empty cell — apply same axis limits for consistent sizing
                    
                    #ax.plot(xaxis, xaxis, color="#FFFFFF")
                    apply_common_plot_settingsMV(global_minIntensity, global_maxIntensity, ppm_range, legend_visible=legend_visible, ax=ax)
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
                filename = f"{filename}_{fileending}grid.png"
                outPath = path.join(output_directory, filename)
                
                # Update status bar before saving
                update_status(statusbar, f"Saving {filename}...")

                # Save the figure
                fig.savefig(outPath, dpi=dpi, bbox_inches='tight', pad_inches=0)

                exported_count += 1

                update_status(statusbar, f"Successfully saved {filename} to {output_directory}")
            except Exception as e:
                update_status(statusbar,f'Error saving multivoxel plot: {str(e)}')
        return fig


def export_mv_grid(output_directory, xaxis, dataTable, include_mean, include_sdev,
                   plot_individual_plots, add_vertical_lines, ppm_list_vertical, selected_color, ppm_range,
                   legend_visible=False,
                   y_limits=None, export_figure=True, dpi=300, statusbar=None):
    """
    Export multivoxel grid plots for all cases in the loaded dataTable
    """
    
    # Check if this is multivoxel data
    if 'x_pos' not in dataTable.columns or 'y_pos' not in dataTable.columns:
        if statusbar:
            update_status(statusbar, "Data is not suitable for multivoxel grid export")
        return
    
    # Compute global x/y range across ALL cases for consistent grid sizes
    all_x = [int(float(x)) for x in dataTable['x_pos'].unique()]
    all_y = [int(float(y)) for y in dataTable['y_pos'].unique()]
    global_x_range = (min(all_x), max(all_x))
    global_y_range = (min(all_y), max(all_y))

    # Get all unique case IDs from the loaded data
    extracted = dataTable['ID'].str.extract(r'^(.+?)_X_')
    has_xml_ids = extracted.iloc[:, 0].notna().any()
    if has_xml_ids:
        case_ids = [c for c in extracted.iloc[:, 0].unique() if notna(c)]
        id_mode = 'xml'
    else:
        # CSV: each unique ID is one case
        case_ids = [c for c in dataTable['ID'].unique() if notna(c)]
        id_mode = 'csv'

    for case_id in case_ids:
        try:
            # Filter data for this specific case
            if id_mode == 'xml':
                case_data = dataTable[dataTable['ID'].str.startswith(case_id + '_X_')].copy()
            else:
                case_data = dataTable[dataTable['ID'] == case_id].copy()

            if case_data.empty:
                continue

            update_status(statusbar, f"Exporting {case_id or 'multivoxel'}...")

            # Create the plot for this case with global grid dimensions
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
                legend_visible=legend_visible,
                fig=None,
                global_x_range=global_x_range,
                global_y_range=global_y_range
            )
            
            # Close the figure to free memory
            if fig:
                plt.close(fig)
                
            update_status(statusbar, f"Exported {case_id or 'multivoxel'} to {output_directory}")

        except Exception as e:
            if statusbar:
                update_status(statusbar, f"Error exporting {case_id or 'multivoxel'}: {str(e)}")
    




