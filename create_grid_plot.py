from status import update_status
from numpy import mean, std
from os import path, makedirs
from conflict_handling import sanitize_filename
from plot_settings import add_vertical_line_with_text, apply_common_plot_settings, calculate_grid_dimensions

def create_grid(output_directory, xaxis, dataTable, include_mean, include_sdev, 
                plot_individual_plots, add_vertical_lines, ppm_list_vertical, selected_color, ppm_range, 
                grid_rows=None, grid_cols=None, y_limits=None, export_figure=False, save_subplot=False,
                 legend_visible=False, 
                canvas_width=None, canvas_height=None, dpi=None, statusbar=None, fig=None):
    """
    Create a grid layout for multi-voxel data where position in the grid corresponds to spatial position
    
    Parameters:
    output_directory (str): Directory to save outputs
    xaxis (array): Pre-loaded x-axis values
    dataTable (DataFrame): Pre-loaded data table with all spectra
    include_mean (bool): Whether to include mean lines
    include_sdev (bool): Whether to include standard deviation
    plot_individual_plots (bool): Whether to plot individual spectra
    add_vertical_lines (bool): Whether to add vertical reference lines
    ppm_list_vertical(list): PPM values for location of vertical lines
    grid_rows (int): Number of rows in the grid
    grid_cols (int): Number of columns in the grid
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
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    
    # Check if dataTable has position information
    if 'X_Pos' not in dataTable.columns or 'Y_Pos' not in dataTable.columns:
        if statusbar:
            update_status(statusbar, "Error: Grid plot requires X_Pos and Y_Pos columns in data", 3000)
        return None
    
    # Calculate global y-limits if not provided
    if y_limits is None:
        from global_intensities import calculate_y_limit
        global_minIntensity, global_maxIntensity = calculate_y_limit(dataTable, not plot_individual_plots, include_sdev)
    else:
        global_minIntensity, global_maxIntensity = y_limits
    
    # Determine grid dimensions if not provided
    if grid_rows is None or grid_cols is None:
        # Get unique X and Y positions to determine grid size
        x_positions = sorted(dataTable['X_Pos'].unique())
        y_positions = sorted(dataTable['Y_Pos'].unique())
        grid_cols = len(x_positions)
        grid_rows = len(y_positions)
    
    if statusbar:
        update_status(statusbar, f"Creating grid with {grid_rows} rows and {grid_cols} columns", 2000)
    
    # Create position mapping for faster lookups
    position_lookup = {}
    for x_idx, x_pos in enumerate(sorted(dataTable['X_Pos'].unique())):
        for y_idx, y_pos in enumerate(sorted(dataTable['Y_Pos'].unique(), reverse=True)):  # Reversed for standard grid orientation
            position_lookup[(x_pos, y_pos)] = (y_idx, x_idx)  # Row, Col format for subplot

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
    else:
        # Use default scaling based on number of subplots
        fig = plt.figure(figsize=(5*grid_cols, 4*grid_rows))
    
    # Create GridSpec for more control over spacing
    gs = GridSpec(grid_rows, grid_cols, figure=fig, wspace=0.3, hspace=0.4)
    
    # Base name for output file
    options = {
        'mean': include_mean,
        'sdev': include_sdev, 
        'each_spectra': plot_individual_plots,
        'added_lines': add_vertical_lines
    }
    parts = ['Grid', f"{grid_rows}x{grid_cols}"]
    parts.extend([key for key, value in options.items() if value])
    filename = '_'.join(parts) + '.png'
    outPath = path.join(output_directory, filename)
    
    # Plot data for each grid position
    for x_pos in sorted(dataTable['X_Pos'].unique()):
        for y_pos in sorted(dataTable['Y_Pos'].unique(), reverse=True):
            # Get the grid position from our lookup
            if (x_pos, y_pos) in position_lookup:
                row_idx, col_idx = position_lookup[(x_pos, y_pos)]
                
                # Get data for this position
                position_data = dataTable[(dataTable['X_Pos'] == x_pos) & (dataTable['Y_Pos'] == y_pos)]
                
                # Skip if no data for this position
                if position_data.empty:
                    continue
                
                # Create subplot at this grid position
                ax = fig.add_subplot(gs[row_idx, col_idx])
                
                # Get color for current spectra
                if isinstance(selected_color, dict):
                    unique_tissues = position_data['TissueType'].unique()
                    if len(unique_tissues) == 1 and unique_tissues[0] in selected_color:
                        color_current = selected_color[unique_tissues[0]]
                    else:
                        # Use first available color
                        color_current = next(iter(selected_color.values())) if selected_color else '#000000'
                else:
                    # Default color if not a dict
                    color_current = selected_color if isinstance(selected_color, str) else '#000000'
                
                # Prepare data for mean and standard deviation
                case_intensities = []
                cases_selected = position_data['ID'].values.tolist()
                
                # Plot individual cases or collect intensities
                if plot_individual_plots:
                    for case in cases_selected:
                        case_intensity = position_data.loc[position_data['ID'] == case]
                        case_intensity = case_intensity[[col for col in case_intensity.columns if col.startswith('PPM_')]]
                        case_intensity_array = case_intensity.to_numpy().flatten()
                        case_intensities.append(case_intensity_array)
                        ax.plot(xaxis, case_intensity_array, color=color_current, linewidth=1, clip_on=True)
                else:
                    # If not plotting individual plots, still collect intensities for mean and std
                    for case in cases_selected:
                        case_intensity = position_data.loc[position_data['ID'] == case]
                        case_intensity = case_intensity[[col for col in case_intensity.columns if col.startswith('PPM_')]]
                        case_intensity_array = case_intensity.to_numpy().flatten()
                        case_intensities.append(case_intensity_array)
                
                # Plot mean and standard deviation if requested
                if include_mean and case_intensities:
                    mean_intensity = mean(case_intensities, axis=0)
                    
                    # Only darken color if plotting individual cases
                    if plot_individual_plots:
                        # Darken the color for the mean line
                        from matplotlib.colors import to_rgb
                        mean_color = tuple(max(0, c * 0.5) for c in to_rgb(color_current))
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
                if add_vertical_lines and ppm_list_vertical:
                    for item in ppm_list_vertical:
                        add_vertical_line_with_text(ax, item, float(global_maxIntensity), str(item))
                
                # Add title with position coordinates
                ax.set_title(f'X:{x_pos}, Y:{y_pos} (n={len(cases_selected)})')
                
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
                if legend_handles:
                    ax.legend(handles=legend_handles, loc='best')
                
                # Apply common plot settings - ensure same x-axis range for all plots
                apply_common_plot_settings(global_minIntensity, global_maxIntensity, ppm_range, legend_visible, ax=ax)
                
                # Save individual subplot if requested
                if output_directory and save_subplot:
                    try:
                        # Create sanitized filename for this position
                        position_name = f"X{x_pos}_Y{y_pos}"
                        subplot_filename = f"{sanitize_filename(position_name)}-{filename}"
                        outPath_subplot = path.join(output_directory, subplot_filename)
                        
                        # Create new figure with larger dimensions for the individual plot
                        fig_single = plt.figure(figsize=(10, 6))
                        ax_single = fig_single.add_subplot(111)
                        
                        # Plot the exact same data as in the main subplot
                        if plot_individual_plots:
                            for case_intensity_array in case_intensities:
                                ax_single.plot(xaxis, case_intensity_array, color=color_current, linewidth=1, clip_on=True)
                        
                        if include_mean and case_intensities:
                            mean_intensity = mean(case_intensities, axis=0)
                            
                            # Use same color logic as in main plot
                            if plot_individual_plots:
                                from matplotlib.colors import to_rgb
                                mean_color = tuple(max(0, c * 0.5) for c in to_rgb(color_current))
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
                                                label='±σ')
                        
                        if add_vertical_lines:
                            for item in ppm_list_vertical:
                                add_vertical_line_with_text(ax_single, item, float(global_maxIntensity), str(item))
                        
                        # Add title
                        ax_single.set_title(f'Position X:{x_pos}, Y:{y_pos} (n={len(cases_selected)})')
                        
                        # Add legend if needed
                        if legend_handles:
                            ax_single.legend(handles=legend_handles, loc='best')
                        
                        # Apply common plot settings
                        apply_common_plot_settings(global_minIntensity, global_maxIntensity, ppm_range, legend_visible, ax=ax_single)
                        
                        # Save the individual subplot
                        fig_single.tight_layout()
                        fig_single.savefig(outPath_subplot, dpi=dpi)
                        plt.close(fig_single)  # Close to free memory
                        
                        if statusbar:
                            update_status(statusbar, f'Saved plot for position X:{x_pos}, Y:{y_pos} as {subplot_filename}', 2000)
                    
                    except Exception as e:
                        if statusbar:
                            update_status(statusbar, f'Error saving subplot for position X:{x_pos}, Y:{y_pos}: {str(e)}', 3000)
    
    # Add empty axes for any missing grid positions to maintain grid structure
    for row in range(grid_rows):
        for col in range(grid_cols):
            # Check if this position has an axis already
            has_axis = False
            for ax in fig.get_axes():
                if ax.get_subplotspec().get_gridspec_subplot_region() == (row, col):
                    has_axis = True
                    break
            
            # If no axis, add an empty one
            if not has_axis:
                ax = fig.add_subplot(gs[row, col])
                ax.axis('off')
                ax.text(0.5, 0.5, "No data", ha='center', va='center')
    
    # Add a grid title
    fig.suptitle("Multi-Voxel Grid Plot", fontsize=16)
    
    try:
        fig.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for suptitle
    except:
        pass
    
    # Save overall figure if requested
    if output_directory and export_figure:
        try:
            # Ensure output directory exists
            makedirs(output_directory, exist_ok=True)
            
            # Save the figure
            plt.savefig(outPath, dpi=dpi)
            
            if statusbar:
                update_status(statusbar, f'Saved grid plot as {filename}', 3000)
        except Exception as e:
            if statusbar:
                update_status(statusbar, f'Error saving grid plot: {str(e)}', 3000)
    
    return fig