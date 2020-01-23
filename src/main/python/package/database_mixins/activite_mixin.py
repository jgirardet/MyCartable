from PySide2.QtCore import Property, Signal, Slot
from PySide2.QtQml import QQmlProperty
from pony.orm import db_session


class ActiviteMixin:
    lessonsListChanged = Signal()
    exercicesListChanged = Signal()
    evaluationsListChanged = Signal()

    @Slot()
    def update_activites(self):
        self.lessonsListChanged.emit()
        self.exercicesListChanged.emit()
        self.evaluationsListChanged.emit()

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

    @property
    def activites_all(self):
        return [self.lessonsList, self.exercicesList, self.evaluationsList]

    @property
    def activites_signal_all(self):
        return [
            self.lessonsListChanged,
            self.exercicesListChanged,
            self.evaluationsListChanged,
        ]
