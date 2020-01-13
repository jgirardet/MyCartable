from datetime import datetime

from fbs_runtime.application_context.PySide2 import ApplicationContext
import sys
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import QUrl, Property, QObject, Slot, Signal

import qrc

import package.database
from pony.orm import db_session, select
from package.utils import MatieresDispatcher


class DatabaseObject(QObject):
    fakenotify = Signal()
    matiereListChanged = Signal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.m_d = MatieresDispatcher(self.db)
        self._currentMatiere = -1
        self._currentPage = {}

    # currentMatiere
    currentMatiereChanged = Signal()

    @Property(int, notify=currentMatiereChanged)
    def currentMatiere(self, notify=currentMatiereChanged):
        return self._currentMatiere

    @currentMatiere.setter
    def currentMatiere_set(self, value):
        if self._currentMatiere == value:
            return
        elif isinstance(value, int):
            self._currentMatiere = value
        else:
            return
        print(f"current matiere set to: {self._currentMatiere}")
        self.currentMatiereChanged.emit()

    @Slot(str)
    def setCurrentMatiereFromString(self, value):
        self._currentMatiere = self.m_d.nom_id[value]
        print(f"current matiere set with {value } to: {self._currentMatiere}")

        self.currentMatiereChanged.emit()

    @Slot(int, result=int)
    def getMatiereIndexFromId(self, matiere_id):
        try:
            return self.m_d.id_index[matiere_id]
        except KeyError:
            print("matiere index non trouvé ou currentMatiere non settée")

    # matieresList
    @Property("QVariantList", notify=matiereListChanged)
    def matieresList(self):
        return list(self.m_d.nom_id.keys())

    @Slot()
    def matieresListRefresh(self):
        self.m_d = MatieresDispatcher(self.db)
        self.matiereListChanged.emit()

    # newPage
    @Slot(int, result="QVariantMap")
    def newPage(self, activite):
        with db_session:
            return self.db.Page.new_page(activite=activite)

    # currentPage
    currentPageChanged = Signal()

    @Property("QVariantMap", notify=currentPageChanged)
    def currentPage(self):
        return self._currentPage

    @currentPage.setter
    def currentPage_set(self, value):
        page_id = value["page_id"]
        with db_session:
            self._currentPage = self.db.Page.get(id=page_id).to_dict()
        self.currentPageChanged.emit()

    @Slot(str, int, result="QVariantList")
    def getPagesByMatiereAndActivite(self, matiere_nom, activite_index):
        with db_session:
            matiere = self.db.Matiere.get(id=self.m_d.nom_id[matiere_nom])
            if matiere:
                return self.db.Activite.pages_by_matiere_and_famille(
                    matiere.id, activite_index
                )
            return []




if __name__ == "__main__":

    # init database first
    package.database.db = package.database.init_database()
    from package.database.factory import populate_database

    populate_database()
    # import all database related stuf
    from package.qml_models import RecentsModel

    appctxt = ApplicationContext()
    engine = QQmlApplicationEngine()
    ddb = DatabaseObject(package.database.db)
    qmlRegisterType(RecentsModel, "" "RecentsModel", 1, 0, "RecentsModel")
    engine.rootContext().setContextProperty("ddb", ddb)
    engine.load(QUrl("qrc:///qml/main.qml"))
    engine.addImportPath("qrc:/qml/")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(appctxt.app.exec_())
