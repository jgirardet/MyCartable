from datetime import datetime

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication


def create_singleshot(fn):
    # timer = QTimer(QApplication.instance() or QApplication())
    timer = QTimer(QApplication.instance())
    timer.setSingleShot(True)
    timer.timeout.connect(fn)
    return timer


def get_new_filename(ext):
    """relative path"""
    return datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S") + ext
