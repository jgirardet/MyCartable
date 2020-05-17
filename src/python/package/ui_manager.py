from PySide2.QtCore import QObject, Property, Signal, Slot


class UiManager(QObject):

    menuFlottantTextChanged = Signal()
    menuFlottantStabyloChanged = Signal()
    menuFlottantTableauChanged = Signal()
    menuTargetChanged = Signal()

    def __init__(self):
        super().__init__()
        self._menuTarget = None
        self._toast = None
        self._annotationCurrentTextSizeFactor = 15

    @Property(QObject, notify=menuFlottantTextChanged)
    def menuFlottantText(self):
        return self._menuFlottantText

    @menuFlottantText.setter
    def menuFlottantText_set(self, value: int):
        self._menuFlottantText = value
        self.menuFlottantTextChanged.emit()

    @Property(QObject, notify=menuFlottantStabyloChanged)
    def menuFlottantStabylo(self):
        return self._menuFlottantStabylo

    @menuFlottantStabylo.setter
    def menuFlottantStabylo_set(self, value: int):
        self._menuFlottantStabylo = value
        self.menuFlottantStabyloChanged.emit()

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

    # toastChanged = Signal()

    # @Property(QObject, notify=toastChanged)
    # def toast(self):
    #     return self._toast
    #
    # @toast.setter
    # def toast_set(self, value: int):
    #     self._toast = value
    #     self.toastChanged.emit()

    # # @Slot(str, QObject)
    # @Slot(str)
    # def sendToast(self, msg):
    #     # print(window)
    #     # toast = self.toast.createWithInitialProperties(
    #     # {"msg": "par lar", "parent": window}
    #     # {"msg": "par lar"}
    #     # )
    #     print(self.toast)
    #     self.toast.msg = "aaaaaaaaaaaa"
    #     # print(toast)
    #     self.toast.open()

    sendToast = Signal(str)
