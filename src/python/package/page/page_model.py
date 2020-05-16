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
from pony.orm import db_session, ObjectNotFound, make_proxy, flush
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

    def insertRow(self, value) -> bool:
        return self.insertRows(value, 0)

    def insertRows(self, row: int, value, index=QModelIndex()) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + value - 1)
        with db_session:
            self.count = self.page.sections.count()
        self.lastPosition = row
        self.endInsertRows()
        return True

    def roleNames(self) -> typing.Dict:
        default = super().roleNames()
        default[self.PageRole] = QByteArray(b"page")
        return default

    @Slot(int, int, result=bool)
    def move(self, source: int, target: int):
        if source == target:
            return False

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
            if not source_obj:
                return False
            source_obj.position = target

        self.endMoveRows()
        self.lastPosition = target
        return True

    @Slot(int, result=bool)
    def removeSection(self, row):
        return self.removeRows(row, 0, parent=QModelIndex())

    def removeRows(self, row: int, count: int, parent: QModelIndex()) -> bool:
        # count = nombre de row à supprimer en plus
        self.beginRemoveRows(QModelIndex(), row, row + count)
        with db_session:
            item = self.page.sections.select(lambda sec: sec.position == row).first()
            if item:
                item.delete()
            else:
                return False
            flush()  # bien garder pour le count d'apres
            self.count = self.page.sections.count()
            self.lastPosition = row
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QModelIndex()) -> int:
        return self.row_count

    countChanged = Signal()

    @Property(int, notify=countChanged)
    def count(self):
        return self.row_count

    @count.setter
    def count_set(self, value: int):
        self.row_count = value
        self.countChanged.emit()

    def slotReset(self, value):
        self.beginResetModel()
        # breakpoint()
        if not value:
            self.page = None
        with db_session:
            page = self.db.Page.get(id=value)
            if not page:
                self.endResetModel()
                return
            self.page = make_proxy(page)
            self.count = self.page.sections.count()
        self.lastPositionChanged.emit()
        self.endResetModel()
        return True

    ################## Property ########################

    lastPositionChanged = Signal()

    @Property(int, notify=lastPositionChanged)
    def lastPosition(self):
        with db_session:
            return self.page.lastPosition

    @lastPosition.setter
    def lastPosition_set(self, value: int):
        with db_session:
            self.page.lastPosition = value
        self.lastPositionChanged.emit()
