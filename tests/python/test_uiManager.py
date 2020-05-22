import pytest
from PySide2.QtCore import QObject
from package.ui_manager import UiManager


@pytest.fixture
def uiman() -> UiManager:
    return UiManager()


class TestUiManager:
    def test_menuFlottantAnnotationText(self, uiman: UiManager, qtbot):
        a = QObject()
        with qtbot.waitSignal(uiman.menuFlottantAnnotationTextChanged):
            uiman.menuFlottantAnnotationText = a
        assert uiman.menuFlottantAnnotationText == a

    def test_menuFlottantText(self, uiman: UiManager, qtbot):
        a = QObject()
        with qtbot.waitSignal(uiman.menuFlottantTextChanged):
            uiman.menuFlottantText = a
        assert uiman.menuFlottantText == a

    def test_menuAnnotationFlottantText(self, uiman: UiManager, qtbot):
        a = QObject()
        with qtbot.waitSignal(uiman.menuAnnotationFlottantTextChanged):
            uiman.menuAnnotationFlottantText = a
        assert uiman.menuAnnotationFlottantText == a

    def test_menuFlottantTableau(self, uiman: UiManager, qtbot):
        a = QObject()
        with qtbot.waitSignal(uiman.menuFlottantTableauChanged):
            uiman.menuFlottantTableau = a
        assert uiman.menuFlottantTableau == a

    def test_menuFlottantImage(self, uiman: UiManager, qtbot):
        a = QObject()
        with qtbot.waitSignal(uiman.menuFlottantImageChanged):
            uiman.menuFlottantImage = a
        assert uiman.menuFlottantImage == a

    def test_menuTarget(self, uiman: UiManager, qtbot):
        a = QObject()
        with qtbot.waitSignal(uiman.menuTargetChanged):
            uiman.menuTarget = a
        assert uiman.menuTarget == a

        with qtbot.assertNotEmitted(uiman.menuTargetChanged):
            uiman.menuTarget = a

    def test_annotationCurrentTextSizeFactor(self, uiman: UiManager, qtbot):
        assert uiman.annotationCurrentTextSizeFactor == 15
        with qtbot.waitSignal(uiman.annotationCurrentTextSizeFactorChanged):
            uiman.annotationCurrentTextSizeFactor = 40
        assert uiman.annotationCurrentTextSizeFactor == 40

    def test_annotationDessinCurrentLineWidth(self, uiman: UiManager, qtbot):
        assert uiman.annotationDessinCurrentLineWidth == 3
        with qtbot.waitSignal(uiman.annotationDessinCurrentLineWidthChanged):
            uiman.annotationDessinCurrentLineWidth = 10
        assert uiman.annotationDessinCurrentLineWidth == 10

    def test_annotationDessinCurrentStrokeStyle(self, uiman: UiManager, qtbot):
        assert uiman.annotationDessinCurrentStrokeStyle == "black"
        with qtbot.waitSignal(uiman.annotationDessinCurrentStrokeStyleChanged):
            uiman.annotationDessinCurrentStrokeStyle = "red"
        assert uiman.annotationDessinCurrentStrokeStyle == "red"

    def test_annotationDessinCurrentTool(self, uiman: UiManager, qtbot):
        assert uiman.annotationDessinCurrentTool == "black"
        with qtbot.waitSignal(uiman.annotationDessinCurrentToolChanged):
            uiman.annotationDessinCurrentTool = "red"
        assert uiman.annotationDessinCurrentTool == "red"
