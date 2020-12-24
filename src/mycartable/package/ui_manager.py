from PySide2.QtCore import QObject, Property, Signal, Slot
from PySide2.QtGui import QColor
from PySide2.QtQml import QQmlComponent

DEFAULT_ANNOTATION_CURRENT_TEXT_SIZE_FACTOR = 15


class UiManager(QObject):

    menuFlottantTextChanged = Signal()
    menuFlottantAnnotationTextChanged = Signal()
    menuFlottantAnnotationDessinChanged = Signal()
    menuFlottantImageChanged = Signal()
    menuFlottantTableauChanged = Signal()
    menuTargetChanged = Signal()
    mainLayoutsChanged = Signal()
    nullCompChanged = Signal()

    NULL_COMP = QQmlComponent()

    MAIN_LAYOUTS = {
        "vide": {
            "splittype": "vide",
            "splittext": "",
            "splitindex": 0,
            "spliturl": "qrc:/qml/layouts/VideLayout.qml",
            "splitcomp": NULL_COMP,
        },
        "classeur": {
            "splittype": "classeur",
            "splittext": "Classeur",
            "splitindex": 1,
            "spliturl": "qrc:/qml/layouts/ClasseurLayout.qml",
            "splitcomp": NULL_COMP,
        },
        "classeur2": {
            "splittype": "classeur2",
            "splittext": "Classeur2",
            "splitindex": 2,
            "spliturl": "qrc:/qml/layouts/ClasseurLayout.qml",
            "splitcomp": NULL_COMP,
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_default()

    def set_default(self):
        self._menuTarget = None
        self._toast = None
        self._buzyIndicator = False
        self._annotationCurrentTextSizeFactor = (
            DEFAULT_ANNOTATION_CURRENT_TEXT_SIZE_FACTOR
        )
        self._annotationDessinCurrentLineWidth = 3
        self._annotationDessinCurrentStrokeStyle = QColor("black")
        self._annotationDessinCurrentTool = "fillrect"
        self._annotationCurrentTool = "text"
        self._menuFlottantAnnotationText = None
        self._menuFlottantAnnotationDessin = None
        self._mainLayouts = {}

    @Slot()
    def resetUiManager(self):
        self.set_default()

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

    @Property("QVariantMap", notify=mainLayoutsChanged)
    def mainLayouts(self):
        return self.MAIN_LAYOUTS

    @Property(QQmlComponent, notify=nullCompChanged)
    def nullComp(self):
        return self.NULL_COMP

    # @Slot(str, QObject, result=QObject)
    # def findParent(self, parent_name: str, child: QObject):
    #     if child is None:
    #         return None
    #     if child.property("objectName") != parent_name:
    #         return self.findParent(parent_name, child.parent())
    #     else:
    #         return child
