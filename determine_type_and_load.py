from os import path
from xml.etree import ElementTree as ET
from status import update_status
from read_xmls import readxml_list_of_jmrui, readxml_list_of_multi_voxel, readxml_list_of_spectraclassifier
from read_csv import read_list_of_csv
from read_jmrui_version import read_list_of_jmrui_text

def determine_filetype(filepath_list):
    filepath = filepath_list[0]
    try:
        # Try parsing as XML
        tree = ET.parse(filepath)
        root = tree.getroot()

        if root.get('CreatedBy') == 'MRSPlotter' and root.get('Format') == 'SpectraClassifier':
            return 'SpectraClassifier'
        
        grid_elements = root.findall('.//Grid')
        if grid_elements:
            # Check if any Grid element contains a Voxel with Xaxis attribute
            for grid in grid_elements:
                voxels = grid.findall('.//Voxel[@Xaxis]')
                if len(voxels) > 1:
                    return 'multi_voxel'  
                else:
                    return 'jMRUI2XML'
        
        # Check for SpectraClassifier
        elif root.findall('.//Case'):
            return 'SpectraClassifier'
        
        # Default to JMRUI if it has Voxel but none of the above
        elif root.findall('.//Voxel'):
            return 'jMRUI2XML'
        

        else:
            return None  # Unknown XML structure
    
    except ET.ParseError:
        # If XML parsing fails, check file extension first
        file_extension = path.splitext(filepath)[1].lower()
        
        if file_extension == '.csv':
            return "CSV_file"
        elif file_extension == '.txt':
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Example logic for identifying specific text file types
                    if "jMRUI Data Textfile" in content:
                        return "jMRUI Data Textfile"
                    else:
                        return "TextFile"
            except Exception as e:
                return f"Error reading file: {e}"
        else:
            return f"Unsupported file type: {file_extension}"


def read_files(filepath_list, ppm_range,  statusbar=None):
    filepath = filepath_list[0]
    filetype = determine_filetype(filepath_list)
    update_status(statusbar, f"{filetype} file type", 3000)
    #print(filetype)

    if filetype == 'multi_voxel':

        firstPPM, lastPPM,number_of_points,xaxis,dataTable = readxml_list_of_multi_voxel(file_paths=filepath_list,
                                                                                ppm_range=ppm_range,                                                                                 
                                                                                statusbar=None)
    elif filetype == 'SpectraClassifier':

        firstPPM, lastPPM,number_of_points,xaxis,dataTable = readxml_list_of_spectraclassifier(file_paths=filepath_list,
                                                                ppm_range=ppm_range,             
                                                                statusbar=None)
    elif filetype == 'jMRUI2XML':

        firstPPM, lastPPM,number_of_points,xaxis,dataTable = readxml_list_of_jmrui(file_paths=filepath_list,
                                                                                   ppm_range=ppm_range,
                                                                                   statusbar=None)
    elif filetype == 'jMRUI Data Textfile':
        firstPPM, lastPPM, number_of_points, xaxis, dataTable = read_list_of_jmrui_text(file_paths=filepath_list,
                                                                                        ppm_range=ppm_range,
                                                                                        statusbar= None)
    elif filetype == 'CSV_file':
        firstPPM, lastPPM, number_of_points, xaxis, dataTable = read_list_of_csv(file_paths=filepath_list,
                                                                                        ppm_range=ppm_range,
                                                                                        statusbar= None)

    else:
        update_status(statusbar, f"Unknown file type", 3000)
        # Handle unknown file type
   
    #dataTable['TissueType'] = dataTable['TissueType'].replace('***', 'non-specific')

    return firstPPM, lastPPM,number_of_points,xaxis,dataTable




