from pathlib import Path
from subprocess import CalledProcessError
from time import sleep
from unittest.mock import patch

import pytest
from package import BINARY
from package.convert import (
    get_binary_path,
    get_command_line_pdftopng,
    collect_files,
    run_convert_pdf,
    find_soffice,
)
import sys

from package.database.factory import *
from package.ui_manager import UiManager


def test_get_binary_path():
    if sys.platform == "linux":
        assert get_binary_path("bla") == BINARY / "bla"
    elif sys.platform == "win32":
        assert get_binary_path("bla") == BINARY / "bla.exe"


def test_command_line_pdftopng():

    assert get_command_line_pdftopng("bla.pdf", "root", resolution=111) == [
        str(get_binary_path("pdftopng")),
        "-r",
        "111",
        "bla.pdf",
        "root",
    ]
    res = get_command_line_pdftopng(Path("bla.pdf"), Path("root"), resolution=111)
    assert all(isinstance(x, str) for x in res)


def test_collect_files_no_prefix(tmp_path):

    # standard
    res = []
    for i in range(5):
        name = "bla000" + str(i) + ".png"
        p = tmp_path / name
        p.touch()
        res.append(p)
    assert collect_files(tmp_path, ext=".png") == res
    assert res[1] == tmp_path / "bla0001.png"


def test_collect_files_standard_avec_prefix(tmp_path):
    # standard avec prefix
    pref = "pref"
    res = []
    for i in range(5):
        name = pref + "bla000" + str(i) + ".png"
        p = tmp_path / name
        p.touch()
        res.append(p)
    assert collect_files(tmp_path, pref=pref, ext=".png") == res
    assert res[1] == tmp_path / "prefbla0001.png"


def test_collect_files_standard_checkordalphbetique(tmp_path):

    # check  ordre alphabétique
    res = []
    for i in range(1, 6):
        name = "bla000" + str(i) + ".png"
        p = tmp_path / name
        p.touch()
        res.append(p)

    name = "bla000" + str(0) + ".png"
    p = tmp_path / name
    p.touch()
    res = [p] + res

    assert collect_files(tmp_path, ext=".png") == res


@pytest.mark.skip("lent")
def test_convert_pdf(resources, tmp_path):
    res = run_convert_pdf(resources / "2pages.pdf", tmp_path / "rien")
    assert len(res) == 2
    for f in res:
        assert f.is_file()
        assert f.name.startswith("xxx")  # le default

    assert run_convert_pdf(resources / "xxxxxx .pdf", tmp_path / "rien") == []
    assert (
        run_convert_pdf(resources / "xxxxxx .pdf", tmp_path / "rien", timeout=0) == []
    )


def test_find_soffice(qtbot):

    # default dir
    assert find_soffice()

    # en cherchant
    with patch("package.convert.Path.is_file", return_value=False):
        assert find_soffice()

    # pas trouvé
    class Rien:
        stdout = b""

    with pytest.raises(EnvironmentError):
        with patch("package.convert.Path.is_file", return_value=False):
            with patch("package.convert.subprocess.run", return_value=Rien()):
                find_soffice()

    # pas trouvé avec toast
    with pytest.raises(EnvironmentError):
        with patch("package.convert.Path.is_file", return_value=False):
            with patch("package.convert.subprocess.run", return_value=Rien()):
                ui = UiManager()
                with qtbot.waitSignal(ui.sendToast):
                    find_soffice(ui=ui)


#
# # def mock_build_odt()
# def test_soffice_convert(ddbr):
