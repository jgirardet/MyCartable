import sys
from pathlib import Path

from PySide2.QtGui import QFont, QFontDatabase, QIcon, QPixmap
from package import get_prod
from package.constantes import APPNAME, ORGNAME, BASE_FONT
from PySide2.QtCore import (
    QUrl,
    QStandardPaths,
    QSettings,
    QCoreApplication,
    QLocale,
    QFile,
)

from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

from loguru import logger


import package.database
from pony.orm import DBException, db_session, Database
import tempfile


def main_init_database(filename=None, prod=False):
    # init database first
    settings = QSettings()
    logger.info(f"ficher settings : {settings.fileName()}")
    newdb = Database()
    import package.database

    if prod:
        from package.files_path import ROOT_DATA

        filename = settings.value("General/ddb_path", ROOT_DATA / "mycartable.ddb")
        create_db = True
    else:
        QStandardPaths.setTestModeEnabled(True)
        filename = str(Path(tempfile.gettempdir()) / "filename")
        create_db = True

    package.database.db = newdb

    db = package.database.init_database(newdb, filename=filename, create_db=create_db)

    if not prod:
        from tests.python.factory import populate_database

        # populate_database()

    return package.database.db


def register_new_qml_type(databaseObject):
    from package.operations.models import (
        AdditionModel,
        SoustractionModel,
        MultiplicationModel,
        DivisionModel,
    )

    # from package.page.text_section import DocumentEditor
    from package.page.annotation_model import AnnotationModel

    AdditionModel.ddb = databaseObject
    SoustractionModel.ddb = databaseObject
    MultiplicationModel.ddb = databaseObject
    DivisionModel.ddb = databaseObject

    # qmlRegisterType(DocumentEditor, "DocumentEditor", 1, 0, "DocumentEditor")
    qmlRegisterType(AdditionModel, "MyCartable", 1, 0, "AdditionModel")
    qmlRegisterType(SoustractionModel, "MyCartable", 1, 0, "SoustractionModel")
    qmlRegisterType(MultiplicationModel, "MyCartable", 1, 0, "MultiplicationModel")
    qmlRegisterType(DivisionModel, "MyCartable", 1, 0, "DivisionModel")
    qmlRegisterType(AnnotationModel, "MyCartable", 1, 0, "AnnotationModel")


def create_singleton_instance(prod=False):
    # models
    from package.database_object import DatabaseObject
    from package.ui_manager import UiManager

    ui_manager = UiManager()
    databaseObject = DatabaseObject(package.database.db, ui=ui_manager, debug=False)

    if not prod:
        databaseObject.anneeActive = 2019
        with db_session:
            databaseObject.currentPage = databaseObject.db.Page.select().first().id

    return databaseObject, ui_manager


def setup_qml(ddb, ui_manager):
    # import ressources

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


def setup_logging():
    t = Path(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), APPNAME)
    if not t.is_dir():
        t.mkdir(parents=True)
    logger_path = t / "mycartable_log.txt"
    logger.add(t / logger_path, rotation="10 MB")
    logger.info(f"logfile path : {logger_path}")


@logger.catch(reraise=True)
def main(filename=None):
    prod = get_prod()
    if not prod:
        QStandardPaths.setTestModeEnabled(True)
    setup_logging()

    logger.info(f"Application en mode {'PROD' if prod else 'DEBUG'}")

    # global settings
    QCoreApplication.setApplicationName(APPNAME)
    QCoreApplication.setOrganizationName(ORGNAME)
    QLocale.setDefault(QLocale(QLocale.French, QLocale.France))

    # create de app
    app = QApplication([])

    # First instanciate db
    main_init_database(filename=filename, prod=prod)

    # create instance de ce qui sera des singleton dans qml
    databaseObject, ui_manager = create_singleton_instance(prod)
    app.dao = databaseObject

    # register les new qml type
    register_new_qml_type(databaseObject)

    # setup le qml et retourne l'engine
    # import qrc

    engine = setup_qml(databaseObject, ui_manager)

    # Manifestement l'acces au qrc n'est pas immediat apres creation de l'app
    # donc on met tout ça un peu plus "loin"
    app.setWindowIcon(QIcon(":/icons/mycartable.png"))
    QFontDatabase.addApplicationFont(":/fonts/Verdana.ttf")
    font = QFont(BASE_FONT, 12, QFont.Normal)
    app.setFont(font)

    # run the app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
