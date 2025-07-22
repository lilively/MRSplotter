from PyQt6.QtWidgets import (
    QStyledItemDelegate
)
from PyQt6.QtCore import Qt, QRect, QModelIndex, QEvent
from PyQt6.QtGui import QColor


class ColorDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color_box_width = 20
             
    def paint(self, painter, option, index: QModelIndex):
        """Paint the label and the color box next to it."""
        super().paint(painter, option, index)
        # Get the label text and color
        label = index.data(Qt.ItemDataRole.DisplayRole)
        color = index.data(Qt.ItemDataRole.UserRole)
        # If color is not a valid QColor, fall back to black
        if color is None:
            color = "black"
        if isinstance(color, str):
            color = QColor(color)  # Convert string to QColor
        # Set a fixed size for the color box (e.g., 20px width)
        color_box_width = self.color_box_width
        color_box_height = option.rect.height()  # Keep the height same as the row height
        # Define the position and size of the color box (fixed width of 20px)
        color_rect = QRect(option.rect.left(), option.rect.top(), color_box_width, color_box_height)
        painter.fillRect(color_rect, color)
        
    def editorEvent(self, event, model, option, index):
        """Handle mouse click events on the color box"""
        if event.type() == QEvent.Type.MouseButtonRelease:
            # Calculate the color box rectangle
            color_rect = QRect(option.rect.left(), option.rect.top(), 
                              self.color_box_width, option.rect.height())
            
            # Check if click was within color box
            if color_rect.contains(event.pos()):
                # Get the parent widget (list widget)
                list_widget = self.parent()
                if hasattr(list_widget, 'pick_color_for_item'):
                    list_widget.pick_color_for_item(index)
                    return True
                
        return super().editorEvent(event, model, option, index)