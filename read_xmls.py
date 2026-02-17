from pathlib import Path
from filter_data_ppm import get_PPM
from numpy import linspace, flip, nan
from status import update_status
from pandas import concat, DataFrame
import xml.etree.ElementTree as ET


def readXML_jmrui(filepath, ppm_range):
    caseID = Path(filepath).stem
# Parse XML file
    tree = ET.parse(filepath)
    root = tree.getroot()
    data = []

    for voxel in root.findall('.//Voxel'):
        #theese can be single variables, as all of them are the same 
        firstPPM = float(voxel.get('FirstPPM'))
        lastPPM = float(voxel.get('LastPPM'))
        number_of_points = float(voxel.get('PointsNumber'))
        points = [float(p) for p in voxel.find('Points').text.split()]
        
        #ppm_range = (min(first_ppm, last_ppm), max(first_ppm, last_ppm))

        if ppm_range[0]<firstPPM:
            ppm_range[0] = firstPPM

        if ppm_range[1]>lastPPM:
            ppm_range[1] = lastPPM

        min_point = get_PPM(ppm_range[0], number_of_points, lastPPM, firstPPM)
        max_point = get_PPM(ppm_range[1], number_of_points, lastPPM, firstPPM)
        points_filtered = points[max_point:min_point+1]

        #selecting data for columns
        voxel_data = {
        'ID' : str(Path(filepath).stem),
        # 'FirstPPM': float(voxel.get('FirstPPM')),
        # 'LastPPM': float(voxel.get('LastPPM')),
        # 'number_of_points': int(voxel.get('number_of_points')),
        #'SNR': float(voxel.get('SNR')),
        # 'Xaxis': int(voxel.get('Xaxis')),
        # 'Yaxis': int(voxel.get('Yaxis')),
        # #'Zaxis': int(voxel.get('Zaxis')),
        'TissueType': voxel.find('Tissue').get('Type'),}

        #voxel_data['SNR'] = float(voxel.get('SNR')) if voxel.get('SNR') else None
        if voxel_data.get('SNR') is not None:
            voxel_data['SNR'] = float(voxel_data.get('SNR'))
            
        voxel_data.update({'PPM_{}'.format(i): points_filtered[i] for i in range(len(points_filtered))})
        
        data.append(voxel_data)

    dataTable = DataFrame(data)
        
    xaxis = flip(linspace(ppm_range[0], ppm_range[1], len(points_filtered), endpoint=True))
    number_of_points = len(points_filtered)
    return caseID, firstPPM, lastPPM,number_of_points, points_filtered,xaxis,dataTable


def readXML_SpectraClassifier(ppm_range, filepath, output_directory=None,  statusbar=None): 
    if isinstance(filepath, str):
        filepath = [filepath]  # Convert single string to list
    for item in filepath:
        tree = ET.parse(item) 
        root = tree.getroot()
        data = []

        for case in root.findall('.//Case'):
        #theese can be single variables, as all of them are the same
            firstPPM = float(case.find('.//Parameters').get('FirstPPM'))
            lastPPM = float(case.find('.//Parameters').get('LastPPM'))
            number_of_points = int(case.find('.//Parameters').get('PointsNumber'))
            points = [float(p) for p in case.find('.//Points').text.split()]

            if ppm_range[0]<firstPPM:
                ppm_range[0] = firstPPM

            if ppm_range[1]>lastPPM:
                ppm_range[1] = lastPPM

            min_point = get_PPM(ppm_range[0], number_of_points, lastPPM, firstPPM)
            max_point = get_PPM(ppm_range[1], number_of_points, lastPPM, firstPPM)
            points_filtered = points[max_point:min_point+1]
            


            params = case.find('.//Parameters')
            voxel_data = {
            'ID' : case.get('ID'),
            'TissueType':case.find('Tissue').get('Type'),
            }

            # Extract X/Y coordinates if present (multivoxel data)
            if params is not None:
                if params.get('Xaxis') is not None and params.get('Yaxis') is not None:
                    voxel_data['x_pos'] = params.get('Xaxis')
                    voxel_data['y_pos'] = params.get('Yaxis')
                if params.get('SNR') is not None:
                    voxel_data['SNR'] = float(params.get('SNR'))

            voxel_data.update({'PPM_{}'.format(i): points_filtered[i] for i in range(len(points_filtered))})
            
            data.append(voxel_data)

        dataTable = DataFrame(data)
        xaxis = flip(linspace(ppm_range[0], ppm_range[1], len(points_filtered), endpoint=True))
        number_of_points = len(points_filtered)
        update_status(statusbar,f"{len(data)} xml files processed")
        
        return firstPPM, lastPPM,number_of_points,xaxis,dataTable

