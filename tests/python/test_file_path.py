import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from package.files_path import root_data, files, tmp_files
from PySide2.QtCore import QStandardPaths


def test_root_data_en_test():
    appdata = (
        Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
        / "MyCartable"
    )
    # desactive en attendant la sauvegarde
    # appdata = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    rrr = root_data()
    assert rrr == appdata
    shutil.rmtree(rrr)
    rrr = root_data()
    assert rrr.is_dir()


def test_root_data_en_prod():
    with patch("package.files_path.get_prod", return_value=True):

        appdata = (
            Path(QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))
            / "MyCartable"
        )
        # desactive en attendant la sauvegarde
        # appdata = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
        rrr = root_data(create=False)
        assert rrr == appdata


def test_files():
    root = root_data()
    (root / "files").mkdir(parents=True)
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
