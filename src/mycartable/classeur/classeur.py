from typing import Union, Optional
from uuid import UUID

from mycartable.types import DTB

from pony.orm import db_session, ObjectNotFound

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, pyqtProperty, QTimer
from loguru import logger

from .pagelist_model import RecentsModel
from .matiere import MatieresDispatcher, Matiere
from . import Page


class Classeur(DTB):

    # db: Database

    anneeChanged = pyqtSignal()
    recentsChanged = pyqtSignal()
    currentMatiereChanged = pyqtSignal()
    pageChanged = pyqtSignal()

    """
    Pure python
    """

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.reset()
        self.setup_connections()

    def reset(self):
        self._annee = 0
        self._matieresDispatcher: MatieresDispatcher = None
        self._currentMatiere: Matiere = None
        self._page: Page = None
        self._recents: RecentsModel = None
        self.newPage_timer = None

    def setup_connections(self):
        self.anneeChanged.connect(self.recentsChanged)

    """
    Qt Properties
    """

    @pyqtProperty(int, notify=anneeChanged)
    def annee(self):
        return self._annee

    @annee.setter
    def annee(self, annee: int):
        self.reset()
        if annee:
            self._annee = annee
            self._matieresDispatcher = MatieresDispatcher(self.db, annee)
            self._recents = RecentsModel(self._annee, parent=self)
            logger.info(f"Année en cours : {annee}")
            self.anneeChanged.emit()

    @pyqtProperty(QObject, notify=currentMatiereChanged)
    def currentMatiere(self):
        return self._currentMatiere

    @currentMatiere.setter
    def currentMatiere(self, value):
        # breakpoint()

        if isinstance(value, UUID):
            value = str(value)
        # ignore same
        if self._currentMatiere and self.currentMatiere.id == value:
            return
        with db_session:
            try:
                self._currentMatiere = Matiere(
                    self.db.Matiere[value].to_dict(), parent=self
                )
            except ObjectNotFound as res:
                logger.error(res)
                return
        logger.info(f"current matiere set to: {self._currentMatiere}")
        self.currentMatiereChanged.emit()

    @pyqtProperty(int, notify=currentMatiereChanged)
    def currentMatiereIndex(self):
        if self.currentMatiere:
            return self.matieresDispatcher.indexFromId(self.currentMatiere.id)
        else:
            return 0

    @pyqtProperty(QObject, notify=anneeChanged)
    def matieresDispatcher(self):
        return self._matieresDispatcher

    @pyqtProperty(QObject, notify=pageChanged)
    def page(self):
        return self._page

    @pyqtProperty(QObject, notify=recentsChanged)
    def recents(self):
        return self._recents

    """
    Qt pyqtSlots
    """

    @pyqtSlot()
    def deletePage(self):
        old = self.page.id
        self.page.delete()
        self._page = None
        self.pageChanged.emit()
        self.onDeletePage(old)

    @pyqtSlot(str)
    def newPage(self, activiteId: str) -> Optional[dict]:
        new_item = Page.new(parent=self, activite=activiteId)
        logger.debug(f'New Page "{new_item.id}" created')
        self.setPage(new_item)
        QTimer.singleShot(0, lambda: self.onNewPage(activiteId))

    @pyqtSlot(str)
    @pyqtSlot(int)
    def setCurrentMatiere(self, value: Union[int, str]) -> None:
        if isinstance(value, int):
            value = self.matieresDispatcher.idFromIndex(value)
        self.currentMatiere = value

    @pyqtSlot(str)
    @pyqtSlot(Page)
    def setPage(self, value: Union[str, Page]):
        new_page = value if isinstance(value, Page) else Page.get(value, parent=self)
        if self._page:
            self._page.setParent(None)
        self._page = new_page
        self.pageChanged.emit()
        logger.info(f"CurrentPage changed to {self.page.titre}")
        self.setCurrentMatiere(self.page.matiereId)
        self.page.titreChanged.connect(self.onPageTitreChanged)
        self.page.pageModified.connect(self.onPageModified)

    @pyqtSlot(str, str)
    def movePage(self, page: str, activite: str):

        res = self.setDB("Page", page, {"activite": activite})
        if res:
            self.onMovePage()

    """
    Callback de liaisons
    """

    def onPageTitreChanged(self):
        def wrapped():
            self.recents.update_titre(self.page)
            for ac in self.currentMatiere.activites:
                if ac.id == self.page.activite:
                    ac.pages.update_titre(self.page)
                    break

        QTimer.singleShot(0, wrapped)

    def onNewPage(self, activiteId):
        self.recents.insertRow(0)
        for ac in self.currentMatiere.activites:
            if ac.id == activiteId:
                ac.pages.insertRow(0)
                break

    def onDeletePage(self, pageid):
        def wrapped():
            self.recents.remove_by_Id(pageid)
            for ac in self.currentMatiere.activites:
                ac.pages.remove_by_Id(pageid)

        QTimer.singleShot(0, wrapped)

    def onMovePage(self):
        def wrapped():
            self.recents.reset()
            for ac in self.currentMatiere.activites:
                ac.pages.reset()

        QTimer.singleShot(0, wrapped)

    def onPageModified(self):
        def wrapped():
            self.recents.move_to(self.page.id, 0)

        QTimer.singleShot(0, wrapped)
