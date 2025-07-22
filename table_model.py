from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from numpy import zeros, column_stack, unique, nan, isnan, int32, float32
from numpy import float32, floating, int32, integer, issubdtype, zeros, column_stack, unique, nan
from pandas import isna, notna, DataFrame
from conflict_handling import sanitize_filename


class TableModel(QAbstractTableModel):
    """High-performance table model using NumPy arrays for faster data handling"""
    
    def __init__(self, dataframe):
        super().__init__()
        # Store original dataframe for reference
        self._original_df = dataframe.copy()
        
        # Store column information
        self.columns = list(dataframe.columns)
        self.column_types = {}
        
        # Map columns to indices for quick lookup
        self.column_indices = {col: i for i, col in enumerate(self.columns)}
        
        # Determine column types and create string mappings for categorical columns
        self.string_maps = {}
        self.reverse_string_maps = {}
        
        # Convert to numpy arrays for performance
        arrays = []
        
        for col in self.columns:
            # Determine data type
            if dataframe[col].dtype == 'object' or dataframe[col].dtype == 'category':
                # For string/object columns, create a mapping to integers
                unique_values = dataframe[col].dropna().unique()
                value_to_int = {val: i for i, val in enumerate(unique_values)}
                int_to_value = {i: val for i, val in enumerate(unique_values)}
                
                # Store mappings
                self.string_maps[col] = value_to_int
                self.reverse_string_maps[col] = int_to_value
                
                # Convert to integer representation
                int_array = zeros(len(dataframe), dtype=int32)
                int_array.fill(-1)  # -1 represents NaN
                
                for i, val in enumerate(dataframe[col]):
                    if notna(val):
                        int_array[i] = value_to_int.get(val, -1)
                
                arrays.append(int_array)
                self.column_types[col] = 'string'
            
            elif issubdtype(dataframe[col].dtype, integer):
                # Integer columns
                arrays.append(dataframe[col].fillna(-9999).to_numpy(dtype=int32))
                self.column_types[col] = 'int'
            
            elif issubdtype(dataframe[col].dtype, floating):
                # Float columns
                arrays.append(dataframe[col].fillna(nan).to_numpy(dtype=float32))
                self.column_types[col] = 'float'
            
            else:
                # Default to float for unknown types
                arrays.append(dataframe[col].fillna(nan).to_numpy(dtype=float32))
                self.column_types[col] = 'float'
        
        # Stack arrays horizontally for the data matrix
        self.data_array = column_stack(arrays)
        
    def rowCount(self, parent=QModelIndex()):
        return self.data_array.shape[0]
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        row, col = index.row(), index.column()
        if row >= self.data_array.shape[0] or col >= len(self.columns):
            return None
        
        column_name = self.columns[col]
        value = self.data_array[row, col]
        
        if role == Qt.ItemDataRole.DisplayRole:
            # Format the value based on column type
            if self.column_types[column_name] == 'string':
                if value == -1:
                    return ""
                return str(self.reverse_string_maps[column_name].get(value, ""))
            
            elif self.column_types[column_name] == 'float':
                if isnan(value):
                    return ""
                # Format floating point numbers
                return f"{value:.6f}" if abs(value) < 0.0001 else f"{value:.4f}"
            
            elif self.column_types[column_name] == 'int':
                if value == -9999:  # NaN placeholder
                    return ""
                return str(int(value))
            
            else:
                return str(value)
        
        return None
        
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal and section < len(self.columns):
                return self.columns[section]
            if orientation == Qt.Orientation.Vertical and section < self.data_array.shape[0]:
                return str(section)
        return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
            
        column_name = self.columns[index.column()]
        
        # Make specific columns editable
        if column_name == 'TissueType':
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        elif self.column_types[column_name] in ['float', 'int']:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
            
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    
    def cleanup_string_mappings(self, column_name):
        """Remove unused entries from string mappings for a specific column"""
        if column_name not in self.column_indices or self.column_types[column_name] != 'string':
            return
            
        col_idx = self.column_indices[column_name]
        
        # Get all unique indices actually used in the data array
        used_indices = set(int(idx) for idx in unique(self.data_array[:, col_idx]) if idx >= 0)
        
        # Find indices that are in the mapping but not used in the data
        all_indices = set(self.reverse_string_maps[column_name].keys())
        unused_indices = all_indices - used_indices
        
        # If no unused indices, nothing to do
        if not unused_indices:
            return
            
        # Create new mappings
        values_to_keep = [self.reverse_string_maps[column_name][idx] for idx in used_indices]
        
        # Create new clean mappings
        new_string_map = {}
        new_reverse_map = {}
        
        for new_idx, value in enumerate(values_to_keep):
            new_string_map[value] = new_idx
            new_reverse_map[new_idx] = value
            
        # Update data array with new indices
        for old_idx in used_indices:
            value = self.reverse_string_maps[column_name][old_idx]
            new_idx = new_string_map[value]
            # Replace old index with new index in the data array
            self.data_array[:, col_idx][self.data_array[:, col_idx] == old_idx] = new_idx
            
        # Replace the old mappings with new ones
        self.string_maps[column_name] = new_string_map
        self.reverse_string_maps[column_name] = new_reverse_map

    def sanitize_input(self, value):
        """Sanitize input string to handle problematic characters"""
        if value is None:
            return None
            
        # Convert to string
        string_val = str(value).strip()
        
        # Replace problematic single characters with safer alternatives if needed
        if string_val == ')':
            return 'right_paren'
        if string_val == '(':
            return 'left_paren'
        if string_val == '[':
            return 'left_bracket'
        if string_val == ']':
            return 'right_bracket'
        
        # Or just return the value as is
        return string_val
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
            
        row, col = index.row(), index.column()
        if row >= self.data_array.shape[0] or col >= len(self.columns):
            return False
            
        column_name = self.columns[col]
        
        try:
            # For string columns
            if self.column_types[column_name] == 'string':
                if not value or isna(value):
                    self.data_array[row, col] = -1  # Represents NaN for strings
                    self.dataChanged.emit(index, index)
                else:
                    # Sanitize the input value using the existing sanitize_filename function
                    # This will handle all problematic characters consistently
                    string_val = sanitize_filename(value)
                    
                    # Check if the value exists in our mapping
                    if string_val in self.string_maps[column_name]:
                        # Use existing mapping
                        self.data_array[row, col] = self.string_maps[column_name][string_val]
                    else:
                        # Add new value to mappings
                        new_idx = len(self.string_maps[column_name])
                        self.string_maps[column_name][string_val] = new_idx
                        self.reverse_string_maps[column_name][new_idx] = string_val
                        self.data_array[row, col] = new_idx
                    
                    self.dataChanged.emit(index, index)
            
            # For float columns
            elif self.column_types[column_name] == 'float':
                if not value or isna(value):
                    self.data_array[row, col] = nan
                else:
                    self.data_array[row, col] = float(value)
                self.dataChanged.emit(index, index)
            
            # For integer columns
            elif self.column_types[column_name] == 'int':
                if not value or isna(value):
                    self.data_array[row, col] = -9999  # NaN placeholder
                else:
                    self.data_array[row, col] = int(value)
                self.dataChanged.emit(index, index)
            
            # Generic case
            else:
                if not value or isna(value):
                    self.data_array[row, col] = nan
                else:
                    self.data_array[row, col] = value
                self.dataChanged.emit(index, index)
                    
            return True
            
        except (ValueError, TypeError) as e:
            print(f"Error setting data: {e}")
            return False
    
    def get_data(self):
        """Return the current dataframe - for compatibility with PandasTableModel"""
        return self.get_data_frame()

    def get_unique_values(self, column_name):
        """Get unique values for a column"""
        if column_name not in self.column_indices:
            return []
        
        col_idx = self.column_indices[column_name]
        
        if self.column_types[column_name] == 'string':
            # For string columns
            unique_indices = unique(self.data_array[:, col_idx])
            unique_indices = unique_indices[unique_indices >= 0]  # Remove NaN (-1)
            
            return [self.reverse_string_maps[column_name].get(idx) for idx in unique_indices]
        else:
            # For numeric columns
            unique_values = unique(self.data_array[:, col_idx])
            if self.column_types[column_name] == 'int':
                unique_values = unique_values[unique_values != -9999]  # Remove NaN placeholder
            return unique_values.tolist()
    
    def filter_by_value(self, column_name, value):
        """Get a filtered view of the data"""
        if column_name not in self.column_indices:
            return self.data_array.copy()
            
        col_idx = self.column_indices[column_name]
        
        if self.column_types[column_name] == 'string':
            if value == "All":
                return self.data_array.copy()
                
            # Convert string value to numeric
            numeric_value = self.string_maps[column_name].get(value, -1)
            mask = self.data_array[:, col_idx] == numeric_value
            return self.data_array[mask].copy()
        else:
            if value == "All":
                return self.data_array.copy()
                
            # For numeric filter
            mask = self.data_array[:, col_idx] == value
            return self.data_array[mask].copy()
    
    def get_data_frame(self):
        """Convert back to pandas DataFrame"""
        import pandas as pd
        
        data_dict = {}
        
        for col in self.columns:
            col_idx = self.column_indices[col]
            col_data = self.data_array[:, col_idx]
            
            # Convert based on column type
            if self.column_types[col] == 'string':
                # Convert numeric representations back to strings
                string_data = []
                for val in col_data:
                    if val == -1:
                        string_data.append(None)
                    else:
                        string_data.append(self.reverse_string_maps[col].get(val))
                data_dict[col] = string_data
            
            elif self.column_types[col] == 'int':
                # Convert special placeholder back to NaN
                int_data = col_data.copy()
                int_data[int_data == -9999] = nan
                data_dict[col] = int_data
            
            else:
                data_dict[col] = col_data
        
        return DataFrame(data_dict)
    
    def reset_data(self):
        """Reset to original data"""
        # Reinitialize from the original dataframe
        self.__init__(self._original_df)
        self.layoutChanged.emit()