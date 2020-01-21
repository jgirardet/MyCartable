from PySide2.QtCore import Property, Signal, QObject
from pony.orm import db_session


class RecentsMixin:
    recentsModelChanged = Signal()

    @Property(QObject, notify=recentsModelChanged)
    def recentsModel(self):
        return self.models["recentsModel"]
