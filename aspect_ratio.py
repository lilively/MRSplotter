def calculate_figure_size(dataTable, canvas_width=None, canvas_height=None, dpi=100, base_size=12):
    """
    Calculate figure size based on grid aspect ratio from x_pos and y_pos.
    
    Parameters:
    -----------
    dataTable : DataFrame
        Data table containing x_pos and y_pos columns
    canvas_width : int, optional
        Canvas width in pixels
    canvas_height : int, optional
        Canvas height in pixels
    dpi : int
        DPI for figure (default: 100)
    base_size : float
        Base size in inches for default sizing (default: 12)
    
    Returns:
    --------
    tuple : (width_inches, height_inches)
    """
    # Get unique x and y positions
    x_values = sorted([int(float(x)) for x in dataTable['x_pos'].unique()])
    y_values = sorted([int(float(y)) for y in dataTable['y_pos'].unique()])
    xlen = len(x_values)
    ylen = len(y_values)
    
    # Calculate aspect ratio (width/height)
    aspect_ratio = xlen / ylen
    
    # Calculate figure size
    if canvas_width is not None and canvas_height is not None:
        # Use provided canvas dimensions but adjust to match grid aspect ratio
        if aspect_ratio >= 1:  # Wider than tall
            width_inches = canvas_width / dpi
            height_inches = width_inches / aspect_ratio
        else:  # Taller than wide
            height_inches = canvas_height / dpi
            width_inches = height_inches * aspect_ratio
    else:
        # Default: base size adjusted by aspect ratio
        if aspect_ratio >= 1:
            width_inches = base_size
            height_inches = base_size / aspect_ratio
        else:
            width_inches = base_size * aspect_ratio
            height_inches = base_size
    
    return (width_inches, height_inches)