import pytest
from PySide2.QtCore import QObject
from package.ui_manager import UiManager


@pytest.fixture
def uiman() -> UiManager:
    return UiManager()


def test_uiman(uiman, qtbot):
    assert True


# class TestUiMan
