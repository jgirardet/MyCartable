from PySide2.QtCore import (
    Qt,
    Slot,
    QModelIndex,
    QByteArray,
    Signal,
    Property,
)
from PySide2.QtGui import QColor
import typing

from package.page.basemodel import SectionDetailModel
from package.utils import WDict, shift_list
from pony.orm import db_session


class FriseModel(SectionDetailModel):

    RatioRole = Qt.UserRole + 1
    SeparatorPositionRole = Qt.UserRole + 2
    SeparatorTextRole = Qt.UserRole + 3
    LegendesRole = Qt.UserRole + 4
    ZoneIdRole = Qt.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.zones = []
        self._sectionItem = {}

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

    def _insertRows(self, row: int, count):
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

        self._reset()  # changemnt de position des zones donc plus logiq de tout reprendre

    def _moveRows(self, sourceRow, count, destinationChild):
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
        self._reset()

    def _removeRows(self, row: int, count: int):
        for d in self.zones[row : row + count + 1]:
            self.dao.delDB("ZoneFrise", d["id"])
        self._reset()

    @Slot(result=bool)
    def reset(self):
        self.beginResetModel()
        self._reset()
        self.endResetModel()
        self.titreChanged.emit()
        self.heightChanged.emit()
        return True

    def _reset(self):
        self._sectionItem = self.dao.loadSection(self.sectionId)
        self.zones = [WDict(z) for z in self._sectionItem["zones"]]

    def _after_reset(self):
        self.titreChanged.emit()
        self.heightChanged.emit()

    # Properties

    heightChanged = Signal()

    @Property(int, notify=heightChanged)
    def height(self):
        return self._sectionItem.get("height", 0)

    @height.setter
    def height_set(self, value: int):
        self._height = value
        self.heightChanged.emit()

    titreChanged = Signal()

    @Property(str, notify=titreChanged)
    def titre(self):
        return self._sectionItem.get("titre", "")

    @titre.setter
    def titre_set(self, value: int):
        if self.dao.setDB("FriseSection", self.sectionId, {"titre": value}):
            self._sectionItem["titre"] = value
            self.titreChanged.emit()
