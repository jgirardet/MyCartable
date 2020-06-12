from pathlib import Path

from PySide2.QtCore import QStandardPaths
from package.constantes import APPNAME


def root_data():
    r = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    if not r.is_dir():
        r.mkdir(parents=True)
    return r


ROOT_DATA = root_data()


def files(root_d):
    f = root_d / "files"
    if not f.is_dir():
        f.mkdir(parents=True)
    return f


FILES = files(ROOT_DATA)


def tmp_files():
    t = Path(QStandardPaths.writableLocation(QStandardPaths.TempLocation), APPNAME)
    if not t.is_dir():
        t.mkdir(parents=True)
    return t


TMP = tmp_files()
