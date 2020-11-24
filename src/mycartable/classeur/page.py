import typing
from PySide2.QtCore import Signal, Property, QObject, QModelIndex, QByteArray, Qt, Slot
from mycartable.package.utils import shift_list

from .sections import SectionFactory, Section
from mycartable.types.bridge import Bridge
from mycartable.types.listmodel import DtbListModel
from pony.orm import db_session


class Page(Bridge):
    """
    prop
        pagemodel
        currentPage/set -> classeur
        # currentTitre/set
    fn
        newPage -> classeur
        removePage -> classeur
        # setCurrentTitre : ok
        exportpdf
        eportodt

    """

    entity_name = "Page"
    pageSignal = Signal()
    titreSignal = Signal()
    lastPositionSignal = Signal()
    matiereChanged = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = PageModel(parent=self)

    """
    Python Code
    """

    """
    Qt Property
    """

    @Property(QObject, notify=pageSignal)
    def classeur(self):
        return self.parent()

    @Property(str, notify=pageSignal)
    def titre(self) -> str:
        return self._data.get("titre", "")

    @titre.setter
    def setTitre(self, value):
        self._set_field("titre", value)
        self.titreSignal.emit()

    @Property(int, notify=lastPositionSignal)
    def lastPosition(self) -> int:
        return self._data.get("lastPosition", 0)

    @lastPosition.setter
    def setLastPosition(self, value):
        print("setlast", value)
        self._set_field("lastPosition", value)
        self.lastPositionSignal.emit()

    @Property(str, notify=pageSignal)
    def matiereId(self) -> str:
        return self._data.get("matiere", "")

    @Property(QObject, notify=pageSignal)
    def model(self) -> "PageModel":
        # print(self._model.data(QModelIndex(0, 0), PageModel.PageRole))
        return self._model

    """
    Qt Slots
    """

    @Slot(str, int, "QVariantMap", result=bool)
    @Slot(str, result=bool)
    def addSection(
        self, classtype: str, position: int = None, params: dict = {}
    ) -> bool:
        return self.model.addSection(classtype, position, params)


class PageModel(DtbListModel):
    SectionRole = Qt.UserRole + 1
    pageSignal = Signal()
    countChanged = Signal()

    def __init__(self, parent=None):
        self._data = {}
        super().__init__(parent)

    def _roleNames(self) -> typing.Dict:
        return {self.SectionRole: QByteArray(b"section")}

    def _reset(self):
        self._data = self.dtb.getDB("Page", self.parent().id)

    @db_session
    def _insertRows(self, row, count):
        self._reset()

    def _moveRows(self, sourceRow, count, destinationChild):
        sections = shift_list(
            self._data["sections"], sourceRow, 1 + count, destinationChild
        )
        with db_session:
            for n, sec in enumerate(sections):
                item = self.dtb.setDB(
                    "Section",
                    sec,
                    {
                        "_position": n,
                    },
                )
                if not item:
                    break
        self._data["sections"] = sections

    def _removeRows(self, row: int, count: int):
        for sec in self._data["sections"][row : row + count + 1]:
            self.dtb.delDB("Section", sec)
        self._reset()

    def data(self, index: QModelIndex, role: int) -> Section:
        if not index.isValid():
            return None
        elif role == self.SectionRole:
            sec_id = self._data["sections"][index.row()]
            return SectionFactory.get(sec_id)
        else:
            return None

    def rowCount(self, parent):
        return len(self._data["sections"])

    def addSection(
        self, classtype: str, position: int = None, params: dict = {}
    ) -> bool:
        """Add a section of type `classtype` at position `position`
        to page `page_id` width params `params`"""
        if position is None:
            position = self.rowCount(QModelIndex())
        params["position"] = position
        SectionFactory.new(self.page.id, classtype, **params)
        return self.insertRow(position)

    @Property(Page, notify=pageSignal)
    def page(self):
        return self.parent()

    @Property(int, notify=countChanged)
    def count(self):
        return self.rowCount(QModelIndex())

    @Slot(result=bool)
    def append(self) -> bool:
        """Slot to append a row at the end"""
        raise NotImplementedError("please use page addSection instead")
