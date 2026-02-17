from PyQt6.QtCore import QCoreApplication


def update_status(statusbar, message):
        if statusbar:
            statusbar.setText(message)
            # Force the application to process events to update the UI
            QCoreApplication.processEvents()

