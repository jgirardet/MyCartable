import typing

from PyQt5 import sip
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtProperty,
    QObject,
    QModelIndex,
    QByteArray,
    Qt,
    pyqtSlot,
    QTimer,
)

from .commands import AddSectionCommand

from pony.orm import db_session

from .convert import Converter
from .matiere import Matiere
from .sections import Section
from mycartable.utils import shift_list
from mycartable.types.bridge import Bridge
from mycartable.types.collections import DtbListModel


class Page(Bridge):

    entity_name = "Page"
    UPDATE_MODIFIED_DELAY = 10000
    lastPositionChanged = pyqtSignal()
    titreChanged = pyqtSignal()
    pageModified = pyqtSignal()

    """
    Python Code
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = PageModel(parent=self)
        QTimer.singleShot(self.UPDATE_MODIFIED_DELAY, self.update_modified_if_viewed)

    def update_modified_if_viewed(self):
        if res := self._dtb.execDB("Page", self.id, "update_modified"):
            self._data["modified"] = res.isoformat()
            self.pageModified.emit()

    """
    Qt pyqtProperty
    """

    @pyqtProperty(str, constant=True)
    def activite(self):
        return self._data.get("activite", "")

    @pyqtProperty(QObject, constant=True)
    def classeur(self):
        return self.parent()

    @pyqtProperty(str, notify=titreChanged)
    def titre(self) -> str:
        return self._data.get("titre", "")

    @titre.setter
    def titre(self, value):
        self.set_field("titre", value)

    @pyqtProperty(int, notify=lastPositionChanged)
    def lastPosition(self) -> int:
        res = self._data.get("lastPosition", 0)
        return res if res else 0

    @lastPosition.setter
    def lastPosition(self, value):
        self.set_field("lastPosition", value)

    @pyqtProperty(str, constant=True)
    def matiereId(self) -> str:
        return self._data.get("matiere", "")

    @pyqtProperty(QObject, constant=True)
    def matiere(self) -> str:
        if not hasattr("self", "_matiere"):
            self._matiere = Matiere(self._dtb.getDB("Matiere", self.matiereId))
        return self._matiere

    @pyqtProperty(QObject, constant=True)
    def model(self) -> "PageModel":
        return self._model

    """
    Qt pyqtSlots
    """

    @pyqtSlot(str, int, "QVariantMap", result=bool)
    @pyqtSlot(str, result=bool)
    def addSection(
        self, classtype: str, position: int = None, params: dict = {}
    ) -> bool:
        self.classeur.undoStack.push(
            AddSectionCommand(self, classtype=classtype, position=position, **params)
        )
        return True

    @pyqtSlot()
    def exportToPDF(self):
        Converter(self).export_to_pdf()

    @pyqtSlot()
    def exportToODT(self):
        Converter(self).export_to_odt()


class PageModel(DtbListModel):
    SectionRole = Qt.UserRole + 1
    countChanged = pyqtSignal()

    def __init__(self, **kwargs):
        self._data = {}
        super().__init__(**kwargs)

    def _roleNames(self) -> typing.Dict:
        return {self.SectionRole: QByteArray(b"section")}

    def _reset(self):
        self._data = self._dtb.getDB("Page", self.parent().id)

    @db_session
    def _insertRows(self, row, count):
        self._reset()
        self.page.lastPosition = min(row, self.count - 1)

    def _moveRows(self, sourceRow, count, destinationChild):
        sections = shift_list(
            self._data["sections"], sourceRow, 1 + count, destinationChild
        )
        with db_session:
            for n, sec in enumerate(sections):
                item = self._dtb.setDB(
                    "Section",
                    sec,
                    {
                        "_position": n,
                    },
                )
        self._data["sections"] = sections
        self.page.lastPosition = (
            destinationChild
            if destinationChild < sourceRow
            else max(destinationChild - 1 + count, 0)
        )

    def _removeRows(self, row: int, count: int):
        for sec in self._data["sections"][row : row + count + 1]:
            self._dtb.delDB("Section", sec)
        self._reset()
        self.page.lastPosition = min(row, self.count - 1)

    def data(self, index: QModelIndex, role: int) -> Section:
        if not index.isValid():
            return None
        elif role == self.SectionRole:
            sec_id = self._data["sections"][index.row()]
            sec = Section.get(sec_id)
            sip.transferto(sec, sec)
            return sec

        else:
            return None

    def rowCount(self, parent):
        return len(self._data["sections"])

    @pyqtProperty(Page, constant=True)
    def page(self) -> Page:
        return self.parent()

    @pyqtProperty(int, notify=countChanged)
    def count(self) -> int:
        return self.rowCount(QModelIndex())

    @pyqtSlot(result=bool)
    def append(self) -> bool:
        """pyqtSlot to append a row at the end"""
        raise NotImplementedError("please use page addSection instead")
