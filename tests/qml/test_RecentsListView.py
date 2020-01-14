from PySide2.QtCore import QUrl, QObject
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType, QtQml
from PySide2.QtQuick import QQuickView, QQuickWindow
from PySide2.QtWidgets import QApplication
from fbs_runtime.application_context.PySide2 import ApplicationContext
from package.database.factory import f_activite
from package.qml_models import RecentsModel
from PySide2.QtQml import QtQml


class TestConnectionWithQml:

    def testSignalArguments(self, database):
        from main import main_setup
        from package.database_object import DatabaseObject
        appctxt = ApplicationContext()
        ddb =  DatabaseObject(database)
        engine = main_setup(ddb)
        print(engine.rootObjects())
        root = engine.rootObjects()[0]
        assert root
        button = root.findChild(QObject, "_itemDispatcher")
        print(button)
        f_activite()
        # view.show()
        button.newPage.emit(1)
        # button.clicked.emit()
        # self.assertEqual(obj.value, 42)