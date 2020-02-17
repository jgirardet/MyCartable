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
)
from mimesis import typing
from package.constantes import FILES
from pony.orm import db_session
from package.database import db
import logging

LOG = logging.getLogger("__name__")


class PageModel(QAbstractListModel):

    db = db
    PageRole = Qt.UserRole + 1

    itemAdded = Signal(int)

    def __init__(self, parent=None):
        self._datas = []
        self.page_id = 0
        self._lastPosition = 0
        super().__init__(parent=parent)

    def data(self, index, role: int) -> typing.Any:
        if not index.isValid():
            return None
        elif role == self.PageRole:
            return self._datas[index.row()]
        # elif role == Qt.DisplayRole:
        #     return self._datas[index.row()]
        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsDropEnabled
            # return Qt.ItemIsEnabled
        return QAbstractItemModel.flags(index) | Qt.ItemIsEditable

    def insertRow(self) -> bool:
        row = self.rowCount()
        return super().insertRow(row)

    def insertRows(self, row: int, value, index=QModelIndex()) -> bool:
        self.beginInsertRows(QModelIndex(), self.rowCount(index), self.rowCount(index))
        success = self._reload()
        self.endInsertRows()
        print(self.lastPosition, row)
        self.lastPosition = row
        print(self.lastPosition, row)
        return success

    def roleNames(self) -> typing.Dict:
        default = super().roleNames()
        default[self.PageRole] = QByteArray(b"page")
        return default

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._datas)

    def slotReset(self, value):
        self.page_id = value
        self.beginResetModel()
        self._reload()
        self.endResetModel()

    def _reload(self):
        with db_session:
            page = self.db.Page.get(id=self.page_id)
            if not page:
                return False
            self._datas = page.content_dict
            self.lastPosition = page.lastPosition
            return True

    ################## Property ########################

    lastPositionChanged = Signal()

    @Property(int, notify=lastPositionChanged)
    def lastPosition(self):
        return self._lastPosition

    @lastPosition.setter
    def lastPosition_set(self, value: int):
        self._lastPosition = value
        self.lastPositionChanged.emit()
