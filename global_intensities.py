from numpy import nanmax, nanmin, isnan, isinf
def calculate_y_limit(dataTable, include_mean, include_sdev):
    """
    Calculate the global minimum and maximum intensity values across tissue types.
    Parameters:
        dataTable (pd.DataFrame): The data table containing tissue information.
        include_mean (bool): If True, use mean values for limit calculation.
        include_sdev (bool): If True, include standard deviation in the min/max calculation.
    Returns:
        tuple: (global_minIntensity, global_maxIntensity)
    """    
    tissueTypes = dataTable['TissueType'].unique()
    minimum_list = []
    maximum_list = []
    
    for elem in tissueTypes:
        # Filter and calculate
        filteredTable = dataTable[dataTable['TissueType'] == elem]
        filteredIntensity = filteredTable[[col for col in filteredTable.columns if col.startswith('PPM_')]]
        
        # Get count of spectra in this group
        spectra_count = len(filteredTable)
        
        if include_mean:
            meanIntensity = filteredIntensity.mean(axis=0)
            
            # Only calculate standard deviation if there are at least 2 spectra
            # This prevents the single-spectrum NaN/inf problem
            if include_sdev and spectra_count > 1:
                sdevIntensity = filteredIntensity.std(axis=0)
                minIntensity = nanmin(meanIntensity - sdevIntensity)
                maxIntensity = nanmax(meanIntensity + sdevIntensity)
            else:
                # For single spectrum or when std dev not needed, just use mean
                minIntensity = nanmin(meanIntensity)
                maxIntensity = nanmax(meanIntensity)
        else:
            # When showing individual spectra
            minIntensity = nanmin(filteredIntensity.values)
            maxIntensity = nanmax(filteredIntensity.values)
        
        # Only add valid values
        if not (isnan(minIntensity) or isinf(minIntensity)):
            minimum_list.append(minIntensity)
        if not (isnan(maxIntensity) or isinf(maxIntensity)):
            maximum_list.append(maxIntensity)
    
    # Make sure we have valid values
    if not minimum_list or not maximum_list:
        return -1, 1
    
    # Compute global min and max
    global_minIntensity = min(minimum_list)
    global_maxIntensity = max(maximum_list)
    
    return global_minIntensity, global_maxIntensity