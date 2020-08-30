from pathlib import Path

from PySide2.QtCore import QStandardPaths
from loguru import logger
from package.constantes import APPNAME
from package import get_prod


def root_data(create=True):
    prod = get_prod()
    if prod:
        r = (
            Path(QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))
            / APPNAME
        )
    else:
        r = Path(
            QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), APPNAME
        )
    # en attendant le vrai systeme de sauvegarde
    # r = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    if not r.is_dir() and create:
        r.mkdir(parents=True)
    logger.info(f"Root data set to {r}")
    return r


ROOT_DATA = root_data()
print("ROOT DATA", ROOT_DATA)


def files(root_d):
    f = root_d / "files"
    if not f.is_dir():
        f.mkdir(parents=True)
    logger.info(f"Files path set to {f}")
    return f


FILES = files(ROOT_DATA)


def tmp_files():
    t = Path(QStandardPaths.writableLocation(QStandardPaths.TempLocation), APPNAME)
    if not t.is_dir():
        t.mkdir(parents=True)
    logger.info(f"TMP path set to {t}")
    return t


TMP = tmp_files()
