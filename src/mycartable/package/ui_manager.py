from PySide2.QtCore import QObject, Property, Signal, Slot
from PySide2.QtGui import QColor

DEFAULT_ANNOTATION_CURRENT_TEXT_SIZE_FACTOR = 15


class UiManager(QObject):

    menuFlottantTextChanged = Signal()
    menuFlottantAnnotationTextChanged = Signal()
    menuFlottantAnnotationDessinChanged = Signal()
    menuFlottantImageChanged = Signal()
    menuFlottantTableauChanged = Signal()
    menuTargetChanged = Signal()

    def __init__(self):
        super().__init__()
        self._menuTarget = None
        self._toast = None
        self._buzyIndicator = False
        self._annotationCurrentTextSizeFactor = (
            DEFAULT_ANNOTATION_CURRENT_TEXT_SIZE_FACTOR
        )
        self._annotationDessinCurrentLineWidth = 3
        self._annotationDessinCurrentStrokeStyle = "black"
        self._annotationDessinCurrentTool = "fillrect"
        self._annotationCurrentTool = "text"
        self._menuFlottantAnnotationText = None
        self._menuFlottantAnnotationDessin = None

    @Property(QObject, notify=menuFlottantTextChanged)
    def menuFlottantText(self):
        return self._menuFlottantText

    @menuFlottantText.setter
    def menuFlottantText_set(self, value: int):
        self._menuFlottantText = value
        self.menuFlottantTextChanged.emit()

    @Property(QObject, notify=menuFlottantAnnotationTextChanged)
    def menuFlottantAnnotationText(self):
        return self._menuFlottantAnnotationText

    @menuFlottantAnnotationText.setter
    def menuFlottantAnnotationText_set(self, value: int):
        self._menuFlottantAnnotationText = value
        self.menuFlottantAnnotationTextChanged.emit()

    @Property(QObject, notify=menuFlottantAnnotationDessinChanged)
    def menuFlottantAnnotationDessin(self):
        return self._menuFlottantAnnotationDessin

    @menuFlottantAnnotationDessin.setter
    def menuFlottantAnnotationDessin_set(self, value: int):
        self._menuFlottantAnnotationDessin = value
        self.menuFlottantAnnotationDessinChanged.emit()

    @Property(QObject, notify=menuFlottantImageChanged)
    def menuFlottantImage(self):
        return self._menuFlottantImage

    @menuFlottantImage.setter
    def menuFlottantImage_set(self, value: int):
        self._menuFlottantImage = value
        self.menuFlottantImageChanged.emit()

    @Property(QObject, notify=menuFlottantTableauChanged)
    def menuFlottantTableau(self):
        return self._menuFlottantTableau

    @menuFlottantTableau.setter
    def menuFlottantTableau_set(self, value: int):
        self._menuFlottantTableau = value
        self.menuFlottantTableauChanged.emit()

    @Property(QObject, notify=menuTargetChanged)
    def menuTarget(self):
        return self._menuTarget

    @menuTarget.setter
    def menuTarget_set(self, value: int):
        if value != self._menuTarget:
            self._menuTarget = value
            self.menuTargetChanged.emit()

    annotationCurrentTextSizeFactorChanged = Signal()

    @Property(int, notify=annotationCurrentTextSizeFactorChanged)
    def annotationCurrentTextSizeFactor(self):
        return self._annotationCurrentTextSizeFactor

    @annotationCurrentTextSizeFactor.setter
    def annotationCurrentTextSizeFactor_set(self, value: int):
        self._annotationCurrentTextSizeFactor = value
        self.annotationCurrentTextSizeFactorChanged.emit()

    annotationDessinCurrentLineWidthChanged = Signal()

    @Property(int, notify=annotationDessinCurrentLineWidthChanged)
    def annotationDessinCurrentLineWidth(self):
        return self._annotationDessinCurrentLineWidth

    @annotationDessinCurrentLineWidth.setter
    def annotationDessinCurrentLineWidth_set(self, value: int):
        self._annotationDessinCurrentLineWidth = value
        self.annotationDessinCurrentLineWidthChanged.emit()

    annotationDessinCurrentStrokeStyleChanged = Signal()

    @Property(QColor, notify=annotationDessinCurrentStrokeStyleChanged)
    def annotationDessinCurrentStrokeStyle(self):
        return self._annotationDessinCurrentStrokeStyle

    @annotationDessinCurrentStrokeStyle.setter
    def annotationDessinCurrentStrokeStyle_set(self, value: int):
        self._annotationDessinCurrentStrokeStyle = value
        self.annotationDessinCurrentStrokeStyleChanged.emit()

    annotationDessinCurrentToolChanged = Signal()

    @Property(str, notify=annotationDessinCurrentToolChanged)
    def annotationDessinCurrentTool(self):
        return self._annotationDessinCurrentTool

    @annotationDessinCurrentTool.setter
    def annotationDessinCurrentTool_set(self, value: int):
        self._annotationDessinCurrentTool = value
        self.annotationDessinCurrentToolChanged.emit()

    annotationCurrentToolChanged = Signal()

    @Property(str, notify=annotationCurrentToolChanged)
    def annotationCurrentTool(self):
        return self._annotationCurrentTool

    @annotationCurrentTool.setter
    def annotationCurrentTool_set(self, value: int):
        self._annotationCurrentTool = value
        self.annotationCurrentToolChanged.emit()

    sendToast = Signal(str)

    buzyIndicatorChanged = Signal()

    @Property(bool, notify=buzyIndicatorChanged)
    def buzyIndicator(self):
        return self._buzyIndicator

    @buzyIndicator.setter
    def buzyIndicator_set(self, value: int):
        self._buzyIndicator = value
        self.buzyIndicatorChanged.emit()

    @Slot()
    def unSetBuzyIndicator(self, *args, **kwargs):
        self.buzyIndicator = False
