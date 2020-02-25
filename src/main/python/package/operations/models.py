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


class AdditionModel(QAbstractListModel):
    paramsChanged = Signal()

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

    cursorChanged = Signal()

    @Property(int, notify=cursorChanged)
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor_set(self, value: int):
        print(value)
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
        if (
            0 < value < self.columns - 1
            or self.rows * self.columns - self.columns
            < value
            <= self.rows * self.columns
        ):
            return False
        else:
            return True

    @Slot(int)
    def updateCase(self, currentIndex):
        self.cursor = self._get_next_cursor_position(currentIndex)

    def _get_next_cursor_position(self, position):
        if position > self.columns:
            diff = self.rowCount() - position
            new = int(self.columns - diff - 1)
        else:
            new = self.columns * (self.rows - 1) + position
        return new


a = AdditionModel()
# print(a.index(1, 1).isValid())
# print(a.index(1, 1).internalPointer())
# print(a.index(2, 1).isValid())
# print(a.index(5, 1).isValid())
# print(a.index(0, 0).isValid())
# print("parent ******************")
# print(a.parent(a.index(0, 0)))
# print(a.parent(a.index(0, 1)))
# print(a.parent(a.index(1, 1)))
# print(a.parent(a.index(1, 0)))
print("rowcount ******************")
# assert a.rowCount(a.index(0, 0)) == 0
# assert a.rowCount(a.index(1, 0)) == 0
# assert a.rowCount(a.index(-1, -1)) == 3
# assert a.rowCount(a.index(0, 1)) == 0
#
# assert a.columnCount(a.index(0, 0)) == 2, a.columnCount(a.index(0, 0))
# assert a.columnCount(a.index(0, 1)) == 0, a.columnCount(a.index(0, 1))
# assert a.columnCount(a.index(-1, -1)) == 2, a.columnCount(a.index(-1, -1))
#
# assert a.hasChildren(QModelIndex())
# assert a.hasChildren(a.index(0, 0))

# print(a.rowCount())
# print(a.columnCount(a.index(1, 1)))
# print(a.columnCount())
# a.data(a.index(1, 1), Qt.DisplayRole)
# a.data(a.index(-1, 1), Qt.DisplayRole)
# a.data(a.index(2, 2), Qt.DisplayRole)
# a.data(a.index(2, 1), Qt.DisplayRole)
# a.data(a.index(0, 0), Qt.DisplayRole)

# class AdditionModel(QAbstractItemModel):
#
#     datasChanged = Signal()
#
#     @Property("QVariantList", notify=datasChanged)
#     def datas(self):
#         return self._datas
#
#     @datas.setter
#     def datas_set(self, value: int):
#         self._datas = []
#         self._datas = [[0, 1, 2, 3,], [4, 5, 6, 7], [8, 9, 10, 11]]
#         # for el in value:
#         #     self._datas += value
#         print(self._datas)
#         self.datasChanged.emit()
#
#     def __init__(self, parent=None):
#         # def __init__(self, datas, parent=None):
#         super().__init__(parent=parent)
#         self._datas =' []
#
#     def columnCount(self, parent=QModelIndex()) -> int:
#         if not parent.isValid():
#             return 4
#         else:
#             return 0
#         # return 4
#         # return len(self._datas[0])
#         # return len(self._datas[0])
#
#     def rowCount(self, parent=QModelIndex()) -> int:
#         # if parent.isValid():
#         #     return 0
#         # else:
#         # return len(self._datas)
#         if not parent.isValid():
#             return 3
#         else:
#             return 0
#
#     def data(self, index, role):
#         if not index.isValid():
#             return None
#         elif role == Qt.DisplayRole:
#             # return self.datas[index.row()]
#             return self._datas[index.row()][index.column()]
#         else:
#             return None
#
#     def index(self, row, column, parent=QModelIndex()):
#         # The model/view framework considers negative values out-of-bounds,
#         # however in python they work when indexing into lists. So make sure
#         # we return an invalid index for out-of-bounds row/col
#         print(row, column)
#         if (
#             row < 0
#             or column < 0
#             or row >= self.rowCount(parent)
#             or column >= self.columnCount(parent)
#         ):
#             return QModelIndex()
#
#         if not parent.isValid():
#             return QModelIndex()
#
#         return self.createIndex(row, column, self._datas[row][column])
#
#         # if not parent.isValid():
#         #     parentItem = self.datas
#         # else:
#         #     parentItem = parent.internalPointer()
#
#         # return self.createIndex(row, column, self.datas[row][column])
#         # return self.createIndex(row, column, self.datas[row])
#
#     def parent(self, index):
#         """
#         Public method to get the index of the parent object.
#
#         @param index index of the item (QModelIndex)
#         @return index of parent item (QModelIndex)
#         """
#         # return QModelIndex()
#         if not index.isValid():
#             return QModelIndex()
#         #
#         if index.column() == 0:
#             return QModelIndex()
#
#         else:
#             self.createIndex(index.row(), 0, self._datas[index.row()][0])
# parentItem = childItem.parent()
#
# if parentItem == self.rootItem:
# return QModelIndex()

# return self.createIndex(parentItem.row(),0 , parentItem)

# def hasChildren(self, parent=QModelIndex()) -> bool:
# if parent.isValid():
#     return False
# else:
#     return True  # (len(self._workspace.sortedDocuments) > 0)


#
# class AdditionModel(QAbstractTableModel):
#
#     datasChanged = Signal()
#
#     @Property("QVariantList", notify=datasChanged)
#     def datas(self):
#         return self._datas
#
#     @datas.setter
#     def datas_set(self, value: int):
#         self._datas = value
#         self.datasChanged.emit()
#
#     def __init__(self, parent=None):
#         # def __init__(self, datas, parent=None):
#         super().__init__(parent=parent)
#         self._datas = []
#
#     def columnCount(self, parent=QModelIndex()) -> int:
#         return len(self.datas[0])
#
#     def data(self, index, role):
#         print(self.datas, self.rowCount(), self.columnCount())
#         print(index.row(), index.column(), index.isValid())
#         if not index.isValid():
#             return None
#         elif role == Qt.DisplayRole:
#             print(self.datas[index.row()][index.column()])
#             return self.datas[index.row()][index.column()]
#         else:
#             return None
#
#     def rowCount(self, parent=QModelIndex()) -> int:
#         return len(self.datas)
