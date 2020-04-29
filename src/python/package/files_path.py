from pathlib import Path

from PySide2.QtCore import QStandardPaths

ROOT_DATA = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
if not ROOT_DATA.is_dir():
    ROOT_DATA.mkdir(parents=True)

FILES = ROOT_DATA / "files"
if not FILES.is_dir():
    FILES.mkdir(parents=True)
