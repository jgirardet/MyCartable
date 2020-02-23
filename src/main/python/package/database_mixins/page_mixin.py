from PySide2.QtCore import Slot, Signal, Property, QObject, QTimer
from package.constantes import TITRE_TIMER_DELAY
from package.utils import create_singleshot
from pony.orm import db_session, make_proxy
import logging

LOG = logging.getLogger(__name__)


class PageMixin:
    currentPageChanged = Signal("QVariantMap")
    newPageCreated = Signal(dict)
    currentTitreChanged = Signal()

    TITRE_TIMER_DELAY = TITRE_TIMER_DELAY

    def __init__(self):
        self._currentPage = 0
        self._currentTitre = ""
        self._currentEntry = None

        self.timer_titre = create_singleshot(self._currentTitreSet)

        from package.list_models import PageModel

        self.models.update({"pageModel": PageModel()})

    @Property(QObject, notify=currentPageChanged)
    def pageModel(self):
        return self.models["pageModel"]

    # newPage
    @Slot(int, result="QVariantMap")
    def newPage(self, activite):
        with db_session:
            new_item = self.db.Page.new_page(activite=activite)
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

        if new_id:
            with db_session:
                page = self.db.Page[new_id].to_dict()
            self.currentPageChanged.emit(page)
            self.setCurrentEntry()
        else:
            self._currentEntry = None
            self._currentPage = 0

    @Slot(int)
    def removePage(self, pageId):
        if self.currentPage == pageId:
            self.currentPage = 0
        with db_session:
            item = self.db.Page.get(id=pageId)
            if item:
                item.delete()

    def setCurrentEntry(self):
        with db_session:
            item = self.db.Page.get(id=self.currentPage)
            self._currentTitre = item.titre
            self._currentEntry = make_proxy(item)
            self.currentTitreChanged.emit()

    @Property(str, notify=currentTitreChanged)
    def currentTitre(self):
        return self._currentTitre

    @currentTitre.setter
    def currentTitreSet(self, value):
        if self.currentPage:
            if value != self._currentTitre:
                self._currentTitre = value
                self.timer_titre.start(self.TITRE_TIMER_DELAY)

    def _currentTitreSet(self):
        with db_session:
            self._currentEntry.titre = self._currentTitre
        self.currentTitreChanged.emit()
        LOG.debug(f"nouveau titre : {self._currentTitre}")
