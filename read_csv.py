from pandas import read_csv, DataFrame, concat
import pandas as pd
from numpy import array, linspace, flip
from pathlib import Path
from status import update_status
from io import StringIO


def safe_ppm_range_check(ppm_range, xaxis):
    """
    Safely check and validate PPM range against xaxis.
    
    Parameters:
    -----------
    ppm_range : tuple or None
        Range of PPM values to filter (min_ppm, max_ppm)
    xaxis : numpy.ndarray
        Array of PPM values
    
    Returns:
    --------
    tuple
        Validated PPM range or None if invalid
    """
    if ppm_range is None or len(xaxis) == 0:
        return None
    
    try:
        min_ppm, max_ppm = ppm_range
        xaxis_min, xaxis_max = float(xaxis.min()), float(xaxis.max())
        
        # Ensure the range makes sense
        if min_ppm > max_ppm:
            print(f"Warning: Invalid PPM range {ppm_range} - min > max")
            return None
            
        # Check if range overlaps with available data
        if max_ppm < xaxis_min or min_ppm > xaxis_max:
            print(f"Warning: PPM range {ppm_range} doesn't overlap with data range [{xaxis_min:.2f}, {xaxis_max:.2f}]")
            return None
            
        return (min_ppm, max_ppm)
        
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error validating PPM range: {e}")
        return None


