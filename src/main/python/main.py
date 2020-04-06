import os

# from fbs_runtime.application_context.PySide2 import ApplicationContext
from pathlib import Path

from PySide2.QtWidgets import QApplication
import sys
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import QUrl, QLocale, QStandardPaths, QSettings

import sys

if getattr(sys, "frozen", False):
    # we are running in a bundle
    frozen = "ever so"
    bundle_dir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
print(bundle_dir)
sys.path.append(bundle_dir)

import package.database
from package.constantes import APPNAME, ORGNAME
import logging


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def main_init_database():
    # init database first
    package.database.db = package.database.init_database()
    from package.database.factory import populate_database

    populate_database()
    return package.database.db


def register_new_qml_type(databaseObject):
    from package.operations.models import (
        AdditionModel,
        SoustractionModel,
        MultiplicationModel,
        DivisionModel,
    )
    from package.page.text_section import DocumentEditor

    qmlRegisterType(DocumentEditor, "DocumentEditor", 1, 0, "DocumentEditor")
    AdditionModel.ddb = databaseObject
    SoustractionModel.ddb = databaseObject
    MultiplicationModel.ddb = databaseObject
    DivisionModel.ddb = databaseObject

    qmlRegisterType(AdditionModel, "Operations", 1, 0, "AdditionModel")
    qmlRegisterType(SoustractionModel, "Operations", 1, 0, "SoustractionModel")
    qmlRegisterType(MultiplicationModel, "Operations", 1, 0, "MultiplicationModel")
    qmlRegisterType(DivisionModel, "Operations", 1, 0, "DivisionModel")


def create_singleton_instance():
    # models
    from package.database_object import DatabaseObject
    from package.ui_manager import UiManager

    databaseObject = DatabaseObject(package.database.db, debug=False)
    ui_manager = UiManager()
    databaseObject.ui = ui_manager
    return databaseObject, ui_manager


def setup_qml(ddb, ui_manager):
    # import ressources
    import qrc

    # # set env : why ???
    # os.environ["QT_STYLE_OVERRIDE"] = ""

    # Create engine
    engine = QQmlApplicationEngine()

    # register property instance
    engine.rootContext().setContextProperty("ddb", ddb)
    engine.rootContext().setContextProperty("uiManager", ui_manager)

    # load main
    engine.load(QUrl("qrc:///qml/main.qml"))

    # quit if error
    if not engine.rootObjects():
        sys.exit(-1)

    return engine


def create_app():
    # appctxt = QApplication([])
    # appctxt.app.setApplicationName(APPNAME)
    # appctxt.app.setOrganizationName(ORGNAME)
    # appctxt.app.setOrganizationDomain("bla.com")
    # return appctxt
    app = QApplication([])
    app.setApplicationName(APPNAME)
    app.setOrganizationName(ORGNAME)
    app.setOrganizationDomain("bla.com")
    return app


def main():
    # First instanciate db
    main_init_database()

    # create de app
    appctxt = create_app()

    # create instance de ce qui sera des singleton dans qml
    databaseObject, ui_manager = create_singleton_instance()

    # register les new qml type
    register_new_qml_type(databaseObject)

    # setup le qml et retourne l'engine
    engine = setup_qml(databaseObject, ui_manager)

    # run the app
    sys.exit(appctxt.exec_())
    # sys.exit(appctxt.app.exec_())


if __name__ == "__main__":
    main()
