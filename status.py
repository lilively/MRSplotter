from PyQt6.QtCore import QCoreApplication


def update_status(statusbar,message, duration=1000):
        if statusbar:
            statusbar.showMessage(message, duration)
            # Force the application to process events to update the UI
            QCoreApplication.processEvents()

