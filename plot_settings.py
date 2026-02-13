import matplotlib.pyplot as plt
from math import ceil, sqrt



def add_vertical_line_with_text(ax_or_plt, x_position, y_position, text):
    """
    Adds a vertical line and text annotation at a specified position.
    
    Parameters:
    ax_or_plt: Either a matplotlib axes object or plt
    x_position (float): x-coordinate for the vertical line
    y_position (float): y-coordinate for the text
    text (str): The text to display
    """
    # Handle both plt and axis objects
    if ax_or_plt == plt:
        # If plt was passed, get the current axis
        ax = plt.gca()
        # Use plt methods for backward compatibility
        ax_or_plt.axvline(x=x_position, color='gray', linestyle='--', alpha=0.7)
        ax_or_plt.text(x_position, y_position * 0.95, text, 
                    rotation=90, verticalalignment='top', horizontalalignment='right')
    else:
        # If an axis was passed, use axis methods
        ax = ax_or_plt
        ax.axvline(x=x_position, color='gray', linestyle='--', alpha=0.7)
        ax.text(x_position, y_position * 0.95, text, 
              rotation=90, verticalalignment='top', horizontalalignment='right')
    
def apply_common_plot_settings(min_intensity, max_intensity, ppm_range,legend_visible=False, label_length=None, ax=None):
    """
    Apply common plot settings to current or specified axes
   
    Parameters:
    min_intensity (float): Minimum intensity for y-axis
    max_intensity (float): Maximum intensity for y-axis
    ppm_range (list): PPM range to plot [min, max]
    label_length (list or int, optional): List or integer used to determine font size for legend
    ax (Axes, optional): Matplotlib axes to apply settings to. If None, use current axes.
    """
   
    # Get current axes if none specified
    if ax is None:
        ax = plt.gca()
   
    # Set y-axis limits
    ax.set_ylim(min_intensity, max_intensity)
   
    # Set x-axis limits - invert because ppm decreases from left to right
    if ppm_range:
        ax.set_xlim(max(ppm_range), min(ppm_range))
   
    # Set labels with increased font size
    ax.set_xlabel('ppm', fontsize=14)
    ax.set_ylabel('Intensity', fontsize=14)
   
    # Increase tick label font size
    ax.tick_params(axis='both', which='major', labelsize=14)
   
    # Increase title font size if there is a title
    if ax.get_title():
        ax.set_title(ax.get_title(), fontsize=15)
    
    legend = ax.get_legend()
    if legend: 
        legend.set_visible(legend_visible)
        
        if legend_visible:  # Only set font size when legend is visible
            if isinstance(label_length, list):
                if len(label_length) > 14:
                    font_size = 9
                elif len(label_length) > 10:
                    font_size = 10
                elif len(label_length) > 6:
                    font_size = 12
                else:
                    font_size = 16
            else:
                # Handle cases without label_length list
                handles, labels = ax.get_legend_handles_labels()
                long_labels = any(len(label) > 10 for label in labels)
                
                if long_labels:
                    font_size = 12
                else:
                    font_size = 16 
            
            # Apply the font size to legend text
            plt.setp(legend.get_texts(), fontsize=font_size)



def apply_common_plot_settingsMV(min_intensity, max_intensity, ppm_range, legend_visible=False, label_length=None, ax=None):
    """
    Apply common plot settings to current or specified axes
   
    Parameters:
    min_intensity (float): Minimum intensity for y-axis
    max_intensity (float): Maximum intensity for y-axis
    ppm_range (list): PPM range to plot [min, max]
    label_length (list or int, optional): List or integer used to determine font size for legend
    ax (Axes, optional): Matplotlib axes to apply settings to. If None, use current axes.
    """
    # Get current axes if none specified
    if ax is None:
        ax = plt.gca()
   
    # Set y-axis limits
    ax.set_ylim(min_intensity, max_intensity)
   
    # Set x-axis limits - invert because ppm decreases from left to right
    if ppm_range:
        ax.set_xlim(max(ppm_range), min(ppm_range))
   
    # Increase tick label font size
    ax.tick_params(axis='both', which='major', labelsize=14)
   
    # Increase title font size if there is a title
    if ax.get_title():
        ax.set_title(ax.get_title(), fontsize=15)
    
    legend = ax.get_legend()
    if legend: 
        legend.set_visible(legend_visible)
        
        if legend_visible:  # Only set font size when legend is visible
            if isinstance(label_length, list):
                if len(label_length) > 14:
                    font_size = 9
                elif len(label_length) > 10:
                    font_size = 10
                elif len(label_length) > 6:
                    font_size = 12
                else:
                    font_size = 16
            else:
                # Handle cases without label_length list
                handles, labels = ax.get_legend_handles_labels()
                long_labels = any(len(label) > 10 for label in labels)
                
                if long_labels:
                    font_size = 12
                else:
                    font_size = 16 
            
            # Apply the font size to legend text
            plt.setp(legend.get_texts(), fontsize=font_size)


def remove_empty_subplots(selected_tissue_types, num_cols, num_rows, fig):
    for i in range(len(selected_tissue_types) + 1, (num_rows * num_cols) + 1):
        if i <= (num_rows * num_cols):
            ax = fig.add_subplot(num_rows, num_cols, i)
            ax.axis('off')









def calculate_grid_dimensions(num_plots):
    """Calculate optimal grid dimensions for subplots based on the number of plots."""
    if num_plots <= 1:
        return 1, 1
   
    # Special cases for better layouts
    if num_plots == 2:
        return 2, 1  # 2 columns, 1 row 
    # elif num_plots == 5:
    #     return 5, 1
    elif num_plots in [5, 6]:
        # For 5 or 6 plots, use 3 columns and 2 rows as preferred
        return 3, 2  # 3 columns, 2 rows 
   
    # For other cases, calculate dimensions
    cols = min(ceil(sqrt(num_plots)), 3)
    rows = ceil(num_plots / cols)
   
    return cols, rows









