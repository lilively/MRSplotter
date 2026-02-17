from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import (
    QStyle
    
)
from os import path
class Ui_svPlotter(object):

    def update_std_dev_enabled(self, state):
        # Enable standard deviation checkbox only when mean is checked
        self.select_mean_std.setEnabled(state == 2)  # Qt.Checked equals 2
        # Uncheck standard deviation when mean is unchecked
        if state != 2:  # Qt.Checked equals 2
            self.select_mean_std.setChecked(False)
    

    def update_plot_config_enabled(self, selected_plot_type):
        """Enable configure plot button only when Subplot is selected"""
        self.configure_plot_button.setEnabled(selected_plot_type == "Subplot") 


    def update_is_brain_h_enabled(self, state):
        """Enable/disable the isBrainH checkbox based on the Add vertical lines checkbox state"""
        self.add_lines_is_brainH.setEnabled(state == 2)  # 2 is Qt.Checked in PyQt
        # If vertical lines are unchecked, also uncheck isBrainH
        if state == 0:  # 0 is Qt.Unchecked in PyQt
            self.add_lines_is_brainH.setChecked(False)

    def update_ppm_inputs_enabled(self, state):
        """Enable/disable the ppm input fields based on the Add vertical lines checkbox state"""
        enabled = state == 2  # 2 is Qt.Checked in PyQt
        self.ppm_one_input.setEnabled(enabled)
        self.ppm_two_input.setEnabled(enabled)
        self.ppm_three_input.setEnabled(enabled)
        
        # If isBrainH is checked, update the ppm values
        if enabled and self.add_lines_is_brainH.isChecked():
            self.update_ppm_values(2)  # 2 is Qt.Checked in PyQt
        # Clear the fields if unchecked
        elif not enabled:
            self.ppm_one_input.clear()
            self.ppm_two_input.clear()
            self.ppm_three_input.clear()

    def update_ppm_values(self, state):
        """Set default ppm values when isBrainH is checked"""
        if state == 2:  # 2 is Qt.Checked in PyQt
            self.ppm_one_input.setText("3.21")
            self.ppm_two_input.setText("3.03")
            self.ppm_three_input.setText("1.29")
        # Only clear if vertical lines are still checked (user wants custom values)
        elif self.add_lines_check.isChecked():
            self.ppm_one_input.clear()
            self.ppm_two_input.clear()
            self.ppm_three_input.clear()

    def on_plot_type_changed(self):
        plot_type = self.plot_type.currentText()
        if plot_type == "Multivoxel grid":
            self.select_mean.setEnabled(False)
            self.select_mean.setChecked(False)
        else:
            self.select_mean.setEnabled(True)
        
        # Update export options
        self.update_export_options_enabled()

    def update_export_options_enabled(self):
        #Check if any data is selected
        data_selected = self.each_selected.isChecked() or self.select_mean.isChecked()
        
        if not data_selected:
            # No data selected - disable and uncheck all export options
            self.export_displayed_plot.setEnabled(False)
            self.export_displayed_plot.setChecked(False)
            self.export_each_subplot.setEnabled(False)
            self.export_each_subplot.setChecked(False)
            self.export_individual_plot.setEnabled(False)
            self.export_individual_plot.setChecked(False)
            self.export_multivoxel_grid.setEnabled(False)
            self.export_multivoxel_grid.setChecked(False)
            self.export_intensities.setEnabled(False)
            self.export_intensities.setChecked(False)
            return
        
        #Check plot type and enable options
        plot_type = self.plot_type.currentText()
        
        # Export plot(s) - always available when data is selected
        self.export_displayed_plot.setEnabled(True)
        
        # Plot type specific logic
        if plot_type == "Superimposed plot":
            # Superimposed: export plot(s) + export each voxel
            self.export_each_subplot.setEnabled(False)
            self.export_each_subplot.setChecked(False)
            self.export_individual_plot.setEnabled(self.each_selected.isChecked()) 
            self.export_multivoxel_grid.setEnabled(False)
            self.export_multivoxel_grid.setChecked(False)
            
        elif plot_type == "Subplot":
            # Subplot: export plot(s) + export individual subplots + export each voxel
            self.export_each_subplot.setEnabled(True)
            self.export_individual_plot.setEnabled(self.each_selected.isChecked())  
            self.export_multivoxel_grid.setEnabled(False)
            self.export_multivoxel_grid.setChecked(False)
            
        elif plot_type == "Multivoxel grid":
            # Multivoxel grid: export plot(s) + export individual + export multivoxel grids
            self.export_displayed_plot.setEnabled(False)
            self.export_each_subplot.setEnabled(False)
            self.export_each_subplot.setChecked(False)
            self.export_individual_plot.setEnabled(self.each_selected.isChecked())
            self.export_multivoxel_grid.setEnabled(True)
        
        # Uncheck individual plot if each_selected is not checked
        if not self.each_selected.isChecked():
            self.export_individual_plot.setChecked(False)
        
        # Step 3: Intensities - only when vertical lines are checked
        vertical_lines_checked = self.add_lines_check.isChecked()
        self.export_intensities.setEnabled(data_selected and vertical_lines_checked)
        if not vertical_lines_checked:
            self.export_intensities.setChecked(False)

    def setupUi(self, svPlotter):
        svPlotter.setObjectName("svPlotter")
        svPlotter.resize(1200, 900)
        svPlotter.setMinimumSize(800, 900)
        #svPlotter.setMaximumSize(2500, 1350)

        # Create central widget
        self.centralwidget = QtWidgets.QWidget(parent=svPlotter)
        self.centralwidget.setObjectName("centralwidget")
        svPlotter.setCentralWidget(self.centralwidget)
        
        # Main horizontal layout
        self.main_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")
        
        # Left sidebar for controls
        self.sidebar_widget = QtWidgets.QWidget()
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar_widget)
        self.sidebar_widget.setMaximumWidth(350)
        
        # File Selection Section
        # Create a QGroupBox instead of just a label
        self.file_select_group = QtWidgets.QGroupBox("Select file(s) for plotting")
        self.file_select_group.setObjectName("file_select_group")
        # Create a layout inside the QGroupBox
        self.file_select_container = QtWidgets.QVBoxLayout(self.file_select_group)

        self.load_files_btn = QtWidgets.QPushButton("Open Files")
        self.load_files_btn.setObjectName("load_files_btn")
        self.load_files_btn.setStyleSheet("QPushButton { padding: 3px; min-width: 80px; max-width: 100px; }")
        self.file_select_container.addWidget(self.load_files_btn)

        self.xml_file_list = QtWidgets.QListWidget()
        self.xml_file_list.setObjectName("xml_file_list")
        self.xml_file_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.file_select_container.addWidget(self.xml_file_list)

        # Add the process files button here:
        self.process_btn_layout = QtWidgets.QHBoxLayout()
        self.process_btn_layout.setObjectName("process_btn_layout")

        self.process_btn_layout.addStretch()

        self.process_files_btn = QtWidgets.QPushButton("Process selected file(s)")
        self.process_files_btn.setObjectName("process_files_btn")
        self.process_files_btn.setStyleSheet("QPushButton { padding: 3px; min-width: 140px; max-width: 150px; }")
        self.process_btn_layout.addWidget(self.process_files_btn)
        self.file_select_container.addLayout(self.process_btn_layout)




        ## Add the QGroupBox to the sidebar layout
        self.sidebar_layout.addWidget(self.file_select_group)

        # PPM Range Section
        # Create a QGroupBox instead of just a label
        self.ppm_range_group = QtWidgets.QGroupBox("Select PPM Range for Plotting")
        self.ppm_range_group.setObjectName("ppm_range_group")
        # Create a layout inside the QGroupBox
        self.ppm_range_container = QtWidgets.QVBoxLayout(self.ppm_range_group)

        # Create the horizontal layout for the PPM inputs
        self.ppm_range_layout = QtWidgets.QHBoxLayout()
        self.first_ppm_label = QtWidgets.QLabel("First PPM")
        self.first_ppm_label.setObjectName("first_ppm_label")
        self.first_ppm_input = QtWidgets.QLineEdit()
        self.first_ppm_input.setObjectName("first_ppm_input")

        self.last_ppm_label = QtWidgets.QLabel("Last PPM")
        self.last_ppm_label.setObjectName("last_ppm_label")
        self.last_ppm_input = QtWidgets.QLineEdit()
        self.last_ppm_input.setObjectName("last_ppm_input")

        self.update_xaxis = QtWidgets.QPushButton('Update limits')
        self.update_xaxis.setObjectName('update_limits')
        self.update_xaxis.setStyleSheet("QPushButton { padding: 3px; min-width: 80px; max-width: 80px; }")
       

        self.ppm_range_layout.addWidget(self.first_ppm_label)
        self.ppm_range_layout.addWidget(self.first_ppm_input)
        self.ppm_range_layout.addWidget(self.last_ppm_label)
        self.ppm_range_layout.addWidget(self.last_ppm_input)
        self.ppm_range_layout.addWidget(self.update_xaxis)

        # Add the horizontal layout to the QGroupBox's layout
        self.ppm_range_container.addLayout(self.ppm_range_layout)

        # Add the QGroupBox to the sidebar layout
        self.sidebar_layout.addWidget(self.ppm_range_group)

    #####################
    #####################
