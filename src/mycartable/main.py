import sys
import tempfile
from pathlib import Path

from PySide2.QtGui import QFont, QFontDatabase, QIcon
from mycartable.classeur import Classeur
from mycartable.defaults.constantes import APPNAME, ORGNAME
from mycartable.defaults.configuration import (
    DEFAUT_CONFIGURATION,
    KEEP_UPDATED_CONFIGURATION,
)
from mycartable.types import Annee, ChangeMatieres
from mycartable.types.dtb import DTB
from mycartable import get_prod

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

import qrc  # QRC do not erase

from pony.orm import Database, db_session


def main_init_database(filename=None, prod=False):
    # init database first
    settings = QSettings()
    logger.info(f"ficher settings : {settings.fileName()}")
    newdb = Database()
    create_db = False
    import mycartable.database

    if prod:
        from mycartable.defaults.files_path import ROOT_DATA

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

    from mycartable.migrations.migrations import make_migrations

    if filename != ":memory:" and Path(filename).is_file():
        migrate_res = make_migrations(filename)
        if not migrate_res:
            from mycartable.defaults.files_path import LOGFILE

            raise SystemError(f"voir dans {LOGFILE}")

    mycartable.database.db = newdb

    db = mycartable.database.init_database(
        newdb, filename=filename, create_db=create_db
    )

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

    return mycartable.database.db


def register_new_qml_type():

    qmlRegisterType(ChangeMatieres, "MyCartable", 1, 0, "ChangeMatieres")
    qmlRegisterType(Classeur, "MyCartable", 1, 0, "Classeur")
    qmlRegisterType(DTB, "MyCartable", 1, 0, "Database")
    qmlRegisterType(Annee, "MyCartable", 1, 0, "Annee")


def load_engine(engine: QQmlApplicationEngine):
    # load main
    engine.load(QUrl("qrc:///qml/main.qml"))

    # quit if error
    if not engine.rootObjects():
        sys.exit(-1)


def setup_logging():
    from mycartable.defaults.files_path import LOGFILE

    logger.add(LOGFILE, rotation="10 MB")
    logger.info(f"logfile path : {LOGFILE}")


def update_configuration(db: Database):
    with db_session:

        for k, v in DEFAUT_CONFIGURATION.items():
            if db.Configuration.option(k) is None:
                db.Configuration.add(k, v)
        for k, v in KEEP_UPDATED_CONFIGURATION.items():
            db.Configuration.add(k, v)


def add_database_to_types(db: Database):

    ChangeMatieres.db = db
    DTB.db = db


def initial_setup_application(app: QApplication):
    # global settings
    QCoreApplication.setApplicationName(APPNAME)
    QCoreApplication.setOrganizationName(ORGNAME)
    QLocale.setDefault(QLocale(QLocale.French, QLocale.France))

    app.setWindowIcon(QIcon(":/icons/mycartable.png"))
    QFontDatabase.addApplicationFont(":/fonts/Verdana.ttf")
    QFontDatabase.addApplicationFont(":/fonts/Code New Roman.otf")
    QFontDatabase.addApplicationFont(":/fonts/LiberationMono-Regular.ttf")


def late_setup_application(app: QApplication, db: Database):
    with db_session:
        base_font = db.Configuration.option("fontMain")
    font = QFont(base_font, 12, QFont.Normal)
    app.setFont(font)


@logger.catch(reraise=True)
def main(filename=None):
    prod = get_prod()
    if not prod:
        QStandardPaths.setTestModeEnabled(True)
    setup_logging()
    logger.info(f"Application en mode {'PROD' if prod else 'DEBUG'}")

    # create de app and initial setup
    app = QApplication([])
    initial_setup_application(app)

    # create database and update configation with default values if needed
    db = main_init_database(filename=filename, prod=prod)
    update_configuration(db)
    add_database_to_types(db)

    # qml
    register_new_qml_type()
    engine = QQmlApplicationEngine()

    # late configuration
    late_setup_application(app, db)

    # run the app
    load_engine(engine)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
