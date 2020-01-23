from PySide2.QtCore import Property, Signal, QObject, Slot
from pony.orm import db_session


class RecentsMixin:
    recentsModelChanged = Signal()
    recentsItemClicked = Signal(int, int)


    def __init__(self):
        from package.list_models import RecentsModel
        self.models.update({
            "recentsModel": RecentsModel()
        })


    @Property(QObject, notify=recentsModelChanged)
    def recentsModel(self):
        return self.models["recentsModel"]
