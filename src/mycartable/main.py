import sys
import tempfile
from pathlib import Path

from PySide2.QtGui import QFont, QFontDatabase, QIcon, QPixmap
from mycartable.types.dtb import DTB
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


def main_init_database(filename=None, prod=False):
    # init database first
    settings = QSettings()
    logger.info(f"ficher settings : {settings.fileName()}")
    newdb = Database()
    create_db = False
    import package.database

    if prod:
        from package.files_path import ROOT_DATA

        filename = settings.value("General/ddb_path", ROOT_DATA / "mycartable.ddb")
        create_db = True
    else:
        QStandardPaths.setTestModeEnabled(True)
        # filename = Path(tempfile.gettempdir()) / "devddbmdk.sqlite"
        filename = "/home/jimmy/Documents/MyCartable/mycartable.ddb"
        # filename = ":memory:"
        # filename.unlink()
        create_db = True

    from migrations import make_migrations

    migrate_res = make_migrations(filename)
    if not migrate_res:
        from package.files_path import LOGFILE

        raise SystemError(f"voir dans {LOGFILE}")

    package.database.db = newdb

    db = package.database.init_database(newdb, filename=filename, create_db=create_db)

    # if not prod:
    #     from tests.python.factory import populate_database
    #
    #     try:
    #         populate_database()
    #     except:
    #         pass

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
    from package.page.frise_model import FriseModel

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
    qmlRegisterType(FriseModel, "MyCartable", 1, 0, "FriseModel")


def create_singleton_instance(prod=False):
    # models
    from package.database_object import DatabaseObject
    from package.ui_manager import UiManager

    ui_manager = UiManager()
    databaseObject = DatabaseObject(package.database.db, ui=ui_manager, debug=False)

    # if not prod:
    #     databaseObject.anneeActive = 2019
    #     with db_session:
    #         databaseObject.currentPage = databaseObject.db.Page.select().first().id
    dtb = DTB(package.database.db)

    return databaseObject, ui_manager, dtb


def setup_qml(ddb, ui_manager, dtb):
    # import ressources

    # # set env : why ???
    # os.environ["QT_STYLE_OVERRIDE"] = ""

    # Create engine
    engine = QQmlApplicationEngine()

    # register property instance
    engine.rootContext().setContextProperty("ddb", ddb)
    engine.rootContext().setContextProperty("uiManager", ui_manager)
    engine.rootContext().setContextProperty("c_dtb", dtb)

    # load main
    engine.load(QUrl("qrc:///qml/main.qml"))

    # quit if error
    if not engine.rootObjects():
        sys.exit(-1)

    return engine


def setup_logging():
    from package.files_path import LOGFILE

    logger.add(LOGFILE, rotation="10 MB")
    logger.info(f"logfile path : {LOGFILE}")


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
    databaseObject, ui_manager, dtb = create_singleton_instance(prod)
    app.dao = databaseObject

    # register les new qml type
    register_new_qml_type(databaseObject)

    # setup le qml et retourne l'engine
    # import qrc

    engine = setup_qml(databaseObject, ui_manager, dtb)

    # Manifestement l'acces au qrc n'est pas immediat apres creation de l'app
    # donc on met tout ça un peu plus "loin"
    app.setWindowIcon(QIcon(":/icons/mycartable.png"))
    QFontDatabase.addApplicationFont(":/fonts/Verdana.ttf")
    QFontDatabase.addApplicationFont(":/fonts/Code New Roman.otf")
    QFontDatabase.addApplicationFont(":/fonts/LiberationMono-Regular.ttf")
    font = QFont(BASE_FONT, 12, QFont.Normal)
    app.setFont(font)

    # run the app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
