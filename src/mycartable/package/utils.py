import collections
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from PySide2.QtCore import QTimer, QFile, QTextStream, QRunnable, QThreadPool
from PySide2.QtWidgets import QApplication
from package import WIN


def create_singleshot(fn):
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
    "KEY_1": [10, 2],
    "KEY_2": [11, 3],
    "KEY_3": [12, 4],
    "KEY_4": [13, 5],
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


def qrunnable(fn: Callable, *args, run=True, **kwargs) -> QRunnable:
    class QQRunnable(QRunnable):
        def run(self):
            fn(*args, **kwargs)

    runner = QQRunnable()
    if run:
        QThreadPool.globalInstance().start(runner)

    return runner


class WDict(collections.UserDict):
    def __init__(self, *args, **kwargs):
        """permet d'initialiser un dict sous forme nested
        WDict("aaa.bbb.ccc", 2) => {"aaa":{"bbb":{"ccc":2}}}
        """
        if len(args) >= 2 and isinstance(args[0], str):
            value = args[1]
            for key in reversed(args[0].split(".")):
                value = {key: value}
            self.data = value
        else:
            super().__init__(*args, **kwargs)

    def update(self, other):
        """
        Recursively update nested dict
        :param other: some Mapping
        :return: self, updated
        """
        for k, v in other.items():
            if isinstance(v, collections.abc.Mapping):
                self[k] = WDict.update(self.get(k, {}), v)
            else:
                self[k] = v
        return self


def shift_list(l, idx, count, target):
    """
    Move count element from index idx to index target. target index means "before"
    the move.
    :param l: Iterable
    :param idx: int
    :param count: int
    :param target: int
    :return: list
    """
    if idx == target:
        return l
    elif idx < target:
        # cas où déplacement n'aurait aucun effet
        if idx <= target <= idx + count:
            return l

        sl = l[idx : idx + count]
        for n, it in enumerate(sl):
            l.insert(n + target, it)
        return l[:idx] + l[idx + count :]
    else:
        return l[:target] + l[idx : idx + count :] + l[target:idx] + l[idx + count :]
