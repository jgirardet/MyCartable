from pathlib import Path
from time import sleep

from package.convert import get_binary_root, get_binary_path, get_command_line_pdftopng, collect_files, run_convert_pdf
import sys


def test_get_binary_root(tmp_path):
    if sys.platform == "linux":
        assert get_binary_root() == Path(__file__).parents[1] / "binary" / "linux"
    elif sys.platform == "win32":
        assert get_binary_root() == Path(__file__).parent[1] / "binary" / "windows"

    sys._MEIPASS = str(tmp_path)
    sys.frozen = True
    if sys.platform == "linux":
        assert get_binary_root() == tmp_path / "binary" / "linux"
    elif sys.platform == "win32":
        assert get_binary_root() == tmp_path / "binary" / "windows"

    del sys._MEIPASS
    del sys.frozen


def test_get_binary_path():
    if sys.platform == "linux":
        assert (
            get_binary_path("bla")
            == Path(__file__).parents[1] / "binary" / "linux" / "bla"
        )
    elif sys.platform == "win32":
        assert (
            get_binary_path()
            == Path(__file__).parent[1] / "binary" / "windows" / "bla.exe"
        )


def test_command_line_pdftopng():

        assert get_command_line_pdftopng("bla.pdf", "root", resolution=111) == [
            str(get_binary_path("pdftopng")),
            "-r",
            "111",
            "bla.pdf",
            "root",
        ]



def test_collect_files_no_prefix(tmp_path):

    # standard
    res = []
    for i in range(5):
        name=  "bla000" +  str(i) + ".png"
        p = tmp_path / name
        p.touch()
        res.append(p)
    assert collect_files(tmp_path,ext= ".png") == res
    assert res[1] == tmp_path / "bla0001.png"

def test_collect_files_standard_avec_prefix(tmp_path):
    # standard avec prefix
    pref="pref"
    res = []
    for i in range(5):
        name=  pref + "bla000" +  str(i) + ".png"
        p = tmp_path / name
        p.touch()
        res.append(p)
    assert collect_files(tmp_path,pref=pref, ext= ".png") == res
    assert res[1] == tmp_path / "prefbla0001.png"

def test_collect_files_standard_checkordalphbetique(tmp_path):

    # check  ordre alphabétique
    res = []
    for i in range(1,6):
        name=  "bla000" +  str(i) + ".png"
        p = tmp_path / name
        p.touch()
        res.append(p)

    name = "bla000" + str(0) + ".png"
    p = tmp_path / name
    p.touch()
    res = [p] + res

    assert collect_files(tmp_path, ext= ".png") == res


def test_convert_pdf(pdf_2pages, tmp_path):
    res = run_convert_pdf(pdf_2pages, tmp_path / "rien")
    assert len(res) == 2
    for f in res:
        assert f.is_file()
        assert f.name.startswith("xxx") #le default