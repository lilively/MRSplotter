from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QListWidgetItem, QColorDialog, QSizePolicy, QDialog, QInputDialog, QMessageBox,
    QStyle
)
from PyQt6.QtCore import Qt, QEvent, QSettings
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from combine_labels_dialog import CombineLabelDialog
from source_labels_dialog import SourceLabelsDialog
from color_dialog import ColorDelegate
from navigation_toolbar import CustomNavigationToolbar

from PyQt6.QtGui import QColor, QIcon
from visualize import Ui_svPlotter
import matplotlib.pyplot as plt
from pandas import notna
from random import randint
from os import path
from sys import argv, exit
from determine_type_and_load import read_files, determine_filetype
from create_plot_subplots import create_subplot
from create_superimposed import create_superimposed
from create_individual_plots import create_individual_plots
from global_intensities import calculate_y_limit
from conflict_handling import validate_ppm_range, sort_numbers
from status import update_status
from create_multivoxel_grid import create_multivoxel_plot, export_mv_grid


class MRSPlotter(QMainWindow):
    def __init__(self):
        super().__init__()

        
        # Set up the UI from visualize.py
        self.ui = Ui_svPlotter()
        self.ui.setupUi(self)
        icon_path = path.join(path.dirname(path.abspath(__file__)), "resources", "favicon-32x32.png")
        self.setWindowIcon(QIcon(icon_path))
        self.settings = QSettings(" ", "MRSplotter")

        # Create a color dialog for reuse
         # Create a color dialog for reuse
        self.color_dialog = QColorDialog(self)
        self.color_dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        
        # Load custom colors from persistent storage
        self.custom_colors = self.load_custom_colors()


        # Connect the Update limits button
        self.ui.update_xaxis.clicked.connect(self.confirm_and_update)
    
        
        # Create plot widget with layout
        self.plot_widget = self.ui.plot_widget
        self.plot_layout = self.ui.plot_layout
        
        # Set up the matplotlib figure with a tight layout
        self.create_figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        
        # Make sure the plot_widget has an expanding policy too
        self.ui.plot_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )

        def get_parent(*args, **kwargs):
            return self
        
        self.canvas.parent = get_parent

        # Create the toolbar
        self.toolbar = CustomNavigationToolbar(self.canvas, self)
        # Add the tool to the toolbar

        self.ui.plot_layout.addWidget(self.toolbar)
        self.ui.plot_layout.addWidget(self.canvas, 1)
        self.ui.plot_layout.addWidget(self.ui.statusbar)

        self.legend_visible = True

        if hasattr(self.toolbar, 'legend_action'):
            self.toolbar.legend_action.triggered.connect(self.update_legend_status)
        
        

        # Connect buttons to functions
        self.ui.load_files_btn.clicked.connect(self.load_files)
        self.ui.process_files_btn.clicked.connect(self.process_selected_files)
        self.ui.select_outdir_btn.clicked.connect(self.select_output_directory)
        
        self.ui.modify_data_button.clicked.connect(self.confirm_and_edit)
        self.ui.modify_data_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        #self.ui.import_labels_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))

        
        # Connect selection changes to update_plot for real-time preview
        self.ui.labels_found.itemSelectionChanged.connect(self.update_preview)
        # Add double-click functionality for color selection
        self.ui.labels_found.itemDoubleClicked.connect(self.label_double_clicked)

        # Connect selection to lisboxes
        self.ui.xml_file_list.installEventFilter(self)
        self.ui.labels_found.installEventFilter(self)

        # Connect the combine labels button
        self.ui.combine_labels_btn.clicked.connect(self.show_combine_labels_dialog)
        # Connect the source labels button
        self.ui.source_labels_btn.clicked.connect(self.show_source_labels_dialog)
        # Connect the reset combinations button
        self.ui.reset_combinations_btn.clicked.connect(self.confirm_reset_labels)

        self.ui.first_ppm_input.editingFinished.connect(self.update_preview)
        self.ui.last_ppm_input.editingFinished.connect(self.update_preview)
        
        # Plot options
        # Connect the configure plot button
        self.ui.configure_plot_button.clicked.connect(self.show_grid_config_dialog)
        self.filetype = None
        self.number_of_files = None
        # self.update_plot_type_options()

        # Initialize grid settings with defaults
        self.use_auto_grid = True
        self.grid_rows = 2
        self.grid_cols = 2
        self.ui.select_mean.stateChanged.connect(self.update_preview)
        self.ui.select_mean.stateChanged.connect(self.update_vertical_lines_enabled)
        self.ui.select_mean_std.stateChanged.connect(self.update_preview)
        self.ui.each_selected.stateChanged.connect(self.update_preview)
        self.ui.each_selected.stateChanged.connect(self.update_vertical_lines_enabled)
        self.ui.add_lines_check.stateChanged.connect(self.update_preview_if_ppm_entered)
        self.update_vertical_lines_enabled()
        self.ui.add_lines_is_brainH.stateChanged.connect(self.update_preview)
        self.ui.ppm_one_input.editingFinished.connect(self.update_preview)
        self.ui.ppm_two_input.editingFinished.connect(self.update_preview)
        self.ui.ppm_three_input.editingFinished.connect(self.update_preview)
        self.ui.plot_type.currentTextChanged.connect(self.update_preview)
        self.ui.plot_type.currentTextChanged.connect(self.ui.on_plot_type_changed)
        self.ui.plot_type.currentTextChanged.connect(self.ui.update_export_options_enabled)
        self.ui.plot_type.currentTextChanged.connect(self.ui.on_plot_type_changed)
        
        
        
        # Set up the color delegate for the labels list
        self.label_delegate = ColorDelegate(self.ui.labels_found)
        self.ui.labels_found.setItemDelegate(self.label_delegate)
        
        # Add pick_color_for_item method to the labels list widget for delegate to use
        self.ui.labels_found.pick_color_for_item = self.pick_color_for_item
        
        # Dictionary to store label colors
        self.color_map = {}
        
        # Predefined distinctive colors for random assignment (tab20)
        self.distinctive_colors = [
            "#1b5b88", "#ff7f0e", "#2ca02c", "#aa3d3d", "#9467bd", 
            "#8c564b", "#803469", "#707070", "#bcbd22", "#17becf",
            "#5f7694", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5",
            "#c49c94", "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5"
        ]
        
        # Store data for plotting
        self.firstPPM = None
        self.lastPPM = None
        self.number_of_points = None
        self.xaxis = None
        self.dataTable = None
        self.files_processed = False
        self.selected_files = []
        
        # Set default PPM values
        self.ui.first_ppm_input.setText("0.00")
        self.ui.last_ppm_input.setText("4.50")
        
        # Connect export plot button
        self.ui.button_export_plot.clicked.connect(self.export_plots)
        
        # Initialize the empty plot
        self.clear_plot()
        
        # Connect the window resized signal to update plots
        self.canvas.mpl_connect('resize_event', self.on_canvas_resize)

        plt.rcParams['savefig.dpi'] = 600  # Set default DPI for saving
    
    def on_canvas_resize(self, event):
        """Handle canvas resize events"""
        if self.files_processed:
            # Update the plot when the canvas size changes
            self.update_preview()

    def create_figure(self):
        """Create a figure for display"""
        
        self.figure = plt.figure(figsize=(8, 6))
        return self.figure
    
    def update_legend_status(self):
            if hasattr(self.toolbar, 'legend_action'):
                self.legend_visible = not self.toolbar.legend_action.isChecked()
                self.update_preview()

    def reset_figure(self):
        """Reset figure layout to defaults and force a complete redraw"""
        if not hasattr(self, 'figure') or self.figure is None:
            self.create_figure()
            if hasattr(self, 'canvas'):
                self.canvas.figure = self.figure
        
        # Store the original size
        if hasattr(self, 'figure'):
            figsize = self.figure.get_size_inches()
            self.figure.clear()
        
        # Force reset the layout parameters
        self.figure.subplots_adjust(
            left=0.125,
            right=0.9,
            top=0.9,
            bottom=0.11,
            wspace=0.2,
            hspace=0.2
        )
        
        # If data is loaded, fully re-update the preview
        if self.files_processed:
            # Make sure we have a clean plot before updating
            self.update_preview()
        else:
            # If no data, just create a default axis
            ax = self.figure.add_subplot(111)
            ax.set_xlabel("PPM")
            ax.set_ylabel("Intensity")
            ax.invert_xaxis()
            ax.text(0.5, 0.5, "Select files and click 'Process Files' to process data", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes)
            self.canvas.draw()
        
        # Update the toolbar
        if hasattr(self, 'toolbar'):
            self.toolbar.update()

    def change_font_size(self):
        # Get current font size (approximate - taking from first axis title)
        current_size = self.canvas.figure.axes[0].title.get_fontsize()
        
        # Create a dialog to get new font size from user
        new_size, ok = QInputDialog.getDouble(
            self, "Change Font Size", "Font Size:", 
            current_size, 6, 72, 1
        )
        
        if ok:
            # Apply the new font size to all text elements
            for ax in self.canvas.figure.get_axes():
                # Title
                if ax.get_title():
                    ax.title.set_fontsize(new_size)
                
                # Axis labels
                ax.xaxis.label.set_fontsize(new_size)
                ax.yaxis.label.set_fontsize(new_size)
                
                # Tick labels
                ax.tick_params(axis='both', labelsize=new_size)
                
                if ax.get_legend():
                    for text in ax.get_legend().get_texts():
                        text.set_fontsize(new_size)
            # Redraw the canvas to apply changes
            self.canvas.draw()

    def get_random_color(self, index=None):
        """Get a random color from the distinctive colors list or generate one"""
        if index is not None and index < len(self.distinctive_colors):
            return QColor(self.distinctive_colors[index])
        else:
            # Generate a random color with good saturation and value
            h = randint(0, 359)  # Hue
            s = randint(150, 255)  # Saturation
            v = randint(150, 255)  # Value
            return QColor.fromHsv(h, s, v)
        
    def eventFilter(self, obj, event):
        """Handle events for the list widgets"""
        if (obj == self.ui.xml_file_list or obj == self.ui.labels_found) and event.type() == QEvent.Type.KeyPress:
            # Select All (Ctrl+A)
            if event.key() == Qt.Key.Key_A and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                for i in range(obj.count()):
                    obj.item(i).setSelected(True)
                return True
                
            # Deselect All (Ctrl+D)
            elif event.key() == Qt.Key.Key_D and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                for i in range(obj.count()):
                    obj.item(i).setSelected(False)
                return True
    
        # Pass other events to the parent class
        return super().eventFilter(obj, event)
    
    def modify_data(self):
        """Open a dialog to view and modify the filtered dataframe"""
        if not self.files_processed or self.dataTable is None:
            update_status(self.ui.statusbar,"Please load and process files first")
            return

        # Check if filtered_dataTable exists, if not use the full dataTable
        # Important: Make a fresh copy to ensure we're not editing an outdated version
        if hasattr(self, 'filtered_dataTable') and self.filtered_dataTable is not None:
            # Rebuild the filtered dataTable to ensure it's current
            selected_labels = [item.text() for item in self.ui.labels_found.selectedItems()]
            self.filtered_dataTable = self.dataTable[self.dataTable['TissueType'].isin(selected_labels)].copy()
            df_to_edit = self.filtered_dataTable
        else:
            df_to_edit = self.dataTable.copy()
        
        # Create the dialog
        from data_editor_dialog import DataEditorDialog
        output_dir = self.ui.outdir_input.text() if hasattr(self.ui, 'outdir_input') else None
        
        dialog = DataEditorDialog(df_to_edit, self, output_directory=output_dir, xaxis=self.xaxis)
        
        # Connect to the dataModified signal
        dialog.dataModified.connect(self.handle_data_editor_modified)
        
        # Show the dialog as modal (blocks until closed)
        result = dialog.exec()
        
        # If dialog was accepted through the OK button
        if result == QDialog.DialogCode.Accepted:
            modified_df = dialog.get_modified_data()
            
            # Update the main dataframe - this is a backup approach in case
            # the signal handler didn't execute for some reason
            self.update_data_after_edit(modified_df)
    
    def handle_data_editor_modified(self, modified_df, was_accepted):
        """Handle when data in the editor was modified via the signal"""
        if was_accepted and modified_df is not None:
            self.update_data_after_edit(modified_df)
            
    def update_data_after_edit(self, modified_df):
        """Update data after editing in the DataEditorDialog"""
        if modified_df is None:
            return

        try:
            # Store the original dataframe
            self.dataTable = modified_df.copy()
            
            # Update tissue type labels
            if 'TissueType' in self.dataTable.columns:
                # Get unique tissue types and sort them
                tissue_types = sorted(
                    [str(label) for label in self.dataTable['TissueType'].unique()
                    if notna(label) and str(label).strip()],
                    key=sort_numbers
                )
                
                # Clear existing labels
                self.ui.labels_found.clear()
                
                # Store current color map for reuse
                old_color_map = self.color_map.copy() if hasattr(self, 'color_map') else {}
                self.color_map = {}
                
                # Add labels to the list with colors
                for i, label in enumerate(tissue_types):
                    item = QListWidgetItem(str(label))
                    
                    # Preserve existing color if possible
                    if str(label) in old_color_map:
                        color = old_color_map[str(label)]
                    else:
                        # Assign a new color
                        color = self.get_random_color(i)
                    
                    # Update the color map
                    self.color_map[str(label)] = color
                    item.setData(Qt.ItemDataRole.UserRole, color)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.ui.labels_found.addItem(item)
                
                # If no items were added, add a default "No labels" item
                if self.ui.labels_found.count() == 0:
                    item = QListWidgetItem("No labels")
                    self.ui.labels_found.addItem(item)
            
            # Update the plot preview
            self.update_preview()
            update_status(self.ui.statusbar,"Data modified successfully")
            
        except Exception as e:
            print(f"Error in update_data_after_edit: {e}")
            update_status(self.ui.statusbar,f"Error updating data: {str(e)}")
            
    def update_dataframe(self, original_df, modified_df):
        """Safely update the original dataframe with modifications"""
        # If no 'temp_row_id' column exists, create one
        if 'temp_row_id' not in original_df.columns:
            original_df['temp_row_id'] = range(len(original_df))
            modified_df['temp_row_id'] = original_df['temp_row_id'].loc[modified_df.index]
        
        # Update the main dataframe based on the modified one
        for index, row in modified_df.iterrows():
            main_idx = original_df[original_df['temp_row_id'] == row['temp_row_id']].index
            if not main_idx.empty:
                original_df.loc[main_idx, :] = row
        
        # Remove temporary column
        if 'temp_row_id' in original_df.columns:
            original_df.drop('temp_row_id', axis=1, inplace=True)
        
        return original_df

    def update_labels_and_colors(self, dataframe):
        """Update labels while preserving existing color mappings"""
        # Get current unique tissue types
        current_tissue_types = sorted(dataframe['TissueType'].unique(), key=sort_numbers)
        
        # Clear existing labels
        self.ui.labels_found.clear()
        
        # Temporary new color map to avoid losing existing colors
        new_color_map = {}
        
        # Repopulate labels with new tissue types
        for i, label in enumerate(current_tissue_types):
            item = QListWidgetItem(str(label))
            
            # Preserve existing color if possible, otherwise assign a new color
            if label in self.color_map:
                new_color_map[label] = self.color_map[label]
            else:
                new_color_map[label] = self.get_random_color(i)
            
            item.setData(Qt.ItemDataRole.UserRole, new_color_map[label])
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.labels_found.addItem(item)
        
        # Update the color map
        self.color_map = new_color_map
        
        # Select the first label by default
        if self.ui.labels_found.count() > 0:
            self.ui.labels_found.item(0).setSelected(True)

    def label_double_clicked(self, item):
        label = item.text()
        current_color = self.color_map.get(label, QColor("#000000"))
        self.color_dialog.setCurrentColor(current_color)
        
        # Restore previously saved custom colors
        for i in range(16):
            if i < len(self.custom_colors) and self.custom_colors[i].isValid():
                self.color_dialog.setCustomColor(i, self.custom_colors[i])
        
        if self.color_dialog.exec():
            color = self.color_dialog.currentColor()
            
            # Save all custom colors for next time
            for i in range(16):
                self.custom_colors[i] = self.color_dialog.customColor(i)
            
            # IMPORTANT: Save to disk for persistence between sessions
            self.save_custom_colors_to_disk()
            
            self.color_map[label] = color
            item.setData(Qt.ItemDataRole.UserRole, color)
            self.ui.labels_found.update()
            self.update_preview()

    def pick_color_for_item(self, index):
        item = self.ui.labels_found.item(index.row())
        label = item.text()
        current_color = self.color_map.get(label, QColor("#000000"))
        self.color_dialog.setCurrentColor(current_color)
        
        # Restore previously saved custom colors
        for i in range(16):
            if i < len(self.custom_colors) and self.custom_colors[i].isValid():
                self.color_dialog.setCustomColor(i, self.custom_colors[i])
        
        if self.color_dialog.exec():
            color = self.color_dialog.currentColor()
            
            # Save all custom colors for next time
            for i in range(16):
                self.custom_colors[i] = self.color_dialog.customColor(i)
            
            # IMPORTANT: Save to disk for persistence between sessions
            self.save_custom_colors_to_disk()
            
            self.color_map[label] = color
            item.setData(Qt.ItemDataRole.UserRole, color)
            self.ui.labels_found.update()
            self.update_preview()

    def load_custom_colors(self):
        """Load custom colors from QSettings"""
        colors = []
        for i in range(16):
            color_name = self.settings.value(f"customColor{i}", "#ffffff")
            colors.append(QColor(color_name))
        return colors

    def save_custom_colors_to_disk(self):
        """Save custom colors to QSettings for persistence between sessions"""
        for i in range(16):
            if self.custom_colors[i].isValid():
                self.settings.setValue(f"customColor{i}", self.custom_colors[i].name())

    def show_combine_labels_dialog(self):
        """Show dialog to combine labels into classes"""
        if not self.files_processed or not self.dataTable is not None:
            update_status(self.ui.statusbar,"Please load and process files first")
            return

        # Get all available labels
        all_labels = [self.ui.labels_found.item(i).text() 
                    for i in range(self.ui.labels_found.count())]
        
        dialog = CombineLabelDialog(self, all_labels)
        if dialog.exec():
            # Process the combinations
            self.process_label_combinations(dialog.combinations)

    def show_source_labels_dialog(self):
        """Show dialog to load source labels from a contribution file"""
        if not self.files_processed or self.dataTable is None:
            update_status(self.ui.statusbar,"Please load and process files first")
            return

        dialog = SourceLabelsDialog(self)
        if not dialog.exec():
            return

        lookup = dialog.winning_source_lookup
        lookup_by = dialog.lookup_by

        # Replace TissueType based on lookup
        replaced = 0
        if 'ID' not in self.dataTable.columns:
            update_status(self.ui.statusbar,"No ID column found in loaded data")
            return

        if lookup_by == 'ID':
            for idx, row in self.dataTable.iterrows():
                voxel_id = str(row['ID'])
                if voxel_id in lookup:
                    self.dataTable.at[idx, 'TissueType'] = lookup[voxel_id]
                    replaced += 1
        elif lookup_by == 'ID_xy':
            x_col = y_col = None
            for candidate in ['x_pos', 'X_pos', 'Xpos', 'x']:
                if candidate in self.dataTable.columns:
                    x_col = candidate
                    break
            for candidate in ['y_pos', 'Y_pos', 'Ypos', 'y']:
                if candidate in self.dataTable.columns:
                    y_col = candidate
                    break
            if x_col is None or y_col is None:
                update_status(self.ui.statusbar,"No x/y coordinate columns found in loaded data")
                return
            import re
            for idx, row in self.dataTable.iterrows():
                voxel_id = str(row['ID'])
                # Strip _X_{n}_Y_{n} suffix from IDs generated by multi-voxel XML reader
                base_id = re.sub(r'_X_\d+_Y_\d+$', '', voxel_id)
                x = int(float(row[x_col]))
                y = int(float(row[y_col]))
                # Try base ID first (XML multi-voxel), then full ID (CSV)
                key = (base_id, x, y)
                if key not in lookup:
                    key = (voxel_id, x, y)
                if key in lookup:
                    self.dataTable.at[idx, 'TissueType'] = lookup[key]
                    replaced += 1

        # Update labels list and colors
        self.ui.labels_found.clear()
        tissue_types = sorted(self.dataTable['TissueType'].unique(), key=sort_numbers)
        for i, label in enumerate(tissue_types):
            item = QListWidgetItem(str(label))
            if str(label) not in self.color_map:
                self.color_map[str(label)] = self.get_random_color(i)
            item.setData(Qt.ItemDataRole.UserRole, self.color_map[str(label)])
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.labels_found.addItem(item)

        if self.ui.labels_found.count() > 0:
            self.ui.labels_found.item(0).setSelected(True)

        self.filtered_dataTable = None
        self.update_preview()
        update_status(self.ui.statusbar,f"Relabeled {replaced}/{len(self.dataTable)} voxels with source labels")

    def reset_label_combinations(self):
        """Reset any label combinations and restore original labels"""
        if not self.files_processed or self.dataTable is None:
            update_status(self.ui.statusbar,"No data to reset")
            return
        
        # Reload the original data from the selected files
        success = self.load_data_from_files(self.selected_files)
        
        if success:
            update_status(self.ui.statusbar,"Label combinations reset to original")
            # This will also update the labels list and colors
            self.update_preview()
        else:
            update_status(self.ui.statusbar,"Failed to reset label combinations")

    def process_label_combinations(self, combinations):
        """Process the label combinations and update the UI"""
        # Example implementation:
        if not combinations:
            return
            
        # Make a copy of the original data
        combined_data = self.dataTable.copy()
        
        # Update TissueType column based on combinations
        for class_name, labels in combinations.items():
            if not labels:
                continue
                
            # Create a mask for all rows with the specified labels
            mask = combined_data['TissueType'].isin(labels)
            
            # Update those rows with the new class name
            combined_data.loc[mask, 'TissueType'] = class_name
            
            # NEW CODE: Ensure the new combined class inherits a color from one of its source labels
            if class_name not in self.color_map and labels:
                # Try to use the color of the first source label
                for source_label in labels:
                    if source_label in self.color_map:
                        self.color_map[class_name] = self.color_map[source_label]
                        break
        
        # Update the dataTable with combined data
        self.dataTable = combined_data
        
        # Update the labels list
        self.ui.labels_found.clear()
        
        # Get unique tissue types after combining
        tissue_types = sorted(combined_data['TissueType'].unique(), key=sort_numbers)
        
        # Add labels to the list
        for i, label in enumerate(tissue_types):
            item = QListWidgetItem(str(label))
            
            # Assign color - either use existing or create new
            if str(label) not in self.color_map:
                self.color_map[str(label)] = self.get_random_color(i)
                    
            item.setData(Qt.ItemDataRole.UserRole, self.color_map[str(label)])
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.labels_found.addItem(item)
        
        # Select the first label by default
        if self.ui.labels_found.count() > 0:
            self.ui.labels_found.item(0).setSelected(True)
        
        # Force recalculation of any cached data
        self.filtered_dataTable = None
        
        # Update the preview
        self.update_preview()
        
        # Show success message
        update_status(self.ui.statusbar,f"Created {len(combinations)} combined label classes")
        
    def resizeEvent(self, event):
        """Handle window resize event by updating the plot size"""
        super().resizeEvent(event)
        if hasattr(self, 'canvas') and self.files_processed:
            # Trigger redraw when window is resized
            self.canvas.figure.tight_layout()
            self.canvas.draw_idle()  # Use draw_idle for better performance
    
    def clear_plot(self):
        """Clear the plot area and add default labels"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_xlabel("PPM")
        ax.set_ylabel("Intensity")
        ax.invert_xaxis()  # Invert x-axis as is common for spectroscopy data
        ax.text(0.5, 0.5, "Select files and click 'Select Files' to process data", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes)
        self.canvas.draw()

       
    def load_files(self):
        """Load XML and text files and update the file list without processing them"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", "", "All Supported Files (*.xml *.txt *.csv);;XML Files (*.xml);;Text Files (*.txt);;CSV Files (*.csv)"
        )
    
        if files:
            # Clear existing items
            self.ui.xml_file_list.clear()
        
            # Add new files to the list (without automatically selecting them)
            for file in files:
                item = QListWidgetItem(file)
                self.ui.xml_file_list.addItem(item)
            
            # Select all files by default
            for i in range(self.ui.xml_file_list.count()):
                self.ui.xml_file_list.item(i).setSelected(True)
        
            # Reset processed flag
            self.files_processed = False
        
            # Clear the plot area
            self.clear_plot()

    def select_output_directory(self):
        """Open a dialog to select the output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if directory:
            self.ui.outdir_input.setText(directory)

    def get_selected_files(self):
        """Return a list of selected XML files"""
        return [self.ui.xml_file_list.item(i).text() 
                for i in range(self.ui.xml_file_list.count()) 
                if self.ui.xml_file_list.item(i).isSelected()]
    
    def show_message_dialog(self, title, text, info_text=None, icon=None, buttons=None):
        """
        Show a message dialog with customizable buttons.
        
        Parameters:
        title (str): Window title
        text (str): Main message text
        info_text (str, optional): Additional information text
        icon (QMessageBox.Icon, optional): Icon to display
        buttons (QMessageBox.StandardButton, optional): Buttons to display, defaults to Ok
        
        Returns:
        int: The StandardButton value that was clicked
        """

        
        msg = QMessageBox(self)
        
        if icon is not None:
            msg.setIcon(icon)
        
        msg.setWindowTitle(title)
        msg.setText(text)
        
        if info_text:
            msg.setInformativeText(info_text)
        
        # Use specified buttons or default to OK
        if buttons:
            msg.setStandardButtons(buttons)
            # For confirmation dialogs, set No as default
            if buttons & QMessageBox.StandardButton.No:
                msg.setDefaultButton(QMessageBox.StandardButton.No)
        else:
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    
        return msg.exec()
    
    def confirm_and_update(self):
        """Ask for confirmation before updating data and preview"""
        from PyQt6.QtWidgets import QMessageBox
        
        result = self.show_message_dialog(
            "Confirm Update",
            "If you click Yes, all previous modifications will be reset.",
            "Any label combinations or color customizations will need to be redone. Do you want to continue?",
            QMessageBox.Icon.Warning,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # User confirmed, proceed with update
            self.update_data_and_preview()

    def confirm_and_edit(self):
        """Ask for confirmation before updating data and preview"""
        from PyQt6.QtWidgets import QMessageBox
        
        result = self.show_message_dialog(
            "Confirm Edit",
            "Would you like to preview and edit your data?",
            info_text=None,
            icon=QMessageBox.Icon.Question,  # Use Icon.Question instead of StandardButton
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # User confirmed, proceed with update
            self.modify_data()
    
    def confirm_reset_labels(self):
        """Ask for confirmation before updating data and preview"""
        from PyQt6.QtWidgets import QMessageBox
        
        result = self.show_message_dialog(
            "Confirm Reset",
            "Would you like to reset labels?",
            info_text=None,
            icon=QMessageBox.Icon.Question,  # Use Icon.Question instead of StandardButton
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # User confirmed, proceed with update
            self.reset_label_combinations()

    def show_grid_config_dialog(self):
        """Show dialog to configure grid layout for subplots"""
        # Only proceed if subplot is selected
        if self.ui.plot_type.currentText() != "Subplot":
            return
            
        from grid_dioalog import GridConfigDialog
        selected_items = self.ui.labels_found.selectedItems()
        num_plots = len(selected_items)
        # Get current settings
        auto_grid = getattr(self, 'use_auto_grid', True)
        rows = getattr(self, 'grid_rows', 2)
        cols = getattr(self, 'grid_cols', 2)
        
        dialog = GridConfigDialog(self, auto_grid, rows, cols, num_plots=num_plots)
        if dialog.exec():
            # Store the settings
            settings = dialog.get_settings()
            self.use_auto_grid = settings['auto_grid']
            self.grid_rows = settings['rows'] 
            self.grid_cols = settings['cols']
            
            update_status(self.ui.statusbar,f"New grid settings: auto={self.use_auto_grid}, rows={self.grid_rows}, cols={self.grid_cols}")
          
            
            # If we already have data loaded, update the preview
            if self.files_processed:
                self.update_preview()
            
  


    def update_data_and_preview(self):
        #self.ui.each_selected.setChecked(True)
        """Update data when PPM range changes, then update preview
        This is now only called when the Update limits button is clicked"""
        if self.files_processed and self.selected_files:
            try:
                # Save the current selection before updating
                selected_labels = [item.text() for item in self.ui.labels_found.selectedItems()]
                
                # Get and validate the PPM range
                try:
                    first_ppm = float(self.ui.first_ppm_input.text())
                    last_ppm = float(self.ui.last_ppm_input.text())
                
                except ValueError:
                    first_ppm = 0.0
                    last_ppm = 4.5
                    update_status(self.ui.statusbar,"Using default PPM range [0.0, 4.5]")
                
                # Store original values for comparison later
                original_first_ppm = first_ppm
                original_last_ppm = last_ppm
                
                # Reload data using the current PPM range
                success = self.load_data_from_files(self.selected_files)
                
                if not success:
                    update_status(self.ui.statusbar,"Failed to load data with the specified PPM range")
                    return
                
                # Check if either PPM range boundary was adjusted
                if original_first_ppm != self.valid_ppm_range[0] or original_last_ppm != self.valid_ppm_range[1]:
                    # Show appropriate status message
                    if original_first_ppm != self.valid_ppm_range[0] and original_last_ppm != self.valid_ppm_range[1]:
                        update_status(self.ui.statusbar,
                            f"Using PPM range {self.valid_ppm_range[0]} to {self.valid_ppm_range[1]} from file (input was out of range)")
                    elif original_first_ppm != self.valid_ppm_range[0]:
                        update_status(self.ui.statusbar,
                            f"Using first PPM {self.valid_ppm_range[0]} from file (input was out of range)")
                    elif original_last_ppm != self.valid_ppm_range[1]:
                        update_status(self.ui.statusbar,
                            f"Using last PPM {self.valid_ppm_range[1]} from file (input was out of range)")
                    
                # For PPM range adjustment:
                self.show_message_dialog(
                "PPM Range Adjusted",
                "The PPM range has been adjusted to fit data boundaries.",
                f"Using range: {self.valid_ppm_range[0]:.2f} ppm to {self.valid_ppm_range[1]:.2f} ppm", QMessageBox.Icon.Information
                )

                # Update the input fields separately
                self.ui.first_ppm_input.setText(f"{self.valid_ppm_range[0]:.2f}")
                self.ui.last_ppm_input.setText(f"{self.valid_ppm_range[1]:.2f}")

                
                # Restore the previous selection
                if selected_labels:
                    # First, deselect the default selection
                    for i in range(self.ui.labels_found.count()):
                        self.ui.labels_found.item(i).setSelected(False)
                    
                    # Then select the previously selected labels if they still exist
                    any_selected = False
                    for i in range(self.ui.labels_found.count()):
                        item = self.ui.labels_found.item(i)
                        if item.text() in selected_labels:
                            item.setSelected(True)
                            any_selected = True
                    
                    # If none of the previous labels exist, select the first one
                    if not any_selected and self.ui.labels_found.count() > 0:
                        self.ui.labels_found.item(0).setSelected(True)
                
                # Update the plot preview with new data
                self.update_preview()
        
            except Exception as e:
                update_status(self.ui.statusbar,f"Error updating PPM range: {str(e)}")
                print(f"Error in update_data_and_preview: {e}")

    

    def load_data_from_files(self, selected_files):
        """Load data from files using the current PPM range"""
        if not selected_files:
            return False
            
        try:
            first_ppm = float(self.ui.first_ppm_input.text())
            last_ppm = float(self.ui.last_ppm_input.text())
        except ValueError:
            first_ppm = 0.0
            last_ppm = 4.5
            
        ppm_range = ppm_range = [min(first_ppm, last_ppm), max(first_ppm, last_ppm)]
        
        #PPM range is validated in read_files
        self.file_firstPPM, self.file_lastPPM, self.number_of_points, self.xaxis, self.dataTable = read_files(
            selected_files, ppm_range, statusbar=self.ui.statusbar
        )
        self.filetype = determine_filetype(selected_files)
        self.number_of_files = len(selected_files)
        self.update_plot_type_options() 
        

        self.valid_ppm_range = validate_ppm_range(ppm_range, self.file_firstPPM, self.file_lastPPM, statusbar=self.ui.statusbar, parent=self)
         # Update PPM input
        self.ui.first_ppm_input.setText(f"{self.valid_ppm_range[0]:.2f}") ###CH
        self.ui.last_ppm_input.setText(f"{self.valid_ppm_range[1]:.2f}")
        
        # Store the selected files for future reference
        self.selected_files = selected_files
        
        # Extract unique tissue types and update labels
        if 'TissueType' in self.dataTable.columns:
            tissueTypes = sorted(self.dataTable['TissueType'].unique(), key=sort_numbers)

            
            # Clear existing labels
            self.ui.labels_found.clear()
            
            # Add labels to the list with random distinctive colors
            for i, label in enumerate(tissueTypes):
                item = QListWidgetItem(str(label))
                # Assign a random distinctive color to each label (preserve existing)
                if str(label) not in self.color_map:
                    self.color_map[str(label)] = self.get_random_color(i)
                item.setData(Qt.ItemDataRole.UserRole, self.color_map[str(label)])
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.labels_found.addItem(item)
            
            # Select the first label by default
            if self.ui.labels_found.count() > 0:
                self.ui.labels_found.item(0).setSelected(True)
        
        # Mark files as processed
        self.files_processed = True
        return True

    def process_selected_files(self):
        """Process the currently selected files"""
        selected_files = self.get_selected_files()
        
        if self.load_data_from_files(selected_files):
            # print(f"DataFrame info after loading {determine_filetype(selected_files[0])}:")
            # print(f"Columns: {self.dataTable.columns.tolist()}")
            # print(f"Data types: {self.dataTable.dtypes}")
            # print(f"Sample data: {self.dataTable.head(2)}")
            # # Update the preview plot
            self.update_preview()

    def update_plot_type_options(self):
        # Store current selection
        current_selection = self.ui.plot_type.currentText()
    
        # Remove Multivoxel grid if it exists
        multivoxel_index = self.ui.plot_type.findText('Multivoxel grid')
        if multivoxel_index >= 0:
            self.ui.plot_type.removeItem(multivoxel_index)
    
        # Add Multivoxel grid only if file type is multivoxel or data has x/y coordinates
        has_xy = (hasattr(self, 'dataTable') and self.dataTable is not None
                  and 'x_pos' in self.dataTable.columns and 'y_pos' in self.dataTable.columns)
        if has_xy or (hasattr(self, 'filetype') and self.filetype in ('multi_voxel', 'CSV_multi_voxel')):
            self.ui.plot_type.addItem('Multivoxel grid')
            self.ui.export_multivoxel_grid.setEnabled(True)
            self.ui.select_mean.setEnabled(True)
        else:
            # Disable the export multivoxel grid checkbox for non-multivoxel files
            self.ui.export_multivoxel_grid.setEnabled(False)
            self.ui.export_multivoxel_grid.setChecked(False)
    
        # Restore selection if still valid, otherwise default to first option
        index = self.ui.plot_type.findText(current_selection)
        if index >= 0:
            self.ui.plot_type.setCurrentIndex(index)
        else:
            self.ui.plot_type.setCurrentIndex(0)

    def update_vertical_lines_enabled(self):
        """Enable the vertical lines checkbox only when mean or each spectra is selected."""
        enabled = self.ui.select_mean.isChecked() or self.ui.each_selected.isChecked()
        self.ui.add_lines_check.setEnabled(enabled)
        if not enabled:
            self.ui.add_lines_check.setChecked(False)

    def update_preview_if_ppm_entered(self):
        """Only update preview when at least one ppm input has a value."""
        for input_field in [self.ui.ppm_one_input, self.ui.ppm_two_input, self.ui.ppm_three_input]:
            if input_field.text().strip():
                self.update_preview()
                return

    def update_preview(self):
        """Update the plot preview based on current settings with improved error handling"""
        # Don't update the preview if no files have been processed yet
        if not self.files_processed or self.xaxis is None or self.dataTable is None:
            return
        
       
        
        # Get plot options
        if hasattr(self.toolbar, 'legend_action'):
            self.legend_visible = not self.toolbar.legend_action.isChecked()
        include_mean = self.ui.select_mean.isChecked()
        include_sdev = self.ui.select_mean_std.isChecked()
        plot_individual_plots = self.ui.each_selected.isChecked()
        plot_type = self.ui.plot_type.currentText() 
        add_vertical_lines = self.ui.add_lines_check.isChecked()
        

        if not (include_mean or plot_individual_plots):
            update_status(self.ui.statusbar,"Please select mean or each spectra to display", timeout=5000)
            self.clear_plot()
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_xlabel("PPM")
            ax.set_ylabel("Intensity")
            ax.invert_xaxis()
            ax.text(0.5, 0.5, "Please select at least one display option:\n• Mean Spectrum\n• Individual Spectra", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes)
            self.canvas.draw()
            return

         # Check if figure exists and create if needed
        if not hasattr(self, 'figure') or self.figure is None:
            self.create_figure()
            self.canvas.figure = self.figure
        
        # Process PPM values for vertical lines
        self.ppm_list_vertical_lines = []
        for input_field in [self.ui.ppm_one_input, self.ui.ppm_two_input, self.ui.ppm_three_input]:
            ppm_text = input_field.text()
            if ppm_text.strip():
                try:
                    self.ppm_list_vertical_lines.append(float(ppm_text))
                except ValueError:
                    print(f"Invalid PPM value: {ppm_text}")
        
        # Get list of selected labels
        selected_items = self.ui.labels_found.selectedItems()
        if not selected_items:
            # If no labels are selected, select the first one by default
            if self.ui.labels_found.count() > 0:
                self.ui.labels_found.item(0).setSelected(True)
                selected_items = self.ui.labels_found.selectedItems()
        
        # Get selected label texts
        selected_labels = [item.text() for item in selected_items]
        
        # Add error handling for empty selection after reloading
        if not selected_labels:
            update_status(self.ui.statusbar,"No valid labels selected for current PPM range")
            self.clear_plot()
            return
        
        # Filter dataTable to include only selected tissue types
        self.filtered_dataTable = self.dataTable[self.dataTable['TissueType'].isin(selected_labels)].copy()
        
        # Check if filtered data is empty
        if self.filtered_dataTable.empty:
            update_status(self.ui.statusbar,"No data available for selected labels in this PPM range")
            self.clear_plot()
            return
        
        try:
            # Calculate y-limits using the filtered data
            self.y_limits = calculate_y_limit(
                self.filtered_dataTable,
                False if plot_individual_plots else include_mean,
                include_sdev)
        except Exception as e:
            update_status(self.ui.statusbar,f"Error calculating y-limits: {str(e)}")
            self.clear_plot()
            return
        
        # Create a color map for selected labels only
        selected_color_map = {label: self.color_map[label].name() for label in selected_labels if label in self.color_map}
        
        # Get the current canvas dimensions
        canvas_width = self.canvas.width()
        canvas_height = self.canvas.height()

        # Clear figure without destroying it
        self.figure.clear()

        try:
            if plot_type == "Subplot":
                result_fig = create_subplot(
                    output_directory="",  
                    xaxis=self.xaxis,
                    dataTable=self.filtered_dataTable,
                    include_mean=include_mean,
                    include_sdev=include_sdev,
                    plot_individual_plots=plot_individual_plots,
                    add_vertical_lines=add_vertical_lines,
                    legend_visible=self.legend_visible,
                    ppm_list_vertical=self.ppm_list_vertical_lines,
                    selected_color=selected_color_map, 
                    ppm_range=self.valid_ppm_range,
                    save_subplot=False,
                    canvas_width=canvas_width,
                    y_limits=self.y_limits, 
                    canvas_height=canvas_height,
                    dpi=self.figure.dpi,
                    export_figure=False, 
                    statusbar=self.ui.statusbar,
                    fig=self.figure,
                    use_auto_grid=self.use_auto_grid,
                    grid_rows=self.grid_rows,
                    grid_cols=self.grid_cols
                    )
                
                # Check if we got a valid figure back
                if result_fig is None:
                    raise ValueError("Failed to create subplot - create_subplot returned None")
                    
            elif plot_type == "Superimposed plot":
                result_fig = create_superimposed(
                    output_directory="", 
                    xaxis=self.xaxis,
                    dataTable=self.filtered_dataTable,
                    include_mean=include_mean,
                    include_sdev=include_sdev,
                    plot_individual_plots=plot_individual_plots,
                    add_vertical_lines=add_vertical_lines,
                    legend_visible=self.legend_visible,
                    ppm_list_vertical=self.ppm_list_vertical_lines,
                    selected_color=selected_color_map, 
                    ppm_range=self.valid_ppm_range,
                    canvas_width=canvas_width,
                    canvas_height=canvas_height,
                    y_limits=self.y_limits,
                    dpi=self.figure.dpi,
                    export_figure=False, 
                    statusbar=self.ui.statusbar,
                    fig=self.figure 
                )
                
                # Check if we got a valid figure back
                if result_fig is None:
                    raise ValueError("Failed to create superimposed plot - create_superimposed returned None")
            
            elif plot_type == "Multivoxel grid":
                result_fig = create_multivoxel_plot(
                    output_directory="", 
                    xaxis=self.xaxis,
                    dataTable=self.dataTable,
                    include_mean=include_mean,
                    include_sdev=include_sdev,
                    plot_individual_plots=plot_individual_plots,
                    add_vertical_lines=add_vertical_lines,
                    legend_visible=self.legend_visible,
                    ppm_list_vertical=self.ppm_list_vertical_lines,
                    selected_color=selected_color_map, 
                    ppm_range=self.valid_ppm_range,
                    canvas_width=canvas_width,
                    canvas_height=canvas_height,
                    y_limits=None,
                    dpi=self.figure.dpi,
                    export_figure=False, 
                    statusbar=self.ui.statusbar,
                    fig=self.figure 
                )
                
                # Check if we got a valid figure back
                if result_fig is None:
                    raise ValueError("Failed to create multivoxel plot - create_multivoxel_grid returned None")
            
            # Try tight layout - wrap in try/except as tight_layout can sometimes fail
            try:
                self.figure.tight_layout()
            except Exception as layout_error:
                print(f"Warning: tight_layout failed: {layout_error}")
                # Try a more robust approach
                self.figure.subplots_adjust(
                    left=0.125, 
                    right=0.9, 
                    top=0.9, 
                    bottom=0.1, 
                    wspace=0.2, 
                    hspace=0.2
                )
            
            # Make sure to draw the canvas
            self.canvas.draw()

     
        except Exception as e:
            # Handle any errors gracefully
            update_status(self.ui.statusbar,f"Error creating plot: {str(e)}")
            print(f"Error in update_preview: {str(e)}")
            
            # Create a fallback empty plot with error message
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_xlabel("PPM")
            ax.set_ylabel("Intensity")
            ax.text(0.5, 0.5, f"Error creating plot: {str(e)}",
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes)
            self.canvas.draw()


   
    def export_plots(self):
        """Export plots with proper figure management to avoid closing the main canvas figure"""
        if not self.files_processed:
            update_status(self.ui.statusbar,"Please select and process files first")
            return
                
        # Get output directory
        self.output_directory = self.ui.outdir_input.text()
        if not self.output_directory:
            update_status(self.ui.statusbar,"Please select an output directory for saving")
            return
        
        # Check if any export option is selected
        export_displayed = self.ui.export_displayed_plot.isChecked()
        export_each_subplot = self.ui.export_each_subplot.isChecked()
        export_individual = self.ui.export_individual_plot.isChecked()
        export_intensities = self.ui.export_intensities.isChecked()
        export_multivoxel_grid = self.ui.export_multivoxel_grid.isChecked()
        
        if not (export_displayed or export_each_subplot or export_individual or export_intensities or export_multivoxel_grid):
            update_status(self.ui.statusbar,"Please select at least one export option")
            return
        
        # Get plot options
                # Get plot options
        if hasattr(self.toolbar, 'legend_action'):
            self.legend_visible = not self.toolbar.legend_action.isChecked()
        resolution = self.ui.export_quality.currentText()
        include_mean = self.ui.select_mean.isChecked()
        include_sdev = self.ui.select_mean_std.isChecked()
        plot_individual_plots = self.ui.each_selected.isChecked()
        add_vertical_lines = self.ui.add_lines_check.isChecked()
        plot_type = self.ui.plot_type.currentText()
        
        # Get list of selected labels
        selected_items = self.ui.labels_found.selectedItems()
        selected_labels = [item.text() for item in selected_items]
        
        # Create a color map for selected labels only
        selected_color_map = {label: self.color_map[label].name() for label in selected_labels if label in self.color_map}
        
        # Track if any export was successful
        export_success = False

        # Export resolution:
        if resolution == '300 dpi':
            res_dpi = 300
        elif resolution == '600 dpi':
            res_dpi = 600
        elif resolution == '800 dpi':
            res_dpi = 800
        else:
            res_dpi = 300  # Default fallback

        # Important: Store the current matplotlib figure to restore it later
        current_fig = plt.gcf()
        
        # Export the currently displayed plot
        if export_displayed or export_each_subplot:
            try:
                # Create a separate figure for export
                export_fig = plt.figure(figsize=(10, 6))
                
                if plot_type == "Subplot":
                    create_subplot(
                        output_directory=self.output_directory,
                        xaxis=self.xaxis,
                        dataTable=self.filtered_dataTable,
                        include_mean=include_mean,
                        include_sdev=include_sdev,
                        plot_individual_plots=plot_individual_plots,
                        add_vertical_lines=add_vertical_lines,
                        legend_visible=self.legend_visible,
                        ppm_list_vertical=self.ppm_list_vertical_lines,
                        selected_color=selected_color_map, 
                        ppm_range=self.valid_ppm_range,
                        y_limits=self.y_limits,
                        export_figure=export_displayed,
                        save_subplot=export_each_subplot,
                        dpi=res_dpi,
                        statusbar=self.ui.statusbar,
                        fig=export_fig,
                        use_auto_grid=self.use_auto_grid,
                        grid_rows=self.grid_rows,
                        grid_cols=self.grid_cols
                    )
                elif plot_type == "Superimposed plot":
                    create_superimposed(
                        output_directory=self.output_directory,
                        xaxis=self.xaxis,
                        dataTable=self.filtered_dataTable,
                        include_mean=include_mean,
                        include_sdev=include_sdev,
                        plot_individual_plots=plot_individual_plots,
                        add_vertical_lines=add_vertical_lines,
                        legend_visible=self.legend_visible,
                        ppm_list_vertical=self.ppm_list_vertical_lines,
                        selected_color=selected_color_map,  
                        ppm_range=self.valid_ppm_range,
                        y_limits=self.y_limits,
                        export_figure=export_displayed,
                        dpi=res_dpi,
                        statusbar=self.ui.statusbar,
                        fig=export_fig
                    )               
                # elif plot_type == "Multivoxel grid":
                #     # For displayed plot export, only export the first case (currently displayed)
                #     case_ids = self.dataTable['ID'].str.extract(r'^(.+?)_X_').iloc[:, 0].unique()
                #     if len(case_ids) > 0:
                #         first_case = case_ids[0]
                #         # Filter data for just the first case
                #         first_case_data = self.dataTable[self.dataTable['ID'].str.startswith(first_case + '_X_')].copy()
                        
                #         create_multivoxel_plot(
                #             output_directory=self.output_directory,
                #             xaxis=self.xaxis,
                #             dataTable=first_case_data, 
                #             include_mean=include_mean,
                #             include_sdev=include_sdev,
                #             plot_individual_plots=plot_individual_plots,
                #             add_vertical_lines=add_vertical_lines,
                #             ppm_list_vertical=self.ppm_list_vertical_lines,
                #             selected_color=selected_color_map, 
                #             ppm_range=self.valid_ppm_range,
                #             y_limits=None,
                #             export_figure=True,
                #             dpi=res_dpi,
                #             statusbar=self.ui.statusbar,
                #             fig=export_fig
                #         )

                # Close just the export figure, not all figures
                plt.close(export_fig)
                export_success = True
                
            except Exception as e:
                update_status(self.ui.statusbar,f"Error exporting plot: {str(e)}")
        
        if export_multivoxel_grid:
            try:
                export_mv_grid(
                output_directory=self.output_directory,
                xaxis=self.xaxis,
                dataTable=self.dataTable,
                include_mean=include_mean,
                include_sdev=include_sdev,
                plot_individual_plots=plot_individual_plots,
                add_vertical_lines=add_vertical_lines,
                ppm_list_vertical=self.ppm_list_vertical_lines,
                selected_color=selected_color_map,
                ppm_range=self.valid_ppm_range,
                legend_visible=self.legend_visible,
                y_limits=None,
                dpi=res_dpi,
                statusbar=self.ui.statusbar,
                export_figure=True
            )
               
                export_success = True
            except Exception as e:
                update_status(self.ui.statusbar,f"Error exporting individual plots: {str(e)}")

        if export_individual:
            try:
                create_individual_plots(
                    output_directory=self.output_directory,
                    xaxis=self.xaxis,
                    dataTable=self.filtered_dataTable,
                    include_mean=False,
                    include_sdev=False,
                    add_vertical_lines=add_vertical_lines,
                    legend_visible=self.legend_visible,
                    ppm_list_vertical=self.ppm_list_vertical_lines,
                    selected_color=selected_color_map, 
                    ppm_range=self.valid_ppm_range,
                    export_figure=export_individual,
                    dpi=res_dpi, 
                    statusbar=self.ui.statusbar 
                )
                export_success = True
            except Exception as e:
                update_status(self.ui.statusbar,f"Error exporting individual plots: {str(e)}")
        if export_intensities:
            try:
                from metabolites import export_intenity 
                export_intenity(
                    output_directory=self.output_directory,
                    ppm_list_vertical=self.ppm_list_vertical_lines,
                    ppm_range=self.valid_ppm_range,
                    statusbar=self.ui.statusbar,
                    number_of_points=self.number_of_points,
                    dataTable=self.filtered_dataTable
                )
                export_success = True
            except Exception as e:
                update_status(self.ui.statusbar,f"Error exporting intensities: {str(e)}")
        
        # Restore the original figure to avoid disrupting the main canvas
        plt.figure(self.figure.number)
        
        # Force redraw of the canvas to restore the plot
        self.update_preview()
        
        # Show success message
        if export_success:
            update_status(self.ui.statusbar,f"File(s) exported to {self.output_directory}")
        else:
            update_status(self.ui.statusbar,"No files exported. Check export options and try again.")


# Run application when executed directly
if __name__ == "__main__":
    app = QApplication(argv)
    window = MRSPlotter()
    window.show()
    exit(app.exec())