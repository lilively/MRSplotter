# import os
# from MRSPlotter.determine_type_and_load import read_XML_files
# from create_superimposed import create_superimposed
# from create_plot_subplots import create_subplot
# from metabolites import export_intenity




# # xml_directory = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\sinlgeVoxelData\Meningioma-data\xml-uab_ID\SE-limitedrange-discarded"
# # #xml_directory = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\sv_data\Meningioma\Xml UAB\SE-M"
# # output_directory = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\Visu_test"

# # selected_files = []
# # for file in os.listdir(xml_directory):
# #     filepath = os.path.join(xml_directory,file)
# #     selected_files.append(filepath)

# # selected_files = [r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\mv_data\pseudoprogression_gulnur\4.2ppm_xml\Case 13.xml"]

# # ##########################
# # include_mean = True 
# # include_sdev = False
# # plot_individual_plots = True # When True, plot individual cases. When False, plot only means.
# # add_vertical_lines = True
# # selected_color = ['#00c4ff']
# # ppm_range = [0,4]
# # add_brainH = True
# # add_cusom_lines = True
# # export_figure = False
# # ppm_list_vertical = [3.21, 3.03, 1.29]
# # #ppm_list_vertical = ['3.21', '3.03', '1.29']

# # firstPPM,lastPPM,number_of_points,xaxis,dataTable = read_XML_files(
# #             selected_files, ppm_range)

# # print(dataTable.head(4))
# # output_directory= r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\Visu_test\1"

# # # create_subplot(output_directory, xaxis, dataTable, include_mean, include_sdev, 
# # #                    plot_individual_plots, add_vertical_lines, ppm_list_vertical, selected_color, ppm_range, 
# # #                    y_limits=None, export_figure=False, save_subplot=True, canvas_width=None, 
# # #                    canvas_height=None, dpi=300, statusbar=None)

# # export_intenity(output_directory=output_directory,
# #                 ppm_list_vertical=ppm_list_vertical,
# #                 ppm_range=ppm_range,
# #                 number_of_points=number_of_points,
# #                 dataTable=dataTable,
# #                 statusbar=None)


# # print('Test done')
# # create_superimposed(output_directory, xaxis, dataTable, include_mean, include_sdev, plot_individual_plots, 
# #                         add_vertical_lines,ppm_list_vertical, selected_color, ppm_range, export_figure=False, y_limits=None,
# #                         canvas_width=None, canvas_height=None, dpi=None, statusbar=None)

# from plot_settings import calculate_grid_dimensions

# # print(calculate_grid_dimensions(1))
# # print(calculate_grid_dimensions(2))
# # print(calculate_grid_dimensions(3))
# # print(calculate_grid_dimensions(4))
# # print(calculate_grid_dimensions(5))
# # print(calculate_grid_dimensions(6))
# # print(calculate_grid_dimensions(7))
# print(calculate_grid_dimensions(14))



# # xml_directory = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\sv_data\Low-grade-glioma\Xml UAB\long echo xml"
# # #xml_directory = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\sv_data\Meningioma\Xml UAB\SE-M"
# # output_directory = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\Visu_test\3"

# # selected_files = []
# # for file in os.listdir(xml_directory):
# #     filepath = os.path.join(xml_directory,file)
# #     selected_files.append(filepath)


# # ##########################
# # include_mean = True
# # include_sdev = False
# # plot_individual_plots = True # When True, plot individual cases. When False, plot only means.
# # add_vertical_lines = True
# # selected_color = ['#00c4ff']
# # ppm_range = [0,4.5]
# # export_figure = False
# # res_dpi = 300

# # firstPPM,lastPPM,number_of_points,xaxis,dataTable = read_SV_files(
# #             selected_files, ppm_range, save_output=False
# #         )

# # create_individual_plots(output_directory, xaxis, dataTable, include_mean, include_sdev, plot_individual_plots, 
# #                         add_vertical_lines, selected_color, ppm_range, export_figure=True, 
# #                         canvas_width=None, canvas_height=None, dpi=res_dpi)



# # selected_files1 =  [r'C:/Users/lilif/OneDrive/Desktop/Dropbox/Phd/sinlgeVoxelData/Meningioma-data/xml-uab_ID/SE-limitedrange-discarded/SV_2-SE.xml',
# #                     r'C:/Users/lilif/OneDrive/Desktop/Dropbox/Phd/sinlgeVoxelData/Meningioma-data/xml-uab_ID/SE-limitedrange-discarded/SV_3-SE.xml', 
# #                     r'C:/Users/lilif/OneDrive/Desktop/Dropbox/Phd/sinlgeVoxelData/Meningioma-data/xml-uab_ID/SE-limitedrange-discarded/SV_4-SE.xml', 
# #                     r'C:/Users/lilif/OneDrive/Desktop/Dropbox/Phd/sinlgeVoxelData/Meningioma-data/xml-uab_ID/SE-limitedrange-discarded/SV_5-SE.xml']
# selected_files2 = [r"C:\Users\lilif\OneDrive\Desktop\INTERPRET 1TE-ShortMRS100.xml"]

