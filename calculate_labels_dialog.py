import pandas as pd
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDialogButtonBox, QPushButton, QFileDialog,
    QMessageBox,QCheckBox, QDoubleSpinBox, QGroupBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from determine_type_and_load import read_files
from plot_sources import plot_sources
from calculate_labels_function import calculate_labels
from status import update_status

class CalcLabelsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create labels")
        self.resize(600, 400)
        self.winning_source_lookup = {}

        #Get
        self.ppm_range = parent.valid_ppm_range
        self.dataTable = parent.dataTable
        self.statusbar = parent.ui.statusbar

        layout = QVBoxLayout(self)

        # Source contribution file picker
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File with spectra:"))
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select file(s)")
        file_layout.addWidget(self.file_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
  
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        # Create plot widget with layout
        self.figure = Figure(figsize=(5, 4), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(250)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_visible(False)           
        self.placeholder_text = self.figure.text(
            0.5, 0.5, "Load a file to display the plot",
            ha="center", va="center",
            fontsize=11, color="gray", style="italic"
        )
        layout.addWidget(self.canvas)

        ###
        similarity_group = QGroupBox("Calculate similarity")
        similarity_layout = QVBoxLayout(similarity_group)
        row = QHBoxLayout()

        self.corr_checkbox = QCheckBox("Pearson's correlation higher than:")
        self.corr_checkbox.setChecked(False)
        row.addWidget(self.corr_checkbox)

        self.corr_threshold = QLineEdit()
        self.corr_threshold.setObjectName('corr_th_input')
        self.corr_threshold.setText('0.8')
        row.addWidget(self.corr_threshold)

        row.addStretch()

        self.calc_labels_btn = QPushButton("Calculate labels")
        self.calc_labels_btn.clicked.connect(self.on_calculate_labels)
        self.calc_labels_btn.setEnabled(False)

        row.addWidget(self.calc_labels_btn)

        similarity_layout.addLayout(row)
        layout.addWidget(similarity_group)
        self.corr_threshold.setEnabled(self.corr_checkbox.isChecked())
        self.corr_checkbox.toggled.connect(self.corr_threshold.setEnabled)
        self.corr_checkbox.toggled.connect(self._update_calc_enabled)

        # Add some information about how manual settings work
        self.manual_note = QLabel("Ensure that the following columns are found: ID and Labels or winning source number")
        self.manual_note.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.manual_note)

        # OK / Cancel
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Apply new labels")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _any_similarity_selected(self):
        return self.corr_checkbox.isChecked()

    def _update_calc_enabled(self):
        self.calc_labels_btn.setEnabled(self._any_similarity_selected())

    def browse_file(self):
        paths, _ = QFileDialog.getOpenFileNames(
        self, "Select Source Contribution File(s)", "",
        "Supported Files (*.csv *.xml);;CSV Files (*.csv);;XML Files (*.xml);;All Files (*)"
        )
        
        if paths:
            self.file_input.setText("; ".join(paths))
            self.update_label_plot(paths)

    def update_label_plot(self, file_paths):
        if isinstance(file_paths, str):
            file_paths = [p.strip() for p in file_paths.split(";") if p.strip()]
        try:
            self.label_firstPPM, self.label_lastPPM, \
            self.label_number_of_points, self.label_xaxis, \
            self.source_dataTable = read_files(
                file_paths, self.ppm_range, statusbar=None
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read file:\n{e}")
            return

        self.placeholder_text.set_visible(False)

        tissue_types = self.source_dataTable['TissueType'].unique()
        cmap = plt.get_cmap('tab10')
        selected_color = {t: cmap(i % 10) for i, t in enumerate(tissue_types)}

        plot_sources(
            output_directory=None,
            xaxis=self.label_xaxis,
            dataTable=self.source_dataTable,
            include_mean=False,
            include_sdev=False,
            plot_individual_plots=True,
            add_vertical_lines=False,
            ppm_list_vertical=None,
            selected_color=selected_color,
            ppm_range=self.ppm_range,
            export_figure=False,
            legend_visible=True,
            fig=self.figure
        )

        for ax in self.figure.axes:
            legend = ax.get_legend()
            if legend:
                plt.setp(legend.get_texts(), fontsize=7)
        self.canvas.draw()


    
    def on_calculate_labels(self):
        use_correlation = self.corr_checkbox.isChecked()

        threshold = None
        if use_correlation:
            try:
                threshold = float(self.corr_threshold.text())
                if not -1 <= threshold <= 1:
                    raise ValueError("out of range")
            except ValueError:
                QMessageBox.warning(self, "Error", "Threshold must be a number between -1 and 1.")
                self._update_calc_enabled()
                return

        if not hasattr(self, 'source_dataTable') or self.source_dataTable is None:
            QMessageBox.warning(self, "Error", "Please load a source spectra file first.")
            self._update_calc_enabled()
            return

        self.calc_labels_btn.setEnabled(False)
        try:
            update_status(self.statusbar, f"Calculate labels by correlation={use_correlation}, threshold={threshold}")
            self.modified_dataTable = calculate_labels(
                dataTable=self.dataTable.copy(),
                soucreTable=self.source_dataTable,
                th=threshold,
                sbar=self.statusbar
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to calculate labels:\n{e}")
        finally:
            self._update_calc_enabled()


    def accept(self):
        if not hasattr(self, 'modified_dataTable') or self.modified_dataTable is None:
            QMessageBox.warning(self, "Error",
                                "Please click 'Calculate labels' before applying.")
            return

        parent = self.parent()
        parent.dataTable = self.modified_dataTable
        if 'TissueType' in parent.dataTable.columns:
            parent.dataTable['TissueType'] = parent.dataTable['TissueType'].astype(str)

        # Refresh labels_found list and preserve existing colors
        from PyQt6.QtWidgets import QListWidgetItem
        from PyQt6.QtCore import Qt
        from conflict_handling import sort_numbers

        parent.ui.labels_found.clear()
        tissue_types = sorted(parent.dataTable['TissueType'].unique(), key=sort_numbers)
        for i, label in enumerate(tissue_types):
            item = QListWidgetItem(str(label))
            if str(label) not in parent.color_map:
                parent.color_map[str(label)] = parent.get_random_color(i)
            item.setData(Qt.ItemDataRole.UserRole, parent.color_map[str(label)])
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            parent.ui.labels_found.addItem(item)

        if parent.ui.labels_found.count() > 0:
            parent.ui.labels_found.item(0).setSelected(True)

        parent.filtered_dataTable = None
        parent.update_preview()
        update_status(self.statusbar, "Applied correlation-based labels")

        super().accept()
