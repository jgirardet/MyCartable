import pytest
from PySide2.QtCore import QObject
from package.ui_manager import UiManager


@pytest.fixture
def uiman() -> UiManager:
    return UiManager()


def test_uiman(uiman):
    assert True


# class TestUiManager:
#     def test_menuFlottantStabylo(self, uiman: UiManager, qtbot):
#         a = QObject()
#         with qtbot.waitSignal(uiman.menuFlottantStabyloChanged):
#             uiman.menuFlottantStabylo = a
#         assert uiman.menuFlottantStabylo == a
#
#     def test_menuFlottantText(self, uiman: UiManager, qtbot):
#         a = QObject()
#         with qtbot.waitSignal(uiman.menuFlottantTextChanged):
#             uiman.menuFlottantText = a
#         assert uiman.menuFlottantText == a
#
#     def test_menuTarget(self, uiman: UiManager, qtbot):
#         a = QObject()
#         with qtbot.waitSignal(uiman.menuTargetChanged):
#             uiman.menuTarget = a
#         assert uiman.menuTarget == a
#
#         with qtbot.assertNotEmitted(uiman.menuTargetChanged):
#             uiman.menuTarget = a
