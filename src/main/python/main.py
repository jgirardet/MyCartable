from fbs_runtime.application_context.PySide2 import ApplicationContext
import sys
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import (
    QUrl,
)
from PySide2.QtCore import QObject,  Slot
import qrc

class MatiereModel(QObject):

    @Slot(result=str)
    def hello(self):
        return "Hello"





if __name__ == "__main__":
    appctxt = ApplicationContext()
    engine = QQmlApplicationEngine()
    qmlRegisterType(MatiereModel, "MatiereModel", 1, 0, "MatiereModel")

    engine.load(QUrl("qrc:///qml/main.qml"))
    engine.addImportPath("qrc:/qml/")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(appctxt.app.exec_())
