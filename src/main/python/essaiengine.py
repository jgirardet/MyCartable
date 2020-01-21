from PySide2.QtCore import QUrl, QObject
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

from PySide2.QtWidgets import QApplication
from package.database_object import DatabaseObject


root_qml = b"""
import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12


ApplicationWindow {
    id: root
    width: 800
    height: 600
    visible: true
    MenuBar {
        id: mymenu
        objectName: "mymenu"
        Menu {
            title: qsTr("&Edition")
            Action { text: qsTr("Cu&t") }
            Action { text: qsTr("&Copy") }
            Action { text: qsTr("&Paste") }
        }
    }
}
"""
# import package.database
# db = package.database.init_database()
# app = QApplication.instance() or QApplication([])
# ddb = DatabaseObject(db)
# engine = QQmlApplicationEngine()
# from package.qml_models import RecentsModel
#
# qmlRegisterType(RecentsModel, "" "RecentsModel", 1, 0, "RecentsModel")
# engine.rootContext().setContextProperty("ddb", ddb)
# # engine.loadData(root_qml)
# engine.load("/home/jimmy/dev/cacahuete/MyCartable/src/main/resources/base/qml/main.qml")
#
# print(engine.rootObjects())
# del engine
# del app


def init_database():
    # init database first
    import package.database

    package.database.db = package.database.init_database()
    # from package.database.factory import populate_database
    # populate_database()
    return package.database.db


def main_setup(ddb):
    import sys
    import importlib

    # if "qrc" in sys.modules:
    #     import qrc
    #     importlib.reload(qrc)
    # if "qrc" not in sys.modules:
    #     import qrc
    # import all database related stuf after
    from package.list_models import RecentsModel

    qmlRegisterType(RecentsModel, "" "RecentsModel", 1, 0, "RecentsModel")
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("ddb", ddb)
    print("apres ddb context")

    engine.loadData(root_qml)
    # engine.load(QUrl("qrc:///qml/MainMenuBar.qml"))
    # a = engine.load("/home/jimmy/dev/cacahuete/MyCartable/src/main/resources/base/qml/main.qml")
    print("apres load")

    # engine.addImportPath("qrc:/qml/")

    return engine


def root():
    app = QApplication.instance() or QApplication([])

    from package.database_object import DatabaseObject

    root_db = init_database()
    ddb = DatabaseObject(root_db)
    print("apres ddb")

    engine = main_setup(ddb)
    print("apres main")
    root_ = engine.rootObjects()[0]
    root_.ddb = ddb
    return app, engine
    # yield root_
    # app.quit()
    # import sys
    # del app
    # del engine
    # fn_reset_db(root_db)


app, engine = root()
print(engine.rootObjects())
app.quit()
# del app
# del engine


print("deuxime")
engine.clearComponentCache()
engine.exit.emit(2)
del engine
del app
print(dir())
app, engine = root()

print(engine.rootObjects()[0].children()[0].children()[1].objectName())
print(
    engine.rootObjects()[0].children()[0].children()[1].findChildren(QObject, "mymenu")
)
# app, engine = root()
# print(engine.rootObjects())
