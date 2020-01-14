from PySide2.QtCore import QUrl, QObject, QMetaObject, QGenericArgument
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType, QtQml, QQmlProperty
from PySide2.QtQuick import QQuickView, QQuickWindow
from PySide2.QtWidgets import QApplication
from fbs_runtime.application_context.PySide2 import ApplicationContext
from fixtures import r, s
from package.database.factory import f_activite, f_matiere
from PySide2.QtCore import QTimer




class TestConnectionWithQml:

    def testSignalArguments(self, database, engine):
        f_matiere(nom="bla")
        f_matiere(nom="lot")
        root = engine()
        # select = root.g("_comboBoxSelectMatiere")
        # assert r(select, "model") == ['bla', 'lot']
        select = root.W._comboBoxSelectMatiere
        select.model == ['bla', 'lot']
        recent_header =  root.g("recentsHeader")
        assert r(recent_header, "text") == '-1'

        print(ddb)
        # QMetaObject.invokeMethod(select, None,  b"onActivated",  1)
        # Q_ARG
        # QTimer.singleShot(0, select, b"onActivated")
        print(ddb.m_d.nom_id)
        ddb.setCurrentMatiereFromString("lot")
        assert r(recent_header, "text") == '2'
        assert r(select, "currentText") == 'lot'
        # view.show()
        # button.clicked.emit()
        # self.assertEqual(obj.value, 42)