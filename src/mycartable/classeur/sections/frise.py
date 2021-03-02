from PyQt5.QtCore import (
    Qt,
    QModelIndex,
    QByteArray,
    pyqtSignal,
    pyqtProperty,
    QObject,
    pyqtSlot,
)
from PyQt5.QtGui import QColor
import typing

from flatten_dict import flatten, unflatten
from mycartable.types.setable import Setable

from .section import Section, SetSectionCommand, UpdateSectionCommand
from mycartable.types import DtbListModel
from mycartable.utils import WDict, shift_list


class FriseSection(Section, Setable):
    entity_name = "FriseSection"
    set_command = SetSectionCommand

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

    ROLES = {
        Qt.EditRole: "texte",
        RatioRole: "ratio",
        Qt.BackgroundRole: "style.bgColor",
    }

    ratioChanged = pyqtSignal(int, float)
    legendeAdded = pyqtSignal(int, int, "QVariantMap")
    legendeUpdated = pyqtSignal(int, int, "QVariantMap")
    legendeRemoved = pyqtSignal(int, int)

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
        elif role == self.LegendesRole:
            return row["legendes"]
        elif role == self.ZoneIdRole:
            return row["id"]
        else:
            return None

    def setData(self, index, value, role) -> bool:
        if not index.isValid() or role not in self.ROLES:
            return False
        data = WDict(self.ROLES[role], value)
        self.parent().undoStack.push(
            UpdateZoneFriseCommand(
                section=self.parent(),
                index=index.row(),
                new_data=data,
                text="frise: modifier",
            )
        )
        return True

    def set_data(self, index: int, data: dict):
        zone: dict = self.zones[index]
        if self._dtb.setDB("ZoneFrise", zone["id"], data):
            zone.update(data)
            idx: QModelIndex = self.index(index, 0)
            self.dataChanged.emit(idx, idx)
            if "ratio" in data:
                self.ratioChanged.emit(index, data["ratio"])
            return True
        else:
            return False

    def restore_row(self, **kwargs):
        self.beginInsertRows(QModelIndex(), kwargs["position"], kwargs["position"])
        self._dtb.execDB("ZoneFrise", None, "restore", **kwargs)
        self._reset()
        self.endInsertRows()

    def backup_row(self, index: int):
        zone: dict = self.zones[index]
        res = self._dtb.execDB("ZoneFrise", zone["id"], "backup")
        return res

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

    def _reset(self):
        self.parent()._data = self._dtb.getDB("FriseSection", self.parent().id)
        self.zones = [WDict(z) for z in self.parent()._data["zones"]]

    def _after_reset(self):
        self.parent().titreChanged.emit()
        self.parent().heightChanged.emit()

    """
    Qt Slot
    """

    @pyqtSlot()
    def add(self):
        self.parent().undoStack.push(
            AddZoneFriseCommand(section=self.parent(), text="frise: ajout zone")
        )

    @pyqtSlot(int, result=bool)
    def remove(self, row: int):
        self.parent().undoStack.push(
            RemoveZoneFriseCommand(
                section=self.parent(), index=row, text="frise: suppression zone"
            )
        )
        return True

    @pyqtSlot(int, int, result=bool)
    def move(self, source: int, target: int):
        """pyqtSlot to move a single row from source to target"""
        self.parent().undoStack.push(
            MoveZoneFriseCommand(
                section=self.parent(),
                source=source,
                target=target,
                text="frise: deplacer zone",
            )
        )
        return True

    @pyqtSlot(int, "QVariantMap")
    def addLegende(self, zoneIndex: int, values: dict):
        self.parent().undoStack.push(
            AddLegendFriseCommand(
                section=self.parent(),
                values=values,
                zone_index=zoneIndex,
                text="frise: ajouter legende",
            )
        )

    @pyqtSlot(int, int)
    def removeLegende(self, zoneIndex: int, legendeIndex: int):
        self.parent().undoStack.push(
            RemoveLegendFriseCommand(
                section=self.parent(),
                zone_index=zoneIndex,
                legende_index=legendeIndex,
                text="frise: supprimer legende",
            )
        )

    @pyqtSlot(int, int, "QVariantMap")
    def updateLegende(self, zoneIndex: int, legendeIndex: int, values: dict):
        self.parent().undoStack.push(
            UpdateLegendFriseCommand(
                section=self.parent(),
                values=values,
                zone_index=zoneIndex,
                legende_index=legendeIndex,
                text="frise: modifier legende",
            )
        )


class UpdateZoneFriseCommand(UpdateSectionCommand):
    def __init__(self, *, index: int, new_data: dict, **kwargs):
        super().__init__(**kwargs)
        self._new_data = new_data

        self._zone: dict = kwargs["section"].model.zones[index].copy()
        self._index = index

    def undo(self):
        model = self.get_section().model
        prev = flatten(self._zone)
        newcontent = flatten(self._new_data)
        to_update = unflatten({k: prev[k] for k in newcontent})
        model.set_data(self._index, to_update)

    def redo(self):
        model = self.get_section().model
        model.set_data(self._index, self._new_data)


