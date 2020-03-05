from PySide2.QtCore import (
    QAbstractTableModel,
    Qt,
    QModelIndex,
    Signal,
    Property,
    QAbstractItemModel,
    QAbstractListModel,
    Slot,
)

from package.database import db
from pony.orm import db_session, make_proxy


class OperationModel(QAbstractListModel):
    cursorChanged = Signal()
    paramsChanged = Signal()
    sectionIdChanged = Signal()

    def __init__(self):
        super().__init__()
        self._cursor = 0
        self.editables = []
        self.db = db
        self.params = None
        self.sectionIdChanged.connect(self.on_sectionId_changed)

    def on_sectionId_changed(self):
        # c'est une post init method
        with db_session:
            self.proxy = make_proxy(self.db.Section.get(id=self.sectionId))
            self.params = self.proxy.to_dict(with_collections=True)
        self.editables = self.get_editables()

    @Property("QVariantList", notify=paramsChanged)
    def datas(self):
        return self.params["datas"]

    @Property(int, notify=paramsChanged)
    def rows(self):
        return int(self.params["rows"])

    @Property(int, notify=paramsChanged)
    def columns(self):
        return int(self.params["columns"])

    @Property(int, notify=sectionIdChanged)
    def sectionId(self):
        return self._sectionId

    @sectionId.setter
    def SectionId_set(self, value: int):
        self._sectionId = value
        self.sectionIdChanged.emit()

    @Property(int, notify=cursorChanged)
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor_set(self, value: int):
        if value != self._cursor:
            self._cursor = value
            self.cursorChanged.emit()

    def rowCount(self, parent=QModelIndex()) -> int:

        return len(self.datas)

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            value = self.datas[index.row()]
            return value

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsDropEnabled

        return QAbstractItemModel.flags(index) | Qt.ItemIsEditable

    def setData(self, index, value, role) -> bool:

        if index.isValid() and role == Qt.EditRole:
            with db_session:
                self.proxy.update_datas(index.row(), value)
            self.datas[index.row()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    @Slot(int)
    def autoMoveNext(self, currentIndex):
        self.cursor = self.auto_move_next(currentIndex)

    @Slot(int, int)
    def moveCursor(self, index, key):
        self.cursor = self.move_cursor(index, key)

    @Slot(int, result=bool)
    def readOnly(self, value):
        return value not in self.editables

    @Slot(int, result=bool)
    def isResultLine(self, index):
        return self.is_result_line(index)

    @Slot(int, result=bool)
    def isRetenueLine(self, index):
        return self.is_retenue_line(index)

    def auto_move_next(self, position):
        return position

    def get_editables(self):
        return []

    def is_result_line(self, index):
        return False

    def is_retenue_line(self, index):
        return False

    def move_cursor(self, index, key):
        return self.cursor


# TODO : get colomn from index and get row from index


class AdditionModel(OperationModel):
    def auto_move_next(self, position):
        if position == self.rowCount() - self.columns + 1:
            return position
        elif position > self.columns:
            diff = self.rowCount() - position
            new = int(self.columns - diff - 1)
        else:
            new = self.columns * (self.rows - 1) + position
        return new

    def get_editables(self):
        first_line = [x for x in range(1, self.columns - 1)]
        last_line = [
            x for x in range(self.rowCount() - self.columns + 1, self.rowCount())
        ]
        return first_line + last_line

    @Slot(int, result=bool)
    def isMiddleLine(self, index):
        return not self.isResultLine(index) and not self.isRetenueLine(index)

    def is_result_line(self, index):
        return index >= self.rowCount() - self.columns

    def is_retenue_line(self, index):
        return 0 <= index and index < self.columns

    def move_cursor(self, index, key):
        new = self.cursor
        if key == Qt.Key_Up:
            temp = index - self.columns * (self.rows - 1)
            if temp == self.columns - 1:
                new = temp - 1
            elif temp > 0:
                new = temp
        elif key == Qt.Key_Down:
            temp = index + self.columns * (self.rows - 1)
            if temp <= self.rowCount():
                new = temp
        elif key == Qt.Key_Left:
            if index - 1 in self.editables:
                new = index - 1
        elif key == Qt.Key_Right:
            if index + 1 in self.editables:
                new = index + 1

        return new
