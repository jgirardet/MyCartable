import sys
import tempfile
from pathlib import Path

from PySide2.QtGui import QFont, QFontDatabase, QIcon
from mycartable.types.dtb import DTB
from mycartable.types.globus import Globus
from package import get_prod
from package.constantes import APPNAME, ORGNAME, BASE_FONT
from PySide2.QtCore import (
    QUrl,
    QStandardPaths,
    QSettings,
    QCoreApplication,
    QLocale,
)

from PySide2.QtWidgets import QApplication
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

from loguru import logger


import package.database
from pony.orm import Database, db_session


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
        # filename.unlink()
        filename = Path(tempfile.gettempdir()) / "devddbmdk.sqlite"

        # filename = "/home/jimmy/Documents/MyCartable/mycartable.ddb"
        # filename = ":memory:"
        # filename = ":memory:"
        create_db = True

    from migrations import make_migrations

    if filename != ":memory:" and Path(filename).is_file():
        migrate_res = make_migrations(filename)
        if not migrate_res:
            from package.files_path import LOGFILE

            raise SystemError(f"voir dans {LOGFILE}")

    package.database.db = newdb

    db = package.database.init_database(newdb, filename=filename, create_db=create_db)

    if not prod:
        from tests.factory import Faker

        with db_session:
            db.Configuration.add("annee", 2019)

        try:
            f = Faker(db)
            m = f.f_matiere(groupe=2019)
            ac = f.f_activite(matiere=m)
            p = f.f_page(activite=ac)
            f.f_textSection(page=p)
        except:
            pass

    return package.database.db


def register_new_qml_type(databaseObject, db):
    # from package.operations.models import (
    #     AdditionModel,
    #     SoustractionModel,
    #     MultiplicationModel,
    #     DivisionModel,
    # )

    # from package.page.text_section import DocumentEditor
    from package.page.frise_model import FriseModel
    from mycartable.types.changematieres import ChangeMatieres
    from mycartable.types.annee import Annee
    from mycartable.classeur import Classeur

    # AdditionModel.ddb = databaseObject
    # SoustractionModel.ddb = databaseObject
    # MultiplicationModel.ddb = databaseObject
    # DivisionModel.ddb = databaseObject
    ChangeMatieres.db = db
    Classeur.db = db
    DTB.db = db
    # Globus.db = db
    Annee

    # qmlRegisterType(DocumentEditor, "DocumentEditor", 1, 0, "DocumentEditor")
    # qmlRegisterType(AdditionModel, "MyCartable", 1, 0, "AdditionModel")
    # qmlRegisterType(SoustractionModel, "MyCartable", 1, 0, "SoustractionModel")
    # qmlRegisterType(MultiplicationModel, "MyCartable", 1, 0, "MultiplicationModel")
    # qmlRegisterType(DivisionModel, "MyCartable", 1, 0, "DivisionModel")
    # qmlRegisterType(AnnotationModel, "MyCartable", 1, 0, "AnnotationModel")
    qmlRegisterType(FriseModel, "MyCartable", 1, 0, "FriseModel")
    qmlRegisterType(ChangeMatieres, "MyCartable", 1, 0, "ChangeMatieres")
    qmlRegisterType(Classeur, "MyCartable", 1, 0, "Classeur")
    qmlRegisterType(DTB, "MyCartable", 1, 0, "Database")
    qmlRegisterType(Globus, "MyCartable", 1, 0, "Globus")
    qmlRegisterType(Annee, "MyCartable", 1, 0, "Annee")
    # from mycartable.classeur import Section

    # qmlRegisterType(Section, "MyCartable", 1, 0, "Section")


def create_singleton_instance(prod=False):
    # models
    from package.database_object import DatabaseObject
    from package.ui_manager import UiManager

    ui_manager = UiManager()
    databaseObject = DatabaseObject(package.database.db, ui=ui_manager, debug=False)
    globus = Globus()
    globus.db = package.database.db
    # if not prod:
    #     databaseObject.anneeActive = 2019
    #     with db_session:
    #         databaseObject.currentPage = databaseObject.db.Page.select().first().id
    dtb = DTB()

    return databaseObject, ui_manager, dtb, globus


def setup_qml(ddb, ui_manager, dtb, globus):

    # Create engine
    engine = QQmlApplicationEngine()

    # register property instance
    engine.rootContext().setContextProperty("ddb", ddb)
    engine.rootContext().setContextProperty("uiManager", ui_manager)
    engine.rootContext().setContextProperty("c_dtb", dtb)
    engine.rootContext().setContextProperty("globus", globus)

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
    db = main_init_database(filename=filename, prod=prod)

    # create instance de ce qui sera des singleton dans qml
    DTB.db = db
    databaseObject, ui_manager, dtb, globus = create_singleton_instance(prod)
    app.dao = databaseObject

    # register les new qml type
    register_new_qml_type(databaseObject, db)

    # setup le qml et retourne l'engine
    # import qrc

    engine = setup_qml(databaseObject, ui_manager, dtb, globus)

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
