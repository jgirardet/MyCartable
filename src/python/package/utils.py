import sys
import uuid
from dataclasses import dataclass
from datetime import datetime

from PySide2.QtCore import QTimer, QFile
from PySide2.QtWidgets import QApplication


WIN = sys.platform == "win32"
LINUX = sys.platform == "linux"


def create_singleshot(fn):
    # timer = QTimer(QApplication.instance() or QApplication())
    timer = QTimer(QApplication.instance())
    timer.setSingleShot(True)
    timer.timeout.connect(fn)
    return timer


def get_new_filename(ext):
    """relative path"""
    return (
        datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        + "-"
        + uuid.uuid4().hex[0:5]
        + ext
    )


KEYS = {
    "KEY_1": [10, 3],
    "KEY_2": [11, 4],
    "KEY_3": [12, 5],
    "KEY_4": [13, 6],
}

# 1 pour windows 0 pour linux
OS = 1 if WIN else 0


@dataclass
class KeyCross:
    key: list

    def __eq__(self, other):
        if isinstance(other, int):
            return self.key[OS] == other
        elif isinstance(other, dict):
            return self.key[OS] == other["nativeScanCode"]
        else:
            return False


class KeyWizard:
    """ordre linux windows"""

    """raccourci clavier compatible windows linux"""

    def __init__(self):
        for k, v in KEYS.items():
            setattr(self, k, KeyCross(key=v))


KeyW = KeyWizard()


def read_qrc(path):
    file = QFile(path)
    if file.open(QFile.ReadOnly | QFile.Text):
        return file.readData(file.bytesAvailable())
    else:
        raise FileNotFoundError(f"{path} n'est pas une ressource valide")
