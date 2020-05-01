from pathlib import Path

from PySide2.QtCore import QStandardPaths as Qs
from package.files_path import ROOT_DATA


def test_path_names():
    assert ROOT_DATA == Path(Qs.writableLocation(Qs.AppDataLocation))