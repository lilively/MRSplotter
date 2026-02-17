from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QGridLayout, 
    QLineEdit, QDialogButtonBox, QListWidget, QAbstractItemView, QPushButton
)



class CombineLabelDialog(QDialog):
    def __init__(self, parent=None, labels=None):
        super().__init__(parent)
        self.setWindowTitle("Combine Labels")
        self.resize(650, 400)
        self.labels = labels or []
        self.combinations = {}  # Will store the class-to-labels mapping

        # Main layout
        layout = QVBoxLayout(self)
        
        # Number of classes selector
        num_classes_layout = QHBoxLayout()
        num_classes_label = QLabel("Number of classes:")
        self.num_classes_spin = QSpinBox()
        self.num_classes_spin.setRange(1, 4)
        self.num_classes_spin.setValue(1)
        self.num_classes_spin.valueChanged.connect(self.update_class_widgets)
        num_classes_layout.addWidget(num_classes_label)
        num_classes_layout.addWidget(self.num_classes_spin)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_dialog)
        num_classes_layout.addWidget(self.reset_btn)
        
        num_classes_layout.addStretch()
        layout.addLayout(num_classes_layout)
        
        self.class_container = QWidget()
        self.class_layout = QGridLayout(self.class_container)
        
        self.class_lists = []
        self.class_names = []
        

        self.update_class_widgets(self.num_classes_spin.value())
        
        layout.addWidget(self.class_container)
        

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def reset_dialog(self):
        """Reset all selections and fields in the dialog"""
        # Reset class names
        for name_field in self.class_names:
            name_field.clear()
        
        # Clear all selections in the list widgets
        for class_list in self.class_lists:
            for i in range(class_list.count()):
                class_list.item(i).setSelected(False)
    
        
    def update_class_widgets(self, num_classes):
        # Clear existing widgets
        for i in reversed(range(self.class_layout.count())): 
            self.class_layout.itemAt(i).widget().setParent(None)
        
        self.class_lists = []
        self.class_names = []
        
        # Create new widgets for each class
        for i in range(num_classes):

            class_label = QLabel(f"Class {i+1}:")
            self.class_layout.addWidget(class_label, i, 0)
            

            class_name = QLineEdit()
            class_name.setPlaceholderText(f"Class {i+1} name")
            self.class_names.append(class_name)
            self.class_layout.addWidget(class_name, i, 1)
            

            class_list = QListWidget()
            class_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

            for label in self.labels:
                class_list.addItem(label)
            self.class_lists.append(class_list)
            self.class_layout.addWidget(class_list, i, 2)
    
    def accept(self):
        self.combinations = {}
        for i, class_list in enumerate(self.class_lists):
            class_name = self.class_names[i].text() or f"Class {i+1}"
            self.combinations[class_name] = [
                self.class_lists[i].item(j).text() 
                for j in range(self.class_lists[i].count()) 
                if self.class_lists[i].item(j).isSelected()
            ]
        super().accept()