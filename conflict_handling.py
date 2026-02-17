from re import sub, split as re_split
from status import update_status


def sort_numbers(s):
    """Sort key that handles embedded numbers naturally.
    'Source 2' comes before 'Source 10', '***' is always last."""
    s = str(s)
    if s == '***':
        return (1,)
    return (0,) + tuple(
        int(part) if part.isdigit() else part.casefold()
        for part in re_split(r'(\d+)', s)
    )


def sanitize_filename(name):
    """Sanitize filenames by replacing invalid characters"""
    # Convert to string in case name is not a string
    original = str(name)
    
    # Replace characters that are invalid in filenames
    sanitized = sub(r'[\\/*?:"<>|]', '_', original)
    
    # Check if the name is empty, consists only of whitespace, 
    # or if all characters were replaced with underscores
    if not sanitized or sanitized.isspace() or sanitized.count('_') == len(sanitized):
        sanitized = "unnamed_label"
        
    return sanitized

def validate_ppm_range(ppm_range, firstPPM, lastPPM, statusbar=None, parent=None):
    """
    Validate and adjust PPM range to stay within data boundaries
    
    Parameters:
    ppm_range (list): [first_ppm, last_ppm] range to validate
    firstPPM (float): Minimum available PPM in the data
    lastPPM (float): Maximum available PPM in the data
    statusbar: Optional statusbar for notifications
    
    Returns:
    list: Adjusted [first_ppm, last_ppm] range
    """
    # Create a copy to avoid modifying the original
    valid_range = list(ppm_range)
    
    # Track if adjustments were made
    adjustments_made = False
    
    # Ensure PPM range is within data bounds
    if valid_range[0] < firstPPM:
        valid_range[0] = firstPPM
        adjustments_made = True
    
    if valid_range[1] > lastPPM:
        valid_range[1] = lastPPM
        adjustments_made = True
    
    # Show adjustment message if needed
    if adjustments_made and statusbar:
        update_status(statusbar, f"PPM range adjusted to fit data bounds: {valid_range[0]:.2f}ppm, {valid_range[1]:.2f} ppm from file.")
            # Show a popup dialog if parent is provided
    if adjustments_made and parent:
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("PPM Range Adjusted")
        msg.setText("The PPM range has been adjusted to fit data boundaries.")
        msg.setInformativeText(f"Using range: {valid_range[0]:.2f} ppm to {valid_range[1]:.2f} ppm")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    return tuple(valid_range)
