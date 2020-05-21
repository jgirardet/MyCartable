from PySide2.QtGui import QFont, QFontDatabase
from package.constantes import APPNAME, ORGNAME
from PySide2.QtCore import (
    QUrl,
    QLocale,
    QStandardPaths,
    QSettings,
    QCoreApplication,
    QFile,
)
import os

# from fbs_runtime.application_context.PySide2 import ApplicationContext
from pathlib import Path

from PySide2.QtWidgets import QApplication
import sys
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

import sys

from package import PROD

import package.database
import logging


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def main_init_database(filename=None):
    # init database first
    settings = QSettings()
    if PROD:
        from package.files_path import ROOT_DATA

        filename = settings.value("General/ddb_path", ROOT_DATA / "mycartable.ddb")
        create_db = True
    else:
        filename = ":memory:"
        create_db = False

    package.database.db = package.database.init_database(
        filename=filename, create_db=create_db
    )

    if not PROD:

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
    from package.page.tableau_section import TableauModel
    from package.page.annotation_model import AnnotationModel

    AdditionModel.ddb = databaseObject
    SoustractionModel.ddb = databaseObject
    MultiplicationModel.ddb = databaseObject
    DivisionModel.ddb = databaseObject
    TableauModel.ddb = databaseObject

    qmlRegisterType(DocumentEditor, "DocumentEditor", 1, 0, "DocumentEditor")
    qmlRegisterType(AdditionModel, "MyCartable", 1, 0, "AdditionModel")
    qmlRegisterType(SoustractionModel, "MyCartable", 1, 0, "SoustractionModel")
    qmlRegisterType(MultiplicationModel, "MyCartable", 1, 0, "MultiplicationModel")
    qmlRegisterType(DivisionModel, "MyCartable", 1, 0, "DivisionModel")
    qmlRegisterType(TableauModel, "MyCartable", 1, 0, "TableauModel")
    qmlRegisterType(AnnotationModel, "MyCartable", 1, 0, "AnnotationModel")


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


#
# def create_app():
#     app = QApplication([])
#     return app


def main(filename=None):
    if not PROD:
        QStandardPaths.setTestModeEnabled(True)

    # global settings
    QCoreApplication.setApplicationName(APPNAME)
    QCoreApplication.setOrganizationName(ORGNAME)

    # create de app
    app = QApplication([])

    # First instanciate db
    main_init_database(filename=filename)

    # create instance de ce qui sera des singleton dans qml
    databaseObject, ui_manager = create_singleton_instance()
    app.dao = databaseObject

    # register les new qml type
    register_new_qml_type(databaseObject)

    # setup le qml et retourne l'engine
    # import qrc

    engine = setup_qml(databaseObject, ui_manager)
    QFontDatabase.addApplicationFont(":/fonts/Verdana.ttf")
    font = QFont("Verdana", 12, QFont.Normal)
    # font = QFont('Verdana', 12, QFont.Normal)
    app.setFont(font)

    # run the app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
