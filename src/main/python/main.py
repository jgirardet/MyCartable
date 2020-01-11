from fbs_runtime.application_context.PySide2 import ApplicationContext
import sys
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import (
    QUrl,
    Property, QObject, Slot,
    Signal)

import qrc

import package.database
from pony.orm import db_session


class DatabaseObject(QObject):
    fakenotify = Signal()
    fakenotify2 = Signal()

    def __init__(self):
        super().__init__()
        self.db = package.database.db


    @Property('QVariantList', notify=fakenotify)
    def matiereNoms(self):
        with db_session:
            return self.db.Matiere.noms()

    @Property('QVariantList', notify=fakenotify2)
    def recents(self):
        with db_session:
            return self.db.Page.recents()



    @Slot(result=list)
    def withslot(self):
        with db_session:
            return self.db.Page.recents()








if __name__ == "__main__":

    package.database.db = package.database.init_database()
    from package.database.factory import populate_database
    populate_database()

    appctxt = ApplicationContext()
    engine = QQmlApplicationEngine()
    # qmlRegisterType(MatiereModel, "MatiereModel", 1, 0, "MatiereModel")
    ddb = DatabaseObject()
    engine.rootContext().setContextProperty("ddb", ddb)
    engine.load(QUrl("qrc:///qml/main.qml"))
    engine.addImportPath("qrc:/qml/")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(appctxt.app.exec_())