# # selected_files3 = [r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\mv_data\pseudoprogression_gulnur\4.2ppm_xml\Case 11.xml",
# #                    r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\mv_data\pseudoprogression_gulnur\4.2ppm_xml\Case 12.xml"]



# # firstPPM, lastPPM,number_of_points,xaxis,dataTable = read_SV_files(selected_files3, ppm_range,  statusbar=None)

# # # #firstPPM, lastPPM, number_of_points, xaxis, dataTable = readXML_SC(ppm_range=ppm_range, filepath=filepaths)

# from load_SV_xmls import read_XML_files
# firstPPM, lastPPM, number_of_points, xaxis, dataTable = read_XML_files(selected_files2, ppm_range,  statusbar=None)


# print(dataTable.head(3))


# from load_SV_xmls import determine_filetype

# filepath = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\jmruitext_format\jMRUI-precuneus\All-minimal-processing-ref.txt"
# print(determine_filetype(filepath))
# print(xaxis)

# print(f"Filtering to PPM range: {ppm_range[0]} to {ppm_range[1]}")
# print(f"First PPM from file: {firstPPM}, last PPM from file {lastPPM}")


#filepath = r"C:\Users\lilif\OneDrive\Desktop\jmrui_test\SV0577-v7.txt"
#filepath= r"C:\Users\lilif\OneDrive\Desktop\jmrui_test\SV0577-v7-ref.txt"
#filepath = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\sv_data\Low-grade-glioma\Quality control\FWHM-progress\short echo water\se-batch4.txt"
#filepath = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\jmruitext_format\jMRUI-precuneus\All-minimal-processing-ref.txt"

# # filepath = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\jmruitext_format\test.csv"

# # from read_jmrui_type import check_phase_coherence
# # ppm_range = [-3.7, 12.4]

# # from read_jmrui_version import read_jmrui_text_data
# # from read_csv import read_structured_csv
# # import matplotlib.pyplot as plt
# # # firstPPM, lastPPM, points_filtered,xaxis,filtered_dataTable = read_jmrui_text_data(filepath, ppm_range=ppm_range)

# # firstPPM, lastPPM, points_filtered,xaxis,filtered_dataTable = read_structured_csv(filepath, ppm_range=ppm_range)

# # print(f'First PPM: {firstPPM}, Last PPM: {lastPPM}')

# # # Create a single figure for visualization
# # plt.figure(figsize=(10, 6))
# # print(filtered_dataTable.head(3))
# # print((points_filtered))
# # print((xaxis))
# # # Plot each signal on the same axes
# # for i, (_, row) in enumerate(filtered_dataTable.iterrows()):
# #     # Extract signal details
# #     signal_id = row['ID']

# #     y_values = row.iloc[4:].values
    
# #     # Plot the spectrum with a label
# #     plt.plot(xaxis, y_values)

# # # Add labels and legend
# # plt.xlabel('Chemical Shift (ppm)')
# # plt.ylabel('Signal Intensity')
# # plt.title('MR Spectroscopy Data')


# # # Set the x-axis limits to follow MRS convention (higher ppm values on left)
# # #plt.gca().set_xlim(ppm_range[0], ppm_range[1])
# # plt.gca().axvline(x=3.21, color='gray', linestyle='--', alpha=0.7)
# # #plt.gca().set_xlim(lastPPM, firstPPM)
# # plt.gca().invert_xaxis()
# # plt.show()
# def create_subplot(output_directory, xaxis, dataTable, include_mean, include_sdev, 
#                    plot_individual_plots, add_vertical_lines, ppm_list_vertical, selected_color, ppm_range, 
#                    y_limits=None, export_figure=False, save_subplot=False, canvas_width=None, 
#                    canvas_height=None, dpi=None, statusbar=None, fig=None, 
#                    use_auto_grid=True, grid_rows=2, grid_cols=2):

from plot_settings import add_vertical_line_with_text, apply_common_plot_settingsMV
from matplotlib import path, pyplot as plt
from matplotlib.gridspec import GridSpec
from determine_type_and_load import read_files
from os import path, makedirs, listdir
from status import update_status
from numpy import isnan

xml_directory = r"C:\Users\lilif\OneDrive\Desktop\test-mv\test-cases"
#xml_directory = r"C:\Users\lilif\OneDrive\Desktop\Dropbox\Phd\sv_data\Meningioma\Xml UAB\SE-M"
output_directory = r"C:\Users\lilif\OneDrive\Desktop\test-mv"

