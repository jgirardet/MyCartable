from PySide2.QtCore import Property, Signal
from pony.orm import db_session


class RecentsMixin:
    recentsModelChanged = Signal()
    recentsItemClicked = Signal(int, int)

    @Property("QVariantList", notify=recentsModelChanged)
    def recentsModel(self):
        with db_session:
            return self.db.Page.recents(self.annee_active)
