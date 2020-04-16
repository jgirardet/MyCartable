import json

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal, Property
from descriptors import cachedproperty
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
        print(self.params)

    def rowCount(self, parent=QModelIndex()) -> int:
        return int(self.params["rows"])

    def columnCount(self, parent=QModelIndex()) -> int:
        return int(self.params["columns"])

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            value = (
                self.datas[index.row()][index.column()]
                + str(index.row())
                + " "
                + str(index.column())
            )
            return value

    @property
    def datas(self):
        return self.params["datas"]

    def setData(self, index, value, role) -> bool:
        if index.isValid() and role == Qt.EditRole:
            old = self.datas[index.row()][index.column()]
            if old == value:
                return False

            with db_session:
                self.proxy.update_datas(index.row(), index.column(), value)
            self.datas[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    @Property(int, notify=sectionIdChanged)
    def sectionId(self):
        return self._sectionId

    @sectionId.setter
    def sectionId_set(self, value: int):
        self._sectionId = value
        self.sectionIdChanged.emit()

    def custom_params_load(self):
        pass

    # columnsChanged = Signal()
    #
    # @Property(int, notify=columnsChanged)
    # def columns(self):
    #     return self.columnCount()

    rowsChanged = Signal()

    @Property(int, notify=rowsChanged)
    def n_rows(self):
        """créer uniquement pour un problème de conflit avec TableModel """
        return self.rowCount()

    # @rows.setter
    # def columns_set(self, value: int):
    #     self._columns = value
    #     self.columnsChanged.emit()

    # @Property(int, notify=cursorChanged)
    # def cursor(self):
    #     return self._cursor
    #
    # @cursor.setter
    # def cursor_set(self, value: int):
    #     self._cursor = value
    #     self.cursorChanged.emit()

    #
    # numberOfLinesChanged = Signal()
    #
    # @Property(int, notify=numberOfLinesChanged)
    # def numberOfLines(self):
    #     a = (
    #         sum(max(x.count("\n") for x in ligne) for ligne in self.datas)
    #         + self.rowCount()
    #     )
    #     print(a, "numberOfLines")
    #     return a
