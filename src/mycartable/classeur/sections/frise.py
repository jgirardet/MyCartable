from PyQt5.QtCore import (
    Qt,
    pyqtSlot,
    QModelIndex,
    QByteArray,
    pyqtSignal,
    pyqtProperty,
    QObject,
)
from PyQt5.QtGui import QColor
import typing

from .section import Section
from mycartable.types import DtbListModel
from mycartable.utils import WDict, shift_list


class FriseSection(Section):
    entity_name = "FriseSection"

    heightChanged = pyqtSignal()
    titreChanged = pyqtSignal()

    def __init__(self, data: dict = {}, parent=None, **kwargs):
        super().__init__(data=data, parent=parent, **kwargs)
        self._model = FriseModel(self)

    @pyqtProperty(int, notify=heightChanged)
    def height(self):
        return self._data["height"]

    @height.setter
    def height(self, value: int):
        self.set_field("height", value)
        self.heightChanged.emit()

    @pyqtProperty(str, notify=titreChanged)
    def titre(self):
        return self._data["titre"]

    @titre.setter
    def titre(self, value: str):
        self.set_field("titre", value)
        self.titreChanged.emit()

    @pyqtProperty(QObject, constant=True)
    def model(self):
        return self._model


class FriseModel(DtbListModel):

    RatioRole = Qt.UserRole + 1
    SeparatorPositionRole = Qt.UserRole + 2
    SeparatorTextRole = Qt.UserRole + 3
    LegendesRole = Qt.UserRole + 4
    ZoneIdRole = Qt.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.zones = []
        self.reset()

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
        if self._dtb.setDB("ZoneFrise", zone["id"], data):
            zone.update(data)
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def _insertRows(self, row: int, count):
        # start datanase work
        for pos in range(row, row + count + 1):
            item = self._dtb.addDB(
                "ZoneFrise",
                {
                    "frise": self.parent().id,
                    "texte": "new",
                    "ratio": 0.2,
                    "style": {"bgColor": QColor("lightgoldenrodyellow")},
                    "position": pos,
                },
            )
            self._dtb.addDB(
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
        for n, zo in enumerate(self.zones):
            item = self._dtb.setDB(
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
            self._dtb.delDB("ZoneFrise", d["id"])
        self._reset()

    @pyqtSlot(result=bool)
    def reset(self):
        self.beginResetModel()
        self._reset()
        self.endResetModel()
        self._after_reset()
        return True

    def _reset(self):
        self.parent()._data = self._dtb.getDB("FriseSection", self.parent().id)
        self.zones = [WDict(z) for z in self.parent()._data["zones"]]

    def _after_reset(self):
        self.parent().titreChanged.emit()
        self.parent().heightChanged.emit()
