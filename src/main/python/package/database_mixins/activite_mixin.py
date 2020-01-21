from PySide2.QtCore import Property, Signal, Slot
from PySide2.QtQml import QQmlProperty
from pony.orm import db_session


class ActiviteMixin:
    lessonsListChanged = Signal()
    exercicesListChanged = Signal()
    evaluationsListChanged = Signal()


    @Property("QVariantList", notify=lessonsListChanged)
    def lessonsList(self):
        with db_session:
            return self.db.Activite.pages_by_matiere_and_famille(self.currentMatiere, 0)


    @Property("QVariantList", notify=exercicesListChanged)
    def exercicesList(self):
        with db_session:
            return self.db.Activite.pages_by_matiere_and_famille(self.currentMatiere, 1)

    @Property("QVariantList", notify=evaluationsListChanged)
    def evaluationsList(self):
        with db_session:
            return self.db.Activite.pages_by_matiere_and_famille(self.currentMatiere, 2)

