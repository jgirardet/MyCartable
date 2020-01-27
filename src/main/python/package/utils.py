from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication


def create_single_shot(fn):
    timer = QTimer(QApplication.instance() or QApplication())
    timer.setSingleShot(True)
    timer.timeout.connect(fn)
    return timer