# Modify data Section
# Create a QGroupBox instead of just a label with reduced margins
        self.modify_data_group = QtWidgets.QGroupBox("")
        self.modify_data_group.setObjectName("modify_data_group")
        # Use a more compact margin for the group box
        self.modify_data_group.setContentsMargins(3, 3, 3, 3)

        # Create a layout inside the QGroupBox with reduced spacing
        self.modify_data_container = QtWidgets.QVBoxLayout(self.modify_data_group)
        self.modify_data_container.setSpacing(2)  # Reduce spacing between elements
        self.modify_data_container.setContentsMargins(5, 5, 5, 5)  # Smaller margins inside the group

        # Create the data view/edit section
        self.modify_data_layout = QtWidgets.QHBoxLayout()
        self.modify_data_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.modify_data_layout.setSpacing(3)  # Minimal spacing between button and label

        # Create a small button (on the left)
        self.modify_data_button = QtWidgets.QPushButton('')
        self.modify_data_button.setObjectName('view_edit_button')
        self.modify_data_button.setFixedSize(25, 25)  # Even smaller button
        self.modify_data_layout.addWidget(self.modify_data_button)

        # Add label with elided text if needed
        self.modify_data_label = QtWidgets.QLabel("Review, Edit or Export data")
        self.modify_data_label.setObjectName("modify_data_label")
        self.modify_data_layout.addWidget(self.modify_data_label)

        # Add the layouts to the QGroupBox's layout (no extra spacing)
        self.modify_data_container.addLayout(self.modify_data_layout)
        

        # Add the QGroupBox to the sidebar layout
        self.sidebar_layout.addWidget(self.modify_data_group)
