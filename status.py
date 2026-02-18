from PyQt6.QtCore import QCoreApplication, QTimer


def update_status(statusbar, message, timeout=10000):
        if statusbar:
            statusbar.setText(message)
            QCoreApplication.processEvents()
            QTimer.singleShot(timeout, lambda: statusbar.setText(""))

