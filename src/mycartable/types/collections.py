import typing

from PyQt5.QtCore import (
    QModelIndex,
    Qt,
    pyqtSlot,
    QAbstractListModel,
    QAbstractTableModel,
)
from mycartable.types.dtb import DTB


class DTBAble:
    """
        Modèle par défault des collections.
        Les appels database sont fait via self._dtb

        Virtual method:
        _roleNames
    *
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dtb = DTB()
        self.reset()

    def flags(self, index):
        if not index.isValid():
            return
        return super().flags(index) | Qt.ItemIsEditable

    def roleNames(self) -> typing.Dict:
        default = super().roleNames()
        for role, role_name in self._roleNames().items():
            default[role] = role_name
        return default

    def _reset(self):
        pass

    def _roleNames(self):
        return {}

    def _after_reset(self):
        pass

    @pyqtSlot(result=bool)
    def reset(self):
        """Int the model"""
        self.beginResetModel()
        self._reset()
        self.endResetModel()
        self._after_reset()
        return True


class RowAble:
    """
    Mixin de gestion des lignes
    Methods implémentables:
    _moveRows
    _deleteRows
    _removeRows

    """

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    def insertRows(self, row: int, count, parent=QModelIndex()) -> bool:
        """Insert n rows (n = 1 + count)  at row"""

        self.beginInsertRows(parent, row, row + count)
        # start datanase work
        self._insertRows(row, count)
        # end database work
        self.endInsertRows()
        return True

    def moveRow(self, sourceRow, destinationChild) -> bool:
        """Move a single row"""
        return self.moveRows(
            QModelIndex(), sourceRow, 0, QModelIndex(), destinationChild
        )

    def moveRows(
        self, sourceParent, sourceRow, count, destinationParent, destinationChild
    ) -> bool:
        """Move n rows (n=1+ count)  from sourceRow to destinationChild
        destinationChild index is the "before moving. So to move row 0 to row1
        destination child should be 2
        """
        if (
            sourceRow == destinationChild
            or destinationChild == sourceRow + 1  # +1 means non move
            or destinationChild > self.rowCount(QModelIndex())  # invalid
            or sourceRow > self.rowCount(QModelIndex()) - 1  # invalid
        ):
            return False

        self.beginMoveRows(
            sourceParent,
            sourceRow,
            sourceRow + count,
            destinationParent,
            destinationChild,
        )
        self._moveRows(sourceRow, count, destinationChild)

        self.endMoveRows()
        return True

    def removeRow(self, row, parent=QModelIndex()) -> bool:
        """Remove one row at index row"""
        return self.removeRows(row, 0, parent)

    def removeRows(self, row: int, count: int, parent=QModelIndex()) -> bool:
        """Remove n rows (n=1+count) starting at row"""
        self.beginRemoveRows(QModelIndex(), row, row + count)

        # start database work
        self._removeRows(row, count)
        # end database work

        self.endRemoveRows()
        return True

    def insertRow(self, row) -> bool:
        """Insert a single row at row"""
        return self.insertRows(row, 0)

    """
    Virtual Methods to be subclassed
    """

    def _insertRows(self, row, count):
        pass

    def _removeRows(self, row, count):
        pass

    def _moveRows(self, sourceRow, count, destinationChild):
        pass

    """QT Properties"""

    """QT pyqtSlots"""


class RowSlotable(RowAble):
    """
    Rowable avec les Slot
    """

    @pyqtSlot(result=bool)
    def append(self) -> bool:
        """pyqtSlot to append a row at the end"""
        return self.insertRow(self.rowCount())

    @pyqtSlot(int, int, result=bool)
    def move(self, source: int, target: int):
        """pyqtSlot to move a single row from source to target"""
        return self.moveRow(source, target)

    @pyqtSlot(int, result=bool)
    def remove(self, row: int):
        """pyqtSlot to remove one row"""
        return self.removeRow(row)


class BaseListModel(QAbstractListModel):
    """
    AbstractListModel with only kwargs constructor
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaseTableModel(QAbstractTableModel):
    """
    AbstractTableModel with only kwargs constructor
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DtbListModel(RowSlotable, DTBAble, BaseListModel):
    """
    DTB list model to subclass
    """


class DtbTableModel(RowSlotable, DTBAble, BaseTableModel):
    """
    DTB table model to sublclass
    """
