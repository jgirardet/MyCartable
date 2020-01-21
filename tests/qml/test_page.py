from PySide2.QtCore import QUrl, QObject
from PySide2.QtQml import QQmlProperty, QQmlApplicationEngine
from PySide2.QtWidgets import QApplication
from fixtures import ss


class TestObjectDatabase:
    def test_currentPage(self, rootObject):
        rootObject.ddb._currentPage = 2
        assert rootObject.ddb.currentPage == 2

    def test_currentPage(self, rootObject):
        rootObject.ddb._currentPage = 2
        assert rootObject.ddb.currentPage == 2

    def test_setCurrentPAge(self, rootObject, ddbr):
        rlv = rootObject.W._recentsListView
        rlv.currentIndex = 2
        item = ss(rootObject.ddb.db.Page.recents)[4]
        print(rlv.model)
        a = QQmlProperty.read(rlv.obj, "onCurrentIndexChanged")
        print(a)
        # print(rlv.obj.contentItem.data)#(item['id'], item['matiere'])

    def test_lv(self, ddbr, matieres_list):
        qapp = QApplication.instance() or QApplication([])
        engine = QQmlApplicationEngine()

        # Import stuff
        from package.database_object import DatabaseObject
        import qrc
        from package.database.factory import populate_database

        # Add type and property
        ddb = DatabaseObject(ddbr)
        engine.rootContext().setContextProperty("ddb", ddb)
        engine.load(QUrl("qrc:///qml/RecentsListView.qml"))
        root = engine.rootObjects()[0]

        # set context and utils
        populate_database(matieres_list=matieres_list, nb_activite=3, nb_page=100)
        # root.W = QRootWrapper(root)
        # root.ddb = engine.rootContext().contextProperty("ddb")

        print(QQmlProperty.read(root, "spacing"))
        print(dir(root))
        d = QQmlProperty.read(root, "delegate")
        print(QQmlProperty.read(d, "contentItem"))

        del root
        del engine
        del qapp
