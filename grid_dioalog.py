from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, 
    QLabel, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt
from plot_settings import calculate_grid_dimensions
class GridConfigDialog(QDialog):
    def __init__(self, parent=None, auto_grid=True, rows=2, cols=2, num_plots=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Grid Layout")
        self.resize(300, 170)
        
        # Store the number of plots for auto calculation
        self.num_plots = num_plots
        
        # Calculate auto grid dimensions if num_plots is provided
        if self.num_plots:
            from plot_settings import calculate_grid_dimensions
            self.auto_cols, self.auto_rows = calculate_grid_dimensions(self.num_plots)
        else:
            self.auto_cols, self.auto_rows = 2, 2  # Default if no plots selected
        
        self.manual_rows = rows
        self.manual_cols = cols

        # Main layout
        layout = QVBoxLayout(self)
        
        # Auto grid checkbox with calculated dimensions
        auto_text = "Automatically determine grid layout"
        if self.num_plots and auto_grid:
            auto_text += f" ({self.auto_rows}×{self.auto_cols})"
        
        self.auto_grid = QCheckBox(auto_text)
        self.auto_grid.setChecked(auto_grid)
        layout.addWidget(self.auto_grid)
        
        # Row and column controls
        grid_layout = QHBoxLayout()
        
        # Row control
        row_layout = QHBoxLayout()
        row_label = QLabel("Rows:")
        self.row_input = QSpinBox()
        self.row_input.setMinimum(1)
        self.row_input.setMaximum(10)
        self.row_input.setValue(rows)
        row_layout.addWidget(row_label)
        row_layout.addWidget(self.row_input)
        
        # Column control
        col_layout = QHBoxLayout()
        col_label = QLabel("Columns:")
        self.col_input = QSpinBox()
        self.col_input.setMinimum(1)
        self.col_input.setMaximum(10)
        self.col_input.setValue(cols)
        col_layout.addWidget(col_label)
        col_layout.addWidget(self.col_input)
        
        # Add row and column controls to grid layout
        grid_layout.addLayout(row_layout)
        grid_layout.addLayout(col_layout)
        layout.addLayout(grid_layout)

        self.auto_grid.stateChanged.connect(self.update_controls_enabled)
        
        # Initial state update
        self.update_controls_enabled(
            Qt.CheckState.Checked if self.auto_grid.isChecked() else Qt.CheckState.Unchecked
        )
        
        # Add some information about how manual settings work
        self.manual_note = QLabel("Uncheck auto mode to customize grid dimension")
        self.manual_note.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.manual_note)
        
        # Connect auto grid checkbox to enable/disable row/col controls
        self.auto_grid.stateChanged.connect(self.update_controls_enabled)
        
        # Initial state update
        self.update_controls_enabled(
            Qt.CheckState.Checked if self.auto_grid.isChecked() else Qt.CheckState.Unchecked
        )
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def update_controls_enabled(self, state):
        """Enable/disable row and column inputs based on Auto checkbox state"""
        enabled = not self.auto_grid.isChecked()
        
        # Set enabled state for the inputs
        self.row_input.setEnabled(enabled)
        self.col_input.setEnabled(enabled)
        self.manual_note.setVisible(enabled) 
        
    def get_settings(self):
            """Return the current grid settings"""
            if self.auto_grid.isChecked():
                # Return the auto-calculated values when auto grid is enabled
                return {
                    'auto_grid': True,
                    'rows': self.auto_rows,
                    'cols': self.auto_cols
                }
            else:
                # Return user-specified values when auto grid is disabled
                return {
                    'auto_grid': False,
                    'rows': self.row_input.value(),
                    'cols': self.col_input.value()
                }
            
    def update_controls_enabled(self, state):
        """Enable/disable and update row and column inputs based on Auto checkbox state"""
        is_auto = self.auto_grid.isChecked()
        
        if is_auto:
            # When switching to auto, store current manual values and show auto values
            self.manual_rows = self.row_input.value()
            self.manual_cols = self.col_input.value()
            self.row_input.setValue(self.auto_rows)
            self.col_input.setValue(self.auto_cols)
        else:
            # When switching to manual, restore manual values
            self.row_input.setValue(self.manual_rows)
            self.col_input.setValue(self.manual_cols)
        
        # Set enabled state for the inputs
        self.row_input.setEnabled(not is_auto)
        self.col_input.setEnabled(not is_auto)
    
    def accept(self):
        if not self.auto_grid.isChecked() and self.num_plots:
            total_cells = self.row_input.value() * self.col_input.value()
            if total_cells < self.num_plots:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Grid", 
                                f"Grid ({self.row_input.value()}×{self.col_input.value()}) too small for {self.num_plots} plots")
                return
        super().accept()