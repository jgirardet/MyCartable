import PySide2
from PySide2.QtCore import QAbstractListModel, Qt, Slot
from mimesis import typing
from pony.orm import db_session
from package.database import db
import logging
LOG = logging.getLogger("__name__")

class BaseListModel(QAbstractListModel):
    db = None
    DeleteRole = Qt.UserRole + 1
    AddRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        self._datas = None
        super().__init__(parent=parent)

    def populate(self):
        raise NotImplementedError() # pragma: no cover_all

    @db_session
    def update_datas(self):
        self._datas = None
        self.populate()
        if self._datas is None:
            self._datas = [d.to_dict() for d in self.db.select()]

    def rowCount(self, parent: PySide2.QtCore.QModelIndex) -> int:
        if self._datas is None:
            self.update_datas()
        return len(self._datas)

    def data(self, index: PySide2.QtCore.QModelIndex, role: int) -> typing.Any:
        if not index.isValid():
            return None
        elif role == Qt.DisplayRole:
            return self._datas[index.row()]
        else:
            return None


# class PageModel(BaseListModel):
#
#     db = db.Page
#
#     def populate(self):
#         pass


class RecentsModel(BaseListModel):

    db = db.Page

    def populate(self):
        self._datas = self.db.recents()

    @Slot()
    def modelReset(self):
        self.beginResetModel()
        self._datas = None
        self.endResetModel()
        LOG.info("recents model reloading")

