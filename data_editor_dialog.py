from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, 
    QHeaderView, QLabel, QMessageBox, QComboBox,
    QFileDialog, QMenuBar, QApplication, QWidget,
    QSizePolicy, QAbstractItemView 
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QAction, QShortcut
from table_model import TableModel



class DataEditorDialog(QDialog):
    # Add a custom signal for data modification
    dataModified = pyqtSignal(object, bool)  # DataFrame, was_accepted
    
    def __init__(self, dataframe, parent=None, output_directory=None, xaxis = None):
        super().__init__(parent)
        self.setWindowTitle("Data Editor")
        self.resize(1000, 600)
        self.original_df = dataframe.copy()
        self.df = dataframe.copy()
        self.output_directory = output_directory
        self.xaxis = xaxis  
        self.is_fullscreen = False
        self.modified_df = None
        self.result_accepted = False
        # Set window flags to allow minimize/maximize
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a menu bar widget (not attached to window like in QMainWindow)
        menu_widget = QWidget()
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        
        self.menu_bar = QMenuBar()
        menu_layout.addWidget(self.menu_bar)
        
        # Create menus
        self.create_menu_bar()
        
        main_layout.addWidget(menu_widget)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Info and filter area
        info_label = QLabel(f"Total rows: {len(self.df)} | Double-click cells to edit")
        content_layout.addWidget(info_label)
        
        # Filter layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Label:"))
        
        self.label_combo = QComboBox()
        self.label_combo.addItem("All")
        if 'TissueType' in self.df.columns:
            for label in sorted(self.df['TissueType'].unique()):
                self.label_combo.addItem(str(label))
        self.label_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.label_combo)
        filter_layout.addStretch()
        
        content_layout.addLayout(filter_layout)
        
        # Table view
        self.table_view = QTableView()
        self.table_view.setStyleSheet("""
            QTableView {
                border: 1px solid #d0d0d0;
                selection-background-color: #b5d3e7;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                padding: 4px;
            }
        """)
        self.model = TableModel(self.df)
        self.table_view.setModel(self.model)
        
        # Set column widths
        header = self.table_view.horizontalHeader()
        for i in range(len(self.df.columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        # Make the table sortable
        self.table_view.setSortingEnabled(True)
        
        # Make the table expand with the dialog
        self.table_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        content_layout.addWidget(self.table_view)
        
        # Button layout (for OK/Reset/Cancel)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.handle_accept)
        
        reset_button = QPushButton("Reset Changes")
        reset_button.clicked.connect(self.reset_changes)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.handle_reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(reset_button)
        
        content_layout.addLayout(button_layout)
        
        # Add content to main layout
        main_layout.addWidget(content_widget)
        
        # Create a status bar
        self.status_bar = QLabel("Ready")
        self.status_bar.setStyleSheet("background-color: #f0f0f0; padding: 3px; border-top: 1px solid #d0d0d0;")
        main_layout.addWidget(self.status_bar)
        
        # Set up shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Fullscreen toggle (F11)
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        
        # Maximize toggle (Alt+Enter)
        maximize_shortcut = QShortcut(QKeySequence("Alt+Return"), self)
        maximize_shortcut.activated.connect(self.toggle_maximize)
    
    def create_menu_bar(self):
        """Create the menu bar with all menus and actions"""
        # File menu
        file_menu = self.menu_bar.addMenu("Export")
        
        # Export CSV
        export_action = QAction("Export as csv", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_action)

         # Export XML
        export_action_xml = QAction("Export as xml (SpectraClassifier format)", self)
        export_action_xml.setShortcut(QKeySequence("Ctrl+X"))
        export_action_xml.triggered.connect(self.export_to_xml)
        file_menu.addAction(export_action_xml)

    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def apply_filter(self, label):
        """Filter table data based on the selected tissue type label"""
        if label == "All":
            # Reset to unfiltered data
            self.model = TableModel(self.df)
        else:
            # Only use the DataFrame filtering approach for consistency
            filtered_df = self.df[self.df['TissueType'] == label].copy()
            self.model = TableModel(filtered_df)
        
        # Update the table view with the new model
        self.table_view.setModel(self.model)
        
        # Reset column widths
        header = self.table_view.horizontalHeader()
        for i in range(len(self.df.columns)):
            if i < self.model.columnCount():  # Only resize columns that exist in the model
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        # Update the status bar
        self.status_bar.setText(f"Filtered: showing {self.model.rowCount()} of {len(self.df)} rows")

    def keyPressEvent(self, event):
        # Copy (Ctrl+C)
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            selected = self.table_view.selectedIndexes()
            if selected:
                # Sort by row, then by column
                selected.sort(key=lambda x: (x.row(), x.column()))
                rows = sorted(set(index.row() for index in selected))
                cols = sorted(set(index.column() for index in selected))
                
                text = ""
                for r in rows:
                    row_data = []
                    for c in cols:
                        index = self.model.index(r, c)
                        row_data.append(str(self.model.data(index, Qt.ItemDataRole.DisplayRole) or ""))
                    text += "\t".join(row_data) + "\n"
                
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                self.status_bar.setText("Copied selection to clipboard")
        
        # Paste (Ctrl+V)
        elif event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            clipboard = QApplication.clipboard()
            clipboard_text = clipboard.text()
            
            selected = self.table_view.selectedIndexes()
            if selected and clipboard_text:
                # Get the starting position for paste
                start_row = min(index.row() for index in selected)
                start_col = min(index.column() for index in selected)
                
                # Parse the clipboard text
                rows = clipboard_text.split('\n')
                if rows and rows[-1] == '':  # Common when copying from spreadsheets
                    rows.pop()
                    
                # Paste data
                for i, row_text in enumerate(rows):
                    cells = row_text.split('\t')
                    for j, cell_text in enumerate(cells):
                        row = start_row + i
                        col = start_col + j
                        
                        if row < self.model.rowCount() and col < self.model.columnCount():
                            # Create index and set data
                            index = self.model.index(row, col)
                            self.model.setData(index, cell_text, Qt.ItemDataRole.EditRole)
                
                self.status_bar.setText("Pasted data from clipboard")
        
        # Select All (Ctrl+A)
        elif event.key() == Qt.Key.Key_A and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.table_view.selectAll()
            self.status_bar.setText("Selected all cells")
                
        else:
            # Handle other key presses with the default behavior
            super().keyPressEvent(event)
    
    def reset_changes(self):
        """Reset the dataframe to its original state"""
        reply = QMessageBox.question(
            self, "Confirm Reset", 
            "Are you sure you want to reset all changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.df = self.original_df.copy()
            self.model = TableModel(self.df)
            self.table_view.setModel(self.model)
            
            # Reset column widths
            header = self.table_view.horizontalHeader()
            for i in range(len(self.df.columns)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            
            # Reset the filter combobox
            self.label_combo.setCurrentText("All")
            
            self.status_bar.setText("All changes reset to original data")

    def export_to_csv(self):
        """Export the current view to CSV with xaxis as a separate section"""
        # Start in the output directory if specified
        initial_dir = self.output_directory if self.output_directory else ""
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", initial_dir, "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_name:
            try:
                # Get the current data from the model
                current_data = self.model.get_data()
                
                # Ensure file has .csv extension
                if not file_name.lower().endswith('.csv'):
                    file_name += '.csv'
                
                # Export the data with xaxis in a structured format
                import csv
                from datetime import datetime
                
                with open(file_name, 'w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    
                    # Write metadata header
                    writer.writerow(["# Export Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                    writer.writerow(["# Columns", len(current_data.columns)])
                    writer.writerow(["# Rows", len(current_data)])
                    writer.writerow(["# First PPM", (min(self.xaxis))])
                    writer.writerow(["# Last PPM", max(self.xaxis)])
                    writer.writerow(["# Number of points", len(self.xaxis)])
                    writer.writerow([])  # Empty row as separator
                    
                    # # Write PPM values if available
                    # if self.xaxis is not None:
                    #     writer.writerow(["# PPM Values (xaxis)"])
                    #     # Write all xaxis values in a single row
                    #     writer.writerow(self.xaxis)
                    #     writer.writerow([])  # Empty row as separator

                    writer.writerow(current_data.columns)
                    for _, row in current_data.iterrows():
                        writer.writerow(row)
                    
                QMessageBox.information(self, "Export Successful", 
                                    f"Data exported to {file_name} successfully.")
                self.status_bar.setText(f"Exported data to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", 
                                    f"Error exporting data: {str(e)}")
                self.status_bar.setText("Export failed")


    def export_to_xml(self):
        """Export the current view to XML in SpectraClassifier format"""
        initial_dir = self.output_directory if self.output_directory else ""
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save XML File in SpectraClassifier format", initial_dir, "XML Files (*.xml);;All Files (*)"
        )
        
        if file_name:
            try:
                current_data = self.model.get_data()
                
                if not file_name.lower().endswith('.xml'):
                    file_name += '.xml'
                
                import xml.etree.ElementTree as ET
                from datetime import datetime
                
                root = ET.Element("DATASET")
                root.set("CreatedBy", "MRSPlotter")
                root.set("Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                root.set("Format", "SpectraClassifier")
                
                # Get spectral data columns
                ppm_cols = sorted([col for col in current_data.columns if col.startswith('PPM_')],
                                key=lambda x: int(x.split('_')[1]))
                
                # Get PPM parameters from xaxis
                first_ppm = min(self.xaxis) if self.xaxis is not None and len(self.xaxis) > 0 else 0
                last_ppm = max(self.xaxis) if self.xaxis is not None and len(self.xaxis) > 0 else 0
                number_of_points = len(ppm_cols)
                
                case_count = 0
                
                # Process each row as a separate Case (handles MV data with multiple voxels per ID)
                if 'ID' in current_data.columns:
                    has_positions = 'x_pos' in current_data.columns and 'y_pos' in current_data.columns

                    for _, row in current_data.iterrows():
                        unique_id = str(row['ID'])

                        case_id = unique_id

                        if has_positions:
                            x = int(round(float(row['x_pos'])))
                            y = int(round(float(row['y_pos'])))

                        # Create Case element
                        case = ET.SubElement(root, "Case")
                        case.set("ID", case_id)

                        # Add Tissue element
                        tissue = ET.SubElement(case, "Tissue")
                        tissue.set("Type", str(row.get('TissueType', 'Unknown')))
                        tissue.text = ""  # Prevent self-closing

                        # Add Spectrum element
                        spectrum = ET.SubElement(case, "Spectrum")
                        spectrum.set("Name", case_id)
                        #spectrum.set("Name",  f"{unique_id}_X_{x}_Y_{y}")

                        # Add Parameters element
                        parameters = ET.SubElement(spectrum, "Parameters")
                        parameters.set("FirstPPM", str(first_ppm))
                        parameters.set("LastPPM", str(last_ppm))
                        parameters.set("PointsNumber", str(number_of_points))

                        # Add optional X and Y if available
                        if has_positions:
                            parameters.set("Xaxis", str(int(x)))
                            parameters.set("Yaxis", str(int(y)))

                        # Add optional SNR if available
                        if 'SNR' in row:
                            parameters.set("SNR", str(row['SNR']))

                        # Add Points element with spectral data
                        points = ET.SubElement(spectrum, "Points")

                        # Extract spectral data for this row
                        spectral_data = []
                        for col in ppm_cols:
                            val = row[col]
                            if val is None or str(val).lower() in ['nan', 'inf', '-inf']:
                                spectral_data.append('0.0')
                            else:
                                spectral_data.append(str(float(val)))

                        points.text = ' '.join(spectral_data)
                        case_count += 1
                        
                        # # Debug first few cases
                        # if case_count <= 3:
                        #     print(f"Case {case_count}: ID='{unique_id}', TissueType='{row.get('TissueType')}', Points={len(spectral_data)}")
                        #     if 'SNR' in row:
                        #         print(f"  SNR: {row['SNR']}")
                
                else:
                    # Fallback: treat each row as separate case if no ID column
                    print("No ID column found. Treating each row as separate case.")
                    for index, row in current_data.iterrows():
                        case = ET.SubElement(root, "Case")
                        case.set("ID", f"case_{index}")
                        
                        tissue = ET.SubElement(case, "Tissue")
                        tissue.set("Type", str(row.get('TissueType', 'Unknown')))
                        tissue.text = ""
                        
                        spectrum = ET.SubElement(case, "Spectrum")
                        spectrum.set("Name", f"spectrum_{index}")
                        
                        
                        
                        parameters = ET.SubElement(spectrum, "Parameters")
                        parameters.set("FirstPPM", str(first_ppm))
                        parameters.set("LastPPM", str(last_ppm))
                        parameters.set("PointsNumber", str(number_of_points))
                        
                        if 'SNR' in row:
                            parameters.set("SNR", str(row['SNR']))

                        points = ET.SubElement(spectrum, "Points")
                        spectral_data = []
                        for col in ppm_cols:
                            val = row[col]
                            if val is None or str(val).lower() in ['nan', 'inf', '-inf']:
                                spectral_data.append('0.0')
                            else:
                                spectral_data.append(str(float(val)))
                        
                        points.text = ' '.join(spectral_data)
                        case_count += 1
                
                # print(f"Total Cases created: {case_count}")
                # print("=== END EXPORT DEBUG ===\n")
                
                # Write file
                tree = ET.ElementTree(root)
                ET.indent(tree, space="  ", level=0)
                tree.write(file_name, encoding='utf-8', xml_declaration=True)
                
                QMessageBox.information(self, "Export Successful", 
                                    f"Exported {case_count} cases to {file_name} in SpectraClassifier format")
                self.status_bar.setText(f"Exported {case_count} cases to {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Error: {str(e)}")
                self.status_bar.setText("Export failed")
                print(f"Export error: {e}")

    def handle_accept(self):
        """Handle OK button click (like accept in QDialog)"""
        reply = QMessageBox.question(
            self, "Confirm Changes", 
            "Are you sure you want to save all changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Commit any pending edits by closing any open editor
            if self.table_view.state() == QAbstractItemView.State.EditingState:
                self.table_view.commitData(self.table_view.currentEditor())
                self.table_view.closeEditor(self.table_view.currentEditor(), QAbstractItemView.EditTrigger.NoEditTriggers)
            
            # Get the current data from the model
            current_data = self.model.get_data()
            
            # Always save changes, even if they seem identical
            self.df = current_data.copy()
            self.modified_df = current_data.copy()
            self.result_accepted = True
            
            # Emit signal that data was modified
            self.dataModified.emit(self.modified_df, True)
            
            # Close the dialog with accept
            self.accept()
   
    def handle_reject(self):
        """Reset the dataframe to its original state"""
        reply = QMessageBox.question(
            self, "Confirm Exit", 
            "Are you sure you want to return to main menu?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        """Handle Cancel button click (like reject in QDialog)"""
        if reply == QMessageBox.StandardButton.Yes:
            self.result_accepted = False
            
            # Emit signal that modification was cancelled
            self.dataModified.emit(None, False)
            
            # Close the dialog with reject
            self.reject()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Commit any pending edits by closing any open editor
        if self.table_view.state() == QAbstractItemView.State.EditingState:
            self.table_view.commitData(self.table_view.currentEditor())
            self.table_view.closeEditor(self.table_view.currentEditor(), QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # If changes made but not explicitly accepted/rejected
        if not hasattr(self, 'result_accepted') or self.result_accepted is None:
            if self.has_changes():
                reply = QMessageBox.question(
                    self, "Save Changes?", 
                    "Do you want to save your changes before closing?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.modified_df = self.model.get_data()
                    self.result_accepted = True
                    # Emit signal that data was modified
                    self.dataModified.emit(self.modified_df, True)
                elif reply == QMessageBox.StandardButton.No:
                    self.result_accepted = False
                    # Emit signal that modification was cancelled
                    self.dataModified.emit(None, False)
                else:  # Cancel
                    event.ignore()
                    return
        
        # Let the window close
        super().closeEvent(event)
    
    def has_changes(self):
        """Check if there are unsaved changes"""
        current_data = self.model.get_data()
        return not current_data.equals(self.original_df)
    
    def get_modified_data(self):
        """Return the modified dataframe"""
        # Always return the modified dataframe if accepted
        if self.result_accepted:
            return self.modified_df
        return self.original_df

    def was_accepted(self):
        """Return whether OK was clicked (similar to QDialog.exec() returning Accepted)"""
        return self.result_accepted is True