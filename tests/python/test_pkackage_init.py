import sys
from unittest.mock import patch

import pytest
from package import LINUX, WIN, get_prod, ROOT, get_root_binary_path


@pytest.mark.skipif(sys.platform == "win32", reason="linux test")
def test_WIN_LINUX_linux():
    assert LINUX
    assert not WIN


@pytest.mark.skipif(sys.platform == "linux", reason="windows test")
def test_WIN_LINUX_windows():
    assert WIN
    assert not LINUX


def test_getprod(monkeypatch):

    # default
    assert not get_prod()

    # MYCARTABLE_PROD SET
    monkeypatch.setenv("MYCARTABLE_PROD", "True")
    assert get_prod()
    monkeypatch.delenv("MYCARTABLE_PROD")
    assert not get_prod()

    with patch("package.sys.executable", "blfze/blfze/pythonw.exe"):
        with patch("package.WIN", True):
            assert get_prod()

    monkeypatch.setenv("MYCARTABLE_PROD", "True")
    with patch("package.LINUX", True):
        assert get_prod()
    monkeypatch.delenv("MYCARTABLE_PROD")


def test_get_root_binary_path():
    if LINUX:
        assert get_root_binary_path() == ROOT / "binary" / "linux"
    else:
        assert get_root_binary_path() == ROOT / "binary" / "windows"
