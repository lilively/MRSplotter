from pandas import read_csv, DataFrame, concat
from numpy import array, linspace, flip
from pathlib import Path
from status import update_status
from io import StringIO


def read_structured_csv(file_path, ppm_range):
    """
    A robust function to read a structured CSV file that contains metadata, 
    and data table, handling the format exported by DataEditorDialog.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
    ppm_range : tuple
        Range of PPM values to filter (min_ppm, max_ppm)
    
    Returns:
    --------
    tuple: (first_ppm, last_ppm, number_of_points, xaxis, data_table)
        first_ppm : float
            First PPM value
        last_ppm : float
            Last PPM value
        number_of_points : int
            Number of points in xaxis
        xaxis : numpy.ndarray
            Array of PPM values
        data_table : pandas.DataFrame
            Data table with all columns from the CSV
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Parse states
    STATE_INIT = 0
    STATE_METADATA = 1
    STATE_DATA = 2
    
    current_state = STATE_INIT
    metadata = {}
    data_lines = []
    
    # First pass: Parse the file line by line
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Skip empty lines, but they might indicate a state change
            if not line:
                continue
            
            # Handle metadata lines
            if line.startswith('#'):
                if current_state == STATE_INIT:
                    current_state = STATE_METADATA
                
                # Parse metadata
                line = line.lstrip('#').strip()
                
                # Try to extract key-value pairs
                parts = line.split(',', 1)
                if len(parts) >= 2:
                    key, value = parts
                    metadata[key.strip()] = value.strip()
                continue
            
            # Handle data table lines
            if current_state in [STATE_METADATA, STATE_INIT]:
                current_state = STATE_DATA
            
            data_lines.append(line)
    
    # Parse the data table from the collected lines
    if data_lines:
        data_csv = StringIO('\n'.join(data_lines))
        data_table = read_csv(data_csv)
    else:
        # If no data table was found, return an empty DataFrame
        data_table = DataFrame()
    
    # Extract PPM values from metadata
    try:
        firstPPM = float(metadata.get('First PPM', 0))
        lastPPM = float(metadata.get('Last PPM', 0))
        number_of_points = int(metadata.get('Number of points', 0))
        
        # Generate xaxis based on metadata
        xaxis = flip(linspace(firstPPM, lastPPM, number_of_points))
    except (ValueError, TypeError) as e:
        print(f"Error extracting PPM values from metadata: {e}")
        # Default values if metadata extraction fails
        firstPPM = 0
        lastPPM = 0
        number_of_points = 0
        xaxis = array([])
    
    return firstPPM, lastPPM, number_of_points, xaxis, data_table


def read_list_of_csv(file_paths, ppm_range, statusbar=None):
    """
    Read in data from a list of file paths
    Parameters:
    file_paths (list): List of file paths to CSV files
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
        if statusbar is not None:
            update_status(statusbar, f"Currently reading in {filepath}", 3000)
        
        file_firstPPM, file_lastPPM, file_number_of_points, file_xaxis, filtered_dataTable = read_structured_csv(
            file_path=filepath,
            ppm_range=ppm_range
        )
        
        dfs.append(filtered_dataTable)
        
        # Store parameters from the last file (or you could select specific ones)
        firstPPM, lastPPM, number_of_points = file_firstPPM, file_lastPPM, file_number_of_points
        xaxis = file_xaxis
    
    # Combine all data tables
    dataTable = concat(dfs, axis=0)
   
    if statusbar is not None:
        update_status(statusbar, f"{len(dfs)} CSV files processed", 3000)
    
    return firstPPM, lastPPM, number_of_points, xaxis, dataTable

def read_list_of_csv(file_paths, ppm_range, statusbar=None):
    """
    Read in data from a list of file paths
    Parameters:
    file_paths (list): List of file paths to CSV files
    ppm_range (tuple): Range of PPM values to filter (first_ppm, last_ppm)    
    Returns:
    tuple: (firstPPM, lastPPM, number_of_points, xaxis, dataTable)
    """
    
    # Read in data from each file
    dfs = []
    firstPPM, lastPPM, number_of_points = None, None, None
    xaxis = None
    
    for filepath in file_paths:
        print(f"Currently reading in {filepath}")
        if statusbar is not None:
            update_status(statusbar, f"Currently reading in {filepath}", 3000)
        
        file_firstPPM, file_lastPPM, file_number_of_points, file_xaxis, filtered_dataTable = read_structured_csv(
            file_path=filepath,
            ppm_range=ppm_range
        )
        
        dfs.append(filtered_dataTable)
        
        # Store parameters from the last file (or you could select specific ones)
        firstPPM, lastPPM, number_of_points = file_firstPPM, file_lastPPM, file_number_of_points
        xaxis = file_xaxis
    
    # Combine all data tables
    dataTable = concat(dfs, axis=0)
   
    if statusbar is not None:
        update_status(statusbar, f"{len(dfs)} CSV files processed", 3000)
    
    return firstPPM, lastPPM, number_of_points, xaxis, dataTable