import matplotlib.pyplot as plt
from os import path
from plot_settings import add_vertical_line_with_text, apply_common_plot_settings
from status import update_status

def create_individual_plots(output_directory, xaxis, dataTable, include_mean, include_sdev, 
                           add_vertical_lines, ppm_list_vertical,
                           selected_color, ppm_range, export_figure=True,
                           y_limits = None,  legend_visible=False,
                           canvas_width=None, canvas_height=None, dpi=None, statusbar=None):
    """
    Create individual plots for each case in each tissue type
    
    Parameters:
    output_directory (str): Directory to save outputs
    xaxis (array): Pre-loaded x-axis values
    dataTable (DataFrame): Pre-loaded data table with all spectra
    include_mean (bool): Whether to include mean lines
    include_sdev (bool): Whether to include standard deviation
    add_vertical_lines (bool): Whether to add vertical reference lines
    ppm_list_vertical(list): PPM values for location of vertical lines
    selected_color (dict): Color map for selected tissue types
    ppm_range (list): PPM range to plot
    export_figure (bool): Whether to export the figure
    y_limits (list): Generated from filtered dataTable
    canvas_width (int, optional): Width of canvas in pixels
    canvas_height (int, optional): Height of canvas in pixels
    dpi (int, optional): DPI for the figure
    statusbar (QStatusBar, optional): Status bar for displaying messages
    
    Returns:
    bool: True if successful, False otherwise
    """
    update_status(statusbar,"Starting individual plot export...")
    # Get the tissue types from the data table based on selected colors
    selected_tissue_types = list(selected_color.keys())

    if not selected_tissue_types:
        # If no tissue types are selected, return False
        return False
    
    # Calculate global y-limits
    if y_limits is None:
        from global_intensities import calculate_y_limit
        global_minIntensity, global_maxIntensity = calculate_y_limit(dataTable, False, include_sdev)
    else:
        global_minIntensity, global_maxIntensity = y_limits
    
    # Calculate figure size based on canvas dimensions if provided
    if canvas_width is not None and canvas_height is not None:
        # Convert pixels to inches for matplotlib
        width_inches = canvas_width / dpi
        height_inches = canvas_height / dpi
        figsize = (width_inches, height_inches)
    else:
        # Use default size for a single plot
        figsize = (10, 6)
    
    # Track if we exported any figures
    exported_count = 0
    
    # Plot data for each selected tissue type
    for tissue_type in selected_tissue_types:
        # Get color for current tissue type from color map
        if tissue_type in selected_color:
            color_current = selected_color[tissue_type]
        else:
            # Default color if not found in map
            color_current = '#000000'
        
        # Filter data for current tissue type
        filtered = dataTable[dataTable['TissueType'] == tissue_type]

        # Get PPM columns
        ppm_cols = sorted(
            [col for col in filtered.columns if col.startswith('PPM_')],
            key=lambda c: float(c.split('_')[1])
        )

        # Determine file ending based on options
        fileending = ''
        if add_vertical_lines:
            fileending = 'vertical'
        elif not legend_visible:
            fileending = 'legend'

        update_status(statusbar, f"Processing {len(filtered)} spectra for tissue type: {tissue_type}")

        # Iterate per row so each voxel gets its own plot
        for row_idx, row in filtered.iterrows():
            case_id = row['ID']

            # Build a unique label for the plot title and filename
            has_xy = 'x_pos' in filtered.columns and 'y_pos' in filtered.columns
            if has_xy:
                x_pos = row['x_pos']
                y_pos = row['y_pos']
                plot_label = f"{case_id}_X{x_pos}_Y{y_pos}"
            else:
                plot_label = str(case_id)

            # Create a new figure for each spectrum
            fig = plt.figure(figsize=figsize, dpi=dpi)
            ax = fig.add_subplot(111)

            case_intensity_array = row[ppm_cols].values.astype(float)

            ax.plot(
                xaxis, case_intensity_array[:len(xaxis)], color=color_current, linewidth=2, clip_on=True,
                label=f"{tissue_type}"
            )

            ax.legend(loc='best')

            # Add vertical reference lines if requested
            if add_vertical_lines:
                for i, item in enumerate(ppm_list_vertical):
                    add_vertical_line_with_text(ax, item, float(global_maxIntensity), str(item))

            # Add title
            ax.set_title(f'{plot_label} - {tissue_type}')

            apply_common_plot_settings(global_minIntensity, global_maxIntensity, ppm_range, legend_visible, ax=ax)

            # Adjust layout
            plt.tight_layout()

            # Save figure if requested
            if output_directory and export_figure:
                from conflict_handling import sanitize_filename
                sanitized_tissue = sanitize_filename(tissue_type)
                sanitized_label = sanitize_filename(plot_label)
                filename = f"{sanitized_label}_{sanitized_tissue}_{fileending}.png"
                outPath = path.join(output_directory, filename)
                try:
                    plt.savefig(outPath, dpi=dpi)

                    if statusbar:
                        update_status(statusbar,f"Saving results as {filename} to {output_directory}")
                    else:
                        print(f'Saving results as {filename} to {output_directory}')

                    exported_count += 1
                except Exception as e:
                    if statusbar:
                        update_status(statusbar,f"Error saving {filename}...")
                    else:
                        print(f"Error saving {filename}: {str(e)}")

            # Close the figure to free memory
            plt.close(fig)
    
    # Return True if we exported any figures
    return exported_count > 0

