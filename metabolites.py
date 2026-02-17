from os import path
from status import update_status


def export_intenity(output_directory,ppm_list_vertical, ppm_range, statusbar, number_of_points, dataTable):
    from filter_data_ppm import get_PPM
    for item in ppm_list_vertical:

        try:
            ppm_column = get_PPM(item, number_of_points, ppm_range[1], ppm_range[0])
            ppm_column = get_PPM(item, number_of_points, ppm_range[1], ppm_range[0])
            update_status(statusbar,(f'The column for {item} is {ppm_column}'))
            #case_info = dataTable.iloc[:, :4]
            #case_info = dataTable[['ID', 'TissueType', 'x_pos', 'y_pos']]
            available_columns = ['ID', 'TissueType','SNR', 'x_pos', 'y_pos']
            case_info = dataTable[[col for col in available_columns if col in dataTable.columns]]

            data_ppm = dataTable[[col for col in dataTable.columns if col.startswith('PPM_')]]
            data_column = data_ppm.iloc[:, ppm_column]
            data_column  = data_column.rename(f'Intensity at {item} ppm')

            result = case_info.copy()
            result[f'Intensity at {item} ppm'] = data_column
        
        except Exception as e:
                        if statusbar:
                            update_status(statusbar,f"Error saving {filename}...")
                        else:
                            print(f"Error saving {filename}: {str(e)}")
        if output_directory :
            filename = f'Intensities_{str(item)}_ppm.xlsx'
            outPath = path.join(output_directory, filename)
        try:
            result.to_excel(outPath, index=False)
        # Update status bar if available
            if statusbar:
                update_status(statusbar,f"Saving intensities at {item} as {filename} to {output_directory}")
            else:
                print(f'Saving results as {filename} to {output_directory}')
        except Exception as e:
                        if statusbar:
                            update_status(statusbar,f"Error saving {filename}...")
                        else:
                            print(f"Error saving {filename}: {str(e)}")



