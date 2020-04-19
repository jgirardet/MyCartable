import json

from PySide2.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    Signal,
    Property,
    QByteArray,
)
from descriptors import cachedproperty
from package.database import db

from pony.orm import db_session, make_proxy, ObjectNotFound
import logging

LOG = logging.getLogger(__name__)


class TableauModel(QAbstractTableModel):
    sectionIdChanged = Signal()
    ddb = None

    def __init__(self):
        super().__init__()
        self.db = db
        # self.params = {"rows": 0, "columns": 0, "datas": []}
        self._sectionId = None
        self._rows = 0
        self._columns = 0
        self.sectionIdChanged.connect(self.load_proxy)

    @db_session
    def load_proxy(self):
        # c'est une post init method
        try:
            self.proxy = make_proxy(self.db.Section.get(id=self.sectionId))
            self._rows = self.proxy.lignes
            self._columns = self.proxy.colonnes
        except AttributeError as err:
            LOG.debug(err)
            self._sectionId = None
            return

    def rowCount(self, parent=QModelIndex()) -> int:
        return self._rows

    def columnCount(self, parent=QModelIndex()) -> int:
        return self._columns

    def roleNames(self):
        default = super().roleNames()
        # print(default)
        default[Qt.BackgroundRole] = QByteArray(b"background")
        return default

    @db_session
    def data(self, index, role):
        if not index.isValid():
            return
        cell = self.get_cell(index)
        if not cell:
            return
        elif role == Qt.DisplayRole:
            return cell.texte + str(index.row()) + " " + str(index.column())

        elif role == Qt.BackgroundRole:
            # print(cell.bgColor, "cell.bgColor")
            return cell.bgColor

    @db_session
    def setData(self, index, value, role) -> bool:
        # print(index, value, role)
        if not index.isValid():
            return False

        cell = self.get_cell(index)
        updated = False
        if not cell:
            return False

        old = self.data(index, role)
        if old == value:
            return False

        if role == Qt.EditRole:
            cell.texte = value
            updated = True
        elif role == Qt.BackgroundRole:
            cell.bgColor = value
            updated = True

        if updated:
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    @Property(int, notify=sectionIdChanged)
    def sectionId(self):
        return self._sectionId

    @sectionId.setter
    def sectionId_set(self, value: int):
        self._sectionId = value
        self.sectionIdChanged.emit()

    n_rowsChanged = Signal()

    @Property(int, notify=n_rowsChanged)
    def n_rows(self):
        """créer uniquement pour un problème de conflit avec TableModel """
        return self.rowCount()

    def get_cell(self, index):
        try:
            return self.db.TableauCell[self.sectionId, index.row(), index.column()]
        except ObjectNotFound:
            LOG.debug(
                f"TableauCell[{self.sectionId}, {index.row}, {index.column} not found"
            )
