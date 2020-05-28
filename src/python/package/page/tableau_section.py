import json

from PySide2.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    Signal,
    Property,
    QByteArray,
)
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QApplication
from package.database import db

from pony.orm import db_session, make_proxy, ObjectNotFound
import logging

LOG = logging.getLogger(__name__)


class TableauModel(QAbstractTableModel):
    sectionIdChanged = Signal()

    ddb = None

    UnderlineRole = Qt.UserRole + 1
    PointSizeRole = Qt.UserRole + 2

    def __init__(self):
        super().__init__()
        self.db = db
        # self.params = {"rows": 0, "columns": 0, "datas": []}
        self._sectionId = None
        self._rows = 0
        self._columns = 0
        self.sectionIdChanged.connect(self.load_proxy)
        app = QApplication.instance()
        self.dataChanged.connect(app.dao.updateRecentsAndActivites)

    @db_session
    def load_proxy(self):
        # c'est une post init method
        try:
            self.proxy = make_proxy(self.db.Section.get(id=self.sectionId))
        except AttributeError as err:
            LOG.debug(err)
            self._sectionId = None
            return
            # self.proxy.debug()
        self._rows = self.proxy.lignes
        self._columns = self.proxy.colonnes
        self._init_datas()

    def _init_datas(self):
        self._datas = []
        for i in range(self.rowCount()):
            cells = [x.to_dict() for x in self.proxy.get_cells_par_ligne(i)]
            self._datas.append(cells)

    def rowCount(self, parent=QModelIndex()) -> int:
        return self._rows

    def columnCount(self, parent=QModelIndex()) -> int:
        return self._columns

    def roleNames(self):
        default = super().roleNames()
        default[Qt.BackgroundRole] = QByteArray(b"background")
        default[Qt.ForegroundRole] = QByteArray(b"foreground")
        default[self.UnderlineRole] = QByteArray(b"underline")
        default[self.PointSizeRole] = QByteArray(b"pointSize")
        return default

    # @db_session
    def data(self, index, role):
        # if not index.isValid():
        #     return
        row = self._datas[index.row()]
        # if not row:
        #     print("index, not cell", index)
        #     return
        # elif role == Qt.DisplayRole:

        return row  # ["texte"]  # + str(index.row()) + " " + str(index.column())

        # elif role == Qt.BackgroundRole:
        #     return (
        #         QColor("white")
        #         if cell["style"]["bgColor"] == "transparent"
        #         else cell["style"]["bgColor"]
        #     )
        # elif role == Qt.ForegroundRole:
        #     return cell["style"]["fgColor"]
        # elif role == self.UnderlineRole:
        #     return cell["style"]["underline"]
        # elif role == self.PointSizeRole:
        #     return cell["style"]["pointSize"] if cell["style"]["pointSize"] else 12

    @db_session
    def setData(self, index, value, role) -> bool:
        if not index.isValid():
            return False

        cell = self._datas(index.row(), index.column())

        updated = False
        if not cell:
            return False
        old = self.data(index, role)
        if old == value:
            return False

        if role == Qt.EditRole:
            # print("write", cell.to_dict(), index, value)
            cell["texte"] = value
            updated = True
        elif role == Qt.BackgroundRole:
            cell["style"]["bgColor"] = value
            updated = True
        elif role == Qt.ForegroundRole:
            cell["style"]["fgColor"] = value
            updated = True
        elif role == self.UnderlineRole:
            cell["style"]["underline"] = value
            updated = True
        elif role == self.PointSizeRole:
            cell["style"]["pointSize"] = value
            updated = True

        if updated:
            db.TableauCell[self.sectionId, index.row(), index.column()].set(**cell)
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

    #
    # def get_cell(self, index):
    #     # testé dans content et setData
    #     try:
    #         return self.db.TableauCell[self.sectionId, index.row(), index.column()]
    #     except ObjectNotFound:
    #         LOG.debug(
    #             f"TableauCell[{self.sectionId}, {index.row}, {index.column} not found"
    #         )
