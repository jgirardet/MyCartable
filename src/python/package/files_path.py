from pathlib import Path

from PySide2.QtCore import QStandardPaths, QUrl

ROOT_DATA = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
if not ROOT_DATA.is_dir():
    ROOT_DATA.mkdir(parents=True)

FILES = ROOT_DATA / "files"
if not FILES.is_dir():
    FILES.mkdir(parents=True)


def filesify(items, field="path"):
    for it in items:
        it[field] = QUrl.fromLocalFile(str(FILES / it[field])).toEncoded()

    return items
