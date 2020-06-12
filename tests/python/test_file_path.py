import shutil
from pathlib import Path

from package.files_path import root_data, files, tmp_files
from PySide2.QtCore import QStandardPaths


def test_root_data():
    appdata = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    rrr = root_data()
    assert rrr == appdata
    shutil.rmtree(rrr)
    rrr = root_data()
    assert rrr.is_dir()


def test_files():
    root = root_data()
    fil = files(root)
    assert fil.is_dir()
    shutil.rmtree(root)
    fil = files(root)
    assert fil.is_dir()
    assert fil == root / "files"


def test_tmp_files():
    tt = tmp_files()
    shutil.rmtree(tt)
    tt = tmp_files()
    assert tt.is_dir()