#####################
#####################


        #Select label section
        self.label_group = QtWidgets.QGroupBox("Select label(s)")
        self.label_group.setObjectName("label_group")
        self.label_container = QtWidgets.QVBoxLayout(self.label_group)

        # Add the QGroupBox to the sidebar layout
        self.sidebar_layout.addWidget(self.label_group)

        self.labels_found = QtWidgets.QListWidget()
        self.labels_found.setObjectName("labels_found")
        self.labels_found.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.label_container.addWidget(self.labels_found)


        # In the label_container layout, after the labels_found widget
        self.combine_labels_btn = QtWidgets.QPushButton("")
        self.combine_labels_btn.setObjectName("combine_labels_btn")
        self.combine_labels_btn.setToolTip("Combine Labels")
        self.combine_labels_btn.setStyleSheet("QPushButton { padding: 3px; min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px; }")

        # In the label_container layout,
        self.source_labels_btn = QtWidgets.QPushButton("")
        self.source_labels_btn.setObjectName("source_labels_btn")
        self.source_labels_btn.setToolTip("Load Labels")
        self.source_labels_btn.setStyleSheet("QPushButton { padding: 3px; min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px; }")

        # Add a button to reset label combinations (icon only, same as toolbar)
        self.reset_combinations_btn = QtWidgets.QPushButton()
        self.reset_combinations_btn.setObjectName("reset_combinations_btn")
        self.reset_combinations_btn.setToolTip("Reset Combinations")
        self.reset_combinations_btn.setStyleSheet("QPushButton { padding: 3px; min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px; }")

        # All buttons in one row, aligned left
        combine_buttons_layout = QtWidgets.QHBoxLayout()
        combine_buttons_layout.setSpacing(0)
        combine_buttons_layout.setContentsMargins(0, 0, 0, 0)
        combine_buttons_layout.addWidget(self.combine_labels_btn)
        combine_buttons_layout.addWidget(self.source_labels_btn)
        combine_buttons_layout.addWidget(self.reset_combinations_btn)
        combine_buttons_layout.addStretch(1)

        # Add the button layout to the label container
        self.label_container.addLayout(combine_buttons_layout)
        
       
       

       # Plot options section
        # Create a QGroupBox instead of just a label
        self.plot_options_group = QtWidgets.QGroupBox("Customize Display")
        self.plot_options_group.setObjectName("plot_options_group")

        # Create a layout inside the QGroupBox
        self.plot_options_container = QtWidgets.QVBoxLayout(self.plot_options_group)

        # Create the plot type layout
        self.plot_type_layout = QtWidgets.QHBoxLayout()
        self.plot_type_label = QtWidgets.QLabel("Select a plot style")
        self.plot_type_label.setObjectName("plot_type_label")
        self.plot_type = QtWidgets.QComboBox()
        self.plot_type.addItems(['Superimposed plot', 'Subplot', 'Multivoxel grid'])
        self.plot_type.setCurrentIndex(0)
        self.plot_type.setStyleSheet("QComboBox { padding: 3px; min-height: 15px; min-width: 120px; }")
        self.plot_type_layout.addWidget(self.plot_type_label)
        self.plot_type_layout.addWidget(self.plot_type)

        # Create a small button (on the left)
        self.configure_plot_button = QtWidgets.QPushButton('')
        self.configure_plot_button.setObjectName('configure_plot_button')
        self.configure_plot_button.setFixedSize(40, 24)  # Even smaller button
        self.plot_type_layout.addWidget(self.configure_plot_button)
        
        # Connect plot type to control enabled state of configure button
        self.plot_type.currentTextChanged.connect(self.update_plot_config_enabled)
        # Set initial state
     
        self.update_plot_config_enabled(self.plot_type.currentText())
        

        # Detect dark mode: if the window background is dark, use white icons
        res_dir = path.join(path.dirname(path.abspath(__file__)), "resources")
        bg_color = QtWidgets.QApplication.instance().palette().color(QPalette.ColorRole.Window)
        is_dark = bg_color.lightnessF() < 0.5

        # Set icon for the configure button
        settings_icon = "icons8-settings_white.svg" if is_dark else "icons8-settings.svg"
        self.configure_plot_button.setIcon(QIcon(path.join(res_dir, settings_icon)))
        self.configure_plot_button.setToolTip("Configure grid layout for subplots")

        # Set icon for the source/load labels button
        add_icon = "add_white.png" if is_dark else "add.png"
        self.source_labels_btn.setIcon(QIcon(path.join(res_dir, add_icon)))

        # Set icon for the combine labels button
        arrows_icon = "arrows_white.png" if is_dark else "arrows.png"
        self.combine_labels_btn.setIcon(QIcon(path.join(res_dir, arrows_icon)))

        # Set icon for the reset combinations button
        reset_icon = "reset_white.png" if is_dark else "reset.png"
        self.reset_combinations_btn.setIcon(QIcon(path.join(res_dir, reset_icon)))

        # Set initial state
        self.update_plot_config_enabled(self.plot_type.currentText())

        # Add the plot type layout to the container
        self.plot_options_container.addLayout(self.plot_type_layout)

        # Add all the checkboxes to the container
        self.each_selected = QtWidgets.QCheckBox("Each selected spectra")
        self.each_selected.setObjectName("each_spectra")
        #self.each_selected.setChecked(True) 
        self.plot_options_container.addWidget(self.each_selected)

        self.select_mean = QtWidgets.QCheckBox("Means by tumor label")
        self.select_mean.setObjectName("select_mean")
        self.plot_options_container.addWidget(self.select_mean)

        self.select_mean_std = QtWidgets.QCheckBox("Add Standard deviation")
        self.select_mean_std.setObjectName("select_mean_std")
        self.plot_options_container.addWidget(self.select_mean_std)

        # Initially disable it if mean is not selected
        self.select_mean_std.setEnabled(self.select_mean.isChecked())
        # Connect the mean checkbox state to control the enabled state of std dev
        self.select_mean.stateChanged.connect(self.update_std_dev_enabled)

        # ####
        self.add_lines_layout = QtWidgets.QHBoxLayout()
        self.add_lines_label = QtWidgets.QLabel("Add vertical lines")
        self.add_lines_label.setObjectName("add_lines_label")
        self.add_lines_check = QtWidgets.QCheckBox("Add vertical lines")
        self.add_lines_is_brainH = QtWidgets.QCheckBox("isBrainH")
        self.add_lines_layout.addWidget(self.add_lines_check )
        self.add_lines_layout.addWidget(self.add_lines_is_brainH)

        # Initially disable isBrainH checkbox
        self.add_lines_is_brainH.setEnabled(False)
        # Connect the add_lines_check state to control the enabled state of isBrainH
        self.add_lines_check.stateChanged.connect(self.update_is_brain_h_enabled)
        # Connect the isBrainH checkbox to set default ppm values
        self.add_lines_is_brainH.stateChanged.connect(self.update_ppm_values)

        self.plot_options_container.addLayout(self.add_lines_layout)

        self.ppm_plot_layout = QtWidgets.QHBoxLayout()
        self.plot_options_container.addLayout(self.ppm_plot_layout)
        

        self.ppm_one_input = QtWidgets.QLineEdit()
        self.ppm_one_input.setObjectName('ppm_one')
        self.ppm_one_input.setFixedSize(60, 20)  # Fixed width and height
        self.ppm_one_label = QtWidgets.QLabel("ppm")
        self.ppm_one_label.setObjectName('ppm_one_label')

        self.ppm_two_input = QtWidgets.QLineEdit()
        self.ppm_two_input.setObjectName('ppm_two')
        self.ppm_two_input.setFixedSize(60, 20)  # Fixed width and height
        self.ppm_two_label = QtWidgets.QLabel("ppm")
        self.ppm_two_label.setObjectName('ppm_two_label')

        self.ppm_three_input = QtWidgets.QLineEdit()
        self.ppm_three_input.setObjectName('ppm_three')
        self.ppm_three_input.setFixedSize(60, 20)  # Fixed width and height
        self.ppm_three_label = QtWidgets.QLabel("ppm")
        self.ppm_three_label.setObjectName('ppm_three_label')

        self.ppm_plot_layout.addWidget(self.ppm_one_input)
        self.ppm_plot_layout.addWidget(self.ppm_one_label)
        self.ppm_plot_layout.addWidget(self.ppm_two_input)
        self.ppm_plot_layout.addWidget(self.ppm_two_label)
        self.ppm_plot_layout.addWidget(self.ppm_three_input)
        self.ppm_plot_layout.addWidget(self.ppm_three_label)

        # Initially disable ppm input fields
        self.ppm_one_input.setEnabled(False)
        self.ppm_two_input.setEnabled(False)
        self.ppm_three_input.setEnabled(False)
        # Connect the add_lines_check state to control the enabled state of ppm inputs
        self.add_lines_check.stateChanged.connect(self.update_ppm_inputs_enabled)
        


 #Select output directory section
        # Create a QGroupBox instead of just a label
        self.output_group_group = QtWidgets.QGroupBox("Select output directory for exporting")
        self.output_group_group.setObjectName("output_group_group")
        # Create a layout inside the QGroupBox
        self.output_group_container = QtWidgets.QVBoxLayout(self.output_group_group)

        # Create the horizontal layout for the directory selection
        self.output_group_layout = QtWidgets.QHBoxLayout()
        self.select_outdir_btn = QtWidgets.QPushButton("Select Directory")
        self.select_outdir_btn.setObjectName("select_outdir_btn")
        self.select_outdir_btn.setStyleSheet("QPushButton { padding: 3px; min-width: 90px; max-width: 100px; }")
        self.outdir_input = QtWidgets.QLineEdit()
        self.outdir_input.setObjectName("outdir_input")

        self.output_group_layout.addWidget(self.select_outdir_btn)
        self.output_group_layout.addWidget(self.outdir_input)

        # Add the horizontal layout to the QGroupBox's layout
        self.output_group_container.addLayout(self.output_group_layout)

        



        # Export options section
        # Create a QGroupBox instead of just a label
        self.export_options_group = QtWidgets.QGroupBox("Customize Display")
        self.export_options_group.setObjectName("export_options_group")

        # Create a layout inside the QGroupBox
        self.export_options_container = QtWidgets.QVBoxLayout(self.export_options_group)
        # Export options section
        # Create a QGroupBox instead of just a label
        self.export_options_group = QtWidgets.QGroupBox("Export settingss")
        self.export_options_group.setObjectName("export_options_group")
        
        # Create a layout inside the QGroupBox
        self.export_options_container = QtWidgets.QVBoxLayout(self.export_options_group)
       
        # Create the quality layout
        self.export_quality_layout = QtWidgets.QHBoxLayout()
        self.export_quality_label = QtWidgets.QLabel("Select resolution for export")
        self.export_quality_label.setObjectName("export_quality_label")
        self.export_quality = QtWidgets.QComboBox()
        self.export_quality.addItems(['300 dpi', '600 dpi', '800 dpi'])
        self.export_quality.setCurrentIndex(0)
        self.export_quality_layout.addWidget(self.export_quality_label)
        self.export_quality_layout.addWidget(self.export_quality)

        self.export_options_container.addLayout(self.export_quality_layout)

        self.export_displayed_plot = QtWidgets.QCheckBox("Export plot(s)")
        self.export_displayed_plot.setObjectName("export_superimpsed")
        self.export_options_container.addWidget(self.export_displayed_plot)

        self.export_each_subplot = QtWidgets.QCheckBox("Export individual subplot(s)")
        self.export_each_subplot.setObjectName("export_superimpsed")
        self.export_options_container.addWidget(self.export_each_subplot)
        self.export_each_subplot.setEnabled(False)

        # Connect the dropdown selection change to control visibility of the subplot export option
        self.export_individual_plot = QtWidgets.QCheckBox("Export each voxel on individual plot")
        self.export_individual_plot.setObjectName("export_individual")
        self.export_options_container.addWidget(self.export_individual_plot)

        self.export_multivoxel_grid = QtWidgets.QCheckBox("Export processed multivoxel grids")
        self.export_multivoxel_grid.setObjectName("export_multivoxel")
        self.export_options_container.addWidget(self.export_multivoxel_grid)
        self.export_multivoxel_grid.setEnabled(False)

        
        # # # Initially disable it if mean is not selected
        # # self.export_individual_plot.setEnabled(self.each_selected.isChecked())
        # # # Connect the mean checkbox state to control the enabled state of std dev
        # # self.each_selected.stateChanged.connect(self.update_export_individual_enabled)

        self.export_intensities = QtWidgets.QCheckBox("Intensities at selected ppm value(s) as .xlsx")
        self.export_intensities.setObjectName('export_intensities')
        ##self.export_intensities.setEnabled(self.add_lines_check.isChecked())
        ##self.add_lines_check.stateChanged.connect(self.update_addlines_enable)

        # Connect both checkboxes to update export options
        self.each_selected.stateChanged.connect(self.update_export_options_enabled)
        self.select_mean.stateChanged.connect(self.update_export_options_enabled)
        self.plot_type.currentTextChanged.connect(self.update_export_options_enabled)
        self.add_lines_check.stateChanged.connect(self.update_export_options_enabled)  
        # Set initial states based on default selections
        self.on_plot_type_changed()

        self.update_export_options_enabled()

        self.export_options_container.addWidget(self.export_intensities)

        # Add the QGroupBox to the sidebar layout
        self.sidebar_layout.addWidget(self.plot_options_group)
        self.sidebar_layout.addWidget(self.output_group_group)
        self.sidebar_layout.addWidget(self.export_options_group)
        
        # Add a spacer to push export button to the bottom
        self.sidebar_layout.addStretch()

        # Save Plot Button
        self.button_export_plot = QtWidgets.QPushButton("Export File(s)")
        self.button_export_plot.setObjectName("button_gen_plot")
        self.sidebar_layout.addWidget(self.button_export_plot)

        # Add the sidebar to the main layout
        self.main_layout.addWidget(self.sidebar_widget)

        # Right side for plot
        self.plot_widget = QtWidgets.QWidget()
        self.plot_widget.setObjectName("plot_widget")
        self.plot_layout = QtWidgets.QVBoxLayout(self.plot_widget)
        self.plot_layout.setObjectName("plot_layout")

        # Plot area will be added in the main.py file

        # Add the plot widget to the main layout with stretch
        self.main_layout.addWidget(self.plot_widget, 1)

        # Status bar label (added to plot_layout after canvas in main.py)
        self.statusbar = QtWidgets.QLabel("Ready — Load files to get started")
        self.statusbar.setObjectName("statusbar")
        self.statusbar.setStyleSheet("""
            QLabel {
                background-color: rgba(1, 1, 1, 0.08);
                color: #383B96;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 10px;
                
            }
        """)
        self.statusbar.setWordWrap(True)

        # Set widget names and connect signals
        self.retranslateUi(svPlotter)
        QtCore.QMetaObject.connectSlotsByName(svPlotter)

    def retranslateUi(self, svPlotter):
        _translate = QtCore.QCoreApplication.translate
        svPlotter.setWindowTitle(_translate("svPlotter", "MRSplotter"))
        
        # File selection group
        self.file_select_group.setTitle(_translate("svPlotter", "Select file(s) for plotting"))
        self.load_files_btn.setText(_translate("svPlotter", "Open Files"))
        self.process_files_btn.setText(_translate("svPlotter", "Process selected file(s)"))


        # Label group
        self.label_group.setTitle(_translate("svPlotter", "Select label(s)"))
        
        # PPM Range group
        self.ppm_range_group.setTitle(_translate("svPlotter", "Select PPM Range for Plotting"))
        self.first_ppm_label.setText(_translate("svPlotter", "First PPM"))
        self.last_ppm_label.setText(_translate("svPlotter", "Last PPM"))
        self.update_xaxis.setText(_translate("svPlotter", "Update limits"))
        
        # Output group
        self.output_group_group.setTitle(_translate("svPlotter", "Select output directory for exporting"))
        self.select_outdir_btn.setText(_translate("svPlotter", "Select Directory"))
        
        # Plot options group
        self.plot_options_group.setTitle(_translate("svPlotter", "Customize Display"))
        self.export_options_group.setTitle(_translate("svPlotter", "Export Settings"))
        self.plot_type_label.setText(_translate("svPlotter", "Select a plot style"))
        self.each_selected.setText(_translate("svPlotter", "Each selected spectra"))
        self.select_mean.setText(_translate("svPlotter", "Means by tumor label"))
        self.select_mean_std.setText(_translate("svPlotter", "Add Standard deviation"))
        self.export_displayed_plot.setText(_translate("svPlotter", "Export plot(s)"))
        self.export_each_subplot.setText(_translate("svPlotter", "Export individual subplot(s)"))
        self.export_individual_plot.setText(_translate("svPlotter", "Export each voxel on individual plot"))
        self.export_intensities.setText(_translate("svPlotter", "Intensities at selected ppm value(s) as .xlsx"))
        # Export button
        self.button_export_plot.setText(_translate("svPlotter", "Export file(s)"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    svPlotter = QtWidgets.QMainWindow()
    ui = Ui_svPlotter()
    ui.setupUi(svPlotter)
    svPlotter.show()
    sys.exit(app.exec())