class AddZoneFriseCommand(UpdateSectionCommand):
    def redo(self):
        model = self.get_section().model
        model.append()

    def undo(self):
        model = self.get_section().model
        model.removeRow(model.rowCount() - 1)


class RemoveZoneFriseCommand(UpdateSectionCommand):
    def __init__(self, *, index: int, **kwargs):
        super().__init__(**kwargs)
        self._index = index
        self.backup = kwargs["section"].model.backup_row(self._index)

    def redo(self):
        model = self.get_section().model
        model.removeRow(self._index)

    def undo(self):
        model = self.get_section().model
        model.restore_row(**self.backup)


class MoveZoneFriseCommand(UpdateSectionCommand):
    def __init__(self, *, source: int, target: int, **kwargs):
        super().__init__(**kwargs)

        self._source = source
        self._target = target
        self._id = kwargs["section"].model.zones[source]["id"]

    def redo(self):
        model = self.get_section().model

        model.moveRow(self._source, self._target)
        for n, z in enumerate(model.zones):
            if z["id"] == self._id:
                self._new_pos = n
                return

    def undo(self):
        model = self.get_section().model
        model.moveRow(self._new_pos, self._source)


class RemoveLegendFriseCommand(UpdateSectionCommand):
    def __init__(self, *, zone_index: int, legende_index: int, **kwargs):
        super().__init__(**kwargs)

        self._zone_index = zone_index
        self._legende_index = legende_index

    def redo(self):
        model = self.get_section().model
        self._legende = model.zones[self._zone_index]["legendes"].pop(
            self._legende_index
        )
        model._dtb.delDB("FriseLegende", self._legende["id"])
        model.legendeRemoved.emit(self._zone_index, self._legende_index)

    def undo(self):
        model = self.get_section().model
        res = model._dtb.addDB("FriseLegende", self._legende)
        model.zones[self._zone_index]["legendes"].insert(self._legende_index, res)
        model.legendeAdded.emit(self._zone_index, self._legende_index, res)


class RemoveLegendFriseCommand(UpdateSectionCommand):
    def __init__(self, *, zone_index: int, legende_index: int, **kwargs):
        super().__init__(**kwargs)

        self._zone_index = zone_index
        self._legende_index = legende_index

    def redo(self):
        model = self.get_section().model
        self._legende = model.zones[self._zone_index]["legendes"].pop(
            self._legende_index
        )
        model._dtb.delDB("FriseLegende", self._legende["id"])
        model.legendeRemoved.emit(self._zone_index, self._legende_index)

    def undo(self):
        model = self.get_section().model
        res = model._dtb.addDB("FriseLegende", self._legende)
        model.zones[self._zone_index]["legendes"].insert(self._legende_index, res)
        model.legendeAdded.emit(self._zone_index, self._legende_index, res)


class AddLegendFriseCommand(UpdateSectionCommand):
    def __init__(self, *, zone_index: int, values: dict, **kwargs):
        super().__init__(**kwargs)

        self._values = values
        self._zone_index = zone_index
        self._legende_index = len(
            kwargs["section"].model.zones[self._zone_index]["legendes"]
        )

    def redo(self):
        model = self.get_section().model
        res = model._dtb.addDB("FriseLegende", self._values)
        model.zones[self._zone_index]["legendes"].append(res)
        model.legendeAdded.emit(self._zone_index, self._legende_index, res)

    def undo(self):
        model = self.get_section().model
        self._legende = model.zones[self._zone_index]["legendes"].pop(
            self._legende_index
        )
        model._dtb.delDB("FriseLegende", self._legende["id"])
        model.legendeRemoved.emit(self._zone_index, self._legende_index)


class UpdateLegendFriseCommand(UpdateSectionCommand):
    def __init__(self, *, zone_index: int, legende_index: int, values: dict, **kwargs):
        super().__init__(**kwargs)

        self._values = values
        self._zone_index = zone_index
        self._legende_index = legende_index
        self.backup = (
            kwargs["section"]
            .model.zones[self._zone_index]["legendes"][self._legende_index]
            .copy()
        )

    def redo(self):
        model = self.get_section().model
        res = model._dtb.setDB("FriseLegende", self.backup["id"], self._values)
        model.zones[self._zone_index]["legendes"][self._legende_index] = res
        model.legendeUpdated.emit(self._zone_index, self._legende_index, res)

    def undo(self):
        model = self.get_section().model
        res = model._dtb.setDB("FriseLegende", self.backup["id"], self.backup)
        model.zones[self._zone_index]["legendes"][self._legende_index] = res
        model.legendeUpdated.emit(self._zone_index, self._legende_index, res)