def read_structured_csv(file_path, ppm_range):
    """
    A robust function to read a structured CSV file that contains metadata, 
    and data table, handling the format exported by DataEditorDialog.
    Now handles Excel-modified files with extra empty rows/columns.
    
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
    
    try:
        # First pass: Parse the file line by line
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()
            
        # Detect delimiter from the entire file content
        file_content = ''.join(lines)
        delimiter = detect_delimiter(file_content)
        #print(f"Detected delimiter: '{delimiter}'")
        
        # Process lines
        for line_num, line in enumerate(lines):
            line = line.strip()
            
            # Skip completely empty lines
            if not line:
                continue
            
            # Handle metadata lines
            if line.startswith('#'):
                if current_state == STATE_INIT:
                    current_state = STATE_METADATA
                
                # Parse metadata
                line = line.lstrip('#').strip()
                
                # Try to extract key-value pairs
                if delimiter in line:
                    parts = line.split(delimiter, 1)
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        value_part = parts[1].strip()
                        
                        # Handle Excel's extra delimiters - take only the first non-empty value
                        if delimiter in value_part:
                            value_candidates = [v.strip() for v in value_part.split(delimiter)]
                            # Find the first non-empty value
                            value = next((v for v in value_candidates if v), '')
                        else:
                            value = value_part
                        
                        # Only store non-empty values
                        if key and value:
                            metadata[key] = value
                continue
            
            # Handle data table lines
            if current_state in [STATE_METADATA, STATE_INIT]:
                current_state = STATE_DATA
            
            # Check if this looks like a header line (contains column names)
            if current_state == STATE_DATA:
                # Skip lines that are just delimiters (Excel artifacts)
                if line.replace(delimiter, '').strip() == '':
                    continue
                    
                data_lines.append(line)
        

        
        # Parse the data table from the collected lines
        if data_lines:
            # Find the real header line (should contain ID, TissueType, PPM_0, etc.)
            header_line_idx = None
            
            for i, line in enumerate(data_lines):
                # Look for a line that contains expected column patterns
                if ('ID' in line and 'TissueType' in line and 'PPM_' in line) or \
                   ('id' in line.lower() and ('tissue' in line.lower() or 'type' in line.lower())):
                    header_line_idx = i
                    break
            
            if header_line_idx is not None:
                # Use the real header and data after it
                header_line = data_lines[header_line_idx]
                data_content = '\n'.join([header_line] + data_lines[header_line_idx + 1:])
            else:
                # Fallback: skip lines that look like Excel artifacts
                filtered_lines = []
                skip_next = False
                
                for line in data_lines:
                    # Skip lines that are just "Column1;Column2;..." patterns
                    if line.startswith('Column1' + delimiter) or \
                       all(part.strip().startswith('Column') and part.strip()[6:].replace(delimiter, '').isdigit() 
                           for part in line.split(delimiter)[:5] if part.strip()):
                        continue
                    filtered_lines.append(line)
                
                data_content = '\n'.join(filtered_lines)
            
            # Join lines and create StringIO
            data_csv = StringIO(data_content)
            
            try:
                # Read with detected delimiter
                data_table = read_csv(data_csv, delimiter=delimiter, on_bad_lines='skip')

                data_table = clean_dataframe(data_table)
 
            except Exception as e:
                data_table = DataFrame()
        else:
            data_table = DataFrame()
    
    except Exception as e:
        return 0, 0, 0, array([]), DataFrame()
    
    # Extract PPM values from metadata
    try:
        firstPPM = float(metadata.get('First PPM', 0))
        lastPPM = float(metadata.get('Last PPM', 0))
        number_of_points = int(metadata.get('Number of points', 0))
        
        
        # Validate the values before generating xaxis
        if number_of_points > 0 and firstPPM != lastPPM:
            # Generate xaxis based on metadata
            xaxis = flip(linspace(firstPPM, lastPPM, number_of_points))
        else:
            xaxis = array([])
            
    except (ValueError, TypeError) as e:
        # Default values if metadata extraction fails
        firstPPM = 0
        lastPPM = 0
        number_of_points = 0
        xaxis = array([])
    

    validated_ppm_range = safe_ppm_range_check(ppm_range, xaxis)
    if ppm_range is not None and validated_ppm_range is None:
        print(f"Warning: PPM range validation failed for {ppm_range}")

    return firstPPM, lastPPM, number_of_points, xaxis, data_table


def detect_delimiter(text):
    """
    Detect the delimiter used in CSV text.
    
    Parameters:
    -----------
    text : str
        The CSV text to analyze
    
    Returns:
    --------
    str
        The detected delimiter (';', ',', '\t', or '|')
    """
    # Count occurrences of potential delimiters in the first few lines
    lines = text.split('\n')[:5]  # Check first 5 lines
    delimiters = [';', ',', '\t', '|']
    delimiter_counts = {}
    
    for delimiter in delimiters:
        count = sum(line.count(delimiter) for line in lines if line.strip())
        delimiter_counts[delimiter] = count
    
    # Return the delimiter with the highest count
    if delimiter_counts:
        return max(delimiter_counts, key=delimiter_counts.get)
    else:
        return ','  # Default to comma


def clean_dataframe(df):
    """
    Clean a DataFrame by removing empty rows and columns that Excel might have added.
    Also handles missing expected columns.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to clean
    
    Returns:
    --------
    pandas.DataFrame
        Cleaned DataFrame
    """
    if df.empty:
        return df
    
    original_shape = df.shape
    
    # First, check if we have Excel's "Column1", "Column2" headers that slipped through
    if df.columns[0].startswith('Column') and df.columns[0][6:].isdigit():
        # Try to find the real header row in the data
        for idx, row in df.iterrows():
            row_values = [str(v) for v in row.values if pd.notna(v)]
            row_str = ';'.join(row_values)  # Assuming semicolon delimiter
            
            if ('ID' in row_str and 'TissueType' in row_str and 'PPM_' in row_str):
                # Set this row as the new header
                new_header = row.values
                # Keep data after this row
                df = df.iloc[idx+1:].copy()
                df.columns = new_header
                break
    
    # Remove columns that are completely empty or contain only NaN/whitespace
    cols_to_keep = []
    for col in df.columns:
        # Skip any remaining columns that are just "Column1", "Column2" etc.
        if isinstance(col, str) and col.startswith('Column') and col[6:].replace('Column', '').isdigit():
            continue
            
        # Check if column has any non-null, non-empty values
        if df[col].notna().any():
            # Check if any non-null values are not just whitespace
            non_null_values = df[col].dropna().astype(str).str.strip()
            if not non_null_values.empty and (non_null_values != '').any():
                cols_to_keep.append(col)
    
    if cols_to_keep:
        df = df[cols_to_keep]

    
    # Remove rows that are completely empty or contain only NaN/whitespace
    if not df.empty:
        # Create a mask for rows that have at least one meaningful value
        meaningful_rows = df.apply(
            lambda row: row.notna().any() and 
                       (row.dropna().astype(str).str.strip() != '').any(), 
            axis=1
        )
        df = df[meaningful_rows]

    
    # Reset index after removing rows
    df = df.reset_index(drop=True)
    
    # Add TissueType column if it doesn't exist (for backwards compatibility)
    if not df.empty and 'TissueType' not in df.columns:
        # Try to find a column that might be TissueType
        possible_tissue_cols = [col for col in df.columns if 'tissue' in str(col).lower() or 'type' in str(col).lower()]
        if possible_tissue_cols:
            # Rename the first match to TissueType
            df = df.rename(columns={possible_tissue_cols[0]: 'TissueType'})
        else:
            # Add a default TissueType column
            df['TissueType'] = 'Unknown'


    return df


def is_excel_empty_row(line):
    """
    Check if a line represents an Excel-generated empty row.
    Excel often fills empty cells with commas.
    
    Parameters:
    -----------
    line : str
        The line to check
    
    Returns:
    --------
    bool
        True if the line is considered empty
    """
    if not line.strip():
        return True
    
    # Check if line contains only commas and whitespace
    cleaned_line = line.replace(',', '').replace(' ', '').replace('\t', '')
    return not cleaned_line


def read_list_of_csv(file_paths, ppm_range, statusbar=None):
    """
    Read in data from a list of file paths
    Parameters:
    file_paths (list): List of file paths to CSV files
    ppm_range (tuple): Range of PPM values to filter (first_ppm, last_ppm)    
    statusbar: Optional status bar for progress updates
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
            update_status(statusbar, f"Currently reading in {filepath}")
        
        try:
            file_firstPPM, file_lastPPM, file_number_of_points, file_xaxis, filtered_dataTable = read_structured_csv(
                file_path=filepath,
                ppm_range=ppm_range
            )
            
            # Only add non-empty DataFrames
            if not filtered_dataTable.empty:
                dfs.append(filtered_dataTable)
            
            # Store parameters from the last file (or you could select specific ones)
            firstPPM, lastPPM, number_of_points = file_firstPPM, file_lastPPM, file_number_of_points
            xaxis = file_xaxis
            
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            if statusbar is not None:
                update_status(statusbar, f"Error reading {filepath}: {e}")
            continue
    
    # Combine all data tables
    if dfs:
        dataTable = concat(dfs, axis=0, ignore_index=True)
        # Clean the combined DataFrame as well
        dataTable = clean_dataframe(dataTable)
    else:
        dataTable = DataFrame()
   
    # Normalize coordinate column names to match multi-voxel XML convention
    col_renames = {}
    for candidate in ['X_pos', 'Xpos']:
        if candidate in dataTable.columns and 'x_pos' not in dataTable.columns:
            col_renames[candidate] = 'x_pos'
            break
    for candidate in ['Y_pos', 'Ypos']:
        if candidate in dataTable.columns and 'y_pos' not in dataTable.columns:
            col_renames[candidate] = 'y_pos'
            break
    if col_renames:
        dataTable.rename(columns=col_renames, inplace=True)

    # Ensure all PPM columns are numeric (coerce non-numeric values to NaN)
    if not dataTable.empty:
        ppm_cols = [c for c in dataTable.columns if str(c).startswith('PPM_')]
        for col in ppm_cols:
            dataTable[col] = pd.to_numeric(dataTable[col], errors='coerce')

    if statusbar is not None:
        update_status(statusbar, f"{len(dfs)} CSV files processed")

    return firstPPM, lastPPM, number_of_points, xaxis, dataTable