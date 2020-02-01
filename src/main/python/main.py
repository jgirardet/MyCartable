import os

from fbs_runtime.application_context.PySide2 import ApplicationContext
import sys
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import QUrl, QObject, QRegExp

import package.database
from package.constantes import APPNAME
from package.database_object import DatabaseObject
import logging


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


def main_init_database():
    # init database first
    package.database.db = package.database.init_database()
    from package.database.factory import populate_database

    populate_database()
    return package.database.db


def main_setup(ddb):
    # set env
    os.environ["QT_STYLE_OVERRIDE"] = ""

    import qrc

    # import all ddb related stuf after

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("ddb", ddb)
    engine.load(QUrl("qrc:///qml/main.qml"))

    return engine


if __name__ == "__main__":

    main_init_database()

    appctxt = ApplicationContext()
    appctxt.app.setApplicationName(APPNAME)

    # models
    database = DatabaseObject(package.database.db)

    engine = main_setup(database)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(appctxt.app.exec_())
