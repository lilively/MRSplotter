import matplotlib.pyplot as plt
from numpy import mean, std
from os import path, makedirs
from status import update_status
from plot_settings import apply_common_plot_settings, add_vertical_line_with_text


def plot_sources(output_directory, xaxis, dataTable, include_mean, include_sdev, plot_individual_plots,
                 add_vertical_lines, ppm_list_vertical, selected_color, ppm_range,
                 export_figure=False, y_limits=None, canvas_width=None, canvas_height=None, legend_visible=False,
                 dpi=None, statusbar=None, fig=None):
    """
    Plot source spectra superimposed. 
    """

    selected_tissue_types = list(selected_color.keys())

    if not selected_tissue_types:
        if statusbar:
            update_status(statusbar, "No tissue types selected for superimposed plot")
        return None



    if y_limits is None:
        try:
            from global_intensities import calculate_y_limit
            global_minIntensity, global_maxIntensity = calculate_y_limit(
                dataTable[dataTable['TissueType'].isin(selected_tissue_types)],
                not plot_individual_plots,
                include_sdev,
            )
        except Exception as e:
            update_status(statusbar, f"Error calculating Y limits: {str(e)}")
            global_minIntensity, global_maxIntensity = -5, 15
    else:
        global_minIntensity, global_maxIntensity = y_limits

    if canvas_width is not None and canvas_height is not None and dpi is not None:
        width_inches = canvas_width / dpi
        height_inches = canvas_height / dpi
        if fig is None:
            fig = plt.figure(figsize=(width_inches, height_inches), dpi=dpi)
        else:
            fig.clear()
    else:
        if fig is None:
            fig = plt.figure(figsize=(10, 6))
            if dpi is not None:
                fig.set_dpi(dpi)
        else:
            fig.clear()

    ax = fig.add_subplot(111)

    for tissue_type in selected_tissue_types:
        if tissue_type in selected_color:
            color_current = selected_color[tissue_type]
        else:
            color_current = '#000000'

        filtered = dataTable[dataTable['TissueType'] == tissue_type]
        num_spectra = len(filtered)

        if num_spectra == 0:
            update_status(statusbar, f"No cases found for tissue type: {tissue_type}")
            continue

        ppm_cols = sorted(
            [col for col in filtered.columns if col.startswith('PPM_')],
            key=lambda c: float(c.split('_')[1]), reverse=True,
        )

        case_intensities = []

        if plot_individual_plots:
            for i, (row_idx, row) in enumerate(filtered.iterrows()):
                case_intensity_array = row[ppm_cols].values.astype(float)
                case_intensities.append(case_intensity_array)
                line, = ax.plot(
                    xaxis, case_intensity_array[:len(xaxis)], color=color_current, linewidth=1.2, clip_on=False,
                    label=f"{tissue_type}" if i == 0 and not (include_mean or include_sdev) else "",
                )
        else:
            for row_idx, row in filtered.iterrows():
                case_intensity_array = row[ppm_cols].values.astype(float)
                case_intensities.append(case_intensity_array)

        

    if ax.get_legend_handles_labels()[0]:
        legend = ax.legend(loc='best')
        for line in legend.get_lines():
            line.set_linewidth(2)

    apply_common_plot_settings(global_minIntensity, global_maxIntensity, ppm_range, legend_visible,
                               label_length=selected_tissue_types, ax=ax)
    
    ax.set_xlabel('ppm', fontsize=12)
    ax.set_ylabel('Intensity', fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=10)

    # ax.legend(loc='upper center',
    #       bbox_to_anchor=(0.5, -0.15),
    #       ncol=2,          
    #       frameon=False)


    return fig
