import matplotlib.pyplot as plt
from numpy import mean, std
from os import path, makedirs
from status import update_status
from plot_settings import apply_common_plot_settings, add_vertical_line_with_text


def create_superimposed(output_directory, xaxis, dataTable, include_mean, include_sdev, plot_individual_plots, 
                        add_vertical_lines, ppm_list_vertical, selected_color, ppm_range, 
                        export_figure=False, y_limits=None, canvas_width=None, canvas_height=None,  legend_visible=False,
                        dpi=None, statusbar=None, fig=None):
    """
    Create superimposed plot using pre-loaded data
    
    Parameters:
    output_directory (str): Directory to save outputs
    xaxis (array): Pre-loaded x-axis values
    dataTable (DataFrame): Pre-loaded data table with all spectra
    include_mean (bool): Whether to include mean lines
    include_sdev (bool): Whether to include standard deviation
    plot_individual_plots (bool): Whether to plot individual spectra
    add_vertical_lines (bool): Whether to add vertical reference lines
    ppm_list_vertical(list): PPM values for location of vertical lines
    selected_color (dict): Color map for selected tissue types
    ppm_range (list): PPM range to plot
    y_limits (list): Generated from filtered dataTable
    export_figure (bool): Whether to export the figure
    canvas_width (int, optional): Width of canvas in pixels
    canvas_height (int, optional): Height of canvas in pixels
    dpi (int, optional): DPI for the figure
    statusbar (StatusBar, optional): Status bar for updates
    fig (Figure, optional): Existing matplotlib figure to use
    
    Returns:
    Figure: The matplotlib figure object
    """


    
    # Get the tissue types from the data table based on selected colors
    selected_tissue_types = list(selected_color.keys())

    
    if not selected_tissue_types:
        # If no tissue types are selected, return None
        if statusbar:
            update_status(statusbar, "No tissue types selected for superimposed plot", 3000)
        return None
    
    # Create options dictionary for filename
    options = {
        'mean': include_mean,
        'sdev': include_sdev, 
        'each_spectra': plot_individual_plots,
        'added_lines': add_vertical_lines,
        'legend': legend_visible
    }

    # Base name with tissue count
    parts = ['Superimposed', str(len(selected_tissue_types))]

    # Add enabled options to parts using list comprehension
    parts.extend([key for key, value in options.items() if value])

    # Join with underscores and add extension
    filename = '_'.join(parts) + '.png'
    
    # Ensure output directory exists if exporting
    if export_figure and output_directory:
        try:
            makedirs(output_directory, exist_ok=True)
            outPath = path.join(output_directory, filename)
            
            # Debug information
            update_status(statusbar,f"Preparing to save superimposed plot to: {outPath}", 2000)
        except Exception as e:
            update_status(statusbar,f"Error creating output directory: {str(e)}", 3000)
            return None
    
    # Calculate global y-limits
    if y_limits is None:
        try:
            from global_intensities import calculate_y_limit
            global_minIntensity, global_maxIntensity = calculate_y_limit(
                dataTable[dataTable['TissueType'].isin(selected_tissue_types)], 
                not plot_individual_plots, 
                include_sdev
            )
        except Exception as e:
            update_status(statusbar,f"Error calculating Y limits: {str(e)}", 3000)
            # Fall back to default y-limits
            global_minIntensity, global_maxIntensity = -5, 15
    else:
        global_minIntensity, global_maxIntensity = y_limits
    

    # Calculate figure size based on canvas dimensions if provided
    if canvas_width is not None and canvas_height is not None and dpi is not None:
        # Convert pixels to inches for matplotlib
        width_inches = canvas_width / dpi
        height_inches = canvas_height / dpi
        
        # Use existing figure or create new one
        if fig is None:
            fig = plt.figure(figsize=(width_inches, height_inches), dpi=dpi)
        else:
            fig.clear()
    else:
        # Use default size for a single plot if no fig provided
        if fig is None:
            fig = plt.figure(figsize=(10, 6))
            if dpi is not None:
                fig.set_dpi(dpi)
        else:
            fig.clear()
    
    # Create a single subplot
    ax = fig.add_subplot(111)


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
        num_spectra = len(filtered)

        # Skip if no data found
        if num_spectra == 0:
            update_status(statusbar,f"No cases found for tissue type: {tissue_type}", 2000)
            continue

        # Get PPM columns sorted numerically
        ppm_cols = sorted(
            [col for col in filtered.columns if col.startswith('PPM_')],
            key=lambda c: int(c.split('_')[1])
        )

        # Prepare data for mean and standard deviation
        case_intensities = []

        # Plot individual spectra (iterate per row to handle multivoxel IDs correctly)
        if plot_individual_plots:
            for i, (row_idx, row) in enumerate(filtered.iterrows()):
                case_intensity_array = row[ppm_cols].values.astype(float)
                case_intensities.append(case_intensity_array)
                line, = ax.plot(
                    xaxis, case_intensity_array[:len(xaxis)], color=color_current, linewidth=1, clip_on=False,
                    label=f"{tissue_type}" if i == 0 and not (include_mean or include_sdev) else ""
                )
        else:
            # Collect intensities for mean and std
            for row_idx, row in filtered.iterrows():
                case_intensity_array = row[ppm_cols].values.astype(float)
                case_intensities.append(case_intensity_array)
        
        # Plot mean if requested
        if include_mean and case_intensities:
            mean_intensity = mean(case_intensities, axis=0)
            
            # Determine colors based on whether individual plots are shown
            if plot_individual_plots:
                # Use darker version of current color for mean when showing individual plots
                mean_color = tuple(max(0, c * 0.5) for c in plt.cm.colors.to_rgb(color_current))
                ax.plot(xaxis, mean_intensity, color=mean_color, linewidth=2,
                    label=f"{tissue_type} (n={num_spectra})", clip_on=False)
            else:
                # Use the regular color when only showing mean
                ax.plot(xaxis, mean_intensity, color=color_current, linewidth=2,
                    label=f"{tissue_type} (n={num_spectra})", clip_on=False)
            
            # Handle standard deviation with consistent coloring
            if include_sdev:
                std_intensity = std(case_intensities, axis=0)
                # Use a color that matches the mean line's style
                fill_color = color_current if not plot_individual_plots else mean_color
                ax.fill_between(xaxis,
                        mean_intensity - std_intensity,
                        mean_intensity + std_intensity,
                        color=fill_color,
                        alpha=0.2)
    
   
    
    
    # Add vertical reference lines if requested
    if add_vertical_lines:
        for i, elem in enumerate(ppm_list_vertical):
            add_vertical_line_with_text(ax, elem, float(global_maxIntensity), str(elem))
    
    # Add title
    ax.set_title(f'Superimposed MR Spectra - {len(selected_tissue_types)} Tissue Types')
    
    # Configure legend
    if ax.get_legend_handles_labels()[0]:  # Check if there are any legend entries
        legend = ax.legend(loc='best')
        # Make legend lines thicker for better visibility
        for line in legend.get_lines():
            line.set_linewidth(2)
    
    apply_common_plot_settings(global_minIntensity, global_maxIntensity, ppm_range, legend_visible, label_length=selected_tissue_types, ax=ax)
    

    try:
        plt.tight_layout()
    except Warning:
        # Use a more flexible approach if tight_layout doesn't work
        plt.subplots_adjust(
            left=0.125,
            right=0.9,
            top=0.9,
            bottom=0.125,
            wspace=0.2,
            hspace=0.2
    )

    
    # Save figure if requested
    if output_directory and export_figure:
        try:
            # Ensure directory exists
            makedirs(output_directory, exist_ok=True)
            from conflict_handling import sanitize_filename
            # Define output path
            filename = sanitize_filename(filename)
            outPath = path.join(output_directory, filename)
            
            # Save the figure
            fig.savefig(outPath, dpi=dpi, bbox_inches='tight')
            
            update_status(statusbar,f'Successfully saved superimposed plot as {filename} to {output_directory}', 3000)
        except Exception as e:
            update_status(statusbar,f'Error saving superimposed plot: {str(e)}', 5000)

    return fig