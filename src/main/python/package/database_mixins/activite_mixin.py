from PySide2.QtCore import Property, Signal, Slot
from PySide2.QtQml import QQmlProperty
from pony.orm import db_session


class ActiviteMixin:
    lessonsListChanged = Signal()
    exercicesListChanged = Signal()
    evaluationsListChanged = Signal()

    def __init__(self, *args, **kwargs):
        self._currentActivite = None

    #
    # currentActiviteChanged = Signal()
    #
    # @Property(int, notify=currentActiviteChanged)
    # def currentActivite(self):
    #     return self._currentActivite
    #
    # @currentActivite.setter
    # def currentActivite_set(self, value: int):
    #     self._currentActivite = value
    #     self.currentActiviteChanged.emit()
