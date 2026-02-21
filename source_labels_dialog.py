import pandas as pd
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDialogButtonBox, QPushButton, QFileDialog,
    QMessageBox
)


class SourceLabelsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Source Labels")
        self.resize(500, 120)
        self.winning_source_lookup = {}

        layout = QVBoxLayout(self)

        # Source contribution file picker
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Source contribution file:"))
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select an Excel file (.xlsx)")
        file_layout.addWidget(self.file_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        # OK / Cancel
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Source Contribution File", "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if path:
            self.file_input.setText(path)

    def accept(self):
        file_path = self.file_input.text().strip()
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            df.columns = [c.lower() for c in df.columns]
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read file:\n{e}")
            return

        if 'repetition' in df.columns:
            repetitions = sorted(df['repetition'].unique())
            if len(repetitions) > 1:
                from PyQt6.QtWidgets import QInputDialog
                items = [str(r) for r in repetitions]
                chosen, ok = QInputDialog.getItem(
                    self, "Select Repetition",
                    "Multiple repetitions detected. Please select:",
                    items, 0, False
                )
                if not ok:
                    return
                df = df[df['repetition'] == int(chosen)]

        self.winning_source_lookup = {}
        try:
            has_id = 'id' in df.columns
            has_xy = 'x' in df.columns and 'y' in df.columns

            if not has_id:
                QMessageBox.warning(self, "Error",
                    "File must contain an 'ID' column.")
                return

            if has_xy:
                unique_positions = df[['x', 'y']].drop_duplicates()
                is_multivoxel = len(unique_positions) > 1
            else:
                is_multivoxel = False

            if is_multivoxel:
                # mV: ID + x + y identifies each voxel
                self.lookup_by = 'ID_xy'
                for _, row in df.iterrows():
                    voxel_id = str(row['id'])
                    x, y = int(row['x']), int(row['y'])
                    winning_num = int(row['winning source number'])
                    self.winning_source_lookup[(voxel_id, x, y)] = f"Source {winning_num}"
            else:
                # SV: ID alone is unique
                self.lookup_by = 'ID'
                for _, row in df.iterrows():
                    voxel_id = str(row['id'])
                    winning_num = int(row['winning source number'])
                    self.winning_source_lookup[voxel_id] = f"Source {winning_num}"
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to parse data:\n{e}")
            return

        super().accept()