def readxml_list_of_jmrui(file_paths, ppm_range, output_directory=None,  statusbar=None):
    """
    Read in data from a list of file paths
    Parameters:
    file_paths (list): List of file paths to XML files
    ppm_range (tuple): Range of PPM values to filter (first_ppm, last_ppm)    
    Returns:
    tuple: (firstPPM, lastPPM, number_of_points, xaxis, dataTable)
    """
    
    # Read in data from each file
    dfs = []
    firstPPM, lastPPM, number_of_points = None, None, None
    xaxis = None
    
    for filepath in file_paths:
        #print(f"Currently reading in {filepath}")
        update_status(statusbar,f"Currently reading in {filepath}")
        caseID, first_ppm, last_ppm, num_points, points_filtered, file_xaxis, dataTable_read = readXML_jmrui(filepath, ppm_range)
        dfs.append(dataTable_read)
        
        # Store parameters from the last file (or you could select specific ones)
        firstPPM, lastPPM, number_of_points = first_ppm, last_ppm, num_points
        xaxis = file_xaxis
    
    # Combine all data tables
    dataTable = concat(dfs, axis=0)
   
    update_status(statusbar,f"{len(dfs)} xml files processed")
    
    return firstPPM, lastPPM, number_of_points, xaxis, dataTable






def read_multi_voxel_as_table(filepath,ppm_range):
    caseID = Path(filepath).stem
    
    # Parse XML file and extract data
    try:
        tree = ET.parse(filepath)
    except ET.ParseError as e:
        raise ValueError(f"Error parsing XML file: {e}")
    
    root = tree.getroot()
    data = []

    
    for grid in root.findall('.//Grid/'):
        try:
            number_of_points = int(grid.get('PointsNumber'))
            firstPPM = float(grid.get('FirstPPM'))
            lastPPM = float(grid.get('LastPPM'))
            row_data = {
                'ID': f"{caseID}_X_{grid.get('Xaxis')}_Y_{grid.get('Yaxis')}",
                'TissueType': (grid.find('.//Tissue').get('Type')),
                'x_pos': grid.get('Xaxis'),
                'y_pos': grid.get('Yaxis'),
                
            }

            points = [float(p) for p in grid.find('Points').text.split()]

            from conflict_handling import validate_ppm_range

            ppm_range = validate_ppm_range(ppm_range, firstPPM, lastPPM, statusbar=None)
            
            min_point = get_PPM(ppm_range[0], number_of_points, lastPPM, firstPPM)
            max_point = get_PPM(ppm_range[1], number_of_points, lastPPM, firstPPM)

            points_filtered = points[max_point:min_point+1]
            if grid.get('SNR') is not None:
                row_data['SNR'] = float(grid.get('SNR'))
            
            row_data.update({'PPM_{}'.format(i): points_filtered[i] for i in range(len(points_filtered))})
            
        
            data.append(row_data)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error processing grid data: {e}")

    # Create a DataFrame with all the extracted data
    dataTable = DataFrame(data)
    xaxis = flip(linspace(ppm_range[0], ppm_range[1], len(points_filtered), endpoint=True))
    number_of_points = len(points_filtered)
    return caseID, firstPPM, lastPPM,number_of_points, points_filtered,xaxis,dataTable


def readxml_list_of_multi_voxel(file_paths, ppm_range,  statusbar=None):
    dfs = []
    firstPPM, lastPPM, number_of_points = None, None, None
    xaxis = None
    
    for filepath in file_paths:
        #print(f"Currently reading in {filepath}")        update_status(statusbar,f"Currently reading in voxels {filepath}")
        caseID, first_ppm, last_ppm, num_points, points_filtered, file_xaxis, dataTable_read = read_multi_voxel_as_table(filepath, ppm_range)
        dfs.append(dataTable_read)
        
        # Store parameters from the last file (or you could select specific ones)
        firstPPM, lastPPM, number_of_points = first_ppm, last_ppm, num_points
        xaxis = file_xaxis
    
     # Combine all data tables
    dataTable = concat(dfs, axis=0)
   
    update_status(statusbar,f"{len(dfs)} xml files processed")
    
    return firstPPM, lastPPM,number_of_points,xaxis,dataTable


def readxml_list_of_spectraclassifier(file_paths, ppm_range,  statusbar=None):
    dfs = []
    firstPPM, lastPPM, number_of_points = None, None, None
    xaxis = None
    
    for filepath in file_paths:
        #print(f"Currently reading in {filepath}")        update_status(statusbar,f"Currently reading in voxels {filepath}")
        firstPPM, lastPPM,number_of_points,xaxis,dataTable = readXML_SpectraClassifier(ppm_range=ppm_range,
                                                                        filepath =filepath,             
                                                                        statusbar=None)
                
        dfs.append(dataTable)
        
        # Store parameters from the last file (or you could select specific ones)
        firstPPM, lastPPM, number_of_points = firstPPM, lastPPM, number_of_points
        xaxis = xaxis
     # Combine all data tables
    dataTable = concat(dfs, axis=0)
   
    update_status(statusbar,f"{len(dfs)} xml files processed")
    
    return firstPPM, lastPPM,number_of_points,xaxis,dataTable

