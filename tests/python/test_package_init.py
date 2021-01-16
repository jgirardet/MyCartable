import sys
from unittest.mock import patch

import pytest
from mycartable import LINUX, WIN, get_prod


@pytest.mark.skipif(sys.platform == "win32", reason="linux test")
def test_WIN_LINUX_linux():
    assert LINUX
    assert not WIN


@pytest.mark.skipif(sys.platform == "linux", reason="windows test")
def test_WIN_LINUX_windows():
    assert WIN
    assert not LINUX


@pytest.mark.skipif(WIN, reason="linux only")
def test_getprod(monkeypatch):

    # default
    assert not get_prod()

    # MYCARTABLE_PROD SET
    monkeypatch.setenv("MYCARTABLE_PROD", "True")
    assert get_prod()
    monkeypatch.delenv("MYCARTABLE_PROD")
    assert not get_prod()

    monkeypatch.setenv("APPIMAGE", "True")
    assert get_prod()
    monkeypatch.delenv("APPIMAGE")


@pytest.mark.skipif(LINUX, reason="Windows only")
def test_getprod(monkeypatch):

    # default
    assert not get_prod()

    # MYCARTABLE_PROD SET
    monkeypatch.setenv("MYCARTABLE_PROD", "True")
    assert get_prod()
    monkeypatch.delenv("MYCARTABLE_PROD")
    assert not get_prod()

    with patch("mycartable.sys.executable", "blfze/blfze/pythonw.exe"):
        assert get_prod()
