import typing

from PyQt5.QtCore import (
    pyqtSignal,
    pyqtProperty,
    QObject,
    QModelIndex,
    QByteArray,
    pyqtSlot,
    QTimer,
)

from loguru import logger
from mycartable.defaults.roles import SectionRole
from pony.orm import db_session
from .convert import Converter
from .matiere import Matiere
from mycartable.utils import shift_list
from mycartable.types.bridge import Bridge
from mycartable.types.collections import DtbListModel
from . import Section
from . import BasePageCommand


class Page(Bridge):

    entity_name = "Page"
    UPDATE_MODIFIED_DELAY = 10000
    lastPositionChanged = pyqtSignal()
    titreChanged = pyqtSignal()
    pageModified = pyqtSignal()

    """
    Python Code
    """

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
        self._model = PageModel(parent=self)
        QTimer.singleShot(self.UPDATE_MODIFIED_DELAY, self.update_modified_if_viewed)

    def update_modified_if_viewed(self):
        if res := self._dtb.execDB("Page", self.id, "update_modified"):
            self._data["modified"] = res.isoformat()
            self.pageModified.emit()

    def get_section(self, idx: int) -> Section:
        return self.model.data(self.model.index(idx, 0), SectionRole)

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
            self._matiere = Matiere(
                self._dtb.getDB("Matiere", self.matiereId), parent=self
            )
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
        self.undoStack.push(
            AddSectionCommand(
                page=self, classtype=classtype, position=position, **params
            )
        )
        return True

    @pyqtSlot(int)
    def removeSection(self, row: int) -> bool:
        if row < self.model.count:
            self.undoStack.push(RemoveSectionCommand(page=self, position=row))
        else:
            logger.error(
                f"Pas de section à la position {row} (nb sections: {self.model.count})"
            )

    @pyqtSlot()
    def exportToPDF(self):
        Converter(self).export_to_pdf()

    @pyqtSlot()
    def exportToODT(self):
        Converter(self).export_to_odt()

    @pyqtSlot(int, result=Section)
    def getSection(self, idx: int):
        return self.get_section(idx)


class PageModel(DtbListModel):
    countChanged = pyqtSignal()

    def __init__(self, **kwargs):
        self._data = {}
        super().__init__(**kwargs)

    def _roleNames(self) -> typing.Dict:
        return {SectionRole: QByteArray(b"section")}

    def _reset(self):
        self._data = self._dtb.getDB("Page", self.parent().id)
        self._sections = [
            Section.get(sec_id, parent=self.parent(), undoStack=self.parent().undoStack)
            for sec_id in self._data["sections"]
        ]
        del self._data["sections"]  # par sécurité

    @db_session
    def _insertRows(self, row, count):
        self.page.lastPosition = min(row, self.count - 1)
        for sec in self._sections[row + count + 1 :]:
            sec.position += 1

    def insertSection(self, sections: typing.List[Section], position: int):
        self._sections = (
            self._sections[:position] + sections + self._sections[position:]
        )
        self.insertRows(position, len(sections) - 1)

    def _moveRows(self, sourceRow, count, destinationChild):
        sections = shift_list(self._sections, sourceRow, 1 + count, destinationChild)
        with db_session:
            for n, sec in enumerate(sections):
                sec._dtb.setDB(
                    "Section",
                    sec.id,
                    {
                        "_position": n,
                    },
                )
                sec.position = n
        self._sections = list(sections)
        self.page.lastPosition = (
            destinationChild
            if destinationChild < sourceRow
            else max(destinationChild - 1 + count, 0)
        )

    def _removeRows(self, row: int, count: int):
        for sec in self._sections[row + count :]:
            sec.position -= 1
        to_delete = self._sections[row : row + count + 1]
        self._sections = self._sections[:row] + self._sections[row + count + 1 :]
        for sec in to_delete:
            sec.delete()
        self.page.lastPosition = min(row, self.count - 1)

    def data(self, index: QModelIndex, role: int) -> Section:
        if not index.isValid():
            return None
        elif role == SectionRole:
            res = self._sections[index.row()]
            return res

        else:
            return None

    def rowCount(self, parent):
        return len(self._sections)

    """
    Pyqt Property
    """

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


class AddSectionCommand(BasePageCommand):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nb: int = 0  # nombre de section ajoutées

    formulations = {
        "TextSection": "Insérer un zone de texte",
        "EquationSection": "Insérer une zone d'équation",
        "AdditionSection": "Insérer une addition",
        "MultiplicationSection": "Insérer une multiplication",
        "SoustractionSection": "Insérer une soustraction",
        "DivisionSection": "Insérer une division",
        "TableauSection": "Insérer une tableau",
        "FriseSection": "Insérer une frise",
        "ImageSection": "Insérer une image",
    }

    def redo(self) -> None:
        position = self.params.get("position", None)
        if position is None:
            position = self.page.model.rowCount(QModelIndex())
        self.params["position"] = position
        self.setText(self.formulations.get(self.params["classtype"], ""))
        new_secs = Section.new_sub(
            page=self.page.id,
            parent=self.page,
            undoStack=self.page.undoStack,
            **self.params,
        )
        new_secs = [new_secs] if not isinstance(new_secs, list) else new_secs
        new_secs = list(filter(lambda x: x is not None, new_secs))  # on enleve les None
        nb = len(new_secs) - 1
        if nb >= 0:
            self.nb = nb
            self.position = position
            self.page.model.insertSection(new_secs, position)

    def undo(self) -> None:
        self.page.model.removeRows(
            self.position, self.nb
        )  # removeRows enleve 1 de base déjà enlevé avant


class RemoveSectionCommand(BasePageCommand):

    formulations = {
        "TextSection": "Supprimer un zone de texte",
        "EquationSection": "Supprimer une zone d'équation",
        "AdditionSection": "Supprimer une addition",
        "MultiplicationSection": "Supprimer une multiplication",
        "SoustractionSection": "Supprimer une soustraction",
        "DivisionSection": "Supprimer une division",
        "TableauSection": "Supprimer une tableau",
        "FriseSection": "Supprimer une frise",
        "ImageSection": "Supprimer une image",
    }

    def __init__(self, *, position: int, **kwargs):
        super().__init__(**kwargs)
        self.position = position
        section = self.page.get_section(position)
        self.setText(self.formulations.get(section.entity_name))

    def redo(self) -> None:
        section = self.page.get_section(self.position)
        if not section:
            return
        self.params = section.backup()
        self.page.model.removeRow(self.position)

    def undo(self) -> None:
        new_sec = Section.restore(parent=self.page, params=self.params)
        self.page.model.insertSection([new_sec], self.position)
