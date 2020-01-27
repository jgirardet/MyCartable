import PySide2
from PySide2.QtCore import QAbstractListModel, Qt, Slot, QModelIndex, QByteArray
from mimesis import typing
from pony.orm import db_session
from package.database import db
import logging

LOG = logging.getLogger("__name__")


class BaseListModel(QAbstractListModel):
    db = None
    PageRole = Qt.UserRole + 1
    DeleteRole = Qt.UserRole + 2
    AddRole = Qt.UserRole + 3

    def __init__(self, parent=None):
        self._datas = None
        super().__init__(parent=parent)

    def roleNames(self) -> typing.Dict:
        default = super().roleNames()
        default[self.PageRole] = QByteArray(b"page")
        # default[self.AddRole] = QByteArray(b'add')
        return default

    def populate(self):
        raise NotImplementedError()  # pragma: no cover_all

    @db_session
    def update_datas(self):
        self._datas = None
        self.populate()
        if self._datas is None:
            self._datas = [d.to_dict() for d in self.db.select()]

    def rowCount(self, parent=QModelIndex()) -> int:
        if self._datas is None:
            self.update_datas()
        return len(self._datas)

    def data(self, index, role: int) -> typing.Any:
        if not index.isValid():
            return None
        elif role == self.PageRole:
            return self._datas[index.row()]
        else:
            return None



class RecentsModel(BaseListModel):

    db = db.Page
    #

    def populate(self):
        self._datas = self.db.recents()

    @Slot()
    def slotResetModel(self):
        self.beginResetModel()
        self._datas = None
        self.endResetModel()
        LOG.info("recents model reloading")



class PageModel(QAbstractListModel):

    db = db
    TexteRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        self._datas = []
        super().__init__(parent=parent)


    def roleNames(self) -> typing.Dict:
        default = super().roleNames()
        default[self.TexteRole] = QByteArray(b"texte")
        default[self.TypeRole] = QByteArray(b"type")
        # default[self.AddRole] = QByteArray(b'add')
        return default

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._datas)

    def data(self, index , role:int) -> typing.Any:
        if not index.isValid():
            return None
        #
        elif role == Qt.DisplayRole:
            a =  self._datas[index.row()]
            if a['id'] % 2:
                a['type']="texte"
            else:
                a['type']="image"
            return a

    def slotReset(self, value):
        self.beginResetModel()
        with db_session:
            page = self.db.Page.get(id=value)
            if not page:
                return

            self._datas = page.content
            print("datas", self._datas)
        self.endResetModel()
[]
