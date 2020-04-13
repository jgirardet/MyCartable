# from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from package.database import db

# from pony.orm import db_session, make_proxy
#


#
# class TableauModel(QAbstractTableModel):
#     def __init__(self):
#         super().__init__()
#         self._cursor = 0
#         self.db = db
#         self.params = {"rows": 0, "columns": 0, "datas": []}
#         self._sectionId = None
#         self.sectionIdChanged.connect(self.load_params)
#         self.dataChanged.connect(self.ddb.recentsModelChanged)
#
#     @db_session
#     def load_params(self):
#         # c'est une post init method
#         try:
#             self.proxy = make_proxy(self.db.Section.get(id=self.sectionId))
#         except AttributeError:
#             self._sectionId = None
#             return
#         self.params = self.proxy.to_dict()
#         self.custom_params_load()
#         self.cursor = self.getInitialPosition()
#
#     def rowCount(self, parent=QModelIndex()) -> int:
#         return int(self.params["rows"])
#
#     def columnCount(self, parent=QModelIndex()) -> int:
#         return int(self.params["columns"])
#
#     def data(self, index, role):
#         if index.isValid() and role == Qt.DisplayRole:
#             value = self.datas[index.row() * index.column()]
#             return value
