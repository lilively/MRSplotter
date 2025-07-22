from numpy import float32, floating, int32, integer, issubdtype, zeros, column_stack, unique, where, isin, nan
from pandas import isna, notna, DataFrame

class TableReading:
    """A high-performance replacement for pandas DataFrame specifically for MRS data"""
    
    def __init__(self, dataframe=None):
        # Initialize from a pandas DataFrame if provided
        if dataframe is not None:
            self.initialize_from_dataframe(dataframe)
        else:
            self.columns = []
            self.column_types = {}
            self.column_indices = {}
            self.data = None
            self.string_maps = {}
            self.reverse_string_maps = {}
    
    def initialize_from_dataframe(self, df):
        """Initialize the FastDataTable from a pandas DataFrame"""
        # Store column names
        self.columns = list(df.columns)
        
        # Create mapping from column name to index
        self.column_indices = {col: i for i, col in enumerate(self.columns)}
        
        # Determine the type of each column
        self.column_types = {}
        self.string_maps = {}
        self.reverse_string_maps = {}
        
        # Convert to appropriate numpy arrays for each type
        arrays = []
        
        for col in self.columns:
            if df[col].dtype == 'object' or df[col].dtype == 'category':
                # For string/object columns, create a mapping to integers for efficiency
                unique_values = df[col].dropna().unique()
                value_to_int = {val: i for i, val in enumerate(unique_values)}
                int_to_value = {i: val for i, val in enumerate(unique_values)}
                
                # Store the mappings
                self.string_maps[col] = value_to_int
                self.reverse_string_maps[col] = int_to_value
                
                # Convert strings to integers using the mapping
                int_array = zeros(len(df), dtype=int32)
                int_array.fill(-1)  # -1 will represent NaN
                
                for i, val in enumerate(df[col]):
                    if notna(val):
                        int_array[i] = value_to_int.get(val, -1)
                
                arrays.append(int_array)
                self.column_types[col] = 'string'
            
            elif issubdtype(df[col].dtype, integer):
                # For integer columns
                arrays.append(df[col].fillna(-9999).to_numpy(dtype=int32))
                self.column_types[col] = 'int'
            
            elif issubdtype(df[col].dtype, floating):
                # For float columns
                arrays.append(df[col].fillna(nan).to_numpy(dtype=float32))
                self.column_types[col] = 'float'
            
            else:
                # Default to float for unknown types
                arrays.append(df[col].fillna(nan).to_numpy(dtype=float32))
                self.column_types[col] = 'float'
        
        # Stack arrays horizontally to create the data matrix
        self.data = column_stack(arrays)
    
    def get_row(self, idx):
        """Get a row as a dictionary"""
        if idx < 0 or idx >= self.data.shape[0]:
            return None
        
        row = {}
        for col in self.columns:
            col_idx = self.column_indices[col]
            value = self.data[idx, col_idx]
            
            # Convert value based on column type
            if self.column_types[col] == 'string':
                if value == -1:
                    row[col] = None
                else:
                    row[col] = self.reverse_string_maps[col].get(value)
            else:
                row[col] = value
        
        return row
    
    def set_value(self, row_idx, col, value):
        """Set a specific value in the data table"""
        if col not in self.column_indices:
            return False
        
        col_idx = self.column_indices[col]
        
        if self.column_types[col] == 'string':
            if isna(value):
                self.data[row_idx, col_idx] = -1
            else:
                # Handle string values
                string_val = str(value)
                if string_val in self.string_maps[col]:
                    self.data[row_idx, col_idx] = self.string_maps[col][string_val]
                else:
                    # Add new string value to mapping
                    new_idx = len(self.string_maps[col])
                    self.string_maps[col][string_val] = new_idx
                    self.reverse_string_maps[col][new_idx] = string_val
                    self.data[row_idx, col_idx] = new_idx
        
        else:
            # Handle numeric values
            try:
                if isna(value):
                    if self.column_types[col] == 'float':
                        self.data[row_idx, col_idx] = nan
                    else:
                        self.data[row_idx, col_idx] = -9999  # NaN representation for int
                else:
                    self.data[row_idx, col_idx] = value
            except ValueError:
                return False
        
        return True
    
    def get_unique_values(self, col):
        """Get unique values for a column"""
        if col not in self.column_indices:
            return []
        
        col_idx = self.column_indices[col]
        
        if self.column_types[col] == 'string':
            # For string columns, use the reverse mapping
            unique_indices = unique(self.data[:, col_idx])
            unique_indices = unique_indices[unique_indices >= 0]  # Remove NaN (-1)
            
            return [self.reverse_string_maps[col].get(idx) for idx in unique_indices]
        else:
            # For numeric columns
            unique_values = unique(self.data[:, col_idx])
            if self.column_types[col] == 'int':
                unique_values = unique_values[unique_values != -9999]  # Remove NaN placeholder
            return unique_values.tolist()
    
    def filter_rows(self, col, values):
        """Get indices of rows where column values match the given values"""
        if col not in self.column_indices:
            return []
        
        col_idx = self.column_indices[col]
        
        if self.column_types[col] == 'string':
            # Convert string values to their numeric representations
            numeric_values = [self.string_maps[col].get(val, -1) for val in values]
            return where(isin(self.data[:, col_idx], numeric_values))[0]
        else:
            return where(isin(self.data[:, col_idx], values))[0]
    
    def to_dataframe(self):
        """Convert back to pandas DataFrame"""
        df_data = {}
        
        for col in self.columns:
            col_idx = self.column_indices[col]
            col_data = self.data[:, col_idx]
            
            if self.column_types[col] == 'string':
                # Convert numeric representations back to strings
                string_data = []
                for val in col_data:
                    if val == -1:
                        string_data.append(None)
                    else:
                        string_data.append(self.reverse_string_maps[col].get(val))
                df_data[col] = string_data
            
            elif self.column_types[col] == 'int':
                # Convert special placeholder back to NaN
                int_data = col_data.copy()
                int_data[int_data == -9999] = nan
                df_data[col] = int_data
            
            else:
                df_data[col] = col_data
        
        return DataFrame(df_data)
    
    def update_from_filtered(self, filtered_data, filter_indices=None):
        """Update data based on a filtered version that was modified"""
        if isinstance(filtered_data, TableReading):
            # If filtered_data is already a FastDataTable
            filtered_numpy = filtered_data.data
            for i, orig_idx in enumerate(filter_indices):
                self.data[orig_idx] = filtered_numpy[i]
        else:
            # Convert pandas DataFrame to FastDataTable first
            filtered_table = TableReading(filtered_data)
            self.update_from_filtered(filtered_table, filter_indices)
    
    def get_subset(self, indices):
        """Get a subset of rows using the provided indices"""
        if len(indices) == 0:
            return None
        
        subset = TableReading()
        subset.columns = self.columns.copy()
        subset.column_indices = self.column_indices.copy()
        subset.column_types = self.column_types.copy()
        subset.string_maps = self.string_maps.copy()
        subset.reverse_string_maps = self.reverse_string_maps.copy()
        
        # Select rows by indices
        subset.data = self.data[indices].copy()
        
        return subset
    
    @property
    def shape(self):
        """Get the shape of the data"""
        if self.data is None:
            return (0, 0)
        return self.data.shape