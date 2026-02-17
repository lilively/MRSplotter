from status import update_status
import matplotlib.pyplot as plt
from numpy import mean, std
from os import path, makedirs
from conflict_handling import sanitize_filename, sort_numbers
from plot_settings import add_vertical_line_with_text, apply_common_plot_settings, calculate_grid_dimensions
def create_subplot(output_directory, xaxis, dataTable, include_mean, include_sdev, 
                   plot_individual_plots, add_vertical_lines, ppm_list_vertical, selected_color, ppm_range, 
                   y_limits=None, export_figure=False, save_subplot=False, canvas_width=None, 
                   canvas_height=None, dpi=None, statusbar=None, fig=None,  legend_visible=False,
                   use_auto_grid=True, grid_rows=2, grid_cols=2):
    """
    Create subplots using pre-loaded data
    
    Parameters:
    output_directory (str): Directory to save outputs
    xaxis (array): Pre-loaded x-axis values
    dataTable (DataFrame): Pre-loaded data table with all spectra
    include_mean (bool): Whether to include mean lines
    include_sdev (bool): Whether to include standard deviation
    plot_individual_plots (bool): Whether to plot individual spectra
    add_vertical_lines (bool): Whether to add vertical reference lines
    ppm_list_vertical(list): PPM values for location of vertical lines
    y_limits (list): Generated from filtered dataTable
    selected_color (dict or str): Color map for tissue types or a single color
    ppm_range (list): PPM range to plot
    export_figure (bool): Whether to export the overall figure
    save_subplot (bool): Whether to save individual subplots as separate figures
    canvas_width (int, optional): Width in pixels for the canvas
    canvas_height (int, optional): Height in pixels for the canvas
    dpi (int, optional): DPI for saved figures
    
    Returns:
    Figure: The matplotlib figure object
    """



    # Get the tissue types from the data table
    all_tissue_types = sorted(dataTable['TissueType'].unique(), key=sort_numbers)
    
    # Filter to only include tissue types that have a color in the selected_color dictionary
    if isinstance(selected_color, dict):
        selected_tissue_types = [tissue for tissue in all_tissue_types if tissue in selected_color]
    else:
        selected_tissue_types = all_tissue_types

    #☻selected_tissue_types = ['MEN-1', 'MEN-2', '***']
    # If no tissue types selected, return None
    if len(selected_tissue_types) == 0:
        if statusbar:
            update_status(statusbar, "No tissue types selected for plotting")
        return None

    # Debug info
    #if statusbar:
        #update_status(statusbar, f"Creating subplot for {len(selected_tissue_types)} tissue types")
    
    # # Create sanitized tissue names dictionary for filenames
    # sanitized_tissues = {tissue: sanitize_filename(tissue) for tissue in selected_tissue_types}
    
    options = {
        'mean': include_mean,
        'sdev': include_sdev, 
        'each_spectra': plot_individual_plots,
        'added_lines': add_vertical_lines,
        'legend': legend_visible
    }

    # Base name with tissue count
    parts = ['Subplot', str(len(selected_tissue_types))]

    # Add enabled options to parts using list comprehension
    parts.extend([key for key, value in options.items() if value])

    # Join with underscores and add extension
    filename = '_'.join(parts) + '.png'
    outPath = path.join(output_directory, filename)

    # Calculate global y-limits if not provided
    if y_limits is None:
        from global_intensities import calculate_y_limit
        global_minIntensity, global_maxIntensity = calculate_y_limit(dataTable, not plot_individual_plots, include_sdev)
    else:
        global_minIntensity, global_maxIntensity = y_limits

    # Calculate number of rows and columns
    num_tissue_types = len(selected_tissue_types)

    if not use_auto_grid:
        num_cols, num_rows = grid_cols, grid_rows
    else:
        # Use automatic grid calculation
        num_cols, num_rows = calculate_grid_dimensions(num_tissue_types)
    
   
    #num_cols, num_rows  = calculate_grid_dimensions(num_tissue_types)
    
    
    # Debug info
    if statusbar:
        update_status(statusbar, f"Grid: {num_rows}×{num_cols}, PPM range: {ppm_range}")

    if not include_mean and not plot_individual_plots:
        # Create at least one subplot to display a message
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "Please select Mean or Individual Spectra to display data", 
                horizontalalignment='center', 
                verticalalignment='center',
                transform=ax.transAxes)
        apply_common_plot_settings(global_minIntensity, global_maxIntensity,  legend_visible,label_length=num_tissue_types, ppm_range=ppm_range, ax=ax)
        return fig
    
    # Calculate figure size based on canvas dimensions if provided
    if canvas_width is not None and canvas_height is not None and dpi is not None:
        # Convert pixels to inches for matplotlib
        width_inches = canvas_width / dpi
        height_inches = canvas_height / dpi
        # Create figure with size based on canvas dimensions
        if fig is None:
            fig = plt.figure(figsize=(width_inches, height_inches), dpi=dpi)
        else:
            fig.clear()
            
        # # Debug info
        # if statusbar:
        #     update_status(statusbar, f"Canvas: {width_inches:.1f}×{height_inches:.1f} inches at {dpi} DPI")
    else:
        # Use default scaling based on number of subplots
        fig = plt.figure(figsize=(5*num_cols, 4*num_rows))

    # Iterate through tissue types
    for idx, elem in enumerate(selected_tissue_types, 1):
        # Create subplot
        ax = plt.subplot(num_rows, num_cols, idx)
        plt.subplots_adjust(bottom=0.2)  # Adjust this value as needed
        
        # Get color for current tissue type from color map
        if isinstance(selected_color, dict) and elem in selected_color:
            # If it's a color map and this tissue has a specific color
            color_current = selected_color[elem]
        elif isinstance(selected_color, list) and len(selected_color) > 0:
            # Use first color from list if available
            color_current = selected_color[0]
        else:
            # Default color if not found in map or if selected_color is a string
            color_current = selected_color if isinstance(selected_color, str) else '#000000'
            
        # Filter data for current tissue type
        filtered = dataTable[dataTable['TissueType'] == elem]
        num_spectra = len(filtered)

        # Get PPM columns sorted numerically
        ppm_cols = sorted(
            [col for col in filtered.columns if col.startswith('PPM_')],
            key=lambda c: float(c.split('_')[1])
        )

        # Prepare data for mean and standard deviation
        case_intensities = []

        # Plot individual spectra (iterate per row to handle multivoxel IDs correctly)
        if plot_individual_plots:
            for row_idx, row in filtered.iterrows():
                case_intensity_array = row[ppm_cols].values.astype(float)
                case_intensities.append(case_intensity_array)
                ax.plot(xaxis, case_intensity_array[:len(xaxis)], color=color_current, linewidth=1, clip_on=True)
        else:
            # Collect intensities for mean and std
            for row_idx, row in filtered.iterrows():
                case_intensity_array = row[ppm_cols].values.astype(float)
                case_intensities.append(case_intensity_array)
   
        # Plot mean and standard deviation if requested
        if include_mean and case_intensities:
            mean_intensity = mean(case_intensities, axis=0)
       
            # Only darken color if plotting individual cases
            if plot_individual_plots:
                # Darken the color for the mean line
                mean_color = tuple(max(0, c * 0.5) for c in plt.cm.colors.to_rgb(color_current))
            else:
                mean_color = color_current
       
            # Plot mean line
            ax.plot(xaxis, mean_intensity, color=mean_color, linewidth=2, label='Mean', clip_on=True)

            # Plot standard deviation if requested
            if include_sdev:
                std_intensity = std(case_intensities, axis=0)
                ax.fill_between(xaxis,
                             mean_intensity - std_intensity,
                             mean_intensity + std_intensity,
                             color=mean_color,
                             alpha=0.2,
                             label='±σ')
    

        
        # Add vertical reference lines if requested
        if add_vertical_lines:
            for i, item in enumerate(ppm_list_vertical):
                add_vertical_line_with_text(ax, item, float(global_maxIntensity), str(item))

        # Add title
        ax.set_title(f'{elem} n={num_spectra}')
    
        # Configure legend handles
        legend_handles = []
    
        # Add mean to legend
        if include_mean and case_intensities:
            legend_handles.append(
                plt.Line2D([0], [0], color=mean_color, lw=2, label='Mean')
            )
        
            # Add std dev if included
            if include_sdev:
                legend_handles.append(
                    plt.Rectangle((0,0), 0.5, 0.5, 
                                 color=mean_color, 
                                 alpha=0.2, label='±σ')
                )

        # Add legend if there are handles
        if legend_handles :
            ax.legend(handles=legend_handles, loc='best')
        
        # Apply common plot settings - ensure same x-axis range for all plots
        apply_common_plot_settings(global_minIntensity, global_maxIntensity, ppm_range, legend_visible, ax=ax, label_length=num_tissue_types)

        # Save individual subplot if requested
        if output_directory and save_subplot:
            try:
                # Create sanitized filename
                sanitized_elem = sanitize_filename(elem)
                subplot_filename = f"{sanitized_elem}-{filename}"

                outPath_subplot = path.join(output_directory, subplot_filename)
                
                # Create new figure for the individual plot
                fig_single = plt.figure(figsize=(10, 6))
                ax_single = fig_single.add_subplot(111)
                
                # Plot the exact same data as in the main subplot
                # Plot individual cases if enabled
                if plot_individual_plots:
                    for case_intensity_array in case_intensities:
                        ax_single.plot(xaxis, case_intensity_array, color=color_current, linewidth=1, alpha=0.5, clip_on=True)
                
                # Plot mean and standard deviation if requested
                if include_mean and case_intensities:
                    mean_intensity = mean(case_intensities, axis=0)
                    
                    # Use same color logic as in main plot
                    if plot_individual_plots:
                        mean_color = tuple(max(0, c * 0.5) for c in plt.cm.colors.to_rgb(color_current))
                    else:
                        mean_color = color_current
                    
                    # Plot mean line
                    ax_single.plot(xaxis, mean_intensity, color=mean_color, linewidth=2, label='Mean', clip_on=True)
                    
                    # Plot standard deviation if requested
                    if include_sdev:
                        std_intensity = std(case_intensities, axis=0)
                        ax_single.fill_between(xaxis,
                                         mean_intensity - std_intensity,
                                         mean_intensity + std_intensity,
                                         color=mean_color,
                                         alpha=0.2,
                                         label='± Std Dev')
                        

                        
                for i, item in enumerate(ppm_list_vertical):
                    add_vertical_line_with_text(ax_single, item, float(global_maxIntensity), str(item))
                
               
                
                # Add vertical reference lines if requested
                
                
                # Add title
                ax_single.set_title(f'{elem} n={num_spectra}')
                
                # Add legend if needed
                if legend_handles:
                    ax_single.legend(handles=legend_handles, loc='best')

                 #    Apply common plot settings - ensure same x-axis range for all plots
                apply_common_plot_settings(global_minIntensity, global_maxIntensity, ppm_range, legend_visible, label_length=num_tissue_types, ax=ax_single)
                
                # Save the individual subplot
                fig_single.tight_layout()
                fig_single.savefig(outPath_subplot, dpi=dpi)
                plt.close(fig_single)  # Close to free memory
                
                # Update status bar if available
                
                update_status(statusbar, f'Saved plot for {elem} as {subplot_filename}')

            except Exception as e:
                update_status(statusbar, f'Error saving subplot for {elem}: {str(e)}')


    try:
        fig.tight_layout()
    except:
        pass 
    
    # Save overall figure if requested
    if output_directory and export_figure:
        try:
            # Ensure output directory exists
            makedirs(output_directory, exist_ok=True)
            
            # Save the figure
            plt.savefig(outPath, dpi=dpi)
            
            
            update_status(statusbar, f'Saved combined plot as {filename}')
        except Exception as e:
            update_status(statusbar, f'Error saving combined plot: {str(e)}')


    return fig

