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

    @Property("QVariantList", notify=paramsChanged)
    def datas(self):
        return self._params["datas"]

    @Property(int, notify=paramsChanged)
    def rows(self):
        return self._params["rows"]

    @Property(int, notify=paramsChanged)
    def columns(self):
        return self._params["columns"]

    @Property("QVariantMap", notify=paramsChanged)
    def params(self):
        return self._params

    @params.setter
    def params_set(self, value: int):
        self._params = value
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

    @Slot(int, result=bool)
    def readOnly(self, value):
        return self.read_only(value)

    @Slot(int)
    def autoMoveNext(self, currentIndex):
        self.cursor = self.auto_move_next(currentIndex)

    def auto_move_next(self, position):
        return position

    def read_only(self, value):
        return False


class AdditionModel(OperationModel):
    def auto_move_next(self, position):
        if position > self.columns:
            diff = self.rowCount() - position
            new = int(self.columns - diff - 1)
        else:
            new = self.columns * (self.rows - 1) + position
        return new

    def read_only(self, value):
        if (
            0 < value < self.columns - 1
            or self.rows * self.columns - self.columns
            < value
            <= self.rows * self.columns
        ):
            return False
        else:
            return True
