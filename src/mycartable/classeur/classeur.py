from typing import Union, Optional
from uuid import UUID

from PySide2.QtCore import Slot, Signal, QObject, Property
from loguru import logger
from .matiere import MatieresDispatcher, Matiere
from .page import Page
from pony.orm import db_session, Database, ObjectNotFound


"""
connections restant à établir:
page:
    titre changed => recents
pagemodel : 
    modif content => recents
    insertsection => recents
    removesection => recents
    moverow=> recents
"""


class Classeur(QObject):

    db: Database

    anneeChanged = Signal()
    activitesChanged = Signal()
    currentMatiereChanged = Signal()
    pageChanged = Signal()

    """
    Pure python
    """

    def __init__(self):
        super().__init__()
        self.reset()
        self.setup_connections()

    def reset(self):
        self._annee = 0
        self._matieresDispatcher: MatieresDispatcher = None
        self._currentMatiere: Matiere = None
        self._page: Page = None

    def setup_connections(self):
        self.currentMatiereChanged.connect(self.activitesChanged)

    """
    Qt Properties
    """

    @Property(int, notify=anneeChanged)
    def annee(self):
        return self._annee

    @annee.setter
    def annee_set(self, annee: int):
        self.reset()
        if annee:
            self._annee = annee
            self._matieresDispatcher = MatieresDispatcher(self.db, annee)
            logger.info(f"Année en cours : {annee}")
            self.anneeChanged.emit()

    @Property(QObject, notify=currentMatiereChanged)
    def currentMatiere(self):
        return self._currentMatiere

    @currentMatiere.setter
    def current_matiere_set(self, value):
        if isinstance(value, UUID):
            value = str(value)
        # ignore same
        if self._currentMatiere and self.currentMatiere.id == value:
            return
        with db_session:
            try:
                self._currentMatiere = Matiere(self.db.Matiere[value].to_dict())
            except ObjectNotFound as res:
                logger.error(res)
                return
        logger.info(f"current matiere set to: {self._currentMatiere}")
        self.currentMatiereChanged.emit()

    @Property(int, notify=currentMatiereChanged)
    def currentMatiereIndex(self):
        if self.currentMatiere:
            return self.matieresDispatcher.indexFromId(self.currentMatiere.id)
        else:
            return 0

    @Property(QObject, notify=anneeChanged)
    def matieresDispatcher(self):
        return self._matieresDispatcher

    @Property(QObject, notify=pageChanged)
    def page(self):
        return self._page

    """
    Qt Slots
    """

    @Slot()
    def deletePage(self):
        self.page.delete()
        self._page = None
        self.pageChanged.emit()

    @Slot(str)
    def newPage(self, activiteId: str) -> Optional[dict]:
        new_item = Page.new(activite=activiteId)
        logger.debug(f'New Page "{new_item.id}" created')
        self.setPage(new_item)

    @Property("QVariantList", notify=activitesChanged)
    def pagesParActivite(self):
        res = []
        if self.currentMatiere:
            with db_session:
                matiere = self.db.Matiere[self.currentMatiere.id]
                res = matiere.pages_par_activite()
        return res

    @Slot(str)
    @Slot(int)
    def setCurrentMatiere(self, value: Union[int, str]):
        if isinstance(value, int):
            value = self.matieresDispatcher.idFromIndex(value)
        self.currentMatiere = value

    @Slot(str)
    @Slot(Page)
    def setPage(self, value: Union[str, Page]):
        new_page = value if isinstance(value, Page) else Page.get(value)
        new_page.setParent(self)
        if self._page:
            self._page.setParent(None)
        self._page = new_page
        self.pageChanged.emit()
        logger.info(f"CurrentPage changed to {self.page.titre}")
        self.setCurrentMatiere(self.page.matiereId)
