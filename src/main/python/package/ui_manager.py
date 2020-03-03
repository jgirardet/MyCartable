from PySide2.QtCore import QObject, Property, Signal


class UiManager(QObject):

    menuFlottantTextChanged = Signal()
    menuFlottantStabyloChanged = Signal()
    menuTargetChanged = Signal()

    def __init__(self):
        super().__init__()
        self._menuTarget = None

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

    @Property(QObject, notify=menuTargetChanged)
    def menuTarget(self):
        return self._menuTarget

    @menuTarget.setter
    def menuTarget_set(self, value: int):
        if value != self._menuTarget:
            self._menuTarget = value
            self.menuTargetChanged.emit()
