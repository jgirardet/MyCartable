# from PySide2.QtCore import QUrl, QObject
# from PySide2.QtQml import QQmlProperty, QQmlApplicationEngine
# from PySide2.QtWidgets import QApplication
# from fixtures import ss
#
#
# class TestObjectDatabase:
#     def test_currentPage(self, rootObject):
#         rootObject.ddb._currentPage = 2
#         assert rootObject.ddb.currentPage == 2
#
#     def test_currentPage(self, rootObject):
#         rootObject.ddb._currentPage = 2
#         assert rootObject.ddb.currentPage == 2
#
#     def test_setCurrentPAge(self, rootObject, ddbr):
#         rlv = rootObject.W._recentsListView
#         rlv.currentIndex = 2
#         item = ss(rootObject.ddb.db.Page.recents)[4]
#         print(rlv.model)
#         a = QQmlProperty.read(rlv.obj, "onCurrentIndexChanged")
#         print(a)
#         # print(rlv.obj.contentItem.data)#(item['id'], item['matiere'])
#
#
