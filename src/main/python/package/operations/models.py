from PySide2.QtCore import (
    QAbstractTableModel,
    Qt,
    QModelIndex,
    Signal,
    Property,
    QAbstractItemModel,
)


class AdditionModel(QAbstractItemModel):

    datasChanged = Signal()

    @Property("QVariantList", notify=datasChanged)
    def datas(self):
        return self._datas

    @datas.setter
    def datas_set(self, value: int):
        self._datas = []
        for el in value:
            self._datas += value
        self._datas
        self.datasChanged.emit()

    def __init__(self, parent=None):
        # def __init__(self, datas, parent=None):
        super().__init__(parent=parent)
        self._datas = []

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.datas[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.DisplayRole:
            return self.datas[index.row()][index.column()]
        else:
            return None

    def index(self, row, column, parent=QModelIndex()):
        # The model/view framework considers negative values out-of-bounds,
        # however in python they work when indexing into lists. So make sure
        # we return an invalid index for out-of-bounds row/col
        print(row, column)
        if (
            row < 0
            or column < 0
            or row >= self.rowCount(parent)
            or column >= self.columnCount(parent)
        ):
            return QModelIndex()

        # if not parent.isValid():
        #     parentItem = self.datas
        # else:
        #     parentItem = parent.internalPointer()

        return self.createIndex(row, column, self.datas[row][column])

    def parent(self, index):
        """
        Public method to get the index of the parent object.

        @param index index of the item (QModelIndex)
        @return index of parent item (QModelIndex)
        """
        return QModelIndex()
        # if not index.isValid():
        #     return QModelIndex()
        #
        # childItem = index.internalId()
        # parentItem = childItem.parent()
        #
        # if parentItem == self.rootItem:
        # return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        else:
            return len(self.datas)

    def hasChildren(self, parent=QModelIndex()) -> bool:
        if parent.isValid():
            return False
        else:
            return True  # (len(self._workspace.sortedDocuments) > 0)


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
