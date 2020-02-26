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


class OperationModel(QAbstractListModel):
    paramsChanged = Signal()
    cursorChanged = Signal()

    def __init__(self):
        super().__init__()
        self._cursor = 0
        self.editables = []

    @Property("QVariantList", notify=paramsChanged)
    def datas(self):
        return self._params["datas"]

    @Property(int, notify=paramsChanged)
    def rows(self):
        return int(self._params["rows"])

    @Property(int, notify=paramsChanged)
    def columns(self):
        return int(self._params["columns"])

    @Property("QVariantMap", notify=paramsChanged)
    def params(self):
        return self._params

    @params.setter
    def params_set(self, value: int):
        self._params = value
        self.editables = self.get_editables()
        self.paramsChanged.emit()

    @Property(int, notify=cursorChanged)
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor_set(self, value: int):
        self._cursor = value
        self.cursorChanged.emit()

    def rowCount(self, parent=QModelIndex()) -> int:

        return len(self.datas)

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            value = self.datas[index.row()]
            return value

    @Slot(int)
    def autoMoveNext(self, currentIndex):
        self.cursor = self.auto_move_next(currentIndex)

    @Slot(int, int)
    def moveCursor(self, index, key):
        self.cursor = self.move_cursor(index, key)

    @Slot(int, result=bool)
    def readOnly(self, value):
        return value not in self.editables

    def auto_move_next(self, position):
        return position

    def get_editables(self):
        return []

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