selected_files = []
for file in listdir(xml_directory):
    filepath = path.join(xml_directory,file)
    selected_files.append(filepath)


##########################
include_mean = True
include_sdev = False
plot_individual_plots = True # When True, plot individual cases. When False, plot only means.
add_vertical_lines = True
selected_color = ['#00c4ff']
#ppm_range = [0,4.5]
ppm_range = [-2.7,7.1]
export_figure = False
res_dpi = 300

firstPPM,lastPPM,number_of_points,xaxis,dataTable = read_files(
            selected_files, ppm_range
        )

def get_row_data(x_pos, y_pos, case_id):
    """Get intensity data for specific x,y position"""
    mask = (dataTable['x_pos'] == str(x_pos)) & (dataTable['y_pos'] == str(y_pos)) & (dataTable['ID'].str.startswith(case_id + '_X_'))
    filtered_data = dataTable[mask]
    
    if filtered_data.empty:
        return None, None  # Changed from: return None
    
    # Get PPM columns (intensity data)
    ppm_columns = [col for col in filtered_data.columns if col.startswith('PPM_')]
    if not ppm_columns:
        return None, None  # Changed from: return None
        
    # Get the first row's intensity data
    intensity_data = filtered_data[ppm_columns].iloc[0].values
    tissue_type = filtered_data['TissueType'].iloc[0]
    return intensity_data, tissue_type

def create_multivoxel_grid(output_directory, xaxis, dataTable, ppm_range, 
                        export_figure=False,y_limits = None, dpi=300, statusbar=None, fig=None):
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
    

    
    # Get unique x and y values from the data
    x_values = sorted(dataTable['x_pos'].unique())
    y_values = sorted(dataTable['y_pos'].unique())
    
    xlen = len(x_values)
    ylen = len(y_values)
    n = xlen * ylen
    
    # Get min/max for range - convert to integers
    xmin, xmax = int(min(x_values)), int(max(x_values))
    ymin, ymax = int(min(y_values)), int(max(y_values))

    if y_limits is None:
        from global_intensities import calculate_y_limit
        global_minIntensity, global_maxIntensity = calculate_y_limit(dataTable, False, include_sdev)
    else:
        global_minIntensity, global_maxIntensity = y_limits

    all_tissue_types = sorted(dataTable['TissueType'].unique())
    case_ids = dataTable['ID'].str.extract(r'^([^_]+)_X_').iloc[:, 0].unique().tolist()

    for case in case_ids:
        if fig is None:
            fig = plt.figure(figsize=(12, 10))
        else:
            fig.clear()
        filename = case  
        fig.suptitle(filename, fontweight='bold', fontsize=12, y=0.91)
        
        # Create grid layout
        gs = GridSpec(ylen, xlen, figure=fig, hspace=0.0, wspace=0.0)
        
        counter = 0
        
        for y_idx, y_pos in enumerate(range(ymin, ymax+1)): 
            for x_idx, x_pos in enumerate(range(xmin, xmax+1)):
                ax = fig.add_subplot(gs[y_idx, x_idx])

                
                # Get intensity data for this position
                result = intensity_data, tissue_type = get_row_data(x_pos, y_pos,case)
                if result is not None:
                    intensity_data, tissue_type = result

                if intensity_data is not None and len(intensity_data) > 0 and not all(isnan(intensity_data)):
                    # Valid data exists
                    if tissue_type in selected_color:
                        color_current = selected_color[tissue_type]
                    else:
                        color_current = "#2B4A60"
                    # Plot the spectrum
                    ax.plot(xaxis, intensity_data, color=color_current, linewidth=0.9)
                    apply_common_plot_settingsMV(global_minIntensity, global_maxIntensity, ppm_range, ax=ax)
                    # Add coordinate label
                    coord_label = f"{x_pos}-{y_pos}"
                    ax.text(0.05, 0.85, coord_label, transform=ax.transAxes, 
                        verticalalignment='bottom', fontweight='bold', fontsize=8)
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
    
        fig.supxlabel('PPM', fontsize=14, y=0.08) 
        fig.supylabel('Intensity', fontsize=14, x=0.10)
        # Export if requested
        if output_directory and export_figure:
            try:
                # Ensure directory exists
                makedirs(output_directory, exist_ok=True)
                from conflict_handling import sanitize_filename
                # Define output path
                filename = f"{case}_{'grid'}.png"
                outPath = path.join(output_directory, filename)
                
                # Save the figure
                fig.savefig(outPath, dpi=dpi, bbox_inches='tight')
                
                update_status(statusbar,f'Successfully saved superimposed plot as {filename} to {output_directory}', 3000)
            except Exception as e:
                update_status(statusbar,f'Error saving superimposed plot: {str(e)}', 5000)
        return fig





# create_multivoxel_grid(output_directory, xaxis,dataTable,ppm_range)


for elem in selected_files:
    print(elem)