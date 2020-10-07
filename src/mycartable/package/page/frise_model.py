from PySide2.QtCore import (
    QAbstractListModel,
    Qt,
    Slot,
    QModelIndex,
    QByteArray,
    Signal,
    Property,
    QObject,
)
from PySide2.QtGui import QColor
import typing

from package.utils import WDict, shift_list
from pony.orm import db_session


class FriseModel(QAbstractListModel):

    RatioRole = Qt.UserRole + 1
    SeparatorPositionRole = Qt.UserRole + 2
    SeparatorTextRole = Qt.UserRole + 3
    LegendesRole = Qt.UserRole + 4
    ZoneIdRole = Qt.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.zones = []
        self._sectionId = ""
        self._sectionItem = {}
        self.dao: "DatabaseObject" = None
        self.sectionIdChanged.connect(lambda: self.reset())

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.zones)

    def roleNames(self) -> typing.Dict:
        default = super().roleNames()
        default[self.RatioRole] = QByteArray(b"ratio")
        default[Qt.BackgroundRole] = QByteArray(b"backgroundColor")
        default[self.SeparatorPositionRole] = QByteArray(b"separatorPosition")
        default[self.SeparatorTextRole] = QByteArray(b"separatorText")
        default[self.LegendesRole] = QByteArray(b"legendes")
        default[self.ZoneIdRole] = QByteArray(b"zoneId")
        return default

    def data(self, index, role: int) -> typing.Any:
        if not self.rowCount() or not index.isValid():
            return None
        row = self.zones[index.row()]
        if role == Qt.DisplayRole:
            return row["texte"]
        elif role == Qt.BackgroundRole:
            return row["style"]["bgColor"]
        elif role == self.RatioRole:
            return row["ratio"]
        elif role == self.SeparatorPositionRole:
            return row["style"]["strikeout"]
        elif role == self.SeparatorTextRole:
            return row["separatorText"]
        elif role == self.LegendesRole:
            return row["legendes"]
        elif role == self.ZoneIdRole:
            return row["id"]
        else:
            return None

    ROLES = {
        Qt.EditRole: "texte",
        RatioRole: "ratio",
        Qt.BackgroundRole: "style.bgColor",
        SeparatorPositionRole: "style.strikeout",
        SeparatorTextRole: "separatorText",
    }

    def setData(self, index, value, role) -> bool:
        if not index.isValid() or role not in self.ROLES:
            return False
        zone: dict = self.zones[index.row()]
        data = WDict(self.ROLES[role], value)
        if self.dao.setDB("ZoneFrise", zone["id"], data):
            zone.update(data)
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    @Slot(result=bool)
    def append(self) -> bool:
        """Slot to append a row at the end"""
        return self.insertRow(self.rowCount())

    def insertRow(self, row) -> bool:
        """Insert a single row at row"""
        return self.insertRows(row, 0)

    def insertRows(self, row: int, count, index=QModelIndex()) -> bool:
        """Insert n rows (n = 1 + count)  at row"""

        self.beginInsertRows(QModelIndex(), row, row + count)

        # start datanase work
        with db_session:
            for pos in range(row, row + count + 1):
                item = self.dao.addDB(
                    "ZoneFrise",
                    {
                        "frise": self.sectionId,
                        "texte": "new",
                        "ratio": 0.2,
                        "style": {"bgColor": QColor("lightgoldenrodyellow")},
                        "position": pos,
                    },
                )
                self.dao.addDB(
                    "FriseLegende",
                    {
                        "zone": item["id"],
                        "texte": "",
                        "relativeX": 1,
                        "side": False,
                    },
                )
                if not item:
                    break

        self.resetInternalData()  # changemnt de position des zones donc plus logiq de tout reprendre
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
        self.zones = shift_list(self.zones, sourceRow, 1 + count, destinationChild)
        with db_session:
            for n, zo in enumerate(self.zones):
                item = self.dao.setDB(
                    "ZoneFrise",
                    zo["id"],
                    {
                        "_position": n,
                    },
                )
                if not item:
                    break
        self.resetInternalData()

        self.endMoveRows()
        return True

    @Slot(int, result=bool)
    def remove(self, row: int):
        """Slot to remove one row"""
        return self.removeRow(row)

    def removeRow(self, row, parent=QModelIndex()) -> bool:
        """Remove one row at index row"""
        return self.removeRows(row, 0, parent)

    def removeRows(self, row: int, count: int, parent=QModelIndex()) -> bool:
        """Remove n rows (n=1+count) starting at row"""
        self.beginRemoveRows(QModelIndex(), row, row + count)

        # start database work
        for d in self.zones[row : row + count + 1]:
            self.dao.delDB("ZoneFrise", d["id"])
        self.resetInternalData()
        # end database work

        self.endRemoveRows()
        return True

    @Slot(result=bool)
    def reset(self):
        self.beginResetModel()
        self.resetInternalData()
        self.endResetModel()
        self.titreChanged.emit()
        self.heightChanged.emit()
        return True

    def resetInternalData(self):
        self._sectionItem = self.dao.loadSection(self.sectionId)
        self.zones = [WDict(z) for z in self._sectionItem["zones"]]

    daoChanged = Signal()

    @Property(QObject, notify=daoChanged)
    def dao(self):
        return self._dao

    @dao.setter
    def dao_set(self, value: int):
        self._dao = value
        self.daoChanged.emit()

    heightChanged = Signal()

    @Property(int, notify=heightChanged)
    def height(self):
        return self._sectionItem.get("height", 0)

    @height.setter
    def height_set(self, value: int):
        self._height = value
        self.heightChanged.emit()

    sectionIdChanged = Signal()

    @Property(str, notify=sectionIdChanged)
    def sectionId(self):
        return self._sectionId

    @sectionId.setter
    def sectionId_set(self, value: str):
        if value:
            self._sectionId = value
            self.sectionIdChanged.emit()

    titreChanged = Signal()

    @Property(str, notify=titreChanged)
    def titre(self):
        return self._sectionItem.get("titre", "")

    @titre.setter
    def titre_set(self, value: int):
        if self.dao.setDB(self.sectionId, {"titre": value}):
            self._sectionItem["titre"] = value
            self.titreChanged.emit()
