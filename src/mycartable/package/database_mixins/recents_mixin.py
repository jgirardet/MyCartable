from PySide2.QtCore import Property, Signal
from pony.orm import db_session


class RecentsMixin:
    recentsModelChanged = Signal()
    recentsItemClicked = Signal(str, str)

    @Property("QVariantList", notify=recentsModelChanged)
    def recentsModel(self):
        with db_session:
            res = self.db.Page.recents(self.annee_active)
            return res
