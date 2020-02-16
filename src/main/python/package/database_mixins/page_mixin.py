from PySide2.QtCore import Slot, Signal, Property, QObject, QTimer
from package.constantes import TITRE_TIMER_DELAY
from package.utils import create_single_shot
from pony.orm import db_session, make_proxy
import logging

LOG = logging.getLogger(__name__)


class PageMixin:
    currentPageChanged = Signal(int)
    newPageCreated = Signal(dict)
    currentTitreChanged = Signal()

    TITRE_TIMER_DELAY = TITRE_TIMER_DELAY

    def __init__(self):
        self._currentPage = 0
        self._currentTitre = ""
        self._currentEntry = None
        self._currentPageIndex = None

        self.titreTimer = create_single_shot(self._currentTitreSet)

        from package.list_models import PageModel

        self.models.update({"pageModel": PageModel()})

    @Property(QObject, notify=currentPageChanged)
    def pageModel(self):
        return self.models["pageModel"]

    # newPage
    @Slot(int, result="QVariantMap")
    def newPage(self, activite):
        with db_session:
            new_item = self.db.Page.new_page(activite=activite, titre="nouveau")
        self.newPageCreated.emit(new_item)

    # currentPage
    @Property(int, notify=currentPageChanged)
    def currentPage(self):
        return self._currentPage

    @currentPage.setter
    def currentPageSet(self, new_id):
        if self._currentPage == new_id:
            return
        self._currentPage = new_id
        LOG.debug(f"CurrentPage changed to {new_id}")
        self.currentPageChanged.emit(new_id)
        self.setCurrentEntry()

    def setCurrentEntry(self):
        with db_session:
            item = self.db.Page.get(id=self.currentPage)
            self._currentTitre = item.titre
            self._currentEntry = make_proxy(item)
            self.currentTitreChanged.emit()

    @Property(str, notify=currentTitreChanged)
    def currentTitre(self):
        return self._currentTitre

    currentPageIndexChanged = Signal()

    @Property(int, notify=currentPageIndexChanged)
    def currentPageIndex(self):
        return self._currentPageIndex

    @currentPageIndex.setter
    def currentPageIndex_set(self, value: int):
        self._currentPageIndex = value
        self.currentPageIndexChanged.emit()

    @currentTitre.setter
    def currentTitreSet(self, value):
        if self.currentPage:
            if value != self._currentTitre:
                self._currentTitre = value
                self.titreTimer.start(self.TITRE_TIMER_DELAY)

    def _currentTitreSet(self):
        with db_session:
            self._currentEntry.titre = self._currentTitre
        self.currentTitreChanged.emit()
        LOG.debug(f"nouveau titre : {self._currentTitre}")
