import typing
from PySide2.QtCore import Signal, Property, QObject, QModelIndex, QByteArray, Qt, Slot
from pony.orm import db_session

from .matiere import Matiere
from .sections import Section, ImageSection
from mycartable.package.utils import shift_list
from mycartable.types.bridge import Bridge
from mycartable.types.listmodel import DtbListModel


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
    lastPositionChanged = Signal()
    titreChanged = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = PageModel(parent=self)

    """
    Python Code
    """

    """
    Qt Property
    """

    @Property(QObject, constant=True)
    def classeur(self):
        return self.parent()

    @Property(str, notify=titreChanged)
    def titre(self) -> str:
        return self._data.get("titre", "")

    @titre.setter
    def setTitre(self, value):
        self.set_field("titre", value)

    @Property(int, notify=lastPositionChanged)
    def lastPosition(self) -> int:
        return self._data.get("lastPosition", 0)

    @lastPosition.setter
    def setLastPosition(self, value):
        self.set_field("lastPosition", value)

    @Property(str, constant=True)
    def matiereId(self) -> str:
        return self._data.get("matiere", "")

    @Property(QObject, constant=True)
    def matiere(self) -> str:
        if not hasattr("self", "_matiere"):
            self._matiere = Matiere(self._dtb.getDB("Matiere", self.matiereId))
        return self._matiere

    @Property(QObject, constant=True)
    def model(self) -> "PageModel":
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
    countChanged = Signal()

    def __init__(self, parent=None):
        self._data = {}
        super().__init__(parent)

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
            return Section.get(sec_id)
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
        Section.new_sub(page=self.page.id, classtype=classtype, **params)
        return self.insertRow(position)

    @Property(Page, constant=True)
    def page(self) -> Page:
        return self.parent()

    @Property(int, notify=countChanged)
    def count(self) -> int:
        return self.rowCount(QModelIndex())

    @Slot(result=bool)
    def append(self) -> bool:
        """Slot to append a row at the end"""
        raise NotImplementedError("please use page addSection instead")
