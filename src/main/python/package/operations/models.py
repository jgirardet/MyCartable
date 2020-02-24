from PySide2.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal, Property


class AdditionModel(QAbstractTableModel):

    datasChanged = Signal()

    @Property("QVariantList", notify=datasChanged)
    def datas(self):
        return self._datas

    @datas.setter
    def datas_set(self, value: int):
        self._datas = value
        self.datasChanged.emit()

    def __init__(self, parent=None):
        # def __init__(self, datas, parent=None):
        # self._datas = data
        super().__init__(parent=parent)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.datas[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.DisplayRole:
            return self.datas[index.row()][index.column()]
        else:
            return None

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.datas)
