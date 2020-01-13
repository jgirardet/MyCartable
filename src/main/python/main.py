from datetime import datetime

from fbs_runtime.application_context.PySide2 import ApplicationContext
import sys
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import QUrl, Property, QObject, Slot, Signal

import qrc

import package.database
from pony.orm import db_session


class DatabaseObject(QObject):
    fakenotify = Signal()
    recentsChanged = Signal()
    matiereChanged = Signal()


    def __init__(self):
        super().__init__()
        self.db = package.database.db

    @Property(int)
    def currentMatiere(self, notify=matiereChanged):
        if not hasattr(self, "matiere_en_cours"):
            self._currentMatiere = 1
        return self._currentMatiere

    @currentMatiere.setter
    def current_matiere_set(self, value):
        if isinstance(value, str):
            pass
        elif isinstance(value, int)
            self._currentMatiere = value


    # @Property("QVariantList", notify=fakenotify)
    # def matiereNoms(self):
    #     with db_session:
    #         return self.db.Matiere.noms()

    @Property("QVariantList", notify=recentsChanged)
    def recents(self):
        return [1, 2, 3, 4, 5, 6, 7, 8]
        with db_session:
            return self.db.Page.recents()


    sNewPage  = Signal('QVariantMap', arguments=['lid'])
    #
    @Slot(int, result="QVariantMap")
    def newPage(self, activite):
        with db_session:
            return self.db.Page.new_page(activite=activite)

    @Slot(int, result="QVariantMap")
    def getPageById(self, page_id):
        with db_session:
            return self.db.Page.get(id=page_id).to_dict()

    @Slot(str, int, result="QVariantList")
    def getPagesByMatiereAndActivite(self, matiere_nom, activite_index):
        with db_session:
            matiere = self.db.Matiere.get(lambda p: p.nom == matiere_nom)
            if matiere:
                return  self.db.Activite.pages_by_matiere_and_famille(matiere.id, activite_index)
            return []

    @Slot(result="QVariantList")
    def matiereNoms(self):
        with db_session:
            return  self.db.Matiere.noms()



if __name__ == "__main__":

    # init database first
    package.database.db = package.database.init_database()
    from package.database.factory import populate_database

    populate_database()
    # import all database related stuf
    from package.qml_models import RecentsModel

    appctxt = ApplicationContext()
    engine = QQmlApplicationEngine()
    ddb = DatabaseObject()
    qmlRegisterType(RecentsModel, "" "RecentsModel", 1, 0, "RecentsModel")
    engine.rootContext().setContextProperty("ddb", ddb)
    engine.load(QUrl("qrc:///qml/main.qml"))
    engine.addImportPath("qrc:/qml/")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(appctxt.app.exec_())
