from numpy import flip, nan, arange, min, max
from pandas import DataFrame, concat
import regex as re
from status import update_status
from os import path

def read_jmrui_text_data(filepath, ppm_range):
    """
    Process jMRUI file with correct PPM calculation, handling different file formats
    
    Args:
        filepath: Path to jMRUI text file
        ppm_range: Range of PPM values to include [min, max]
        
    Returns:
        tuple: (firstPPM, lastPPM, points_filtered, xaxis, filtered_dataTable)
    """

    
    # Get filename from path for determining file type
    filename = path.basename(filepath)
    
    # Parse header to get key parameters
    signals_dict = {}
    number_of_points = 0
    number_of_signals = 1
    sampling_interval = 1.0
    transmitter_freq = 0
    reference_frequency_hz = 0
    has_reference_frequency = False
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Stop when we reach the data section
            if 'sig(real)' in line and 'fft(real)' in line:
                break
            
            # Look for key parameters
            if 'PointsInDataset' in line:
                number_of_points = int(float(line.split(':', 1)[1].strip()))
            elif 'DatasetsInFile' in line:
                number_of_signals = int(float(line.split(':', 1)[1].strip()))
            elif 'SamplingInterval' in line:
                sampling_interval = float(line.split(':', 1)[1].strip())
            elif 'TransmitterFrequency' in line:
                transmitter_freq = float(line.split(':', 1)[1].strip())
            elif 'Reference Frequency' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    # Extract only numeric parts, handling cases where "Hz" or other text is included
                    ref_freq_str = parts[1].strip()
                    # Use regex to extract numeric value (including scientific notation and decimal points)
                    numeric_matches = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', ref_freq_str)
                    if numeric_matches:
                        reference_frequency_hz = float(numeric_matches[0])
                        has_reference_frequency = True
            elif 'SignalNames' in line:
                signal_names_str = line.split(':', 1)[1].strip()
                signal_names = signal_names_str.strip(';').split(';')
                signals_dict = {name: i for i, name in enumerate(signal_names)}
    
    # If signal names weren't found, create default names
    if not signals_dict:
        signals_dict = {f"Signal_{i+1}": i for i in range(number_of_signals)}
    
    # Read data section
    data = {}
    current_signal = None
    found_data_section = False
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Find the column headers line
            if 'sig(real)' in line and 'fft(real)' in line:
                found_data_section = True
                continue
                
            # Track which signal we're reading
            if found_data_section and line.startswith('Signal'):
                parts = line.split()
                signal_idx = int(parts[1]) - 1  # Convert to 0-based index
                current_signal = signal_idx
                data[current_signal] = []
                continue
                
            # Read signal data
            if found_data_section and current_signal is not None and not line.startswith('Signal'):
                parts = line.split()
                if len(parts) >= 3:  # Need at least fft(real)
                    try:
                        data[current_signal].append(float(parts[2]))  # fft(real)
                    except (ValueError, IndexError):
                        pass
    

    
    # Create the DataFrame
    df_data = {
        'ID': list(signals_dict.keys()),
        'Signal_number': list(signals_dict.values()),
        #'Refrence frequency [Hz]': reference_frequency_hz,
        'TissueType': ['no label found'] * len(signals_dict)
    }
    
    # Add intensities
    for i in range(number_of_points):
        column_values = []
        for label, signal in signals_dict.items():
            if signal in data and i < len(data[signal]):
                column_values.append(data[signal][i])
            else:
                column_values.append(nan)
        df_data[f'PPM_{i}'] = column_values
    
    # Create the DataFrame
    dataTable = DataFrame(df_data)
    
    # Calculate spectroscopy parameters
    dwell_time_s = sampling_interval * 1e-3  # Convert ms to s
    spectral_width_hz = 1 / dwell_time_s
    frequency_resolution = spectral_width_hz / number_of_points
    
    # Create a centered frequency axis
    freq_axis_hz = arange(-number_of_points/2, number_of_points/2) * frequency_resolution
    

    if transmitter_freq > 0:
        # Standard formula: PPM = (freq - reference_freq) / (transmitter_freq * 10^-6)
        ppm_axis = (freq_axis_hz - reference_frequency_hz) / (transmitter_freq * 1e-6)
    else:
        # If no transmitter frequency, just use frequency in Hz
        ppm_axis = freq_axis_hz - reference_frequency_hz

    
    if not has_reference_frequency and transmitter_freq > 0:
        # Set 0 ppm as the new center reference
        center_freq_hz = freq_axis_hz[len(freq_axis_hz) // 2]
        reference_frequency_hz = center_freq_hz - (reference_frequency_hz * transmitter_freq * 1e-6)
    
    # Recalculate ppm_axis with this reference frequency
    ppm_axis = (freq_axis_hz - reference_frequency_hz) / (transmitter_freq * 1e-6)
    
    # Update the reference frequency in the dataTable
    df_data['Refrence frequency [Hz]'] = reference_frequency_hz
    
    # For spectroscopy display, ensure PPM axis decreases from left to right
    if ppm_axis[0] < ppm_axis[-1]:
        ppm_axis = flip(ppm_axis)
        # Since we've already flipped the data, we need to flip the columns too
        ppm_columns = [f'PPM_{i}' for i in range(number_of_points)]
        dataTable[ppm_columns] = dataTable[ppm_columns].iloc[:, ::-1]
    
    # Get PPM bounds
    firstPPM = min(ppm_axis)
    lastPPM = max(ppm_axis)
    
    # Adjust ppm_range if needed
    if ppm_range[0] < firstPPM:
        ppm_range[0] = firstPPM
    if ppm_range[1] > lastPPM:
        ppm_range[1] = lastPPM
    
    # Function to find index closest to a PPM value
    def get_PPM(ppm_value, ppm_axis):
        return abs(ppm_axis - ppm_value).argmin()
    
    # Get indices for filtering
    start_idx = get_PPM(ppm_range[0], ppm_axis)
    end_idx = get_PPM(ppm_range[1], ppm_axis)
    
    # Ensure start_idx <= end_idx
    if start_idx > end_idx:
        start_idx, end_idx = end_idx, start_idx
    
    points_filtered = end_idx - start_idx + 1
    
    # Build the list of columns to keep
    #filtered_columns = ['ID', 'TissueType', 'Refrence frequency [Hz]', 'Signal_number'] + [f'PPM_{i}' for i in range(start_idx, end_idx+1)]
    filtered_columns = ['ID', 'TissueType', 'Signal_number'] + [f'PPM_{i}' for i in range(start_idx, end_idx+1)]
    filtered_dataTable = dataTable[filtered_columns]
    
    # Extract final x-axis
    xaxis = ppm_axis[start_idx:end_idx+1]
    
    return firstPPM, lastPPM, points_filtered, xaxis, filtered_dataTable



def read_list_of_jmrui_text(file_paths, ppm_range,  statusbar=None):
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
        firstPPM, lastPPM, number_of_points,xaxis,filtered_dataTable = read_jmrui_text_data(filepath=filepath,
                                                                                       ppm_range=ppm_range)
        dfs.append(filtered_dataTable)
        
        # Store parameters from the last file (or you could select specific ones)
        firstPPM, lastPPM, number_of_points = firstPPM, lastPPM, number_of_points
        xaxis =xaxis
    
    # Combine all data tables
    dataTable = concat(dfs, axis=0)
   
    update_status(statusbar,f"{len(dfs)} xml files processed")
    
    return firstPPM, lastPPM, number_of_points, xaxis, dataTable
