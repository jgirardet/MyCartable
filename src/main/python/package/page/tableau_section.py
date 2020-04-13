from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal, Property
from package.database import db

from pony.orm import db_session, make_proxy


class TableauModel(QAbstractTableModel):
    cursorChanged = Signal()
    paramsChanged = Signal()
    sectionIdChanged = Signal()
    ddb = None

    def __init__(self):
        super().__init__()
        self._cursor = 0
        self.db = db
        self.params = {"rows": 0, "columns": 0, "datas": []}
        self._sectionId = None
        self.sectionIdChanged.connect(self.load_params)
        self.dataChanged.connect(self.ddb.recentsModelChanged)

    @db_session
    def load_params(self):
        # c'est une post init method
        try:
            self.proxy = make_proxy(self.db.Section.get(id=self.sectionId))
        except AttributeError:
            self._sectionId = None
            return
        self.params = self.proxy.to_dict()
        self.custom_params_load()
        # self.cursor = self.getInitialPosition()

    def rowCount(self, parent=QModelIndex()) -> int:
        return int(self.params["rows"])

    def columnCount(self, parent=QModelIndex()) -> int:
        return int(self.params["columns"])

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            value = self.datas[index.row()][index.column()]
            return value

    @Property("QVariantList", notify=paramsChanged)
    def datas(self):
        return self.params["datas"]

    @Property(int, notify=sectionIdChanged)
    def sectionId(self):
        return self._sectionId

    @sectionId.setter
    def sectionId_set(self, value: int):
        self._sectionId = value
        self.sectionIdChanged.emit()

    def custom_params_load(self):
        pass
