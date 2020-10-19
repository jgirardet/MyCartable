from PySide2.QtCore import (
    QAbstractListModel,
    Slot,
    QModelIndex,
    Signal,
    Property,
    QObject,
    Qt,
)


class DaoListModel(QAbstractListModel):
    """
    Modèle par défault des collections.
    Les appels database sont fait via self.dao qui devra être donné en paramêtre
    au moment de l'instanciation vai la Property `dao`.
    Signal `tiggerInit` est connecté à reset(). Devra être appelé manuelement ou connecté
    à un autre signal

    Les méthods `_moveRows`, `_indesertRows`, `removeRows` peuvent être implémentées.

    Ne pas oublier d'implémenter RowCount

    ex : FriseModel

    """

    triggerInit = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.dao: "DatabaseObject" = None
        self.triggerInit.connect(lambda: self.reset())

    def flags(self, index):
        if not index.isValid():
            return
        return super().flags(index) | Qt.ItemIsEditable

    @Slot(result=bool)
    def append(self) -> bool:
        """Slot to append a row at the end"""
        return self.insertRow(self.rowCount())

    def insertRow(self, row) -> bool:
        """Insert a single row at row"""
        return self.insertRows(row, 0)

    def _insertRows(self, row, count):
        pass

    def insertRows(self, row: int, count, index=QModelIndex()) -> bool:
        """Insert n rows (n = 1 + count)  at row"""

        self.beginInsertRows(QModelIndex(), row, row + count)
        # start datanase work
        self._insertRows(row, count)
        # end database work
        self.endInsertRows()
        return True

    @Slot(int, int, result=bool)
    def move(self, source: int, target: int):
        """Slot to move a single row from source to target"""
        return self.moveRow(source, target)

    def moveRow(self, sourceRow, destinationChild) -> bool:
        """Move a single row"""
        return self.moveRows(
            QModelIndex(), sourceRow, 0, QModelIndex(), destinationChild
        )

    def _moveRows(self, sourceRow, count, destinationChild):
        pass

    def moveRows(
        self, sourceParent, sourceRow, count, destinationParent, destinationChild
    ) -> bool:
        """Move n rows (n=1+ count)  from sourceRow to destinationChild
        destinationChild index is the "before moving. So to move row 0 to row1
        destination child should be 2
        """
        if sourceRow == destinationChild:
            return False

        self.beginMoveRows(
            QModelIndex(),
            sourceRow,
            sourceRow + count,
            QModelIndex(),
            destinationChild,
        )
        self._moveRows(sourceRow, count, destinationChild)

        self.endMoveRows()
        return True

    @Slot(int, result=bool)
    def remove(self, row: int):
        """Slot to remove one row"""
        return self.removeRow(row)

    def removeRow(self, row, parent=QModelIndex()) -> bool:
        """Remove one row at index row"""
        return self.removeRows(row, 0, parent)

    def _removeRows(self, row, count):
        pass

    def removeRows(self, row: int, count: int, parent=QModelIndex()) -> bool:
        """Remove n rows (n=1+count) starting at row"""
        self.beginRemoveRows(QModelIndex(), row, row + count)

        # start database work
        self._removeRows(row, count)
        # end database work

        self.endRemoveRows()
        return True

    def _reset(self):
        pass

    def _after_reset(self):
        pass

    @Slot(result=bool)
    def reset(self):
        self.beginResetModel()
        self._reset()
        self.endResetModel()
        self._after_reset()
        return True

    daoChanged = Signal()

    @Property(QObject, notify=daoChanged)
    def dao(self):
        return self._dao

    @dao.setter
    def dao_set(self, value: int):
        self._dao = value
        self.daoChanged.emit()


class SectionDetailModel(DaoListModel):

    sectionIdChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._sectionId = ""
        self.sectionIdChanged.connect(self.triggerInit)

    @Property(str, notify=sectionIdChanged)
    def sectionId(self):
        return self._sectionId

    @sectionId.setter
    def sectionId_set(self, value: str):
        if value:
            self._sectionId = value
            self.sectionIdChanged.emit()
