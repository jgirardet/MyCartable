import sys
import uuid
from dataclasses import dataclass
from datetime import datetime

from PySide2.QtCore import QTimer, QFile, QTextStream
from PySide2.QtWidgets import QApplication
from package import WIN


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


def read_qrc(path, mode="t"):
    file = QFile(path)
    if file.open(QFile.ReadOnly):
        if mode == "t":  # pragma: no branch
            out = QTextStream(file)
            return out.readAll()
        # other format to be added
        # content = file.readAll()
        # return content.data().decode().replace("\r\n", "\n"
    else:
        raise FileNotFoundError(f"{path} n'est pas une ressource valide")
