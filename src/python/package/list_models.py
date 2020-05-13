import PySide2
from PySide2.QtCore import (
    QAbstractListModel,
    Qt,
    Slot,
    QModelIndex,
    QByteArray,
    QUrl,
    QAbstractItemModel,
    Signal,
    Property,
    QObject,
)
from mimesis import typing
from pony.orm import db_session, ObjectNotFound, make_proxy
from package.database import db
import logging

LOG = logging.getLogger("__name__")


class PageModel(QAbstractListModel):

    db = db
    PageRole = Qt.UserRole + 1

    def __init__(self, parent=None):
        self.page = None
        super().__init__(parent=parent)
        self.row_count = 0

    @db_session
    def data(self, index, role: int) -> typing.Any:
        if not index.isValid():
            return None
        elif role == self.PageRole:
            return (
                self.page.sections.select(lambda sec: sec.position == index.row())
                .first()
                .to_dict()
            )
        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsDropEnabled
        return QAbstractItemModel.flags(index) | Qt.ItemIsEditable

    def insertRow(self) -> bool:
        nb = self.rowCount()
        # print("insert orw", row)
        return super().insertRow(nb)

    def insertRows(self, row: int, value, index=QModelIndex()) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + value - 1)
        with db_session:
            self.row_count = self.page.sections.count()
        self.endInsertRows()
        self.lastPosition = row
        return True

    def roleNames(self) -> typing.Dict:
        default = super().roleNames()
        default[self.PageRole] = QByteArray(b"page")
        return default

    # def removeRow(self, row):
    #     self.removeRows(row, row, parent=QModelIndex())
    #
    # def removeRows(self, row: int, count: int, parent: QModelIndex()) -> bool:
    #     self.beginRemoveRows(QModelIndex(), row, row)
    #     self.endRemoveRows()
    #     self.lastPosition == row
    #     return True

    # @Slot(int, int, int, result=bool)
    # def moveRows(
    #     self,
    #     # sourceParent,
    #     sourceRow: int,
    #     count: int,
    #     # destinationParent,
    #     destinationChild: int,
    # ) -> bool:
    #     self.beginMoveRows(
    #         QModelIndex(),
    #         sourceRow,
    #         sourceRow + count,
    #         QModelIndex(),
    #         destinationChild,
    #     )
    #     self.endMoveRows()
    #     return True

    @Slot(int, int, result=bool)
    def move(self, source: int, target: int):
        if source == target:
            return

        elif source > target:
            end = target

        elif source < target:
            end = target + 1

        if not self.beginMoveRows(QModelIndex(), source, source, QModelIndex(), end,):
            return False

        with db_session:
            source_obj = self.page.sections.select(
                lambda o: o.position == source
            ).first()
            source_obj.position = target

        self.endMoveRows()
        return True

    def rowCount(self, parent=QModelIndex()) -> int:
        return self.row_count

    @db_session
    def slotReset(self, value):
        self.beginResetModel()
        if not value:
            self.page = None
        with db_session:
            page = self.db.Page.get(id=value)
            if not page:
                self.endResetModel()
                return
            self.page = make_proxy(page)
            self.row_count = self.page.sections.count()
        self.lastPositionChanged.emit()
        self.endResetModel()
        return True

    ################## Property ########################

    lastPositionChanged = Signal()

    @Property(int, notify=lastPositionChanged)
    def lastPosition(self):
        with db_session:
            return self.page.lastPosition
        return self.lastPosition

    @lastPosition.setter
    def lastPosition_set(self, value: int):
        print("last position sect")
        with db_session:
            self.page.lastPosition = value
        self.lastPositionChanged.emit()
